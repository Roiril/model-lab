"""IVRC booth scale-check params (units: meters)."""

# --- booth footprint ---
BOOTH = 1.8                  # 1800mm — exhibition area edge
FLOOR_THICKNESS = 0.005      # 5mm — visual slab
BORDER_W = 0.03              # 30mm — perimeter highlight strip
BORDER_H = 0.01              # 10mm — slightly raised so boundary reads at a glance

# --- corner posts (volume markers) ---
POST_SIZE = 0.03             # 30mm square
POST_H = 2.0                 # 2000mm — typical booth volume reference

# --- human reference (avg adult ~170cm) ---
HUMAN_H = 1.70
HEAD_R = 0.10                # 200mm head
NECK_R = 0.04
NECK_H = 0.06
TORSO_R_X = 0.20             # shoulder half-width
TORSO_R_Y = 0.12             # chest depth half
TORSO_H = 0.55
HIP_H = 0.10
ARM_R = 0.05
ARM_H = 0.65
LEG_R = 0.08
LEG_H = 0.90
SHOULDER_OFFSET = 0.22       # arm centerline from body axis
LEG_OFFSET = 0.10            # leg centerline from body axis
