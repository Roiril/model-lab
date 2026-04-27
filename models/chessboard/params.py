"""Chessboard params (units: meters). 7x7 grid sized for toio."""

# --- play area ---
SQUARE = 0.032        # 32mm — toio core cube footprint
N = 6                 # 6x6 grid
PLAY = SQUARE * N     # 224mm — playing area edge

# --- floor / grooves ---
THICKNESS = 0.004     # 4mm floor
GROOVE_W = 0.0004     # 0.4mm — narrow enough not to catch toio
GROOVE_D = 0.0003     # 0.3mm

# --- inner visual rim ---
RIM_W = 0.002         # 2mm wide
RIM_H = 0.001         # 1mm above floor surface

# --- outer wall ---
WALL_W = 0.008        # 8mm wide
WALL_H = 0.0055       # 5.5mm total (= 4mm floor + 1.5mm above floor surface)

# --- derived ---
RIM_OUTER = PLAY + 2 * RIM_W           # 228mm
WALL_INNER = RIM_OUTER                  # 228mm
OUTER = WALL_INNER + 2 * WALL_W         # 252mm
WALL_H_FROM_FLOOR = WALL_H - THICKNESS  # 21mm above floor surface
