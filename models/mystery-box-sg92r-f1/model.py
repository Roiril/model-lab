"""面の選択は slots.json。形状と検査契約を同時に再生成する。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose import build

build()
