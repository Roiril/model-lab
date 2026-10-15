import json
from pathlib import Path

here = Path(__file__).resolve().parent.parent
mount = json.loads((here / "build/v2-mount-interface.json").read_text(encoding="utf-8"))
frame = json.loads((here / "build/v2-frame-interface.json").read_text(encoding="utf-8"))
mount["mount_geometry"].update(frame["mount_geometry"])
mount["frame"] = frame["frame"]
mount["frame"]["assembly_order"] = ["lower_frame", "posts", "carrier_front", "carrier_right",
                                     "wiring", "carrier_back", "carrier_left", "upper_frame", "tray", "faces"]
mount["wiring"].update({
    "bottom_reserved_mm": [56, 40, 11], "bottom_reserved_center_mm": [0, 0, -41.5],
    "print_direction_world": [0, 0, 1], "print_bed_world_z_mm": -47,
    "floor_core_mm": [[-25, -17, -47], [25, 17, -44]],
    "floor_45deg_transition": {"z_mm": [-44, -41], "size_xy_mm": [[50, 34], [56, 40]]},
    "channel_floor_z_mm": [-41, -39], "divider_centers_y_mm": [-12, -4, 4, 12],
    "divider_width_mm": 2, "divider_z_mm": [-39, -36],
    "feet": {"type": "rigid_T_capture", "centers_x_mm": [-14, 14],
             "stem_width_mm": 5, "stem_y_mm": [16.5, 46], "head_width_mm": 7,
             "head_y_mm": [46, 47.5], "z_mm": [-47, -45.45],
             "lower_frame_window": {"y_mm": [42.5, 47.75],
                 "z_width_sections_mm": [[-50.5, 0.5], [-47, 7.5], [-43.8, 7.5]],
                 "foot_down_play_mm": 0.25},
             "back_carrier_notch": {"v_mm": [45.25, 48.5],
                 "d_width_sections_mm": [[2.5, 7.5], [4, 7.5], [5, 5.5], [6.5, 5.5]]},
             "assembly": "Without bottom panel/back carrier: translate y=-4, lower, slide y=+4; capture by back carrier and upper ring.",
             "service": "Remove upper ring and back carrier before withdrawing the guide. Cassette exchange leaves both installed."},
    "tray_mount": {"type": "rigid_35deg_bayonet", "post_z_mm": [-39, -28],
                   "post_clip_radius_mm": 9.8, "hook_outer_x_mm": 10.4,
                   "hook_z_mm": [-30.4, -28], "hook_underside_deg": 45,
                   "tray_throat_outer_x_mm": 10.2, "tray_pocket_outer_x_mm": 10.8,
                   "stop_centers_xy_mm": [[-8, -8], [-8, 8], [8, -8], [8, 8]],
                   "stop_size_xy_mm": [3, 3], "stop_z_mm": [-39, -32.25]},
})
mount["compatibility"] = {"previous": "resident-face-v1", "compatible": False,
    "reason": "Panel width, key heads, receiver ownership and skeleton joints changed for support-free printing.",
    "preserved": ["three datum seats", "asymmetric positioning", "two releasable keys",
                  "40mm normal extraction with all other faces installed", "60mm service wire"]}
target = here / "interface.json"
tmp = target.with_suffix(".json.tmp")
tmp.write_text(json.dumps(mount, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
json.loads(tmp.read_text(encoding="utf-8"))
tmp.replace(target)
