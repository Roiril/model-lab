"""demo/demo.ino を Arduino Uno 向けに実コンパイルし、結果を build/firmware_report.json の compile 節へ書く。通電・書き込みはしない。

公式 Arduino CLI は新しく入れない。C4-2 が D 配下へ隔離した CLI と設定を使う（場所は C4-2 の build/demo_compile_report.json から読む。
--cli / --config / --work-directory で指定してもよい）。見つからない、または C4-2 が検証した実行ファイルと SHA が違うときは、
コンパイルせず「未コンパイル」と report に書いて終了コード 0 で終わる。PATH と Arduino の設定は変えない。

  py -3.11 models/tangible-pixel-cube/compile_demo.py
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "demo" / "demo.ino"
REPORT = HERE / "build" / "firmware_report.json"
C4_2_REPORT = ROOT / "models" / "mystery-box-sg92r-c4-2" / "build" / "demo_compile_report.json"
BOUNDARY_MESSAGE = "Check horn mounting if the required phase trim exceeds 10 degrees."


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_text(path, text):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with open(temporary, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(temporary, path)


def atomic_bytes(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def discover():
    """C4-2 の記録から (cli, config, work, 検証済み SHA) を引く。無ければ None"""
    if not C4_2_REPORT.is_file():
        return None
    recorded = json.loads(C4_2_REPORT.read_text(encoding="utf-8"))
    config = Path(recorded["configuration"]["configFile"])
    return config.parent / "cli" / "arduino-cli.exe", config, config.parent / "tangible-pixel-cube-compile", \
        recorded["cli"]["executableSha256"], recorded


def write_compile(report, section):
    report["compile"] = section
    atomic_text(REPORT, json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--work-directory", type=Path)
    args = parser.parse_args()
    if not REPORT.is_file():
        raise FileNotFoundError("build/firmware_report.json が無い。先に firmware.py を実行する")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    source_sha = digest(SOURCE)
    if report["source"]["sha256"] != source_sha:
        raise ValueError("demo.ino が firmware_report.json の記録と違う。firmware.py を実行し直す")
    base = {"sourceSha256": source_sha, "target": "arduino:avr:uno"}

    found = discover()
    cli = args.cli or (found[0] if found else None)
    config = args.config or (found[1] if found else None)
    work = args.work_directory or (found[2] if found else None)
    verified_sha = found[3] if found else None
    reason = None
    if cli is None or config is None or work is None:
        reason = "公式 Arduino CLI の場所が分からない（C4-2 の demo_compile_report.json が無く、--cli / --config 未指定）"
    elif not cli.is_file() or not config.is_file():
        reason = f"公式 Arduino CLI または設定が存在しない: {cli} / {config}"
    elif verified_sha is not None and digest(cli) != verified_sha:
        reason = "Arduino CLI の実行ファイルが C4-2 で検証した SHA-256 と一致しない（別物は使わない）"
    if reason is not None:
        write_compile(report, {**base, "status": "not-compiled", "reason": reason})
        print(json.dumps({"compiled": False, "reason": reason}, ensure_ascii=False))
        return

    work.mkdir(parents=True, exist_ok=True)
    source_text = SOURCE.read_text(encoding="utf-8")
    trim_match = re.search(r"constexpr float PHASE_TRIM_DEG = (-?\d+(?:\.\d+)?)f;", source_text)
    if trim_match is None:
        raise ValueError("共通角度補正の定数が見つからない")
    environment = os.environ.copy()
    environment["TEMP"] = str(work)
    environment["TMP"] = str(work)
    environment["LANG"] = environment["LC_ALL"] = "en_US.UTF-8"   # 出力を英語に固定（日本語のロケールだと Flash / RAM の行の形が変わる）

    def compile_sketch(sketch, build_path):
        command = [str(cli), "--config-file", str(config), "compile",
                   "--fqbn", "arduino:avr:uno", "--build-path", str(build_path), str(sketch)]
        started = time.monotonic()
        result = subprocess.run(command, capture_output=True, env=environment)
        return command, result, round((time.monotonic() - started) * 1000)

    fixtures = []
    for trim, should_compile in ((-10, True), (10, True), (-11, False), (11, False)):
        name = f"phase_{'minus' if trim < 0 else 'plus'}_{abs(trim)}"
        fixture = work / name
        fixture.mkdir(exist_ok=True)
        modified = source_text[:trim_match.start(1)] + f"{trim:.1f}" + source_text[trim_match.end(1):]
        atomic_bytes(fixture / (name + ".ino"), modified.encode("utf-8"))
        command, result, elapsed = compile_sketch(fixture, work / (name + "_build"))
        diagnostic = result.stderr.decode("utf-8", errors="replace")
        rejected = BOUNDARY_MESSAGE in diagnostic
        passed = result.returncode == 0 if should_compile else result.returncode != 0 and rejected
        fixtures.append({"trimDeg": trim, "expectedCompile": should_compile, "compileExitCode": result.returncode,
                         "boundaryDiagnosticDetected": rejected, "pass": passed, "elapsedMs": elapsed})
    if not all(row["pass"] for row in fixtures):
        write_compile(report, {**base, "status": "failed", "reason": "位相補正の境界 4 例が期待どおりでない",
                               "phaseTrimBoundary": fixtures})
        print(json.dumps({"compiled": True, "pass": False, "phaseTrimBoundary": fixtures}, ensure_ascii=False))
        raise SystemExit(1)

    build_path = work / "production_build"
    command, result, elapsed = compile_sketch(SOURCE.parent, build_path)
    if digest(SOURCE) != source_sha:
        raise RuntimeError("コンパイル中に demo.ino が変わった")
    output = result.stdout.decode("utf-8", errors="replace")
    if result.returncode != 0:
        write_compile(report, {**base, "status": "failed", "compileExitCode": result.returncode,
                               "stderrTail": result.stderr.decode("utf-8", errors="replace")[-2000:]})
        print(json.dumps({"compiled": True, "pass": False, "exitCode": result.returncode}))
        raise SystemExit(1)
    flash = re.search(r"Sketch uses (\d+) bytes.*?Maximum is (\d+) bytes", output, re.DOTALL)
    ram = re.search(r"Global variables use (\d+) bytes.*?leaving (\d+) bytes.*?Maximum is (\d+) bytes", output, re.DOTALL)
    if flash is None or ram is None:
        raise ValueError("コンパイラーの Flash / RAM の実出力を読めない")
    hex_path = build_path / "demo.ino.hex"
    if not hex_path.is_file():
        raise FileNotFoundError(hex_path)
    section = {**base, "status": "compiled", "pass": True,
               "compiledAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "cli": {"file": str(cli), "executableSha256": digest(cli)},
               "config": str(config), "workDirectory": str(work),
               "command": subprocess.list2cmdline(command), "compileExitCode": result.returncode,
               "compileElapsedMs": elapsed, "stderrBytes": len(result.stderr),
               "flashBytes": int(flash[1]), "flashMaximumBytes": int(flash[2]),
               "flashPercent": int(int(flash[1]) * 100 / int(flash[2])),
               "ramBytes": int(ram[1]), "ramRemainingBytes": int(ram[2]), "ramMaximumBytes": int(ram[3]),
               "ramPercent": int(int(ram[1]) * 100 / int(ram[3])),
               "hex": {"file": str(hex_path), "sha256": digest(hex_path), "sizeBytes": hex_path.stat().st_size},
               "phaseTrimBoundary": fixtures,
               "globalPathModified": False, "hardwareTested": False}
    write_compile(report, section)
    print(json.dumps({"compiled": True, "pass": True, "flashBytes": section["flashBytes"],
                      "flashMaximumBytes": section["flashMaximumBytes"], "ramBytes": section["ramBytes"],
                      "ramMaximumBytes": section["ramMaximumBytes"], "hexSha256": section["hex"]["sha256"]}))


if __name__ == "__main__":
    main()
