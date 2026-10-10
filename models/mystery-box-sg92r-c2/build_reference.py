"""既定SG92Rの出力を保持し、C2試験寸法の参照だけを生成する。"""
import os
from pathlib import Path
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
BLENDER = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")

if __name__ == "__main__":
    env = dict(os.environ, SG92R_PROFILE="c2-drawing-trial")
    result = subprocess.run(
        [str(BLENDER), "--background", "--python-exit-code", "1", "--python",
         str(ROOT / "models/sg92r-photo/model.py")],
        env=env, cwd=ROOT,
    )
    raise SystemExit(result.returncode)
