from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
runpy.run_path(str(HERE.parents[1] / 'lib' / 'd_cube_verify.py'),
               init_globals={'MODEL_HERE': HERE}, run_name='__main__')
