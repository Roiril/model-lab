"""同じSTLから描画した三方向を並べる。寸法や輪郭は加工しない。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image
import params

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "exports" / params.MODEL_NAME
FILES = ("studio-left.png", "studio-front.png", "studio-right.png")


def main():
    paths = [OUT / name for name in FILES]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
    images = [Image.open(path).convert("RGB") for path in paths]
    # Preserve aspect ratio. A common height makes each view equally legible.
    height = 720
    views = [im.resize((round(im.width*height/im.height), height), Image.Resampling.LANCZOS)
             for im in images]
    sheet = Image.new("RGB", (sum(im.width for im in views), height))
    offset = 0
    for im in views:
        sheet.paste(im, (offset, 0))
        offset += im.width
    sheet.save(OUT / "three-views.png")
    print(f"SAVED={OUT / 'three-views.png'} VIEWS={len(views)} SIZE={sheet.size}")


if __name__ == "__main__":
    main()
