"""uHand を Unity のプロジェクトへ入れる（入れ直す）。

py -3.11 models/hiwonder-uhand/unity_install.py <Unity のプロジェクトのフォルダ>
  <project>/Assets/UHand/ に次を置く。
    hiwonder-uhand-rigged.fbx / .json     exports/ から（先に anim_build.py を回しておく）
    Editor/UHandSetup.cs                  読み込み設定と Animator の組み立て
    Runtime/UHandDriver.cs                実行時に動かす部品
入れたあと Unity で Tools > uHand > Build Animator Controller を実行する。
batchmode なら -executeMethod UHand.EditorTools.UHandSetup.BuildAndVerifyBatch（結果は <project>/uhand_verify.txt）。
FBX が目録より古いときは止まる（焼き直し忘れを入れない）。
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.normpath(os.path.join(HERE, "../../exports"))
NAME = "hiwonder-uhand-rigged"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(proj, "Assets")):
        raise SystemExit(f"Unity のプロジェクトではない（Assets が無い）: {proj}")
    fbx, js = (os.path.join(EXPORTS, NAME + e) for e in (".fbx", ".json"))
    for p in (fbx, js):
        if not os.path.exists(p):
            raise SystemExit(f"無い: {p}（先に anim_build.py を回す）")
    srcs = [os.path.join(HERE, f) for f in ("model.py", "params.py", "kin.py", "anim_lib.py", "anim_build.py")]
    srcs += [os.path.join(HERE, "anim", "poses.json")]
    srcs += [os.path.join(HERE, "anim", "clips", f) for f in os.listdir(os.path.join(HERE, "anim", "clips"))]
    newer = [os.path.relpath(s, HERE) for s in srcs if os.path.getmtime(s) > os.path.getmtime(fbx)]
    if newer:
        raise SystemExit("FBX より新しい定義がある。anim_build.py を回してから入れる: " + ", ".join(newer))
    dst = os.path.join(proj, "Assets", "UHand")
    for sub in ("Editor", "Runtime"):
        os.makedirs(os.path.join(dst, sub), exist_ok=True)
    src = os.path.join(HERE, "unity", "Assets", "UHand")
    pairs = [(fbx, os.path.join(dst, NAME + ".fbx")), (js, os.path.join(dst, NAME + ".json")),
             (os.path.join(src, "Editor", "UHandSetup.cs"), os.path.join(dst, "Editor", "UHandSetup.cs")),
             (os.path.join(src, "Runtime", "UHandDriver.cs"), os.path.join(dst, "Runtime", "UHandDriver.cs"))]
    for a, b in pairs:
        shutil.copyfile(a, b + ".tmp")
        os.replace(b + ".tmp", b)
        print("置いた:", os.path.relpath(b, proj))


main()
