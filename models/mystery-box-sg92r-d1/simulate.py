"""D1の体積重心を使ってC系と同じ運動方程式を計算する。"""
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
runpy.run_path(str(HERE.parents[1] / 'lib' / 'd_cube_simulate.py'),
               init_globals={'MODEL_HERE': HERE}, run_name='__main__')
