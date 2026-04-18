# toio Core Cube cover — modular system dimensions (m)

# toio Core Cube body
TOIO_W = 0.032   # 32mm
TOIO_D = 0.032   # 32mm
TOIO_H = 0.032   # 32mm

# Base cover geometry
FIT_CLR = 0.0003  # 0.3mm per side (snug fit)
WALL    = 0.002   # 2mm side wall
TOP_RIM = 0.006   # 6mm top rim (holds dovetail; leaves 3mm floor below slot)
COVER_H = 0.034   # 34mm — cavity 28mm deep, bottom 4mm left open for tires

# Derived base dimensions
BASE_IW = TOIO_W + 2 * FIT_CLR   # 32.6mm inner
BASE_ID = TOIO_D + 2 * FIT_CLR
BASE_OW = BASE_IW + 2 * WALL     # 36.6mm outer
BASE_OD = BASE_ID + 2 * WALL

# Dovetail rail — single, centered, runs along Y axis (slide module in from ±Y)
RAIL_TOP_W = 0.006   # 6mm slot opening width at top surface
RAIL_DEPTH = 0.003   # 3mm slot depth
RAIL_ANGLE = 15      # degrees — gentle taper, FDM-friendly without supports
RAIL_CLR   = 0.0002  # 0.2mm clearance per side (width direction)

# Module (swappable exterior)
MODULE_W = BASE_OW   # 36.6mm — flush with base outer
MODULE_D = BASE_OD   # 36.6mm
MODULE_H = 0.012     # 12mm tall module body

# Head peg connection (module socket ↔ face peg)
PEG_W   = 0.012   # 12mm square
PEG_H   = 0.004   # 4mm insertion depth
PEG_CLR = 0.0002  # 0.2mm clearance per side (press fit)

# Head (face piece)
HEAD_W  = 0.030   # 30mm
HEAD_D  = 0.026   # 26mm
HEAD_H  = 0.016   # 16mm
