"""旧 import 先との互換。共有実装は lib/printmech/mesh.py。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))

from printmech.mesh import Mesh, RAY_DIR, clearance, contact, inside  # noqa: E402,F401

__all__ = ["Mesh", "RAY_DIR", "inside", "contact", "clearance"]
