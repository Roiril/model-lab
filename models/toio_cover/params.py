# Toio Core Cube dimensions (m)
TOIO_W = 0.032
TOIO_D = 0.032
TOIO_H = 0.020

# Cover design
CLEARANCE = 0.0003   # 0.3mm per side (snug fit)
WALL      = 0.002    # 2mm side wall
TOP       = 0.002    # 2mm top wall

# Derived
INNER_W = TOIO_W + CLEARANCE * 2
INNER_D = TOIO_D + CLEARANCE * 2
INNER_H = TOIO_H + CLEARANCE   # tiny top clearance, open bottom

OUTER_W = INNER_W + WALL * 2
OUTER_D = INNER_D + WALL * 2
OUTER_H = INNER_H + TOP
