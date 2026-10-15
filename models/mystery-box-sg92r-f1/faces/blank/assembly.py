"""Cassette-only assembly; insertion into the cube is composed by the host."""
import numpy as np


def steps(interface, common_params):
    result = [{"id": "panel", "title": "面板を置く", "instruction": "外側を下にして面板を置きます。", "moving": ["panel"],
               "frames": [{"panel": np.eye(4)}, {"panel": np.eye(4)}]}]
    for part in ("key_l", "key_r"):
        frames = []
        for distance in np.linspace(-12, 0, 25):
            matrix = np.eye(4)
            matrix[2, 3] = distance
            frames.append({part: matrix})
        result.append({"id": f"insert-{part}", "title": "固定キーを入れる",
                       "instruction": "キーの長い腕を内側へ向け、面板のくぼみから差し込みます。骨格への固定時に先端の爪を指で中央へ押します。",
                       "moving": [part], "frames": frames})
    return result
