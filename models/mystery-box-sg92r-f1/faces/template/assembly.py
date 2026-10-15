"""Cassette-only insertion paths; the host handles slot insertion and keys."""
import numpy as np


def steps(interface, common_params):
    return [{"id": "mount", "title": "面を準備する", "instruction": "前板と左右の固定キーを準備します。",
             "moving": ["panel", "key_l", "key_r"],
             "frames": [{part: np.eye(4) for part in ("panel", "key_l", "key_r")} for _ in range(2)]}]
