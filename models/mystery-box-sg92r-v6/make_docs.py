"""Current revision2 entry point."""
import pathlib,runpy
runpy.run_path(str(pathlib.Path(__file__).with_name('make_docs_revision.py')),run_name="__main__")
