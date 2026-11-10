"""uHand の動きを扱う入口。Blender の場所や引数の順を覚えなくてよいように 1 本にまとめた。

py -3.11 models/hiwonder-uhand/anim.py check                      定義と機構の検査（exit 0 で合格）
py -3.11 models/hiwonder-uhand/anim.py build                      検査 → 骨入りの FBX / GLB / 目録を exports/ に書く
py -3.11 models/hiwonder-uhand/anim.py preview <clip> [view]      8 コマの 1 枚絵と動画（view: front / palm / back / side）
py -3.11 models/hiwonder-uhand/anim.py sheets [view]              全クリップの 1 枚絵
py -3.11 models/hiwonder-uhand/anim.py pose <姿勢の名前> [view]    poses.json の姿勢を 1 枚
py -3.11 models/hiwonder-uhand/anim.py dofs index=1,thumb=0.5 [view]   量を直に決めて 1 枚
py -3.11 models/hiwonder-uhand/anim.py status                     書き出しが定義より古くないか
py -3.11 models/hiwonder-uhand/anim.py unity <Unity のプロジェクト>   FBX とスクリプトを入れる（古ければ止まる）
py -3.11 models/hiwonder-uhand/anim.py unity-test                 試験用の空プロジェクトで読み込み・組み立て・照合まで通す
絵と動画は exports/uhand-anim-preview/ に出る。ブラウザでは http://localhost:3000/viewer/uhand-anim.html
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../.."))
BLENDER = os.environ.get("BLENDER", "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
UNITY = os.environ.get("UNITY", "C:/Program Files/Unity/Hub/Editor/2022.3.62f2/Editor/Unity.exe")
FBX = os.path.join(ROOT, "exports", "hiwonder-uhand-rigged.fbx")
TEST_PROJECT = os.path.join(os.environ.get("TEMP", "C:/Temp"), "uhut")


def sources():
    out = [os.path.join(HERE, f) for f in ("model.py", "params.py", "kin.py", "anim_lib.py", "anim_build.py")]
    out.append(os.path.join(HERE, "anim", "poses.json"))
    d = os.path.join(HERE, "anim", "clips")
    return out + [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".json")]


def stale():
    """FBX より新しい定義の一覧。FBX が無ければ None。"""
    if not os.path.exists(FBX):
        return None
    t = os.path.getmtime(FBX)
    return [os.path.relpath(s, HERE) for s in sources() if os.path.getmtime(s) > t]


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT).returncode


def blender(script, *args):
    """Blender を裏で回す。出力は [..] で始まる行と誤りだけ通す。"""
    p = subprocess.run([BLENDER, "--background", "--python", os.path.join(HERE, script), "--", *args],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = p.stdout + p.stderr
    bad = "Traceback" in text or "Error:" in text
    show = False
    for line in text.splitlines():
        if line.startswith("Traceback"):
            show = True
        if show or line.startswith("[") or "Error" in line or "SystemExit" in line:
            if "HIPEW" not in line:
                print(line)
    return 1 if (p.returncode != 0 or bad) else 0


def check():
    return run([sys.executable, os.path.join(HERE, "anim_check.py")])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    cmd, rest = a[0], a[1:]
    if cmd == "check":
        return check()
    if cmd == "build":
        return check() or blender("anim_build.py")
    if cmd == "preview" and rest:
        return blender("anim_preview.py", "--clip", rest[0], *(("--view", rest[1]) if len(rest) > 1 else ()))
    if cmd == "sheets":
        return blender("anim_preview.py", "--clip", "all", *(("--view", rest[0]) if rest else ()))
    if cmd in ("pose", "dofs") and rest:
        return blender("anim_preview.py", "--" + cmd, rest[0], *(("--view", rest[1]) if len(rest) > 1 else ()))
    if cmd == "status":
        s = stale()
        if s is None:
            print("書き出しがまだ無い。anim.py build を実行する")
            return 1
        if s:
            print("書き出しより新しい定義がある。anim.py build を実行する:", ", ".join(s))
            return 1
        print("書き出しは最新")
        return 0
    if cmd == "unity" and rest:
        return run([sys.executable, os.path.join(HERE, "unity_install.py"), rest[0]])
    if cmd == "unity-test":
        if not os.path.exists(UNITY):
            print("Unity が無い:", UNITY, "（環境変数 UNITY で場所を渡せる）")
            return 1
        if os.path.isdir(TEST_PROJECT):
            shutil.rmtree(TEST_PROJECT)
        rc = run([UNITY, "-batchmode", "-nographics", "-createProject", TEST_PROJECT, "-quit",
                  "-logFile", TEST_PROJECT + "_create.log"])
        rc = rc or run([sys.executable, os.path.join(HERE, "unity_install.py"), TEST_PROJECT])
        if rc:
            return rc
        rc = run([UNITY, "-batchmode", "-nographics", "-projectPath", TEST_PROJECT, "-executeMethod",
                  "UHand.EditorTools.UHandSetup.BuildAndVerifyBatch", "-logFile", os.path.join(TEST_PROJECT, "run.log")])
        res = os.path.join(TEST_PROJECT, "uhand_verify.txt")
        if os.path.exists(res):
            lines = open(res, encoding="utf-8").read().splitlines()
            for line in lines:
                if not line.startswith("ok "):
                    print(line)
        else:
            print("結果が無い。ログを見る:", os.path.join(TEST_PROJECT, "run.log"))
            rc = rc or 1
        print("Unity の試験:", "合格" if rc == 0 else f"不合格（exit {rc}）")
        return rc
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
