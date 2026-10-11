"""Arduino Unoの実コンパイルと角度補正の境界を検査する。通電はしない。"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
SOURCE = HERE / "demo/demo.ino"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return {"file": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


def atomic_bytes(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--work-directory", type=Path, required=True)
    args = parser.parse_args()
    if not args.cli.is_file() or not args.config.is_file():
        raise FileNotFoundError("Arduino CLIまたは隔離設定ファイルが存在しない")
    report_path = BUILD / "demo_compile_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if digest(args.cli) != report["cli"]["executableSha256"]:
        raise ValueError("検証済みArduino CLIと実行ファイルが一致しない")
    args.work_directory.mkdir(parents=True, exist_ok=True)
    before = digest(SOURCE)
    source_text = SOURCE.read_text(encoding="utf-8")
    trim_match = re.search(r"constexpr float PHASE_TRIM_DEG = (-?\d+(?:\.\d+)?)f;", source_text)
    if trim_match is None:
        raise ValueError("共通角度補正の定数が見つからない")
    environment = os.environ.copy()
    environment["TEMP"] = str(args.work_directory)
    environment["TMP"] = str(args.work_directory)

    def compile_sketch(sketch, build_path):
        command = [str(args.cli), "--config-file", str(args.config), "compile",
                   "--fqbn", "arduino:avr:uno", "--build-path", str(build_path), str(sketch)]
        started = time.monotonic()
        result = subprocess.run(command, capture_output=True, env=environment)
        return command, result, round((time.monotonic() - started) * 1000)

    fixtures = []
    for trim, should_compile in ((-10, True), (10, True), (-11, False), (11, False)):
        name = f"phase_{'minus' if trim < 0 else 'plus'}_{abs(trim)}"
        fixture = args.work_directory / name
        fixture.mkdir(exist_ok=True)
        fixture_source = fixture / (name + ".ino")
        modified = source_text[:trim_match.start(1)] + f"{trim:.1f}" + source_text[trim_match.end(1):]
        atomic_bytes(fixture_source, modified.encode("utf-8"))
        command, result, elapsed = compile_sketch(fixture, args.work_directory / (name + "_build"))
        diagnostic = result.stderr.decode("utf-8", errors="replace")
        fixture_stdout, fixture_stderr = fixture / "stdout.txt", fixture / "stderr.txt"
        atomic_bytes(fixture_stdout, result.stdout)
        atomic_bytes(fixture_stderr, result.stderr)
        expected_rejection = "Check horn mounting if the required phase trim exceeds 10 degrees." in diagnostic
        passed = result.returncode == 0 if should_compile else result.returncode != 0 and expected_rejection
        fixtures.append({"trimDeg": trim, "expectedCompile": should_compile,
                         "compileExitCode": result.returncode, "pass": passed,
                         "boundaryDiagnosticDetected": expected_rejection,
                         "sourceSha256": digest(fixture_source), "elapsedMs": elapsed,
                         "source": {"file": str(fixture_source.absolute()), "sha256": digest(fixture_source)},
                         "stdout": {"file": str(fixture_stdout.absolute()), "sha256": digest(fixture_stdout)},
                         "stderr": {"file": str(fixture_stderr.absolute()), "sha256": digest(fixture_stderr)},
                         "command": subprocess.list2cmdline(command)})
    if not all(row["pass"] for row in fixtures):
        print(json.dumps({"phaseCalibration": fixtures, "pass": False}))
        raise SystemExit(1)
    build_path = args.work_directory / "production_build"
    command, result, elapsed = compile_sketch(SOURCE.parent, build_path)
    stdout_path, stderr_path = BUILD / "demo_compile_stdout.txt", BUILD / "demo_compile_stderr.txt"
    atomic_bytes(stdout_path, result.stdout)
    atomic_bytes(stderr_path, result.stderr)
    if result.returncode != 0 or before != digest(SOURCE):
        raise RuntimeError("正本デモのコンパイル未成立または途中のソース変更")
    output = result.stdout.decode("utf-8", errors="strict")
    flash = re.search(r"Sketch uses (\d+) bytes.*Maximum is (\d+) bytes", output)
    ram = re.search(r"Global variables use (\d+) bytes.*leaving (\d+) bytes.*Maximum is (\d+) bytes", output)
    if flash is None or ram is None:
        raise ValueError("コンパイラーのFlash/RAM実出力を読めない")
    hex_path = build_path / "demo.ino.hex"
    if not hex_path.is_file():
        raise FileNotFoundError(hex_path)
    atomic_bytes(BUILD / "demo.ino.hex", hex_path.read_bytes())
    report["pass"] = True
    report["compiledAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report["source"] = record(SOURCE)
    report["algorithm"] = record(Path(__file__))
    report["commands"] = [row for row in report["commands"] if row["name"] != "compile"] + [
        {"name": "compile", "command": subprocess.list2cmdline(command)}]
    report["results"].update(compileExitCode=result.returncode, compileElapsedMs=elapsed,
                            stdoutLog=stdout_path.relative_to(ROOT).as_posix(),
                            stdoutSha256=digest(stdout_path),
                            stderrLog=stderr_path.relative_to(ROOT).as_posix(),
                            stderrSha256=digest(stderr_path), stderrBytes=len(result.stderr))
    report.update(flashBytes=int(flash[1]), flashMaximumBytes=int(flash[2]),
                  ramBytes=int(ram[1]), ramRemainingBytes=int(ram[2]), ramMaximumBytes=int(ram[3]))
    report["flashPercent"] = int(report["flashBytes"] * 100 / report["flashMaximumBytes"])
    report["ramPercent"] = int(report["ramBytes"] * 100 / report["ramMaximumBytes"])
    report["artifact"] = record(BUILD / "demo.ino.hex") | {"sizeBytes": hex_path.stat().st_size}
    report["compileOutput"] = {"stdout": record(stdout_path), "stderr": record(stderr_path)}
    report["configuration"]["temp"] = str(args.work_directory.absolute())
    report["configuration"]["compileWorkDirectory"] = str(args.work_directory.absolute())
    report["phaseTrim"] = {"compiledTrimDeg": float(trim_match[1]),
                           "allowedTrimDeg": [-10, 10], "logicalPatternAnglesDeg": [15, 50, 90, 130, 165],
                           "physicalPhaseMeasured": False, "calibration": fixtures,
                           "pass": all(row["pass"] for row in fixtures)}
    atomic_bytes(report_path, (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"pass": True, "flashBytes": report["flashBytes"],
                      "ramBytes": report["ramBytes"], "phaseCalibrationPass": report["phaseTrim"]["pass"],
                      "hexSha256": report["artifact"]["sha256"]}))


if __name__ == "__main__":
    main()
