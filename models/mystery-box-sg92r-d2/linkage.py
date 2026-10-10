"""D2の4節リンク運動学。単位:mm・度。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
import params as P  # noqa: E402
from d_cube_geometry import install_linkage  # noqa: E402

install_linkage(globals(), P)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    values = sweep()
    print(f"H={H} O={O} a={A_LEN:.2f} B0={tuple(round(v, 2) for v in B0)} l={L_LINK:.3f}")
    print(f"alpha: {values[0][1]:.1f} -> {values[-1][1]:.1f} (Δ {values[-1][1]-values[0][1]:.1f}°)")
