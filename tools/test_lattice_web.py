"""lattice_web.py: build/ の必須ファイル検査・ui 節・index.json の試験。"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lattice_web as web

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def write_stl(path):
    triangle = struct.pack("<12fH", 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0)
    path.write_bytes(b"\0" * 80 + struct.pack("<I", 1) + triangle)


def write_model(root, model, groups=2, ui=None, skip=()):
    """表示に要る最小の build/ 一式。"""
    folder = root / "models" / model
    build = folder / "build"
    build.mkdir(parents=True)
    write_stl(build / "a.stl")
    ids = [f"pixel_{i}" for i in range(groups)]
    files = {
        "manifest.json": {"meta": {}, "parts": [
            {"id": "a", "label": "A", "assembly": "build/a.stl", "print": "print_a.stl"},
            {"id": "gauge", "assembly": "build/missing.stl", "fit_only": True}]},
        "motion.json": {"home_servo_deg": 0, "frames": [
            {"servo_deg": 0, "transforms": {"a": IDENTITY}}, {"servo_deg": 10, "transforms": {"a": IDENTITY}}]},
        "boolean_evidence.json": {},
        "sim_tables.json": {
            "limitsDeg": [0, 10], "duration_s": 1,
            "groups": [{"id": i, "label": i, "massKg": 0.001} for i in ids],
            "rows": [{"servoDeg": d, "inertiaRestKgm2": 0, "inertiaGroupsKgm2": 0, "dMGroupsDqKgm2PerRad": 0,
                      "gravityRestNm": 0, "gravityGroupsNm": 0, "liftsMm": [0] * groups,
                      "dLiftDqMPerRad": [0] * groups, "d2LiftDq2MPerRad2": [0] * groups} for d in (0, 10)],
            "const": {k: 1 for k in ("stallTorqueNm", "dtS", "recordS", "settleS", "motorInertiaKgm2", "controlBandRad",
                                    "noLoadSpeedRadS", "servoFrictionNm", "gravityMS2", "contactToleranceN")}},
        "simulate_report.json": {"overall": {"calculationPass": True}, "driveGeometry": {"geometryPass": True}},
        "assembly.json": {"pass": True, "steps": [{"title": "t", "instruction": "i", "checkText": "c", "moving": ["a"],
                                                    "frames": [{"progress": 0, "transforms": {"a": IDENTITY}}],
                                                    "report": {"samples": 1}}]},
        "drive_report.json": {"overall": {"geometryPass": True}, "interfaces": []},
    }
    for name, value in files.items():
        if name not in skip:
            (build / name).write_text(json.dumps(value), encoding="utf-8")
    if ui is not None:
        (build / "ui.json").write_text(json.dumps(ui), encoding="utf-8")
    return folder


class LatticeWebTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.root = Path(self._dir.name)

    def tearDown(self):
        self._dir.cleanup()

    def test_missing_files_are_listed_and_nothing_is_written(self):
        folder = write_model(self.root, "m", skip=("assembly.json", "drive_report.json"))
        (folder / "build/a.stl").unlink()
        self.assertEqual(web.missing_inputs(folder), ["build/assembly.json", "build/drive_report.json", "build/a.stl"])
        with self.assertRaisesRegex(FileNotFoundError, "assembly.json.*drive_report.json.*a.stl"):
            web.export("m", self.root)
        self.assertFalse((self.root / "viewer/lattice/assets").exists())

    def test_fit_only_parts_need_no_stl(self):
        self.assertEqual(web.missing_inputs(write_model(self.root, "m")), [])

    def test_unknown_model_without_ui_json_uses_defaults(self):
        write_model(self.root, "tangible-pixel-cube")
        result = web.export("tangible-pixel-cube", self.root)
        asset = json.loads((self.root / "viewer/lattice/assets/tangible-pixel-cube.json").read_text(encoding="utf-8"))
        self.assertEqual(asset["ui"], {})
        self.assertEqual(asset["model"], "tangible-pixel-cube")
        self.assertEqual(asset["meta"]["assembly_steps"], ["i"])
        self.assertEqual([p["id"] for p in asset["parts"]], ["a"])
        self.assertEqual(result["models"], 1)

    def test_ui_json_is_written_and_indexed_but_legacy_models_get_no_ui(self):
        # 旧 3 モデルは build/ui.json があっても ui 節を足さない（表示データのバイト一致を守る）。
        write_model(self.root, "mystery-box-sg92r-c3", ui={"label": "ignored"})
        write_model(self.root, "tangible-pixel-cube", ui={
            "label": "TPC", "navLabel": "TPC 画素の立方体", "navOrder": 40,
            "physics": {"playback": "motion-frames", "chartSeries": ["pixel_1"], "term": "画素"},
            "legendGroups": [{"label": "画素", "prefix": "a"}], "colors": {"a": "#0072b2"}})
        assets = self.root / "viewer/lattice/assets"
        web.export("mystery-box-sg92r-c3", self.root)
        self.assertFalse((assets / "index.json").exists())
        web.export("tangible-pixel-cube", self.root)
        self.assertNotIn("ui", json.loads((assets / "mystery-box-sg92r-c3.json").read_text(encoding="utf-8")))
        written = json.loads((assets / "tangible-pixel-cube.json").read_text(encoding="utf-8"))["ui"]
        self.assertEqual(written["physics"]["playback"], "motion-frames")
        index = json.loads((assets / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index, [{"id": "tangible-pixel-cube", "navLabel": "TPC 画素の立方体", "navOrder": 40}])

    def test_late_reports_are_omitted_when_absent_and_nulled_for_layout_only(self):
        write_model(self.root, "m")
        web.export("m", self.root)
        asset = json.loads((self.root / "viewer/lattice/assets/m.json").read_text(encoding="utf-8"))
        for key in ("continuous_path_support_evidence", "first_layer_contact_evidence"):
            self.assertNotIn(key, asset)
        self.assertIsNone(asset["print_path_evidence"])
        build = self.root / "models/m/build"
        (build / "delivery_report.json").write_text(json.dumps({"status": "layout_only"}), encoding="utf-8")
        (build / "first_layer_contact_evidence.json").write_text(json.dumps({"overall": {}}), encoding="utf-8")
        web.export("m", self.root)
        asset = json.loads((self.root / "viewer/lattice/assets/m.json").read_text(encoding="utf-8"))
        for key in ("continuous_path_support_evidence", "first_layer_contact_evidence"):
            self.assertIn(key, asset)
            self.assertIsNone(asset[key])

    def test_bad_ui_is_reported_with_every_problem(self):
        write_model(self.root, "m", groups=7)
        with self.assertRaisesRegex(ValueError, "7個.*5本まで"):
            web.export("m", self.root)
        self.assertFalse((self.root / "viewer/lattice/assets/m.json").exists())
        bad = {"physics": {"playback": "spin", "chartSeries": ["pixel_0", "ghost"]}, "print": {"downloadBase": "tmp"},
               "colors": {"a": "blue"}, "legendGroups": [{"label": "x"}]}
        folder = self.root / "models/m/build"
        (folder / "ui.json").write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            web.export("m", self.root)
        message = str(caught.exception)
        for fragment in ("playback", "ghost", "downloadBase", "#rrggbb", "parts（id の配列）か prefix"):
            self.assertIn(fragment, message)

    def test_chart_series_limits(self):
        write_model(self.root, "m", groups=25, ui={"physics": {"chartSeries": [f"pixel_{i}" for i in range(5)]}})
        web.export("m", self.root)
        folder = self.root / "models/m/build"
        too_many = {"physics": {"chartSeries": [f"pixel_{i}" for i in range(6)]}}
        (folder / "ui.json").write_text(json.dumps(too_many), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "chartSeries"):
            web.export("m", self.root)

    def test_input_shape_problems_are_named(self):
        folder = write_model(self.root, "m")
        sim = json.loads((folder / "build/sim_tables.json").read_text(encoding="utf-8"))
        del sim["rows"][1]["liftsMm"]
        del sim["const"]["dtS"]
        (folder / "build/sim_tables.json").write_text(json.dumps(sim), encoding="utf-8")
        motion = json.loads((folder / "build/motion.json").read_text(encoding="utf-8"))
        motion["frames"][0]["transforms"]["a"] = [1, 2, 3]
        (folder / "build/motion.json").write_text(json.dumps(motion), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            web.export("m", self.root)
        message = str(caught.exception)
        for fragment in ("rows[1]", "liftsMm", "dtS", "16要素の行列"):
            self.assertIn(fragment, message)

    def test_cli_returns_2_for_missing_inputs_and_rejects_bad_names(self):
        err, out = io.StringIO(), io.StringIO()
        with redirect_stderr(err), redirect_stdout(out):
            self.assertEqual(web.main(["no-such-model-xyz"]), 2)
        self.assertIn("書き出せません", err.getvalue())
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            web.main(["../etc"])

    def test_legacy_models_rewrite_to_the_committed_bytes(self):
        """旧 3 モデルを書き出し直すと、コミット済みの表示データとバイト一致する（本物の assets は触らない）。

        過去モデルの監査（models/mystery-box-sg92r-c4-2/audit.py）が C4-1 の表示データを HEAD と照合する。
        """
        committed = web.ROOT / "viewer/lattice/assets"
        for model in web.LEGACY_MODELS:
            with self.subTest(model=model):
                self.assertEqual(web.missing_inputs(web.ROOT / "models" / model), [])
                web.export(model, web.ROOT, assets=self.root)
                self.assertEqual((self.root / f"{model}.json").read_bytes(), (committed / f"{model}.json").read_bytes())
        self.assertFalse((self.root / "index.json").exists())


if __name__ == "__main__":
    unittest.main()
