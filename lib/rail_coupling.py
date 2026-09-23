"""手すりの円筒差し込み。寸法はmm。固定はテープで行う。"""

CLEAR = .35                     # 円筒どうしの半径方向の隙間
SPIGOT_R = 17.8                 # 外径35.6、穴28.6に対して肉厚3.5
SPIGOT_LEAD = .4                # 先端外角の45度面取り
ENGAGEMENT = 7.3                # 内外ともM字へ入る長さ
SOCKET_R = SPIGOT_R + CLEAR     # M字の円形受け径36.3
SOCKET_DEPTH = 8.5
SOCKET_LEAD = .4
SOCKET_FLOOR_LEAD = .5
SOCKET_OUTER_R = 21.0           # M字の口元だけ外径42で補強
SOCKET_BLEND = 5.0
COLLAR_R = 20.6                 # カーブ端の肩。外径41.2
COLLAR_HOLD = 2.0
COLLAR_BLEND = 8.0


def export_print_part(ob, exports_dir, filename):
    """既存の3MF出力。形状と印刷向きのみを格納する。"""
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / 'models/pipe-foot-corner-split/export_3mf.py'
    spec = importlib.util.spec_from_file_location('handrail_export_3mf', path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    exporter.REVISION = 'handrail-socket-20260923'
    return exporter.export_part(ob, exports_dir, filename)
