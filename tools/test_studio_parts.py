import contextlib
import hashlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.dirname(__file__))
import studio_parts  # noqa: E402


def stl_bytes(seed=0):
    """三角形 1 個の binary STL。seed で中身を変える。"""
    header = b"test".ljust(80, b"\0")
    triangle = struct.pack("<12fH", 0, 0, 1, 0, 0, seed, 10, 0, seed, 0, 10, seed, 0)
    return header + struct.pack("<I", 1) + triangle


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Fixture:
    """tempdir に models/<model>/build/... と exports/ を作る。"""

    def __init__(self, test, model="demo"):
        self.model = model
        self._tmp = tempfile.TemporaryDirectory()
        test.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        os.makedirs(os.path.join(self.root, "exports"))

    def path(self, *parts):
        return os.path.join(self.root, *parts)

    def write(self, rel, data):
        full = self.path(*rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        mode = "wb" if isinstance(data, bytes) else "w"
        with open(full, mode, **({} if mode == "wb" else {"encoding": "utf-8"})) as fh:
            fh.write(data)
        return full

    def manifest(self, parts, stls=True):
        for index, part in enumerate(parts):
            if stls and part.get("assembly"):
                self.write(f"models/{self.model}/{part['assembly']}", stl_bytes(index))
        self.write(f"models/{self.model}/build/manifest.json",
                   json.dumps({"meta": {}, "parts": parts}, ensure_ascii=False))

    def ui(self, ui):
        self.write(f"models/{self.model}/build/ui.json", json.dumps(ui, ensure_ascii=False))

    def names(self, names):
        self.write(f"models/{self.model}/part-names.json", json.dumps(names, ensure_ascii=False))

    def ledger_path(self):
        return self.path("viewer", "studio", "parts", self.model + ".json")

    def read_ledger(self):
        with open(self.ledger_path(), encoding="utf-8") as fh:
            return json.load(fh)


def part(part_id, label=None, **extra):
    base = {"id": part_id, "label": part_id if label is None else label, "assembly": f"build/{part_id}.stl",
            "print": f"build/print_{part_id}.stl", "color": "#aabbcc"}
    base.update(extra)
    return base


class LedgerShape(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture(self)
        self.fx.manifest([
            part("housing", "外装（底と四方の壁）", exterior=True),
            part("gear_0", "歯車 0"), part("gear_1", "歯車 1"),
            part("sg92r", "SG92R", stock=True, print=None),
            part("comb", "位相合わせ治具", jig=True),
        ])

    def test_top_level_keys_and_types(self):
        studio_parts.write_parts("demo", self.fx.root)
        ledger = self.fx.read_ledger()
        self.assertEqual(list(ledger), ["version", "model", "source", "sourceSha256", "groups", "parts"])
        self.assertEqual(ledger["version"], 1)
        self.assertEqual(ledger["model"], "demo")
        self.assertEqual(ledger["source"], "models/demo/build/manifest.json")
        with open(self.fx.path("models", "demo", "build", "manifest.json"), "rb") as fh:
            self.assertEqual(ledger["sourceSha256"], sha(fh.read()))
        for group in ledger["groups"]:
            self.assertEqual(set(group), {"id", "label", "color"})
        for entry in ledger["parts"]:
            self.assertEqual(
                set(entry), {"id", "label", "systemLabel", "group", "kind", "file", "sha256",
                             "size", "aliases", "color"})
            self.assertIn(entry["kind"], studio_parts.KINDS)
            self.assertIsInstance(entry["aliases"], list)

    def test_part_order_follows_manifest(self):
        studio_parts.write_parts("demo", self.fx.root)
        self.assertEqual([p["id"] for p in self.fx.read_ledger()["parts"]],
                         ["housing", "gear_0", "gear_1", "sg92r", "comb"])

    def test_kind(self):
        studio_parts.write_parts("demo", self.fx.root)
        kinds = {p["id"]: p["kind"] for p in self.fx.read_ledger()["parts"]}
        self.assertEqual(kinds, {"housing": "printed", "gear_0": "printed", "gear_1": "printed",
                                 "sg92r": "stock", "comb": "jig"})

    def test_part_without_print_is_stock(self):
        fx = Fixture(self)
        fx.manifest([part("servo", print=None), part("x")])
        studio_parts.write_parts("demo", fx.root)
        self.assertEqual(fx.read_ledger()["parts"][0]["kind"], "stock")

    def test_stl_files_match_ledger_and_source(self):
        studio_parts.write_parts("demo", self.fx.root)
        for entry in self.fx.read_ledger()["parts"]:
            self.assertEqual(entry["file"], f"demo-part-{entry['id']}.stl")
            with open(self.fx.path("exports", entry["file"]), "rb") as fh:
                exported = fh.read()
            with open(self.fx.path("models", "demo", "build", entry["id"] + ".stl"), "rb") as fh:
                source = fh.read()
            self.assertEqual(exported, source)
            self.assertEqual(entry["sha256"], sha(exported))
            self.assertEqual(entry["size"], len(exported))

    def test_slash_id_becomes_safe_file_name(self):
        fx = Fixture(self)
        fx.manifest([part("frame/lower", assembly="build/parts/frame/lower.stl")])
        studio_parts.write_parts("demo", fx.root)
        entry = fx.read_ledger()["parts"][0]
        self.assertEqual(entry["file"], "demo-part-frame__lower.stl")
        self.assertTrue(os.path.isfile(fx.path("exports", entry["file"])))


class Groups(unittest.TestCase):
    def test_legend_groups_prefix_parts_and_leftovers(self):
        fx = Fixture(self)
        fx.manifest([
            part("housing", exterior=True), part("guide"), part("pixel_0_0"), part("pixel_1_0"),
            part("clip_0"), part("clip_1"), part("servo", print=None, stock=True), part("comb", jig=True),
        ])
        fx.ui({"legendGroups": [
            {"label": "画素", "prefix": "pixel_", "color": "#e69f00"},
            {"label": "押さえクリップ", "parts": ["clip_0", "clip_1"]},
        ]})
        studio_parts.write_parts("demo", fx.root)
        ledger = fx.read_ledger()
        groups = {g["id"]: g for g in ledger["groups"]}
        self.assertEqual(list(groups), ["pixel", "clip", "jig", "stock", "shell", "other"])
        self.assertEqual(groups["pixel"]["label"], "画素")
        self.assertEqual(groups["pixel"]["color"], "#e69f00")
        self.assertEqual(groups["clip"]["color"], "#aabbcc")  # 色が無ければ先頭の部品の色
        of = {p["id"]: p["group"] for p in ledger["parts"]}
        self.assertEqual(of, {"housing": "shell", "guide": "other", "pixel_0_0": "pixel",
                              "pixel_1_0": "pixel", "clip_0": "clip", "clip_1": "clip",
                              "servo": "stock", "comb": "jig"})
        for group in ledger["groups"]:
            self.assertTrue(group["label"])

    def test_first_legend_group_wins(self):
        fx = Fixture(self)
        fx.manifest([part("a_1"), part("a_2")])
        fx.ui({"legendGroups": [{"label": "一", "parts": ["a_1"]}, {"label": "二", "prefix": "a_"}]})
        studio_parts.write_parts("demo", fx.root)
        of = {p["id"]: p["group"] for p in fx.read_ledger()["parts"]}
        self.assertEqual(of["a_1"], "a")
        self.assertEqual(of["a_2"], "a_2")  # 同じ id になる群は番号を付けて分ける

    def test_prefix_groups_without_ui_json(self):
        fx = Fixture(self)
        fx.manifest([
            part("frame/lower"), part("front/panel"), part("front/lid"),
            part("key_left"), part("key_right"), part("box"), part("bearing_button"),
        ])
        studio_parts.write_parts("demo", fx.root)
        ledger = fx.read_ledger()
        labels = {g["id"]: g["label"] for g in ledger["groups"]}
        self.assertEqual(labels, {"frame": "枠", "front": "正面", "key": "留め具", "other": "その他"})
        of = {p["id"]: p["group"] for p in ledger["parts"]}
        self.assertEqual(of["frame/lower"], "frame")
        self.assertEqual(of["key_left"], "key")
        self.assertEqual(of["box"], "other")
        self.assertEqual(of["bearing_button"], "other")  # 接頭辞を共有する部品が 1 個だけなら群にしない

    def test_unknown_prefix_warns_but_has_label(self):
        fx = Fixture(self)
        fx.manifest([part("zzz/a")])
        _, warnings = studio_parts.write_parts("demo", fx.root)
        self.assertEqual(fx.read_ledger()["groups"][0]["label"], "zzz")
        self.assertTrue(any("zzz" in w for w in warnings))

    def test_every_part_belongs_to_a_declared_group(self):
        fx = Fixture(self)
        fx.manifest([part("a/x"), part("b_1"), part("b_2"), part("solo")])
        studio_parts.write_parts("demo", fx.root)
        ledger = fx.read_ledger()
        ids = {g["id"] for g in ledger["groups"]}
        self.assertEqual(len(ids), len(ledger["groups"]))
        self.assertTrue(all(p["group"] in ids for p in ledger["parts"]))


class PartNames(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture(self)
        self.fx.manifest([part("housing", "外装（底と四方の壁）"), part("lid", "蓋")])

    def test_no_file_means_system_labels(self):
        studio_parts.write_parts("demo", self.fx.root)
        entry = self.fx.read_ledger()["parts"][0]
        self.assertEqual(entry["label"], "外装（底と四方の壁）")
        self.assertEqual(entry["systemLabel"], "外装（底と四方の壁）")
        self.assertEqual(entry["aliases"], [])

    def test_override_keeps_system_label(self):
        self.fx.names({"housing": {"label": "箱", "aliases": ["外側", "ケース", "外側"]}})
        studio_parts.write_parts("demo", self.fx.root)
        ledger = self.fx.read_ledger()
        entry = ledger["parts"][0]
        self.assertEqual(entry["label"], "箱")
        self.assertEqual(entry["systemLabel"], "外装（底と四方の壁）")
        self.assertEqual(entry["aliases"], ["外側", "ケース"])
        self.assertEqual(ledger["parts"][1]["label"], "蓋")  # 触っていない部品はそのまま

    def test_aliases_only_keeps_label(self):
        self.fx.names({"lid": {"aliases": ["ふた"]}})
        studio_parts.write_parts("demo", self.fx.root)
        entry = self.fx.read_ledger()["parts"][1]
        self.assertEqual((entry["label"], entry["aliases"]), ("蓋", ["ふた"]))

    def test_broken_names_are_listed(self):
        cases = {
            "未知の id": ({"nothing": {"label": "x"}}, "nothing"),
            "余分なキー": ({"lid": {"name": "x"}}, "使えないキー"),
            "空の label": ({"lid": {"label": " "}}, "label"),
            "aliases が配列でない": ({"lid": {"aliases": "ふた"}}, "aliases"),
            "オブジェクトでない": ({"lid": "ふた"}, "オブジェクト"),
        }
        for name, (names, needle) in cases.items():
            with self.subTest(name):
                self.fx.names(names)
                with self.assertRaises(studio_parts.PartsError) as ctx:
                    studio_parts.build_ledger("demo", self.fx.root)
                self.assertTrue(any(needle in p for p in ctx.exception.problems), ctx.exception.problems)

    def test_names_file_not_object(self):
        self.fx.write("models/demo/part-names.json", "[1]")
        with self.assertRaises(studio_parts.PartsError):
            studio_parts.build_ledger("demo", self.fx.root)

    def test_names_file_not_json(self):
        self.fx.write("models/demo/part-names.json", "{")
        with self.assertRaises(studio_parts.PartsError) as ctx:
            studio_parts.build_ledger("demo", self.fx.root)
        self.assertIn("part-names.json", ctx.exception.problems[0])


class BrokenInput(unittest.TestCase):
    def problems(self, fx, model="demo"):
        with self.assertRaises(studio_parts.PartsError) as ctx:
            studio_parts.build_ledger(model, fx.root)
        return ctx.exception.problems

    def test_unknown_model(self):
        fx = Fixture(self)
        self.assertIn("models/ にありません", self.problems(fx, "nope")[0])

    def test_missing_manifest(self):
        fx = Fixture(self)
        os.makedirs(fx.path("models", "demo"))
        self.assertIn("manifest.json がありません", self.problems(fx)[0])

    def test_manifest_not_json(self):
        fx = Fixture(self)
        fx.write("models/demo/build/manifest.json", "{")
        self.assertIn("JSON として壊れています", self.problems(fx)[0])

    def test_empty_parts(self):
        fx = Fixture(self)
        fx.write("models/demo/build/manifest.json", '{"parts": []}')
        self.assertIn("parts", self.problems(fx)[0])

    def test_all_problems_are_listed_together(self):
        fx = Fixture(self)
        fx.manifest([
            part("a", label=""), part("b", color="red"), part("c", assembly="build/none.stl"),
            part("d", assembly="../../outside.stl"), part("a2", id="b"), part("e"),
        ], stls=False)
        fx.write("models/demo/build/e.stl", b"not an stl")
        problems = self.problems(fx)
        text = "\n".join(problems)
        for needle in ("部品 a の label", "部品 b の color", "部品 c の STL がありません",
                       "モデルの外", "id が重複", "部品 e の build/e.stl は STL として読めません"):
            self.assertIn(needle, text)

    def test_bad_part_id(self):
        fx = Fixture(self)
        fx.manifest([part("has space")], stls=False)
        self.assertIn("id は", self.problems(fx)[0])

    def test_colliding_file_names(self):
        fx = Fixture(self)
        fx.manifest([part("a/b", assembly="build/1.stl"), part("a__b", assembly="build/2.stl")])
        self.assertIn("書き出し先が同じ", "\n".join(self.problems(fx)))

    def test_ui_json_problems(self):
        fx = Fixture(self)
        fx.manifest([part("a_1")])
        fx.ui({"legendGroups": [{"label": "x", "parts": ["zzz"]}, {"prefix": "q"}]})
        text = "\n".join(self.problems(fx))
        self.assertIn("zzz", text)
        self.assertIn("label が要ります", text)

    def test_nothing_is_written_when_input_is_broken(self):
        fx = Fixture(self)
        fx.manifest([part("a"), part("b", assembly="build/none.stl")], stls=False)
        fx.write("models/demo/build/a.stl", stl_bytes())
        with self.assertRaises(studio_parts.PartsError):
            studio_parts.write_parts("demo", fx.root)
        self.assertEqual(os.listdir(fx.path("exports")), [])
        self.assertFalse(os.path.exists(fx.ledger_path()))

    def test_main_reports_in_japanese_and_exits_2(self):
        fx = Fixture(self)
        fx.manifest([part("a", label="")], stls=False)
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = studio_parts.main(["demo"], root=fx.root)
        self.assertEqual(code, 2)
        self.assertIn("入力に問題があります", err.getvalue())
        self.assertIn("label がありません", err.getvalue())

    def test_main_without_args_does_every_model_and_fails_if_any_is_broken(self):
        fx = Fixture(self)
        fx.manifest([part("a")])
        fx.write("models/broken/build/manifest.json", "{")
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = studio_parts.main([], root=fx.root)
        self.assertEqual(code, 2)
        self.assertTrue(os.path.isfile(fx.ledger_path()))  # 壊れていないモデルは書く
        self.assertIn("demo: 部品 1", out.getvalue())


class Rewrite(unittest.TestCase):
    def test_rerun_leaves_files_untouched(self):
        fx = Fixture(self)
        fx.manifest([part("a"), part("b")])
        studio_parts.write_parts("demo", fx.root)
        targets = [fx.ledger_path(), fx.path("exports", "demo-part-a.stl")]
        for target in targets:
            os.utime(target, (1_000_000_000, 1_000_000_000))
        studio_parts.write_parts("demo", fx.root)
        for target in targets:
            self.assertEqual(os.path.getmtime(target), 1_000_000_000)

    def test_changed_source_updates_hash(self):
        fx = Fixture(self)
        fx.manifest([part("a")])
        studio_parts.write_parts("demo", fx.root)
        before = fx.read_ledger()["parts"][0]["sha256"]
        fx.write("models/demo/build/a.stl", stl_bytes(7))
        studio_parts.write_parts("demo", fx.root)
        entry = fx.read_ledger()["parts"][0]
        self.assertNotEqual(entry["sha256"], before)
        with open(fx.path("exports", entry["file"]), "rb") as fh:
            self.assertEqual(sha(fh.read()), entry["sha256"])

    def test_removed_part_stl_is_deleted_but_other_files_stay(self):
        fx = Fixture(self)
        fx.manifest([part("a"), part("b")])
        studio_parts.write_parts("demo", fx.root)
        keep = fx.write("exports/demo-part-unlisted.stl", stl_bytes())
        fx.manifest([part("a")])
        studio_parts.write_parts("demo", fx.root)
        self.assertFalse(os.path.exists(fx.path("exports", "demo-part-b.stl")))
        self.assertTrue(os.path.exists(fx.path("exports", "demo-part-a.stl")))
        self.assertTrue(os.path.exists(keep))  # 前の台帳に無いファイルは消さない

    def test_no_temp_files_left(self):
        fx = Fixture(self)
        fx.manifest([part("a")])
        studio_parts.write_parts("demo", fx.root)
        left = [n for d in (fx.path("exports"), os.path.dirname(fx.ledger_path()))
                for n in os.listdir(d) if n.endswith(".tmp")]
        self.assertEqual(left, [])

    def test_ledger_is_utf8_with_japanese_kept(self):
        fx = Fixture(self)
        fx.manifest([part("a", label="外装")])
        studio_parts.write_parts("demo", fx.root)
        with open(fx.ledger_path(), "rb") as fh:
            raw = fh.read()
        self.assertIn("外装".encode("utf-8"), raw)
        self.assertNotIn(b"\r\n", raw)


class RealModels(unittest.TestCase):
    """リポジトリの機構モデルが台帳にできること（build/manifest.json が揃っているものだけ）。"""

    def test_each_real_manifest_builds_a_consistent_ledger(self):
        models = [m for m in studio_parts._all_models(studio_parts.ROOT)
                  if m in ("tangible-pixel-cube", "mystery-box-sg92r-f1", "flag-box")]
        if not models:
            self.skipTest("対象モデルの build/manifest.json がありません")
        for model in models:
            with self.subTest(model):
                ledger, stls, _ = studio_parts.build_ledger(model)
                self.assertEqual(len(ledger["parts"]), len(stls))
                group_ids = {g["id"] for g in ledger["groups"]}
                self.assertTrue(all(p["group"] in group_ids for p in ledger["parts"]))
                self.assertEqual(len({p["file"] for p in ledger["parts"]}), len(ledger["parts"]))


if __name__ == "__main__":
    unittest.main()
