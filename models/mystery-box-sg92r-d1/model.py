"""D1の80mm鋭角箱を生成する。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from d_cube_geometry import create_model  # noqa: E402

_impl = create_model(__file__)
globals().update({name: getattr(_impl, name) for name in dir(_impl) if not name.startswith("__")})

if __name__ == "__main__":
    main()
