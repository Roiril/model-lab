; HEADER_BLOCK_START
; BambuStudio 02.03.01.51
; model printing time: 26m 18s; total estimated time: 33m 34s
; total layer number: 40
; total filament length [mm] : 5782.90
; total filament volume [cm^3] : 13909.51
; total filament weight [g] : 17.53
; model label id: 8,12,16
; filament_density: 1.26
; filament_diameter: 1.75
; max_z_height: 8.00
; filament: 1
; HEADER_BLOCK_END

; CONFIG_BLOCK_START
; accel_to_decel_enable = 0
; accel_to_decel_factor = 50%
; activate_air_filtration = 0
; additional_cooling_fan_speed = 70
; apply_scarf_seam_on_circles = 1
; apply_top_surface_compensation = 0
; auxiliary_fan = 1
; avoid_crossing_wall_includes_support = 0
; bed_custom_model = 
; bed_custom_texture = 
; bed_exclude_area = 0x0,18x0,18x28,0x28
; bed_temperature_formula = by_first_filament
; before_layer_change_gcode = 
; best_object_pos = 0.5,0.5
; bottom_color_penetration_layers = 3
; bottom_shell_layers = 3
; bottom_shell_thickness = 0
; bottom_surface_pattern = monotonic
; bridge_angle = 0
; bridge_flow = 1
; bridge_no_support = 0
; bridge_speed = 50
; brim_object_gap = 0.1
; brim_type = no_brim
; brim_width = 5
; chamber_temperatures = 0
; change_filament_gcode = ;=X1 20250822=\nM620 S[next_extruder]A\nM204 S9000\nG1 Z{max_layer_z + 3.0} F1200\n\nG1 X70 F21000\nG1 Y245\nG1 Y265 F3000\nM400\nM106 P1 S0\nM106 P2 S0\n{if nozzle_temperature[previous_extruder] > 142 && next_extruder < 255}\nM104 S{nozzle_temperature[previous_extruder]}\n{endif}\n{if long_retractions_when_cut[previous_extruder]}\nM620.11 S1 I[previous_extruder] E-{retraction_distances_when_cut[previous_extruder]} F{flush_volumetric_speeds[previous_extruder]/2.4053*60}\n{else}\nM620.11 S0\n{endif}\nM400\nG1 X90 F3000\nG1 Y255 F4000\nG1 X100 F5000\nG1 X120 F15000\nG1 X20 Y50 F21000\nG1 Y-3\n{if toolchange_count == 2}\n; get travel path for change filament\nM620.1 X[travel_point_1_x] Y[travel_point_1_y] F21000 P0\nM620.1 X[travel_point_2_x] Y[travel_point_2_y] F21000 P1\nM620.1 X[travel_point_3_x] Y[travel_point_3_y] F21000 P2\n{endif}\nM620.1 E F{flush_volumetric_speeds[previous_extruder]/2.4053*60} T{flush_temperatures[previous_extruder]}\nT[next_extruder]\nM620.1 E F{flush_volumetric_speeds[next_extruder]/2.4053*60} T{flush_temperatures[next_extruder]}\n\n{if next_extruder < 255}\n{if long_retractions_when_cut[previous_extruder]}\nM620.11 S1 I[previous_extruder] E{retraction_distances_when_cut[previous_extruder]} F{flush_volumetric_speeds[previous_extruder]/2.4053*60}\nM628 S1\nG92 E0\nG1 E{retraction_distances_when_cut[previous_extruder]} F{flush_volumetric_speeds[previous_extruder]/2.4053*60}\nM400\nM629 S1\n{else}\nM620.11 S0\n{endif}\nG92 E0\n{if flush_length_1 > 1}\nM83\n; FLUSH_START\n; always use highest temperature to flush\nM400\n{if filament_type[next_extruder] == "PETG"}\nM109 S260\n{elsif filament_type[next_extruder] == "PVA"}\nM109 S210\n{else}\nM109 S{flush_temperatures[next_extruder]}\n{endif}\n{if flush_length_1 > 23.7}\nG1 E23.7 F{flush_volumetric_speeds[previous_extruder]/2.4053*60} ; do not need pulsatile flushing for start part\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{flush_volumetric_speeds[previous_extruder]/2.4053*60}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\n{else}\nG1 E{flush_length_1} F{flush_volumetric_speeds[previous_extruder]/2.4053*60}\n{endif}\n; FLUSH_END\nG1 E-[old_retract_length_toolchange] F1800\nG1 E[old_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_2 > 1}\n\nG91\nG1 X3 F12000; move aside to extrude\nG90\nM83\n\n; FLUSH_START\nG1 E{flush_length_2 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_2 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_3 > 1}\n\nG91\nG1 X3 F12000; move aside to extrude\nG90\nM83\n\n; FLUSH_START\nG1 E{flush_length_3 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_3 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_4 > 1}\n\nG91\nG1 X3 F12000; move aside to extrude\nG90\nM83\n\n; FLUSH_START\nG1 E{flush_length_4 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{flush_volumetric_speeds[next_extruder]/2.4053*60}\nG1 E{flush_length_4 * 0.02} F50\n; FLUSH_END\n{endif}\n; FLUSH_START\nM400\nM109 S{nozzle_temperature[next_extruder]}\nG1 E2 F{flush_volumetric_speeds[next_extruder]/2.4053*60} ;Compensate for filament spillage during waiting temperature\n; FLUSH_END\nM400\nG92 E0\nG1 E-[new_retract_length_toolchange] F1800\nM106 P1 S255\nM400 S3\n\nG1 X70 F5000\nG1 X90 F3000\nG1 Y255 F4000\nG1 X105 F5000\nG1 Y265 F5000\nG1 X70 F10000\nG1 X100 F5000\nG1 X70 F10000\nG1 X100 F5000\n\nG1 X70 F10000\nG1 X80 F15000\nG1 X60\nG1 X80\nG1 X60\nG1 X80 ; shake to put down garbage\nG1 X100 F5000\nG1 X165 F15000; wipe and shake\nG1 Y256 ; move Y to aside, prevent collision\nM400\nG1 Z{max_layer_z + 3.0} F3000\n{if layer_z <= (initial_layer_print_height + 0.001)}\nM204 S[initial_layer_acceleration]\n{else}\nM204 S[default_acceleration]\n{endif}\n{else}\nG1 X[x_after_toolchange] Y[y_after_toolchange] Z[z_after_toolchange] F12000\n{endif}\nM621 S[next_extruder]A\n
; circle_compensation_manual_offset = 0
; circle_compensation_speed = 200
; close_fan_the_first_x_layers = 1
; compatible_printers_condition = 
; complete_print_exhaust_fan_speed = 70
; cool_plate_temp = 35
; cool_plate_temp_initial_layer = 35
; counter_coef_1 = 0
; counter_coef_2 = 0.008
; counter_coef_3 = -0.041
; counter_limit_max = 0.033
; counter_limit_min = -0.035
; curr_bed_type = Textured PEI Plate
; default_acceleration = 10000
; default_filament_colour = ""
; default_filament_profile = "Bambu PLA Basic @BBL X1C"
; default_jerk = 0
; default_nozzle_volume_type = Standard
; default_print_profile = 0.20mm Standard @BBL X1C
; deretraction_speed = 30
; detect_floating_vertical_shell = 1
; detect_narrow_internal_solid_infill = 1
; detect_overhang_wall = 1
; detect_thin_wall = 0
; diameter_limit = 50
; different_settings_to_system = ;;
; draft_shield = disabled
; during_print_exhaust_fan_speed = 70
; elefant_foot_compensation = 0.15
; enable_arc_fitting = 1
; enable_circle_compensation = 0
; enable_height_slowdown = 0
; enable_long_retraction_when_cut = 2
; enable_overhang_bridge_fan = 1
; enable_overhang_speed = 1
; enable_pre_heating = 0
; enable_pressure_advance = 0
; enable_prime_tower = 0
; enable_support = 0
; enable_wrapping_detection = 0
; enforce_support_layers = 0
; eng_plate_temp = 0
; eng_plate_temp_initial_layer = 0
; ensure_vertical_shell_thickness = enabled
; exclude_object = 1
; extruder_ams_count = 
; extruder_clearance_dist_to_rod = 33
; extruder_clearance_height_to_lid = 90
; extruder_clearance_height_to_rod = 34
; extruder_clearance_max_radius = 68
; extruder_colour = #018001
; extruder_offset = 0x2
; extruder_printable_area = 
; extruder_type = Direct Drive
; extruder_variant_list = "Direct Drive Standard,Direct Drive High Flow"
; fan_cooling_layer_time = 100
; fan_direction = left
; fan_max_speed = 100
; fan_min_speed = 100
; filament_adaptive_volumetric_speed = 0
; filament_adhesiveness_category = 100
; filament_change_length = 5
; filament_colour = #00AE42
; filament_cost = 24.99
; filament_density = 1.26
; filament_diameter = 1.75
; filament_end_gcode = "; filament end gcode \n\n"
; filament_extruder_variant = "Direct Drive Standard"
; filament_flow_ratio = 0.98
; filament_flush_temp = 0
; filament_flush_volumetric_speed = 0
; filament_ids = GFA00
; filament_is_support = 0
; filament_long_retractions_when_cut = 1
; filament_map = 1
; filament_map_mode = Auto For Flush
; filament_max_volumetric_speed = 21
; filament_minimal_purge_on_wipe_tower = 15
; filament_notes = 
; filament_pre_cooling_temperature = 0
; filament_prime_volume = 30
; filament_printable = 3
; filament_ramming_travel_time = 0
; filament_ramming_volumetric_speed = -1
; filament_retraction_distances_when_cut = 18
; filament_scarf_gap = 0%
; filament_scarf_height = 10%
; filament_scarf_length = 10
; filament_scarf_seam_type = none
; filament_self_index = 1,1
; filament_settings_id = "Bambu PLA Basic @BBL X1C"
; filament_shrink = 100%
; filament_soluble = 0
; filament_start_gcode = "; filament start gcode\n{if  (bed_temperature[current_extruder] >55)||(bed_temperature_initial_layer[current_extruder] >55)}M106 P3 S200\n{elsif(bed_temperature[current_extruder] >50)||(bed_temperature_initial_layer[current_extruder] >50)}M106 P3 S150\n{elsif(bed_temperature[current_extruder] >45)||(bed_temperature_initial_layer[current_extruder] >45)}M106 P3 S50\n{endif}\nM142 P1 R35 S40\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"
; filament_type = PLA
; filament_velocity_adaptation_factor = 1
; filament_vendor = "Bambu Lab"
; filename_format = {input_filename_base}_{filament_type[0]}_{print_time}.gcode
; filter_out_gap_fill = 0
; first_layer_print_sequence = 0
; first_x_layer_fan_speed = 0
; flush_into_infill = 0
; flush_into_objects = 0
; flush_into_support = 1
; flush_multiplier = 1
; flush_volumes_matrix = 0,280,280,280,280,0,280,280,280,280,0,280,280,280,280,0
; flush_volumes_vector = 140,140,140,140,140,140,140,140
; full_fan_speed_layer = 0
; fuzzy_skin = none
; fuzzy_skin_point_distance = 0.8
; fuzzy_skin_thickness = 0.3
; gap_infill_speed = 250
; gcode_add_line_number = 0
; gcode_flavor = marlin
; grab_length = 0
; has_scarf_joint_seam = 0
; head_wrap_detect_zone = 
; hole_coef_1 = 0
; hole_coef_2 = -0.008
; hole_coef_3 = 0.23415
; hole_limit_max = 0.22
; hole_limit_min = 0.088
; hot_plate_temp = 55
; hot_plate_temp_initial_layer = 55
; hotend_cooling_rate = 2
; hotend_heating_rate = 2
; impact_strength_z = 13.8
; independent_support_layer_height = 1
; infill_combination = 0
; infill_direction = 45
; infill_jerk = 9
; infill_lock_depth = 1
; infill_rotate_step = 0
; infill_shift_step = 0.4
; infill_wall_overlap = 15%
; inherits_group = ;;
; initial_layer_acceleration = 500
; initial_layer_flow_ratio = 1
; initial_layer_infill_speed = 105
; initial_layer_jerk = 9
; initial_layer_line_width = 0.5
; initial_layer_print_height = 0.2
; initial_layer_speed = 50
; initial_layer_travel_acceleration = 6000
; inner_wall_acceleration = 0
; inner_wall_jerk = 9
; inner_wall_line_width = 0.45
; inner_wall_speed = 300
; interface_shells = 0
; interlocking_beam = 0
; interlocking_beam_layer_count = 2
; interlocking_beam_width = 0.8
; interlocking_boundary_avoidance = 2
; interlocking_depth = 2
; interlocking_orientation = 22.5
; internal_bridge_support_thickness = 0.8
; internal_solid_infill_line_width = 0.42
; internal_solid_infill_pattern = zig-zag
; internal_solid_infill_speed = 250
; ironing_direction = 45
; ironing_flow = 10%
; ironing_inset = 0.21
; ironing_pattern = zig-zag
; ironing_spacing = 0.15
; ironing_speed = 30
; ironing_type = no ironing
; is_infill_first = 0
; layer_change_gcode = ; layer num/total_layer_count: {layer_num+1}/[total_layer_count]\n; update layer progress\nM73 L{layer_num+1}\nM991 S0 P{layer_num} ;notify layer change
; layer_height = 0.2
; line_width = 0.42
; locked_skeleton_infill_pattern = zigzag
; locked_skin_infill_pattern = crosszag
; long_retractions_when_cut = 0
; long_retractions_when_ec = 0
; machine_end_gcode = ;===== date: 20240528 =====================\nM400 ; wait for buffer to clear\nG92 E0 ; zero the extruder\nG1 E-0.8 F1800 ; retract\nG1 Z{max_layer_z + 0.5} F900 ; lower z a little\nG1 X65 Y245 F12000 ; move to safe pos\nG1 Y265 F3000\n\nG1 X65 Y245 F12000\nG1 Y265 F3000\nM140 S0 ; turn off bed\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off remote part cooling fan\nM106 P3 S0 ; turn off chamber cooling fan\n\nG1 X100 F12000 ; wipe\n; pull back filament to AMS\nM620 S255\nG1 X20 Y50 F12000\nG1 Y-3\nT255\nG1 X65 F12000\nG1 Y265\nG1 X100 F12000 ; wipe\nM621 S255\nM104 S0 ; turn off hotend\n\nM622.1 S1 ; for prev firmware, default turned on\nM1002 judge_flag timelapse_record_flag\nM622 J1\n    M400 ; wait all motion done\n    M991 S0 P-1 ;end smooth timelapse at safe pos\n    M400 S3 ;wait for last picture to be taken\nM623; end of "timelapse_record_flag"\n\nM400 ; wait all motion done\nM17 S\nM17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom\n{if (max_layer_z + 100.0) < 250}\n    G1 Z{max_layer_z + 100.0} F600\n    G1 Z{max_layer_z +98.0}\n{else}\n    G1 Z250 F600\n    G1 Z248\n{endif}\nM400 P100\nM17 R ; restore z current\n\nM220 S100  ; Reset feedrate magnitude\nM201.2 K1.0 ; Reset acc magnitude\nM73.2   R1.0 ;Reset left time magnitude\nM1002 set_gcode_claim_speed_level : 0\n;=====printer finish  sound=========\nM17\nM400 S1\nM1006 S1\nM1006 A0 B20 L100 C37 D20 M40 E42 F20 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C46 D10 M80 E46 F10 N80\nM1006 A44 B20 L100 C39 D20 M60 E48 F20 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C39 D10 M60 E39 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C39 D10 M60 E39 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C48 D10 M60 E44 F10 N100\nM1006 A0 B10 L100 C0 D10 M60 E0 F10  N100\nM1006 A49 B20 L100 C44 D20 M100 E41 F20 N100\nM1006 A0 B20 L100 C0 D20 M60 E0 F20 N100\nM1006 A0 B20 L100 C37 D20 M30 E37 F20 N60\nM1006 W\n\nM17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power\nM960 S5 P0 ; turn off logo lamp\n
; machine_load_filament_time = 29
; machine_max_acceleration_e = 5000,5000
; machine_max_acceleration_extruding = 20000,20000
; machine_max_acceleration_retracting = 5000,5000
; machine_max_acceleration_travel = 9000,9000
; machine_max_acceleration_x = 20000,20000
; machine_max_acceleration_y = 20000,20000
; machine_max_acceleration_z = 500,200
; machine_max_jerk_e = 2.5,2.5
; machine_max_jerk_x = 9,9
; machine_max_jerk_y = 9,9
; machine_max_jerk_z = 3,3
; machine_max_speed_e = 30,30
; machine_max_speed_x = 500,200
; machine_max_speed_y = 500,200
; machine_max_speed_z = 20,20
; machine_min_extruding_rate = 0
; machine_min_travel_rate = 0
; machine_pause_gcode = M400 U1
; machine_prepare_compensation_time = 260
; machine_start_gcode = ;===== machine: X1-0.4 ====================\n;===== date: 20250909 ==================\n;===== start printer sound ================\nM17\nM400 S1\nM1006 S1\nM1006 A0 B10 L100 C37 D10 M60 E37 F10 N60\nM1006 A0 B10 L100 C41 D10 M60 E41 F10 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A46 B10 L100 C43 D10 M70 E39 F10 N100\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N100\nM1006 A43 B10 L100 C0 D10 M60 E39 F10 N100\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N100\nM1006 A41 B10 L100 C0 D10 M100 E41 F10 N100\nM1006 A44 B10 L100 C0 D10 M100 E44 F10 N100\nM1006 A49 B10 L100 C0 D10 M100 E49 F10 N100\nM1006 A0 B10 L100 C0 D10 M100 E0 F10 N100\nM1006 A48 B10 L100 C44 D10 M60 E39 F10 N100\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N100\nM1006 A44 B10 L100 C0 D10 M90 E39 F10 N100\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N100\nM1006 A46 B10 L100 C43 D10 M60 E39 F10 N100\nM1006 W\n;===== turn on the HB fan =================\nM104 S75 ;set extruder temp to turn on the HB fan and prevent filament oozing from nozzle\n;===== reset machine status =================\nM290 X40 Y40 Z2.6666666\nG91\nM17 Z0.4 ; lower the z-motor current\nG380 S2 Z30 F300 ; G380 is same as G38; lower the hotbed , to prevent the nozzle is below the hotbed\nG380 S2 Z-25 F300 ;\nG1 Z5 F300;\nG90\nM17 X1.2 Y1.2 Z0.75 ; reset motor current to default\nM960 S5 P1 ; turn on logo lamp\nG90\nM220 S100 ;Reset Feedrate\nM221 S100 ;Reset Flowrate\nM73.2   R1.0 ;Reset left time magnitude\nM1002 set_gcode_claim_speed_level : 5\nM221 X0 Y0 Z0 ; turn off soft endstop to prevent protential logic problem\nG29.1 Z{+0.0} ; clear z-trim value first\nM204 S10000 ; init ACC set to 10m/s^2\n\n;===== heatbed preheat ====================\nM1002 gcode_claim_action : 2\nM140 S[bed_temperature_initial_layer_single] ;set bed temp\nM190 S[bed_temperature_initial_layer_single] ;wait for bed temp\n\n{if scan_first_layer}\n;=========register first layer scan=====\nM977 S1 P60\n{endif}\n\n;=============turn on fans to prevent PLA jamming=================\n{if filament_type[initial_no_support_extruder]=="PLA"}\n    {if (bed_temperature[initial_no_support_extruder] >45)||(bed_temperature_initial_layer[initial_no_support_extruder] >45)}\n    M106 P3 S180\n    {endif};Prevent PLA from jamming\n    M142 P1 R35 S40\n{endif}\nM106 P2 S100 ; turn on big fan ,to cool down toolhead\n\n;===== prepare print temperature and material ==========\nM104 S[nozzle_temperature_initial_layer] ;set extruder temp\nG91\nG0 Z10 F1200\nG90\nG28 X\nM975 S1 ; turn on\nG1 X60 F12000\nG1 Y245\nG1 Y265 F3000\nM620 M\nM620 S[initial_no_support_extruder]A   ; switch material if AMS exist\n    M109 S[nozzle_temperature_initial_layer]\n    G1 X120 F12000\n\n    G1 X20 Y50 F12000\n    G1 Y-3\n    T[initial_no_support_extruder]\n    G1 X54 F12000\n    G1 Y265\n    M400\nM621 S[initial_no_support_extruder]A\nM620.1 E F{flush_volumetric_speeds[initial_no_support_extruder]/2.4053*60} T{flush_temperatures[initial_no_support_extruder]}\n\nM412 S1 ; ===turn on filament runout detection===\n\nM109 S250 ;set nozzle to common flush temp\nM106 P1 S0\nG92 E0\nG1 E50 F200\nM400\nM104 S[nozzle_temperature_initial_layer]\nG92 E0\nG1 E50 F200\nM400\nM106 P1 S255\nG92 E0\nG1 E5 F300\nM109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]-20} ; drop nozzle temp, make filament shink a bit\nG92 E0\nG1 E-0.5 F300\n\nG1 X70 F9000\nG1 X76 F15000\nG1 X65 F15000\nG1 X76 F15000\nG1 X65 F15000; shake to put down garbage\nG1 X80 F6000\nG1 X95 F15000\nG1 X80 F15000\nG1 X165 F15000; wipe and shake\nM400\nM106 P1 S0\n;===== prepare print temperature and material end =====\n\n\n;===== wipe nozzle ===============================\nM1002 gcode_claim_action : 14\nM975 S1\nM106 S255\nG1 X65 Y230 F18000\nG1 Y264 F6000\nM109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]-20}\nG1 X100 F18000 ; first wipe mouth\n\nG0 X135 Y253 F20000  ; move to exposed steel surface edge\nG28 Z P0 T300; home z with low precision,permit 300deg temperature\nG29.2 S0 ; turn off ABL\nG0 Z5 F20000\n\nG1 X60 Y265\nG92 E0\nG1 E-0.5 F300 ; retrack more\nG1 X100 F5000; second wipe mouth\nG1 X70 F15000\nG1 X100 F5000\nG1 X70 F15000\nG1 X100 F5000\nG1 X70 F15000\nG1 X100 F5000\nG1 X70 F15000\nG1 X90 F5000\nG0 X128 Y261 Z-1.5 F20000  ; move to exposed steel surface and stop the nozzle\nM104 S140 ; set temp down to heatbed acceptable\nM106 S255 ; turn on fan (G28 has turn off fan)\n\nM221 S; push soft endstop status\nM221 Z0 ;turn off Z axis endstop\nG0 Z0.5 F20000\nG0 X125 Y259.5 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y262.5\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y260.0\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y262.0\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y260.5\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y261.5\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 Z0.5 F20000\nG0 X125 Y261.0\nG0 Z-1.01\nG0 X131 F211\nG0 X124\nG0 X128\nG2 I0.5 J0 F300\nG2 I0.5 J0 F300\nG2 I0.5 J0 F300\nG2 I0.5 J0 F300\n\nM109 S140 ; wait nozzle temp down to heatbed acceptable\nG2 I0.5 J0 F3000\nG2 I0.5 J0 F3000\nG2 I0.5 J0 F3000\nG2 I0.5 J0 F3000\n\nM221 R; pop softend status\nG1 Z10 F1200\nM400\nG1 Z10\nG1 F30000\nG1 X128 Y128\nG29.2 S1 ; turn on ABL\n;G28 ; home again after hard wipe mouth\nM106 S0 ; turn off fan , too noisy\n;===== wipe nozzle end ================================\n\n;===== check scanner clarity ===========================\nG1 X128 Y128 F24000\nG28 Z P0\nM972 S5 P0\nG1 X230 Y15 F24000\n;===== check scanner clarity end =======================\n\n;===== bed leveling ==================================\nM1002 judge_flag g29_before_print_flag\nM622 J1\n\n    M1002 gcode_claim_action : 1\n    G29 A X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]}\n    M400\n    M500 ; save cali data\n\nM623\n;===== bed leveling end ================================\n\n;===== home after wipe mouth============================\nM1002 judge_flag g29_before_print_flag\nM622 J0\n\n    M1002 gcode_claim_action : 13\n    G28\n\nM623\n;===== home after wipe mouth end =======================\n\nM975 S1 ; turn on vibration supression\n\n;=============turn on fans to prevent PLA jamming=================\n{if filament_type[initial_no_support_extruder]=="PLA"}\n    {if (bed_temperature[initial_no_support_extruder] >45)||(bed_temperature_initial_layer[initial_no_support_extruder] >45)}\n    M106 P3 S180\n    {endif};Prevent PLA from jamming\n    M142 P1 R35 S40\n{endif}\nM106 P2 S100 ; turn on big fan ,to cool down toolhead\n\nM104 S{nozzle_temperature_initial_layer[initial_no_support_extruder]} ; set extrude temp earlier, to reduce wait time\n\n;===== mech mode fast check============================\nG1 X128 Y128 Z10 F20000\nM400 P200\nM970.3 Q1 A7 B30 C80  H15 K0\nM974 Q1 S2 P0\n\nG1 X128 Y128 Z10 F20000\nM400 P200\nM970.3 Q0 A7 B30 C90 Q0 H15 K0\nM974 Q0 S2 P0\n\nM975 S1\nG1 F30000\nG1 X230 Y15\nG28 X ; re-home XY\n;===== mech mode fast check============================\n\n{if scan_first_layer}\n;start heatbed  scan====================================\nM976 S2 P1\nG90\nG1 X128 Y128 F20000\nM976 S3 P2  ;register void printing detection\n{endif}\n\n;===== nozzle load line ===============================\nM975 S1\nG90\nM83\nT1000\nG1 X18.0 Y1.0 Z0.8 F18000;Move to start position\nM109 S{nozzle_temperature[initial_no_support_extruder]}\nG1 Z0.2\nG0 E2 F300\nG0 X240 E15 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\nG0 Y11 E0.700 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\nG0 X239.5\nG0 E0.2\nG0 Y1.5 E0.700\nG0 X231 E0.700 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\nM400\n\n;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==\n;curr_bed_type={curr_bed_type}\n{if curr_bed_type=="Textured PEI Plate"}\nG29.1 Z{-0.04} ; for Textured PEI Plate\n{endif}\n\n;===== draw extrinsic para cali paint =================\nM1002 judge_flag extrude_cali_flag\nM622 J1\n\n    M1002 gcode_claim_action : 8\n\n    T1000\n\n    G0 F1200.0 X231 Y12   Z0.2 E0.577\n    G0 F1200.0 X226 Y12   Z0.2 E0.275\n    G0 F1200.0 X226 Y1.5  Z0.2 E0.577\n    G0 F1200.0 X220 Y1.5  Z0.2 E0.330\n    G0 F1200.0 X220 Y8    Z0.2 E0.358\n    G0 F1200.0 X210 Y8    Z0.2 E0.549\n    G0 F1200.0 X210 Y1.5  Z0.2 E0.357\n\n    G0 X48.0 E11.9 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\n    G0 X48.0 Y12 E0.772 F1200.0\n    G0 X45.0 E0.22 F1200.0\n    G0 X35.0 Y6.0 E0.86 F1200.0\n\n    ;=========== extruder cali extrusion ==================\n    T1000\n    M83\n    {if default_acceleration > 0}\n        {if outer_wall_acceleration > 0}\n            M204 S[outer_wall_acceleration]\n        {else}\n            M204 S[default_acceleration]\n        {endif}\n    {endif}\n    G0 X35.000 Y6.000 Z0.300 F30000 E0\n    G1 F1500.000 E0.800\n    M106 S0 ; turn off fan\n    G0 X185.000 E9.35441 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G0 X187 Z0\n    G1 F1500.000 E-0.800\n    G0 Z1\n    G0 X180 Z0.3 F18000\n\n    M900 L1000.0 M1.0\n    M900 K0.040\n    G0 X45.000 F30000\n    G0 Y8.000 F30000\n    G1 F1500.000 E0.800\n    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 F1500.000 E-0.800\n    G1 X183 Z0.15 F30000\n    G1 X185\n    G1 Z1.0\n    G0 Y6.000 F30000 ; move y to clear pos\n    G1 Z0.3\n    M400\n\n    G0 X45.000 F30000\n    M900 K0.020\n    G0 X45.000 F30000\n    G0 Y10.000 F30000\n    G1 F1500.000 E0.800\n    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 F1500.000 E-0.800\n    G1 X183 Z0.15 F30000\n    G1 X185\n    G1 Z1.0\n    G0 Y6.000 F30000 ; move y to clear pos\n    G1 Z0.3\n    M400\n\n    G0 X45.000 F30000\n    M900 K0.000\n    G0 X45.000 F30000\n    G0 Y12.000 F30000\n    G1 F1500.000 E0.800\n    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 F1500.000 E-0.800\n    G1 X183 Z0.15 F30000\n    G1 X185\n    G1 Z1.0\n    G0 Y6.000 F30000 ; move y to clear pos\n    G1 Z0.3\n\n    G0 X45.000 F30000 ; move to start point\n\nM623 ; end of "draw extrinsic para cali paint"\n\n\nM1002 judge_flag extrude_cali_flag\nM622 J0\n    G0 X231 Y1.5 F30000\n    G0 X18 E14.3 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\nM623\n\nM104 S140\n\n\n;=========== laser and rgb calibration ===========\nM400\nM18 E\nM500 R\n\nM973 S3 P14\n\nG1 X120 Y1.0 Z0.3 F18000.0;Move to first extrude line pos\nT1100\nG1 X235.0 Y1.0 Z0.3 F18000.0;Move to first extrude line pos\nM400 P100\nM960 S1 P1\nM400 P100\nM973 S6 P0; use auto exposure for horizontal laser by xcam\nM960 S0 P0\n\nG1 X240.0 Y6.0 Z0.3 F18000.0;Move to vertical extrude line pos\nM960 S2 P1\nM400 P100\nM973 S6 P1; use auto exposure for vertical laser by xcam\nM960 S0 P0\n\n;=========== handeye calibration ======================\nM1002 judge_flag extrude_cali_flag\nM622 J1\n\n    M973 S3 P1 ; camera start stream\n    M400 P500\n    M973 S1\n    G0 F6000 X228.500 Y4.750 Z0.000\n    M960 S0 P1\n    M973 S1\n    M400 P800\n    M971 S6 P0\n    M973 S2 P0\n    M400 P500\n    G0 Z0.000 F12000\n    M960 S0 P0\n    M960 S1 P1\n    G0 X215.00 Y4.750\n    M400 P200\n    M971 S5 P1\n    M973 S2 P1\n    M400 P500\n    M960 S0 P0\n    M960 S2 P1\n    G0 X228.5 Y6.75\n    M400 P200\n    M971 S5 P3\n    G0 Z0.500 F12000\n    M960 S0 P0\n    M960 S2 P1\n    G0 X228.5 Y6.75\n    M400 P200\n    M971 S5 P4\n    M973 S2 P0\n    M400 P500\n    M960 S0 P0\n    M960 S1 P1\n    G0 X215.00 Y4.750\n    M400 P500\n    M971 S5 P2\n    M963 S1\n    M400 P1500\n    M964\n    T1100\n    G1 Z3 F3000\n\n    M400\n    M500 ; save cali data\n\n    M104 S{nozzle_temperature[initial_no_support_extruder]} ; rise nozzle temp now ,to reduce temp waiting time.\n\n    T1100\n    M400 P400\n    M960 S0 P0\n    G0 F30000.000 Y10.000 X65.000 Z0.000\n    M400 P400\n    M960 S1 P1\n    M400 P50\n\n    M969 S1 N3 A2000\n    G0 F360.000 X181.000 Z0.000\n    M980.3 A70.000 B{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*60/4} C5.000 D{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*60} E5.000 F175.000 H1.000 I0.000 J0.020 K0.040\n    M400 P100\n    G0 F20000\n    G0 Z1 ; rise nozzle up\n    T1000 ; change to nozzle space\n    G0 X45.000 Y4.000 F30000 ; move to test line pos\n    M969 S0 ; turn off scanning\n    M960 S0 P0\n\n\n    G1 Z2 F20000\n    T1000\n    G0 X45.000 Y4.000 F30000 E0\n    M109 S{nozzle_temperature[initial_no_support_extruder]}\n    G0 Z0.3\n    G1 F1500.000 E3.600\n    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n\n    ; see if extrude cali success, if not ,use default value\n    M1002 judge_last_extrude_cali_success\n    M622 J0\n        M400\n        M900 K0.02 M{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*0.02}\n    M623\n\n    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X185.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X190.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X195.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X200.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X205.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X210.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X215.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    G1 X220.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}\n    G1 X225.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\n    M973 S4\n\nM623\n\n;========turn off light and wait extrude temperature =============\nM1002 gcode_claim_action : 0\nM973 S4 ; turn off scanner\nM400 ; wait all motion done before implement the emprical L parameters\n;M900 L500.0 ; Empirical parameters\nM109 S[nozzle_temperature_initial_layer]\nM960 S1 P0 ; turn off laser\nM960 S2 P0 ; turn off laser\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off big fan\nM106 P3 S0 ; turn off chamber fan\n\nM975 S1 ; turn on mech mode supression\nG90\nM83\nT1000\n;===== purge line to wipe the nozzle ============================\nG1 E{-retraction_length[initial_no_support_extruder]} F1800\nG1 X18.0 Y2.5 Z0.8 F18000.0;Move to start position\nG1 E{retraction_length[initial_no_support_extruder]} F1800\nM109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]}\nG1 Z0.2\nG0 X239 E15 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}\nG0 Y12 E0.7 F{outer_wall_volumetric_speed/(0.3*0.5)/4* 60}\n
; machine_switch_extruder_time = 0
; machine_unload_filament_time = 28
; master_extruder_id = 1
; max_bridge_length = 0
; max_layer_height = 0.28
; max_travel_detour_distance = 0
; min_bead_width = 85%
; min_feature_size = 25%
; min_layer_height = 0.08
; minimum_sparse_infill_area = 15
; mmu_segmented_region_interlocking_depth = 0
; mmu_segmented_region_max_width = 0
; no_slow_down_for_cooling_on_outwalls = 0
; nozzle_diameter = 0.4
; nozzle_flush_dataset = 0
; nozzle_height = 4.2
; nozzle_temperature = 220
; nozzle_temperature_initial_layer = 220
; nozzle_temperature_range_high = 240
; nozzle_temperature_range_low = 190
; nozzle_type = hardened_steel
; nozzle_volume = 107
; nozzle_volume_type = Standard
; only_one_wall_first_layer = 0
; ooze_prevention = 0
; other_layers_print_sequence = 0
; other_layers_print_sequence_nums = 0
; outer_wall_acceleration = 5000
; outer_wall_jerk = 9
; outer_wall_line_width = 0.42
; outer_wall_speed = 200
; overhang_1_4_speed = 0
; overhang_2_4_speed = 50
; overhang_3_4_speed = 30
; overhang_4_4_speed = 10
; overhang_fan_speed = 100
; overhang_fan_threshold = 50%
; overhang_threshold_participating_cooling = 95%
; overhang_totally_speed = 10
; override_filament_scarf_seam_setting = 0
; physical_extruder_map = 0
; post_process = 
; pre_start_fan_time = 0
; precise_outer_wall = 0
; precise_z_height = 0
; pressure_advance = 0.02
; prime_tower_brim_width = 3
; prime_tower_enable_framework = 0
; prime_tower_extra_rib_length = 0
; prime_tower_fillet_wall = 1
; prime_tower_flat_ironing = 0
; prime_tower_infill_gap = 150%
; prime_tower_lift_height = -1
; prime_tower_lift_speed = 90
; prime_tower_max_speed = 90
; prime_tower_rib_wall = 1
; prime_tower_rib_width = 8
; prime_tower_skip_points = 1
; prime_tower_width = 35
; print_compatible_printers = "Bambu Lab X1 Carbon 0.4 nozzle";"Bambu Lab X1 0.4 nozzle";"Bambu Lab P1S 0.4 nozzle";"Bambu Lab X1E 0.4 nozzle"
; print_extruder_id = 1
; print_extruder_variant = "Direct Drive Standard"
; print_flow_ratio = 1
; print_sequence = by layer
; print_settings_id = 0.20mm Standard @BBL X1C
; printable_area = 0x0,256x0,256x256,0x256
; printable_height = 250
; printer_extruder_id = 1
; printer_extruder_variant = "Direct Drive Standard"
; printer_model = Bambu Lab X1 Carbon
; printer_notes = 
; printer_settings_id = Bambu Lab X1 Carbon 0.4 nozzle
; printer_structure = corexy
; printer_technology = FFF
; printer_variant = 0.4
; printing_by_object_gcode = 
; process_notes = 
; raft_contact_distance = 0.1
; raft_expansion = 1.5
; raft_first_layer_density = 90%
; raft_first_layer_expansion = -1
; raft_layers = 0
; reduce_crossing_wall = 0
; reduce_fan_stop_start_freq = 1
; reduce_infill_retraction = 1
; required_nozzle_HRC = 3
; resolution = 0.012
; retract_before_wipe = 0%
; retract_length_toolchange = 2
; retract_lift_above = 0
; retract_lift_below = 249
; retract_restart_extra = 0
; retract_restart_extra_toolchange = 0
; retract_when_changing_layer = 1
; retraction_distances_when_cut = 18
; retraction_distances_when_ec = 0
; retraction_length = 0.8
; retraction_minimum_travel = 1
; retraction_speed = 30
; role_base_wipe_speed = 1
; scan_first_layer = 1
; scarf_angle_threshold = 155
; seam_gap = 15%
; seam_placement_away_from_overhangs = 0
; seam_position = back
; seam_slope_conditional = 1
; seam_slope_entire_loop = 0
; seam_slope_gap = 0
; seam_slope_inner_walls = 1
; seam_slope_min_length = 10
; seam_slope_start_height = 10%
; seam_slope_steps = 10
; seam_slope_type = none
; silent_mode = 0
; single_extruder_multi_material = 1
; skeleton_infill_density = 15%
; skeleton_infill_line_width = 0.45
; skin_infill_density = 15%
; skin_infill_depth = 2
; skin_infill_line_width = 0.45
; skirt_distance = 2
; skirt_height = 1
; skirt_loops = 0
; slice_closing_radius = 0.049
; slicing_mode = regular
; slow_down_for_layer_cooling = 1
; slow_down_layer_time = 4
; slow_down_min_speed = 20
; slowdown_end_acc = 100000
; slowdown_end_height = 400
; slowdown_end_speed = 1000
; slowdown_start_acc = 100000
; slowdown_start_height = 0
; slowdown_start_speed = 1000
; small_perimeter_speed = 50%
; small_perimeter_threshold = 0
; smooth_coefficient = 150
; smooth_speed_discontinuity_area = 1
; solid_infill_filament = 1
; sparse_infill_acceleration = 100%
; sparse_infill_anchor = 400%
; sparse_infill_anchor_max = 20
; sparse_infill_density = 15%
; sparse_infill_filament = 1
; sparse_infill_line_width = 0.45
; sparse_infill_pattern = grid
; sparse_infill_speed = 270
; spiral_mode = 0
; spiral_mode_max_xy_smoothing = 200%
; spiral_mode_smooth = 0
; standby_temperature_delta = -5
; start_end_points = 30x-3,54x245
; supertack_plate_temp = 45
; supertack_plate_temp_initial_layer = 45
; support_air_filtration = 0
; support_angle = 0
; support_base_pattern = default
; support_base_pattern_spacing = 2.5
; support_bottom_interface_spacing = 0.5
; support_bottom_z_distance = 0.2
; support_chamber_temp_control = 0
; support_critical_regions_only = 0
; support_expansion = 0
; support_filament = 0
; support_interface_bottom_layers = 2
; support_interface_filament = 0
; support_interface_loop_pattern = 0
; support_interface_not_for_body = 1
; support_interface_pattern = auto
; support_interface_spacing = 0.5
; support_interface_speed = 80
; support_interface_top_layers = 2
; support_line_width = 0.42
; support_object_first_layer_gap = 0.2
; support_object_skip_flush = 0
; support_object_xy_distance = 0.35
; support_on_build_plate_only = 0
; support_remove_small_overhang = 1
; support_speed = 150
; support_style = default
; support_threshold_angle = 30
; support_top_z_distance = 0.2
; support_type = tree(auto)
; symmetric_infill_y_axis = 0
; temperature_vitrification = 45
; template_custom_gcode = 
; textured_plate_temp = 55
; textured_plate_temp_initial_layer = 55
; thick_bridges = 0
; thumbnail_size = 50x50
; time_lapse_gcode = ;========Date 20250206========\n; SKIPPABLE_START\n; SKIPTYPE: timelapse\nM622.1 S1 ; for prev firmware, default turned on\nM1002 judge_flag timelapse_record_flag\nM622 J1\n{if timelapse_type == 0} ; timelapse without wipe tower\nM971 S11 C10 O0\nM1004 S5 P1  ; external shutter\n{elsif timelapse_type == 1} ; timelapse with wipe tower\nG92 E0\nG1 X65 Y245 F20000 ; move to safe pos\nG17\nG2 Z{layer_z} I0.86 J0.86 P1 F20000\nG1 Y265 F3000\nM400\nM1004 S5 P1  ; external shutter\nM400 P300\nM971 S11 C10 O0\nG92 E0\nG1 X100 F5000\nG1 Y255 F20000\n{endif}\nM623\n; SKIPPABLE_END\n
; timelapse_type = 0
; top_area_threshold = 200%
; top_color_penetration_layers = 5
; top_one_wall_type = all top
; top_shell_layers = 5
; top_shell_thickness = 1
; top_solid_infill_flow_ratio = 1
; top_surface_acceleration = 2000
; top_surface_jerk = 9
; top_surface_line_width = 0.42
; top_surface_pattern = monotonicline
; top_surface_speed = 200
; top_z_overrides_xy_distance = 0
; travel_acceleration = 10000
; travel_jerk = 9
; travel_speed = 500
; travel_speed_z = 0
; tree_support_branch_angle = 45
; tree_support_branch_diameter = 2
; tree_support_branch_diameter_angle = 5
; tree_support_branch_distance = 5
; tree_support_wall_count = -1
; upward_compatible_machine = "Bambu Lab P1S 0.4 nozzle";"Bambu Lab P1P 0.4 nozzle";"Bambu Lab X1 0.4 nozzle";"Bambu Lab X1E 0.4 nozzle";"Bambu Lab A1 0.4 nozzle";"Bambu Lab H2D 0.4 nozzle";"Bambu Lab H2D Pro 0.4 nozzle";"Bambu Lab H2S 0.4 nozzle";"Bambu Lab P2S 0.4 nozzle"
; use_firmware_retraction = 0
; use_relative_e_distances = 1
; vertical_shell_speed = 80%
; volumetric_speed_coefficients = "0 0 0 0 0 0"
; wall_distribution_count = 1
; wall_filament = 1
; wall_generator = classic
; wall_loops = 2
; wall_sequence = inner wall/outer wall
; wall_transition_angle = 10
; wall_transition_filter_deviation = 25%
; wall_transition_length = 100%
; wipe = 1
; wipe_distance = 2
; wipe_speed = 80%
; wipe_tower_no_sparse_layers = 0
; wipe_tower_rotation_angle = 0
; wipe_tower_x = 15
; wipe_tower_y = 220
; wrapping_detection_gcode = 
; wrapping_detection_layers = 20
; wrapping_exclude_area = 
; xy_contour_compensation = 0
; xy_hole_compensation = 0
; z_direction_outwall_speed_continuous = 0
; z_hop = 0.4
; z_hop_types = Auto Lift
; CONFIG_BLOCK_END

; EXECUTABLE_BLOCK_START
M73 P0 R33
M201 X20000 Y20000 Z500 E5000
M203 X500 Y500 Z20 E30
M204 P20000 R5000 T20000
M205 X9.00 Y9.00 Z3.00 E2.50
M106 S0
M106 P2 S0
; FEATURE: Custom
;===== machine: X1-0.4 ====================
;===== date: 20250909 ==================
;===== start printer sound ================
M17
M400 S1
M1006 S1
M1006 A0 B10 L100 C37 D10 M60 E37 F10 N60
M1006 A0 B10 L100 C41 D10 M60 E41 F10 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A46 B10 L100 C43 D10 M70 E39 F10 N100
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N100
M1006 A43 B10 L100 C0 D10 M60 E39 F10 N100
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N100
M1006 A41 B10 L100 C0 D10 M100 E41 F10 N100
M1006 A44 B10 L100 C0 D10 M100 E44 F10 N100
M1006 A49 B10 L100 C0 D10 M100 E49 F10 N100
M1006 A0 B10 L100 C0 D10 M100 E0 F10 N100
M1006 A48 B10 L100 C44 D10 M60 E39 F10 N100
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N100
M1006 A44 B10 L100 C0 D10 M90 E39 F10 N100
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N100
M1006 A46 B10 L100 C43 D10 M60 E39 F10 N100
M1006 W
;===== turn on the HB fan =================
M104 S75 ;set extruder temp to turn on the HB fan and prevent filament oozing from nozzle
;===== reset machine status =================
M290 X40 Y40 Z2.6666666
G91
M17 Z0.4 ; lower the z-motor current
G380 S2 Z30 F300 ; G380 is same as G38; lower the hotbed , to prevent the nozzle is below the hotbed
G380 S2 Z-25 F300 ;
G1 Z5 F300;
G90
M17 X1.2 Y1.2 Z0.75 ; reset motor current to default
M960 S5 P1 ; turn on logo lamp
G90
M220 S100 ;Reset Feedrate
M221 S100 ;Reset Flowrate
M73.2   R1.0 ;Reset left time magnitude
M1002 set_gcode_claim_speed_level : 5
M221 X0 Y0 Z0 ; turn off soft endstop to prevent protential logic problem
G29.1 Z0 ; clear z-trim value first
M204 S10000 ; init ACC set to 10m/s^2

;===== heatbed preheat ====================
M1002 gcode_claim_action : 2
M140 S55 ;set bed temp
M190 S55 ;wait for bed temp


;=========register first layer scan=====
M977 S1 P60


;=============turn on fans to prevent PLA jamming=================

    
    M106 P3 S180
    ;Prevent PLA from jamming
    M142 P1 R35 S40

M106 P2 S100 ; turn on big fan ,to cool down toolhead

;===== prepare print temperature and material ==========
M104 S220 ;set extruder temp
G91
G0 Z10 F1200
G90
G28 X
M975 S1 ; turn on
G1 X60 F12000
G1 Y245
G1 Y265 F3000
M620 M
M620 S0A   ; switch material if AMS exist
    M109 S220
    G1 X120 F12000

    G1 X20 Y50 F12000
    G1 Y-3
    T0
    G1 X54 F12000
    G1 Y265
    M400
M621 S0A
M620.1 E F523.843 T240

M412 S1 ; ===turn on filament runout detection===

M109 S250 ;set nozzle to common flush temp
M106 P1 S0
G92 E0
M73 P1 R32
G1 E50 F200
M400
M104 S220
G92 E0
M73 P14 R28
G1 E50 F200
M400
M106 P1 S255
G92 E0
G1 E5 F300
M109 S200 ; drop nozzle temp, make filament shink a bit
G92 E0
M73 P15 R28
G1 E-0.5 F300

M73 P16 R28
G1 X70 F9000
G1 X76 F15000
G1 X65 F15000
G1 X76 F15000
G1 X65 F15000; shake to put down garbage
G1 X80 F6000
G1 X95 F15000
G1 X80 F15000
G1 X165 F15000; wipe and shake
M400
M106 P1 S0
;===== prepare print temperature and material end =====


;===== wipe nozzle ===============================
M1002 gcode_claim_action : 14
M975 S1
M106 S255
G1 X65 Y230 F18000
G1 Y264 F6000
M109 S200
G1 X100 F18000 ; first wipe mouth

G0 X135 Y253 F20000  ; move to exposed steel surface edge
G28 Z P0 T300; home z with low precision,permit 300deg temperature
G29.2 S0 ; turn off ABL
G0 Z5 F20000

G1 X60 Y265
G92 E0
G1 E-0.5 F300 ; retrack more
G1 X100 F5000; second wipe mouth
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X90 F5000
G0 X128 Y261 Z-1.5 F20000  ; move to exposed steel surface and stop the nozzle
M104 S140 ; set temp down to heatbed acceptable
M106 S255 ; turn on fan (G28 has turn off fan)

M221 S; push soft endstop status
M221 Z0 ;turn off Z axis endstop
G0 Z0.5 F20000
G0 X125 Y259.5 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y262.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y260.0
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y262.0
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y260.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y261.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y261.0
G0 Z-1.01
G0 X131 F211
G0 X124
G0 X128
G2 I0.5 J0 F300
G2 I0.5 J0 F300
G2 I0.5 J0 F300
G2 I0.5 J0 F300

M109 S140 ; wait nozzle temp down to heatbed acceptable
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000

M221 R; pop softend status
G1 Z10 F1200
M400
M73 P16 R27
G1 Z10
G1 F30000
G1 X128 Y128
G29.2 S1 ; turn on ABL
;G28 ; home again after hard wipe mouth
M106 S0 ; turn off fan , too noisy
;===== wipe nozzle end ================================

;===== check scanner clarity ===========================
G1 X128 Y128 F24000
G28 Z P0
M972 S5 P0
G1 X230 Y15 F24000
;===== check scanner clarity end =======================

;===== bed leveling ==================================
M1002 judge_flag g29_before_print_flag
M622 J1

    M1002 gcode_claim_action : 1
    G29 A X20 Y6 I141.4 J87.4
    M400
    M500 ; save cali data

M623
;===== bed leveling end ================================

;===== home after wipe mouth============================
M1002 judge_flag g29_before_print_flag
M622 J0

    M1002 gcode_claim_action : 13
    G28

M623
;===== home after wipe mouth end =======================

M975 S1 ; turn on vibration supression

;=============turn on fans to prevent PLA jamming=================

    
    M106 P3 S180
    ;Prevent PLA from jamming
    M142 P1 R35 S40

M106 P2 S100 ; turn on big fan ,to cool down toolhead

M104 S220 ; set extrude temp earlier, to reduce wait time

;===== mech mode fast check============================
G1 X128 Y128 Z10 F20000
M400 P200
M970.3 Q1 A7 B30 C80  H15 K0
M974 Q1 S2 P0

G1 X128 Y128 Z10 F20000
M400 P200
M970.3 Q0 A7 B30 C90 Q0 H15 K0
M974 Q0 S2 P0

M975 S1
G1 F30000
G1 X230 Y15
G28 X ; re-home XY
;===== mech mode fast check============================


;start heatbed  scan====================================
M976 S2 P1
G90
G1 X128 Y128 F20000
M976 S3 P2  ;register void printing detection


;===== nozzle load line ===============================
M975 S1
G90
M83
T1000
M73 P17 R27
G1 X18.0 Y1.0 Z0.8 F18000;Move to start position
M109 S220
G1 Z0.2
G0 E2 F300
G0 X240 E15 F6033.27
G0 Y11 E0.700 F1508.32
G0 X239.5
G0 E0.2
G0 Y1.5 E0.700
G0 X231 E0.700 F6033.27
M400

;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==
;curr_bed_type=Textured PEI Plate

G29.1 Z-0.04 ; for Textured PEI Plate


;===== draw extrinsic para cali paint =================
M1002 judge_flag extrude_cali_flag
M622 J1

    M1002 gcode_claim_action : 8

    T1000

    G0 F1200.0 X231 Y12   Z0.2 E0.577
    G0 F1200.0 X226 Y12   Z0.2 E0.275
    G0 F1200.0 X226 Y1.5  Z0.2 E0.577
    G0 F1200.0 X220 Y1.5  Z0.2 E0.330
    G0 F1200.0 X220 Y8    Z0.2 E0.358
    G0 F1200.0 X210 Y8    Z0.2 E0.549
    G0 F1200.0 X210 Y1.5  Z0.2 E0.357

    G0 X48.0 E11.9 F6033.27
    G0 X48.0 Y12 E0.772 F1200.0
    G0 X45.0 E0.22 F1200.0
    G0 X35.0 Y6.0 E0.86 F1200.0

    ;=========== extruder cali extrusion ==================
    T1000
    M83
    
        
            M204 S5000
        
    
    G0 X35.000 Y6.000 Z0.300 F30000 E0
    G1 F1500.000 E0.800
    M106 S0 ; turn off fan
    G0 X185.000 E9.35441 F6033.27
    G0 X187 Z0
    G1 F1500.000 E-0.800
    G0 Z1
    G0 X180 Z0.3 F18000

    M900 L1000.0 M1.0
    M900 K0.040
    G0 X45.000 F30000
    G0 Y8.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F1508.32
    G1 X70.000 E0.31181 F1508.32
    G1 X75.000 E0.31181 F6033.27
    G1 X80.000 E0.31181 F1508.32
    G1 X85.000 E0.31181 F6033.27
    G1 X90.000 E0.31181 F1508.32
    G1 X95.000 E0.31181 F6033.27
    G1 X100.000 E0.31181 F1508.32
    G1 X105.000 E0.31181 F6033.27
    G1 X110.000 E0.31181 F1508.32
    G1 X115.000 E0.31181 F6033.27
    G1 X120.000 E0.31181 F1508.32
    G1 X125.000 E0.31181 F6033.27
    G1 X130.000 E0.31181 F1508.32
    G1 X135.000 E0.31181 F6033.27
    G1 X140.000 E0.31181 F1508.32
    G1 X145.000 E0.31181 F6033.27
M73 P18 R27
    G1 X150.000 E0.31181 F1508.32
    G1 X155.000 E0.31181 F6033.27
    G1 X160.000 E0.31181 F1508.32
    G1 X165.000 E0.31181 F6033.27
    G1 X170.000 E0.31181 F1508.32
    G1 X175.000 E0.31181 F6033.27
    G1 X180.000 E0.31181 F6033.27
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3
    M400

    G0 X45.000 F30000
    M900 K0.020
    G0 X45.000 F30000
    G0 Y10.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F1508.32
    G1 X70.000 E0.31181 F1508.32
    G1 X75.000 E0.31181 F6033.27
    G1 X80.000 E0.31181 F1508.32
    G1 X85.000 E0.31181 F6033.27
    G1 X90.000 E0.31181 F1508.32
    G1 X95.000 E0.31181 F6033.27
    G1 X100.000 E0.31181 F1508.32
    G1 X105.000 E0.31181 F6033.27
    G1 X110.000 E0.31181 F1508.32
    G1 X115.000 E0.31181 F6033.27
    G1 X120.000 E0.31181 F1508.32
    G1 X125.000 E0.31181 F6033.27
    G1 X130.000 E0.31181 F1508.32
    G1 X135.000 E0.31181 F6033.27
    G1 X140.000 E0.31181 F1508.32
    G1 X145.000 E0.31181 F6033.27
    G1 X150.000 E0.31181 F1508.32
    G1 X155.000 E0.31181 F6033.27
    G1 X160.000 E0.31181 F1508.32
    G1 X165.000 E0.31181 F6033.27
    G1 X170.000 E0.31181 F1508.32
    G1 X175.000 E0.31181 F6033.27
    G1 X180.000 E0.31181 F6033.27
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3
    M400

    G0 X45.000 F30000
    M900 K0.000
    G0 X45.000 F30000
    G0 Y12.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F1508.32
    G1 X70.000 E0.31181 F1508.32
    G1 X75.000 E0.31181 F6033.27
    G1 X80.000 E0.31181 F1508.32
    G1 X85.000 E0.31181 F6033.27
    G1 X90.000 E0.31181 F1508.32
    G1 X95.000 E0.31181 F6033.27
    G1 X100.000 E0.31181 F1508.32
    G1 X105.000 E0.31181 F6033.27
    G1 X110.000 E0.31181 F1508.32
M73 P19 R27
    G1 X115.000 E0.31181 F6033.27
    G1 X120.000 E0.31181 F1508.32
    G1 X125.000 E0.31181 F6033.27
    G1 X130.000 E0.31181 F1508.32
    G1 X135.000 E0.31181 F6033.27
    G1 X140.000 E0.31181 F1508.32
    G1 X145.000 E0.31181 F6033.27
    G1 X150.000 E0.31181 F1508.32
    G1 X155.000 E0.31181 F6033.27
    G1 X160.000 E0.31181 F1508.32
    G1 X165.000 E0.31181 F6033.27
    G1 X170.000 E0.31181 F1508.32
    G1 X175.000 E0.31181 F6033.27
    G1 X180.000 E0.31181 F6033.27
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3

    G0 X45.000 F30000 ; move to start point

M623 ; end of "draw extrinsic para cali paint"


M1002 judge_flag extrude_cali_flag
M622 J0
    G0 X231 Y1.5 F30000
    G0 X18 E14.3 F6033.27
M623

M104 S140


;=========== laser and rgb calibration ===========
M400
M18 E
M500 R

M973 S3 P14

G1 X120 Y1.0 Z0.3 F18000.0;Move to first extrude line pos
T1100
G1 X235.0 Y1.0 Z0.3 F18000.0;Move to first extrude line pos
M400 P100
M960 S1 P1
M400 P100
M973 S6 P0; use auto exposure for horizontal laser by xcam
M960 S0 P0

G1 X240.0 Y6.0 Z0.3 F18000.0;Move to vertical extrude line pos
M960 S2 P1
M400 P100
M973 S6 P1; use auto exposure for vertical laser by xcam
M960 S0 P0

;=========== handeye calibration ======================
M1002 judge_flag extrude_cali_flag
M622 J1

    M973 S3 P1 ; camera start stream
    M400 P500
    M973 S1
    G0 F6000 X228.500 Y4.750 Z0.000
    M960 S0 P1
    M973 S1
    M400 P800
    M971 S6 P0
    M973 S2 P0
    M400 P500
    G0 Z0.000 F12000
    M960 S0 P0
    M960 S1 P1
    G0 X215.00 Y4.750
    M400 P200
    M971 S5 P1
    M973 S2 P1
    M400 P500
    M960 S0 P0
    M960 S2 P1
    G0 X228.5 Y6.75
    M400 P200
    M971 S5 P3
    G0 Z0.500 F12000
    M960 S0 P0
    M960 S2 P1
    G0 X228.5 Y6.75
    M400 P200
    M971 S5 P4
    M973 S2 P0
    M400 P500
    M960 S0 P0
    M960 S1 P1
    G0 X215.00 Y4.750
    M400 P500
    M971 S5 P2
    M963 S1
    M400 P1500
    M964
    T1100
    G1 Z3 F3000

    M400
    M500 ; save cali data

    M104 S220 ; rise nozzle temp now ,to reduce temp waiting time.

    T1100
    M400 P400
    M960 S0 P0
    G0 F30000.000 Y10.000 X65.000 Z0.000
    M400 P400
    M960 S1 P1
    M400 P50

    M969 S1 N3 A2000
    G0 F360.000 X181.000 Z0.000
    M980.3 A70.000 B94.1106 C5.000 D376.442 E5.000 F175.000 H1.000 I0.000 J0.020 K0.040
    M400 P100
    G0 F20000
    G0 Z1 ; rise nozzle up
    T1000 ; change to nozzle space
    G0 X45.000 Y4.000 F30000 ; move to test line pos
    M969 S0 ; turn off scanning
    M960 S0 P0


    G1 Z2 F20000
    T1000
    G0 X45.000 Y4.000 F30000 E0
    M109 S220
    G0 Z0.3
    G1 F1500.000 E3.600
    G1 X65.000 E1.24726 F1508.32
    G1 X70.000 E0.31181 F1508.32
    G1 X75.000 E0.31181 F6033.27
    G1 X80.000 E0.31181 F1508.32
    G1 X85.000 E0.31181 F6033.27
    G1 X90.000 E0.31181 F1508.32
    G1 X95.000 E0.31181 F6033.27
    G1 X100.000 E0.31181 F1508.32
    G1 X105.000 E0.31181 F6033.27
    G1 X110.000 E0.31181 F1508.32
    G1 X115.000 E0.31181 F6033.27
    G1 X120.000 E0.31181 F1508.32
    G1 X125.000 E0.31181 F6033.27
    G1 X130.000 E0.31181 F1508.32
    G1 X135.000 E0.31181 F6033.27

    ; see if extrude cali success, if not ,use default value
    M1002 judge_last_extrude_cali_success
    M622 J0
        M400
        M900 K0.02 M0.125481
    M623

    G1 X140.000 E0.31181 F1508.32
    G1 X145.000 E0.31181 F6033.27
    G1 X150.000 E0.31181 F1508.32
    G1 X155.000 E0.31181 F6033.27
    G1 X160.000 E0.31181 F1508.32
    G1 X165.000 E0.31181 F6033.27
    G1 X170.000 E0.31181 F1508.32
    G1 X175.000 E0.31181 F6033.27
    G1 X180.000 E0.31181 F1508.32
    G1 X185.000 E0.31181 F6033.27
    G1 X190.000 E0.31181 F1508.32
    G1 X195.000 E0.31181 F6033.27
    G1 X200.000 E0.31181 F1508.32
    G1 X205.000 E0.31181 F6033.27
    G1 X210.000 E0.31181 F1508.32
    G1 X215.000 E0.31181 F6033.27
    G1 X220.000 E0.31181 F1508.32
    G1 X225.000 E0.31181 F6033.27
    M973 S4

M623

;========turn off light and wait extrude temperature =============
M1002 gcode_claim_action : 0
M973 S4 ; turn off scanner
M400 ; wait all motion done before implement the emprical L parameters
;M900 L500.0 ; Empirical parameters
M109 S220
M960 S1 P0 ; turn off laser
M960 S2 P0 ; turn off laser
M106 S0 ; turn off fan
M106 P2 S0 ; turn off big fan
M106 P3 S0 ; turn off chamber fan

M975 S1 ; turn on mech mode supression
G90
M83
T1000
;===== purge line to wipe the nozzle ============================
G1 E-0.8 F1800
G1 X18.0 Y2.5 Z0.8 F18000.0;Move to start position
G1 E0.8 F1800
M109 S220
G1 Z0.2
G0 X239 E15 F6033.27
G0 Y12 E0.7 F1508.32
; MACHINE_START_GCODE_END
; filament start gcode
M106 P3 S150

M142 P1 R35 S40
;VT0
G90
G21
M83 ; use relative distances for extrusion
M981 S1 P20000 ;open spaghetti detector
; CHANGE_LAYER
; Z_HEIGHT: 0.2
; LAYER_HEIGHT: 0.2
G1 E-.8 F1800
; layer num/total_layer_count: 1/40
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
M204 S6000
G1 Z.4 F30000
; object ids of layer 1 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer1 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.257 Y8.243
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X141.257 Y6.957 E.04789
G1 X142.543 Y6.957 E.04789
G1 X142.543 Y8.243 E.04789
G1 X141.317 Y8.243 E.04566
; WIPE_START
G1 X141.257 Y6.957 E-.48917
G1 X141.97 Y6.957 E-.27084
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X149.586 Y7.451 Z.6 F30000
G1 X160.257 Y8.143 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X160.257 Y7.657 E.0181
G1 X160.543 Y7.657 E.01065
G1 X160.543 Y8.143 E.0181
G1 X160.317 Y8.143 E.00841
; WIPE_START
G1 X160.257 Y7.657 E-.25019
G1 X160.543 Y7.657 E-.14609
G1 X160.543 Y8.143 E-.2483
G1 X160.317 Y8.143 E-.11543
; WIPE_END
G1 E-.04 F1800
M204 S6000
M73 P19 R26
G1 X152.688 Y8.361 Z.6 F30000
G1 X140.8 Y8.7 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X140.8 Y6.5 E.08194
G1 X143 Y6.5 E.08194
G1 X143 Y7.2 E.02607
G1 X161 Y7.2 E.67043
G1 X161 Y8.6 E.05215
G1 X159.8 Y8.6 E.0447
G1 X159.8 Y8 E.02235
G1 X143 Y8 E.62574
G1 X143 Y8.7 E.02607
G1 X140.86 Y8.7 E.07971
; WIPE_START
G1 X140.805 Y6.701 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X141.44 Y7.338 Z.6 F30000
G1 Z.2
M73 P20 R26
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5914
G1 F6300
M204 S500
G1 X142.162 Y8.06 E.04567
M204 S6000
G1 X142.772 Y7.6 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38588
G1 F3000
M204 S500
M73 P21 R26
G1 X160.028 Y7.6 E.48228
; OBJECT_ID: 12
; WIPE_START
G1 X158.028 Y7.6 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
M204 S6000
G1 X150.397 Y7.712 Z.6 F30000
G1 X114.257 Y8.243 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X114.257 Y6.957 E.04789
G1 X115.543 Y6.957 E.04789
G1 X115.543 Y8.243 E.04789
G1 X114.317 Y8.243 E.04566
; WIPE_START
G1 X114.257 Y6.957 E-.48917
G1 X114.97 Y6.957 E-.27084
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X122.598 Y7.201 Z.6 F30000
G1 X133.257 Y7.543 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X133.257 Y7.057 E.0181
G1 X133.543 Y7.057 E.01065
G1 X133.543 Y7.543 E.0181
G1 X133.317 Y7.543 E.00841
; WIPE_START
G1 X133.257 Y7.057 E-.25019
G1 X133.543 Y7.057 E-.14609
G1 X133.543 Y7.543 E-.2483
G1 X133.317 Y7.543 E-.11543
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X125.698 Y7.995 Z.6 F30000
G1 X113.8 Y8.7 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X113.8 Y6.5 E.08194
G1 X116 Y6.5 E.08194
G1 X116 Y7.2 E.02607
G1 X132.8 Y7.2 E.62574
G1 X132.8 Y6.6 E.02235
G1 X134 Y6.6 E.0447
G1 X134 Y8 E.05215
G1 X116 Y8 E.67043
G1 X116 Y8.7 E.02607
G1 X113.86 Y8.7 E.07971
; WIPE_START
G1 X113.805 Y6.701 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X114.44 Y7.338 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5914
G1 F6300
M204 S500
G1 X115.162 Y8.06 E.04567
M204 S6000
G1 X115.772 Y7.6 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38588
G1 F3000
M204 S500
G1 X133.028 Y7.6 E.48228
; OBJECT_ID: 8
; WIPE_START
G1 X131.028 Y7.6 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
M204 S6000
G1 X127.262 Y14.239 Z.6 F30000
G1 X93.757 Y73.3 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X93.757 Y73.757 E.01702
G1 X83.643 Y73.757 E.37671
G1 X83.643 Y67.643 E.22773
G1 X93.757 Y67.643 E.37671
G1 X93.757 Y73.24 E.20847
M204 S6000
G1 X93.3 Y73.3 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X84.1 Y73.3 E.34266
G1 X84.1 Y68.1 E.19368
G1 X93.3 Y68.1 E.34266
G1 X93.3 Y73.24 E.19145
; WIPE_START
G1 X91.3 Y73.253 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X92.974 Y65.806 Z.6 F30000
G1 X97.3 Y46.557 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X92.043 Y46.557 E.19581
G1 X92.043 Y39.843 E.25008
G1 X92.293 Y39.843 E.00931
G1 X92.293 Y29.057 E.40173
G1 X90.243 Y29.057 E.07635
G1 X90.243 Y22.143 E.25753
G1 X92.293 Y22.143 E.07635
G1 X92.293 Y21.843 E.01117
G1 X97.507 Y21.843 E.19421
G1 X97.507 Y22.143 E.01117
G1 X99.557 Y22.143 E.07635
G1 X99.557 Y29.057 E.25753
G1 X97.507 Y29.057 E.07635
G1 X97.507 Y39.843 E.40173
G1 X97.757 Y39.843 E.00931
G1 X97.757 Y46.557 E.25008
G1 X97.36 Y46.557 E.01479
M204 S6000
G1 X97.3 Y46.1 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X92.5 Y46.1 E.17878
G1 X92.5 Y40.3 E.21603
G1 X92.75 Y40.3 E.00931
G1 X92.75 Y28.6 E.43578
G1 X90.7 Y28.6 E.07635
G1 X90.7 Y22.6 E.22348
G1 X92.75 Y22.6 E.07635
G1 X92.75 Y22.3 E.01117
G1 X97.05 Y22.3 E.16016
G1 X97.05 Y22.6 E.01117
G1 X99.1 Y22.6 E.07635
G1 X99.1 Y28.6 E.22348
G1 X97.05 Y28.6 E.07635
G1 X97.05 Y40.3 E.43578
G1 X97.3 Y40.3 E.00931
G1 X97.3 Y46.04 E.21379
; WIPE_START
G1 X95.3 Y46.065 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X87.668 Y46.069 Z.6 F30000
G1 X35.357 Y46.1 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X35.357 Y46.557 E.01702
G1 X29.643 Y46.557 E.21283
G1 X29.643 Y39.843 E.25008
G1 X29.893 Y39.843 E.00931
G1 X29.893 Y29.057 E.40173
G1 X27.843 Y29.057 E.07635
G1 X27.843 Y22.143 E.25753
G1 X29.893 Y22.143 E.07635
G1 X29.893 Y21.843 E.01117
G1 X35.107 Y21.843 E.19421
G1 X35.107 Y22.143 E.01117
G1 X37.157 Y22.143 E.07635
G1 X37.157 Y29.057 E.25753
G1 X35.107 Y29.057 E.07635
G1 X35.107 Y39.843 E.40173
G1 X35.357 Y39.843 E.00931
G1 X35.357 Y46.04 E.23082
M204 S6000
G1 X34.9 Y46.1 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X30.1 Y46.1 E.17878
G1 X30.1 Y40.3 E.21603
G1 X30.35 Y40.3 E.00931
G1 X30.35 Y28.6 E.43578
G1 X28.3 Y28.6 E.07635
G1 X28.3 Y22.6 E.22348
G1 X30.35 Y22.6 E.07635
G1 X30.35 Y22.3 E.01117
G1 X34.65 Y22.3 E.16016
G1 X34.65 Y22.6 E.01117
G1 X36.7 Y22.6 E.07635
G1 X36.7 Y28.6 E.22348
G1 X34.65 Y28.6 E.07635
G1 X34.65 Y40.3 E.43578
G1 X34.9 Y40.3 E.00931
G1 X34.9 Y46.04 E.21379
; WIPE_START
G1 X32.9 Y46.065 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X33.161 Y53.693 Z.6 F30000
G1 X33.848 Y73.751 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
M73 P22 R26
G1 F3000
M204 S500
G1 X33.7 Y73.754 E.00551
G3 X33.409 Y67.656 I.004 J-3.056 E.34641
G1 X33.7 Y67.642 E.01086
G3 X33.999 Y73.74 I.004 J3.056 E.34678
G1 X33.908 Y73.747 E.00341
M204 S6000
G1 X33.825 Y73.294 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X33.7 Y73.297 E.00467
G3 X33.453 Y68.112 I.004 J-2.599 E.29458
G1 X33.7 Y68.1 E.00921
G3 X33.955 Y73.285 I.004 J2.599 E.29489
G1 X33.885 Y73.29 E.00258
; WIPE_START
G1 X33.7 Y73.297 E-.07047
G1 X33.445 Y73.288 E-.09691
G1 X33.193 Y73.25 E-.09702
G1 X32.945 Y73.189 E-.09695
G1 X32.705 Y73.102 E-.097
G1 X32.474 Y72.993 E-.09694
G1 X32.255 Y72.862 E-.09697
G1 X32.05 Y72.71 E-.09698
G1 X32.029 Y72.691 E-.01075
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X39.452 Y74.469 Z.6 F30000
G1 X106.543 Y90.543 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X20.857 Y90.543 E3.19147
G1 X20.857 Y4.857 E3.19147
G1 X106.543 Y4.857 E3.19147
G1 X106.543 Y90.483 E3.18924
M204 S6000
G1 X107 Y91 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X20.4 Y91 E3.22552
G1 X20.4 Y4.4 E3.22552
G1 X107 Y4.4 E3.22552
G1 X107 Y90.94 E3.22329
; WIPE_START
G1 X105 Y90.941 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X105.122 Y83.31 Z.6 F30000
G1 X106.36 Y5.964 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50021
G1 F6300
M204 S500
G1 X105.641 Y5.246 E.03788
G1 X104.995 Y5.246 E.0241
G1 X106.154 Y6.405 E.06112
G1 X106.154 Y7.052 E.0241
G1 X104.348 Y5.246 E.0952
G1 X103.701 Y5.246 E.0241
G1 X106.154 Y7.699 E.12928
G1 X106.154 Y8.345 E.0241
G1 X103.055 Y5.246 E.16336
G1 X102.408 Y5.246 E.0241
G1 X106.154 Y8.992 E.19744
G1 X106.154 Y9.639 E.0241
G1 X101.761 Y5.246 E.23152
G1 X101.114 Y5.246 E.0241
G1 X106.154 Y10.286 E.2656
G1 X106.154 Y10.932 E.0241
G1 X100.468 Y5.246 E.29968
G1 X99.821 Y5.246 E.0241
G1 X106.154 Y11.579 E.33376
G1 X106.154 Y12.226 E.0241
G1 X99.174 Y5.246 E.36784
G1 X98.528 Y5.246 E.0241
G1 X106.154 Y12.872 E.40192
G1 X106.154 Y13.519 E.0241
G1 X97.881 Y5.246 E.436
G1 X97.234 Y5.246 E.0241
G1 X106.154 Y14.166 E.47008
G1 X106.154 Y14.813 E.0241
G1 X96.587 Y5.246 E.50416
G1 X95.941 Y5.246 E.0241
G1 X106.154 Y15.459 E.53824
G1 X106.154 Y16.106 E.0241
G1 X95.294 Y5.246 E.57232
G1 X94.647 Y5.246 E.0241
G1 X106.154 Y16.753 E.6064
G1 X106.154 Y17.399 E.0241
G1 X94.001 Y5.246 E.64048
G1 X93.354 Y5.246 E.0241
G1 X106.154 Y18.046 E.67456
G1 X106.154 Y18.693 E.0241
G1 X92.707 Y5.246 E.70864
G1 X92.061 Y5.246 E.0241
G1 X106.154 Y19.339 E.74272
G1 X106.154 Y19.986 E.0241
G1 X91.414 Y5.246 E.7768
G1 X90.767 Y5.246 E.0241
G1 X106.154 Y20.633 E.81088
G1 X106.154 Y21.28 E.0241
G1 X90.12 Y5.246 E.84496
G1 X89.474 Y5.246 E.0241
G1 X106.154 Y21.926 E.87904
G1 X106.154 Y22.573 E.0241
G1 X88.827 Y5.246 E.91312
G1 X88.18 Y5.246 E.0241
G1 X106.154 Y23.22 E.9472
G1 X106.154 Y23.866 E.0241
G1 X87.534 Y5.246 E.98129
G1 X86.887 Y5.246 E.0241
G1 X106.154 Y24.513 E1.01537
G1 X106.154 Y25.16 E.0241
G1 X86.24 Y5.246 E1.04945
G1 X85.594 Y5.246 E.0241
M73 P22 R25
G1 X106.154 Y25.807 E1.08353
G1 X106.154 Y26.453 E.0241
G1 X84.947 Y5.246 E1.11761
G1 X84.3 Y5.246 E.0241
G1 X106.154 Y27.1 E1.15169
G1 X106.154 Y27.747 E.0241
G1 X83.653 Y5.246 E1.18577
G1 X83.007 Y5.246 E.0241
G1 X99.516 Y21.754 E.86999
G1 X99.946 Y21.754 E.01603
G1 X99.946 Y22.184 E.01603
G1 X106.154 Y28.393 E.3272
G1 X106.154 Y29.04 E.0241
G1 X99.946 Y22.831 E.3272
G1 X99.946 Y23.478 E.0241
G1 X106.154 Y29.687 E.3272
G1 X106.154 Y30.333 E.0241
G1 X99.946 Y24.125 E.3272
G1 X99.946 Y24.771 E.0241
G1 X106.154 Y30.98 E.3272
G1 X106.154 Y31.627 E.0241
G1 X99.946 Y25.418 E.3272
G1 X99.946 Y26.065 E.0241
G1 X106.154 Y32.274 E.3272
G1 X106.154 Y32.92 E.0241
M73 P23 R25
G1 X99.946 Y26.711 E.3272
G1 X99.946 Y27.358 E.0241
G1 X106.154 Y33.567 E.3272
G1 X106.154 Y34.214 E.0241
G1 X99.946 Y28.005 E.3272
G1 X99.946 Y28.652 E.0241
G1 X106.154 Y34.86 E.3272
G1 X106.154 Y35.507 E.0241
G1 X99.946 Y29.298 E.3272
G1 X99.946 Y29.446 E.00549
G1 X99.446 Y29.446 E.01861
G1 X106.154 Y36.154 E.35351
G1 X106.154 Y36.801 E.0241
G1 X98.799 Y29.446 E.38759
G1 X98.153 Y29.446 E.0241
G1 X106.154 Y37.447 E.42167
G1 X106.154 Y38.094 E.0241
G1 X97.896 Y29.835 E.43523
G1 X97.896 Y30.482 E.0241
G1 X106.154 Y38.741 E.43523
G1 X106.154 Y39.387 E.0241
G1 X97.896 Y31.128 E.43523
G1 X97.896 Y31.775 E.0241
G1 X106.154 Y40.034 E.43523
G1 X106.154 Y40.681 E.0241
G1 X97.896 Y32.422 E.43523
G1 X97.896 Y33.069 E.0241
G1 X106.154 Y41.327 E.43523
G1 X106.154 Y41.974 E.0241
G1 X97.896 Y33.715 E.43523
G1 X97.896 Y34.362 E.0241
G1 X106.154 Y42.621 E.43523
G1 X106.154 Y43.268 E.0241
G1 X97.896 Y35.009 E.43523
G1 X97.896 Y35.655 E.0241
G1 X106.154 Y43.914 E.43523
G1 X106.154 Y44.561 E.0241
G1 X97.896 Y36.302 E.43523
G1 X97.896 Y36.949 E.0241
G1 X106.154 Y45.208 E.43523
G1 X106.154 Y45.854 E.0241
G1 X97.896 Y37.596 E.43523
G1 X97.896 Y38.242 E.0241
G1 X106.154 Y46.501 E.43523
G1 X106.154 Y47.148 E.0241
G1 X97.896 Y38.889 E.43523
G1 X97.896 Y39.454 E.02107
G1 X98.146 Y39.454 E.00932
G1 X98.146 Y39.786 E.01234
G1 X106.154 Y47.795 E.42205
G1 X106.154 Y48.441 E.0241
G1 X98.146 Y40.432 E.42205
G1 X98.146 Y41.079 E.0241
G1 X106.154 Y49.088 E.42205
G1 X106.154 Y49.735 E.0241
G1 X98.146 Y41.726 E.42205
G1 X98.146 Y42.372 E.0241
G1 X106.154 Y50.381 E.42205
G1 X106.154 Y51.028 E.0241
G1 X98.146 Y43.019 E.42205
G1 X98.146 Y43.666 E.0241
G1 X106.154 Y51.675 E.42205
G1 X106.154 Y52.321 E.0241
G1 X98.146 Y44.313 E.42205
G1 X98.146 Y44.959 E.0241
G1 X106.154 Y52.968 E.42205
G1 X106.154 Y53.615 E.0241
G1 X98.146 Y45.606 E.42205
G1 X98.146 Y46.253 E.0241
G1 X106.154 Y54.262 E.42205
G1 X106.154 Y54.908 E.0241
G1 X98.146 Y46.899 E.42205
G1 X98.146 Y46.946 E.00172
G1 X97.545 Y46.946 E.02238
G1 X106.154 Y55.555 E.4537
G1 X106.154 Y56.202 E.0241
G1 X96.898 Y46.946 E.48778
G1 X96.252 Y46.946 E.0241
G1 X106.154 Y56.848 E.52186
G1 X106.154 Y57.495 E.0241
G1 X95.605 Y46.946 E.55594
G1 X94.958 Y46.946 E.0241
G1 X106.154 Y58.142 E.59002
G1 X106.154 Y58.789 E.0241
G1 X94.311 Y46.946 E.6241
G1 X93.665 Y46.946 E.0241
G1 X106.154 Y59.435 E.65818
G1 X106.154 Y60.082 E.0241
M73 P24 R25
G1 X93.018 Y46.946 E.69226
G1 X92.371 Y46.946 E.0241
G1 X106.36 Y60.934 E.73718
; WIPE_START
G1 X104.946 Y59.52 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X103.767 Y51.979 Z.6 F30000
G1 X99.074 Y21.96 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X82.36 Y5.246 E.88083
G1 X81.713 Y5.246 E.0241
G1 X98.222 Y21.754 E.86999
G1 X97.896 Y21.754 E.01217
G1 X97.896 Y21.454 E.01118
G1 X97.275 Y21.454 E.02311
G1 X81.067 Y5.246 E.85418
G1 X80.42 Y5.246 E.0241
G1 X96.629 Y21.454 E.85418
G1 X95.982 Y21.454 E.0241
G1 X79.773 Y5.246 E.85418
G1 X79.126 Y5.246 E.0241
G1 X95.335 Y21.454 E.85418
G1 X94.689 Y21.454 E.0241
G1 X78.48 Y5.246 E.85418
G1 X77.833 Y5.246 E.0241
G1 X94.042 Y21.454 E.85418
G1 X93.395 Y21.454 E.0241
G1 X77.186 Y5.246 E.85418
G1 X76.54 Y5.246 E.0241
G1 X92.748 Y21.454 E.85418
G1 X92.102 Y21.454 E.0241
G1 X75.893 Y5.246 E.85418
G1 X75.246 Y5.246 E.0241
G1 X91.755 Y21.754 E.86999
G1 X91.108 Y21.754 E.0241
G1 X74.6 Y5.246 E.86999
G1 X73.953 Y5.246 E.0241
G1 X90.462 Y21.754 E.86999
G1 X89.854 Y21.754 E.02263
G1 X89.854 Y21.794 E.00147
G1 X73.306 Y5.246 E.87207
G1 X72.659 Y5.246 E.0241
G1 X89.854 Y22.441 E.90615
G1 X89.854 Y23.087 E.0241
G1 X72.013 Y5.246 E.94023
G1 X71.366 Y5.246 E.0241
G1 X89.854 Y23.734 E.97431
G1 X89.854 Y24.381 E.0241
G1 X70.719 Y5.246 E1.00839
G1 X70.073 Y5.246 E.0241
G1 X89.854 Y25.027 E1.04247
G1 X89.854 Y25.674 E.0241
G1 X69.426 Y5.246 E1.07655
G1 X68.779 Y5.246 E.0241
G1 X89.854 Y26.321 E1.11063
G1 X89.854 Y26.968 E.0241
G1 X68.132 Y5.246 E1.14471
G1 X67.486 Y5.246 E.0241
G1 X89.854 Y27.614 E1.17879
G1 X89.854 Y28.261 E.0241
G1 X66.633 Y5.04 E1.22371
; WIPE_START
G1 X68.048 Y6.454 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X73.52 Y11.775 Z.6 F30000
G1 X91.48 Y29.24 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X91.904 Y29.664 E.02236
G1 X91.904 Y30.311 E.0241
G1 X90.833 Y29.24 E.05644
; WIPE_START
G1 X91.904 Y30.311 E-.57561
G1 X91.904 Y29.826 E-.18439
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X92.11 Y31.163 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X90.392 Y29.446 E.09053
G1 X89.854 Y29.446 E.02004
G1 X89.854 Y28.908 E.02004
G1 X66.192 Y5.246 E1.24695
G1 X65.546 Y5.246 E.0241
G1 X91.904 Y31.604 E1.38906
G1 X91.904 Y32.251 E.0241
G1 X64.899 Y5.246 E1.42315
G1 X64.252 Y5.246 E.0241
G1 X91.904 Y32.898 E1.45723
G1 X91.904 Y33.545 E.0241
G1 X63.606 Y5.246 E1.49131
G1 X62.959 Y5.246 E.0241
G1 X91.904 Y34.191 E1.52539
G1 X91.904 Y34.838 E.0241
G1 X62.312 Y5.246 E1.55947
G1 X61.665 Y5.246 E.0241
G1 X91.904 Y35.485 E1.59355
G1 X91.904 Y36.131 E.0241
G1 X61.019 Y5.246 E1.62763
G1 X60.372 Y5.246 E.0241
G1 X91.904 Y36.778 E1.66171
G1 X91.904 Y37.425 E.0241
G1 X59.725 Y5.246 E1.69579
G1 X59.079 Y5.246 E.0241
G1 X91.904 Y38.071 E1.72987
G1 X91.904 Y38.718 E.0241
G1 X58.432 Y5.246 E1.76395
G1 X57.785 Y5.246 E.0241
G1 X91.904 Y39.365 E1.79803
G1 X91.904 Y39.454 E.00334
G1 X91.654 Y39.454 E.00932
G1 X91.654 Y39.762 E.01145
G1 X57.138 Y5.246 E1.81893
G1 X56.492 Y5.246 E.0241
G1 X91.654 Y40.408 E1.85301
G1 X91.654 Y41.055 E.0241
G1 X55.845 Y5.246 E1.8871
G1 X55.198 Y5.246 E.0241
G1 X91.654 Y41.702 E1.92118
G1 X91.654 Y42.348 E.0241
G1 X54.552 Y5.246 E1.95526
G1 X53.905 Y5.246 E.0241
G1 X91.654 Y42.995 E1.98934
G1 X91.654 Y43.642 E.0241
G1 X53.258 Y5.246 E2.02342
G1 X52.612 Y5.246 E.0241
G1 X91.654 Y44.289 E2.0575
G1 X91.654 Y44.935 E.0241
G1 X51.965 Y5.246 E2.09158
G1 X51.318 Y5.246 E.0241
G1 X91.654 Y45.582 E2.12566
G1 X91.654 Y46.229 E.0241
M73 P25 R25
G1 X50.671 Y5.246 E2.15974
G1 X50.025 Y5.246 E.0241
G1 X106.154 Y61.375 E2.95794
G1 X106.154 Y62.022 E.0241
G1 X49.378 Y5.246 E2.99202
G1 X48.731 Y5.246 E.0241
G1 X106.154 Y62.669 E3.0261
G1 X106.154 Y63.315 E.0241
G1 X48.085 Y5.246 E3.06018
G1 X47.438 Y5.246 E.0241
G1 X106.154 Y63.962 E3.09426
G1 X106.154 Y64.609 E.0241
G1 X46.791 Y5.246 E3.12834
G1 X46.144 Y5.246 E.0241
G1 X106.154 Y65.256 E3.16242
G1 X106.154 Y65.902 E.0241
G1 X45.498 Y5.246 E3.19651
G1 X44.851 Y5.246 E.0241
G1 X106.154 Y66.549 E3.23059
G1 X106.154 Y67.196 E.0241
G1 X44.204 Y5.246 E3.26467
G1 X43.558 Y5.246 E.0241
G1 X106.154 Y67.842 E3.29875
G1 X106.154 Y68.489 E.0241
G1 X42.911 Y5.246 E3.33283
G1 X42.264 Y5.246 E.0241
G1 X106.154 Y69.136 E3.36691
G1 X106.154 Y69.782 E.0241
G1 X41.618 Y5.246 E3.40099
G1 X40.971 Y5.246 E.0241
G1 X106.154 Y70.429 E3.43507
G1 X106.154 Y71.076 E.0241
G1 X40.324 Y5.246 E3.46915
G1 X39.677 Y5.246 E.0241
G1 X106.154 Y71.723 E3.50323
G1 X106.154 Y72.369 E.0241
G1 X39.031 Y5.246 E3.53731
G1 X38.384 Y5.246 E.0241
G1 X106.154 Y73.016 E3.57139
G1 X106.154 Y73.663 E.0241
G1 X37.737 Y5.246 E3.60547
G1 X37.091 Y5.246 E.0241
G1 X106.154 Y74.309 E3.63955
G1 X106.154 Y74.956 E.0241
G1 X36.444 Y5.246 E3.67363
G1 X35.797 Y5.246 E.0241
G1 X106.154 Y75.603 E3.70771
G1 X106.154 Y76.25 E.0241
G1 X35.15 Y5.246 E3.74179
G1 X34.504 Y5.246 E.0241
G1 X106.154 Y76.896 E3.77587
G1 X106.154 Y77.543 E.0241
G1 X33.857 Y5.246 E3.80995
G1 X33.21 Y5.246 E.0241
G1 X106.154 Y78.19 E3.84403
G1 X106.154 Y78.836 E.0241
G1 X32.564 Y5.246 E3.87811
G1 X31.917 Y5.246 E.0241
G1 X106.154 Y79.483 E3.91219
G1 X106.154 Y80.13 E.0241
G1 X94.146 Y68.121 E.63285
G1 X94.146 Y68.768 E.0241
M73 P25 R24
G1 X106.154 Y80.776 E.63285
G1 X106.154 Y81.423 E.0241
G1 X94.146 Y69.414 E.63285
G1 X94.146 Y70.061 E.0241
G1 X106.154 Y82.07 E.63285
G1 X106.154 Y82.717 E.0241
G1 X94.146 Y70.708 E.63285
G1 X94.146 Y71.354 E.0241
G1 X106.154 Y83.363 E.63285
G1 X106.154 Y84.01 E.0241
G1 X94.146 Y72.001 E.63285
G1 X94.146 Y72.648 E.0241
G1 X106.154 Y84.657 E.63285
G1 X106.154 Y85.303 E.0241
G1 X94.146 Y73.295 E.63285
G1 X94.146 Y73.941 E.0241
G1 X106.154 Y85.95 E.63285
G1 X106.154 Y86.597 E.0241
G1 X93.703 Y74.146 E.65616
G1 X93.056 Y74.146 E.0241
G1 X106.154 Y87.244 E.69024
G1 X106.154 Y87.89 E.0241
G1 X92.41 Y74.146 E.72432
G1 X91.763 Y74.146 E.0241
G1 X106.154 Y88.537 E.7584
G1 X106.154 Y89.184 E.0241
G1 X91.116 Y74.146 E.79248
G1 X90.47 Y74.146 E.0241
M73 P26 R24
G1 X106.154 Y89.83 E.82656
G1 X106.154 Y90.154 E.01208
G1 X105.832 Y90.154 E.01202
G1 X89.823 Y74.146 E.84364
G1 X89.176 Y74.146 E.0241
G1 X105.185 Y90.154 E.84364
G1 X104.538 Y90.154 E.0241
G1 X88.53 Y74.146 E.84364
G1 X87.883 Y74.146 E.0241
G1 X103.892 Y90.154 E.84364
G1 X103.245 Y90.154 E.0241
G1 X87.236 Y74.146 E.84364
G1 X86.589 Y74.146 E.0241
G1 X102.598 Y90.154 E.84364
G1 X101.952 Y90.154 E.0241
G1 X85.943 Y74.146 E.84364
G1 X85.296 Y74.146 E.0241
G1 X101.305 Y90.154 E.84364
G1 X100.658 Y90.154 E.0241
G1 X84.649 Y74.146 E.84364
G1 X84.003 Y74.146 E.0241
G1 X100.217 Y90.36 E.85448
; WIPE_START
G1 X98.803 Y88.946 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X96.969 Y81.537 Z.6 F30000
G1 X93.485 Y67.46 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X31.27 Y5.246 E3.2786
G1 X30.624 Y5.246 E.0241
G1 X92.632 Y67.254 E3.26776
G1 X91.986 Y67.254 E.0241
G1 X29.977 Y5.246 E3.26776
G1 X29.33 Y5.246 E.0241
G1 X91.339 Y67.254 E3.26776
G1 X90.692 Y67.254 E.0241
G1 X28.683 Y5.246 E3.26776
G1 X28.037 Y5.246 E.0241
G1 X90.046 Y67.254 E3.26776
G1 X89.399 Y67.254 E.0241
G1 X27.39 Y5.246 E3.26776
M73 P27 R24
G1 X26.743 Y5.246 E.0241
G1 X88.752 Y67.254 E3.26776
G1 X88.105 Y67.254 E.0241
G1 X26.097 Y5.246 E3.26776
G1 X25.45 Y5.246 E.0241
G1 X87.459 Y67.254 E3.26776
G1 X86.812 Y67.254 E.0241
G1 X24.803 Y5.246 E3.26776
G1 X24.156 Y5.246 E.0241
G1 X86.165 Y67.254 E3.26776
G1 X85.519 Y67.254 E.0241
G1 X23.51 Y5.246 E3.26776
G1 X22.863 Y5.246 E.0241
G1 X84.872 Y67.254 E3.26776
G1 X84.225 Y67.254 E.0241
G1 X22.216 Y5.246 E3.26776
G1 X21.57 Y5.246 E.0241
G1 X83.578 Y67.254 E3.26776
G1 X83.254 Y67.254 E.01208
G1 X83.254 Y67.577 E.01202
G1 X21.246 Y5.568 E3.26776
G1 X21.246 Y6.215 E.0241
G1 X36.785 Y21.754 E.8189
G1 X36.138 Y21.754 E.0241
G1 X21.246 Y6.862 E.78482
G1 X21.246 Y7.508 E.0241
G1 X35.192 Y21.454 E.73494
G1 X34.545 Y21.454 E.0241
G1 X21.246 Y8.155 E.70086
G1 X21.246 Y8.802 E.0241
G1 X33.898 Y21.454 E.66677
G1 X33.252 Y21.454 E.0241
G1 X21.246 Y9.448 E.63269
G1 X21.246 Y10.095 E.0241
G1 X32.605 Y21.454 E.59861
G1 X31.958 Y21.454 E.0241
G1 X21.246 Y10.742 E.56453
G1 X21.246 Y11.389 E.0241
G1 X31.311 Y21.454 E.53045
G1 X30.665 Y21.454 E.0241
G1 X21.246 Y12.035 E.49637
G1 X21.246 Y12.682 E.0241
G1 X30.018 Y21.454 E.46229
G1 X29.504 Y21.454 E.01914
G1 X29.504 Y21.588 E.00496
G1 X21.246 Y13.329 E.43523
G1 X21.246 Y13.975 E.0241
G1 X29.025 Y21.754 E.40994
G1 X28.378 Y21.754 E.0241
G1 X21.246 Y14.622 E.37586
G1 X21.246 Y15.269 E.0241
G1 X27.731 Y21.754 E.34178
G1 X27.454 Y21.754 E.01031
G1 X27.454 Y22.124 E.01379
M73 P28 R24
G1 X21.246 Y15.916 E.3272
G1 X21.246 Y16.562 E.0241
G1 X27.454 Y22.771 E.3272
G1 X27.454 Y23.418 E.0241
G1 X21.246 Y17.209 E.3272
G1 X21.246 Y17.856 E.0241
G1 X27.454 Y24.064 E.3272
G1 X27.454 Y24.711 E.0241
G1 X21.246 Y18.502 E.3272
G1 X21.246 Y19.149 E.0241
G1 X27.454 Y25.358 E.3272
G1 X27.454 Y26.005 E.0241
G1 X21.246 Y19.796 E.3272
G1 X21.246 Y20.442 E.0241
G1 X27.454 Y26.651 E.3272
G1 X27.454 Y27.298 E.0241
G1 X21.246 Y21.089 E.3272
G1 X21.246 Y21.736 E.0241
G1 X27.454 Y27.945 E.3272
G1 X27.454 Y28.591 E.0241
G1 X21.04 Y22.177 E.33804
; WIPE_START
G1 X22.454 Y23.591 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X28.097 Y28.731 Z.6 F30000
G1 X29.71 Y30.2 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X28.955 Y29.446 E.03978
G1 X28.309 Y29.446 E.0241
G1 X29.504 Y30.641 E.06302
G1 X29.504 Y31.288 E.0241
G1 X21.246 Y23.029 E.43523
G1 X21.246 Y23.676 E.0241
G1 X29.504 Y31.935 E.43523
G1 X29.504 Y32.582 E.0241
G1 X21.246 Y24.323 E.43523
G1 X21.246 Y24.969 E.0241
G1 X29.504 Y33.228 E.43523
G1 X29.504 Y33.875 E.0241
G1 X21.246 Y25.616 E.43523
M73 P28 R23
G1 X21.246 Y26.263 E.0241
G1 X29.504 Y34.522 E.43523
G1 X29.504 Y35.168 E.0241
G1 X21.246 Y26.91 E.43523
G1 X21.246 Y27.556 E.0241
G1 X29.504 Y35.815 E.43523
G1 X29.504 Y36.462 E.0241
G1 X21.246 Y28.203 E.43523
G1 X21.246 Y28.85 E.0241
G1 X29.504 Y37.108 E.43523
G1 X29.504 Y37.755 E.0241
G1 X21.246 Y29.496 E.43523
G1 X21.246 Y30.143 E.0241
G1 X29.504 Y38.402 E.43523
G1 X29.504 Y39.049 E.0241
G1 X21.246 Y30.79 E.43523
G1 X21.246 Y31.436 E.0241
G1 X29.264 Y39.454 E.42253
M73 P29 R23
G1 X29.254 Y40.092 E.02376
G1 X21.246 Y32.083 E.42205
G1 X21.246 Y32.73 E.0241
G1 X29.254 Y40.739 E.42205
G1 X29.254 Y41.385 E.0241
G1 X21.246 Y33.377 E.42205
G1 X21.246 Y34.023 E.0241
G1 X29.254 Y42.032 E.42205
G1 X29.254 Y42.679 E.0241
G1 X21.246 Y34.67 E.42205
G1 X21.246 Y35.317 E.0241
G1 X29.254 Y43.326 E.42205
G1 X29.254 Y43.972 E.0241
G1 X21.246 Y35.963 E.42205
G1 X21.246 Y36.61 E.0241
G1 X29.254 Y44.619 E.42205
G1 X29.254 Y45.266 E.0241
G1 X21.246 Y37.257 E.42205
G1 X21.246 Y37.904 E.0241
G1 X29.46 Y46.118 E.43289
; WIPE_START
G1 X28.046 Y44.704 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X30.972 Y37.654 Z.6 F30000
G1 X37.34 Y22.309 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X83.254 Y68.224 E2.41962
G1 X83.254 Y68.87 E.0241
G1 X37.546 Y23.162 E2.40878
G1 X37.546 Y23.808 E.0241
G1 X83.254 Y69.517 E2.40878
G1 X83.254 Y70.164 E.0241
G1 X37.546 Y24.455 E2.40878
G1 X37.546 Y25.102 E.0241
G1 X83.254 Y70.811 E2.40878
G1 X83.254 Y71.457 E.0241
G1 X37.546 Y25.748 E2.40878
G1 X37.546 Y26.395 E.0241
G1 X83.254 Y72.104 E2.40878
G1 X83.254 Y72.751 E.0241
G1 X37.546 Y27.042 E2.40878
G1 X37.546 Y27.689 E.0241
G1 X83.46 Y73.603 E2.41962
; WIPE_START
G1 X82.046 Y72.189 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X87.344 Y77.683 Z.6 F30000
G1 X99.57 Y90.36 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X37.546 Y28.335 E3.26861
G1 X37.546 Y28.982 E.0241
G1 X98.718 Y90.154 E3.22369
G1 X98.071 Y90.154 E.0241
G1 X37.362 Y29.446 E3.19926
G1 X36.716 Y29.446 E.0241
G1 X97.425 Y90.154 E3.19926
G1 X96.778 Y90.154 E.0241
G1 X36.069 Y29.446 E3.19926
G1 X35.496 Y29.446 E.02137
G1 X35.496 Y29.519 E.00273
G1 X96.131 Y90.154 E3.19539
G1 X95.484 Y90.154 E.0241
G1 X35.496 Y30.166 E3.16131
G1 X35.496 Y30.812 E.0241
G1 X94.838 Y90.154 E3.12723
G1 X94.191 Y90.154 E.0241
G1 X35.496 Y31.459 E3.09315
G1 X35.496 Y32.106 E.0241
G1 X93.544 Y90.154 E3.05907
G1 X92.898 Y90.154 E.0241
G1 X35.496 Y32.752 E3.02499
G1 X35.496 Y33.399 E.0241
G1 X92.251 Y90.154 E2.99091
G1 X91.604 Y90.154 E.0241
G1 X35.496 Y34.046 E2.95683
G1 X35.496 Y34.692 E.0241
G1 X90.958 Y90.154 E2.92275
G1 X90.311 Y90.154 E.0241
G1 X35.496 Y35.339 E2.88867
G1 X35.496 Y35.986 E.0241
G1 X89.664 Y90.154 E2.85459
G1 X89.017 Y90.154 E.0241
G1 X35.496 Y36.633 E2.82051
G1 X35.496 Y37.279 E.0241
G1 X88.371 Y90.154 E2.78643
G1 X87.724 Y90.154 E.0241
G1 X35.496 Y37.926 E2.75235
G1 X35.496 Y38.573 E.0241
G1 X87.077 Y90.154 E2.71827
G1 X86.431 Y90.154 E.0241
G1 X35.29 Y39.014 E2.69503
M204 S6000
G1 X35.54 Y39.91 F30000
G1 F6300
M204 S500
G1 X85.784 Y90.154 E2.64777
G1 X85.137 Y90.154 E.0241
G1 X35.746 Y40.763 E2.60286
G1 X35.746 Y41.41 E.0241
G1 X84.49 Y90.154 E2.56878
G1 X83.844 Y90.154 E.0241
G1 X35.746 Y42.056 E2.53469
G1 X35.746 Y42.703 E.0241
G1 X83.197 Y90.154 E2.50061
G1 X82.55 Y90.154 E.0241
G1 X35.746 Y43.35 E2.46653
G1 X35.746 Y43.996 E.0241
G1 X81.904 Y90.154 E2.43245
G1 X81.257 Y90.154 E.0241
G1 X35.746 Y44.643 E2.39837
G1 X35.746 Y45.29 E.0241
G1 X80.61 Y90.154 E2.36429
G1 X79.964 Y90.154 E.0241
G1 X35.746 Y45.936 E2.33021
G1 X35.746 Y46.583 E.0241
G1 X79.317 Y90.154 E2.29613
G1 X78.67 Y90.154 E.0241
G1 X35.461 Y46.946 E2.27703
G1 X34.815 Y46.946 E.0241
G1 X78.023 Y90.154 E2.27703
G1 X77.377 Y90.154 E.0241
G1 X34.168 Y46.946 E2.27703
G1 X33.521 Y46.946 E.0241
G1 X76.73 Y90.154 E2.27703
G1 X76.083 Y90.154 E.0241
G1 X32.874 Y46.946 E2.27703
G1 X32.228 Y46.946 E.0241
M73 P30 R23
G1 X75.437 Y90.154 E2.27703
G1 X74.79 Y90.154 E.0241
G1 X31.581 Y46.946 E2.27703
G1 X30.934 Y46.946 E.0241
G1 X74.143 Y90.154 E2.27703
G1 X73.496 Y90.154 E.0241
G1 X30.082 Y46.74 E2.28787
; WIPE_START
G1 X31.496 Y48.154 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X25.93 Y42.932 Z.6 F30000
G1 X21.04 Y38.345 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X72.85 Y90.154 E2.73029
G1 X72.203 Y90.154 E.0241
G1 X21.246 Y39.197 E2.68537
G1 X21.246 Y39.844 E.0241
G1 X71.556 Y90.154 E2.65129
G1 X70.91 Y90.154 E.0241
G1 X21.246 Y40.49 E2.61721
G1 X21.246 Y41.137 E.0241
G1 X70.263 Y90.154 E2.58313
G1 X69.616 Y90.154 E.0241
G1 X21.246 Y41.784 E2.54905
G1 X21.246 Y42.43 E.0241
G1 X68.97 Y90.154 E2.51497
G1 X68.323 Y90.154 E.0241
G1 X21.246 Y43.077 E2.48089
G1 X21.246 Y43.724 E.0241
G1 X67.676 Y90.154 E2.44681
G1 X67.029 Y90.154 E.0241
G1 X21.246 Y44.371 E2.41273
G1 X21.246 Y45.017 E.0241
G1 X66.383 Y90.154 E2.37865
G1 X65.736 Y90.154 E.0241
G1 X21.246 Y45.664 E2.34457
G1 X21.246 Y46.311 E.0241
G1 X65.089 Y90.154 E2.31049
G1 X64.443 Y90.154 E.0241
G1 X21.246 Y46.957 E2.27641
G1 X21.246 Y47.604 E.0241
G1 X63.796 Y90.154 E2.24233
G1 X63.149 Y90.154 E.0241
G1 X21.246 Y48.251 E2.20825
G1 X21.246 Y48.898 E.0241
G1 X62.502 Y90.154 E2.17417
G1 X61.856 Y90.154 E.0241
G1 X21.246 Y49.544 E2.14009
M73 P31 R23
G1 X21.246 Y50.191 E.0241
G1 X61.209 Y90.154 E2.10601
G1 X60.562 Y90.154 E.0241
G1 X21.246 Y50.838 E2.07193
G1 X21.246 Y51.484 E.0241
G1 X59.916 Y90.154 E2.03785
G1 X59.269 Y90.154 E.0241
G1 X21.246 Y52.131 E2.00377
G1 X21.246 Y52.778 E.0241
G1 X58.622 Y90.154 E1.96969
G1 X57.976 Y90.154 E.0241
G1 X21.246 Y53.424 E1.93561
G1 X21.246 Y54.071 E.0241
G1 X34.534 Y67.36 E.70028
G2 X33.785 Y67.257 I-.85 J3.422 E.02823
G1 X21.246 Y54.718 E.6608
G1 X21.246 Y55.365 E.0241
G1 X33.178 Y67.297 E.62883
G2 X32.652 Y67.418 I.604 J3.827 E.02012
G1 X21.246 Y56.011 E.60112
G1 X21.246 Y56.658 E.0241
G1 X32.192 Y67.605 E.57687
G2 X31.779 Y67.838 I2.291 J4.533 E.01769
M73 P31 R22
G1 X21.246 Y57.305 E.5551
G1 X21.246 Y57.951 E.0241
G1 X31.417 Y68.123 E.53601
G2 X31.095 Y68.447 I1.495 J1.803 E.01707
G1 X21.246 Y58.598 E.51905
G1 X21.246 Y59.245 E.0241
G1 X30.816 Y68.815 E.50433
G2 X30.586 Y69.232 I2.005 J1.378 E.01777
G1 X21.246 Y59.892 E.49222
G1 X21.246 Y60.538 E.0241
G1 X30.403 Y69.695 E.48257
G2 X30.289 Y70.229 I4.726 J1.284 E.02033
G1 X21.246 Y61.185 E.47659
G1 X21.246 Y61.832 E.0241
G1 X30.482 Y71.068 E.48674
; WIPE_START
G1 X29.068 Y69.654 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X36.7 Y69.554 Z.6 F30000
G1 X36.728 Y69.554 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X57.329 Y90.154 E1.08563
G1 X56.682 Y90.154 E.0241
M73 P32 R22
G1 X37.143 Y70.615 E1.02968
G3 X37.103 Y71.222 I-3.609 J.068 E.02269
G1 X56.035 Y90.154 E.9977
G1 X55.389 Y90.154 E.0241
G1 X36.982 Y71.748 E.97001
G3 X36.795 Y72.208 I-2.439 J-.72 E.01853
G1 X54.742 Y90.154 E.94576
G1 X54.095 Y90.154 E.0241
G1 X36.562 Y72.621 E.92399
G3 X36.277 Y72.983 I-1.974 J-1.257 E.01719
G1 X53.449 Y90.154 E.9049
G1 X52.802 Y90.154 E.0241
G1 X35.953 Y73.305 E.88793
G3 X35.585 Y73.584 I-2.936 J-3.485 E.01721
G1 X52.155 Y90.154 E.87322
G1 X51.508 Y90.154 E.0241
G1 X35.168 Y73.814 E.86111
G3 X34.705 Y73.997 I-1.165 J-2.271 E.0186
G1 X50.862 Y90.154 E.85146
G1 X50.215 Y90.154 E.0241
G1 X34.171 Y74.111 E.84548
G3 X33.554 Y74.14 I-.472 J-3.439 E.02306
G1 X49.568 Y90.154 E.84394
G1 X48.922 Y90.154 E.0241
G1 X32.788 Y74.021 E.85021
G3 X30.379 Y71.612 I.894 J-3.303 E.13289
G1 X21.246 Y62.478 E.48132
G1 X21.246 Y63.125 E.0241
G1 X48.275 Y90.154 E1.4244
G1 X47.628 Y90.154 E.0241
G1 X21.246 Y63.772 E1.39032
G1 X21.246 Y64.418 E.0241
G1 X46.982 Y90.154 E1.35624
G1 X46.335 Y90.154 E.0241
G1 X21.246 Y65.065 E1.32216
G1 X21.246 Y65.712 E.0241
G1 X45.688 Y90.154 E1.28808
G1 X45.041 Y90.154 E.0241
G1 X21.246 Y66.359 E1.254
G1 X21.246 Y67.005 E.0241
G1 X44.395 Y90.154 E1.21992
G1 X43.748 Y90.154 E.0241
G1 X21.246 Y67.652 E1.18584
G1 X21.246 Y68.299 E.0241
G1 X43.101 Y90.154 E1.15176
G1 X42.455 Y90.154 E.0241
G1 X21.246 Y68.945 E1.11768
G1 X21.246 Y69.592 E.0241
G1 X41.808 Y90.154 E1.0836
G1 X41.161 Y90.154 E.0241
G1 X21.246 Y70.239 E1.04952
G1 X21.246 Y70.886 E.0241
G1 X40.514 Y90.154 E1.01544
G1 X39.868 Y90.154 E.0241
G1 X21.246 Y71.532 E.98136
G1 X21.246 Y72.179 E.0241
M73 P33 R22
G1 X39.221 Y90.154 E.94728
G1 X38.574 Y90.154 E.0241
G1 X21.246 Y72.826 E.9132
G1 X21.246 Y73.472 E.0241
G1 X37.928 Y90.154 E.87912
G1 X37.281 Y90.154 E.0241
G1 X21.246 Y74.119 E.84504
G1 X21.246 Y74.766 E.0241
G1 X36.634 Y90.154 E.81096
G1 X35.988 Y90.154 E.0241
G1 X21.246 Y75.412 E.77688
G1 X21.246 Y76.059 E.0241
G1 X35.341 Y90.154 E.7428
G1 X34.694 Y90.154 E.0241
G1 X21.246 Y76.706 E.70872
G1 X21.246 Y77.353 E.0241
G1 X34.047 Y90.154 E.67464
G1 X33.401 Y90.154 E.0241
G1 X21.246 Y77.999 E.64056
G1 X21.246 Y78.646 E.0241
G1 X32.754 Y90.154 E.60648
G1 X32.107 Y90.154 E.0241
G1 X21.246 Y79.293 E.5724
G1 X21.246 Y79.939 E.0241
G1 X31.461 Y90.154 E.53831
G1 X30.814 Y90.154 E.0241
G1 X21.246 Y80.586 E.50423
G1 X21.246 Y81.233 E.0241
G1 X30.167 Y90.154 E.47015
G1 X29.52 Y90.154 E.0241
G1 X21.246 Y81.88 E.43607
G1 X21.246 Y82.526 E.0241
G1 X28.874 Y90.154 E.40199
G1 X28.227 Y90.154 E.0241
G1 X21.246 Y83.173 E.36791
G1 X21.246 Y83.82 E.0241
G1 X27.58 Y90.154 E.33383
G1 X26.934 Y90.154 E.0241
G1 X21.246 Y84.466 E.29975
G1 X21.246 Y85.113 E.0241
G1 X26.287 Y90.154 E.26567
G1 X25.64 Y90.154 E.0241
G1 X21.246 Y85.76 E.23159
G1 X21.246 Y86.406 E.0241
G1 X24.994 Y90.154 E.19751
G1 X24.347 Y90.154 E.0241
G1 X21.246 Y87.053 E.16343
G1 X21.246 Y87.7 E.0241
G1 X23.7 Y90.154 E.12935
G1 X23.053 Y90.154 E.0241
G1 X21.246 Y88.347 E.09527
G1 X21.246 Y88.993 E.0241
G1 X22.407 Y90.154 E.06119
G1 X21.76 Y90.154 E.0241
G1 X21.04 Y89.434 E.03795
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6300
G1 X21.76 Y90.154 E-.387
G1 X22.407 Y90.154 E-.24575
G1 X22.17 Y89.918 E-.12725
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 2/40
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
M106 S255
M106 P2 S178
; open powerlost recovery
M1003 S1
M976 S1 P1 ; scan model before printing 2nd layer
M400 P100
G1 E.8
G1 E-.8
M204 S10000
G17
G3 Z.6 I1.217 J0 P1  F30000
; object ids of layer 2 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer2 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z.8 F30000
M73 P34 R22
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z.8 F30000
G1 X160.4 Y8 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z.8 F30000
G1 X114.002 Y8.498 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
M73 P34 R21
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z.8 F30000
G1 X93.502 Y73.11 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z.8 F30000
G1 X97.11 Y46.302 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.802 E.3747
G1 X90.498 Y28.802 E.068
G1 X90.498 Y22.398 E.21244
G1 X92.548 Y22.398 E.068
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.302 Y22.398 E.068
G1 X99.302 Y28.802 E.21244
G1 X97.252 Y28.802 E.068
G1 X97.252 Y40.098 E.3747
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.41 E.37119
G1 X90.89 Y28.41 E.06299
G1 X90.89 Y22.79 E.17269
G1 X92.94 Y22.79 E.06299
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.91 Y22.79 E.06299
G1 X98.91 Y28.41 E.17269
G1 X96.86 Y28.41 E.06299
G1 X96.86 Y40.49 E.37119
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z.8 F30000
G1 X35.102 Y45.91 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.802 E.3747
G1 X28.098 Y28.802 E.068
G1 X28.098 Y22.398 E.21244
G1 X30.148 Y22.398 E.068
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.902 Y22.398 E.068
G1 X36.902 Y28.802 E.21244
G1 X34.852 Y28.802 E.068
G1 X34.852 Y40.098 E.3747
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.41 E.37119
G1 X28.49 Y28.41 E.06299
G1 X28.49 Y22.79 E.17269
G1 X30.54 Y22.79 E.06299
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.51 Y22.79 E.06299
G1 X36.51 Y28.41 E.17269
G1 X34.46 Y28.41 E.06299
G1 X34.46 Y40.49 E.37119
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.016 Y53.503 Z.8 F30000
G1 X33.819 Y73.497 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.7 Y73.499 E.00393
G3 X33.425 Y67.911 I0 J-2.801 E.28278
G1 X33.7 Y67.897 E.00912
G3 X33.974 Y73.486 I0 J2.801 E.28279
G1 X33.878 Y73.493 E.00319
G1 X33.797 Y73.101 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.7 Y73.107 E.00298
G3 X33.464 Y68.301 I0 J-2.409 E.22525
G1 X33.7 Y68.29 E.00727
G3 X34.17 Y73.061 I0 J2.409 E.21801
G1 X33.857 Y73.094 E.00968
; WIPE_START
M204 S10000
G1 X33.7 Y73.107 E-.05967
G1 X33.23 Y73.064 E-.17946
G1 X32.778 Y72.927 E-.17952
G1 X32.361 Y72.704 E-.17956
G1 X32.032 Y72.434 E-.16179
; WIPE_END
G1 E-.04 F1800
G1 X39.444 Y74.254 Z.8 F30000
G1 X106.798 Y90.798 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X105.872 Y90.634 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42021
G1 F15000
G1 X106.465 Y90.041 E.02578
G1 X106.465 Y89.508 E.0164
G1 X105.508 Y90.465 E.04161
G1 X104.974 Y90.465 E.0164
G1 X106.465 Y88.974 E.06481
G1 X106.465 Y88.441 E.0164
G1 X104.441 Y90.465 E.088
G1 X103.907 Y90.465 E.0164
G1 X106.465 Y87.907 E.1112
G1 X106.465 Y87.373 E.0164
G1 X103.373 Y90.465 E.1344
G1 X102.84 Y90.465 E.0164
G1 X106.465 Y86.84 E.1576
G1 X106.465 Y86.306 E.0164
G1 X102.306 Y90.465 E.1808
G1 X101.773 Y90.465 E.0164
G1 X106.465 Y85.773 E.204
G1 X106.465 Y85.239 E.0164
G1 X101.239 Y90.465 E.2272
G1 X100.706 Y90.465 E.0164
G1 X106.465 Y84.706 E.2504
G1 X106.465 Y84.172 E.0164
G1 X100.172 Y90.465 E.2736
G1 X99.639 Y90.465 E.0164
G1 X106.465 Y83.639 E.2968
G1 X106.465 Y83.105 E.0164
G1 X99.105 Y90.465 E.32
G1 X98.571 Y90.465 E.0164
G1 X106.465 Y82.571 E.34319
G1 X106.465 Y82.038 E.0164
G1 X98.038 Y90.465 E.36639
G1 X97.504 Y90.465 E.0164
G1 X106.465 Y81.504 E.38959
G1 X106.465 Y80.971 E.0164
G1 X96.971 Y90.465 E.41279
G1 X96.437 Y90.465 E.0164
G1 X106.465 Y80.437 E.43599
G1 X106.465 Y79.904 E.0164
G1 X95.904 Y90.465 E.45919
G1 X95.37 Y90.465 E.0164
G1 X106.465 Y79.37 E.48239
G1 X106.465 Y78.836 E.0164
G1 X94.836 Y90.465 E.50559
G1 X94.303 Y90.465 E.0164
G1 X106.465 Y78.303 E.52879
G1 X106.465 Y77.769 E.0164
G1 X93.769 Y90.465 E.55199
G1 X93.236 Y90.465 E.0164
G1 X106.465 Y77.236 E.57519
G1 X106.465 Y76.702 E.0164
G1 X92.702 Y90.465 E.59838
G1 X92.169 Y90.465 E.0164
G1 X106.465 Y76.169 E.62158
G1 X106.465 Y75.635 E.0164
G1 X91.635 Y90.465 E.64478
G1 X91.101 Y90.465 E.0164
G1 X106.465 Y75.101 E.66798
G1 X106.465 Y74.568 E.0164
G1 X90.568 Y90.465 E.69118
G1 X90.034 Y90.465 E.0164
G1 X106.465 Y74.034 E.71438
G1 X106.465 Y73.501 E.0164
G1 X89.501 Y90.465 E.73758
G1 X88.967 Y90.465 E.0164
G1 X106.465 Y72.967 E.76078
G1 X106.465 Y72.434 E.0164
G1 X88.434 Y90.465 E.78398
G1 X87.9 Y90.465 E.0164
G1 X106.465 Y71.9 E.80718
G1 X106.465 Y71.366 E.0164
G1 X87.366 Y90.465 E.83037
G1 X86.833 Y90.465 E.0164
G1 X106.465 Y70.833 E.85357
G1 X106.465 Y70.299 E.0164
G1 X86.299 Y90.465 E.87677
G1 X85.766 Y90.465 E.0164
G1 X106.465 Y69.766 E.89997
G1 X106.465 Y69.232 E.0164
G1 X85.232 Y90.465 E.92317
G1 X84.699 Y90.465 E.0164
G1 X106.465 Y68.699 E.94637
G1 X106.465 Y68.165 E.0164
G1 X84.165 Y90.465 E.96957
G1 X83.631 Y90.465 E.0164
G1 X106.465 Y67.631 E.99277
G1 X106.465 Y67.098 E.0164
G1 X83.098 Y90.465 E1.01597
G1 X82.564 Y90.465 E.0164
G1 X106.465 Y66.564 E1.03917
M73 P35 R21
G1 X106.465 Y66.031 E.0164
G1 X82.031 Y90.465 E1.06237
G1 X81.497 Y90.465 E.0164
G1 X106.465 Y65.497 E1.08556
G1 X106.465 Y64.964 E.0164
G1 X80.964 Y90.465 E1.10876
G1 X80.43 Y90.465 E.0164
G1 X106.465 Y64.43 E1.13196
G1 X106.465 Y63.896 E.0164
G1 X79.896 Y90.465 E1.15516
G1 X79.363 Y90.465 E.0164
G1 X106.465 Y63.363 E1.17836
G1 X106.465 Y62.829 E.0164
G1 X78.829 Y90.465 E1.20156
G1 X78.296 Y90.465 E.0164
G1 X106.465 Y62.296 E1.22476
G1 X106.465 Y61.762 E.0164
G1 X77.762 Y90.465 E1.24796
G1 X77.229 Y90.465 E.0164
G1 X106.465 Y61.229 E1.27116
G1 X106.465 Y60.695 E.0164
G1 X93.835 Y73.324 E.54911
G1 X93.835 Y72.791 E.0164
G1 X106.465 Y60.161 E.54911
G1 X106.465 Y59.628 E.0164
G1 X93.835 Y72.257 E.54911
G1 X93.835 Y71.724 E.0164
G1 X106.465 Y59.094 E.54911
G1 X106.465 Y58.561 E.0164
G1 X93.835 Y71.19 E.54911
G1 X93.835 Y70.657 E.0164
G1 X106.465 Y58.027 E.54911
G1 X106.465 Y57.494 E.0164
G1 X93.835 Y70.123 E.54911
G1 X93.835 Y69.589 E.0164
G1 X106.465 Y56.96 E.54911
G1 X106.465 Y56.427 E.0164
G1 X93.835 Y69.056 E.54911
G1 X93.835 Y68.522 E.0164
G1 X106.465 Y55.893 E.54911
G1 X106.465 Y55.359 E.0164
G1 X93.835 Y67.989 E.54911
G1 X93.835 Y67.565 E.01304
G1 X93.726 Y67.565 E.00337
G1 X106.465 Y54.826 E.55388
G1 X106.465 Y54.292 E.0164
G1 X93.192 Y67.565 E.57707
G1 X92.659 Y67.565 E.0164
G1 X106.465 Y53.759 E.60027
G1 X106.465 Y53.225 E.0164
G1 X92.125 Y67.565 E.62347
G1 X91.592 Y67.565 E.0164
G1 X106.465 Y52.692 E.64667
G1 X106.465 Y52.158 E.0164
G1 X91.058 Y67.565 E.66987
G1 X90.524 Y67.565 E.0164
G1 X106.465 Y51.624 E.69307
G1 X106.465 Y51.091 E.0164
G1 X89.991 Y67.565 E.71627
G1 X89.457 Y67.565 E.0164
G1 X106.465 Y50.557 E.73947
G1 X106.465 Y50.024 E.0164
G1 X88.924 Y67.565 E.76267
G1 X88.39 Y67.565 E.0164
G1 X106.465 Y49.49 E.78587
G1 X106.465 Y48.957 E.0164
G1 X87.857 Y67.565 E.80907
G1 X87.323 Y67.565 E.0164
G1 X106.465 Y48.423 E.83226
G1 X106.465 Y47.889 E.0164
G1 X86.789 Y67.565 E.85546
G1 X86.256 Y67.565 E.0164
G1 X106.465 Y47.356 E.87866
G1 X106.465 Y46.822 E.0164
G1 X85.722 Y67.565 E.90186
G1 X85.189 Y67.565 E.0164
G1 X106.465 Y46.289 E.92506
G1 X106.465 Y45.755 E.0164
G1 X84.655 Y67.565 E.94826
G1 X84.122 Y67.565 E.0164
G1 X106.465 Y45.222 E.97146
G1 X106.465 Y44.688 E.0164
G1 X60.688 Y90.465 E1.99033
G1 X61.222 Y90.465 E.0164
G1 X83.565 Y68.122 E.97146
G1 X83.565 Y68.655 E.0164
G1 X61.755 Y90.465 E.94826
G1 X62.289 Y90.465 E.0164
G1 X83.565 Y69.189 E.92506
G1 X83.565 Y69.722 E.0164
G1 X62.822 Y90.465 E.90186
G1 X63.356 Y90.465 E.0164
G1 X83.565 Y70.256 E.87866
G1 X83.565 Y70.789 E.0164
G1 X63.889 Y90.465 E.85546
G1 X64.423 Y90.465 E.0164
G1 X83.565 Y71.323 E.83226
G1 X83.565 Y71.857 E.0164
G1 X64.957 Y90.465 E.80907
G1 X65.49 Y90.465 E.0164
G1 X83.565 Y72.39 E.78587
G1 X83.565 Y72.924 E.0164
G1 X66.024 Y90.465 E.76267
G1 X66.557 Y90.465 E.0164
G1 X83.565 Y73.457 E.73947
G1 X83.565 Y73.835 E.01162
G1 X83.72 Y73.835 E.00478
G1 X67.091 Y90.465 E.72303
G1 X67.624 Y90.465 E.0164
G1 X84.254 Y73.835 E.72303
G1 X84.787 Y73.835 E.0164
G1 X68.158 Y90.465 E.72303
G1 X68.692 Y90.465 E.0164
G1 X85.321 Y73.835 E.72303
G1 X85.854 Y73.835 E.0164
G1 X69.225 Y90.465 E.72303
G1 X69.759 Y90.465 E.0164
G1 X86.388 Y73.835 E.72303
G1 X86.922 Y73.835 E.0164
G1 X70.292 Y90.465 E.72303
G1 X70.826 Y90.465 E.0164
G1 X87.455 Y73.835 E.72303
G1 X87.989 Y73.835 E.0164
G1 X71.359 Y90.465 E.72303
G1 X71.893 Y90.465 E.0164
G1 X88.522 Y73.835 E.72303
G1 X89.056 Y73.835 E.0164
G1 X72.426 Y90.465 E.72303
G1 X72.96 Y90.465 E.0164
G1 X89.589 Y73.835 E.72303
G1 X90.123 Y73.835 E.0164
G1 X73.494 Y90.465 E.72303
G1 X74.027 Y90.465 E.0164
G1 X90.657 Y73.835 E.72303
G1 X91.19 Y73.835 E.0164
G1 X74.561 Y90.465 E.72303
G1 X75.094 Y90.465 E.0164
G1 X91.724 Y73.835 E.72303
G1 X92.257 Y73.835 E.0164
G1 X75.628 Y90.465 E.72303
G1 X76.161 Y90.465 E.0164
G1 X92.791 Y73.835 E.72303
G1 X93.324 Y73.835 E.0164
G1 X76.525 Y90.634 E.73041
G1 X59.985 Y90.634 F30000
G1 F15000
G1 X106.465 Y44.154 E2.02091
G1 X106.465 Y43.621 E.0164
G1 X59.621 Y90.465 E2.03673
G1 X59.087 Y90.465 E.0164
G1 X106.465 Y43.087 E2.05993
G1 X106.465 Y42.554 E.0164
G1 X58.554 Y90.465 E2.08313
G1 X58.02 Y90.465 E.0164
G1 X106.465 Y42.02 E2.10632
G1 X106.465 Y41.487 E.0164
G1 X57.487 Y90.465 E2.12952
G1 X56.953 Y90.465 E.0164
G1 X106.465 Y40.953 E2.15272
G1 X106.465 Y40.419 E.0164
G1 X56.419 Y90.465 E2.17592
G1 X55.886 Y90.465 E.0164
G1 X106.465 Y39.886 E2.19912
G1 X106.465 Y39.352 E.0164
G1 X55.352 Y90.465 E2.22232
G1 X54.819 Y90.465 E.0164
G1 X106.465 Y38.819 E2.24552
G1 X106.465 Y38.285 E.0164
G1 X54.285 Y90.465 E2.26872
G1 X53.752 Y90.465 E.0164
G1 X106.465 Y37.752 E2.29192
G1 X106.465 Y37.218 E.0164
G1 X97.835 Y45.847 E.3752
G1 X97.835 Y45.314 E.0164
G1 X106.465 Y36.684 E.3752
G1 X106.465 Y36.151 E.0164
G1 X97.835 Y44.78 E.3752
G1 X97.835 Y44.247 E.0164
G1 X106.465 Y35.617 E.3752
G1 X106.465 Y35.084 E.0164
G1 X97.835 Y43.713 E.3752
G1 X97.835 Y43.18 E.0164
G1 X106.465 Y34.55 E.3752
G1 X106.465 Y34.017 E.0164
G1 X97.835 Y42.646 E.3752
G1 X97.835 Y42.112 E.0164
G1 X106.465 Y33.483 E.3752
G1 X106.465 Y32.949 E.0164
G1 X97.835 Y41.579 E.3752
G1 X97.835 Y41.045 E.0164
G1 X106.465 Y32.416 E.3752
G1 X106.465 Y31.882 E.0164
G1 X97.835 Y40.512 E.3752
G1 X97.835 Y39.978 E.0164
G1 X106.465 Y31.349 E.3752
G1 X106.465 Y30.815 E.0164
G1 X97.585 Y39.695 E.38607
G1 X97.585 Y39.161 E.0164
G1 X106.465 Y30.282 E.38607
G1 X106.465 Y29.748 E.0164
G1 X97.585 Y38.627 E.38607
G1 X97.585 Y38.094 E.0164
G1 X106.465 Y29.215 E.38607
G1 X106.465 Y28.681 E.0164
G1 X97.585 Y37.56 E.38607
G1 X97.585 Y37.027 E.0164
G1 X106.465 Y28.147 E.38607
G1 X106.465 Y27.614 E.0164
G1 X97.585 Y36.493 E.38607
G1 X97.585 Y35.96 E.0164
G1 X106.465 Y27.08 E.38607
G1 X106.465 Y26.547 E.0164
G1 X97.585 Y35.426 E.38607
G1 X97.585 Y34.892 E.0164
G1 X106.465 Y26.013 E.38607
G1 X106.465 Y25.48 E.0164
G1 X97.585 Y34.359 E.38607
G1 X97.585 Y33.825 E.0164
G1 X106.465 Y24.946 E.38607
G1 X106.465 Y24.412 E.0164
G1 X97.585 Y33.292 E.38607
G1 X97.585 Y32.758 E.0164
G1 X106.465 Y23.879 E.38607
G1 X106.465 Y23.345 E.0164
G1 X97.585 Y32.225 E.38607
G1 X97.585 Y31.691 E.0164
G1 X106.465 Y22.812 E.38607
G1 X106.465 Y22.278 E.0164
G1 X97.585 Y31.157 E.38607
G1 X97.585 Y30.624 E.0164
G1 X99.074 Y29.135 E.06472
G1 X98.54 Y29.135 E.0164
G1 X97.585 Y30.09 E.04152
G1 X97.585 Y29.557 E.0164
G1 X98.176 Y28.966 E.0257
; WIPE_START
G1 X97.585 Y29.557 E-.31767
G1 X97.585 Y30.09 E-.20275
G1 X98.031 Y29.645 E-.23958
; WIPE_END
G1 E-.04 F1800
G1 X99.466 Y28.744 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F15000
G1 X106.465 Y21.745 E.30431
G1 X106.465 Y21.211 E.0164
G1 X99.635 Y28.04 E.29693
G1 X99.635 Y27.507 E.0164
G1 X106.465 Y20.677 E.29693
G1 X106.465 Y20.144 E.0164
G1 X99.635 Y26.973 E.29693
G1 X99.635 Y26.44 E.0164
G1 X106.465 Y19.61 E.29693
G1 X106.465 Y19.077 E.0164
G1 X99.635 Y25.906 E.29693
G1 X99.635 Y25.372 E.0164
G1 X106.465 Y18.543 E.29693
G1 X106.465 Y18.01 E.0164
G1 X99.635 Y24.839 E.29693
G1 X99.635 Y24.305 E.0164
G1 X106.465 Y17.476 E.29693
G1 X106.465 Y16.942 E.0164
G1 X99.635 Y23.772 E.29693
G1 X99.635 Y23.238 E.0164
G1 X106.465 Y16.409 E.29693
G1 X106.465 Y15.875 E.0164
G1 X99.635 Y22.705 E.29693
G1 X99.635 Y22.171 E.0164
G1 X106.465 Y15.342 E.29693
M73 P36 R21
G1 X106.465 Y14.808 E.0164
G1 X99.208 Y22.065 E.31551
G1 X98.675 Y22.065 E.0164
G1 X106.465 Y14.275 E.33871
G1 X106.465 Y13.741 E.0164
G1 X98.141 Y22.065 E.3619
G1 X97.607 Y22.065 E.0164
G1 X106.465 Y13.207 E.3851
G1 X106.465 Y12.674 E.0164
G1 X97.374 Y21.765 E.39526
G1 X96.84 Y21.765 E.0164
G1 X106.465 Y12.14 E.41846
G1 X106.465 Y11.607 E.0164
G1 X96.307 Y21.765 E.44166
G1 X95.773 Y21.765 E.0164
G1 X106.465 Y11.073 E.46486
G1 X106.465 Y10.54 E.0164
G1 X95.24 Y21.765 E.48806
G1 X94.706 Y21.765 E.0164
G1 X106.465 Y10.006 E.51125
G1 X106.465 Y9.472 E.0164
G1 X94.172 Y21.765 E.53445
G1 X93.639 Y21.765 E.0164
G1 X106.465 Y8.939 E.55765
G1 X106.465 Y8.405 E.0164
G1 X93.105 Y21.765 E.58085
G1 X92.572 Y21.765 E.0164
G1 X106.465 Y7.872 E.60405
G1 X106.465 Y7.338 E.0164
G1 X91.738 Y22.065 E.64029
G1 X91.205 Y22.065 E.0164
G1 X106.465 Y6.805 E.66349
G1 X106.465 Y6.271 E.0164
G1 X90.671 Y22.065 E.68669
G1 X90.165 Y22.065 E.01557
G1 X90.165 Y22.571 E.01557
G1 X22.271 Y90.465 E2.95195
G1 X22.805 Y90.465 E.0164
G1 X90.165 Y23.105 E2.92875
G1 X90.165 Y23.638 E.0164
G1 X23.338 Y90.465 E2.90556
G1 X23.872 Y90.465 E.0164
G1 X90.165 Y24.172 E2.88236
G1 X90.165 Y24.705 E.0164
G1 X24.405 Y90.465 E2.85916
G1 X24.939 Y90.465 E.0164
G1 X90.165 Y25.239 E2.83596
G1 X90.165 Y25.772 E.0164
G1 X25.472 Y90.465 E2.81276
G1 X26.006 Y90.465 E.0164
G1 X90.165 Y26.306 E2.78956
G1 X90.165 Y26.84 E.0164
G1 X26.54 Y90.465 E2.76636
G1 X27.073 Y90.465 E.0164
G1 X90.165 Y27.373 E2.74316
G1 X90.165 Y27.907 E.0164
G1 X27.607 Y90.465 E2.71996
G1 X28.14 Y90.465 E.0164
G1 X90.165 Y28.44 E2.69676
G1 X90.165 Y28.974 E.0164
G1 X28.674 Y90.465 E2.67356
G1 X29.207 Y90.465 E.0164
G1 X90.537 Y29.135 E2.66655
G1 X91.07 Y29.135 E.0164
G1 X29.741 Y90.465 E2.66655
G1 X30.275 Y90.465 E.0164
G1 X91.604 Y29.135 E2.66655
G1 X92.138 Y29.135 E.0164
G1 X30.808 Y90.465 E2.66655
G1 X31.342 Y90.465 E.0164
G1 X92.215 Y29.592 E2.6467
G1 X92.215 Y30.125 E.0164
G1 X31.875 Y90.465 E2.6235
G1 X32.409 Y90.465 E.0164
G1 X92.215 Y30.659 E2.6003
G1 X92.215 Y31.192 E.0164
G1 X32.942 Y90.465 E2.5771
G1 X33.476 Y90.465 E.0164
G1 X92.215 Y31.726 E2.55391
G1 X92.215 Y32.26 E.0164
G1 X34.01 Y90.465 E2.53071
G1 X34.543 Y90.465 E.0164
G1 X92.215 Y32.793 E2.50751
G1 X92.215 Y33.327 E.0164
G1 X35.077 Y90.465 E2.48431
G1 X35.61 Y90.465 E.0164
G1 X92.215 Y33.86 E2.46111
G1 X92.215 Y34.394 E.0164
G1 X36.144 Y90.465 E2.43791
G1 X36.677 Y90.465 E.0164
G1 X92.215 Y34.927 E2.41471
G1 X92.215 Y35.461 E.0164
G1 X37.211 Y90.465 E2.39151
G1 X37.745 Y90.465 E.0164
G1 X92.215 Y35.995 E2.36831
G1 X92.215 Y36.528 E.0164
G1 X38.278 Y90.465 E2.34511
G1 X38.812 Y90.465 E.0164
G1 X92.215 Y37.062 E2.32191
G1 X92.215 Y37.595 E.0164
G1 X39.345 Y90.465 E2.29872
G1 X39.879 Y90.465 E.0164
G1 X92.215 Y38.129 E2.27552
G1 X92.215 Y38.662 E.0164
G1 X40.412 Y90.465 E2.25232
G1 X40.946 Y90.465 E.0164
G1 X92.215 Y39.196 E2.22912
G1 X92.215 Y39.73 E.0164
G1 X41.48 Y90.465 E2.20592
G1 X42.013 Y90.465 E.0164
G1 X91.965 Y40.513 E2.17185
G1 X91.965 Y41.047 E.0164
G1 X42.547 Y90.465 E2.14865
G1 X43.08 Y90.465 E.0164
G1 X91.965 Y41.58 E2.12545
G1 X91.965 Y42.114 E.0164
G1 X43.614 Y90.465 E2.10225
G1 X44.147 Y90.465 E.0164
G1 X91.965 Y42.647 E2.07905
G1 X91.965 Y43.181 E.0164
G1 X44.681 Y90.465 E2.05585
G1 X45.214 Y90.465 E.0164
G1 X91.965 Y43.715 E2.03266
G1 X91.965 Y44.248 E.0164
G1 X45.748 Y90.465 E2.00946
G1 X46.282 Y90.465 E.0164
G1 X91.965 Y44.782 E1.98626
G1 X91.965 Y45.315 E.0164
G1 X46.815 Y90.465 E1.96306
G1 X47.349 Y90.465 E.0164
G1 X91.965 Y45.849 E1.93986
G1 X91.965 Y46.382 E.0164
G1 X47.882 Y90.465 E1.91666
G1 X48.416 Y90.465 E.0164
G1 X92.245 Y46.635 E1.90566
G1 X92.779 Y46.635 E.0164
G1 X48.949 Y90.465 E1.90566
G1 X49.483 Y90.465 E.0164
G1 X93.312 Y46.635 E1.90566
G1 X93.846 Y46.635 E.0164
G1 X50.017 Y90.465 E1.90566
G1 X50.55 Y90.465 E.0164
G1 X94.38 Y46.635 E1.90566
G1 X94.913 Y46.635 E.0164
G1 X51.084 Y90.465 E1.90566
G1 X51.617 Y90.465 E.0164
G1 X95.447 Y46.635 E1.90566
G1 X95.98 Y46.635 E.0164
G1 X52.151 Y90.465 E1.90566
G1 X52.684 Y90.465 E.0164
G1 X96.514 Y46.635 E1.90566
G1 X97.047 Y46.635 E.0164
G1 X53.048 Y90.634 E1.91304
G1 X21.568 Y90.634 F30000
G1 F15000
G1 X106.465 Y5.737 E3.69124
G1 X106.465 Y5.204 E.0164
G1 X21.204 Y90.465 E3.70706
G1 X20.935 Y90.465 E.00826
G1 X20.935 Y90.2 E.00815
G1 X106.2 Y4.935 E3.70722
G1 X105.666 Y4.935 E.0164
G1 X20.935 Y89.666 E3.68402
G1 X20.935 Y89.133 E.0164
G1 X105.133 Y4.935 E3.66082
G1 X104.599 Y4.935 E.0164
G1 X20.935 Y88.599 E3.63762
G1 X20.935 Y88.065 E.0164
G1 X104.065 Y4.935 E3.61442
G1 X103.532 Y4.935 E.0164
G1 X36.615 Y71.852 E2.90949
G2 X36.803 Y71.131 I-3.032 J-1.176 E.02298
G1 X102.998 Y4.935 E2.87811
G1 X102.465 Y4.935 E.0164
G1 X36.83 Y70.57 E2.85373
G2 X36.776 Y70.09 I-2.463 J.032 E.01487
G1 X101.931 Y4.935 E2.83287
G1 X101.398 Y4.935 E.0164
G1 X36.66 Y69.673 E2.81474
G2 X36.502 Y69.297 I-1.992 J.616 E.01255
G1 X100.864 Y4.935 E2.7984
G1 X100.33 Y4.935 E.0164
G1 X36.308 Y68.957 E2.78363
G2 X36.076 Y68.656 I-1.638 J1.023 E.01171
G1 X99.797 Y4.935 E2.77054
G1 X99.263 Y4.935 E.0164
G1 X35.812 Y68.386 E2.7588
G2 X35.517 Y68.148 I-1.356 J1.373 E.01168
G1 X98.73 Y4.935 E2.74842
G1 X98.196 Y4.935 E.0164
G1 X35.19 Y67.941 E2.73943
G2 X34.823 Y67.775 I-2.158 J4.277 E.0124
G1 X97.663 Y4.935 E2.7322
G1 X97.129 Y4.935 E.0164
G1 X34.415 Y67.65 E2.72676
G2 X33.955 Y67.576 I-.795 J3.496 E.01433
G1 X96.595 Y4.935 E2.72356
G1 X96.062 Y4.935 E.0164
G1 X33.42 Y67.577 E2.72362
G2 X32.751 Y67.712 I.101 J2.223 E.02105
G1 X95.528 Y4.935 E2.72948
G1 X94.995 Y4.935 E.0164
G1 X20.935 Y78.995 E3.22004
G1 X20.935 Y79.528 E.0164
G1 X30.712 Y69.751 E.42509
G2 X30.577 Y70.42 I2.087 J.769 E.02105
G1 X20.935 Y80.062 E.41922
G1 X20.935 Y80.595 E.0164
G1 X30.576 Y70.955 E.41917
G2 X30.65 Y71.415 I3.572 J-.335 E.01433
G1 X20.935 Y81.129 E.42237
G1 X20.935 Y81.663 E.0164
G1 X30.775 Y71.823 E.42781
G2 X30.941 Y72.19 I4.448 J-1.793 E.0124
M73 P37 R21
G1 X20.935 Y82.196 E.43504
G1 X20.935 Y82.73 E.0164
G1 X31.148 Y72.517 E.44402
G2 X31.386 Y72.812 I1.611 J-1.061 E.01168
G1 X20.935 Y83.263 E.45441
G1 X20.935 Y83.797 E.0164
G1 X31.656 Y73.076 E.46614
G2 X31.958 Y73.308 I3.815 J-4.637 E.0117
G1 X20.935 Y84.33 E.47924
G1 X20.935 Y84.864 E.0164
G1 X32.297 Y73.502 E.49401
G2 X32.673 Y73.66 I.991 J-1.834 E.01255
G1 X20.935 Y85.398 E.51035
G1 X20.935 Y85.931 E.0164
G1 X33.09 Y73.776 E.52847
G2 X33.57 Y73.83 I.512 J-2.41 E.01487
G1 X20.935 Y86.465 E.54934
G1 X20.935 Y86.998 E.0164
G1 X34.131 Y73.803 E.57372
G2 X34.852 Y73.615 I-.455 J-3.222 E.02298
G1 X20.766 Y87.702 E.61248
G1 X20.766 Y78.631 F30000
G1 F15000
G1 X94.461 Y4.935 E3.20421
G1 X93.928 Y4.935 E.0164
G1 X20.935 Y77.928 E3.17364
G1 X20.935 Y77.394 E.0164
G1 X93.394 Y4.935 E3.15044
G1 X92.861 Y4.935 E.0164
G1 X20.935 Y76.86 E3.12724
G1 X20.935 Y76.327 E.0164
G1 X92.327 Y4.935 E3.10404
G1 X91.793 Y4.935 E.0164
G1 X20.935 Y75.793 E3.08084
G1 X20.935 Y75.26 E.0164
G1 X91.26 Y4.935 E3.05764
G1 X90.726 Y4.935 E.0164
G1 X20.935 Y74.726 E3.03444
G1 X20.935 Y74.193 E.0164
G1 X90.193 Y4.935 E3.01125
G1 X89.659 Y4.935 E.0164
G1 X20.935 Y73.659 E2.98805
G1 X20.935 Y73.125 E.0164
G1 X89.126 Y4.935 E2.96485
G1 X88.592 Y4.935 E.0164
G1 X20.935 Y72.592 E2.94165
G1 X20.935 Y72.058 E.0164
G1 X88.058 Y4.935 E2.91845
G1 X87.525 Y4.935 E.0164
G1 X20.935 Y71.525 E2.89525
G1 X20.935 Y70.991 E.0164
G1 X86.991 Y4.935 E2.87205
G1 X86.458 Y4.935 E.0164
G1 X20.935 Y70.458 E2.84885
M73 P37 R20
G1 X20.935 Y69.924 E.0164
G1 X85.924 Y4.935 E2.82565
G1 X85.391 Y4.935 E.0164
G1 X20.935 Y69.391 E2.80245
G1 X20.935 Y68.857 E.0164
G1 X84.857 Y4.935 E2.77925
G1 X84.323 Y4.935 E.0164
G1 X20.935 Y68.323 E2.75606
G1 X20.935 Y67.79 E.0164
G1 X83.79 Y4.935 E2.73286
G1 X83.256 Y4.935 E.0164
G1 X20.935 Y67.256 E2.70966
G1 X20.935 Y66.723 E.0164
G1 X82.723 Y4.935 E2.68646
G1 X82.189 Y4.935 E.0164
G1 X20.935 Y66.189 E2.66326
G1 X20.935 Y65.656 E.0164
G1 X81.656 Y4.935 E2.64006
G1 X81.122 Y4.935 E.0164
G1 X20.935 Y65.122 E2.61686
G1 X20.935 Y64.588 E.0164
G1 X80.588 Y4.935 E2.59366
G1 X80.055 Y4.935 E.0164
G1 X20.935 Y64.055 E2.57046
G1 X20.935 Y63.521 E.0164
G1 X79.521 Y4.935 E2.54726
G1 X78.988 Y4.935 E.0164
G1 X20.935 Y62.988 E2.52406
G1 X20.935 Y62.454 E.0164
G1 X78.454 Y4.935 E2.50087
G1 X77.921 Y4.935 E.0164
G1 X20.935 Y61.921 E2.47767
G1 X20.935 Y61.387 E.0164
G1 X77.387 Y4.935 E2.45447
G1 X76.853 Y4.935 E.0164
G1 X20.935 Y60.853 E2.43127
G1 X20.935 Y60.32 E.0164
G1 X34.62 Y46.635 E.59499
G1 X34.086 Y46.635 E.0164
G1 X20.935 Y59.786 E.57179
G1 X20.935 Y59.253 E.0164
G1 X33.553 Y46.635 E.54859
G1 X33.019 Y46.635 E.0164
G1 X20.935 Y58.719 E.52539
G1 X20.935 Y58.186 E.0164
G1 X32.486 Y46.635 E.50219
G1 X31.952 Y46.635 E.0164
G1 X20.935 Y57.652 E.479
G1 X20.935 Y57.118 E.0164
G1 X31.418 Y46.635 E.4558
G1 X30.885 Y46.635 E.0164
G1 X20.935 Y56.585 E.4326
G1 X20.935 Y56.051 E.0164
G1 X30.351 Y46.635 E.4094
G1 X29.818 Y46.635 E.0164
G1 X20.935 Y55.518 E.3862
G1 X20.935 Y54.984 E.0164
G1 X29.565 Y46.355 E.3752
G1 X29.565 Y45.821 E.0164
G1 X20.935 Y54.451 E.3752
G1 X20.935 Y53.917 E.0164
G1 X29.565 Y45.288 E.3752
G1 X29.565 Y44.754 E.0164
G1 X20.935 Y53.383 E.3752
G1 X20.935 Y52.85 E.0164
G1 X29.565 Y44.221 E.3752
G1 X29.565 Y43.687 E.0164
G1 X20.935 Y52.316 E.3752
G1 X20.935 Y51.783 E.0164
G1 X29.565 Y43.153 E.3752
G1 X29.565 Y42.62 E.0164
G1 X20.935 Y51.249 E.3752
G1 X20.935 Y50.716 E.0164
G1 X29.565 Y42.086 E.3752
G1 X29.565 Y41.553 E.0164
G1 X20.935 Y50.182 E.3752
G1 X20.935 Y49.648 E.0164
M73 P38 R20
G1 X29.565 Y41.019 E.3752
G1 X29.565 Y40.486 E.0164
G1 X20.935 Y49.115 E.3752
G1 X20.935 Y48.581 E.0164
G1 X29.815 Y39.702 E.38607
G1 X29.815 Y39.168 E.0164
G1 X20.935 Y48.048 E.38607
G1 X20.935 Y47.514 E.0164
G1 X29.815 Y38.635 E.38607
G1 X29.815 Y38.101 E.0164
G1 X20.935 Y46.981 E.38607
G1 X20.935 Y46.447 E.0164
G1 X29.815 Y37.568 E.38607
G1 X29.815 Y37.034 E.0164
G1 X20.935 Y45.913 E.38607
G1 X20.935 Y45.38 E.0164
G1 X29.815 Y36.501 E.38607
G1 X29.815 Y35.967 E.0164
G1 X20.935 Y44.846 E.38607
G1 X20.935 Y44.313 E.0164
G1 X29.815 Y35.433 E.38607
G1 X29.815 Y34.9 E.0164
G1 X20.935 Y43.779 E.38607
G1 X20.935 Y43.246 E.0164
G1 X29.815 Y34.366 E.38607
G1 X29.815 Y33.833 E.0164
G1 X20.935 Y42.712 E.38607
G1 X20.935 Y42.179 E.0164
G1 X29.815 Y33.299 E.38607
G1 X29.815 Y32.766 E.0164
G1 X20.935 Y41.645 E.38607
G1 X20.935 Y41.111 E.0164
G1 X29.815 Y32.232 E.38607
G1 X29.815 Y31.698 E.0164
G1 X20.935 Y40.578 E.38607
G1 X20.935 Y40.044 E.0164
G1 X29.815 Y31.165 E.38607
G1 X29.815 Y30.631 E.0164
G1 X20.935 Y39.511 E.38607
G1 X20.935 Y38.977 E.0164
G1 X29.815 Y30.098 E.38607
G1 X29.815 Y29.564 E.0164
G1 X20.935 Y38.444 E.38607
G1 X20.935 Y37.91 E.0164
G1 X29.71 Y29.135 E.38151
G1 X29.176 Y29.135 E.0164
G1 X20.935 Y37.376 E.35831
G1 X20.935 Y36.843 E.0164
G1 X28.643 Y29.135 E.33512
G1 X28.109 Y29.135 E.0164
G1 X20.935 Y36.309 E.31192
G1 X20.935 Y35.776 E.0164
G1 X27.765 Y28.946 E.29693
G1 X27.765 Y28.413 E.0164
G1 X20.935 Y35.242 E.29693
G1 X20.935 Y34.709 E.0164
G1 X27.765 Y27.879 E.29693
G1 X27.765 Y27.346 E.0164
G1 X20.935 Y34.175 E.29693
G1 X20.935 Y33.641 E.0164
G1 X27.765 Y26.812 E.29693
G1 X27.765 Y26.279 E.0164
G1 X20.935 Y33.108 E.29693
G1 X20.935 Y32.574 E.0164
G1 X27.765 Y25.745 E.29693
G1 X27.765 Y25.211 E.0164
G1 X20.935 Y32.041 E.29693
G1 X20.935 Y31.507 E.0164
G1 X27.765 Y24.678 E.29693
G1 X27.765 Y24.144 E.0164
G1 X20.935 Y30.974 E.29693
G1 X20.935 Y30.44 E.0164
G1 X27.765 Y23.611 E.29693
G1 X27.765 Y23.077 E.0164
G1 X20.935 Y29.906 E.29693
G1 X20.935 Y29.373 E.0164
G1 X27.765 Y22.544 E.29693
G1 X27.765 Y22.065 E.01472
G1 X28.244 Y22.065 E.01472
G1 X45.373 Y4.935 E.74477
G1 X45.906 Y4.935 E.0164
G1 X28.777 Y22.065 E.74477
G1 X29.311 Y22.065 E.0164
G1 X46.44 Y4.935 E.74477
G1 X46.974 Y4.935 E.0164
G1 X30.144 Y21.765 E.73173
G1 X30.678 Y21.765 E.0164
G1 X47.507 Y4.935 E.73173
G1 X48.041 Y4.935 E.0164
G1 X31.211 Y21.765 E.73172
G1 X31.745 Y21.765 E.0164
G1 X48.574 Y4.935 E.73172
G1 X49.108 Y4.935 E.0164
G1 X32.279 Y21.765 E.73172
G1 X32.812 Y21.765 E.0164
G1 X49.641 Y4.935 E.73172
G1 X50.175 Y4.935 E.0164
G1 X33.346 Y21.765 E.73172
G1 X33.879 Y21.765 E.0164
G1 X50.709 Y4.935 E.73172
G1 X51.242 Y4.935 E.0164
G1 X34.413 Y21.765 E.73172
G1 X34.946 Y21.765 E.0164
G1 X51.776 Y4.935 E.73172
G1 X52.309 Y4.935 E.0164
G1 X35.185 Y22.059 E.74453
G1 X35.713 Y22.065 E.01624
G1 X52.843 Y4.935 E.74477
G1 X53.376 Y4.935 E.0164
G1 X36.247 Y22.065 E.74477
G1 X36.781 Y22.065 E.0164
G1 X53.91 Y4.935 E.74477
G1 X54.444 Y4.935 E.0164
G1 X37.235 Y22.144 E.7482
G1 X37.235 Y22.677 E.0164
G1 X54.977 Y4.935 E.7714
G1 X55.511 Y4.935 E.0164
G1 X37.235 Y23.211 E.7946
G1 X37.235 Y23.744 E.0164
G1 X56.044 Y4.935 E.8178
G1 X56.578 Y4.935 E.0164
G1 X37.235 Y24.278 E.84099
G1 X37.235 Y24.811 E.0164
G1 X57.111 Y4.935 E.86419
G1 X57.645 Y4.935 E.0164
G1 X37.235 Y25.345 E.88739
G1 X37.235 Y25.879 E.0164
G1 X58.179 Y4.935 E.91059
G1 X58.712 Y4.935 E.0164
G1 X37.235 Y26.412 E.93379
G1 X37.235 Y26.946 E.0164
G1 X59.246 Y4.935 E.95699
G1 X59.779 Y4.935 E.0164
G1 X37.235 Y27.479 E.98019
G1 X37.235 Y28.013 E.0164
G1 X60.313 Y4.935 E1.00339
G1 X60.846 Y4.935 E.0164
G1 X37.066 Y28.716 E1.03396
; WIPE_START
G1 X38.48 Y27.302 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.749 Y28.966 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F15000
G1 X35.185 Y29.529 E.0245
G1 X35.185 Y30.063 E.0164
G1 X36.113 Y29.135 E.04033
G1 X36.646 Y29.135 E.0164
G1 X35.016 Y30.766 E.0709
; WIPE_START
G1 X36.43 Y29.352 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.799 Y29.185 Z.8 F30000
G1 X20.766 Y29.009 Z.8
G1 Z.4
G1 E.8 F1800
G1 F15000
G1 X44.839 Y4.935 E1.0467
G1 X44.306 Y4.935 E.0164
G1 X20.935 Y28.306 E1.01612
G1 X20.935 Y27.772 E.0164
G1 X43.772 Y4.935 E.99293
G1 X43.239 Y4.935 E.0164
G1 X20.935 Y27.239 E.96973
G1 X20.935 Y26.705 E.0164
G1 X42.705 Y4.935 E.94653
G1 X42.171 Y4.935 E.0164
G1 X20.935 Y26.171 E.92333
G1 X20.935 Y25.638 E.0164
G1 X41.638 Y4.935 E.90013
G1 X41.104 Y4.935 E.0164
G1 X20.935 Y25.104 E.87693
G1 X20.935 Y24.571 E.0164
G1 X40.571 Y4.935 E.85373
G1 X40.037 Y4.935 E.0164
G1 X20.935 Y24.037 E.83053
G1 X20.935 Y23.504 E.0164
G1 X39.504 Y4.935 E.80733
G1 X38.97 Y4.935 E.0164
G1 X20.935 Y22.97 E.78413
G1 X20.935 Y22.436 E.0164
G1 X38.436 Y4.935 E.76093
G1 X37.903 Y4.935 E.0164
G1 X20.935 Y21.903 E.73774
G1 X20.935 Y21.369 E.0164
G1 X37.369 Y4.935 E.71454
G1 X36.836 Y4.935 E.0164
G1 X20.935 Y20.836 E.69134
G1 X20.935 Y20.302 E.0164
G1 X36.302 Y4.935 E.66814
G1 X35.769 Y4.935 E.0164
G1 X20.935 Y19.769 E.64494
G1 X20.935 Y19.235 E.0164
G1 X35.235 Y4.935 E.62174
G1 X34.701 Y4.935 E.0164
G1 X20.935 Y18.702 E.59854
G1 X20.935 Y18.168 E.0164
G1 X34.168 Y4.935 E.57534
G1 X33.634 Y4.935 E.0164
G1 X20.935 Y17.634 E.55214
G1 X20.935 Y17.101 E.0164
G1 X33.101 Y4.935 E.52894
G1 X32.567 Y4.935 E.0164
G1 X20.935 Y16.567 E.50574
G1 X20.935 Y16.034 E.0164
G1 X32.034 Y4.935 E.48255
G1 X31.5 Y4.935 E.0164
G1 X20.935 Y15.5 E.45935
G1 X20.935 Y14.967 E.0164
G1 X30.967 Y4.935 E.43615
G1 X30.433 Y4.935 E.0164
G1 X20.935 Y14.433 E.41295
G1 X20.935 Y13.899 E.0164
G1 X29.899 Y4.935 E.38975
G1 X29.366 Y4.935 E.0164
G1 X20.935 Y13.366 E.36655
G1 X20.935 Y12.832 E.0164
G1 X28.832 Y4.935 E.34335
G1 X28.299 Y4.935 E.0164
G1 X20.935 Y12.299 E.32015
G1 X20.935 Y11.765 E.0164
G1 X27.765 Y4.935 E.29695
G1 X27.232 Y4.935 E.0164
G1 X20.935 Y11.232 E.27375
G1 X20.935 Y10.698 E.0164
G1 X26.698 Y4.935 E.25055
G1 X26.164 Y4.935 E.0164
G1 X20.935 Y10.164 E.22736
G1 X20.935 Y9.631 E.0164
G1 X25.631 Y4.935 E.20416
G1 X25.097 Y4.935 E.0164
G1 X20.935 Y9.097 E.18096
G1 X20.935 Y8.564 E.0164
G1 X24.564 Y4.935 E.15776
M73 P39 R20
G1 X24.03 Y4.935 E.0164
G1 X20.935 Y8.03 E.13456
G1 X20.935 Y7.497 E.0164
G1 X23.497 Y4.935 E.11136
G1 X22.963 Y4.935 E.0164
G1 X20.935 Y6.963 E.08816
G1 X20.935 Y6.429 E.0164
G1 X22.429 Y4.935 E.06496
G1 X21.896 Y4.935 E.0164
G1 X20.935 Y5.896 E.04176
G1 X20.935 Y5.362 E.0164
G1 X21.532 Y4.766 E.02594
G1 X61.55 Y4.766 F30000
G1 F15000
G1 X35.185 Y31.13 E1.1463
G1 X35.185 Y31.664 E.0164
G1 X61.914 Y4.935 E1.16212
G1 X62.447 Y4.935 E.0164
G1 X35.185 Y32.197 E1.18532
G1 X35.185 Y32.731 E.0164
G1 X62.981 Y4.935 E1.20852
G1 X63.514 Y4.935 E.0164
G1 X35.185 Y33.264 E1.23171
G1 X35.185 Y33.798 E.0164
G1 X64.048 Y4.935 E1.25491
G1 X64.581 Y4.935 E.0164
G1 X35.185 Y34.331 E1.27811
G1 X35.185 Y34.865 E.0164
G1 X65.115 Y4.935 E1.30131
G1 X65.648 Y4.935 E.0164
G1 X35.185 Y35.398 E1.32451
G1 X35.185 Y35.932 E.0164
G1 X66.182 Y4.935 E1.34771
G1 X66.716 Y4.935 E.0164
G1 X35.185 Y36.466 E1.37091
G1 X35.185 Y36.999 E.0164
G1 X67.249 Y4.935 E1.39411
G1 X67.783 Y4.935 E.0164
G1 X35.185 Y37.533 E1.41731
G1 X35.185 Y38.066 E.0164
G1 X68.316 Y4.935 E1.44051
G1 X68.85 Y4.935 E.0164
G1 X35.185 Y38.6 E1.4637
G1 X35.185 Y39.133 E.0164
G1 X69.383 Y4.935 E1.4869
G1 X69.917 Y4.935 E.0164
G1 X35.185 Y39.667 E1.5101
G1 X35.185 Y39.765 E.003
G1 X35.435 Y39.765 E.00769
G1 X35.435 Y39.951 E.00572
G1 X70.451 Y4.935 E1.52243
G1 X70.984 Y4.935 E.0164
G1 X35.435 Y40.484 E1.54563
G1 X35.435 Y41.018 E.0164
G1 X71.518 Y4.935 E1.56883
G1 X72.051 Y4.935 E.0164
G1 X35.435 Y41.551 E1.59203
G1 X35.435 Y42.085 E.0164
G1 X72.585 Y4.935 E1.61523
G1 X73.118 Y4.935 E.0164
G1 X35.435 Y42.618 E1.63843
G1 X35.435 Y43.152 E.0164
G1 X73.652 Y4.935 E1.66163
G1 X74.186 Y4.935 E.0164
G1 X35.435 Y43.686 E1.68483
G1 X35.435 Y44.219 E.0164
G1 X74.719 Y4.935 E1.70803
G1 X75.253 Y4.935 E.0164
G1 X35.435 Y44.753 E1.73122
G1 X35.435 Y45.286 E.0164
G1 X75.786 Y4.935 E1.75442
G1 X76.32 Y4.935 E.0164
G1 X35.266 Y45.99 E1.785
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X36.68 Y44.575 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 3/40
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
G17
G3 Z.8 I1.217 J0 P1  F30000
; object ids of layer 3 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer3 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z1 F30000
G1 X160.4 Y8 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z1 F30000
G1 X114.002 Y8.498 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z1 F30000
G1 X93.502 Y73.11 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z1 F30000
G1 X97.11 Y46.302 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.802 E.3747
G1 X90.498 Y28.802 E.068
G1 X90.498 Y22.398 E.21244
G1 X92.548 Y22.398 E.068
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.302 Y22.398 E.068
G1 X99.302 Y28.802 E.21244
G1 X97.252 Y28.802 E.068
G1 X97.252 Y40.098 E.3747
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.41 E.37119
G1 X90.89 Y28.41 E.06299
G1 X90.89 Y22.79 E.17269
G1 X92.94 Y22.79 E.06299
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.91 Y22.79 E.06299
G1 X98.91 Y28.41 E.17269
G1 X96.86 Y28.41 E.06299
G1 X96.86 Y40.49 E.37119
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z1 F30000
G1 X35.102 Y45.91 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.802 E.3747
G1 X28.098 Y28.802 E.068
G1 X28.098 Y22.398 E.21244
G1 X30.148 Y22.398 E.068
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.902 Y22.398 E.068
G1 X36.902 Y28.802 E.21244
G1 X34.852 Y28.802 E.068
G1 X34.852 Y40.098 E.3747
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.41 E.37119
G1 X28.49 Y28.41 E.06299
G1 X28.49 Y22.79 E.17269
G1 X30.54 Y22.79 E.06299
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.51 Y22.79 E.06299
G1 X36.51 Y28.41 E.17269
G1 X34.46 Y28.41 E.06299
G1 X34.46 Y40.49 E.37119
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.011 Y53.504 Z1 F30000
G1 X33.8 Y73.498 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.7 Y73.502 E.00331
G3 X33.491 Y67.907 I.009 J-2.801 E.28441
G3 X34.247 Y67.951 I.204 J3.034 E.02518
G3 X33.975 Y73.489 I-.538 J2.749 E.26517
G1 X33.86 Y73.495 E.00382
G1 X33.778 Y73.103 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.7 Y73.108 E.00241
G3 X33.51 Y68.299 I.01 J-2.409 E.22603
G3 X33.936 Y68.301 I.202 J2.163 E.01312
G3 X34.17 Y73.064 I-.226 J2.398 E.21133
G1 X33.838 Y73.097 E.01026
; WIPE_START
M204 S10000
G1 X33.7 Y73.108 E-.05263
G1 X33.23 Y73.064 E-.17947
G1 X32.778 Y72.927 E-.17953
G1 X32.361 Y72.704 E-.17957
G1 X32.018 Y72.422 E-.1688
; WIPE_END
G1 E-.04 F1800
G1 X39.43 Y74.244 Z1 F30000
G1 X106.798 Y90.798 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.967 Y90.634 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42021
G1 F15000
G1 X37.235 Y27.903 E2.7275
G1 X37.235 Y28.437 E.0164
G1 X99.263 Y90.465 E2.69692
G1 X98.73 Y90.465 E.0164
G1 X37.235 Y28.97 E2.67372
G1 X37.235 Y29.135 E.00507
G1 X36.867 Y29.135 E.01133
G1 X98.196 Y90.465 E2.66655
G1 X97.663 Y90.465 E.0164
G1 X36.333 Y29.135 E2.66654
G1 X35.8 Y29.135 E.0164
G1 X97.129 Y90.465 E2.66654
G1 X96.595 Y90.465 E.0164
G1 X35.266 Y29.135 E2.66654
G1 X35.185 Y29.135 E.00248
G1 X35.185 Y29.588 E.01392
G1 X96.062 Y90.465 E2.64686
G1 X95.528 Y90.465 E.0164
G1 X35.185 Y30.122 E2.62366
G1 X35.185 Y30.655 E.0164
G1 X94.995 Y90.465 E2.60046
G1 X94.461 Y90.465 E.0164
G1 X35.185 Y31.189 E2.57726
G1 X35.185 Y31.722 E.0164
G1 X93.928 Y90.465 E2.55406
G1 X93.394 Y90.465 E.0164
G1 X35.185 Y32.256 E2.53086
G1 X35.185 Y32.79 E.0164
G1 X92.86 Y90.465 E2.50766
G1 X92.327 Y90.465 E.0164
G1 X35.185 Y33.323 E2.48446
G1 X35.185 Y33.857 E.0164
G1 X91.793 Y90.465 E2.46127
G1 X91.26 Y90.465 E.0164
G1 X35.185 Y34.39 E2.43807
G1 X35.185 Y34.924 E.0164
G1 X90.726 Y90.465 E2.41487
G1 X90.193 Y90.465 E.0164
G1 X35.185 Y35.457 E2.39167
G1 X35.185 Y35.991 E.0164
G1 X89.659 Y90.465 E2.36847
G1 X89.126 Y90.465 E.0164
G1 X35.185 Y36.525 E2.34527
G1 X35.185 Y37.058 E.0164
G1 X88.592 Y90.465 E2.32207
G1 X88.058 Y90.465 E.0164
G1 X35.185 Y37.592 E2.29887
G1 X35.185 Y38.125 E.0164
G1 X87.525 Y90.465 E2.27567
G1 X86.991 Y90.465 E.0164
G1 X35.185 Y38.659 E2.25247
G1 X35.185 Y39.192 E.0164
G1 X86.458 Y90.465 E2.22927
G1 X85.924 Y90.465 E.0164
G1 X35.016 Y39.556 E2.21345
; WIPE_START
G1 X36.43 Y40.97 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.622 Y33.34 Z1 F30000
G1 X36.902 Y22.234 Z1
G1 Z.6
G1 E.8 F1800
G1 F15000
G1 X20.935 Y6.267 E.69423
G1 X20.935 Y6.801 E.0164
G1 X36.199 Y22.065 E.66365
G1 X35.665 Y22.065 E.0164
G1 X20.935 Y7.335 E.64045
G1 X20.935 Y7.868 E.0164
G1 X34.832 Y21.765 E.60421
G1 X34.298 Y21.765 E.0164
G1 X20.935 Y8.402 E.58101
G1 X20.935 Y8.935 E.0164
G1 X33.765 Y21.765 E.55781
G1 X33.231 Y21.765 E.0164
G1 X20.935 Y9.469 E.53461
G1 X20.935 Y10.002 E.0164
G1 X32.698 Y21.765 E.51141
G1 X32.164 Y21.765 E.0164
G1 X20.935 Y10.536 E.48821
G1 X20.935 Y11.07 E.0164
G1 X31.63 Y21.765 E.46501
G1 X31.097 Y21.765 E.0164
M73 P40 R20
G1 X20.935 Y11.603 E.44181
G1 X20.935 Y12.137 E.0164
G1 X30.563 Y21.765 E.41862
G1 X30.03 Y21.765 E.0164
G1 X20.935 Y12.67 E.39542
G1 X20.935 Y13.204 E.0164
G1 X29.796 Y22.065 E.38526
G1 X29.263 Y22.065 E.0164
G1 X20.935 Y13.737 E.36206
G1 X20.935 Y14.271 E.0164
G1 X28.729 Y22.065 E.33886
G1 X28.195 Y22.065 E.0164
G1 X20.935 Y14.805 E.31566
G1 X20.935 Y15.338 E.0164
G1 X27.765 Y22.167 E.29693
G1 X27.765 Y22.701 E.0164
G1 X20.935 Y15.872 E.29693
G1 X20.935 Y16.405 E.0164
G1 X27.765 Y23.235 E.29693
G1 X27.765 Y23.768 E.0164
G1 X20.935 Y16.939 E.29693
G1 X20.935 Y17.472 E.0164
G1 X27.765 Y24.302 E.29693
G1 X27.765 Y24.835 E.0164
G1 X20.935 Y18.006 E.29693
G1 X20.935 Y18.54 E.0164
G1 X27.765 Y25.369 E.29693
G1 X27.765 Y25.902 E.0164
G1 X20.935 Y19.073 E.29693
G1 X20.935 Y19.607 E.0164
G1 X27.765 Y26.436 E.29693
G1 X27.765 Y26.97 E.0164
G1 X20.935 Y20.14 E.29693
G1 X20.935 Y20.674 E.0164
G1 X27.765 Y27.503 E.29693
G1 X27.765 Y28.037 E.0164
G1 X20.935 Y21.207 E.29693
G1 X20.935 Y21.741 E.0164
G1 X27.934 Y28.74 E.30431
G1 X28.16 Y28.966 F30000
G1 F15000
G1 X29.815 Y30.62 E.07194
G1 X29.815 Y30.087 E.0164
G1 X28.863 Y29.135 E.04137
G1 X29.397 Y29.135 E.0164
G1 X29.984 Y29.723 E.02554
G1 X29.984 Y31.324 F30000
G1 F15000
M73 P40 R19
G1 X20.935 Y22.275 E.39344
G1 X20.935 Y22.808 E.0164
G1 X29.815 Y31.687 E.38607
G1 X29.815 Y32.221 E.0164
G1 X20.935 Y23.342 E.38607
G1 X20.935 Y23.875 E.0164
G1 X29.815 Y32.755 E.38607
G1 X29.815 Y33.288 E.0164
G1 X20.935 Y24.409 E.38607
G1 X20.935 Y24.942 E.0164
G1 X29.815 Y33.822 E.38607
G1 X29.815 Y34.355 E.0164
G1 X20.935 Y25.476 E.38607
G1 X20.935 Y26.009 E.0164
G1 X29.815 Y34.889 E.38607
G1 X29.815 Y35.422 E.0164
G1 X20.935 Y26.543 E.38607
G1 X20.935 Y27.077 E.0164
G1 X29.815 Y35.956 E.38607
G1 X29.815 Y36.49 E.0164
G1 X20.935 Y27.61 E.38607
G1 X20.935 Y28.144 E.0164
G1 X29.815 Y37.023 E.38607
G1 X29.815 Y37.557 E.0164
G1 X20.935 Y28.677 E.38607
G1 X20.935 Y29.211 E.0164
G1 X29.815 Y38.09 E.38607
G1 X29.815 Y38.624 E.0164
G1 X20.935 Y29.744 E.38607
G1 X20.935 Y30.278 E.0164
G1 X29.815 Y39.157 E.38607
G1 X29.815 Y39.691 E.0164
G1 X20.935 Y30.812 E.38607
G1 X20.935 Y31.345 E.0164
G1 X29.565 Y39.975 E.3752
G1 X29.565 Y40.508 E.0164
G1 X20.935 Y31.879 E.3752
G1 X20.935 Y32.412 E.0164
G1 X29.565 Y41.042 E.3752
G1 X29.565 Y41.575 E.0164
G1 X20.935 Y32.946 E.3752
G1 X20.935 Y33.479 E.0164
G1 X29.565 Y42.109 E.3752
G1 X29.565 Y42.642 E.0164
G1 X20.935 Y34.013 E.3752
G1 X20.935 Y34.547 E.0164
G1 X29.565 Y43.176 E.3752
G1 X29.565 Y43.709 E.0164
G1 X20.935 Y35.08 E.3752
G1 X20.935 Y35.614 E.0164
G1 X29.565 Y44.243 E.3752
G1 X29.565 Y44.777 E.0164
G1 X20.935 Y36.147 E.3752
G1 X20.935 Y36.681 E.0164
G1 X29.565 Y45.31 E.3752
G1 X29.565 Y45.844 E.0164
G1 X20.935 Y37.214 E.3752
G1 X20.935 Y37.748 E.0164
G1 X73.652 Y90.465 E2.29207
G1 X74.186 Y90.465 E.0164
G1 X30.356 Y46.635 E1.90566
G1 X30.89 Y46.635 E.0164
G1 X74.719 Y90.465 E1.90566
G1 X75.253 Y90.465 E.0164
G1 X31.423 Y46.635 E1.90566
G1 X31.957 Y46.635 E.0164
G1 X75.786 Y90.465 E1.90566
G1 X76.32 Y90.465 E.0164
G1 X32.49 Y46.635 E1.90566
G1 X33.024 Y46.635 E.0164
G1 X76.853 Y90.465 E1.90566
G1 X77.387 Y90.465 E.0164
G1 X33.558 Y46.635 E1.90566
G1 X34.091 Y46.635 E.0164
G1 X77.921 Y90.465 E1.90566
G1 X78.454 Y90.465 E.0164
G1 X34.625 Y46.635 E1.90566
G1 X35.158 Y46.635 E.0164
G1 X78.988 Y90.465 E1.90566
G1 X79.521 Y90.465 E.0164
G1 X35.435 Y46.379 E1.91682
G1 X35.435 Y45.845 E.0164
G1 X80.055 Y90.465 E1.94002
G1 X80.588 Y90.465 E.0164
G1 X35.435 Y45.312 E1.96321
G1 X35.435 Y44.778 E.0164
G1 X81.122 Y90.465 E1.98641
G1 X81.656 Y90.465 E.0164
G1 X35.435 Y44.244 E2.00961
G1 X35.435 Y43.711 E.0164
G1 X82.189 Y90.465 E2.03281
G1 X82.723 Y90.465 E.0164
G1 X35.435 Y43.177 E2.05601
G1 X35.435 Y42.644 E.0164
G1 X83.256 Y90.465 E2.07921
G1 X83.79 Y90.465 E.0164
G1 X35.435 Y42.11 E2.10241
G1 X35.435 Y41.577 E.0164
G1 X84.323 Y90.465 E2.12561
G1 X84.857 Y90.465 E.0164
G1 X35.435 Y41.043 E2.14881
G1 X35.435 Y40.509 E.0164
G1 X85.56 Y90.634 E2.17938
G1 X73.288 Y90.634 F30000
G1 F15000
G1 X20.935 Y38.282 E2.27625
G1 X20.935 Y38.815 E.0164
G1 X72.585 Y90.465 E2.24568
G1 X72.051 Y90.465 E.0164
G1 X20.935 Y39.349 E2.22248
G1 X20.935 Y39.882 E.0164
G1 X71.518 Y90.465 E2.19928
G1 X70.984 Y90.465 E.0164
G1 X20.935 Y40.416 E2.17608
G1 X20.935 Y40.949 E.0164
G1 X70.451 Y90.465 E2.15288
G1 X69.917 Y90.465 E.0164
G1 X20.935 Y41.483 E2.12968
G1 X20.935 Y42.017 E.0164
G1 X69.383 Y90.465 E2.10648
G1 X68.85 Y90.465 E.0164
G1 X20.935 Y42.55 E2.08328
G1 X20.935 Y43.084 E.0164
G1 X68.316 Y90.465 E2.06008
G1 X67.783 Y90.465 E.0164
G1 X20.935 Y43.617 E2.03688
G1 X20.935 Y44.151 E.0164
G1 X67.249 Y90.465 E2.01368
G1 X66.716 Y90.465 E.0164
G1 X20.935 Y44.684 E1.99049
G1 X20.935 Y45.218 E.0164
G1 X66.182 Y90.465 E1.96729
G1 X65.648 Y90.465 E.0164
G1 X20.935 Y45.752 E1.94409
G1 X20.935 Y46.285 E.0164
G1 X65.115 Y90.465 E1.92089
G1 X64.581 Y90.465 E.0164
G1 X20.935 Y46.819 E1.89769
G1 X20.935 Y47.352 E.0164
G1 X64.048 Y90.465 E1.87449
G1 X63.514 Y90.465 E.0164
G1 X20.935 Y47.886 E1.85129
G1 X20.935 Y48.419 E.0164
G1 X62.981 Y90.465 E1.82809
G1 X62.447 Y90.465 E.0164
G1 X20.935 Y48.953 E1.80489
G1 X20.935 Y49.487 E.0164
G1 X61.914 Y90.465 E1.78169
G1 X61.38 Y90.465 E.0164
G1 X20.935 Y50.02 E1.75849
G1 X20.935 Y50.554 E.0164
G1 X60.846 Y90.465 E1.7353
G1 X60.313 Y90.465 E.0164
G1 X20.935 Y51.087 E1.7121
G1 X20.935 Y51.621 E.0164
G1 X59.779 Y90.465 E1.6889
G1 X59.246 Y90.465 E.0164
G1 X20.935 Y52.154 E1.6657
G1 X20.935 Y52.688 E.0164
G1 X58.712 Y90.465 E1.6425
G1 X58.179 Y90.465 E.0164
G1 X20.935 Y53.221 E1.6193
G1 X20.935 Y53.755 E.0164
G1 X35.056 Y67.876 E.61397
G2 X34.263 Y67.617 I-1.211 J2.359 E.02576
G1 X20.935 Y54.289 E.57949
G1 X20.935 Y54.822 E.0164
G1 X33.689 Y67.576 E.5545
M73 P41 R19
G2 X33.19 Y67.61 I-.121 J1.852 E.01542
G1 X20.935 Y55.356 E.53282
G1 X20.935 Y55.889 E.0164
G1 X32.756 Y67.71 E.51397
G2 X32.374 Y67.862 I.579 J2.022 E.01266
G1 X20.935 Y56.423 E.49735
G1 X20.935 Y56.956 E.0164
G1 X32.028 Y68.05 E.48232
G2 X31.716 Y68.271 I.967 J1.693 E.01178
G1 X20.935 Y57.49 E.46875
G1 X20.935 Y58.024 E.0164
G1 X31.44 Y68.529 E.45674
G2 X31.196 Y68.818 I1.341 J1.382 E.01166
G1 X20.935 Y58.557 E.44612
G1 X20.935 Y59.091 E.0164
G1 X30.983 Y69.139 E.43688
G2 X30.805 Y69.494 I1.717 J1.085 E.01224
G1 X20.935 Y59.624 E.42913
G1 X20.935 Y60.158 E.0164
G1 X30.672 Y69.895 E.42335
G2 X30.586 Y70.342 I2.239 J.663 E.01403
G1 X20.935 Y60.691 E.41961
G1 X20.935 Y61.225 E.0164
G1 X30.571 Y70.861 E.41897
G2 X30.669 Y71.492 I3.152 J-.164 E.01967
G1 X20.935 Y61.759 E.42321
G1 X20.935 Y62.292 E.0164
G1 X49.108 Y90.465 E1.22492
G1 X49.641 Y90.465 E.0164
G1 X32.908 Y73.731 E.72756
G2 X33.539 Y73.829 I.795 J-3.055 E.01967
G1 X50.175 Y90.465 E.72332
G1 X50.709 Y90.465 E.0164
G1 X34.058 Y73.814 E.72396
G2 X34.505 Y73.728 I-.215 J-2.321 E.01403
G1 X51.242 Y90.465 E.72771
G1 X51.776 Y90.465 E.0164
G1 X34.906 Y73.595 E.73348
G2 X35.261 Y73.417 I-.729 J-1.895 E.01224
G1 X52.309 Y90.465 E.74124
G1 X52.843 Y90.465 E.0164
G1 X35.582 Y73.204 E.75047
G2 X35.871 Y72.96 I-1.093 J-1.586 E.01166
G1 X53.376 Y90.465 E.7611
G1 X53.91 Y90.465 E.0164
G1 X36.129 Y72.684 E.7731
G2 X36.35 Y72.372 I-1.475 J-1.281 E.01179
G1 X54.444 Y90.465 E.78667
G1 X54.977 Y90.465 E.0164
G1 X36.538 Y72.026 E.8017
G2 X36.69 Y71.644 I-1.874 J-.963 E.01266
G1 X55.511 Y90.465 E.81832
G1 X56.044 Y90.465 E.0164
G1 X36.791 Y71.212 E.83711
G2 X36.835 Y70.722 I-2.462 J-.47 E.01513
G1 X56.578 Y90.465 E.85838
G1 X57.111 Y90.465 E.0164
G1 X36.783 Y70.137 E.88384
G2 X36.524 Y69.344 I-2.618 J.418 E.02576
G1 X57.815 Y90.634 E.9257
G1 X48.744 Y90.634 F30000
G1 F15000
G1 X20.935 Y62.826 E1.20909
G1 X20.935 Y63.359 E.0164
G1 X48.041 Y90.465 E1.17852
G1 X47.507 Y90.465 E.0164
G1 X20.935 Y63.893 E1.15532
G1 X20.935 Y64.426 E.0164
G1 X46.974 Y90.465 E1.13212
G1 X46.44 Y90.465 E.0164
G1 X20.935 Y64.96 E1.10892
G1 X20.935 Y65.494 E.0164
G1 X45.906 Y90.465 E1.08572
G1 X45.373 Y90.465 E.0164
G1 X20.935 Y66.027 E1.06252
G1 X20.935 Y66.561 E.0164
G1 X44.839 Y90.465 E1.03932
G1 X44.306 Y90.465 E.0164
G1 X20.935 Y67.094 E1.01612
G1 X20.935 Y67.628 E.0164
G1 X43.772 Y90.465 E.99293
G1 X43.239 Y90.465 E.0164
G1 X20.935 Y68.161 E.96973
G1 X20.935 Y68.695 E.0164
G1 X42.705 Y90.465 E.94653
G1 X42.171 Y90.465 E.0164
G1 X20.935 Y69.229 E.92333
G1 X20.935 Y69.762 E.0164
G1 X41.638 Y90.465 E.90013
G1 X41.104 Y90.465 E.0164
G1 X20.935 Y70.296 E.87693
G1 X20.935 Y70.829 E.0164
G1 X40.571 Y90.465 E.85373
G1 X40.037 Y90.465 E.0164
G1 X20.935 Y71.363 E.83053
G1 X20.935 Y71.896 E.0164
G1 X39.504 Y90.465 E.80733
G1 X38.97 Y90.465 E.0164
G1 X20.935 Y72.43 E.78413
G1 X20.935 Y72.964 E.0164
G1 X38.436 Y90.465 E.76093
G1 X37.903 Y90.465 E.0164
G1 X20.935 Y73.497 E.73774
G1 X20.935 Y74.031 E.0164
G1 X37.369 Y90.465 E.71454
G1 X36.836 Y90.465 E.0164
G1 X20.935 Y74.564 E.69134
G1 X20.935 Y75.098 E.0164
G1 X36.302 Y90.465 E.66814
G1 X35.769 Y90.465 E.0164
G1 X20.935 Y75.631 E.64494
G1 X20.935 Y76.165 E.0164
G1 X35.235 Y90.465 E.62174
G1 X34.701 Y90.465 E.0164
G1 X20.935 Y76.699 E.59854
G1 X20.935 Y77.232 E.0164
G1 X34.168 Y90.465 E.57534
G1 X33.634 Y90.465 E.0164
G1 X20.935 Y77.766 E.55214
G1 X20.935 Y78.299 E.0164
G1 X33.101 Y90.465 E.52894
G1 X32.567 Y90.465 E.0164
G1 X20.935 Y78.833 E.50574
G1 X20.935 Y79.366 E.0164
G1 X32.034 Y90.465 E.48255
G1 X31.5 Y90.465 E.0164
G1 X20.935 Y79.9 E.45935
G1 X20.935 Y80.433 E.0164
G1 X30.967 Y90.465 E.43615
G1 X30.433 Y90.465 E.0164
G1 X20.935 Y80.967 E.41295
G1 X20.935 Y81.501 E.0164
G1 X29.899 Y90.465 E.38975
G1 X29.366 Y90.465 E.0164
G1 X20.935 Y82.034 E.36655
G1 X20.935 Y82.568 E.0164
G1 X28.832 Y90.465 E.34335
G1 X28.299 Y90.465 E.0164
G1 X20.935 Y83.101 E.32015
G1 X20.935 Y83.635 E.0164
G1 X27.765 Y90.465 E.29695
G1 X27.232 Y90.465 E.0164
G1 X20.935 Y84.168 E.27375
G1 X20.935 Y84.702 E.0164
G1 X26.698 Y90.465 E.25055
G1 X26.164 Y90.465 E.0164
G1 X20.935 Y85.236 E.22736
G1 X20.935 Y85.769 E.0164
G1 X25.631 Y90.465 E.20416
G1 X25.097 Y90.465 E.0164
G1 X20.935 Y86.303 E.18096
G1 X20.935 Y86.836 E.0164
G1 X24.564 Y90.465 E.15776
G1 X24.03 Y90.465 E.0164
G1 X20.935 Y87.37 E.13456
G1 X20.935 Y87.903 E.0164
G1 X23.497 Y90.465 E.11136
G1 X22.963 Y90.465 E.0164
G1 X20.935 Y88.437 E.08816
G1 X20.935 Y88.971 E.0164
G1 X22.429 Y90.465 E.06496
G1 X21.896 Y90.465 E.0164
G1 X20.935 Y89.504 E.04176
G1 X20.935 Y90.038 E.0164
G1 X21.532 Y90.634 E.02594
G1 X106.634 Y80.762 F30000
G1 F15000
G1 X93.835 Y67.963 E.55649
G1 X93.835 Y68.496 E.0164
G1 X106.465 Y81.125 E.54911
G1 X106.465 Y81.659 E.0164
G1 X93.835 Y69.03 E.54911
G1 X93.835 Y69.563 E.0164
G1 X106.465 Y82.193 E.54911
G1 X106.465 Y82.726 E.0164
G1 X93.835 Y70.097 E.54911
G1 X93.835 Y70.63 E.0164
G1 X106.465 Y83.26 E.54911
G1 X106.465 Y83.793 E.0164
G1 X93.835 Y71.164 E.54911
G1 X93.835 Y71.697 E.0164
G1 X106.465 Y84.327 E.54911
G1 X106.465 Y84.86 E.0164
G1 X93.835 Y72.231 E.54911
G1 X93.835 Y72.765 E.0164
G1 X106.465 Y85.394 E.54911
G1 X106.465 Y85.928 E.0164
G1 X93.835 Y73.298 E.54911
G1 X93.835 Y73.832 E.0164
G1 X106.465 Y86.461 E.54911
M73 P42 R19
G1 X106.465 Y86.995 E.0164
G1 X93.305 Y73.835 E.57216
G1 X92.772 Y73.835 E.0164
G1 X106.465 Y87.528 E.59536
G1 X106.465 Y88.062 E.0164
G1 X92.238 Y73.835 E.61856
G1 X91.705 Y73.835 E.0164
G1 X106.465 Y88.595 E.64175
G1 X106.465 Y89.129 E.0164
G1 X91.171 Y73.835 E.66495
G1 X90.637 Y73.835 E.0164
G1 X106.465 Y89.663 E.68815
G1 X106.465 Y90.196 E.0164
G1 X90.104 Y73.835 E.71135
G1 X89.57 Y73.835 E.0164
G1 X106.2 Y90.465 E.72303
G1 X105.666 Y90.465 E.0164
G1 X89.037 Y73.835 E.72303
G1 X88.503 Y73.835 E.0164
G1 X105.133 Y90.465 E.72303
G1 X104.599 Y90.465 E.0164
G1 X87.97 Y73.835 E.72303
G1 X87.436 Y73.835 E.0164
G1 X104.065 Y90.465 E.72303
G1 X103.532 Y90.465 E.0164
G1 X86.903 Y73.835 E.72303
G1 X86.369 Y73.835 E.0164
G1 X102.998 Y90.465 E.72303
G1 X102.465 Y90.465 E.0164
G1 X85.835 Y73.835 E.72303
G1 X85.302 Y73.835 E.0164
G1 X101.931 Y90.465 E.72303
G1 X101.398 Y90.465 E.0164
G1 X84.768 Y73.835 E.72303
G1 X84.235 Y73.835 E.0164
G1 X100.864 Y90.465 E.72303
G1 X100.33 Y90.465 E.0164
G1 X37.235 Y27.37 E2.74332
G1 X37.235 Y26.836 E.0164
G1 X83.565 Y73.165 E2.01436
G1 X83.565 Y72.632 E.0164
G1 X37.235 Y26.302 E2.01436
G1 X37.235 Y25.769 E.0164
G1 X83.565 Y72.098 E2.01436
G1 X83.565 Y71.565 E.0164
G1 X37.235 Y25.235 E2.01436
G1 X37.235 Y24.702 E.0164
G1 X83.565 Y71.031 E2.01436
G1 X83.565 Y70.498 E.0164
G1 X37.235 Y24.168 E2.01436
G1 X37.235 Y23.635 E.0164
G1 X83.565 Y69.964 E2.01436
G1 X83.565 Y69.43 E.0164
G1 X37.235 Y23.101 E2.01436
G1 X37.235 Y22.567 E.0164
G1 X83.565 Y68.897 E2.01436
G1 X83.565 Y68.363 E.0164
G1 X20.935 Y5.734 E2.72307
G1 X20.935 Y5.2 E.0164
G1 X83.565 Y67.83 E2.72307
G1 X83.565 Y67.565 E.00815
G1 X83.833 Y67.565 E.00826
G1 X21.204 Y4.935 E2.72307
G1 X21.737 Y4.935 E.0164
G1 X84.367 Y67.565 E2.72307
G1 X84.9 Y67.565 E.0164
G1 X22.271 Y4.935 E2.72307
G1 X22.805 Y4.935 E.0164
G1 X85.434 Y67.565 E2.72307
G1 X85.968 Y67.565 E.0164
G1 X23.338 Y4.935 E2.72307
G1 X23.872 Y4.935 E.0164
G1 X86.501 Y67.565 E2.72307
G1 X87.035 Y67.565 E.0164
G1 X24.405 Y4.935 E2.72307
G1 X24.939 Y4.935 E.0164
G1 X87.568 Y67.565 E2.72307
G1 X88.102 Y67.565 E.0164
G1 X25.472 Y4.935 E2.72307
G1 X26.006 Y4.935 E.0164
G1 X88.635 Y67.565 E2.72307
G1 X89.169 Y67.565 E.0164
G1 X26.54 Y4.935 E2.72307
G1 X27.073 Y4.935 E.0164
G1 X89.703 Y67.565 E2.72307
G1 X90.236 Y67.565 E.0164
G1 X27.607 Y4.935 E2.72307
G1 X28.14 Y4.935 E.0164
G1 X90.77 Y67.565 E2.72307
G1 X91.303 Y67.565 E.0164
G1 X28.674 Y4.935 E2.72307
G1 X29.207 Y4.935 E.0164
G1 X91.837 Y67.565 E2.72307
G1 X92.37 Y67.565 E.0164
G1 X29.741 Y4.935 E2.72307
G1 X30.275 Y4.935 E.0164
G1 X92.904 Y67.565 E2.72307
G1 X93.438 Y67.565 E.0164
G1 X30.808 Y4.935 E2.72307
G1 X31.342 Y4.935 E.0164
G1 X106.465 Y80.058 E3.26628
G1 X106.465 Y79.525 E.0164
G1 X31.875 Y4.935 E3.24308
G1 X32.409 Y4.935 E.0164
G1 X106.465 Y78.991 E3.21988
G1 X106.465 Y78.458 E.0164
G1 X32.942 Y4.935 E3.19668
G1 X33.476 Y4.935 E.0164
G1 X106.465 Y77.924 E3.17348
G1 X106.465 Y77.39 E.0164
G1 X34.01 Y4.935 E3.15028
G1 X34.543 Y4.935 E.0164
G1 X106.465 Y76.857 E3.12708
G1 X106.465 Y76.323 E.0164
G1 X35.077 Y4.935 E3.10388
G1 X35.61 Y4.935 E.0164
G1 X106.465 Y75.79 E3.08069
G1 X106.465 Y75.256 E.0164
G1 X36.144 Y4.935 E3.05749
G1 X36.677 Y4.935 E.0164
G1 X106.465 Y74.723 E3.03429
G1 X106.465 Y74.189 E.0164
G1 X37.211 Y4.935 E3.01109
G1 X37.745 Y4.935 E.0164
G1 X106.465 Y73.655 E2.98789
G1 X106.465 Y73.122 E.0164
G1 X38.278 Y4.935 E2.96469
G1 X38.812 Y4.935 E.0164
G1 X106.465 Y72.588 E2.94149
G1 X106.465 Y72.055 E.0164
G1 X39.345 Y4.935 E2.91829
G1 X39.879 Y4.935 E.0164
G1 X106.465 Y71.521 E2.89509
G1 X106.465 Y70.988 E.0164
G1 X40.412 Y4.935 E2.87189
G1 X40.946 Y4.935 E.0164
G1 X106.465 Y70.454 E2.84869
G1 X106.465 Y69.92 E.0164
G1 X41.48 Y4.935 E2.8255
G1 X42.013 Y4.935 E.0164
G1 X106.465 Y69.387 E2.8023
G1 X106.465 Y68.853 E.0164
G1 X42.547 Y4.935 E2.7791
G1 X43.08 Y4.935 E.0164
G1 X106.465 Y68.32 E2.7559
G1 X106.465 Y67.786 E.0164
G1 X43.614 Y4.935 E2.7327
G1 X44.147 Y4.935 E.0164
G1 X106.465 Y67.253 E2.7095
G1 X106.465 Y66.719 E.0164
G1 X44.681 Y4.935 E2.6863
G1 X45.215 Y4.935 E.0164
G1 X106.465 Y66.186 E2.6631
G1 X106.465 Y65.652 E.0164
G1 X45.748 Y4.935 E2.6399
G1 X46.282 Y4.935 E.0164
G1 X106.465 Y65.118 E2.6167
G1 X106.465 Y64.585 E.0164
G1 X46.815 Y4.935 E2.5935
G1 X47.349 Y4.935 E.0164
G1 X106.465 Y64.051 E2.57031
G1 X106.465 Y63.518 E.0164
G1 X47.882 Y4.935 E2.54711
G1 X48.416 Y4.935 E.0164
G1 X106.465 Y62.984 E2.52391
G1 X106.465 Y62.451 E.0164
G1 X48.949 Y4.935 E2.50071
G1 X49.483 Y4.935 E.0164
G1 X106.465 Y61.917 E2.47751
G1 X106.465 Y61.383 E.0164
G1 X50.017 Y4.935 E2.45431
G1 X50.55 Y4.935 E.0164
G1 X106.465 Y60.85 E2.43111
G1 X106.465 Y60.316 E.0164
G1 X92.784 Y46.635 E.59483
G1 X93.317 Y46.635 E.0164
G1 X106.465 Y59.783 E.57164
G1 X106.465 Y59.249 E.0164
G1 X93.851 Y46.635 E.54844
G1 X94.384 Y46.635 E.0164
G1 X106.465 Y58.716 E.52524
G1 X106.465 Y58.182 E.0164
G1 X94.918 Y46.635 E.50204
G1 X95.452 Y46.635 E.0164
G1 X106.465 Y57.648 E.47884
G1 X106.465 Y57.115 E.0164
G1 X95.985 Y46.635 E.45564
G1 X96.519 Y46.635 E.0164
G1 X106.465 Y56.581 E.43244
G1 X106.465 Y56.048 E.0164
G1 X97.052 Y46.635 E.40924
G1 X97.586 Y46.635 E.0164
G1 X106.465 Y55.514 E.38604
G1 X106.465 Y54.981 E.0164
G1 X97.835 Y46.351 E.3752
G1 X97.835 Y45.818 E.0164
G1 X106.465 Y54.447 E.3752
G1 X106.465 Y53.913 E.0164
G1 X97.835 Y45.284 E.3752
G1 X97.835 Y44.751 E.0164
G1 X106.465 Y53.38 E.3752
G1 X106.465 Y52.846 E.0164
G1 X97.835 Y44.217 E.3752
G1 X97.835 Y43.683 E.0164
G1 X106.465 Y52.313 E.3752
G1 X106.465 Y51.779 E.0164
M73 P43 R19
G1 X97.835 Y43.15 E.3752
G1 X97.835 Y42.616 E.0164
G1 X106.465 Y51.246 E.3752
G1 X106.465 Y50.712 E.0164
G1 X97.835 Y42.083 E.3752
G1 X97.835 Y41.549 E.0164
G1 X106.465 Y50.178 E.3752
G1 X106.465 Y49.645 E.0164
G1 X97.835 Y41.016 E.3752
G1 X97.835 Y40.482 E.0164
G1 X106.634 Y49.281 E.38257
G1 X106.634 Y29.539 F30000
G1 F15000
G1 X99.635 Y22.54 E.30431
G1 X99.635 Y23.073 E.0164
G1 X106.465 Y29.903 E.29693
G1 X106.465 Y30.436 E.0164
G1 X99.635 Y23.607 E.29693
G1 X99.635 Y24.141 E.0164
G1 X106.465 Y30.97 E.29693
G1 X106.465 Y31.504 E.0164
G1 X99.635 Y24.674 E.29693
G1 X99.635 Y25.208 E.0164
G1 X106.465 Y32.037 E.29693
G1 X106.465 Y32.571 E.0164
G1 X99.635 Y25.741 E.29693
G1 X99.635 Y26.275 E.0164
G1 X106.465 Y33.104 E.29693
G1 X106.465 Y33.638 E.0164
G1 X99.635 Y26.808 E.29693
G1 X99.635 Y27.342 E.0164
G1 X106.465 Y34.171 E.29693
G1 X106.465 Y34.705 E.0164
G1 X99.635 Y27.876 E.29693
G1 X99.635 Y28.409 E.0164
G1 X106.465 Y35.239 E.29693
G1 X106.465 Y35.772 E.0164
G1 X99.635 Y28.943 E.29693
G1 X99.635 Y29.135 E.00592
G1 X99.294 Y29.135 E.01048
M73 P43 R18
G1 X106.465 Y36.306 E.31176
G1 X106.465 Y36.839 E.0164
G1 X98.761 Y29.135 E.33496
G1 X98.227 Y29.135 E.0164
G1 X106.465 Y37.373 E.35816
G1 X106.465 Y37.906 E.0164
G1 X97.694 Y29.135 E.38136
G1 X97.585 Y29.135 E.00333
G1 X97.585 Y29.561 E.01307
G1 X106.465 Y38.44 E.38607
G1 X106.465 Y38.974 E.0164
G1 X97.585 Y30.094 E.38607
G1 X97.585 Y30.628 E.0164
G1 X106.465 Y39.507 E.38607
G1 X106.465 Y40.041 E.0164
G1 X97.585 Y31.161 E.38607
G1 X97.585 Y31.695 E.0164
G1 X106.465 Y40.574 E.38607
G1 X106.465 Y41.108 E.0164
G1 X97.585 Y32.228 E.38607
G1 X97.585 Y32.762 E.0164
G1 X106.465 Y41.641 E.38607
G1 X106.465 Y42.175 E.0164
G1 X97.585 Y33.296 E.38607
G1 X97.585 Y33.829 E.0164
G1 X106.465 Y42.708 E.38607
G1 X106.465 Y43.242 E.0164
G1 X97.585 Y34.363 E.38607
G1 X97.585 Y34.896 E.0164
G1 X106.465 Y43.776 E.38607
G1 X106.465 Y44.309 E.0164
G1 X97.585 Y35.43 E.38607
G1 X97.585 Y35.963 E.0164
G1 X106.465 Y44.843 E.38607
G1 X106.465 Y45.376 E.0164
G1 X97.585 Y36.497 E.38607
G1 X97.585 Y37.031 E.0164
G1 X106.465 Y45.91 E.38607
G1 X106.465 Y46.443 E.0164
G1 X97.585 Y37.564 E.38607
G1 X97.585 Y38.098 E.0164
G1 X106.465 Y46.977 E.38607
G1 X106.465 Y47.511 E.0164
G1 X97.585 Y38.631 E.38607
G1 X97.585 Y39.165 E.0164
G1 X106.465 Y48.044 E.38607
G1 X106.465 Y48.578 E.0164
G1 X97.416 Y39.529 E.39344
; WIPE_START
G1 X98.83 Y40.943 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.733 Y45.535 Z1 F30000
G1 X92.134 Y45.986 Z1
G1 Z.6
G1 E.8 F1800
G1 F15000
G1 X51.084 Y4.935 E1.78484
G1 X51.617 Y4.935 E.0164
G1 X91.965 Y45.283 E1.75427
G1 X91.965 Y44.749 E.0164
G1 X52.151 Y4.935 E1.73107
G1 X52.684 Y4.935 E.0164
G1 X91.965 Y44.216 E1.70787
G1 X91.965 Y43.682 E.0164
G1 X53.218 Y4.935 E1.68467
G1 X53.752 Y4.935 E.0164
G1 X91.965 Y43.148 E1.66147
G1 X91.965 Y42.615 E.0164
G1 X54.285 Y4.935 E1.63827
G1 X54.819 Y4.935 E.0164
G1 X91.965 Y42.081 E1.61507
G1 X91.965 Y41.548 E.0164
G1 X55.352 Y4.935 E1.59187
G1 X55.886 Y4.935 E.0164
G1 X91.965 Y41.014 E1.56867
G1 X91.965 Y40.481 E.0164
G1 X56.419 Y4.935 E1.54547
G1 X56.953 Y4.935 E.0164
G1 X91.965 Y39.947 E1.52228
G1 X91.965 Y39.765 E.00561
G1 X92.215 Y39.765 E.00769
G1 X92.215 Y39.663 E.00311
G1 X57.487 Y4.935 E1.50995
G1 X58.02 Y4.935 E.0164
G1 X92.215 Y39.13 E1.48675
G1 X92.215 Y38.596 E.0164
G1 X58.554 Y4.935 E1.46355
G1 X59.087 Y4.935 E.0164
G1 X92.215 Y38.063 E1.44035
G1 X92.215 Y37.529 E.0164
G1 X59.621 Y4.935 E1.41715
G1 X60.154 Y4.935 E.0164
G1 X92.215 Y36.996 E1.39395
G1 X92.215 Y36.462 E.0164
G1 X60.688 Y4.935 E1.37075
G1 X61.222 Y4.935 E.0164
G1 X92.215 Y35.928 E1.34755
G1 X92.215 Y35.395 E.0164
G1 X61.755 Y4.935 E1.32435
G1 X62.289 Y4.935 E.0164
G1 X92.215 Y34.861 E1.30115
G1 X92.215 Y34.328 E.0164
G1 X62.822 Y4.935 E1.27796
G1 X63.356 Y4.935 E.0164
G1 X92.215 Y33.794 E1.25476
G1 X92.215 Y33.261 E.0164
G1 X63.889 Y4.935 E1.23156
G1 X64.423 Y4.935 E.0164
G1 X92.215 Y32.727 E1.20836
G1 X92.215 Y32.193 E.0164
G1 X64.957 Y4.935 E1.18516
G1 X65.49 Y4.935 E.0164
G1 X92.384 Y31.83 E1.16934
G1 X91.655 Y28.966 F30000
G1 F15000
G1 X92.215 Y29.526 E.02435
G1 X92.215 Y30.059 E.0164
G1 X91.291 Y29.135 E.04017
G1 X90.757 Y29.135 E.0164
G1 X92.215 Y30.593 E.06337
G1 X92.215 Y31.126 E.0164
G1 X66.024 Y4.935 E1.13876
G1 X66.557 Y4.935 E.0164
G1 X90.165 Y28.543 E1.02643
G1 X90.165 Y28.009 E.0164
G1 X67.091 Y4.935 E1.00323
G1 X67.624 Y4.935 E.0164
G1 X90.165 Y27.476 E.98003
G1 X90.165 Y26.942 E.0164
G1 X68.158 Y4.935 E.95683
G1 X68.692 Y4.935 E.0164
G1 X90.165 Y26.408 E.93363
G1 X90.165 Y25.875 E.0164
G1 X69.225 Y4.935 E.91043
G1 X69.759 Y4.935 E.0164
G1 X90.165 Y25.341 E.88724
G1 X90.165 Y24.808 E.0164
G1 X70.292 Y4.935 E.86404
G1 X70.826 Y4.935 E.0164
G1 X90.165 Y24.274 E.84084
G1 X90.165 Y23.741 E.0164
G1 X71.359 Y4.935 E.81764
G1 X71.893 Y4.935 E.0164
G1 X90.165 Y23.207 E.79444
G1 X90.165 Y22.674 E.0164
G1 X72.427 Y4.935 E.77124
G1 X72.96 Y4.935 E.0164
G1 X90.165 Y22.14 E.74804
G1 X90.165 Y22.065 E.00231
G1 X90.623 Y22.065 E.01409
G1 X73.494 Y4.935 E.74477
G1 X74.027 Y4.935 E.0164
G1 X91.157 Y22.065 E.74477
G1 X91.69 Y22.065 E.0164
G1 X74.561 Y4.935 E.74477
G1 X75.094 Y4.935 E.0164
G1 X92.215 Y22.056 E.74438
G1 X92.215 Y21.765 E.00895
G1 X92.457 Y21.765 E.00746
G1 X75.628 Y4.935 E.73172
G1 X76.161 Y4.935 E.0164
G1 X92.991 Y21.765 E.73172
G1 X93.524 Y21.765 E.0164
G1 X76.695 Y4.935 E.73172
G1 X77.229 Y4.935 E.0164
G1 X94.058 Y21.765 E.73172
M73 P44 R18
G1 X94.592 Y21.765 E.0164
G1 X77.762 Y4.935 E.73172
G1 X78.296 Y4.935 E.0164
G1 X95.125 Y21.765 E.73172
G1 X95.659 Y21.765 E.0164
G1 X78.829 Y4.935 E.73172
G1 X79.363 Y4.935 E.0164
G1 X96.192 Y21.765 E.73172
G1 X96.726 Y21.765 E.0164
G1 X79.896 Y4.935 E.73172
G1 X80.43 Y4.935 E.0164
G1 X97.259 Y21.765 E.73172
G1 X97.585 Y21.765 E.01002
G1 X97.585 Y22.065 E.00922
G1 X98.093 Y22.065 E.01561
G1 X80.964 Y4.935 E.74477
G1 X81.497 Y4.935 E.0164
G1 X98.627 Y22.065 E.74477
G1 X99.16 Y22.065 E.0164
G1 X82.031 Y4.935 E.74477
G1 X82.564 Y4.935 E.0164
G1 X106.465 Y28.836 E1.03917
G1 X106.465 Y28.302 E.0164
G1 X83.098 Y4.935 E1.01597
G1 X83.631 Y4.935 E.0164
G1 X106.465 Y27.769 E.99277
G1 X106.465 Y27.235 E.0164
G1 X84.165 Y4.935 E.96957
G1 X84.699 Y4.935 E.0164
G1 X106.465 Y26.701 E.94637
G1 X106.465 Y26.168 E.0164
G1 X85.232 Y4.935 E.92317
G1 X85.766 Y4.935 E.0164
G1 X106.465 Y25.634 E.89997
G1 X106.465 Y25.101 E.0164
G1 X86.299 Y4.935 E.87677
G1 X86.833 Y4.935 E.0164
G1 X106.465 Y24.567 E.85357
G1 X106.465 Y24.034 E.0164
G1 X87.366 Y4.935 E.83037
G1 X87.9 Y4.935 E.0164
G1 X106.465 Y23.5 E.80718
G1 X106.465 Y22.966 E.0164
G1 X88.434 Y4.935 E.78398
G1 X88.967 Y4.935 E.0164
G1 X106.465 Y22.433 E.76078
G1 X106.465 Y21.899 E.0164
G1 X89.501 Y4.935 E.73758
G1 X90.034 Y4.935 E.0164
G1 X106.465 Y21.366 E.71438
G1 X106.465 Y20.832 E.0164
G1 X90.568 Y4.935 E.69118
G1 X91.101 Y4.935 E.0164
G1 X106.465 Y20.299 E.66798
G1 X106.465 Y19.765 E.0164
G1 X91.635 Y4.935 E.64478
G1 X92.169 Y4.935 E.0164
G1 X106.465 Y19.231 E.62158
G1 X106.465 Y18.698 E.0164
G1 X92.702 Y4.935 E.59838
G1 X93.236 Y4.935 E.0164
G1 X106.465 Y18.164 E.57519
G1 X106.465 Y17.631 E.0164
G1 X93.769 Y4.935 E.55199
G1 X94.303 Y4.935 E.0164
G1 X106.465 Y17.097 E.52879
G1 X106.465 Y16.564 E.0164
G1 X94.836 Y4.935 E.50559
G1 X95.37 Y4.935 E.0164
G1 X106.465 Y16.03 E.48239
G1 X106.465 Y15.496 E.0164
G1 X95.904 Y4.935 E.45919
G1 X96.437 Y4.935 E.0164
G1 X106.465 Y14.963 E.43599
G1 X106.465 Y14.429 E.0164
G1 X96.971 Y4.935 E.41279
G1 X97.504 Y4.935 E.0164
G1 X106.465 Y13.896 E.38959
G1 X106.465 Y13.362 E.0164
G1 X98.038 Y4.935 E.36639
G1 X98.571 Y4.935 E.0164
G1 X106.465 Y12.829 E.34319
G1 X106.465 Y12.295 E.0164
G1 X99.105 Y4.935 E.32
G1 X99.639 Y4.935 E.0164
G1 X106.465 Y11.761 E.2968
G1 X106.465 Y11.228 E.0164
G1 X100.172 Y4.935 E.2736
G1 X100.706 Y4.935 E.0164
G1 X106.465 Y10.694 E.2504
G1 X106.465 Y10.161 E.0164
G1 X101.239 Y4.935 E.2272
G1 X101.773 Y4.935 E.0164
G1 X106.465 Y9.627 E.204
G1 X106.465 Y9.094 E.0164
G1 X102.306 Y4.935 E.1808
G1 X102.84 Y4.935 E.0164
G1 X106.465 Y8.56 E.1576
G1 X106.465 Y8.027 E.0164
G1 X103.373 Y4.935 E.1344
G1 X103.907 Y4.935 E.0164
G1 X106.465 Y7.493 E.1112
G1 X106.465 Y6.959 E.0164
G1 X104.441 Y4.935 E.088
G1 X104.974 Y4.935 E.0164
G1 X106.465 Y6.426 E.06481
G1 X106.465 Y5.892 E.0164
G1 X105.508 Y4.935 E.04161
G1 X106.041 Y4.935 E.0164
G1 X106.634 Y5.528 E.02578
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X106.041 Y4.935 E-.3187
G1 X105.508 Y4.935 E-.20276
G1 X105.952 Y5.379 E-.23854
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 4/40
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
G17
G3 Z1 I1.217 J0 P1  F30000
; object ids of layer 4 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer4 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z1.2 F30000
G1 X160.4 Y8 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z1.2 F30000
G1 X114.002 Y8.498 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z1.2 F30000
G1 X93.502 Y73.11 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z1.2 F30000
G1 X97.11 Y46.302 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.802 E.3747
G1 X90.498 Y28.802 E.068
G1 X90.498 Y22.398 E.21244
G1 X92.548 Y22.398 E.068
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.302 Y22.398 E.068
G1 X99.302 Y28.802 E.21244
G1 X97.252 Y28.802 E.068
G1 X97.252 Y40.098 E.3747
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.41 E.37119
G1 X90.89 Y28.41 E.06299
G1 X90.89 Y22.79 E.17269
G1 X92.94 Y22.79 E.06299
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.91 Y22.79 E.06299
G1 X98.91 Y28.41 E.17269
G1 X96.86 Y28.41 E.06299
G1 X96.86 Y40.49 E.37119
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z1.2 F30000
G1 X35.102 Y45.91 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.802 E.3747
G1 X28.098 Y28.802 E.068
G1 X28.098 Y22.398 E.21244
G1 X30.148 Y22.398 E.068
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.902 Y22.398 E.068
G1 X36.902 Y28.802 E.21244
G1 X34.852 Y28.802 E.068
G1 X34.852 Y40.098 E.3747
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.41 E.37119
G1 X28.49 Y28.41 E.06299
G1 X28.49 Y22.79 E.17269
G1 X30.54 Y22.79 E.06299
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.51 Y22.79 E.06299
G1 X36.51 Y28.41 E.17269
G1 X34.46 Y28.41 E.06299
G1 X34.46 Y40.49 E.37119
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.006 Y53.504 Z1.2 F30000
G1 X33.781 Y73.499 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.7 Y73.501 E.0027
G3 X33.505 Y67.907 I.008 J-2.801 E.28486
G3 X34.514 Y68.018 I.208 J2.742 E.03385
G3 X33.975 Y73.488 I-.806 J2.682 E.25588
G1 X33.841 Y73.495 E.00443
G1 X33.764 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.097 E.00921
G3 X33.524 Y68.298 I.244 J-2.397 E.21938
G3 X34.17 Y68.336 I.172 J2.604 E.01993
G3 X33.936 Y73.099 I-.462 J2.364 E.21125
G1 X33.824 Y73.099 E.00346
; WIPE_START
M204 S10000
G1 X33.464 Y73.097 E-.13665
G1 X33 Y73.007 E-.17948
G1 X32.564 Y72.826 E-.1796
G1 X32.171 Y72.563 E-.17954
G1 X32.013 Y72.405 E-.08473
; WIPE_END
G1 E-.04 F1800
G1 X39.425 Y74.228 Z1.2 F30000
G1 X106.798 Y90.798 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X104.238 Y83.559 Z1.2 F30000
G1 X97.6 Y30.78 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X97.6 Y29.152 E.05401
G1 X98.882 Y29.15 E.04252
G1 X106.45 Y36.718 E.35502
G1 X106.45 Y35.654 E.03529
G1 X97.85 Y44.254 E.40341
G1 X97.85 Y43.471 E.02597
G1 X106.45 Y52.07 E.40341
G1 X106.45 Y51.006 E.03529
G1 X89.906 Y67.55 E.7761
G1 X91.226 Y67.55 E.04377
G1 X28.626 Y4.95 E2.93666
G1 X29.69 Y4.95 E.03529
G1 X20.95 Y13.69 E.41
G1 X20.95 Y12.626 E.03529
G1 X30.074 Y21.75 E.428
G1 X35.2 Y21.75 E.17006
G1 X35.2 Y22.05 E.00995
G1 X35.619 Y22.05 E.01388
G1 X52.718 Y4.95 E.80217
G1 X51.654 Y4.95 E.03529
G1 X91.95 Y45.246 E1.89035
G1 X91.95 Y42.478 E.09181
G1 X43.978 Y90.45 E2.25044
G1 X45.042 Y90.45 E.03529
G1 X20.95 Y66.358 E1.13019
G1 X20.95 Y67.422 E.03529
G1 X83.422 Y4.95 E2.93067
G1 X82.358 Y4.95 E.03529
G1 X99.457 Y22.05 E.80217
G1 X99.65 Y22.05 E.0064
G1 X99.65 Y22.243 E.0064
G1 X106.45 Y29.042 E.31897
G1 X106.45 Y27.978 E.03529
G1 X97.6 Y36.828 E.41514
G1 X97.6 Y35.545 E.04256
G1 X106.45 Y44.394 E.41514
M73 P45 R18
G1 X106.45 Y43.33 E.03529
G1 X59.33 Y90.45 E2.21048
G1 X60.394 Y90.45 E.03529
G1 X20.95 Y51.006 E1.85038
G1 X20.95 Y52.07 E.03529
G1 X29.55 Y43.471 E.40341
G1 X29.55 Y44.253 E.02597
G1 X20.95 Y35.654 E.40341
G1 X20.95 Y36.718 E.03529
G1 X28.518 Y29.15 E.35501
G1 X29.8 Y29.152 E.04252
G1 X29.8 Y30.78 E.05401
; WIPE_START
G1 X29.8 Y29.152 E-.61876
G1 X29.428 Y29.151 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X35.2 Y29.785 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F15476.087
G1 X35.2 Y29.15 E.02105
G1 X36.194 Y29.15 E.03296
G1 X35.2 Y30.144 E.04661
G1 X35.2 Y31.772 E.05401
; WIPE_START
G1 X35.2 Y30.144 E-.61876
G1 X35.463 Y29.881 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X28.836 Y26.094 Z1.2 F30000
G1 X27.75 Y25.473 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F15476.087
G1 X27.75 Y27.102 E.05401
G1 X20.95 Y20.302 E.31897
G1 X20.95 Y21.366 E.03529
G1 X37.366 Y4.95 E.7701
G1 X36.302 Y4.95 E.03529
G1 X106.45 Y75.098 E3.29076
G1 X106.45 Y74.034 E.03529
G1 X90.034 Y90.45 E.7701
G1 X91.098 Y90.45 E.03529
G1 X35.2 Y34.552 E2.62226
G1 X35.2 Y37.82 E.10839
G1 X68.07 Y4.95 E1.54198
G1 X67.006 Y4.95 E.03529
G1 X90.15 Y28.094 E1.08572
G1 X90.15 Y28.926 E.02761
G1 X28.626 Y90.45 E2.88619
G1 X29.69 Y90.45 E.03529
G1 X20.95 Y81.71 E.41
G1 X20.95 Y82.774 E.03529
G1 X31.162 Y72.562 E.47905
G3 X31.138 Y68.87 I2.6 J-1.863 E.13055
G1 X20.95 Y58.682 E.47794
G1 X20.95 Y59.746 E.03529
G1 X34.046 Y46.65 E.61434
G1 X31.946 Y46.65 E.06964
G1 X75.746 Y90.45 E2.05472
G1 X74.682 Y90.45 E.03529
G1 X91.281 Y73.85 E.77871
G1 X89.85 Y73.85 E.04747
G1 X106.45 Y90.45 E.77871
G1 X105.386 Y90.45 E.03529
G1 X106.45 Y89.386 E.04991
G1 X106.45 Y87.758 E.05401
; WIPE_START
G1 X106.45 Y89.386 E-.61876
G1 X106.187 Y89.649 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X104.45 Y82.216 Z1.2 F30000
G1 X92.2 Y29.785 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F15476.087
G1 X92.2 Y29.15 E.02105
G1 X91.206 Y29.15 E.03296
G1 X92.2 Y30.144 E.04661
G1 X92.2 Y31.772 E.05401
; WIPE_START
G1 X92.2 Y30.144 E-.61876
G1 X91.937 Y29.881 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X98.564 Y26.094 Z1.2 F30000
G1 X99.65 Y25.473 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F15476.087
G1 X99.65 Y27.102 E.05401
G1 X106.45 Y20.302 E.31897
G1 X106.45 Y21.366 E.03529
G1 X90.034 Y4.95 E.7701
G1 X91.098 Y4.95 E.03529
G1 X20.95 Y75.098 E3.29076
G1 X20.95 Y74.034 E.03529
G1 X37.366 Y90.45 E.7701
G1 X36.302 Y90.45 E.03529
G1 X92.2 Y34.552 E2.62226
G1 X92.2 Y37.82 E.10839
G1 X59.33 Y4.95 E1.54198
G1 X60.394 Y4.95 E.03529
G1 X37.25 Y28.094 E1.08572
G1 X37.25 Y28.926 E.02761
G1 X98.774 Y90.45 E2.88619
G1 X97.71 Y90.45 E.03529
G1 X106.45 Y81.71 E.41
G1 X106.45 Y82.774 E.03529
G1 X93.85 Y70.174 E.59106
G1 X93.85 Y71.281 E.03672
G1 X106.45 Y58.682 E.59106
G1 X106.45 Y59.746 E.03529
G1 X93.354 Y46.65 E.61434
G1 X95.454 Y46.65 E.06964
G1 X51.654 Y90.45 E2.05472
G1 X52.718 Y90.45 E.03529
G1 X35.53 Y73.262 E.80633
G2 X35.562 Y68.162 I-1.858 J-2.562 E.19671
G1 X98.774 Y4.95 E2.96539
G1 X97.71 Y4.95 E.03529
G1 X106.45 Y13.69 E.41
G1 X106.45 Y12.626 E.03529
G1 X97.326 Y21.75 E.428
G1 X92.2 Y21.75 E.17006
G1 X92.2 Y22.05 E.00995
G1 X91.781 Y22.05 E.01388
G1 X74.682 Y4.95 E.80217
G1 X75.746 Y4.95 E.03529
G1 X35.45 Y45.246 E1.89035
G1 X35.45 Y42.478 E.09181
G1 X83.422 Y90.45 E2.25044
G1 X82.358 Y90.45 E.03529
G1 X106.45 Y66.358 E1.13019
G1 X106.45 Y67.422 E.03529
G1 X43.978 Y4.95 E2.93067
G1 X45.042 Y4.95 E.03529
G1 X27.943 Y22.05 E.80217
G1 X27.75 Y22.05 E.0064
G1 X27.75 Y22.243 E.0064
G1 X20.95 Y29.042 E.31897
G1 X20.95 Y27.978 E.03529
G1 X29.8 Y36.828 E.41514
G1 X29.8 Y35.545 E.04256
G1 X20.95 Y44.394 E.41514
G1 X20.95 Y43.33 E.03529
G1 X68.07 Y90.45 E2.21048
G1 X67.006 Y90.45 E.03529
G1 X83.605 Y73.85 E.77871
G1 X83.55 Y73.85 E.00185
G1 X83.55 Y67.55 E.209
G1 X20.95 Y4.95 E2.93666
G1 X20.95 Y6.014 E.03529
G1 X22.014 Y4.95 E.04991
G1 X23.642 Y4.95 E.05401
G1 X23.642 Y90.45 F30000
G1 F15476.087
G1 X22.014 Y90.45 E.05401
G1 X20.95 Y89.386 E.04991
G1 X20.95 Y90.45 E.03529
G1 X106.45 Y4.95 E4.01095
G1 X106.45 Y6.014 E.03529
G1 X105.386 Y4.95 E.04991
G1 X103.758 Y4.95 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X105.386 Y4.95 E-.61876
G1 X105.649 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 5/40
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
G17
G3 Z1.2 I1.217 J0 P1  F30000
; object ids of layer 5 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer5 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z1.4 F30000
G1 X160.4 Y8 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z1.4 F30000
G1 X114.002 Y8.498 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z1.4 F30000
G1 X93.502 Y73.11 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
M73 P46 R18
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z1.4 F30000
G1 X97.11 Y46.302 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.802 E.3747
G1 X90.498 Y28.802 E.068
G1 X90.498 Y22.398 E.21244
G1 X92.548 Y22.398 E.068
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.302 Y22.398 E.068
G1 X99.302 Y28.802 E.21244
G1 X97.252 Y28.802 E.068
G1 X97.252 Y40.098 E.3747
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.41 E.37119
G1 X90.89 Y28.41 E.06299
G1 X90.89 Y22.79 E.17269
G1 X92.94 Y22.79 E.06299
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.91 Y22.79 E.06299
G1 X98.91 Y28.41 E.17269
G1 X96.86 Y28.41 E.06299
G1 X96.86 Y40.49 E.37119
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z1.4 F30000
G1 X35.102 Y45.91 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.802 E.3747
G1 X28.098 Y28.802 E.068
G1 X28.098 Y22.398 E.21244
G1 X30.148 Y22.398 E.068
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.902 Y22.398 E.068
G1 X36.902 Y28.802 E.21244
G1 X34.852 Y28.802 E.068
G1 X34.852 Y40.098 E.3747
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.41 E.37119
G1 X28.49 Y28.41 E.06299
G1 X28.49 Y22.79 E.17269
G1 X30.54 Y22.79 E.06299
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.51 Y22.79 E.06299
G1 X36.51 Y28.41 E.17269
G1 X34.46 Y28.41 E.06299
G1 X34.46 Y40.49 E.37119
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.999 Y53.504 Z1.4 F30000
G1 X33.758 Y73.5 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.7 Y73.499 E.00191
G3 X33.425 Y67.911 I0 J-2.801 E.28278
G1 X33.7 Y67.897 E.00912
G3 X33.974 Y73.486 I0 J2.801 E.28279
G1 X33.817 Y73.496 E.00522
G1 X33.737 Y73.107 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.7 Y73.107 E.00113
G3 X33.464 Y68.301 I0 J-2.409 E.22525
G1 X33.7 Y68.29 E.00727
G3 X34.17 Y73.061 I0 J2.409 E.21801
G1 X33.797 Y73.1 E.01153
; WIPE_START
M204 S10000
G1 X33.7 Y73.107 E-.0368
G1 X33.23 Y73.064 E-.17946
G1 X32.778 Y72.927 E-.17952
G1 X32.361 Y72.704 E-.17956
G1 X31.996 Y72.404 E-.17954
G1 X31.987 Y72.394 E-.00512
; WIPE_END
G1 E-.04 F1800
G1 X39.399 Y74.217 Z1.4 F30000
G1 X106.798 Y90.798 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X100.257 Y85.307 Z1.4 F30000
G1 X90.784 Y74.123 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X90.791 Y73.85 E.00905
G1 X91.281 Y73.85 E.01625
G3 X91.18 Y73.929 I-.211 J-.166 E.00431
G1 X75.059 Y90.073 E.75678
G1 X75.369 Y90.073 E.01027
G1 X32.324 Y47.027 E2.01933
G1 X33.669 Y47.027 E.04462
G1 X21.327 Y59.369 E.57895
G1 X21.327 Y59.059 E.01027
G1 X30.869 Y68.6 E.4476
G2 X30.892 Y72.832 I2.897 J2.099 E.15018
G1 X21.327 Y82.397 E.44871
G1 X21.327 Y82.087 E.01027
G1 X29.313 Y90.073 E.37461
G1 X29.003 Y90.073 E.01027
G1 X89.773 Y29.303 E2.8508
G1 X89.773 Y27.717 E.05263
G1 X67.383 Y5.327 E1.05033
G1 X67.693 Y5.327 E.01027
G1 X35.577 Y37.443 E1.50659
G1 X35.577 Y34.929 E.08337
G1 X90.721 Y90.073 E2.58688
G1 X90.411 Y90.073 E.01027
G1 X106.073 Y74.411 E.73471
G1 X106.073 Y74.721 E.01027
G1 X36.679 Y5.327 E3.25537
G1 X36.989 Y5.327 E.01027
G1 X21.327 Y20.989 E.73471
G1 X21.327 Y20.679 E.01027
G1 X27.373 Y26.724 E.28358
G1 X27.373 Y29.527 E.09298
G1 X28.141 Y29.527 E.02549
G1 X21.327 Y36.341 E.31963
G1 X21.327 Y36.031 E.01027
G1 X29.173 Y43.876 E.36803
G1 X21.327 Y51.693 E.36736
G1 X21.327 Y51.383 E.01027
G1 X60.017 Y90.073 E1.81499
G1 X59.707 Y90.073 E.01027
G1 X106.073 Y43.707 E2.17509
G1 X106.073 Y44.017 E.01027
G1 X97.978 Y35.922 E.37975
G1 X97.978 Y36.45 E.01753
G1 X106.073 Y28.355 E.37975
G1 X106.073 Y28.665 E.01027
G1 X100.028 Y22.62 E.28358
G1 X100.028 Y23.474 E.02833
G1 X99.65 Y23.097 E.01769
G1 X99.65 Y23.338 E.00799
G1 X99.665 Y24.866 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.395972
G1 F3000;_EXTRUDE_SET_SPEED
G1 X99.665 Y29.006 E.11908
G1 X99.638 Y29.138 E.00388
G1 X99.506 Y29.165 E.00388
G1 X98.491 Y29.165 E.02918
; Slow Down End
G1 X97.805 Y29.15 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X97.933 Y29.15 E.00424
G1 X97.6 Y29.483 E.0156
G1 X97.6 Y29.152 E.01099
G1 X97.805 Y29.15 E.00679
G1 X97.615 Y29.981 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.383703
G1 F3000;_EXTRUDE_SET_SPEED
G1 X97.615 Y39.576 E.26644
G1 X97.642 Y39.708 E.00374
G1 X97.838 Y39.762 E.00563
G1 X97.865 Y39.894 E.00374
G1 X97.865 Y46.506 E.18359
G1 X97.838 Y46.638 E.00374
G1 X97.706 Y46.665 E.00374
G1 X92.094 Y46.665 E.15582
G1 X91.963 Y46.638 E.00374
G1 X91.935 Y46.506 E.00374
G1 X91.935 Y39.894 E.18359
G1 X91.963 Y39.762 E.00374
G1 X92.158 Y39.708 E.00563
G1 X92.185 Y39.576 E.00374
G1 X92.185 Y29.549 E.27843
; Slow Down End
G1 X91.828 Y29.165 F30000
; Slow Down Start
; LINE_WIDTH: 0.391716
G1 F3000;_EXTRUDE_SET_SPEED
G1 X90.294 Y29.165 E.0436
G1 X90.163 Y29.138 E.00383
G1 X90.135 Y29.006 E.00383
M73 P46 R17
G1 X90.135 Y27.671 E.03794
; Slow Down End
G1 X90.135 Y25.437 F30000
; Slow Down Start
; LINE_WIDTH: 0.386494
G1 F3000;_EXTRUDE_SET_SPEED
G1 X90.135 Y22.194 E.09078
G1 X90.163 Y22.062 E.00377
G1 X90.294 Y22.035 E.00377
G1 X92.026 Y22.035 E.04848
G1 X92.158 Y22.008 E.00377
G1 X92.213 Y21.762 E.00704
G1 X92.344 Y21.735 E.00377
G1 X97.456 Y21.735 E.1431
G1 X97.588 Y21.762 E.00377
G1 X97.642 Y22.008 E.00704
G1 X97.774 Y22.035 E.00377
G1 X99.506 Y22.035 E.04848
G1 X99.638 Y22.062 E.00377
G1 X99.662 Y22.65 E.01646
; Slow Down End
; WIPE_START
G1 X99.638 Y22.062 E-.22344
G1 X99.506 Y22.035 E-.05119
G1 X98.228 Y22.035 E-.48537
; WIPE_END
G1 E-.04 F1800
G1 X92.733 Y21.373 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X91.823 Y21.373 E.03019
G1 X91.823 Y21.673 E.00995
G1 X91.404 Y21.673 E.01388
G1 X75.059 Y5.327 E.76678
G1 X75.369 Y5.327 E.01027
G1 X35.827 Y44.869 E1.85496
G1 X35.827 Y42.855 E.06679
G1 X83.045 Y90.073 E2.21505
G1 X82.735 Y90.073 E.01027
G1 X106.073 Y66.735 E1.0948
G1 X106.073 Y67.045 E.01027
G1 X44.355 Y5.327 E2.89528
G1 X44.665 Y5.327 E.01027
G1 X28.32 Y21.673 E.76678
G1 X29.423 Y21.673 E.03658
G1 X29.423 Y21.373 E.00995
G1 X29.697 Y21.373 E.00909
G1 X21.327 Y13.003 E.39261
G1 X21.327 Y13.313 E.01027
G1 X29.313 Y5.327 E.37461
G1 X29.003 Y5.327 E.01027
G1 X90.848 Y67.173 E2.90128
G1 X90.283 Y67.173 E.01875
G1 X106.073 Y51.383 E.74071
G1 X106.073 Y51.693 E.01027
G1 X98.228 Y43.848 E.36803
G1 X106.073 Y36.031 E.36736
G1 X106.073 Y36.341 E.01027
G1 X99.259 Y29.527 E.31963
G1 X100.028 Y29.527 E.02549
G1 X100.028 Y26.724 E.09298
G1 X106.073 Y20.679 E.28358
G1 X106.073 Y20.989 E.01027
G1 X90.411 Y5.327 E.73471
G1 X90.721 Y5.327 E.01027
G1 X21.327 Y74.721 E3.25537
G1 X21.327 Y74.411 E.01027
G1 X36.989 Y90.073 E.73471
G1 X36.679 Y90.073 E.01027
G1 X91.823 Y34.929 E2.58688
G1 X91.823 Y37.443 E.08337
G1 X59.707 Y5.327 E1.50659
G1 X60.017 Y5.327 E.01027
G1 X37.627 Y27.717 E1.05033
G1 X37.628 Y29.303 E.05263
G1 X98.397 Y90.073 E2.8508
G1 X98.087 Y90.073 E.01027
G1 X106.073 Y82.087 E.37461
G1 X106.073 Y82.397 E.01027
G1 X94.228 Y70.552 E.55567
G1 X94.228 Y70.904 E.0117
G1 X106.073 Y59.059 E.55567
G1 X106.073 Y59.369 E.01027
G1 X93.731 Y47.027 E.57895
G1 X95.076 Y47.027 E.04462
G1 X52.031 Y90.073 E2.01933
G1 X52.341 Y90.073 E.01027
G1 X35.8 Y73.531 E.77598
G2 X35.832 Y67.892 I-2.132 J-2.832 E.21628
G1 X98.397 Y5.327 E2.93505
G1 X98.087 Y5.327 E.01027
G1 X106.073 Y13.313 E.37461
G1 X106.073 Y13.003 E.01027
G1 X97.703 Y21.373 E.39261
G1 X97.978 Y21.373 E.00909
G1 X97.978 Y21.673 E.00995
G1 X99.08 Y21.673 E.03658
G1 X82.735 Y5.327 E.76678
G1 X83.045 Y5.327 E.01027
G1 X21.327 Y67.045 E2.89528
G1 X21.327 Y66.735 E.01027
G1 X44.665 Y90.073 E1.0948
G1 X44.355 Y90.073 E.01027
G1 X91.573 Y42.855 E2.21505
G1 X91.573 Y44.869 E.06679
G1 X52.031 Y5.327 E1.85496
G1 X52.341 Y5.327 E.01027
G1 X35.996 Y21.673 E.76678
G1 X35.577 Y21.673 E.01388
G1 X35.577 Y21.373 E.00995
G1 X34.668 Y21.373 E.03019
; WIPE_START
G1 X35.577 Y21.373 E-.34579
G1 X35.577 Y21.673 E-.114
G1 X35.996 Y21.673 E-.15897
G1 X36.259 Y21.41 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X29 Y23.768 Z1.4 F30000
G1 X27.735 Y24.179 Z1.4
G1 Z1
G1 E.8 F1800
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.384846
G1 F3000;_EXTRUDE_SET_SPEED
G1 X27.735 Y22.194 E.05531
G1 X27.762 Y22.062 E.00375
G1 X27.894 Y22.035 E.00375
G1 X29.626 Y22.035 E.04824
G1 X29.758 Y22.008 E.00375
G1 X29.812 Y21.762 E.007
G1 X29.944 Y21.735 E.00375
G1 X35.056 Y21.735 E.14241
G1 X35.188 Y21.762 E.00375
G1 X35.242 Y22.008 E.007
G1 X35.374 Y22.035 E.00375
G1 X37.106 Y22.035 E.04824
G1 X37.238 Y22.062 E.00375
G1 X37.265 Y22.194 E.00375
G1 X37.265 Y23.689 E.04164
G1 X37.354 Y24.002 E.00907
G1 X37.265 Y24.291 E.00843
G1 X37.265 Y29.006 E.13136
G1 X37.238 Y29.138 E.00375
G1 X37.106 Y29.165 E.00375
G1 X36.125 Y29.165 E.02733
; Slow Down End
G1 X35.215 Y30.015 F30000
; Slow Down Start
; LINE_WIDTH: 0.383816
G1 F3000;_EXTRUDE_SET_SPEED
G1 X35.215 Y39.576 E.2656
G1 X35.242 Y39.708 E.00374
G1 X35.438 Y39.762 E.00563
G1 X35.465 Y39.894 E.00374
G1 X35.465 Y46.506 E.18365
G1 X35.438 Y46.638 E.00374
G1 X35.306 Y46.665 E.00374
G1 X29.694 Y46.665 E.15587
G1 X29.562 Y46.638 E.00374
G1 X29.535 Y46.506 E.00374
G1 X29.535 Y39.894 E.18365
G1 X29.562 Y39.762 E.00374
G1 X29.758 Y39.708 E.00563
G1 X29.785 Y39.576 E.00374
G1 X29.785 Y29.324 E.28478
G1 X29.758 Y29.192 E.00374
G1 X29.626 Y29.165 E.00374
G1 X27.894 Y29.165 E.0481
G1 X27.762 Y29.138 E.00374
G1 X27.735 Y29.006 E.00374
G1 X27.735 Y26.53 E.06877
; Slow Down End
G1 X27.373 Y24.248 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X27.373 Y22.62 E.05401
G1 X21.327 Y28.665 E.28358
G1 X21.327 Y28.355 E.01027
G1 X29.423 Y36.45 E.37975
G1 X29.423 Y35.922 E.01753
G1 X21.327 Y44.017 E.37975
G1 X21.327 Y43.707 E.01027
G1 X67.693 Y90.073 E2.17509
M73 P47 R17
G1 X67.383 Y90.073 E.01027
G1 X83.228 Y74.228 E.74332
G1 X90.228 Y74.228 E.23218
G1 X106.073 Y90.073 E.74332
G1 X106.073 Y89.763 E.01027
G1 X105.763 Y90.073 E.01452
G1 X104.135 Y90.073 E.05401
G1 X90.428 Y73.865 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.394231
G1 F3000;_EXTRUDE_SET_SPEED
G1 X83.694 Y73.865 E.19277
G1 X83.563 Y73.838 E.00386
G1 X83.535 Y73.706 E.00386
G1 X83.535 Y67.694 E.17208
G1 X83.563 Y67.563 E.00386
G1 X83.694 Y67.535 E.00386
G1 X89.442 Y67.535 E.16453
; Slow Down End
G1 X90.87 Y67.535 F30000
; Slow Down Start
; LINE_WIDTH: 0.383729
G1 F3000;_EXTRUDE_SET_SPEED
G1 X93.706 Y67.535 E.07875
G1 X93.838 Y67.563 E.00374
G1 X93.865 Y67.694 E.00374
G1 X93.865 Y73.706 E.16694
G1 X93.838 Y73.838 E.00374
G1 X93.706 Y73.865 E.00374
G1 X92.05 Y73.865 E.04597
; Slow Down End
; WIPE_START
G1 X93.706 Y73.865 E-.62896
G1 X93.838 Y73.838 E-.05119
G1 X93.865 Y73.706 E-.05119
G1 X93.865 Y73.63 E-.02866
; WIPE_END
G1 E-.04 F1800
G1 X87.649 Y69.201 Z1.4 F30000
G1 X84.801 Y67.173 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X83.173 Y67.173 E.05401
G1 X21.327 Y5.327 E2.90128
G1 X21.637 Y5.327 E.01027
G1 X21.327 Y5.637 E.01452
G1 X21.327 Y7.265 E.05401
; WIPE_START
G1 X21.327 Y5.637 E-.61876
G1 X21.59 Y5.374 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X25.204 Y12.097 Z1.4 F30000
G1 X35.577 Y31.395 Z1.4
G1 Z1
G1 E.8 F1800
G1 F15476.087
G1 X35.577 Y29.767 E.05401
G1 X35.817 Y29.527 E.01123
G1 X37.445 Y29.527 E.05401
G1 X36.843 Y70.39 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38292
G1 F3000;_EXTRUDE_SET_SPEED
G1 X36.843 Y71.01 E.01715
G1 X36.722 Y71.617 E.01716
G1 X36.485 Y72.189 E.01716
G1 X36.141 Y72.704 E.01716
G1 X35.704 Y73.141 E.01714
G1 X35.189 Y73.485 E.01716
G1 X34.617 Y73.722 E.01716
G1 X34.01 Y73.843 E.01716
G1 X33.39 Y73.843 E.01715
G1 X32.783 Y73.722 E.01716
G1 X32.211 Y73.485 E.01716
G1 X31.696 Y73.141 E.01716
G1 X31.259 Y72.704 E.01714
G1 X30.915 Y72.189 E.01716
G1 X30.678 Y71.617 E.01715
G1 X30.557 Y71.01 E.01716
G1 X30.557 Y70.39 E.01715
G1 X30.678 Y69.783 E.01716
G1 X30.915 Y69.211 E.01716
G1 X31.259 Y68.696 E.01716
G1 X31.696 Y68.259 E.01714
G1 X32.211 Y67.915 E.01716
G1 X32.781 Y67.678 E.0171
G1 X33.502 Y67.549 E.02028
G1 X34.009 Y67.557 E.01404
G1 X34.617 Y67.678 E.01718
G1 X35.189 Y67.915 E.01716
G1 X35.704 Y68.259 E.01716
G1 X36.141 Y68.696 E.01714
G1 X36.485 Y69.211 E.01716
G1 X36.722 Y69.783 E.01716
G1 X36.831 Y70.332 E.01549
; Slow Down End
G1 X91.823 Y31.395 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X91.823 Y29.767 E.05401
G1 X91.583 Y29.527 E.01123
G1 X89.955 Y29.527 E.05401
; WIPE_START
G1 X91.583 Y29.527 E-.61876
G1 X91.823 Y29.767 E-.12859
G1 X91.823 Y29.8 E-.01265
; WIPE_END
G1 E-.04 F1800
G1 X95.253 Y22.982 Z1.4 F30000
G1 X104.135 Y5.327 Z1.4
G1 Z1
G1 E.8 F1800
G1 F15476.087
G1 X105.763 Y5.327 E.05401
G1 X106.073 Y5.637 E.01452
G1 X106.073 Y5.328 E.01027
G1 X21.327 Y90.073 E3.97556
G1 X21.327 Y89.763 E.01027
G1 X21.637 Y90.073 E.01452
G1 X23.265 Y90.073 E.05401
G1 X106.408 Y4.992 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.399451
G1 F3000;_EXTRUDE_SET_SPEED
G1 X106.435 Y5.124 E.00391
G1 X106.435 Y90.276 E2.47389
G1 X106.408 Y90.408 E.00391
G1 X106.276 Y90.435 E.00391
G1 X21.124 Y90.435 E2.47389
G1 X20.992 Y90.408 E.00391
G1 X20.965 Y90.276 E.00391
G1 X20.965 Y5.124 E2.47389
G1 X20.992 Y4.992 E.00391
G1 X21.124 Y4.965 E.00391
G1 X106.276 Y4.965 E2.47389
G1 X106.349 Y4.98 E.00217
; Slow Down End
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X106.276 Y4.965 E-.02839
G1 X104.351 Y4.965 E-.73161
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 6/40
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
G17
G3 Z1.4 I1.217 J0 P1  F30000
; object ids of layer 6 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer6 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z1.6 F30000
G1 X160.4 Y8 Z1.6
G1 Z1.2
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z1.6 F30000
G1 X114.002 Y8.498 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z1.6 F30000
G1 X93.502 Y73.11 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z1.6 F30000
G1 X97.11 Y46.302 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.802 E.3747
G1 X90.498 Y28.802 E.068
G1 X90.498 Y22.398 E.21244
G1 X92.548 Y22.398 E.068
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.302 Y22.398 E.068
G1 X99.302 Y28.802 E.21244
G1 X97.252 Y28.802 E.068
G1 X97.252 Y40.098 E.3747
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.41 E.37119
G1 X90.89 Y28.41 E.06299
G1 X90.89 Y22.79 E.17269
G1 X92.94 Y22.79 E.06299
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.91 Y22.79 E.06299
G1 X98.91 Y28.41 E.17269
G1 X96.86 Y28.41 E.06299
G1 X96.86 Y40.49 E.37119
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z1.6 F30000
G1 X35.102 Y45.91 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.802 E.3747
G1 X28.098 Y28.802 E.068
G1 X28.098 Y22.398 E.21244
G1 X30.148 Y22.398 E.068
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.902 Y22.398 E.068
G1 X36.902 Y28.802 E.21244
G1 X34.852 Y28.802 E.068
G1 X34.852 Y40.098 E.3747
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.41 E.37119
G1 X28.49 Y28.41 E.06299
G1 X28.49 Y22.79 E.17269
G1 X30.54 Y22.79 E.06299
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.51 Y22.79 E.06299
G1 X36.51 Y28.41 E.17269
G1 X34.46 Y28.41 E.06299
G1 X34.46 Y40.49 E.37119
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.994 Y53.504 Z1.6 F30000
G1 X33.737 Y73.501 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.7 Y73.501 E.00122
G3 X33.534 Y67.905 I.009 J-2.8 E.28571
G3 X34.514 Y68.018 I.183 J2.731 E.03289
G3 X33.975 Y73.488 I-.804 J2.682 E.25597
G1 X33.797 Y73.498 E.0059
G1 X33.718 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.096 E.00782
G3 X33.553 Y68.297 I.244 J-2.396 E.22021
G3 X34.4 Y68.393 I.054 J3.285 E.02625
G3 X33.936 Y73.098 I-.692 J2.307 E.20389
G1 X33.778 Y73.098 E.00484
; WIPE_START
M204 S10000
G1 X33.464 Y73.096 E-.11948
G1 X33 Y73.007 E-.17946
G1 X32.564 Y72.826 E-.17959
G1 X32.171 Y72.563 E-.17954
G1 X31.981 Y72.373 E-.10193
; WIPE_END
G1 E-.04 F1800
G1 X39.392 Y74.199 Z1.6 F30000
G1 X106.798 Y90.798 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
M73 P48 R17
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X105.718 Y90.631 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40163
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X106.428 Y89.92 E.05187
G1 X106.428 Y89.281 E.03297
G1 X105.281 Y90.428 E.08372
G1 X104.643 Y90.428 E.03297
G1 X106.428 Y88.643 E.13034
G1 X106.428 Y88.004 E.03297
G1 X104.004 Y90.428 E.17697
G1 X103.365 Y90.428 E.03297
G1 X106.428 Y87.365 E.22359
G1 X106.428 Y86.727 E.03297
G1 X102.727 Y90.428 E.27021
G1 X102.088 Y90.428 E.03297
G1 X106.428 Y86.088 E.31684
G1 X106.428 Y85.449 E.03297
G1 X101.449 Y90.428 E.36346
G1 X100.811 Y90.428 E.03297
G1 X106.428 Y84.811 E.41009
G1 X106.428 Y84.172 E.03297
G1 X100.172 Y90.428 E.45671
G1 X99.533 Y90.428 E.03297
G1 X106.428 Y83.533 E.50334
G1 X106.428 Y82.894 E.03297
G1 X98.894 Y90.428 E.54996
G1 X98.256 Y90.428 E.03297
G1 X106.428 Y82.256 E.59659
G1 X106.428 Y81.617 E.03297
G1 X97.617 Y90.428 E.64321
G1 X96.978 Y90.428 E.03297
G1 X106.428 Y80.978 E.68984
G1 X106.428 Y80.34 E.03297
G1 X96.34 Y90.428 E.73646
G1 X95.701 Y90.428 E.03297
G1 X106.428 Y79.701 E.78309
G1 X106.428 Y79.062 E.03297
G1 X95.062 Y90.428 E.82971
G1 X94.424 Y90.428 E.03297
G1 X106.428 Y78.424 E.87633
G1 X106.428 Y77.785 E.03297
G1 X93.785 Y90.428 E.92296
G1 X93.146 Y90.428 E.03297
G1 X106.428 Y77.146 E.96958
G1 X106.428 Y76.507 E.03297
G1 X92.507 Y90.428 E1.01621
G1 X91.869 Y90.428 E.03297
G1 X106.428 Y75.869 E1.06283
G1 X106.428 Y75.23 E.03297
G1 X91.23 Y90.428 E1.10946
G1 X90.591 Y90.428 E.03297
G1 X106.428 Y74.591 E1.15608
G1 X106.428 Y73.953 E.03297
G1 X89.953 Y90.428 E1.20271
G1 X89.314 Y90.428 E.03297
G1 X106.428 Y73.314 E1.24933
G1 X106.428 Y72.675 E.03297
G1 X88.675 Y90.428 E1.29596
G1 X88.037 Y90.428 E.03297
G1 X106.428 Y72.037 E1.34258
G1 X106.428 Y71.398 E.03297
G1 X87.398 Y90.428 E1.3892
G1 X86.759 Y90.428 E.03297
G1 X106.428 Y70.759 E1.43583
G1 X106.428 Y70.12 E.03297
G1 X86.12 Y90.428 E1.48245
G1 X85.482 Y90.428 E.03297
G1 X106.428 Y69.482 E1.52908
G1 X106.428 Y68.843 E.03297
G1 X84.843 Y90.428 E1.5757
G1 X84.204 Y90.428 E.03297
G1 X106.428 Y68.204 E1.62233
G1 X106.428 Y67.566 E.03297
G1 X83.566 Y90.428 E1.66895
G1 X82.927 Y90.428 E.03297
G1 X106.428 Y66.927 E1.71558
G1 X106.428 Y66.288 E.03297
G1 X82.288 Y90.428 E1.7622
G1 X81.65 Y90.428 E.03297
G1 X106.428 Y65.65 E1.80883
G1 X106.428 Y65.011 E.03297
G1 X81.011 Y90.428 E1.85545
G1 X80.372 Y90.428 E.03297
G1 X106.428 Y64.372 E1.90208
G1 X106.428 Y63.733 E.03297
G1 X79.733 Y90.428 E1.9487
G1 X79.095 Y90.428 E.03297
G1 X106.428 Y63.095 E1.99532
G1 X106.428 Y62.456 E.03297
G1 X78.456 Y90.428 E2.04195
G1 X77.817 Y90.428 E.03297
G1 X106.428 Y61.817 E2.08857
G1 X106.428 Y61.179 E.03297
G1 X77.179 Y90.428 E2.1352
G1 X76.54 Y90.428 E.03297
G1 X93.097 Y73.872 E1.20862
G1 X92.458 Y73.872 E.03297
G1 X75.901 Y90.428 E1.20862
G1 X75.263 Y90.428 E.03297
G1 X91.384 Y74.307 E1.17687
G1 X90.334 Y74.941 E.06333
G1 X90.34 Y74.712 E.01183
G1 X74.624 Y90.428 E1.14727
G1 X73.985 Y90.428 E.03297
G1 X90.357 Y74.056 E1.19515
G1 X90.362 Y73.872 E.00952
G1 X89.903 Y73.872 E.0237
G1 X73.346 Y90.428 E1.20862
G1 X72.708 Y90.428 E.03297
G1 X89.264 Y73.872 E1.20862
G1 X88.626 Y73.872 E.03297
G1 X72.069 Y90.428 E1.20862
G1 X71.43 Y90.428 E.03297
G1 X87.987 Y73.872 E1.20862
G1 X87.348 Y73.872 E.03297
G1 X70.792 Y90.428 E1.20862
G1 X70.153 Y90.428 E.03297
G1 X86.71 Y73.872 E1.20862
G1 X86.071 Y73.872 E.03297
G1 X69.514 Y90.428 E1.20862
G1 X68.876 Y90.428 E.03297
G1 X85.432 Y73.872 E1.20862
G1 X84.793 Y73.872 E.03297
G1 X68.237 Y90.428 E1.20862
G1 X67.598 Y90.428 E.03297
G1 X84.155 Y73.872 E1.20862
G1 X83.528 Y73.872 E.03233
G1 X83.528 Y73.859 E.00063
G1 X66.959 Y90.428 E1.20951
G1 X66.321 Y90.428 E.03297
G1 X83.528 Y73.221 E1.25614
G1 X83.528 Y72.582 E.03297
G1 X65.682 Y90.428 E1.30276
G1 X65.043 Y90.428 E.03297
G1 X83.528 Y71.943 E1.34939
G1 X83.528 Y71.305 E.03297
G1 X64.405 Y90.428 E1.39601
G1 X63.766 Y90.428 E.03297
G1 X83.528 Y70.666 E1.44264
G1 X83.528 Y70.027 E.03297
G1 X63.127 Y90.428 E1.48926
G1 X62.489 Y90.428 E.03297
G1 X83.528 Y69.389 E1.53589
G1 X83.528 Y68.75 E.03297
G1 X61.85 Y90.428 E1.58251
G1 X61.211 Y90.428 E.03297
G1 X83.528 Y68.111 E1.62913
G1 X83.528 Y67.528 E.03008
G1 X84.111 Y67.528 E.03008
G1 X106.428 Y45.211 E1.62913
G1 X106.428 Y45.85 E.03297
G1 X84.75 Y67.528 E1.58251
G1 X85.389 Y67.528 E.03297
G1 X106.428 Y46.489 E1.53589
G1 X106.428 Y47.127 E.03297
G1 X86.027 Y67.528 E1.48926
G1 X86.666 Y67.528 E.03297
G1 X106.428 Y47.766 E1.44264
G1 X106.428 Y48.405 E.03297
G1 X87.305 Y67.528 E1.39601
G1 X87.943 Y67.528 E.03297
G1 X106.428 Y49.043 E1.34939
G1 X106.428 Y49.682 E.03297
G1 X88.582 Y67.528 E1.30276
G1 X89.221 Y67.528 E.03297
G1 X106.428 Y50.321 E1.25614
G1 X106.428 Y50.959 E.03297
G1 X90.408 Y66.98 E1.16947
G1 X90.727 Y67.299 E.02331
G1 X106.428 Y51.598 E1.14616
G1 X106.428 Y52.237 E.03297
G1 X91.137 Y67.528 E1.11626
G1 X91.776 Y67.528 E.03297
G1 X106.428 Y52.876 E1.06964
G1 X106.428 Y53.514 E.03297
M73 P49 R17
G1 X92.414 Y67.528 E1.02301
G1 X93.053 Y67.528 E.03297
G1 X106.428 Y54.153 E.97639
G1 X106.428 Y54.792 E.03297
G1 X93.692 Y67.528 E.92976
G1 X93.872 Y67.528 E.00929
G1 X93.872 Y67.987 E.02367
G1 X106.428 Y55.43 E.91662
G1 X106.428 Y56.069 E.03297
G1 X93.872 Y68.626 E.91662
G1 X93.872 Y69.264 E.03297
G1 X106.428 Y56.708 E.91662
G1 X106.428 Y57.346 E.03297
G1 X93.872 Y69.903 E.91662
G1 X93.872 Y70.542 E.03297
G1 X106.428 Y57.985 E.91662
G1 X106.428 Y58.624 E.03297
G1 X93.872 Y71.18 E.91662
G1 X93.872 Y71.819 E.03297
G1 X106.428 Y59.263 E.91662
G1 X106.428 Y59.901 E.03297
G1 X93.872 Y72.458 E.91662
M73 P49 R16
G1 X93.872 Y73.097 E.03297
G1 X106.631 Y60.337 E.9314
G1 X90.373 Y67.495 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.44194
; LAYER_HEIGHT: 0.2
G1 F12000
G1 X90.348 Y67.538 E.00162
G1 X90.273 Y67.495 E.00281
G1 X90.296 Y67.482 E.00086
; WIPE_START
G1 X90.273 Y67.495 E-.12323
G1 X90.348 Y67.538 E-.40368
G1 X90.373 Y67.495 E-.23309
; WIPE_END
G1 E-.04 F1800
G1 X90.954 Y74.002 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; LINE_WIDTH: 0.63578
G1 F10626.455
G3 X90.857 Y73.938 I-.069 J-.001 E.01428
; WIPE_START
G1 X90.806 Y74.002 E-.20491
G1 X90.843 Y74.066 E-.18503
G1 X90.917 Y74.066 E-.18503
G1 X90.954 Y74.002 E-.18503
; WIPE_END
G1 E-.04 F1800
G1 X91.221 Y66.374 Z1.6 F30000
G1 X92.131 Y40.348 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40163
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X42.05 Y90.428 E3.65585
G1 X42.689 Y90.428 E.03297
G1 X91.928 Y41.189 E3.59444
G1 X91.928 Y41.827 E.03297
G1 X43.327 Y90.428 E3.54782
G1 X43.966 Y90.428 E.03297
G1 X91.928 Y42.466 E3.50119
G1 X91.928 Y43.105 E.03297
G1 X44.605 Y90.428 E3.45457
G1 X45.244 Y90.428 E.03297
G1 X91.928 Y43.744 E3.40794
G1 X91.928 Y44.382 E.03297
G1 X45.882 Y90.428 E3.36132
G1 X46.521 Y90.428 E.03297
G1 X91.928 Y45.021 E3.31469
G1 X91.928 Y45.66 E.03297
G1 X47.16 Y90.428 E3.26807
G1 X47.798 Y90.428 E.03297
G1 X91.928 Y46.298 E3.22144
G1 X91.928 Y46.672 E.01927
G1 X92.194 Y46.672 E.0137
G1 X48.437 Y90.428 E3.19419
G1 X49.076 Y90.428 E.03297
G1 X92.832 Y46.672 E3.19419
M73 P50 R16
G1 X93.471 Y46.672 E.03297
G1 X49.714 Y90.428 E3.19419
G1 X50.353 Y90.428 E.03297
G1 X94.11 Y46.672 E3.19419
G1 X94.749 Y46.672 E.03297
G1 X50.992 Y90.428 E3.19419
G1 X51.631 Y90.428 E.03297
G1 X95.387 Y46.672 E3.19419
G1 X96.026 Y46.672 E.03297
G1 X52.269 Y90.428 E3.19419
G1 X52.908 Y90.428 E.03297
G1 X96.665 Y46.672 E3.19419
G1 X97.303 Y46.672 E.03297
G1 X53.344 Y90.631 E3.20897
G1 X60.37 Y90.631 F30000
G1 F3000
G1 X106.428 Y44.572 E3.36222
G1 X106.428 Y43.934 E.03297
G1 X59.934 Y90.428 E3.39406
G1 X59.295 Y90.428 E.03297
G1 X106.428 Y43.295 E3.44069
G1 X106.428 Y42.656 E.03297
G1 X58.656 Y90.428 E3.48731
G1 X58.018 Y90.428 E.03297
G1 X106.428 Y42.018 E3.53394
G1 X106.428 Y41.379 E.03297
G1 X57.379 Y90.428 E3.58056
G1 X56.74 Y90.428 E.03297
G1 X106.428 Y40.74 E3.62718
G1 X106.428 Y40.102 E.03297
G1 X56.101 Y90.428 E3.67381
G1 X55.463 Y90.428 E.03297
G1 X106.428 Y39.463 E3.72043
G1 X106.428 Y38.824 E.03297
G1 X54.824 Y90.428 E3.76706
G1 X54.185 Y90.428 E.03297
G1 X106.428 Y38.185 E3.81368
G1 X106.428 Y37.547 E.03297
G1 X97.872 Y46.103 E.62462
G1 X97.872 Y45.465 E.03297
G1 X106.428 Y36.908 E.62462
G1 X106.428 Y36.269 E.03297
G1 X97.872 Y44.826 E.62462
G1 X97.872 Y44.187 E.03297
G1 X106.428 Y35.631 E.62462
G1 X106.428 Y34.992 E.03297
G1 X97.872 Y43.549 E.62462
G1 X97.872 Y42.91 E.03297
G1 X106.428 Y34.353 E.62462
G1 X106.428 Y33.714 E.03297
G1 X97.872 Y42.271 E.62462
G1 X97.872 Y41.632 E.03297
G1 X106.428 Y33.076 E.62462
G1 X106.428 Y32.437 E.03297
G1 X97.872 Y40.994 E.62462
G1 X97.872 Y40.355 E.03297
G1 X106.428 Y31.798 E.62462
G1 X106.428 Y31.16 E.03297
G1 X97.86 Y39.728 E.6255
G1 X97.622 Y39.728 E.01228
G1 X97.622 Y39.328 E.02068
G1 X106.428 Y30.521 E.64287
G1 X106.428 Y29.882 E.03297
G1 X97.622 Y38.689 E.64287
G1 X97.622 Y38.05 E.03297
G1 X106.428 Y29.244 E.64287
G1 X106.428 Y28.605 E.03297
G1 X97.622 Y37.411 E.64287
G1 X97.622 Y36.773 E.03297
G1 X106.428 Y27.966 E.64287
G1 X106.428 Y27.327 E.03297
G1 X97.622 Y36.134 E.64287
G1 X97.622 Y35.495 E.03297
G1 X106.428 Y26.689 E.64287
G1 X106.428 Y26.05 E.03297
G1 X97.622 Y34.857 E.64287
G1 X97.622 Y34.218 E.03297
G1 X106.428 Y25.411 E.64287
G1 X106.428 Y24.773 E.03297
G1 X97.622 Y33.579 E.64287
G1 X97.622 Y32.941 E.03297
G1 X106.428 Y24.134 E.64287
G1 X106.428 Y23.495 E.03297
G1 X97.622 Y32.302 E.64287
G1 X97.622 Y31.663 E.03297
G1 X106.428 Y22.857 E.64287
M73 P51 R16
G1 X106.428 Y22.218 E.03297
G1 X97.622 Y31.024 E.64287
G1 X97.622 Y30.386 E.03297
G1 X99.038 Y28.969 E.10341
G1 X97.789 Y29.272 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.5761
; LAYER_HEIGHT: 0.2
G1 F11815.898
G3 X97.696 Y29.214 I-.063 J-.003 E.01131
; WIPE_START
G1 X97.656 Y29.272 E-.1975
G1 X97.689 Y29.33 E-.1875
G1 X97.756 Y29.33 E-.1875
G1 X97.789 Y29.272 E-.1875
; WIPE_END
G1 E-.04 F1800
G1 X99.692 Y23.114 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; Slow Down Start
; LINE_WIDTH: 0.41601
G1 F3000;_EXTRUDE_SET_SPEED
G1 X100.118 Y23.54 E.01829
G1 X99.692 Y24.192 E.02368
G1 X99.692 Y23.174 E.03095
; Slow Down End
G1 X106.631 Y21.377 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40163
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X99.672 Y28.336 E.50801
G1 X99.672 Y27.697 E.03297
G1 X106.428 Y20.94 E.49323
G1 X106.428 Y20.302 E.03297
G1 X99.672 Y27.058 E.49322
G1 X99.672 Y26.42 E.03297
G1 X106.428 Y19.663 E.49322
G1 X106.428 Y19.024 E.03297
G1 X99.672 Y25.781 E.49322
G1 X99.672 Y25.142 E.03297
G1 X106.428 Y18.386 E.49322
M73 P52 R16
G1 X106.428 Y17.747 E.03297
G1 X100.559 Y23.617 E.42848
G1 X100.645 Y23.485 E.00813
G1 X100.348 Y23.188 E.02164
G1 X106.428 Y17.108 E.44384
G1 X106.428 Y16.47 E.03297
G1 X100.029 Y22.869 E.46715
G1 X99.826 Y22.666 E.01478
G1 X99.672 Y22.644 E.00806
G1 X99.672 Y22.587 E.00293
G1 X106.428 Y15.831 E.49323
G1 X106.428 Y15.192 E.03297
M73 P52 R15
G1 X99.592 Y22.028 E.49903
G1 X98.953 Y22.028 E.03297
G1 X106.428 Y14.553 E.54566
G1 X106.428 Y13.915 E.03297
G1 X98.315 Y22.028 E.59228
G1 X97.676 Y22.028 E.03297
G1 X106.428 Y13.276 E.63891
G1 X106.428 Y12.637 E.03297
G1 X97.337 Y21.728 E.66363
G1 X96.699 Y21.728 E.03297
G1 X106.428 Y11.999 E.71026
G1 X106.428 Y11.36 E.03297
G1 X96.06 Y21.728 E.75688
G1 X95.421 Y21.728 E.03297
G1 X106.428 Y10.721 E.8035
G1 X106.428 Y10.083 E.03297
G1 X94.783 Y21.728 E.85013
G1 X94.144 Y21.728 E.03297
G1 X106.428 Y9.444 E.89675
G1 X106.428 Y8.805 E.03297
G1 X93.505 Y21.728 E.94338
G1 X92.866 Y21.728 E.03297
G1 X106.428 Y8.166 E.99
G1 X106.428 Y7.528 E.03297
G1 X91.928 Y22.028 E1.05853
G1 X91.289 Y22.028 E.03297
G1 X106.428 Y6.889 E1.10515
G1 X106.428 Y6.25 E.03297
G1 X90.65 Y22.028 E1.15178
G1 X90.128 Y22.028 E.02695
G1 X90.128 Y22.55 E.02695
G1 X22.25 Y90.428 E4.95503
G1 X22.889 Y90.428 E.03297
G1 X90.128 Y23.189 E4.9084
G1 X90.128 Y23.828 E.03297
G1 X23.528 Y90.428 E4.86178
G1 X24.166 Y90.428 E.03297
G1 X90.128 Y24.466 E4.81516
G1 X90.128 Y25.105 E.03297
G1 X24.805 Y90.428 E4.76853
G1 X25.444 Y90.428 E.03297
G1 X89.337 Y26.535 E4.66416
G1 X89.14 Y26.836 E.0186
G1 X89.407 Y27.104 E.01952
G1 X26.083 Y90.428 E4.62264
G1 X26.721 Y90.428 E.03297
G1 X89.727 Y27.423 E4.59933
G1 X89.961 Y27.658 E.01712
G1 X90.113 Y27.675 E.00792
G1 X27.36 Y90.428 E4.58095
G1 X27.999 Y90.428 E.03297
G1 X90.128 Y28.299 E4.53541
G1 X90.128 Y28.937 E.03297
G1 X28.637 Y90.428 E4.48878
G1 X29.276 Y90.428 E.03297
G1 X90.533 Y29.172 E4.47168
G1 X91.171 Y29.172 E.03297
G1 X29.915 Y90.428 E4.47168
G1 X30.553 Y90.428 E.03297
G1 X91.758 Y29.224 E4.46786
G1 X91.729 Y29.604 E.01969
G1 X92.05 Y29.57 E.01667
G1 X31.192 Y90.428 E4.4426
G1 X31.831 Y90.428 E.03297
G1 X92.178 Y30.081 E4.40531
G1 X92.178 Y30.72 E.03297
G1 X32.47 Y90.428 E4.35868
G1 X33.108 Y90.428 E.03297
G1 X92.178 Y31.358 E4.31206
G1 X92.178 Y31.997 E.03297
G1 X33.747 Y90.428 E4.26543
G1 X34.386 Y90.428 E.03297
G1 X92.178 Y32.636 E4.21881
G1 X92.178 Y33.274 E.03297
G1 X35.024 Y90.428 E4.17218
G1 X35.663 Y90.428 E.03297
G1 X92.178 Y33.913 E4.12556
G1 X92.178 Y34.552 E.03297
G1 X36.302 Y90.428 E4.07894
G1 X36.94 Y90.428 E.03297
G1 X92.178 Y35.19 E4.03231
G1 X92.178 Y35.829 E.03297
G1 X37.579 Y90.428 E3.98569
G1 X38.218 Y90.428 E.03297
G1 X92.178 Y36.468 E3.93906
G1 X92.178 Y37.107 E.03297
G1 X38.857 Y90.428 E3.89244
G1 X39.495 Y90.428 E.03297
G1 X92.178 Y37.745 E3.84581
G1 X92.178 Y38.384 E.03297
M73 P53 R15
G1 X40.134 Y90.428 E3.79919
G1 X40.773 Y90.428 E.03297
G1 X92.178 Y39.023 E3.75256
G1 X92.178 Y39.661 E.03297
G1 X41.209 Y90.631 E3.72072
G1 X21.409 Y90.631 F30000
G1 F3000
G1 X106.428 Y5.612 E6.20632
G1 X106.428 Y4.973 E.03297
G1 X20.972 Y90.428 E6.23821
G1 X20.972 Y89.791 E.03291
G1 X105.791 Y4.972 E6.19172
G1 X105.152 Y4.972 E.03297
G1 X20.972 Y89.152 E6.14509
G1 X20.972 Y88.513 E.03297
G1 X104.513 Y4.972 E6.09847
G1 X103.875 Y4.972 E.03297
G1 X20.972 Y87.875 E6.05184
G1 X20.972 Y87.236 E.03297
G1 X34.421 Y73.786 E.98182
G3 X33.696 Y73.873 I-.758 J-3.275 E.03777
G1 X20.972 Y86.597 E.92889
G1 X20.972 Y85.959 E.03297
G1 X33.114 Y73.817 E.88635
G3 X32.614 Y73.677 I.754 J-3.666 E.02678
G1 X20.972 Y85.32 E.8499
G1 X20.972 Y84.681 E.03297
G1 X32.173 Y73.48 E.81771
G3 X31.787 Y73.227 I1.089 J-2.084 E.02385
G1 X20.972 Y84.043 E.78953
G1 X20.972 Y83.404 E.03297
G1 X31.445 Y72.931 E.76453
G3 X31.152 Y72.585 I1.606 J-1.655 E.02343
G1 X20.972 Y82.765 E.74317
G1 X20.972 Y82.126 E.03297
G1 X30.902 Y72.196 E.7249
G1 X30.798 Y71.975 E.01261
G3 X30.71 Y71.75 I1.102 J-.559 E.01252
G1 X20.972 Y81.488 E.71087
G1 X20.972 Y80.849 E.03297
G1 X30.577 Y71.244 E.70117
G1 X30.544 Y71.019 E.01172
G3 X30.529 Y70.653 I6.519 J-.436 E.01894
G1 X20.972 Y80.21 E.69771
G1 X20.972 Y79.572 E.03297
G1 X30.63 Y69.913 E.70506
G3 X32.913 Y67.63 I3.104 J.821 E.17463
G1 X95.572 Y4.972 E4.57401
G1 X96.21 Y4.972 E.03297
G1 X33.645 Y67.537 E4.56721
G3 X34.244 Y67.577 I.153 J2.22 E.03107
G1 X96.849 Y4.972 E4.57013
G1 X97.488 Y4.972 E.03297
G1 X34.75 Y67.71 E4.57982
M73 P54 R15
G3 X35.196 Y67.902 I-1.623 J4.383 E.0251
G1 X98.126 Y4.972 E4.59386
G1 X98.765 Y4.972 E.03297
G1 X35.585 Y68.152 E4.61212
G3 X35.931 Y68.445 I-1.355 J1.954 E.02343
G1 X99.404 Y4.972 E4.63348
G1 X100.043 Y4.972 E.03297
G1 X36.227 Y68.787 E4.65848
G3 X36.48 Y69.173 I-1.835 J1.477 E.02385
G1 X100.681 Y4.972 E4.68666
G1 X101.32 Y4.972 E.03297
G1 X36.677 Y69.614 E4.71885
G3 X36.817 Y70.114 I-3.526 J1.253 E.02678
G1 X101.959 Y4.972 E4.7553
G1 X102.597 Y4.972 E.03297
G1 X36.873 Y70.696 E4.79784
G3 X36.786 Y71.422 I-2.479 J.072 E.03784
G1 X103.439 Y4.769 E4.86556
; WIPE_START
G1 X102.024 Y6.183 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.108 Y12.734 Z1.6 F30000
G1 X90.105 Y26.12 Z1.6
G1 Z1.2
G1 E.8 F1800
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.42253
; LAYER_HEIGHT: 0.2
G1 F3000;_EXTRUDE_SET_SPEED
G1 X90.105 Y27.215 E.03386
M73 P55 R15
G1 X89.671 Y26.781 E.01895
G1 X90.072 Y26.17 E.0226
; Slow Down End
G1 X37.231 Y23.967 F30000
; LINE_WIDTH: 0.38292
G1 F12000
G1 X37.21 Y24.003 E.00118
G1 X37.146 Y23.967 E.00204
G1 X37.158 Y23.96 E.00038
G1 X37.069 Y28.346 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40163
; LAYER_HEIGHT: 0.4
M73 P55 R14
G1 F3000
G1 X60.443 Y4.972 E1.70627
G1 X59.804 Y4.972 E.03297
G1 X37.272 Y27.504 E1.64486
G1 X37.272 Y26.866 E.03297
G1 X59.166 Y4.972 E1.59824
G1 X58.527 Y4.972 E.03297
G1 X37.272 Y26.227 E1.55161
G1 X37.272 Y25.588 E.03297
G1 X57.888 Y4.972 E1.50499
G1 X57.25 Y4.972 E.03297
G1 X37.272 Y24.95 E1.45836
G1 X37.272 Y24.398 E.02849
G1 X37.461 Y24.122 E.01725
G1 X56.611 Y4.972 E1.39795
G1 X55.972 Y4.972 E.03297
G1 X37.307 Y23.637 E1.36255
M73 P56 R14
G1 X37.272 Y23.598 E.00271
G1 X37.272 Y23.033 E.02914
G1 X55.333 Y4.972 E1.31849
G1 X54.695 Y4.972 E.03297
G1 X37.272 Y22.395 E1.27187
G1 X37.272 Y22.028 E.01891
G1 X36.999 Y22.028 E.01405
G1 X54.056 Y4.972 E1.24512
G1 X53.417 Y4.972 E.03297
G1 X36.361 Y22.028 E1.24512
G1 X35.722 Y22.028 E.03297
G1 X52.779 Y4.972 E1.24512
G1 X52.14 Y4.972 E.03297
G1 X35.222 Y21.89 E1.23502
G1 X35.222 Y21.728 E.00834
G1 X34.745 Y21.728 E.02463
G1 X51.501 Y4.972 E1.22322
G1 X50.863 Y4.972 E.03297
G1 X34.106 Y21.728 E1.22322
G1 X33.467 Y21.728 E.03297
G1 X50.224 Y4.972 E1.22322
G1 X49.585 Y4.972 E.03297
G1 X32.829 Y21.728 E1.22322
G1 X32.19 Y21.728 E.03297
G1 X48.946 Y4.972 E1.22322
G1 X48.308 Y4.972 E.03297
G1 X31.551 Y21.728 E1.22322
G1 X30.912 Y21.728 E.03297
G1 X47.669 Y4.972 E1.22322
G1 X47.03 Y4.972 E.03297
G1 X30.274 Y21.728 E1.22322
G1 X29.778 Y21.728 E.02557
G1 X29.778 Y22.028 E.01549
G1 X29.335 Y22.028 E.02288
G1 X46.392 Y4.972 E1.24512
G1 X45.753 Y4.972 E.03297
G1 X28.494 Y22.231 E1.2599
G1 X27.931 Y22.794 F30000
G1 F3000
G1 X20.972 Y29.753 E.50801
G1 X20.972 Y30.392 E.03297
G1 X27.728 Y23.635 E.49323
M73 P57 R14
G1 X27.728 Y24.072 E.02255
G1 X27.306 Y24.696 E.03891
G1 X20.972 Y31.03 E.46238
G1 X20.972 Y31.669 E.03297
G1 X26.768 Y25.872 E.42314
G1 X27.088 Y26.192 E.02331
G1 X20.972 Y32.308 E.44646
G1 X20.972 Y32.946 E.03297
G1 X27.407 Y26.511 E.46977
G1 X27.456 Y26.56 E.00355
G1 X27.728 Y26.537 E.01412
G1 X27.728 Y26.829 E.01506
G1 X20.972 Y33.585 E.49323
G1 X20.972 Y34.224 E.03297
G1 X27.728 Y27.467 E.49323
G1 X27.728 Y28.106 E.03297
G1 X20.972 Y34.863 E.49323
G1 X20.972 Y35.501 E.03297
G1 X27.728 Y28.745 E.49323
G1 X27.728 Y29.172 E.02205
G1 X27.94 Y29.172 E.01092
G1 X20.972 Y36.14 E.50867
M73 P58 R14
G1 X20.972 Y36.779 E.03297
G1 X28.579 Y29.172 E.5553
G1 X29.217 Y29.172 E.03297
G1 X20.972 Y37.417 E.60192
G1 X20.972 Y38.056 E.03297
G1 X29.778 Y29.249 E.64287
G1 X29.778 Y29.888 E.03297
G1 X20.972 Y38.695 E.64287
G1 X20.972 Y39.333 E.03297
G1 X29.778 Y30.527 E.64287
G1 X29.778 Y31.166 E.03297
G1 X20.972 Y39.972 E.64287
G1 X20.972 Y40.611 E.03297
G1 X29.778 Y31.804 E.64287
G1 X29.778 Y32.443 E.03297
G1 X20.972 Y41.25 E.64287
G1 X20.972 Y41.888 E.03297
G1 X29.778 Y33.082 E.64287
G1 X29.778 Y33.72 E.03297
G1 X20.972 Y42.527 E.64287
G1 X20.972 Y43.166 E.03297
G1 X29.778 Y34.359 E.64287
G1 X29.778 Y34.998 E.03297
G1 X20.972 Y43.804 E.64287
G1 X20.972 Y44.443 E.03297
G1 X29.778 Y35.636 E.64287
G1 X29.778 Y36.275 E.03297
G1 X20.972 Y45.082 E.64287
G1 X20.972 Y45.72 E.03297
G1 X29.778 Y36.914 E.64287
G1 X29.778 Y37.553 E.03297
G1 X20.972 Y46.359 E.64287
G1 X20.972 Y46.998 E.03297
G1 X29.778 Y38.191 E.64287
G1 X29.778 Y38.83 E.03297
G1 X20.972 Y47.637 E.64287
G1 X20.972 Y48.275 E.03297
G1 X29.778 Y39.469 E.64287
G1 X29.778 Y39.728 E.0134
G1 X29.528 Y39.728 E.0129
G1 X29.528 Y40.357 E.03247
M73 P58 R13
G1 X20.972 Y48.914 E.62462
G1 X20.972 Y49.553 E.03297
G1 X29.528 Y40.996 E.62462
G1 X29.528 Y41.635 E.03297
G1 X20.972 Y50.191 E.62462
G1 X20.972 Y50.83 E.03297
G1 X29.528 Y42.273 E.62462
G1 X29.528 Y42.912 E.03297
G1 X20.972 Y51.469 E.62462
G1 X20.972 Y52.107 E.03297
G1 X29.528 Y43.551 E.62462
G1 X29.528 Y44.19 E.03297
G1 X20.972 Y52.746 E.62462
G1 X20.972 Y53.385 E.03297
G1 X29.528 Y44.828 E.62462
G1 X29.528 Y45.467 E.03297
G1 X20.972 Y54.024 E.62462
G1 X20.972 Y54.662 E.03297
G1 X29.528 Y46.106 E.62462
G1 X29.528 Y46.672 E.02922
G1 X29.601 Y46.672 E.00375
G1 X20.972 Y55.301 E.62993
G1 X20.972 Y55.94 E.03297
G1 X30.24 Y46.672 E.67655
G1 X30.878 Y46.672 E.03297
G1 X20.972 Y56.578 E.72318
G1 X20.972 Y57.217 E.03297
G1 X31.517 Y46.672 E.7698
G1 X32.156 Y46.672 E.03297
G1 X20.972 Y57.856 E.81643
G1 X20.972 Y58.494 E.03297
G1 X32.794 Y46.672 E.86305
G1 X33.433 Y46.672 E.03297
G1 X20.972 Y59.133 E.90968
G1 X20.972 Y59.772 E.03297
G1 X34.072 Y46.672 E.9563
G1 X34.711 Y46.672 E.03297
G1 X20.769 Y60.613 E1.01771
G1 X20.769 Y79.135 F30000
G1 F3000
G1 X94.933 Y4.972 E5.41388
G1 X94.294 Y4.972 E.03297
G1 X20.972 Y78.294 E5.35247
G1 X20.972 Y77.656 E.03297
G1 X93.656 Y4.972 E5.30585
G1 X93.017 Y4.972 E.03297
G1 X20.972 Y77.017 E5.25923
G1 X20.972 Y76.378 E.03297
G1 X92.378 Y4.972 E5.2126
G1 X91.739 Y4.972 E.03297
G1 X20.972 Y75.739 E5.16598
G1 X20.972 Y75.101 E.03297
G1 X91.101 Y4.972 E5.11935
G1 X90.462 Y4.972 E.03297
G1 X20.972 Y74.462 E5.07273
G1 X20.972 Y73.823 E.03297
G1 X89.823 Y4.972 E5.0261
G1 X89.185 Y4.972 E.03297
G1 X20.972 Y73.185 E4.97948
G1 X20.972 Y72.546 E.03297
G1 X88.546 Y4.972 E4.93285
G1 X87.907 Y4.972 E.03297
G1 X20.972 Y71.907 E4.88623
G1 X20.972 Y71.268 E.03297
G1 X87.269 Y4.972 E4.8396
G1 X86.63 Y4.972 E.03297
G1 X20.972 Y70.63 E4.79298
G1 X20.972 Y69.991 E.03297
G1 X85.991 Y4.972 E4.74635
G1 X85.352 Y4.972 E.03297
G1 X20.972 Y69.352 E4.69973
G1 X20.972 Y68.714 E.03297
G1 X84.714 Y4.972 E4.65311
G1 X84.075 Y4.972 E.03297
G1 X20.972 Y68.075 E4.60648
G1 X20.972 Y67.436 E.03297
G1 X83.436 Y4.972 E4.55986
G1 X82.798 Y4.972 E.03297
G1 X20.972 Y66.798 E4.51323
G1 X20.972 Y66.159 E.03297
G1 X82.159 Y4.972 E4.46661
G1 X81.52 Y4.972 E.03297
G1 X20.972 Y65.52 E4.41998
G1 X20.972 Y64.881 E.03297
G1 X80.881 Y4.972 E4.37336
G1 X80.243 Y4.972 E.03297
G1 X20.972 Y64.243 E4.32673
G1 X20.972 Y63.604 E.03297
G1 X79.604 Y4.972 E4.28011
G1 X78.965 Y4.972 E.03297
M73 P59 R13
G1 X20.972 Y62.965 E4.23348
G1 X20.972 Y62.327 E.03297
G1 X78.327 Y4.972 E4.18686
G1 X77.688 Y4.972 E.03297
G1 X20.972 Y61.688 E4.14024
G1 X20.972 Y61.049 E.03297
G1 X77.049 Y4.972 E4.09361
G1 X76.411 Y4.972 E.03297
G1 X35.472 Y45.911 E2.9885
G1 X35.472 Y45.272 E.03297
G1 X75.772 Y4.972 E2.94188
G1 X75.133 Y4.972 E.03297
G1 X35.472 Y44.633 E2.89525
G1 X35.472 Y43.994 E.03297
G1 X74.494 Y4.972 E2.84863
G1 X73.856 Y4.972 E.03297
G1 X35.472 Y43.356 E2.802
G1 X35.472 Y42.717 E.03297
G1 X73.217 Y4.972 E2.75538
G1 X72.578 Y4.972 E.03297
G1 X35.472 Y42.078 E2.70875
G1 X35.472 Y41.44 E.03297
G1 X71.94 Y4.972 E2.66213
G1 X71.301 Y4.972 E.03297
G1 X35.472 Y40.801 E2.6155
G1 X35.472 Y40.162 E.03297
G1 X70.662 Y4.972 E2.56888
G1 X70.024 Y4.972 E.03297
G1 X35.267 Y39.728 E2.5372
G1 X35.222 Y39.728 E.00234
G1 X35.222 Y39.135 E.03063
G1 X69.385 Y4.972 E2.49388
G1 X68.746 Y4.972 E.03297
G1 X35.222 Y38.496 E2.44726
G1 X35.222 Y37.857 E.03297
G1 X68.107 Y4.972 E2.40063
G1 X67.469 Y4.972 E.03297
G1 X35.222 Y37.219 E2.35401
G1 X35.222 Y36.58 E.03297
G1 X66.83 Y4.972 E2.30738
G1 X66.191 Y4.972 E.03297
G1 X35.222 Y35.941 E2.26076
G1 X35.222 Y35.303 E.03297
G1 X65.553 Y4.972 E2.21413
G1 X64.914 Y4.972 E.03297
G1 X35.222 Y34.664 E2.16751
G1 X35.222 Y34.025 E.03297
G1 X64.275 Y4.972 E2.12088
G1 X63.637 Y4.972 E.03297
G1 X35.222 Y33.387 E2.07426
G1 X35.222 Y32.748 E.03297
G1 X62.998 Y4.972 E2.02763
G1 X62.359 Y4.972 E.03297
G1 X35.222 Y32.109 E1.98101
G1 X35.222 Y31.47 E.03297
G1 X61.72 Y4.972 E1.93438
G1 X61.082 Y4.972 E.03297
G1 X35.222 Y30.832 E1.88776
G1 X35.222 Y30.193 E.03297
G1 X36.446 Y28.969 E.08934
M73 P60 R13
G1 X35.401 Y29.282 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.59558
; LAYER_HEIGHT: 0.2
G1 F11399.414
G3 X35.306 Y29.222 I-.065 J-.002 E.01224
; WIPE_START
G1 X35.263 Y29.282 E-.20005
G1 X35.297 Y29.342 E-.18665
G1 X35.366 Y29.342 E-.18664
G1 X35.401 Y29.282 E-.18665
; WIPE_END
G1 E-.04 F1800
G1 X28.751 Y25.536 Z1.6 F30000
G1 X27.678 Y24.932 Z1.6
G1 Z1.2
G1 E.8 F1800
; Slow Down Start
; LINE_WIDTH: 0.47502
G1 F3000;_EXTRUDE_SET_SPEED
G1 X27.678 Y26.098 E.04105
G1 X27.623 Y26.103 E.00197
G1 X27.183 Y25.664 E.02187
G1 X27.645 Y24.982 E.02898
; Slow Down End
G1 X20.769 Y29.317 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40163
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X45.114 Y4.972 E1.77716
G1 X44.476 Y4.972 E.03297
G1 X20.972 Y28.476 E1.71576
M73 P61 R13
G1 X20.972 Y27.837 E.03297
G1 X43.837 Y4.972 E1.66913
G1 X43.198 Y4.972 E.03297
G1 X20.972 Y27.198 E1.62251
G1 X20.972 Y26.559 E.03297
G1 X42.559 Y4.972 E1.57588
M73 P61 R12
G1 X41.921 Y4.972 E.03297
G1 X20.972 Y25.921 E1.52926
G1 X20.972 Y25.282 E.03297
G1 X41.282 Y4.972 E1.48263
G1 X40.643 Y4.972 E.03297
G1 X20.972 Y24.643 E1.43601
G1 X20.972 Y24.005 E.03297
G1 X40.005 Y4.972 E1.38938
G1 X39.366 Y4.972 E.03297
G1 X20.972 Y23.366 E1.34276
G1 X20.972 Y22.727 E.03297
G1 X38.727 Y4.972 E1.29614
G1 X38.088 Y4.972 E.03297
G1 X20.972 Y22.089 E1.24951
G1 X20.972 Y21.45 E.03297
G1 X37.45 Y4.972 E1.20289
G1 X36.811 Y4.972 E.03297
G1 X20.972 Y20.811 E1.15626
M73 P62 R12
G1 X20.972 Y20.172 E.03297
G1 X36.172 Y4.972 E1.10964
G1 X35.534 Y4.972 E.03297
G1 X20.972 Y19.534 E1.06301
G1 X20.972 Y18.895 E.03297
G1 X34.895 Y4.972 E1.01639
G1 X34.256 Y4.972 E.03297
G1 X20.972 Y18.256 E.96976
G1 X20.972 Y17.618 E.03297
G1 X33.618 Y4.972 E.92314
G1 X32.979 Y4.972 E.03297
G1 X20.972 Y16.979 E.87651
G1 X20.972 Y16.34 E.03297
G1 X32.34 Y4.972 E.82989
G1 X31.701 Y4.972 E.03297
G1 X20.972 Y15.701 E.78326
G1 X20.972 Y15.063 E.03297
G1 X31.063 Y4.972 E.73664
G1 X30.424 Y4.972 E.03297
G1 X20.972 Y14.424 E.69002
G1 X20.972 Y13.785 E.03297
G1 X29.785 Y4.972 E.64339
G1 X29.147 Y4.972 E.03297
G1 X20.972 Y13.147 E.59677
G1 X20.972 Y12.508 E.03297
G1 X28.508 Y4.972 E.55014
G1 X27.869 Y4.972 E.03297
G1 X20.972 Y11.869 E.50352
G1 X20.972 Y11.231 E.03297
G1 X27.231 Y4.972 E.45689
G1 X26.592 Y4.972 E.03297
G1 X20.972 Y10.592 E.41027
G1 X20.972 Y9.953 E.03297
G1 X25.953 Y4.972 E.36364
G1 X25.314 Y4.972 E.03297
G1 X20.972 Y9.314 E.31702
G1 X20.972 Y8.676 E.03297
G1 X24.676 Y4.972 E.27039
G1 X24.037 Y4.972 E.03297
G1 X20.972 Y8.037 E.22377
G1 X20.972 Y7.398 E.03297
M73 P63 R12
G1 X23.398 Y4.972 E.17715
G1 X22.76 Y4.972 E.03297
G1 X20.972 Y6.76 E.13052
G1 X20.972 Y6.121 E.03297
G1 X22.121 Y4.972 E.0839
G1 X21.482 Y4.972 E.03297
G1 X20.769 Y5.685 E.05205
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X21.482 Y4.972 E-.38321
G1 X22.121 Y4.972 E-.24271
G1 X21.871 Y5.221 E-.13408
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 7/40
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
G17
G3 Z1.6 I1.217 J0 P1  F30000
; object ids of layer 7 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer7 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z1.8 F30000
G1 X160.4 Y8 Z1.8
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z1.8 F30000
G1 X114.002 Y8.498 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z1.8 F30000
G1 X93.502 Y73.11 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z1.8 F30000
G1 X97.11 Y46.302 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.702 E.37802
G1 X90.598 Y28.702 E.06469
G1 X90.598 Y22.398 E.20912
G1 X92.548 Y22.398 E.06469
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.202 Y22.398 E.06469
G1 X99.202 Y28.702 E.20912
G1 X97.252 Y28.702 E.06469
G1 X97.252 Y40.098 E.37802
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.769 E.36015
G1 X92.94 Y28.369 E.01229
G1 F10411.078
G1 X92.94 Y28.31 E.00181
G1 F9300
G1 X90.99 Y28.31 E.05992
G1 X90.99 Y22.831 E.16835
G1 F10065.328
G1 X90.99 Y22.79 E.00126
M73 P64 R12
G1 F12000
G1 X91.39 Y22.79 E.01229
G1 X92.94 Y22.79 E.04763
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X98.41 Y22.79 E.04763
G1 X98.81 Y22.79 E.01229
G1 F10065.328
G1 X98.81 Y22.831 E.00126
G1 F9300
G1 X98.81 Y28.31 E.16835
G1 X96.86 Y28.31 E.05992
G1 F10411.078
G1 X96.86 Y28.369 E.00181
G1 F12000
G1 X96.86 Y28.769 E.01229
G1 X96.86 Y40.49 E.36015
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z1.8 F30000
G1 X35.102 Y45.91 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.702 E.37802
G1 X28.198 Y28.702 E.06469
G1 X28.198 Y22.398 E.20912
G1 X30.148 Y22.398 E.06469
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.802 Y22.398 E.06469
G1 X36.802 Y28.702 E.20912
G1 X34.852 Y28.702 E.06469
G1 X34.852 Y40.098 E.37802
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.769 E.36015
G1 X30.54 Y28.369 E.01229
G1 F10411.078
G1 X30.54 Y28.31 E.00181
G1 F9300
G1 X28.59 Y28.31 E.05992
G1 X28.59 Y22.831 E.16835
G1 F10065.328
G1 X28.59 Y22.79 E.00126
G1 F12000
G1 X28.99 Y22.79 E.01229
G1 X30.54 Y22.79 E.04763
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X36.01 Y22.79 E.04763
G1 X36.41 Y22.79 E.01229
G1 F10065.328
G1 X36.41 Y22.831 E.00126
G1 F9300
G1 X36.41 Y28.31 E.16835
G1 X34.46 Y28.31 E.05992
G1 F10411.078
G1 X34.46 Y28.369 E.00181
G1 F12000
G1 X34.46 Y28.769 E.01229
G1 X34.46 Y40.49 E.36015
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.977 Y53.505 Z1.8 F30000
G1 X33.676 Y73.502 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.487 E.00833
G3 X33.548 Y67.905 I.284 J-2.786 E.27709
G3 X34.514 Y68.018 I.17 J2.727 E.03241
G3 X33.736 Y73.502 I-.804 J2.683 E.26397
G1 X33.695 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.096 E.00709
G3 X33.568 Y68.296 I.244 J-2.396 E.22062
G3 X34.4 Y68.393 I.034 J3.32 E.02581
G3 X33.936 Y73.098 I-.691 J2.307 E.20392
G1 X33.755 Y73.098 E.00557
; WIPE_START
M204 S10000
G1 X33.464 Y73.096 E-.11049
G1 X33 Y73.007 E-.17944
G1 X32.564 Y72.826 E-.1796
G1 X32.171 Y72.563 E-.17954
G1 X31.965 Y72.357 E-.11092
; WIPE_END
G1 E-.04 F1800
G1 X39.375 Y74.183 Z1.8 F30000
G1 X106.798 Y90.798 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.967 Y90.634 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42021
G1 F15000
G1 X37.135 Y27.803 E2.73184
G1 X37.135 Y28.337 E.0164
G1 X99.263 Y90.465 E2.70127
G1 X98.73 Y90.465 E.0164
G1 X37.135 Y28.87 E2.67807
G1 X37.135 Y29.035 E.00507
G1 X36.767 Y29.035 E.01133
G1 X98.196 Y90.465 E2.67089
G1 X97.663 Y90.465 E.0164
G1 X36.233 Y29.035 E2.67089
G1 X35.7 Y29.035 E.0164
G1 X97.129 Y90.465 E2.67089
G1 X96.595 Y90.465 E.0164
G1 X35.185 Y29.055 E2.67006
G1 X35.185 Y29.588 E.0164
G1 X96.062 Y90.465 E2.64686
G1 X95.528 Y90.465 E.0164
G1 X35.185 Y30.122 E2.62366
G1 X35.185 Y30.655 E.0164
G1 X94.995 Y90.465 E2.60046
G1 X94.461 Y90.465 E.0164
G1 X35.185 Y31.189 E2.57726
G1 X35.185 Y31.722 E.0164
G1 X93.928 Y90.465 E2.55406
G1 X93.394 Y90.465 E.0164
G1 X35.185 Y32.256 E2.53086
G1 X35.185 Y32.79 E.0164
G1 X92.86 Y90.465 E2.50766
G1 X92.327 Y90.465 E.0164
G1 X35.185 Y33.323 E2.48446
G1 X35.185 Y33.857 E.0164
G1 X91.793 Y90.465 E2.46127
G1 X91.26 Y90.465 E.0164
G1 X35.185 Y34.39 E2.43807
G1 X35.185 Y34.924 E.0164
G1 X90.726 Y90.465 E2.41487
G1 X90.193 Y90.465 E.0164
G1 X35.185 Y35.457 E2.39167
G1 X35.185 Y35.991 E.0164
G1 X89.659 Y90.465 E2.36847
G1 X89.126 Y90.465 E.0164
G1 X35.185 Y36.525 E2.34527
G1 X35.185 Y37.058 E.0164
G1 X88.592 Y90.465 E2.32207
G1 X88.058 Y90.465 E.0164
G1 X35.185 Y37.592 E2.29887
G1 X35.185 Y38.125 E.0164
G1 X87.525 Y90.465 E2.27567
G1 X86.991 Y90.465 E.0164
G1 X35.185 Y38.659 E2.25247
G1 X35.185 Y39.192 E.0164
G1 X86.458 Y90.465 E2.22927
G1 X85.924 Y90.465 E.0164
G1 X35.016 Y39.556 E2.21345
; WIPE_START
G1 X36.43 Y40.97 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.622 Y33.34 Z1.8 F30000
G1 X36.902 Y22.234 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F15000
G1 X20.935 Y6.267 E.69423
G1 X20.935 Y6.801 E.0164
G1 X36.199 Y22.065 E.66365
G1 X35.665 Y22.065 E.0164
G1 X20.935 Y7.335 E.64045
G1 X20.935 Y7.868 E.0164
G1 X34.832 Y21.765 E.60421
G1 X34.298 Y21.765 E.0164
G1 X20.935 Y8.402 E.58101
G1 X20.935 Y8.935 E.0164
G1 X33.765 Y21.765 E.55781
G1 X33.231 Y21.765 E.0164
G1 X20.935 Y9.469 E.53461
G1 X20.935 Y10.002 E.0164
G1 X32.698 Y21.765 E.51141
G1 X32.164 Y21.765 E.0164
G1 X20.935 Y10.536 E.48821
M73 P64 R11
G1 X20.935 Y11.07 E.0164
G1 X31.63 Y21.765 E.46501
G1 X31.097 Y21.765 E.0164
G1 X20.935 Y11.603 E.44181
G1 X20.935 Y12.137 E.0164
G1 X30.563 Y21.765 E.41862
G1 X30.03 Y21.765 E.0164
G1 X20.935 Y12.67 E.39542
G1 X20.935 Y13.204 E.0164
G1 X29.796 Y22.065 E.38526
G1 X29.263 Y22.065 E.0164
G1 X20.935 Y13.737 E.36206
G1 X20.935 Y14.271 E.0164
G1 X28.729 Y22.065 E.33886
G1 X28.195 Y22.065 E.0164
G1 X20.935 Y14.805 E.31566
G1 X20.935 Y15.338 E.0164
G1 X27.865 Y22.267 E.30128
G1 X27.865 Y22.801 E.0164
G1 X20.935 Y15.872 E.30128
G1 X20.935 Y16.405 E.0164
G1 X27.865 Y23.335 E.30128
G1 X27.865 Y23.868 E.0164
G1 X20.935 Y16.939 E.30128
G1 X20.935 Y17.472 E.0164
G1 X27.865 Y24.402 E.30128
G1 X27.865 Y24.935 E.0164
G1 X20.935 Y18.006 E.30128
G1 X20.935 Y18.54 E.0164
G1 X27.865 Y25.469 E.30128
G1 X27.865 Y26.002 E.0164
G1 X20.935 Y19.073 E.30128
G1 X20.935 Y19.607 E.0164
G1 X27.865 Y26.536 E.30128
G1 X27.865 Y27.07 E.0164
G1 X20.935 Y20.14 E.30128
G1 X20.935 Y20.674 E.0164
G1 X27.865 Y27.603 E.30128
G1 X27.865 Y28.137 E.0164
G1 X20.935 Y21.207 E.30128
G1 X20.935 Y21.741 E.0164
G1 X27.865 Y28.67 E.30128
G1 X27.865 Y29.035 E.01122
G1 X28.23 Y29.035 E.01122
G1 X29.815 Y30.62 E.06891
G1 X29.815 Y30.087 E.0164
G1 X28.763 Y29.035 E.04571
G1 X29.297 Y29.035 E.0164
G1 X29.984 Y29.723 E.02989
G1 X29.984 Y31.324 F30000
G1 F15000
G1 X20.935 Y22.275 E.39344
G1 X20.935 Y22.808 E.0164
G1 X29.815 Y31.687 E.38607
G1 X29.815 Y32.221 E.0164
G1 X20.935 Y23.342 E.38607
G1 X20.935 Y23.875 E.0164
G1 X29.815 Y32.755 E.38607
G1 X29.815 Y33.288 E.0164
G1 X20.935 Y24.409 E.38607
G1 X20.935 Y24.942 E.0164
G1 X29.815 Y33.822 E.38607
G1 X29.815 Y34.355 E.0164
G1 X20.935 Y25.476 E.38607
G1 X20.935 Y26.009 E.0164
G1 X29.815 Y34.889 E.38607
G1 X29.815 Y35.422 E.0164
G1 X20.935 Y26.543 E.38607
G1 X20.935 Y27.077 E.0164
G1 X29.815 Y35.956 E.38607
G1 X29.815 Y36.49 E.0164
G1 X20.935 Y27.61 E.38607
G1 X20.935 Y28.144 E.0164
G1 X29.815 Y37.023 E.38607
G1 X29.815 Y37.557 E.0164
G1 X20.935 Y28.677 E.38607
G1 X20.935 Y29.211 E.0164
G1 X29.815 Y38.09 E.38607
G1 X29.815 Y38.624 E.0164
G1 X20.935 Y29.744 E.38607
G1 X20.935 Y30.278 E.0164
G1 X29.815 Y39.157 E.38607
G1 X29.815 Y39.691 E.0164
G1 X20.935 Y30.812 E.38607
G1 X20.935 Y31.345 E.0164
G1 X29.565 Y39.975 E.3752
G1 X29.565 Y40.508 E.0164
G1 X20.935 Y31.879 E.3752
G1 X20.935 Y32.412 E.0164
G1 X29.565 Y41.042 E.3752
G1 X29.565 Y41.575 E.0164
G1 X20.935 Y32.946 E.3752
G1 X20.935 Y33.479 E.0164
G1 X29.565 Y42.109 E.3752
G1 X29.565 Y42.642 E.0164
M73 P65 R11
G1 X20.935 Y34.013 E.3752
G1 X20.935 Y34.547 E.0164
G1 X29.565 Y43.176 E.3752
G1 X29.565 Y43.709 E.0164
G1 X20.935 Y35.08 E.3752
G1 X20.935 Y35.614 E.0164
G1 X29.565 Y44.243 E.3752
G1 X29.565 Y44.777 E.0164
G1 X20.935 Y36.147 E.3752
G1 X20.935 Y36.681 E.0164
G1 X29.565 Y45.31 E.3752
G1 X29.565 Y45.844 E.0164
G1 X20.935 Y37.214 E.3752
G1 X20.935 Y37.748 E.0164
G1 X73.652 Y90.465 E2.29207
G1 X74.186 Y90.465 E.0164
G1 X30.356 Y46.635 E1.90566
G1 X30.89 Y46.635 E.0164
G1 X74.719 Y90.465 E1.90566
G1 X75.253 Y90.465 E.0164
G1 X31.423 Y46.635 E1.90566
G1 X31.957 Y46.635 E.0164
G1 X75.786 Y90.465 E1.90566
G1 X76.32 Y90.465 E.0164
G1 X32.49 Y46.635 E1.90566
G1 X33.024 Y46.635 E.0164
G1 X76.853 Y90.465 E1.90566
G1 X77.387 Y90.465 E.0164
G1 X33.558 Y46.635 E1.90566
G1 X34.091 Y46.635 E.0164
G1 X77.921 Y90.465 E1.90566
G1 X78.454 Y90.465 E.0164
G1 X34.625 Y46.635 E1.90566
G1 X35.158 Y46.635 E.0164
G1 X78.988 Y90.465 E1.90566
G1 X79.521 Y90.465 E.0164
G1 X35.435 Y46.379 E1.91682
G1 X35.435 Y45.845 E.0164
G1 X80.055 Y90.465 E1.94002
G1 X80.588 Y90.465 E.0164
G1 X35.435 Y45.312 E1.96321
G1 X35.435 Y44.778 E.0164
G1 X81.122 Y90.465 E1.98641
G1 X81.656 Y90.465 E.0164
G1 X35.435 Y44.244 E2.00961
G1 X35.435 Y43.711 E.0164
G1 X82.189 Y90.465 E2.03281
G1 X82.723 Y90.465 E.0164
G1 X35.435 Y43.177 E2.05601
G1 X35.435 Y42.644 E.0164
G1 X83.256 Y90.465 E2.07921
G1 X83.79 Y90.465 E.0164
G1 X35.435 Y42.11 E2.10241
G1 X35.435 Y41.577 E.0164
G1 X84.323 Y90.465 E2.12561
G1 X84.857 Y90.465 E.0164
G1 X35.435 Y41.043 E2.14881
G1 X35.435 Y40.509 E.0164
G1 X85.56 Y90.634 E2.17938
G1 X73.288 Y90.634 F30000
G1 F15000
G1 X20.935 Y38.282 E2.27625
G1 X20.935 Y38.815 E.0164
G1 X72.585 Y90.465 E2.24568
G1 X72.051 Y90.465 E.0164
G1 X20.935 Y39.349 E2.22248
G1 X20.935 Y39.882 E.0164
G1 X71.518 Y90.465 E2.19928
G1 X70.984 Y90.465 E.0164
G1 X20.935 Y40.416 E2.17608
G1 X20.935 Y40.949 E.0164
G1 X70.451 Y90.465 E2.15288
G1 X69.917 Y90.465 E.0164
G1 X20.935 Y41.483 E2.12968
G1 X20.935 Y42.017 E.0164
G1 X69.383 Y90.465 E2.10648
G1 X68.85 Y90.465 E.0164
G1 X20.935 Y42.55 E2.08328
G1 X20.935 Y43.084 E.0164
G1 X68.316 Y90.465 E2.06008
G1 X67.783 Y90.465 E.0164
G1 X20.935 Y43.617 E2.03688
G1 X20.935 Y44.151 E.0164
G1 X67.249 Y90.465 E2.01368
G1 X66.716 Y90.465 E.0164
G1 X20.935 Y44.684 E1.99049
G1 X20.935 Y45.218 E.0164
G1 X66.182 Y90.465 E1.96729
G1 X65.648 Y90.465 E.0164
G1 X20.935 Y45.752 E1.94409
G1 X20.935 Y46.285 E.0164
G1 X65.115 Y90.465 E1.92089
G1 X64.581 Y90.465 E.0164
G1 X20.935 Y46.819 E1.89769
G1 X20.935 Y47.352 E.0164
G1 X64.048 Y90.465 E1.87449
G1 X63.514 Y90.465 E.0164
G1 X20.935 Y47.886 E1.85129
G1 X20.935 Y48.419 E.0164
G1 X62.981 Y90.465 E1.82809
G1 X62.447 Y90.465 E.0164
G1 X20.935 Y48.953 E1.80489
G1 X20.935 Y49.487 E.0164
G1 X61.914 Y90.465 E1.78169
G1 X61.38 Y90.465 E.0164
G1 X20.935 Y50.02 E1.75849
G1 X20.935 Y50.554 E.0164
G1 X60.846 Y90.465 E1.7353
G1 X60.313 Y90.465 E.0164
G1 X20.935 Y51.087 E1.7121
G1 X20.935 Y51.621 E.0164
G1 X59.779 Y90.465 E1.6889
G1 X59.246 Y90.465 E.0164
G1 X20.935 Y52.154 E1.6657
G1 X20.935 Y52.688 E.0164
G1 X58.712 Y90.465 E1.6425
G1 X58.179 Y90.465 E.0164
G1 X20.935 Y53.221 E1.6193
G1 X20.935 Y53.755 E.0164
G1 X35.056 Y67.876 E.61397
G2 X34.263 Y67.617 I-1.21 J2.357 E.02576
G1 X20.935 Y54.289 E.57949
G1 X20.935 Y54.822 E.0164
G1 X33.686 Y67.573 E.55441
G2 X33.191 Y67.611 I-.104 J1.899 E.01533
G1 X20.935 Y55.356 E.53285
G1 X20.935 Y55.889 E.0164
G1 X32.756 Y67.71 E.51397
G2 X32.374 Y67.862 I.58 J2.024 E.01266
G1 X20.935 Y56.423 E.49735
G1 X20.935 Y56.956 E.0164
G1 X32.028 Y68.05 E.48232
G2 X31.716 Y68.271 I.966 J1.692 E.01179
G1 X20.935 Y57.49 E.46875
G1 X20.935 Y58.024 E.0164
G1 X31.44 Y68.529 E.45674
G2 X31.196 Y68.818 I1.341 J1.382 E.01166
G1 X20.935 Y58.557 E.44612
G1 X20.935 Y59.091 E.0164
G1 X30.983 Y69.139 E.43688
G1 X30.948 Y69.198 E.00212
G2 X30.805 Y69.494 I1.43 J.873 E.01012
G1 X20.935 Y59.624 E.42913
G1 X20.935 Y60.158 E.0164
G1 X30.672 Y69.895 E.42335
G2 X30.586 Y70.342 I2.238 J.663 E.01403
G1 X20.935 Y60.691 E.41961
G1 X20.935 Y61.225 E.0164
G1 X30.571 Y70.861 E.41897
G2 X30.669 Y71.492 I3.149 J-.164 E.01967
G1 X20.935 Y61.759 E.42321
G1 X20.935 Y62.292 E.0164
G1 X49.108 Y90.465 E1.22492
G1 X49.641 Y90.465 E.0164
G1 X32.908 Y73.731 E.72756
G2 X33.539 Y73.829 I.795 J-3.052 E.01967
G1 X50.175 Y90.465 E.72332
G1 X50.709 Y90.465 E.0164
G1 X34.058 Y73.814 E.72396
G2 X34.505 Y73.728 I-.215 J-2.325 E.01403
G1 X51.242 Y90.465 E.72771
G1 X51.776 Y90.465 E.0164
G1 X34.906 Y73.595 E.73348
G2 X35.261 Y73.417 I-.769 J-1.973 E.01224
G1 X52.309 Y90.465 E.74124
G1 X52.843 Y90.465 E.0164
G1 X35.582 Y73.204 E.75047
G2 X35.871 Y72.96 I-1.093 J-1.586 E.01166
G1 X53.376 Y90.465 E.7611
G1 X53.91 Y90.465 E.0164
G1 X36.129 Y72.684 E.7731
G2 X36.35 Y72.372 I-1.473 J-1.279 E.01178
G1 X54.444 Y90.465 E.78667
G1 X54.977 Y90.465 E.0164
G1 X36.538 Y72.026 E.8017
G2 X36.69 Y71.644 I-1.871 J-.962 E.01266
G1 X55.511 Y90.465 E.81832
G1 X56.044 Y90.465 E.0164
G1 X36.791 Y71.211 E.83711
G2 X36.835 Y70.722 I-2.462 J-.47 E.01513
G1 X56.578 Y90.465 E.85838
G1 X57.111 Y90.465 E.0164
G1 X36.783 Y70.137 E.88384
G2 X36.524 Y69.344 I-2.618 J.418 E.02576
G1 X57.815 Y90.634 E.92571
G1 X48.744 Y90.634 F30000
G1 F15000
G1 X20.935 Y62.826 E1.20909
G1 X20.935 Y63.359 E.0164
G1 X48.041 Y90.465 E1.17852
G1 X47.507 Y90.465 E.0164
G1 X20.935 Y63.893 E1.15532
G1 X20.935 Y64.426 E.0164
G1 X46.974 Y90.465 E1.13212
G1 X46.44 Y90.465 E.0164
G1 X20.935 Y64.96 E1.10892
G1 X20.935 Y65.494 E.0164
G1 X45.906 Y90.465 E1.08572
G1 X45.373 Y90.465 E.0164
G1 X20.935 Y66.027 E1.06252
G1 X20.935 Y66.561 E.0164
G1 X44.839 Y90.465 E1.03932
G1 X44.306 Y90.465 E.0164
G1 X20.935 Y67.094 E1.01612
G1 X20.935 Y67.628 E.0164
G1 X43.772 Y90.465 E.99293
G1 X43.239 Y90.465 E.0164
G1 X20.935 Y68.161 E.96973
G1 X20.935 Y68.695 E.0164
G1 X42.705 Y90.465 E.94653
G1 X42.171 Y90.465 E.0164
G1 X20.935 Y69.229 E.92333
G1 X20.935 Y69.762 E.0164
G1 X41.638 Y90.465 E.90013
G1 X41.104 Y90.465 E.0164
G1 X20.935 Y70.296 E.87693
G1 X20.935 Y70.829 E.0164
G1 X40.571 Y90.465 E.85373
G1 X40.037 Y90.465 E.0164
G1 X20.935 Y71.363 E.83053
G1 X20.935 Y71.896 E.0164
G1 X39.504 Y90.465 E.80733
G1 X38.97 Y90.465 E.0164
G1 X20.935 Y72.43 E.78413
G1 X20.935 Y72.964 E.0164
G1 X38.436 Y90.465 E.76093
G1 X37.903 Y90.465 E.0164
M73 P66 R11
G1 X20.935 Y73.497 E.73774
G1 X20.935 Y74.031 E.0164
G1 X37.369 Y90.465 E.71454
G1 X36.836 Y90.465 E.0164
G1 X20.935 Y74.564 E.69134
G1 X20.935 Y75.098 E.0164
G1 X36.302 Y90.465 E.66814
G1 X35.769 Y90.465 E.0164
G1 X20.935 Y75.631 E.64494
G1 X20.935 Y76.165 E.0164
G1 X35.235 Y90.465 E.62174
G1 X34.701 Y90.465 E.0164
G1 X20.935 Y76.699 E.59854
G1 X20.935 Y77.232 E.0164
G1 X34.168 Y90.465 E.57534
G1 X33.634 Y90.465 E.0164
G1 X20.935 Y77.766 E.55214
G1 X20.935 Y78.299 E.0164
G1 X33.101 Y90.465 E.52894
G1 X32.567 Y90.465 E.0164
G1 X20.935 Y78.833 E.50574
G1 X20.935 Y79.366 E.0164
G1 X32.034 Y90.465 E.48255
G1 X31.5 Y90.465 E.0164
G1 X20.935 Y79.9 E.45935
G1 X20.935 Y80.433 E.0164
G1 X30.967 Y90.465 E.43615
G1 X30.433 Y90.465 E.0164
G1 X20.935 Y80.967 E.41295
G1 X20.935 Y81.501 E.0164
G1 X29.899 Y90.465 E.38975
G1 X29.366 Y90.465 E.0164
G1 X20.935 Y82.034 E.36655
G1 X20.935 Y82.568 E.0164
G1 X28.832 Y90.465 E.34335
G1 X28.299 Y90.465 E.0164
G1 X20.935 Y83.101 E.32015
G1 X20.935 Y83.635 E.0164
G1 X27.765 Y90.465 E.29695
G1 X27.232 Y90.465 E.0164
G1 X20.935 Y84.168 E.27375
G1 X20.935 Y84.702 E.0164
G1 X26.698 Y90.465 E.25055
G1 X26.164 Y90.465 E.0164
G1 X20.935 Y85.236 E.22736
G1 X20.935 Y85.769 E.0164
G1 X25.631 Y90.465 E.20416
G1 X25.097 Y90.465 E.0164
G1 X20.935 Y86.303 E.18096
G1 X20.935 Y86.836 E.0164
G1 X24.564 Y90.465 E.15776
G1 X24.03 Y90.465 E.0164
G1 X20.935 Y87.37 E.13456
G1 X20.935 Y87.903 E.0164
G1 X23.497 Y90.465 E.11136
G1 X22.963 Y90.465 E.0164
G1 X20.935 Y88.437 E.08816
G1 X20.935 Y88.971 E.0164
G1 X22.429 Y90.465 E.06496
G1 X21.896 Y90.465 E.0164
G1 X20.935 Y89.504 E.04176
G1 X20.935 Y90.038 E.0164
G1 X21.532 Y90.634 E.02594
G1 X106.634 Y80.762 F30000
G1 F15000
G1 X93.835 Y67.963 E.55649
G1 X93.835 Y68.496 E.0164
G1 X106.465 Y81.125 E.54911
G1 X106.465 Y81.659 E.0164
G1 X93.835 Y69.03 E.54911
G1 X93.835 Y69.563 E.0164
G1 X106.465 Y82.193 E.54911
G1 X106.465 Y82.726 E.0164
G1 X93.835 Y70.097 E.54911
G1 X93.835 Y70.63 E.0164
G1 X106.465 Y83.26 E.54911
G1 X106.465 Y83.793 E.0164
G1 X93.835 Y71.164 E.54911
G1 X93.835 Y71.697 E.0164
G1 X106.465 Y84.327 E.54911
G1 X106.465 Y84.86 E.0164
G1 X93.835 Y72.231 E.54911
G1 X93.835 Y72.765 E.0164
G1 X106.465 Y85.394 E.54911
G1 X106.465 Y85.928 E.0164
G1 X93.835 Y73.298 E.54911
G1 X93.835 Y73.832 E.0164
G1 X106.465 Y86.461 E.54911
G1 X106.465 Y86.995 E.0164
G1 X93.305 Y73.835 E.57216
G1 X92.772 Y73.835 E.0164
G1 X106.465 Y87.528 E.59536
G1 X106.465 Y88.062 E.0164
G1 X92.238 Y73.835 E.61856
G1 X91.705 Y73.835 E.0164
G1 X106.465 Y88.595 E.64175
G1 X106.465 Y89.129 E.0164
G1 X91.171 Y73.835 E.66495
G1 X90.637 Y73.835 E.0164
G1 X106.465 Y89.663 E.68815
G1 X106.465 Y90.196 E.0164
G1 X90.104 Y73.835 E.71135
G1 X89.57 Y73.835 E.0164
G1 X106.2 Y90.465 E.72303
G1 X105.666 Y90.465 E.0164
G1 X89.037 Y73.835 E.72303
G1 X88.503 Y73.835 E.0164
G1 X105.133 Y90.465 E.72303
G1 X104.599 Y90.465 E.0164
G1 X87.97 Y73.835 E.72303
G1 X87.436 Y73.835 E.0164
G1 X104.065 Y90.465 E.72303
G1 X103.532 Y90.465 E.0164
G1 X86.903 Y73.835 E.72303
G1 X86.369 Y73.835 E.0164
G1 X102.998 Y90.465 E.72303
G1 X102.465 Y90.465 E.0164
G1 X85.835 Y73.835 E.72303
G1 X85.302 Y73.835 E.0164
G1 X101.931 Y90.465 E.72303
G1 X101.398 Y90.465 E.0164
G1 X84.768 Y73.835 E.72303
G1 X84.235 Y73.835 E.0164
G1 X100.864 Y90.465 E.72303
G1 X100.33 Y90.465 E.0164
G1 X37.135 Y27.27 E2.74767
G1 X37.135 Y26.736 E.0164
G1 X83.565 Y73.165 E2.01871
G1 X83.565 Y72.632 E.0164
G1 X37.135 Y26.202 E2.01871
G1 X37.135 Y25.669 E.0164
G1 X83.565 Y72.098 E2.01871
G1 X83.565 Y71.565 E.0164
G1 X37.135 Y25.135 E2.01871
G1 X37.135 Y24.602 E.0164
G1 X83.565 Y71.031 E2.01871
G1 X83.565 Y70.498 E.0164
G1 X37.135 Y24.068 E2.01871
G1 X37.135 Y23.535 E.0164
G1 X83.565 Y69.964 E2.01871
G1 X83.565 Y69.43 E.0164
G1 X37.135 Y23.001 E2.01871
G1 X37.135 Y22.467 E.0164
G1 X83.565 Y68.897 E2.01871
G1 X83.565 Y68.363 E.0164
G1 X20.935 Y5.734 E2.72307
G1 X20.935 Y5.2 E.0164
G1 X83.565 Y67.83 E2.72307
G1 X83.565 Y67.565 E.00815
G1 X83.833 Y67.565 E.00826
G1 X21.204 Y4.935 E2.72307
G1 X21.737 Y4.935 E.0164
G1 X84.367 Y67.565 E2.72307
G1 X84.9 Y67.565 E.0164
G1 X22.271 Y4.935 E2.72307
G1 X22.805 Y4.935 E.0164
G1 X85.434 Y67.565 E2.72307
G1 X85.968 Y67.565 E.0164
G1 X23.338 Y4.935 E2.72307
G1 X23.872 Y4.935 E.0164
G1 X86.501 Y67.565 E2.72307
G1 X87.035 Y67.565 E.0164
G1 X24.405 Y4.935 E2.72307
G1 X24.939 Y4.935 E.0164
G1 X87.568 Y67.565 E2.72307
G1 X88.102 Y67.565 E.0164
G1 X25.472 Y4.935 E2.72307
G1 X26.006 Y4.935 E.0164
G1 X88.635 Y67.565 E2.72307
G1 X89.169 Y67.565 E.0164
G1 X26.54 Y4.935 E2.72307
G1 X27.073 Y4.935 E.0164
G1 X89.703 Y67.565 E2.72307
G1 X90.236 Y67.565 E.0164
G1 X27.607 Y4.935 E2.72307
G1 X28.14 Y4.935 E.0164
G1 X90.77 Y67.565 E2.72307
G1 X91.303 Y67.565 E.0164
G1 X28.674 Y4.935 E2.72307
G1 X29.207 Y4.935 E.0164
G1 X91.837 Y67.565 E2.72307
G1 X92.37 Y67.565 E.0164
G1 X29.741 Y4.935 E2.72307
G1 X30.275 Y4.935 E.0164
G1 X92.904 Y67.565 E2.72307
G1 X93.438 Y67.565 E.0164
G1 X30.808 Y4.935 E2.72307
G1 X31.342 Y4.935 E.0164
G1 X106.465 Y80.058 E3.26628
G1 X106.465 Y79.525 E.0164
G1 X31.875 Y4.935 E3.24308
G1 X32.409 Y4.935 E.0164
G1 X106.465 Y78.991 E3.21988
G1 X106.465 Y78.458 E.0164
G1 X32.942 Y4.935 E3.19668
G1 X33.476 Y4.935 E.0164
G1 X106.465 Y77.924 E3.17348
G1 X106.465 Y77.39 E.0164
G1 X34.01 Y4.935 E3.15028
G1 X34.543 Y4.935 E.0164
G1 X106.465 Y76.857 E3.12708
G1 X106.465 Y76.323 E.0164
G1 X35.077 Y4.935 E3.10388
G1 X35.61 Y4.935 E.0164
G1 X106.465 Y75.79 E3.08069
G1 X106.465 Y75.256 E.0164
G1 X36.144 Y4.935 E3.05749
G1 X36.677 Y4.935 E.0164
G1 X106.465 Y74.723 E3.03429
G1 X106.465 Y74.189 E.0164
G1 X37.211 Y4.935 E3.01109
G1 X37.745 Y4.935 E.0164
G1 X106.465 Y73.655 E2.98789
G1 X106.465 Y73.122 E.0164
G1 X38.278 Y4.935 E2.96469
G1 X38.812 Y4.935 E.0164
G1 X106.465 Y72.588 E2.94149
G1 X106.465 Y72.055 E.0164
G1 X39.345 Y4.935 E2.91829
G1 X39.879 Y4.935 E.0164
G1 X106.465 Y71.521 E2.89509
G1 X106.465 Y70.988 E.0164
G1 X40.412 Y4.935 E2.87189
G1 X40.946 Y4.935 E.0164
G1 X106.465 Y70.454 E2.84869
G1 X106.465 Y69.92 E.0164
G1 X41.48 Y4.935 E2.8255
G1 X42.013 Y4.935 E.0164
G1 X106.465 Y69.387 E2.8023
G1 X106.465 Y68.853 E.0164
G1 X42.547 Y4.935 E2.7791
G1 X43.08 Y4.935 E.0164
G1 X106.465 Y68.32 E2.7559
G1 X106.465 Y67.786 E.0164
G1 X43.614 Y4.935 E2.7327
G1 X44.147 Y4.935 E.0164
G1 X106.465 Y67.253 E2.7095
G1 X106.465 Y66.719 E.0164
G1 X44.681 Y4.935 E2.6863
G1 X45.215 Y4.935 E.0164
G1 X106.465 Y66.186 E2.6631
G1 X106.465 Y65.652 E.0164
G1 X45.748 Y4.935 E2.6399
G1 X46.282 Y4.935 E.0164
G1 X106.465 Y65.118 E2.6167
G1 X106.465 Y64.585 E.0164
G1 X46.815 Y4.935 E2.5935
G1 X47.349 Y4.935 E.0164
G1 X106.465 Y64.051 E2.57031
G1 X106.465 Y63.518 E.0164
G1 X47.882 Y4.935 E2.54711
G1 X48.416 Y4.935 E.0164
G1 X106.465 Y62.984 E2.52391
G1 X106.465 Y62.451 E.0164
G1 X48.949 Y4.935 E2.50071
G1 X49.483 Y4.935 E.0164
G1 X106.465 Y61.917 E2.47751
G1 X106.465 Y61.383 E.0164
G1 X50.017 Y4.935 E2.45431
G1 X50.55 Y4.935 E.0164
G1 X106.465 Y60.85 E2.43111
G1 X106.465 Y60.316 E.0164
G1 X92.784 Y46.635 E.59483
G1 X93.317 Y46.635 E.0164
M73 P67 R11
G1 X106.465 Y59.783 E.57164
G1 X106.465 Y59.249 E.0164
G1 X93.851 Y46.635 E.54844
G1 X94.384 Y46.635 E.0164
G1 X106.465 Y58.716 E.52524
G1 X106.465 Y58.182 E.0164
G1 X94.918 Y46.635 E.50204
G1 X95.452 Y46.635 E.0164
G1 X106.465 Y57.648 E.47884
G1 X106.465 Y57.115 E.0164
G1 X95.985 Y46.635 E.45564
G1 X96.519 Y46.635 E.0164
G1 X106.465 Y56.581 E.43244
G1 X106.465 Y56.048 E.0164
G1 X97.052 Y46.635 E.40924
G1 X97.586 Y46.635 E.0164
G1 X106.465 Y55.514 E.38604
G1 X106.465 Y54.981 E.0164
G1 X97.835 Y46.351 E.3752
G1 X97.835 Y45.818 E.0164
G1 X106.465 Y54.447 E.3752
G1 X106.465 Y53.913 E.0164
G1 X97.835 Y45.284 E.3752
G1 X97.835 Y44.751 E.0164
G1 X106.465 Y53.38 E.3752
G1 X106.465 Y52.846 E.0164
M73 P67 R10
G1 X97.835 Y44.217 E.3752
G1 X97.835 Y43.683 E.0164
G1 X106.465 Y52.313 E.3752
G1 X106.465 Y51.779 E.0164
G1 X97.835 Y43.15 E.3752
G1 X97.835 Y42.616 E.0164
G1 X106.465 Y51.246 E.3752
G1 X106.465 Y50.712 E.0164
G1 X97.835 Y42.083 E.3752
G1 X97.835 Y41.549 E.0164
G1 X106.465 Y50.178 E.3752
G1 X106.465 Y49.645 E.0164
G1 X97.835 Y41.016 E.3752
G1 X97.835 Y40.482 E.0164
G1 X106.634 Y49.281 E.38257
G1 X106.634 Y29.539 F30000
G1 F15000
G1 X99.535 Y22.44 E.30866
G1 X99.535 Y22.973 E.0164
G1 X106.465 Y29.903 E.30128
G1 X106.465 Y30.436 E.0164
G1 X99.535 Y23.507 E.30128
G1 X99.535 Y24.041 E.0164
G1 X106.465 Y30.97 E.30128
G1 X106.465 Y31.504 E.0164
G1 X99.535 Y24.574 E.30128
G1 X99.535 Y25.108 E.0164
G1 X106.465 Y32.037 E.30128
G1 X106.465 Y32.571 E.0164
G1 X99.535 Y25.641 E.30128
G1 X99.535 Y26.175 E.0164
G1 X106.465 Y33.104 E.30128
G1 X106.465 Y33.638 E.0164
G1 X99.535 Y26.708 E.30128
G1 X99.535 Y27.242 E.0164
G1 X106.465 Y34.171 E.30128
G1 X106.465 Y34.705 E.0164
G1 X99.535 Y27.776 E.30128
G1 X99.535 Y28.309 E.0164
G1 X106.465 Y35.239 E.30128
G1 X106.465 Y35.772 E.0164
G1 X99.535 Y28.843 E.30128
G1 X99.535 Y29.035 E.00592
G1 X99.194 Y29.035 E.01048
G1 X106.465 Y36.306 E.31611
G1 X106.465 Y36.839 E.0164
G1 X98.661 Y29.035 E.33931
G1 X98.127 Y29.035 E.0164
G1 X106.465 Y37.373 E.36251
G1 X106.465 Y37.906 E.0164
G1 X97.594 Y29.035 E.38571
G1 X97.585 Y29.561 E.01615
G1 X106.465 Y38.44 E.38607
G1 X106.465 Y38.974 E.0164
G1 X97.585 Y30.094 E.38607
G1 X97.585 Y30.628 E.0164
G1 X106.465 Y39.507 E.38607
G1 X106.465 Y40.041 E.0164
G1 X97.585 Y31.161 E.38607
G1 X97.585 Y31.695 E.0164
G1 X106.465 Y40.574 E.38607
G1 X106.465 Y41.108 E.0164
G1 X97.585 Y32.228 E.38607
G1 X97.585 Y32.762 E.0164
G1 X106.465 Y41.641 E.38607
G1 X106.465 Y42.175 E.0164
G1 X97.585 Y33.296 E.38607
G1 X97.585 Y33.829 E.0164
G1 X106.465 Y42.708 E.38607
G1 X106.465 Y43.242 E.0164
G1 X97.585 Y34.363 E.38607
G1 X97.585 Y34.896 E.0164
G1 X106.465 Y43.776 E.38607
G1 X106.465 Y44.309 E.0164
G1 X97.585 Y35.43 E.38607
G1 X97.585 Y35.963 E.0164
G1 X106.465 Y44.843 E.38607
G1 X106.465 Y45.376 E.0164
G1 X97.585 Y36.497 E.38607
G1 X97.585 Y37.031 E.0164
G1 X106.465 Y45.91 E.38607
G1 X106.465 Y46.443 E.0164
G1 X97.585 Y37.564 E.38607
G1 X97.585 Y38.098 E.0164
G1 X106.465 Y46.977 E.38607
G1 X106.465 Y47.511 E.0164
M73 P68 R10
G1 X97.585 Y38.631 E.38607
G1 X97.585 Y39.165 E.0164
G1 X106.465 Y48.044 E.38607
G1 X106.465 Y48.578 E.0164
G1 X97.416 Y39.529 E.39344
; WIPE_START
G1 X98.83 Y40.943 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.733 Y45.535 Z1.8 F30000
G1 X92.134 Y45.986 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F15000
G1 X51.084 Y4.935 E1.78484
G1 X51.617 Y4.935 E.0164
G1 X91.965 Y45.283 E1.75427
G1 X91.965 Y44.749 E.0164
G1 X52.151 Y4.935 E1.73107
G1 X52.684 Y4.935 E.0164
G1 X91.965 Y44.216 E1.70787
G1 X91.965 Y43.682 E.0164
G1 X53.218 Y4.935 E1.68467
G1 X53.752 Y4.935 E.0164
G1 X91.965 Y43.148 E1.66147
G1 X91.965 Y42.615 E.0164
G1 X54.285 Y4.935 E1.63827
G1 X54.819 Y4.935 E.0164
G1 X91.965 Y42.081 E1.61507
G1 X91.965 Y41.548 E.0164
G1 X55.352 Y4.935 E1.59187
G1 X55.886 Y4.935 E.0164
G1 X91.965 Y41.014 E1.56867
G1 X91.965 Y40.481 E.0164
G1 X56.419 Y4.935 E1.54547
G1 X56.953 Y4.935 E.0164
G1 X91.965 Y39.947 E1.52228
G1 X91.965 Y39.765 E.00561
G1 X92.215 Y39.765 E.00769
G1 X92.215 Y39.663 E.00311
G1 X57.487 Y4.935 E1.50995
G1 X58.02 Y4.935 E.0164
G1 X92.215 Y39.13 E1.48675
G1 X92.215 Y38.596 E.0164
G1 X58.554 Y4.935 E1.46355
G1 X59.087 Y4.935 E.0164
G1 X92.215 Y38.063 E1.44035
G1 X92.215 Y37.529 E.0164
G1 X59.621 Y4.935 E1.41715
G1 X60.154 Y4.935 E.0164
G1 X92.215 Y36.996 E1.39395
G1 X92.215 Y36.462 E.0164
G1 X60.688 Y4.935 E1.37075
G1 X61.222 Y4.935 E.0164
G1 X92.215 Y35.928 E1.34755
G1 X92.215 Y35.395 E.0164
G1 X61.755 Y4.935 E1.32435
G1 X62.289 Y4.935 E.0164
G1 X92.215 Y34.861 E1.30115
G1 X92.215 Y34.328 E.0164
G1 X62.822 Y4.935 E1.27796
G1 X63.356 Y4.935 E.0164
G1 X92.215 Y33.794 E1.25476
G1 X92.215 Y33.261 E.0164
G1 X63.889 Y4.935 E1.23156
G1 X64.423 Y4.935 E.0164
G1 X92.215 Y32.727 E1.20836
G1 X92.215 Y32.193 E.0164
G1 X64.957 Y4.935 E1.18516
G1 X65.49 Y4.935 E.0164
G1 X92.384 Y31.83 E1.16934
G1 X91.555 Y28.866 F30000
G1 F15000
G1 X92.215 Y29.526 E.0287
G1 X92.215 Y30.059 E.0164
G1 X91.191 Y29.035 E.04452
G1 X90.657 Y29.035 E.0164
G1 X92.215 Y30.593 E.06772
G1 X92.215 Y31.126 E.0164
G1 X66.024 Y4.935 E1.13876
G1 X66.557 Y4.935 E.0164
G1 X90.265 Y28.643 E1.03078
G1 X90.265 Y28.109 E.0164
G1 X67.091 Y4.935 E1.00758
G1 X67.624 Y4.935 E.0164
G1 X90.265 Y27.576 E.98438
G1 X90.265 Y27.042 E.0164
G1 X68.158 Y4.935 E.96118
G1 X68.692 Y4.935 E.0164
G1 X90.265 Y26.508 E.93798
G1 X90.265 Y25.975 E.0164
G1 X69.225 Y4.935 E.91478
G1 X69.759 Y4.935 E.0164
G1 X90.265 Y25.441 E.89158
G1 X90.265 Y24.908 E.0164
G1 X70.292 Y4.935 E.86838
G1 X70.826 Y4.935 E.0164
G1 X90.265 Y24.374 E.84519
G1 X90.265 Y23.841 E.0164
G1 X71.359 Y4.935 E.82199
G1 X71.893 Y4.935 E.0164
G1 X90.265 Y23.307 E.79879
G1 X90.265 Y22.774 E.0164
G1 X72.427 Y4.935 E.77559
G1 X72.96 Y4.935 E.0164
G1 X90.265 Y22.24 E.75239
G1 X90.265 Y22.065 E.00539
G1 X90.623 Y22.065 E.01102
G1 X73.494 Y4.935 E.74477
G1 X74.027 Y4.935 E.0164
G1 X91.157 Y22.065 E.74477
G1 X91.69 Y22.065 E.0164
G1 X74.561 Y4.935 E.74477
G1 X75.094 Y4.935 E.0164
G1 X92.215 Y22.056 E.74438
G1 X92.215 Y21.765 E.00895
G1 X92.457 Y21.765 E.00746
G1 X75.628 Y4.935 E.73172
G1 X76.161 Y4.935 E.0164
G1 X92.991 Y21.765 E.73172
G1 X93.524 Y21.765 E.0164
G1 X76.695 Y4.935 E.73172
G1 X77.229 Y4.935 E.0164
G1 X94.058 Y21.765 E.73172
G1 X94.592 Y21.765 E.0164
G1 X77.762 Y4.935 E.73172
G1 X78.296 Y4.935 E.0164
G1 X95.125 Y21.765 E.73172
G1 X95.659 Y21.765 E.0164
G1 X78.829 Y4.935 E.73172
G1 X79.363 Y4.935 E.0164
G1 X96.192 Y21.765 E.73172
G1 X96.726 Y21.765 E.0164
G1 X79.896 Y4.935 E.73172
G1 X80.43 Y4.935 E.0164
G1 X97.259 Y21.765 E.73172
G1 X97.585 Y21.765 E.01002
G1 X97.585 Y22.065 E.00922
G1 X98.093 Y22.065 E.01561
G1 X80.964 Y4.935 E.74477
G1 X81.497 Y4.935 E.0164
G1 X98.627 Y22.065 E.74477
G1 X99.16 Y22.065 E.0164
G1 X82.031 Y4.935 E.74477
G1 X82.564 Y4.935 E.0164
G1 X106.465 Y28.836 E1.03917
G1 X106.465 Y28.302 E.0164
G1 X83.098 Y4.935 E1.01597
G1 X83.631 Y4.935 E.0164
G1 X106.465 Y27.769 E.99277
G1 X106.465 Y27.235 E.0164
G1 X84.165 Y4.935 E.96957
G1 X84.699 Y4.935 E.0164
G1 X106.465 Y26.701 E.94637
G1 X106.465 Y26.168 E.0164
G1 X85.232 Y4.935 E.92317
G1 X85.766 Y4.935 E.0164
G1 X106.465 Y25.634 E.89997
G1 X106.465 Y25.101 E.0164
G1 X86.299 Y4.935 E.87677
G1 X86.833 Y4.935 E.0164
G1 X106.465 Y24.567 E.85357
G1 X106.465 Y24.034 E.0164
G1 X87.366 Y4.935 E.83037
G1 X87.9 Y4.935 E.0164
G1 X106.465 Y23.5 E.80718
G1 X106.465 Y22.966 E.0164
G1 X88.434 Y4.935 E.78398
G1 X88.967 Y4.935 E.0164
G1 X106.465 Y22.433 E.76078
G1 X106.465 Y21.899 E.0164
G1 X89.501 Y4.935 E.73758
G1 X90.034 Y4.935 E.0164
G1 X106.465 Y21.366 E.71438
G1 X106.465 Y20.832 E.0164
G1 X90.568 Y4.935 E.69118
G1 X91.101 Y4.935 E.0164
G1 X106.465 Y20.299 E.66798
G1 X106.465 Y19.765 E.0164
G1 X91.635 Y4.935 E.64478
G1 X92.169 Y4.935 E.0164
G1 X106.465 Y19.231 E.62158
G1 X106.465 Y18.698 E.0164
G1 X92.702 Y4.935 E.59838
G1 X93.236 Y4.935 E.0164
G1 X106.465 Y18.164 E.57519
G1 X106.465 Y17.631 E.0164
G1 X93.769 Y4.935 E.55199
G1 X94.303 Y4.935 E.0164
G1 X106.465 Y17.097 E.52879
G1 X106.465 Y16.564 E.0164
G1 X94.836 Y4.935 E.50559
G1 X95.37 Y4.935 E.0164
G1 X106.465 Y16.03 E.48239
G1 X106.465 Y15.496 E.0164
G1 X95.904 Y4.935 E.45919
G1 X96.437 Y4.935 E.0164
G1 X106.465 Y14.963 E.43599
G1 X106.465 Y14.429 E.0164
G1 X96.971 Y4.935 E.41279
G1 X97.504 Y4.935 E.0164
G1 X106.465 Y13.896 E.38959
G1 X106.465 Y13.362 E.0164
G1 X98.038 Y4.935 E.36639
G1 X98.571 Y4.935 E.0164
G1 X106.465 Y12.829 E.34319
G1 X106.465 Y12.295 E.0164
G1 X99.105 Y4.935 E.32
G1 X99.639 Y4.935 E.0164
G1 X106.465 Y11.761 E.2968
G1 X106.465 Y11.228 E.0164
G1 X100.172 Y4.935 E.2736
G1 X100.706 Y4.935 E.0164
G1 X106.465 Y10.694 E.2504
G1 X106.465 Y10.161 E.0164
G1 X101.239 Y4.935 E.2272
G1 X101.773 Y4.935 E.0164
G1 X106.465 Y9.627 E.204
G1 X106.465 Y9.094 E.0164
G1 X102.306 Y4.935 E.1808
G1 X102.84 Y4.935 E.0164
G1 X106.465 Y8.56 E.1576
G1 X106.465 Y8.027 E.0164
G1 X103.373 Y4.935 E.1344
G1 X103.907 Y4.935 E.0164
G1 X106.465 Y7.493 E.1112
G1 X106.465 Y6.959 E.0164
G1 X104.441 Y4.935 E.088
G1 X104.974 Y4.935 E.0164
G1 X106.465 Y6.426 E.06481
G1 X106.465 Y5.892 E.0164
G1 X105.508 Y4.935 E.04161
G1 X106.041 Y4.935 E.0164
G1 X106.634 Y5.528 E.02578
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X106.041 Y4.935 E-.3187
G1 X105.508 Y4.935 E-.20276
G1 X105.952 Y5.379 E-.23854
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 8/40
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
G17
G3 Z1.8 I1.217 J0 P1  F30000
; object ids of layer 8 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer8 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z2 F30000
G1 X160.4 Y8 Z2
G1 Z1.6
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z2 F30000
G1 X114.002 Y8.498 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
M73 P69 R10
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z2 F30000
G1 X93.502 Y73.11 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z2 F30000
G1 X97.11 Y46.302 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.502 E.38466
G1 X90.798 Y28.502 E.05805
G1 X90.798 Y22.398 E.20249
G1 X92.548 Y22.398 E.05805
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X99.002 Y22.398 E.05805
G1 X99.002 Y28.502 E.20249
G1 X97.252 Y28.502 E.05805
G1 X97.252 Y40.098 E.38466
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y29.069 E.35094
G1 X92.94 Y28.669 E.01229
G1 F9901.871
G1 X92.94 Y28.269 E.01229
G1 F3789.734
G1 X92.94 Y28.11 E.00489
G1 F2160
G1 X91.19 Y28.11 E.05377
G1 X91.19 Y22.831 E.16221
G1 F2536.674
G1 X91.19 Y22.79 E.00126
G1 F7799.139
G1 X91.59 Y22.79 E.01229
G1 F12000
G1 X91.99 Y22.79 E.01229
G1 X92.94 Y22.79 E.02919
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X97.81 Y22.79 E.02919
G1 X98.21 Y22.79 E.01229
G1 F7799.139
G1 X98.61 Y22.79 E.01229
G1 F2536.674
G1 X98.61 Y22.831 E.00126
G1 F2160
G1 X98.61 Y28.11 E.16221
G1 X96.86 Y28.11 E.05377
G1 F3789.734
G1 X96.86 Y28.269 E.00489
G1 F9901.871
G1 X96.86 Y28.669 E.01229
G1 F12000
G1 X96.86 Y29.069 E.01229
G1 X96.86 Y40.49 E.35094
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z2 F30000
G1 X35.102 Y45.91 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.502 E.38466
G1 X28.398 Y28.502 E.05805
G1 X28.398 Y22.398 E.20249
G1 X30.148 Y22.398 E.05805
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.602 Y22.398 E.05805
G1 X36.602 Y28.502 E.20249
G1 X34.852 Y28.502 E.05805
G1 X34.852 Y40.098 E.38466
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y29.069 E.35094
G1 X30.54 Y28.669 E.01229
G1 F9901.871
G1 X30.54 Y28.269 E.01229
G1 F3789.734
G1 X30.54 Y28.11 E.00489
G1 F2160
G1 X28.79 Y28.11 E.05377
G1 X28.79 Y22.831 E.16221
G1 F2536.674
G1 X28.79 Y22.79 E.00126
G1 F7799.139
G1 X29.19 Y22.79 E.01229
G1 F12000
G1 X29.59 Y22.79 E.01229
G1 X30.54 Y22.79 E.02919
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X35.41 Y22.79 E.02919
G1 X35.81 Y22.79 E.01229
G1 F7799.139
G1 X36.21 Y22.79 E.01229
G1 F2536.674
G1 X36.21 Y22.831 E.00126
G1 F2160
G1 X36.21 Y28.11 E.16221
G1 X34.46 Y28.11 E.05377
G1 F3789.734
G1 X34.46 Y28.269 E.00489
G1 F9901.871
G1 X34.46 Y28.669 E.01229
G1 F12000
G1 X34.46 Y29.069 E.01229
G1 X34.46 Y40.49 E.35094
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.97 Y53.505 Z2 F30000
G1 X33.65 Y73.5 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.486 E.00746
G3 X33.425 Y67.911 I.274 J-2.788 E.27367
G1 X33.7 Y67.897 E.00912
G3 X33.71 Y73.499 I0 J2.801 E.29158
G1 X33.67 Y73.107 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.23 Y73.061 E.01358
G3 X33.464 Y68.301 I.47 J-2.363 E.21072
G1 X33.7 Y68.29 E.00727
G3 X33.73 Y73.107 I0 J2.409 E.23162
; WIPE_START
M204 S10000
G1 X33.23 Y73.061 E-.19055
G1 X32.778 Y72.927 E-.17942
G1 X32.361 Y72.704 E-.17956
G1 X31.996 Y72.404 E-.17954
G1 X31.944 Y72.341 E-.03094
; WIPE_END
G1 E-.04 F1800
G1 X39.355 Y74.169 Z2 F30000
G1 X106.798 Y90.798 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X105.872 Y90.634 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42021
G1 F15000
G1 X106.465 Y90.041 E.02578
G1 X106.465 Y89.508 E.0164
G1 X105.508 Y90.465 E.04161
G1 X104.974 Y90.465 E.0164
G1 X106.465 Y88.974 E.06481
G1 X106.465 Y88.441 E.0164
G1 X104.441 Y90.465 E.088
G1 X103.907 Y90.465 E.0164
G1 X106.465 Y87.907 E.1112
G1 X106.465 Y87.373 E.0164
G1 X103.373 Y90.465 E.1344
G1 X102.84 Y90.465 E.0164
G1 X106.465 Y86.84 E.1576
G1 X106.465 Y86.306 E.0164
G1 X102.306 Y90.465 E.1808
G1 X101.773 Y90.465 E.0164
G1 X106.465 Y85.773 E.204
G1 X106.465 Y85.239 E.0164
G1 X101.239 Y90.465 E.2272
G1 X100.706 Y90.465 E.0164
G1 X106.465 Y84.706 E.2504
G1 X106.465 Y84.172 E.0164
G1 X100.172 Y90.465 E.2736
G1 X99.639 Y90.465 E.0164
G1 X106.465 Y83.639 E.2968
G1 X106.465 Y83.105 E.0164
G1 X99.105 Y90.465 E.32
G1 X98.571 Y90.465 E.0164
G1 X106.465 Y82.571 E.34319
G1 X106.465 Y82.038 E.0164
G1 X98.038 Y90.465 E.36639
G1 X97.504 Y90.465 E.0164
G1 X106.465 Y81.504 E.38959
G1 X106.465 Y80.971 E.0164
G1 X96.971 Y90.465 E.41279
G1 X96.437 Y90.465 E.0164
G1 X106.465 Y80.437 E.43599
G1 X106.465 Y79.904 E.0164
G1 X95.904 Y90.465 E.45919
G1 X95.37 Y90.465 E.0164
G1 X106.465 Y79.37 E.48239
G1 X106.465 Y78.836 E.0164
G1 X94.836 Y90.465 E.50559
G1 X94.303 Y90.465 E.0164
G1 X106.465 Y78.303 E.52879
G1 X106.465 Y77.769 E.0164
G1 X93.769 Y90.465 E.55199
G1 X93.236 Y90.465 E.0164
G1 X106.465 Y77.236 E.57519
G1 X106.465 Y76.702 E.0164
G1 X92.702 Y90.465 E.59838
G1 X92.169 Y90.465 E.0164
G1 X106.465 Y76.169 E.62158
G1 X106.465 Y75.635 E.0164
G1 X91.635 Y90.465 E.64478
G1 X91.101 Y90.465 E.0164
G1 X106.465 Y75.101 E.66798
G1 X106.465 Y74.568 E.0164
G1 X90.568 Y90.465 E.69118
G1 X90.034 Y90.465 E.0164
G1 X106.465 Y74.034 E.71438
G1 X106.465 Y73.501 E.0164
G1 X89.501 Y90.465 E.73758
G1 X88.967 Y90.465 E.0164
G1 X106.465 Y72.967 E.76078
G1 X106.465 Y72.434 E.0164
G1 X88.434 Y90.465 E.78398
G1 X87.9 Y90.465 E.0164
G1 X106.465 Y71.9 E.80718
G1 X106.465 Y71.366 E.0164
G1 X87.366 Y90.465 E.83037
G1 X86.833 Y90.465 E.0164
G1 X106.465 Y70.833 E.85357
G1 X106.465 Y70.299 E.0164
G1 X86.299 Y90.465 E.87677
G1 X85.766 Y90.465 E.0164
G1 X106.465 Y69.766 E.89997
G1 X106.465 Y69.232 E.0164
G1 X85.232 Y90.465 E.92317
G1 X84.699 Y90.465 E.0164
G1 X106.465 Y68.699 E.94637
G1 X106.465 Y68.165 E.0164
G1 X84.165 Y90.465 E.96957
G1 X83.631 Y90.465 E.0164
G1 X106.465 Y67.631 E.99277
G1 X106.465 Y67.098 E.0164
G1 X83.098 Y90.465 E1.01597
G1 X82.564 Y90.465 E.0164
G1 X106.465 Y66.564 E1.03917
G1 X106.465 Y66.031 E.0164
G1 X82.031 Y90.465 E1.06237
G1 X81.497 Y90.465 E.0164
G1 X106.465 Y65.497 E1.08556
G1 X106.465 Y64.964 E.0164
G1 X80.964 Y90.465 E1.10876
G1 X80.43 Y90.465 E.0164
G1 X106.465 Y64.43 E1.13196
G1 X106.465 Y63.896 E.0164
G1 X79.896 Y90.465 E1.15516
G1 X79.363 Y90.465 E.0164
G1 X106.465 Y63.363 E1.17836
G1 X106.465 Y62.829 E.0164
G1 X78.829 Y90.465 E1.20156
G1 X78.296 Y90.465 E.0164
G1 X106.465 Y62.296 E1.22476
G1 X106.465 Y61.762 E.0164
G1 X77.762 Y90.465 E1.24796
G1 X77.229 Y90.465 E.0164
G1 X106.465 Y61.229 E1.27116
G1 X106.465 Y60.695 E.0164
G1 X93.835 Y73.324 E.54911
G1 X93.835 Y72.791 E.0164
G1 X106.465 Y60.161 E.54911
G1 X106.465 Y59.628 E.0164
G1 X93.835 Y72.257 E.54911
G1 X93.835 Y71.724 E.0164
G1 X106.465 Y59.094 E.54911
G1 X106.465 Y58.561 E.0164
G1 X93.835 Y71.19 E.54911
G1 X93.835 Y70.657 E.0164
G1 X106.465 Y58.027 E.54911
G1 X106.465 Y57.494 E.0164
G1 X93.835 Y70.123 E.54911
G1 X93.835 Y69.589 E.0164
G1 X106.465 Y56.96 E.54911
G1 X106.465 Y56.427 E.0164
G1 X93.835 Y69.056 E.54911
G1 X93.835 Y68.522 E.0164
G1 X106.465 Y55.893 E.54911
G1 X106.465 Y55.359 E.0164
G1 X93.835 Y67.989 E.54911
G1 X93.835 Y67.565 E.01304
G1 X93.726 Y67.565 E.00337
G1 X106.465 Y54.826 E.55388
G1 X106.465 Y54.292 E.0164
G1 X93.192 Y67.565 E.57707
G1 X92.659 Y67.565 E.0164
G1 X106.465 Y53.759 E.60027
G1 X106.465 Y53.225 E.0164
G1 X92.125 Y67.565 E.62347
G1 X91.592 Y67.565 E.0164
G1 X106.465 Y52.692 E.64667
G1 X106.465 Y52.158 E.0164
G1 X91.058 Y67.565 E.66987
G1 X90.524 Y67.565 E.0164
G1 X106.465 Y51.624 E.69307
G1 X106.465 Y51.091 E.0164
G1 X89.991 Y67.565 E.71627
G1 X89.457 Y67.565 E.0164
G1 X106.465 Y50.557 E.73947
G1 X106.465 Y50.024 E.0164
G1 X88.924 Y67.565 E.76267
G1 X88.39 Y67.565 E.0164
G1 X106.465 Y49.49 E.78587
G1 X106.465 Y48.957 E.0164
G1 X87.857 Y67.565 E.80907
G1 X87.323 Y67.565 E.0164
G1 X106.465 Y48.423 E.83226
G1 X106.465 Y47.889 E.0164
G1 X86.789 Y67.565 E.85546
G1 X86.256 Y67.565 E.0164
G1 X106.465 Y47.356 E.87866
G1 X106.465 Y46.822 E.0164
G1 X85.722 Y67.565 E.90186
G1 X85.189 Y67.565 E.0164
G1 X106.465 Y46.289 E.92506
G1 X106.465 Y45.755 E.0164
G1 X84.655 Y67.565 E.94826
G1 X84.122 Y67.565 E.0164
G1 X106.465 Y45.222 E.97146
G1 X106.465 Y44.688 E.0164
G1 X60.688 Y90.465 E1.99033
G1 X61.222 Y90.465 E.0164
G1 X83.565 Y68.122 E.97146
G1 X83.565 Y68.655 E.0164
G1 X61.755 Y90.465 E.94826
G1 X62.289 Y90.465 E.0164
G1 X83.565 Y69.189 E.92506
G1 X83.565 Y69.722 E.0164
G1 X62.822 Y90.465 E.90186
G1 X63.356 Y90.465 E.0164
G1 X83.565 Y70.256 E.87866
G1 X83.565 Y70.789 E.0164
G1 X63.889 Y90.465 E.85546
G1 X64.423 Y90.465 E.0164
G1 X83.565 Y71.323 E.83226
G1 X83.565 Y71.857 E.0164
G1 X64.957 Y90.465 E.80907
G1 X65.49 Y90.465 E.0164
G1 X83.565 Y72.39 E.78587
G1 X83.565 Y72.924 E.0164
G1 X66.024 Y90.465 E.76267
G1 X66.557 Y90.465 E.0164
G1 X83.565 Y73.457 E.73947
G1 X83.565 Y73.835 E.01162
G1 X83.72 Y73.835 E.00478
G1 X67.091 Y90.465 E.72303
G1 X67.624 Y90.465 E.0164
G1 X84.254 Y73.835 E.72303
G1 X84.787 Y73.835 E.0164
G1 X68.158 Y90.465 E.72303
G1 X68.692 Y90.465 E.0164
G1 X85.321 Y73.835 E.72303
G1 X85.854 Y73.835 E.0164
G1 X69.225 Y90.465 E.72303
G1 X69.759 Y90.465 E.0164
G1 X86.388 Y73.835 E.72303
G1 X86.922 Y73.835 E.0164
G1 X70.292 Y90.465 E.72303
G1 X70.826 Y90.465 E.0164
G1 X87.455 Y73.835 E.72303
G1 X87.989 Y73.835 E.0164
G1 X71.359 Y90.465 E.72303
G1 X71.893 Y90.465 E.0164
G1 X88.522 Y73.835 E.72303
G1 X89.056 Y73.835 E.0164
G1 X72.426 Y90.465 E.72303
G1 X72.96 Y90.465 E.0164
G1 X89.589 Y73.835 E.72303
G1 X90.123 Y73.835 E.0164
G1 X73.494 Y90.465 E.72303
G1 X74.027 Y90.465 E.0164
G1 X90.657 Y73.835 E.72303
G1 X91.19 Y73.835 E.0164
G1 X74.561 Y90.465 E.72303
G1 X75.094 Y90.465 E.0164
G1 X91.724 Y73.835 E.72303
G1 X92.257 Y73.835 E.0164
G1 X75.628 Y90.465 E.72303
G1 X76.161 Y90.465 E.0164
G1 X92.791 Y73.835 E.72303
G1 X93.324 Y73.835 E.0164
G1 X76.525 Y90.634 E.73041
G1 X59.985 Y90.634 F30000
G1 F15000
G1 X106.465 Y44.154 E2.02091
G1 X106.465 Y43.621 E.0164
G1 X59.621 Y90.465 E2.03673
G1 X59.087 Y90.465 E.0164
G1 X106.465 Y43.087 E2.05993
G1 X106.465 Y42.554 E.0164
G1 X58.554 Y90.465 E2.08313
G1 X58.02 Y90.465 E.0164
G1 X106.465 Y42.02 E2.10632
G1 X106.465 Y41.487 E.0164
M73 P70 R10
G1 X57.487 Y90.465 E2.12952
G1 X56.953 Y90.465 E.0164
G1 X106.465 Y40.953 E2.15272
G1 X106.465 Y40.419 E.0164
G1 X56.419 Y90.465 E2.17592
G1 X55.886 Y90.465 E.0164
G1 X106.465 Y39.886 E2.19912
G1 X106.465 Y39.352 E.0164
G1 X55.352 Y90.465 E2.22232
G1 X54.819 Y90.465 E.0164
G1 X106.465 Y38.819 E2.24552
G1 X106.465 Y38.285 E.0164
G1 X54.285 Y90.465 E2.26872
G1 X53.752 Y90.465 E.0164
G1 X106.465 Y37.752 E2.29192
G1 X106.465 Y37.218 E.0164
G1 X97.835 Y45.847 E.3752
G1 X97.835 Y45.314 E.0164
G1 X106.465 Y36.684 E.3752
G1 X106.465 Y36.151 E.0164
G1 X97.835 Y44.78 E.3752
G1 X97.835 Y44.247 E.0164
G1 X106.465 Y35.617 E.3752
G1 X106.465 Y35.084 E.0164
G1 X97.835 Y43.713 E.3752
G1 X97.835 Y43.18 E.0164
G1 X106.465 Y34.55 E.3752
G1 X106.465 Y34.017 E.0164
G1 X97.835 Y42.646 E.3752
G1 X97.835 Y42.112 E.0164
G1 X106.465 Y33.483 E.3752
G1 X106.465 Y32.949 E.0164
G1 X97.835 Y41.579 E.3752
G1 X97.835 Y41.045 E.0164
G1 X106.465 Y32.416 E.3752
G1 X106.465 Y31.882 E.0164
G1 X97.835 Y40.512 E.3752
G1 X97.835 Y39.978 E.0164
G1 X106.465 Y31.349 E.3752
G1 X106.465 Y30.815 E.0164
G1 X97.585 Y39.695 E.38607
G1 X97.585 Y39.161 E.0164
G1 X106.465 Y30.282 E.38607
G1 X106.465 Y29.748 E.0164
G1 X97.585 Y38.627 E.38607
G1 X97.585 Y38.094 E.0164
G1 X106.465 Y29.215 E.38607
G1 X106.465 Y28.681 E.0164
G1 X97.585 Y37.56 E.38607
G1 X97.585 Y37.027 E.0164
G1 X106.465 Y28.147 E.38607
G1 X106.465 Y27.614 E.0164
G1 X97.585 Y36.493 E.38607
G1 X97.585 Y35.96 E.0164
G1 X106.465 Y27.08 E.38607
G1 X106.465 Y26.547 E.0164
G1 X97.585 Y35.426 E.38607
G1 X97.585 Y34.892 E.0164
G1 X106.465 Y26.013 E.38607
G1 X106.465 Y25.48 E.0164
G1 X97.585 Y34.359 E.38607
G1 X97.585 Y33.825 E.0164
G1 X106.465 Y24.946 E.38607
G1 X106.465 Y24.412 E.0164
G1 X97.585 Y33.292 E.38607
G1 X97.585 Y32.758 E.0164
G1 X106.465 Y23.879 E.38607
M73 P70 R9
G1 X106.465 Y23.345 E.0164
G1 X97.585 Y32.225 E.38607
G1 X97.585 Y31.691 E.0164
G1 X106.465 Y22.812 E.38607
G1 X106.465 Y22.278 E.0164
G1 X97.585 Y31.157 E.38607
G1 X97.585 Y30.624 E.0164
G1 X106.465 Y21.745 E.38607
G1 X106.465 Y21.211 E.0164
G1 X99.335 Y28.34 E.30998
G1 X99.335 Y27.807 E.0164
G1 X106.465 Y20.677 E.30998
G1 X106.465 Y20.144 E.0164
G1 X99.335 Y27.273 E.30998
G1 X99.335 Y26.74 E.0164
G1 X106.465 Y19.61 E.30998
G1 X106.465 Y19.077 E.0164
G1 X99.335 Y26.206 E.30998
G1 X99.335 Y25.672 E.0164
G1 X106.465 Y18.543 E.30998
G1 X106.465 Y18.01 E.0164
G1 X99.335 Y25.139 E.30998
G1 X99.335 Y24.605 E.0164
G1 X106.465 Y17.476 E.30998
G1 X106.465 Y16.942 E.0164
G1 X99.335 Y24.072 E.30998
G1 X99.335 Y23.538 E.0164
G1 X106.465 Y16.409 E.30998
G1 X106.465 Y15.875 E.0164
G1 X99.335 Y23.005 E.30998
G1 X99.335 Y22.471 E.0164
G1 X106.465 Y15.342 E.30998
G1 X106.465 Y14.808 E.0164
G1 X99.208 Y22.065 E.31551
G1 X98.675 Y22.065 E.0164
G1 X106.465 Y14.275 E.33871
G1 X106.465 Y13.741 E.0164
G1 X98.141 Y22.065 E.3619
G1 X97.607 Y22.065 E.0164
G1 X106.465 Y13.207 E.3851
G1 X106.465 Y12.674 E.0164
G1 X97.374 Y21.765 E.39526
G1 X96.84 Y21.765 E.0164
G1 X106.465 Y12.14 E.41846
G1 X106.465 Y11.607 E.0164
G1 X96.307 Y21.765 E.44166
G1 X95.773 Y21.765 E.0164
G1 X106.465 Y11.073 E.46486
G1 X106.465 Y10.54 E.0164
G1 X95.24 Y21.765 E.48806
G1 X94.706 Y21.765 E.0164
G1 X106.465 Y10.006 E.51125
G1 X106.465 Y9.472 E.0164
G1 X94.172 Y21.765 E.53445
G1 X93.639 Y21.765 E.0164
G1 X106.465 Y8.939 E.55765
G1 X106.465 Y8.405 E.0164
G1 X93.105 Y21.765 E.58085
G1 X92.572 Y21.765 E.0164
G1 X106.465 Y7.872 E.60405
G1 X106.465 Y7.338 E.0164
G1 X91.738 Y22.065 E.64029
G1 X91.205 Y22.065 E.0164
G1 X106.465 Y6.805 E.66349
G1 X106.465 Y6.271 E.0164
G1 X22.271 Y90.465 E3.66066
G1 X22.805 Y90.465 E.0164
G1 X90.465 Y22.805 E2.9418
G1 X90.465 Y23.338 E.0164
G1 X23.338 Y90.465 E2.9186
G1 X23.872 Y90.465 E.0164
G1 X90.465 Y23.872 E2.8954
G1 X90.465 Y24.405 E.0164
G1 X24.405 Y90.465 E2.8722
G1 X24.939 Y90.465 E.0164
G1 X90.465 Y24.939 E2.849
G1 X90.465 Y25.472 E.0164
G1 X25.472 Y90.465 E2.8258
G1 X26.006 Y90.465 E.0164
G1 X90.465 Y26.006 E2.8026
G1 X90.465 Y26.54 E.0164
G1 X26.54 Y90.465 E2.7794
G1 X27.073 Y90.465 E.0164
G1 X90.465 Y27.073 E2.75621
G1 X90.465 Y27.607 E.0164
G1 X27.607 Y90.465 E2.73301
G1 X28.14 Y90.465 E.0164
G1 X90.465 Y28.14 E2.70981
G1 X90.465 Y28.674 E.0164
G1 X28.674 Y90.465 E2.68661
G1 X29.207 Y90.465 E.0164
G1 X90.837 Y28.835 E2.67959
G1 X91.37 Y28.835 E.0164
G1 X29.741 Y90.465 E2.67959
G1 X30.275 Y90.465 E.0164
G1 X91.904 Y28.835 E2.67959
G1 X92.215 Y28.835 E.00955
G1 X92.215 Y29.058 E.00685
G1 X30.808 Y90.465 E2.6699
G1 X31.342 Y90.465 E.0164
G1 X92.215 Y29.592 E2.6467
G1 X92.215 Y30.125 E.0164
G1 X31.875 Y90.465 E2.6235
G1 X32.409 Y90.465 E.0164
G1 X92.215 Y30.659 E2.6003
G1 X92.215 Y31.192 E.0164
G1 X32.942 Y90.465 E2.5771
G1 X33.476 Y90.465 E.0164
G1 X92.215 Y31.726 E2.5539
G1 X92.215 Y32.26 E.0164
G1 X34.01 Y90.465 E2.53071
G1 X34.543 Y90.465 E.0164
G1 X92.215 Y32.793 E2.50751
G1 X92.215 Y33.327 E.0164
G1 X35.077 Y90.465 E2.48431
G1 X35.61 Y90.465 E.0164
G1 X92.215 Y33.86 E2.46111
G1 X92.215 Y34.394 E.0164
G1 X36.144 Y90.465 E2.43791
G1 X36.677 Y90.465 E.0164
G1 X92.215 Y34.927 E2.41471
G1 X92.215 Y35.461 E.0164
G1 X37.211 Y90.465 E2.39151
G1 X37.745 Y90.465 E.0164
G1 X92.215 Y35.995 E2.36831
G1 X92.215 Y36.528 E.0164
G1 X38.278 Y90.465 E2.34511
G1 X38.812 Y90.465 E.0164
G1 X92.215 Y37.062 E2.32191
G1 X92.215 Y37.595 E.0164
G1 X39.345 Y90.465 E2.29872
G1 X39.879 Y90.465 E.0164
G1 X92.215 Y38.129 E2.27552
G1 X92.215 Y38.662 E.0164
G1 X40.412 Y90.465 E2.25232
G1 X40.946 Y90.465 E.0164
G1 X92.215 Y39.196 E2.22912
G1 X92.215 Y39.73 E.0164
G1 X41.48 Y90.465 E2.20592
G1 X42.013 Y90.465 E.0164
G1 X91.965 Y40.513 E2.17185
G1 X91.965 Y41.047 E.0164
G1 X42.547 Y90.465 E2.14865
G1 X43.08 Y90.465 E.0164
G1 X91.965 Y41.58 E2.12545
G1 X91.965 Y42.114 E.0164
G1 X43.614 Y90.465 E2.10225
G1 X44.147 Y90.465 E.0164
G1 X91.965 Y42.647 E2.07905
G1 X91.965 Y43.181 E.0164
G1 X44.681 Y90.465 E2.05585
G1 X45.214 Y90.465 E.0164
G1 X91.965 Y43.715 E2.03266
G1 X91.965 Y44.248 E.0164
G1 X45.748 Y90.465 E2.00946
G1 X46.282 Y90.465 E.0164
G1 X91.965 Y44.782 E1.98626
G1 X91.965 Y45.315 E.0164
G1 X46.815 Y90.465 E1.96306
G1 X47.349 Y90.465 E.0164
G1 X91.965 Y45.849 E1.93986
G1 X91.965 Y46.382 E.0164
G1 X47.882 Y90.465 E1.91666
G1 X48.416 Y90.465 E.0164
G1 X92.245 Y46.635 E1.90566
G1 X92.779 Y46.635 E.0164
G1 X48.949 Y90.465 E1.90566
G1 X49.483 Y90.465 E.0164
G1 X93.312 Y46.635 E1.90566
G1 X93.846 Y46.635 E.0164
G1 X50.017 Y90.465 E1.90566
G1 X50.55 Y90.465 E.0164
G1 X94.38 Y46.635 E1.90566
G1 X94.913 Y46.635 E.0164
G1 X51.084 Y90.465 E1.90566
G1 X51.617 Y90.465 E.0164
G1 X95.447 Y46.635 E1.90566
G1 X95.98 Y46.635 E.0164
G1 X52.151 Y90.465 E1.90566
G1 X52.684 Y90.465 E.0164
G1 X96.514 Y46.635 E1.90566
G1 X97.047 Y46.635 E.0164
G1 X53.048 Y90.634 E1.91304
G1 X21.568 Y90.634 F30000
G1 F15000
M73 P71 R9
G1 X106.465 Y5.737 E3.69124
G1 X106.465 Y5.204 E.0164
G1 X21.204 Y90.465 E3.70706
G1 X20.935 Y90.465 E.00826
G1 X20.935 Y90.2 E.00815
G1 X106.2 Y4.935 E3.70722
G1 X105.666 Y4.935 E.0164
G1 X20.935 Y89.666 E3.68402
G1 X20.935 Y89.133 E.0164
G1 X105.133 Y4.935 E3.66082
G1 X104.599 Y4.935 E.0164
G1 X20.935 Y88.599 E3.63762
G1 X20.935 Y88.065 E.0164
G1 X104.065 Y4.935 E3.61442
G1 X103.532 Y4.935 E.0164
G1 X36.615 Y71.852 E2.90949
G2 X36.803 Y71.131 I-3.032 J-1.176 E.02298
G1 X102.998 Y4.935 E2.87811
G1 X102.465 Y4.935 E.0164
G1 X36.83 Y70.57 E2.85373
G2 X36.776 Y70.09 I-2.463 J.032 E.01487
G1 X101.931 Y4.935 E2.83287
G1 X101.398 Y4.935 E.0164
G1 X36.66 Y69.673 E2.81474
G2 X36.502 Y69.297 I-1.992 J.616 E.01255
G1 X100.864 Y4.935 E2.7984
G1 X100.33 Y4.935 E.0164
G1 X36.308 Y68.957 E2.78363
G2 X36.076 Y68.656 I-1.638 J1.023 E.01171
G1 X99.797 Y4.935 E2.77054
G1 X99.263 Y4.935 E.0164
G1 X35.812 Y68.386 E2.7588
G2 X35.517 Y68.148 I-1.356 J1.373 E.01168
G1 X98.73 Y4.935 E2.74842
G1 X98.196 Y4.935 E.0164
G1 X35.19 Y67.941 E2.73943
G2 X34.823 Y67.775 I-2.153 J4.265 E.0124
G1 X97.663 Y4.935 E2.7322
G1 X97.129 Y4.935 E.0164
G1 X34.415 Y67.65 E2.72676
G2 X33.955 Y67.576 I-.795 J3.496 E.01433
G1 X96.595 Y4.935 E2.72356
G1 X96.062 Y4.935 E.0164
G1 X33.42 Y67.577 E2.72362
G2 X32.751 Y67.712 I.101 J2.223 E.02105
G1 X95.528 Y4.935 E2.72948
G1 X94.995 Y4.935 E.0164
G1 X20.935 Y78.995 E3.22004
G1 X20.935 Y79.528 E.0164
G1 X30.712 Y69.751 E.42509
G2 X30.577 Y70.42 I2.087 J.769 E.02105
G1 X20.935 Y80.062 E.41922
G1 X20.935 Y80.595 E.0164
G1 X30.576 Y70.955 E.41917
G2 X30.65 Y71.415 I3.572 J-.335 E.01433
G1 X20.935 Y81.129 E.42237
G1 X20.935 Y81.663 E.0164
G1 X30.775 Y71.823 E.42781
G2 X30.941 Y72.19 I4.445 J-1.792 E.0124
G1 X20.935 Y82.196 E.43504
G1 X20.935 Y82.73 E.0164
G1 X31.148 Y72.517 E.44402
G2 X31.386 Y72.812 I1.611 J-1.061 E.01168
G1 X20.935 Y83.263 E.45441
G1 X20.935 Y83.797 E.0164
G1 X31.656 Y73.076 E.46614
G2 X31.958 Y73.308 I3.815 J-4.637 E.0117
G1 X20.935 Y84.33 E.47924
G1 X20.935 Y84.864 E.0164
G1 X32.297 Y73.502 E.49401
G2 X32.673 Y73.66 I.991 J-1.834 E.01255
G1 X20.935 Y85.398 E.51035
G1 X20.935 Y85.931 E.0164
G1 X33.09 Y73.776 E.52847
G2 X33.57 Y73.83 I.512 J-2.41 E.01487
G1 X20.935 Y86.465 E.54934
G1 X20.935 Y86.998 E.0164
G1 X34.131 Y73.803 E.57372
G2 X34.852 Y73.615 I-.455 J-3.222 E.02298
G1 X20.766 Y87.702 E.61248
G1 X20.766 Y78.631 F30000
G1 F15000
G1 X94.461 Y4.935 E3.20421
G1 X93.928 Y4.935 E.0164
G1 X20.935 Y77.928 E3.17364
G1 X20.935 Y77.394 E.0164
G1 X93.394 Y4.935 E3.15044
G1 X92.861 Y4.935 E.0164
G1 X20.935 Y76.86 E3.12724
G1 X20.935 Y76.327 E.0164
G1 X92.327 Y4.935 E3.10404
G1 X91.793 Y4.935 E.0164
G1 X20.935 Y75.793 E3.08084
G1 X20.935 Y75.26 E.0164
G1 X91.26 Y4.935 E3.05764
G1 X90.726 Y4.935 E.0164
G1 X20.935 Y74.726 E3.03444
G1 X20.935 Y74.193 E.0164
G1 X90.193 Y4.935 E3.01125
G1 X89.659 Y4.935 E.0164
G1 X20.935 Y73.659 E2.98805
G1 X20.935 Y73.125 E.0164
G1 X89.126 Y4.935 E2.96485
G1 X88.592 Y4.935 E.0164
G1 X20.935 Y72.592 E2.94165
G1 X20.935 Y72.058 E.0164
G1 X88.058 Y4.935 E2.91845
G1 X87.525 Y4.935 E.0164
G1 X20.935 Y71.525 E2.89525
G1 X20.935 Y70.991 E.0164
G1 X86.991 Y4.935 E2.87205
G1 X86.458 Y4.935 E.0164
G1 X20.935 Y70.458 E2.84885
G1 X20.935 Y69.924 E.0164
G1 X85.924 Y4.935 E2.82565
G1 X85.391 Y4.935 E.0164
G1 X20.935 Y69.391 E2.80245
M73 P72 R9
G1 X20.935 Y68.857 E.0164
G1 X84.857 Y4.935 E2.77925
G1 X84.323 Y4.935 E.0164
G1 X20.935 Y68.323 E2.75606
G1 X20.935 Y67.79 E.0164
G1 X83.79 Y4.935 E2.73286
G1 X83.256 Y4.935 E.0164
G1 X20.935 Y67.256 E2.70966
G1 X20.935 Y66.723 E.0164
G1 X82.723 Y4.935 E2.68646
G1 X82.189 Y4.935 E.0164
G1 X20.935 Y66.189 E2.66326
G1 X20.935 Y65.656 E.0164
G1 X81.656 Y4.935 E2.64006
G1 X81.122 Y4.935 E.0164
G1 X20.935 Y65.122 E2.61686
G1 X20.935 Y64.588 E.0164
G1 X80.588 Y4.935 E2.59366
G1 X80.055 Y4.935 E.0164
G1 X20.935 Y64.055 E2.57046
G1 X20.935 Y63.521 E.0164
G1 X79.521 Y4.935 E2.54726
G1 X78.988 Y4.935 E.0164
G1 X20.935 Y62.988 E2.52406
G1 X20.935 Y62.454 E.0164
G1 X78.454 Y4.935 E2.50087
G1 X77.921 Y4.935 E.0164
G1 X20.935 Y61.921 E2.47767
G1 X20.935 Y61.387 E.0164
G1 X77.387 Y4.935 E2.45447
G1 X76.853 Y4.935 E.0164
G1 X20.935 Y60.853 E2.43127
G1 X20.935 Y60.32 E.0164
G1 X34.62 Y46.635 E.59499
G1 X34.086 Y46.635 E.0164
G1 X20.935 Y59.786 E.57179
G1 X20.935 Y59.253 E.0164
G1 X33.553 Y46.635 E.54859
G1 X33.019 Y46.635 E.0164
G1 X20.935 Y58.719 E.52539
G1 X20.935 Y58.186 E.0164
G1 X32.486 Y46.635 E.50219
G1 X31.952 Y46.635 E.0164
G1 X20.935 Y57.652 E.479
G1 X20.935 Y57.118 E.0164
G1 X31.418 Y46.635 E.4558
G1 X30.885 Y46.635 E.0164
G1 X20.935 Y56.585 E.4326
G1 X20.935 Y56.051 E.0164
G1 X30.351 Y46.635 E.4094
G1 X29.818 Y46.635 E.0164
G1 X20.935 Y55.518 E.3862
G1 X20.935 Y54.984 E.0164
G1 X29.565 Y46.355 E.3752
G1 X29.565 Y45.821 E.0164
G1 X20.935 Y54.451 E.3752
G1 X20.935 Y53.917 E.0164
G1 X29.565 Y45.288 E.3752
G1 X29.565 Y44.754 E.0164
G1 X20.935 Y53.383 E.3752
G1 X20.935 Y52.85 E.0164
G1 X29.565 Y44.221 E.3752
G1 X29.565 Y43.687 E.0164
G1 X20.935 Y52.316 E.3752
G1 X20.935 Y51.783 E.0164
G1 X29.565 Y43.153 E.3752
G1 X29.565 Y42.62 E.0164
G1 X20.935 Y51.249 E.3752
G1 X20.935 Y50.716 E.0164
G1 X29.565 Y42.086 E.3752
G1 X29.565 Y41.553 E.0164
G1 X20.935 Y50.182 E.3752
G1 X20.935 Y49.648 E.0164
G1 X29.565 Y41.019 E.3752
G1 X29.565 Y40.486 E.0164
G1 X20.935 Y49.115 E.3752
G1 X20.935 Y48.581 E.0164
G1 X29.815 Y39.702 E.38607
G1 X29.815 Y39.168 E.0164
G1 X20.935 Y48.048 E.38607
G1 X20.935 Y47.514 E.0164
G1 X29.815 Y38.635 E.38607
G1 X29.815 Y38.101 E.0164
G1 X20.935 Y46.981 E.38607
G1 X20.935 Y46.447 E.0164
G1 X29.815 Y37.568 E.38607
G1 X29.815 Y37.034 E.0164
G1 X20.935 Y45.913 E.38607
G1 X20.935 Y45.38 E.0164
G1 X29.815 Y36.501 E.38607
G1 X29.815 Y35.967 E.0164
G1 X20.935 Y44.846 E.38607
G1 X20.935 Y44.313 E.0164
G1 X29.815 Y35.433 E.38607
G1 X29.815 Y34.9 E.0164
G1 X20.935 Y43.779 E.38607
G1 X20.935 Y43.246 E.0164
G1 X29.815 Y34.366 E.38607
G1 X29.815 Y33.833 E.0164
G1 X20.935 Y42.712 E.38607
G1 X20.935 Y42.179 E.0164
G1 X29.815 Y33.299 E.38607
G1 X29.815 Y32.766 E.0164
G1 X20.935 Y41.645 E.38607
G1 X20.935 Y41.111 E.0164
G1 X29.815 Y32.232 E.38607
G1 X29.815 Y31.698 E.0164
G1 X20.935 Y40.578 E.38607
G1 X20.935 Y40.044 E.0164
G1 X29.815 Y31.165 E.38607
G1 X29.815 Y30.631 E.0164
G1 X20.935 Y39.511 E.38607
G1 X20.935 Y38.977 E.0164
G1 X29.815 Y30.098 E.38607
G1 X29.815 Y29.564 E.0164
G1 X20.935 Y38.444 E.38607
G1 X20.935 Y37.91 E.0164
G1 X29.815 Y29.031 E.38607
G1 X29.815 Y28.835 E.006
G1 X29.476 Y28.835 E.0104
G1 X20.935 Y37.376 E.37136
G1 X20.935 Y36.843 E.0164
G1 X28.943 Y28.835 E.34816
G1 X28.409 Y28.835 E.0164
G1 X20.935 Y36.309 E.32496
M73 P73 R9
G1 X20.935 Y35.776 E.0164
G1 X28.065 Y28.646 E.30998
G1 X28.065 Y28.113 E.0164
G1 X20.935 Y35.242 E.30998
G1 X20.935 Y34.709 E.0164
G1 X28.065 Y27.579 E.30998
G1 X28.065 Y27.046 E.0164
G1 X20.935 Y34.175 E.30998
G1 X20.935 Y33.641 E.0164
G1 X28.065 Y26.512 E.30998
G1 X28.065 Y25.979 E.0164
G1 X20.935 Y33.108 E.30998
G1 X20.935 Y32.574 E.0164
G1 X28.065 Y25.445 E.30998
G1 X28.065 Y24.911 E.0164
G1 X20.935 Y32.041 E.30998
G1 X20.935 Y31.507 E.0164
G1 X28.065 Y24.378 E.30998
G1 X28.065 Y23.844 E.0164
G1 X20.935 Y30.974 E.30998
G1 X20.935 Y30.44 E.0164
G1 X28.065 Y23.311 E.30998
G1 X28.065 Y22.777 E.0164
G1 X20.935 Y29.906 E.30998
G1 X20.935 Y29.373 E.0164
G1 X45.373 Y4.935 E1.06252
G1 X45.906 Y4.935 E.0164
G1 X28.777 Y22.065 E.74477
G1 X29.311 Y22.065 E.0164
G1 X46.44 Y4.935 E.74477
G1 X46.974 Y4.935 E.0164
G1 X30.144 Y21.765 E.73173
G1 X30.678 Y21.765 E.0164
G1 X47.507 Y4.935 E.73173
G1 X48.041 Y4.935 E.0164
G1 X31.211 Y21.765 E.73172
G1 X31.745 Y21.765 E.0164
G1 X48.574 Y4.935 E.73172
G1 X49.108 Y4.935 E.0164
G1 X32.279 Y21.765 E.73172
G1 X32.812 Y21.765 E.0164
G1 X49.641 Y4.935 E.73172
G1 X50.175 Y4.935 E.0164
G1 X33.346 Y21.765 E.73172
G1 X33.879 Y21.765 E.0164
G1 X50.709 Y4.935 E.73172
G1 X51.242 Y4.935 E.0164
G1 X34.413 Y21.765 E.73172
G1 X34.946 Y21.765 E.0164
G1 X51.776 Y4.935 E.73172
G1 X52.309 Y4.935 E.0164
G1 X35.185 Y22.059 E.74453
G1 X35.713 Y22.065 E.01624
G1 X52.843 Y4.935 E.74477
G1 X53.376 Y4.935 E.0164
G1 X36.247 Y22.065 E.74477
G1 X36.781 Y22.065 E.0164
G1 X53.91 Y4.935 E.74477
G1 X54.444 Y4.935 E.0164
G1 X36.935 Y22.444 E.76124
G1 X36.935 Y22.977 E.0164
G1 X54.977 Y4.935 E.78444
G1 X55.511 Y4.935 E.0164
G1 X36.935 Y23.511 E.80764
G1 X36.935 Y24.044 E.0164
G1 X56.044 Y4.935 E.83084
G1 X56.578 Y4.935 E.0164
G1 X36.935 Y24.578 E.85404
G1 X36.935 Y25.111 E.0164
G1 X57.111 Y4.935 E.87724
G1 X57.645 Y4.935 E.0164
G1 X36.935 Y25.645 E.90044
G1 X36.935 Y26.179 E.0164
G1 X58.179 Y4.935 E.92364
G1 X58.712 Y4.935 E.0164
G1 X36.935 Y26.712 E.94683
G1 X36.935 Y27.246 E.0164
G1 X59.246 Y4.935 E.97003
G1 X59.779 Y4.935 E.0164
G1 X36.935 Y27.779 E.99323
G1 X36.935 Y28.313 E.0164
G1 X60.313 Y4.935 E1.01643
G1 X60.846 Y4.935 E.0164
M73 P73 R8
G1 X35.185 Y30.596 E1.11572
G1 X35.185 Y31.13 E.0164
G1 X61.38 Y4.935 E1.13892
G1 X61.914 Y4.935 E.0164
G1 X35.185 Y31.664 E1.16212
G1 X35.185 Y32.197 E.0164
G1 X62.447 Y4.935 E1.18532
G1 X62.981 Y4.935 E.0164
G1 X35.185 Y32.731 E1.20852
G1 X35.185 Y33.264 E.0164
G1 X63.514 Y4.935 E1.23171
G1 X64.048 Y4.935 E.0164
G1 X35.185 Y33.798 E1.25491
G1 X35.185 Y34.331 E.0164
G1 X64.581 Y4.935 E1.27811
G1 X65.115 Y4.935 E.0164
G1 X35.185 Y34.865 E1.30131
G1 X35.185 Y35.398 E.0164
G1 X65.648 Y4.935 E1.32451
G1 X66.182 Y4.935 E.0164
G1 X35.185 Y35.932 E1.34771
G1 X35.185 Y36.466 E.0164
G1 X66.716 Y4.935 E1.37091
G1 X67.249 Y4.935 E.0164
G1 X35.185 Y36.999 E1.39411
G1 X35.185 Y37.533 E.0164
G1 X67.783 Y4.935 E1.41731
G1 X68.316 Y4.935 E.0164
G1 X35.185 Y38.066 E1.44051
G1 X35.185 Y38.6 E.0164
G1 X68.85 Y4.935 E1.4637
G1 X69.383 Y4.935 E.0164
G1 X35.185 Y39.133 E1.4869
G1 X35.185 Y39.667 E.0164
G1 X69.917 Y4.935 E1.5101
G1 X70.451 Y4.935 E.0164
G1 X35.435 Y39.951 E1.52243
G1 X35.435 Y40.484 E.0164
G1 X70.984 Y4.935 E1.54563
G1 X71.518 Y4.935 E.0164
G1 X35.435 Y41.018 E1.56883
G1 X35.435 Y41.551 E.0164
G1 X72.051 Y4.935 E1.59203
G1 X72.585 Y4.935 E.0164
G1 X35.435 Y42.085 E1.61523
G1 X35.435 Y42.618 E.0164
G1 X73.118 Y4.935 E1.63843
G1 X73.652 Y4.935 E.0164
G1 X35.435 Y43.152 E1.66163
G1 X35.435 Y43.686 E.0164
G1 X74.186 Y4.935 E1.68483
G1 X74.719 Y4.935 E.0164
G1 X35.435 Y44.219 E1.70803
G1 X35.435 Y44.753 E.0164
G1 X75.253 Y4.935 E1.73122
G1 X75.786 Y4.935 E.0164
G1 X35.435 Y45.286 E1.75442
G1 X35.435 Y45.82 E.0164
G1 X76.49 Y4.766 E1.785
; WIPE_START
G1 X75.075 Y6.18 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X80.518 Y11.531 Z2 F30000
G1 X97.943 Y28.666 Z2
G1 Z1.6
G1 E.8 F1800
G1 F15000
G1 X97.585 Y29.023 E.01555
G1 X97.585 Y29.557 E.0164
G1 X98.307 Y28.835 E.03137
G1 X98.84 Y28.835 E.0164
G1 X97.416 Y30.26 E.06194
; WIPE_START
G1 X98.83 Y28.846 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X91.197 Y28.824 Z2 F30000
G1 X35.515 Y28.666 Z2
G1 Z1.6
G1 E.8 F1800
G1 F15000
G1 X35.185 Y28.996 E.01435
G1 X35.185 Y29.529 E.0164
G1 X35.879 Y28.835 E.03017
G1 X36.413 Y28.835 E.0164
G1 X35.016 Y30.232 E.06075
; WIPE_START
G1 X36.413 Y28.835 E-.75083
G1 X36.389 Y28.835 E-.00917
; WIPE_END
G1 E-.04 F1800
G1 X28.757 Y28.92 Z2 F30000
G1 X20.766 Y29.009 Z2
G1 Z1.6
G1 E.8 F1800
G1 F15000
G1 X44.839 Y4.935 E1.0467
G1 X44.306 Y4.935 E.0164
G1 X20.935 Y28.306 E1.01612
G1 X20.935 Y27.772 E.0164
G1 X43.772 Y4.935 E.99293
G1 X43.239 Y4.935 E.0164
G1 X20.935 Y27.239 E.96973
G1 X20.935 Y26.705 E.0164
G1 X42.705 Y4.935 E.94653
G1 X42.171 Y4.935 E.0164
G1 X20.935 Y26.171 E.92333
G1 X20.935 Y25.638 E.0164
G1 X41.638 Y4.935 E.90013
G1 X41.104 Y4.935 E.0164
G1 X20.935 Y25.104 E.87693
G1 X20.935 Y24.571 E.0164
G1 X40.571 Y4.935 E.85373
G1 X40.037 Y4.935 E.0164
G1 X20.935 Y24.037 E.83053
G1 X20.935 Y23.504 E.0164
G1 X39.504 Y4.935 E.80733
G1 X38.97 Y4.935 E.0164
G1 X20.935 Y22.97 E.78413
G1 X20.935 Y22.436 E.0164
G1 X38.436 Y4.935 E.76093
G1 X37.903 Y4.935 E.0164
G1 X20.935 Y21.903 E.73774
G1 X20.935 Y21.369 E.0164
G1 X37.369 Y4.935 E.71454
G1 X36.836 Y4.935 E.0164
G1 X20.935 Y20.836 E.69134
G1 X20.935 Y20.302 E.0164
G1 X36.302 Y4.935 E.66814
G1 X35.769 Y4.935 E.0164
G1 X20.935 Y19.769 E.64494
G1 X20.935 Y19.235 E.0164
G1 X35.235 Y4.935 E.62174
G1 X34.701 Y4.935 E.0164
G1 X20.935 Y18.702 E.59854
G1 X20.935 Y18.168 E.0164
G1 X34.168 Y4.935 E.57534
G1 X33.634 Y4.935 E.0164
G1 X20.935 Y17.634 E.55214
G1 X20.935 Y17.101 E.0164
G1 X33.101 Y4.935 E.52894
G1 X32.567 Y4.935 E.0164
G1 X20.935 Y16.567 E.50574
G1 X20.935 Y16.034 E.0164
G1 X32.034 Y4.935 E.48255
G1 X31.5 Y4.935 E.0164
G1 X20.935 Y15.5 E.45935
G1 X20.935 Y14.967 E.0164
G1 X30.967 Y4.935 E.43615
G1 X30.433 Y4.935 E.0164
G1 X20.935 Y14.433 E.41295
G1 X20.935 Y13.899 E.0164
G1 X29.899 Y4.935 E.38975
G1 X29.366 Y4.935 E.0164
G1 X20.935 Y13.366 E.36655
G1 X20.935 Y12.832 E.0164
G1 X28.832 Y4.935 E.34335
G1 X28.299 Y4.935 E.0164
G1 X20.935 Y12.299 E.32015
G1 X20.935 Y11.765 E.0164
G1 X27.765 Y4.935 E.29695
G1 X27.232 Y4.935 E.0164
G1 X20.935 Y11.232 E.27375
G1 X20.935 Y10.698 E.0164
G1 X26.698 Y4.935 E.25055
G1 X26.164 Y4.935 E.0164
G1 X20.935 Y10.164 E.22736
G1 X20.935 Y9.631 E.0164
G1 X25.631 Y4.935 E.20416
G1 X25.097 Y4.935 E.0164
G1 X20.935 Y9.097 E.18096
G1 X20.935 Y8.564 E.0164
G1 X24.564 Y4.935 E.15776
G1 X24.03 Y4.935 E.0164
G1 X20.935 Y8.03 E.13456
G1 X20.935 Y7.497 E.0164
G1 X23.497 Y4.935 E.11136
G1 X22.963 Y4.935 E.0164
G1 X20.935 Y6.963 E.08816
G1 X20.935 Y6.429 E.0164
G1 X22.429 Y4.935 E.06496
G1 X21.896 Y4.935 E.0164
G1 X20.935 Y5.896 E.04176
G1 X20.935 Y5.362 E.0164
G1 X21.532 Y4.766 E.02594
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.935 Y5.362 E-.32064
G1 X20.935 Y5.896 E-.20275
G1 X21.376 Y5.456 E-.23661
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 9/40
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
G17
G3 Z2 I1.217 J0 P1  F30000
; object ids of layer 9 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer9 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
M73 P74 R8
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z2.2 F30000
G1 X160.4 Y8 Z2.2
G1 Z1.8
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z2.2 F30000
G1 X114.002 Y8.498 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.439 Y13.924 Z2.2 F30000
G1 X93.502 Y73.11 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.502 Y73.502 E.01301
G1 X83.898 Y73.502 E.31859
G1 X83.898 Y67.898 E.1859
G1 X93.502 Y67.898 E.31859
G1 X93.502 Y73.05 E.1709
G1 X93.11 Y73.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.78 Y65.616 Z2.2 F30000
G1 X97.11 Y46.302 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X92.298 Y46.302 E.15962
G1 X92.298 Y40.098 E.2058
G1 X92.548 Y40.098 E.00829
G1 X92.548 Y28.302 E.39129
G1 X90.998 Y28.302 E.05142
G1 X90.998 Y22.398 E.19585
G1 X92.548 Y22.398 E.05142
G1 X92.548 Y22.098 E.00995
G1 X97.252 Y22.098 E.15604
G1 X97.252 Y22.398 E.00995
G1 X98.802 Y22.398 E.05142
G1 X98.802 Y28.302 E.19585
G1 X97.252 Y28.302 E.05142
G1 X97.252 Y40.098 E.39129
G1 X97.502 Y40.098 E.00829
G1 X97.502 Y46.302 E.2058
G1 X97.17 Y46.302 E.01102
G1 X97.11 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.869 E.35708
G1 X92.94 Y28.469 E.01229
G1 F9901.871
G1 X92.94 Y28.069 E.01229
G1 F3789.734
G1 X92.94 Y27.91 E.00489
G1 F2160
G1 X91.39 Y27.91 E.04763
G1 X91.39 Y22.831 E.15606
G1 F2536.674
G1 X91.39 Y22.79 E.00126
G1 F7799.139
G1 X91.79 Y22.79 E.01229
G1 F12000
G1 X92.19 Y22.79 E.01229
G1 X92.94 Y22.79 E.02305
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X97.61 Y22.79 E.02305
G1 X98.01 Y22.79 E.01229
G1 F7799.139
G1 X98.41 Y22.79 E.01229
G1 F2536.674
G1 X98.41 Y22.831 E.00126
G1 F2160
G1 X98.41 Y27.91 E.15606
G1 X96.86 Y27.91 E.04763
G1 F3789.734
G1 X96.86 Y28.069 E.00489
G1 F9901.871
G1 X96.86 Y28.469 E.01229
G1 F12000
G1 X96.86 Y28.869 E.01229
G1 X96.86 Y40.49 E.35708
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.478 Y45.881 Z2.2 F30000
G1 X35.102 Y45.91 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X35.102 Y46.302 E.01301
G1 X29.898 Y46.302 E.17263
G1 X29.898 Y40.098 E.2058
G1 X30.148 Y40.098 E.00829
G1 X30.148 Y28.302 E.39129
G1 X28.598 Y28.302 E.05142
G1 X28.598 Y22.398 E.19585
G1 X30.148 Y22.398 E.05142
G1 X30.148 Y22.098 E.00995
G1 X34.852 Y22.098 E.15604
G1 X34.852 Y22.398 E.00995
G1 X36.402 Y22.398 E.05142
G1 X36.402 Y28.302 E.19585
G1 X34.852 Y28.302 E.05142
G1 X34.852 Y40.098 E.39129
G1 X35.102 Y40.098 E.00829
G1 X35.102 Y45.85 E.19081
G1 X34.71 Y45.91 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.869 E.35708
G1 X30.54 Y28.469 E.01229
G1 F9901.871
G1 X30.54 Y28.069 E.01229
G1 F3789.734
G1 X30.54 Y27.91 E.00489
G1 F2160
G1 X28.99 Y27.91 E.04763
G1 X28.99 Y22.831 E.15606
G1 F2536.674
G1 X28.99 Y22.79 E.00126
G1 F7799.139
G1 X29.39 Y22.79 E.01229
G1 F12000
G1 X29.79 Y22.79 E.01229
G1 X30.54 Y22.79 E.02305
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X35.21 Y22.79 E.02305
G1 X35.61 Y22.79 E.01229
G1 F7799.139
G1 X36.01 Y22.79 E.01229
G1 F2536.674
G1 X36.01 Y22.831 E.00126
G1 F2160
G1 X36.01 Y27.91 E.15606
G1 X34.46 Y27.91 E.04763
G1 F3789.734
G1 X34.46 Y28.069 E.00489
G1 F9901.871
G1 X34.46 Y28.469 E.01229
G1 F12000
G1 X34.46 Y28.869 E.01229
G1 X34.46 Y40.49 E.35708
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.962 Y53.505 Z2.2 F30000
G1 X33.624 Y73.499 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.487 E.00658
G3 X33.577 Y67.903 I.284 J-2.786 E.27802
G3 X34.514 Y68.018 I.142 J2.723 E.03146
G3 X33.7 Y73.502 I-.804 J2.683 E.26518
G1 X33.684 Y73.501 E.00054
G1 X33.643 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.096 E.00549
G3 X33.596 Y68.295 I.245 J-2.396 E.22149
G3 X34.4 Y68.393 I-.013 J3.424 E.02493
G3 X33.936 Y73.098 I-.691 J2.307 E.20393
G1 X33.703 Y73.098 E.00717
; WIPE_START
M204 S10000
G1 X33.464 Y73.096 E-.09071
G1 X33 Y73.007 E-.17946
G1 X32.564 Y72.826 E-.17959
G1 X32.171 Y72.563 E-.17957
G1 X31.928 Y72.32 E-.13067
; WIPE_END
G1 E-.04 F1800
G1 X39.338 Y74.149 Z2.2 F30000
G1 X106.798 Y90.798 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y90.798 E2.85928
G1 X20.602 Y4.602 E2.85928
G1 X106.798 Y4.602 E2.85928
G1 X106.798 Y90.738 E2.85729
G1 X107.19 Y91.19 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
; WIPE_START
M204 S10000
G1 X105.19 Y91.131 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.967 Y90.634 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42021
G1 F15000
G1 X36.735 Y27.403 E2.74924
G1 X36.735 Y27.937 E.0164
G1 X99.263 Y90.465 E2.71866
G1 X98.73 Y90.465 E.0164
G1 X36.735 Y28.47 E2.69546
G1 X36.735 Y28.635 E.00507
G1 X36.367 Y28.635 E.01133
G1 X98.196 Y90.465 E2.68828
G1 X97.663 Y90.465 E.0164
G1 X35.833 Y28.635 E2.68828
G1 X35.3 Y28.635 E.0164
G1 X97.129 Y90.465 E2.68828
G1 X96.595 Y90.465 E.0164
G1 X35.185 Y29.055 E2.67006
G1 X35.185 Y29.588 E.0164
G1 X96.062 Y90.465 E2.64686
G1 X95.528 Y90.465 E.0164
G1 X35.185 Y30.122 E2.62366
G1 X35.185 Y30.655 E.0164
G1 X94.995 Y90.465 E2.60046
G1 X94.461 Y90.465 E.0164
G1 X35.185 Y31.189 E2.57726
G1 X35.185 Y31.722 E.0164
G1 X93.928 Y90.465 E2.55406
G1 X93.394 Y90.465 E.0164
G1 X35.185 Y32.256 E2.53086
G1 X35.185 Y32.79 E.0164
G1 X92.86 Y90.465 E2.50766
G1 X92.327 Y90.465 E.0164
G1 X35.185 Y33.323 E2.48446
G1 X35.185 Y33.857 E.0164
G1 X91.793 Y90.465 E2.46127
G1 X91.26 Y90.465 E.0164
G1 X35.185 Y34.39 E2.43807
G1 X35.185 Y34.924 E.0164
G1 X90.726 Y90.465 E2.41487
G1 X90.193 Y90.465 E.0164
G1 X35.185 Y35.457 E2.39167
G1 X35.185 Y35.991 E.0164
G1 X89.659 Y90.465 E2.36847
G1 X89.126 Y90.465 E.0164
G1 X35.185 Y36.525 E2.34527
G1 X35.185 Y37.058 E.0164
G1 X88.592 Y90.465 E2.32207
G1 X88.058 Y90.465 E.0164
G1 X35.185 Y37.592 E2.29887
G1 X35.185 Y38.125 E.0164
G1 X87.525 Y90.465 E2.27567
G1 X86.991 Y90.465 E.0164
G1 X35.185 Y38.659 E2.25247
G1 X35.185 Y39.192 E.0164
G1 X86.458 Y90.465 E2.22927
G1 X85.924 Y90.465 E.0164
G1 X35.016 Y39.556 E2.21345
; WIPE_START
G1 X36.43 Y40.97 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.333 Y45.562 Z2.2 F30000
G1 X29.734 Y46.013 Z2.2
G1 Z1.8
G1 E.8 F1800
G1 F15000
G1 X20.935 Y37.214 E.38257
G1 X20.935 Y36.681 E.0164
G1 X29.565 Y45.31 E.3752
G1 X29.565 Y44.777 E.0164
G1 X20.935 Y36.147 E.3752
G1 X20.935 Y35.614 E.0164
G1 X29.565 Y44.243 E.3752
G1 X29.565 Y43.709 E.0164
G1 X20.935 Y35.08 E.3752
G1 X20.935 Y34.547 E.0164
G1 X29.565 Y43.176 E.3752
G1 X29.565 Y42.642 E.0164
G1 X20.935 Y34.013 E.3752
G1 X20.935 Y33.479 E.0164
G1 X29.565 Y42.109 E.3752
G1 X29.565 Y41.575 E.0164
G1 X20.935 Y32.946 E.3752
G1 X20.935 Y32.412 E.0164
G1 X29.565 Y41.042 E.3752
G1 X29.565 Y40.508 E.0164
G1 X20.935 Y31.879 E.3752
G1 X20.935 Y31.345 E.0164
G1 X29.565 Y39.975 E.3752
G1 X29.565 Y39.765 E.00645
G1 X29.815 Y39.765 E.00769
G1 X29.815 Y39.691 E.00227
G1 X20.935 Y30.812 E.38607
G1 X20.935 Y30.278 E.0164
G1 X29.815 Y39.157 E.38607
G1 X29.815 Y38.624 E.0164
G1 X20.935 Y29.744 E.38607
G1 X20.935 Y29.211 E.0164
G1 X29.815 Y38.09 E.38607
G1 X29.815 Y37.557 E.0164
G1 X20.935 Y28.677 E.38607
G1 X20.935 Y28.144 E.0164
G1 X29.815 Y37.023 E.38607
G1 X29.815 Y36.49 E.0164
G1 X20.935 Y27.61 E.38607
G1 X20.935 Y27.077 E.0164
G1 X29.815 Y35.956 E.38607
G1 X29.815 Y35.422 E.0164
G1 X20.935 Y26.543 E.38607
G1 X20.935 Y26.009 E.0164
G1 X29.815 Y34.889 E.38607
G1 X29.815 Y34.355 E.0164
G1 X20.935 Y25.476 E.38607
G1 X20.935 Y24.942 E.0164
G1 X29.815 Y33.822 E.38607
G1 X29.815 Y33.288 E.0164
G1 X20.935 Y24.409 E.38607
G1 X20.935 Y23.875 E.0164
G1 X29.815 Y32.755 E.38607
G1 X29.815 Y32.221 E.0164
G1 X20.935 Y23.342 E.38607
G1 X20.935 Y22.808 E.0164
G1 X29.815 Y31.687 E.38607
G1 X29.815 Y31.154 E.0164
G1 X20.935 Y22.275 E.38607
G1 X20.935 Y21.741 E.0164
G1 X29.984 Y30.79 E.39344
G1 X29.984 Y29.189 F30000
G1 F15000
G1 X29.43 Y28.635 E.02408
G1 X28.897 Y28.635 E.0164
G1 X29.815 Y29.553 E.03991
G1 X29.815 Y30.087 E.0164
G1 X20.935 Y21.207 E.38607
G1 X20.935 Y20.674 E.0164
G1 X28.265 Y28.003 E.31867
M73 P75 R8
G1 X28.265 Y27.47 E.0164
G1 X20.935 Y20.14 E.31867
G1 X20.935 Y19.607 E.0164
G1 X28.265 Y26.936 E.31867
G1 X28.265 Y26.402 E.0164
G1 X20.935 Y19.073 E.31867
G1 X20.935 Y18.54 E.0164
G1 X28.265 Y25.869 E.31867
G1 X28.265 Y25.335 E.0164
G1 X20.935 Y18.006 E.31867
G1 X20.935 Y17.472 E.0164
G1 X28.265 Y24.802 E.31867
G1 X28.265 Y24.268 E.0164
G1 X20.935 Y16.939 E.31867
G1 X20.935 Y16.405 E.0164
G1 X28.265 Y23.735 E.31867
G1 X28.265 Y23.201 E.0164
G1 X20.935 Y15.872 E.31867
G1 X20.935 Y15.338 E.0164
G1 X28.265 Y22.667 E.31867
G1 X28.265 Y22.134 E.0164
G1 X20.935 Y14.805 E.31867
G1 X20.935 Y14.271 E.0164
G1 X28.729 Y22.065 E.33886
G1 X29.263 Y22.065 E.0164
G1 X20.935 Y13.737 E.36206
G1 X20.935 Y13.204 E.0164
G1 X29.796 Y22.065 E.38526
G1 X29.815 Y22.065 E.00057
G1 X29.815 Y21.765 E.00922
G1 X30.03 Y21.765 E.00661
G1 X20.935 Y12.67 E.39542
G1 X20.935 Y12.137 E.0164
G1 X30.563 Y21.765 E.41862
G1 X31.097 Y21.765 E.0164
G1 X20.935 Y11.603 E.44181
G1 X20.935 Y11.07 E.0164
G1 X31.63 Y21.765 E.46501
G1 X32.164 Y21.765 E.0164
G1 X20.935 Y10.536 E.48821
G1 X20.935 Y10.002 E.0164
G1 X32.698 Y21.765 E.51141
G1 X33.231 Y21.765 E.0164
G1 X20.935 Y9.469 E.53461
G1 X20.935 Y8.935 E.0164
G1 X33.765 Y21.765 E.55781
G1 X34.298 Y21.765 E.0164
G1 X20.935 Y8.402 E.58101
G1 X20.935 Y7.868 E.0164
G1 X34.832 Y21.765 E.60421
G1 X35.185 Y21.765 E.01087
G1 X35.185 Y22.065 E.00922
G1 X35.665 Y22.065 E.01476
G1 X20.935 Y7.335 E.64045
G1 X20.935 Y6.801 E.0164
G1 X36.369 Y22.234 E.67103
G1 X36.566 Y22.431 F30000
G1 F15000
G1 X83.565 Y69.43 E2.04348
G1 X83.565 Y69.964 E.0164
G1 X36.735 Y23.135 E2.0361
G1 X36.735 Y23.668 E.0164
G1 X83.565 Y70.498 E2.0361
G1 X83.565 Y71.031 E.0164
G1 X36.735 Y24.202 E2.0361
G1 X36.735 Y24.735 E.0164
G1 X83.565 Y71.565 E2.0361
G1 X83.565 Y72.098 E.0164
G1 X36.735 Y25.269 E2.0361
G1 X36.735 Y25.802 E.0164
G1 X83.565 Y72.632 E2.0361
G1 X83.565 Y73.165 E.0164
G1 X36.735 Y26.336 E2.0361
G1 X36.735 Y26.87 E.0164
G1 X100.33 Y90.465 E2.76506
G1 X100.864 Y90.465 E.0164
G1 X84.235 Y73.835 E.72303
G1 X84.768 Y73.835 E.0164
G1 X101.398 Y90.465 E.72303
G1 X101.931 Y90.465 E.0164
G1 X85.302 Y73.835 E.72303
G1 X85.835 Y73.835 E.0164
G1 X102.465 Y90.465 E.72303
G1 X102.998 Y90.465 E.0164
G1 X86.369 Y73.835 E.72303
G1 X86.903 Y73.835 E.0164
G1 X103.532 Y90.465 E.72303
G1 X104.065 Y90.465 E.0164
G1 X87.436 Y73.835 E.72303
G1 X87.97 Y73.835 E.0164
G1 X104.599 Y90.465 E.72303
G1 X105.133 Y90.465 E.0164
G1 X88.503 Y73.835 E.72303
G1 X89.037 Y73.835 E.0164
G1 X105.666 Y90.465 E.72303
G1 X106.2 Y90.465 E.0164
G1 X89.57 Y73.835 E.72303
G1 X90.104 Y73.835 E.0164
G1 X106.465 Y90.196 E.71135
G1 X106.465 Y89.663 E.0164
G1 X90.637 Y73.835 E.68815
G1 X91.171 Y73.835 E.0164
G1 X106.465 Y89.129 E.66495
G1 X106.465 Y88.595 E.0164
G1 X91.705 Y73.835 E.64175
G1 X92.238 Y73.835 E.0164
G1 X106.465 Y88.062 E.61856
G1 X106.465 Y87.528 E.0164
G1 X92.772 Y73.835 E.59536
G1 X93.305 Y73.835 E.0164
G1 X106.465 Y86.995 E.57216
G1 X106.465 Y86.461 E.0164
G1 X93.835 Y73.832 E.54911
G1 X93.835 Y73.298 E.0164
G1 X106.465 Y85.928 E.54911
G1 X106.465 Y85.394 E.0164
G1 X93.835 Y72.765 E.54911
G1 X93.835 Y72.231 E.0164
G1 X106.465 Y84.86 E.54911
G1 X106.465 Y84.327 E.0164
G1 X93.835 Y71.697 E.54911
G1 X93.835 Y71.164 E.0164
G1 X106.465 Y83.793 E.54911
G1 X106.465 Y83.26 E.0164
G1 X93.835 Y70.63 E.54911
G1 X93.835 Y70.097 E.0164
G1 X106.465 Y82.726 E.54911
G1 X106.465 Y82.193 E.0164
G1 X93.835 Y69.563 E.54911
G1 X93.835 Y69.03 E.0164
G1 X106.465 Y81.659 E.54911
G1 X106.465 Y81.125 E.0164
G1 X93.835 Y68.496 E.54911
G1 X93.835 Y67.963 E.0164
G1 X106.465 Y80.592 E.54911
G1 X106.465 Y80.058 E.0164
G1 X31.342 Y4.935 E3.26628
G1 X31.875 Y4.935 E.0164
G1 X106.465 Y79.525 E3.24308
G1 X106.465 Y78.991 E.0164
G1 X32.409 Y4.935 E3.21988
G1 X32.942 Y4.935 E.0164
G1 X106.465 Y78.458 E3.19668
G1 X106.465 Y77.924 E.0164
G1 X33.476 Y4.935 E3.17348
G1 X34.01 Y4.935 E.0164
G1 X106.465 Y77.39 E3.15028
G1 X106.465 Y76.857 E.0164
G1 X34.543 Y4.935 E3.12708
G1 X35.077 Y4.935 E.0164
G1 X106.465 Y76.323 E3.10388
G1 X106.465 Y75.79 E.0164
G1 X35.61 Y4.935 E3.08069
G1 X36.144 Y4.935 E.0164
G1 X106.465 Y75.256 E3.05749
G1 X106.465 Y74.723 E.0164
G1 X36.677 Y4.935 E3.03429
G1 X37.211 Y4.935 E.0164
G1 X106.465 Y74.189 E3.01109
G1 X106.465 Y73.655 E.0164
G1 X37.745 Y4.935 E2.98789
G1 X38.278 Y4.935 E.0164
G1 X106.465 Y73.122 E2.96469
G1 X106.465 Y72.588 E.0164
G1 X38.812 Y4.935 E2.94149
G1 X39.345 Y4.935 E.0164
G1 X106.465 Y72.055 E2.91829
G1 X106.465 Y71.521 E.0164
G1 X39.879 Y4.935 E2.89509
G1 X40.412 Y4.935 E.0164
G1 X106.465 Y70.988 E2.87189
G1 X106.465 Y70.454 E.0164
G1 X40.946 Y4.935 E2.84869
G1 X41.48 Y4.935 E.0164
G1 X106.465 Y69.92 E2.8255
G1 X106.465 Y69.387 E.0164
G1 X42.013 Y4.935 E2.8023
G1 X42.547 Y4.935 E.0164
G1 X106.465 Y68.853 E2.7791
G1 X106.465 Y68.32 E.0164
G1 X43.08 Y4.935 E2.7559
G1 X43.614 Y4.935 E.0164
G1 X106.465 Y67.786 E2.7327
G1 X106.465 Y67.253 E.0164
G1 X44.147 Y4.935 E2.7095
G1 X44.681 Y4.935 E.0164
G1 X106.465 Y66.719 E2.6863
G1 X106.465 Y66.186 E.0164
G1 X45.215 Y4.935 E2.6631
G1 X45.748 Y4.935 E.0164
G1 X106.465 Y65.652 E2.6399
G1 X106.465 Y65.118 E.0164
G1 X46.282 Y4.935 E2.6167
G1 X46.815 Y4.935 E.0164
G1 X106.465 Y64.585 E2.5935
G1 X106.465 Y64.051 E.0164
G1 X47.349 Y4.935 E2.57031
G1 X47.882 Y4.935 E.0164
G1 X106.465 Y63.518 E2.54711
G1 X106.465 Y62.984 E.0164
G1 X48.416 Y4.935 E2.52391
G1 X48.949 Y4.935 E.0164
G1 X106.465 Y62.451 E2.50071
G1 X106.465 Y61.917 E.0164
G1 X49.483 Y4.935 E2.47751
G1 X50.017 Y4.935 E.0164
G1 X106.634 Y61.553 E2.46169
G1 X93.607 Y67.734 F30000
G1 F15000
G1 X30.808 Y4.935 E2.73045
G1 X30.275 Y4.935 E.0164
G1 X92.904 Y67.565 E2.72307
G1 X92.37 Y67.565 E.0164
G1 X29.741 Y4.935 E2.72307
G1 X29.207 Y4.935 E.0164
G1 X91.837 Y67.565 E2.72307
G1 X91.303 Y67.565 E.0164
G1 X28.674 Y4.935 E2.72307
G1 X28.14 Y4.935 E.0164
G1 X90.77 Y67.565 E2.72307
G1 X90.236 Y67.565 E.0164
G1 X27.607 Y4.935 E2.72307
G1 X27.073 Y4.935 E.0164
G1 X89.703 Y67.565 E2.72307
G1 X89.169 Y67.565 E.0164
G1 X26.54 Y4.935 E2.72307
G1 X26.006 Y4.935 E.0164
G1 X88.635 Y67.565 E2.72307
G1 X88.102 Y67.565 E.0164
G1 X25.472 Y4.935 E2.72307
G1 X24.939 Y4.935 E.0164
G1 X87.568 Y67.565 E2.72307
G1 X87.035 Y67.565 E.0164
G1 X24.405 Y4.935 E2.72307
G1 X23.872 Y4.935 E.0164
G1 X86.501 Y67.565 E2.72307
G1 X85.968 Y67.565 E.0164
G1 X23.338 Y4.935 E2.72307
G1 X22.805 Y4.935 E.0164
G1 X85.434 Y67.565 E2.72307
G1 X84.9 Y67.565 E.0164
G1 X22.271 Y4.935 E2.72307
G1 X21.737 Y4.935 E.0164
G1 X84.367 Y67.565 E2.72307
G1 X83.833 Y67.565 E.0164
G1 X21.204 Y4.935 E2.72307
G1 X20.935 Y4.935 E.00826
G1 X20.935 Y5.2 E.00815
G1 X83.565 Y67.83 E2.72307
G1 X83.565 Y68.363 E.0164
G1 X20.935 Y5.734 E2.72307
G1 X20.935 Y6.267 E.0164
G1 X83.734 Y69.066 E2.73044
; WIPE_START
G1 X82.32 Y67.652 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X83.386 Y75.21 Z2.2 F30000
M73 P76 R8
G1 X85.56 Y90.634 Z2.2
G1 Z1.8
G1 E.8 F1800
G1 F15000
G1 X35.435 Y40.509 E2.17938
G1 X35.435 Y41.043 E.0164
G1 X84.857 Y90.465 E2.14881
G1 X84.323 Y90.465 E.0164
G1 X35.435 Y41.577 E2.12561
G1 X35.435 Y42.11 E.0164
G1 X83.79 Y90.465 E2.10241
G1 X83.256 Y90.465 E.0164
G1 X35.435 Y42.644 E2.07921
G1 X35.435 Y43.177 E.0164
G1 X82.723 Y90.465 E2.05601
G1 X82.189 Y90.465 E.0164
G1 X35.435 Y43.711 E2.03281
G1 X35.435 Y44.244 E.0164
M73 P76 R7
G1 X81.656 Y90.465 E2.00961
G1 X81.122 Y90.465 E.0164
G1 X35.435 Y44.778 E1.98641
G1 X35.435 Y45.312 E.0164
G1 X80.588 Y90.465 E1.96321
G1 X80.055 Y90.465 E.0164
G1 X35.435 Y45.845 E1.94002
G1 X35.435 Y46.379 E.0164
G1 X79.521 Y90.465 E1.91682
G1 X78.988 Y90.465 E.0164
G1 X35.158 Y46.635 E1.90566
G1 X34.625 Y46.635 E.0164
G1 X78.454 Y90.465 E1.90566
G1 X77.921 Y90.465 E.0164
G1 X34.091 Y46.635 E1.90566
G1 X33.558 Y46.635 E.0164
G1 X77.387 Y90.465 E1.90566
G1 X76.853 Y90.465 E.0164
G1 X33.024 Y46.635 E1.90566
G1 X32.49 Y46.635 E.0164
G1 X76.32 Y90.465 E1.90566
G1 X75.786 Y90.465 E.0164
G1 X31.957 Y46.635 E1.90566
G1 X31.423 Y46.635 E.0164
G1 X75.253 Y90.465 E1.90566
G1 X74.719 Y90.465 E.0164
G1 X30.89 Y46.635 E1.90566
G1 X30.356 Y46.635 E.0164
G1 X74.186 Y90.465 E1.90566
G1 X73.652 Y90.465 E.0164
G1 X20.935 Y37.748 E2.29207
G1 X20.935 Y38.282 E.0164
G1 X73.118 Y90.465 E2.26887
G1 X72.585 Y90.465 E.0164
G1 X20.935 Y38.815 E2.24568
G1 X20.935 Y39.349 E.0164
G1 X72.051 Y90.465 E2.22248
G1 X71.518 Y90.465 E.0164
G1 X20.935 Y39.882 E2.19928
G1 X20.935 Y40.416 E.0164
G1 X70.984 Y90.465 E2.17608
G1 X70.451 Y90.465 E.0164
G1 X20.935 Y40.949 E2.15288
G1 X20.935 Y41.483 E.0164
G1 X69.917 Y90.465 E2.12968
G1 X69.383 Y90.465 E.0164
G1 X20.935 Y42.017 E2.10648
G1 X20.935 Y42.55 E.0164
G1 X68.85 Y90.465 E2.08328
G1 X68.316 Y90.465 E.0164
G1 X20.935 Y43.084 E2.06008
G1 X20.935 Y43.617 E.0164
G1 X67.783 Y90.465 E2.03688
G1 X67.249 Y90.465 E.0164
G1 X20.935 Y44.151 E2.01368
G1 X20.935 Y44.684 E.0164
G1 X66.716 Y90.465 E1.99049
G1 X66.182 Y90.465 E.0164
G1 X20.935 Y45.218 E1.96729
G1 X20.935 Y45.752 E.0164
G1 X65.648 Y90.465 E1.94409
G1 X65.115 Y90.465 E.0164
G1 X20.935 Y46.285 E1.92089
G1 X20.935 Y46.819 E.0164
G1 X64.581 Y90.465 E1.89769
G1 X64.048 Y90.465 E.0164
G1 X20.935 Y47.352 E1.87449
G1 X20.935 Y47.886 E.0164
G1 X63.514 Y90.465 E1.85129
G1 X62.981 Y90.465 E.0164
G1 X20.935 Y48.419 E1.82809
G1 X20.935 Y48.953 E.0164
G1 X62.447 Y90.465 E1.80489
G1 X61.914 Y90.465 E.0164
G1 X20.935 Y49.487 E1.78169
G1 X20.935 Y50.02 E.0164
G1 X61.38 Y90.465 E1.75849
G1 X60.846 Y90.465 E.0164
G1 X20.935 Y50.554 E1.7353
G1 X20.935 Y51.087 E.0164
G1 X60.313 Y90.465 E1.7121
G1 X59.779 Y90.465 E.0164
G1 X20.935 Y51.621 E1.6889
G1 X20.935 Y52.154 E.0164
G1 X59.246 Y90.465 E1.6657
G1 X58.712 Y90.465 E.0164
G1 X20.935 Y52.688 E1.6425
G1 X20.935 Y53.221 E.0164
G1 X58.179 Y90.465 E1.6193
G1 X57.645 Y90.465 E.0164
G1 X36.524 Y69.344 E.91833
G3 X36.783 Y70.137 I-2.358 J1.211 E.02576
G1 X57.111 Y90.465 E.88384
G1 X56.578 Y90.465 E.0164
M73 P77 R7
G1 X36.835 Y70.722 E.85838
G3 X36.791 Y71.211 I-2.505 J.02 E.01513
G1 X56.044 Y90.465 E.83711
G1 X55.511 Y90.465 E.0164
G1 X36.69 Y71.644 E.81832
G3 X36.538 Y72.026 I-2.022 J-.579 E.01266
G1 X54.977 Y90.465 E.8017
G1 X54.444 Y90.465 E.0164
G1 X36.35 Y72.372 E.78667
G3 X36.129 Y72.684 I-1.694 J-.967 E.01179
G1 X53.91 Y90.465 E.7731
G1 X53.376 Y90.465 E.0164
G1 X35.871 Y72.96 E.7611
G3 X35.582 Y73.204 I-1.382 J-1.342 E.01166
G1 X52.843 Y90.465 E.75047
G1 X52.309 Y90.465 E.0164
G1 X35.261 Y73.417 E.74124
G1 X35.202 Y73.452 E.00213
G3 X34.906 Y73.595 I-.87 J-1.423 E.01012
G1 X51.776 Y90.465 E.73348
G1 X51.242 Y90.465 E.0164
G1 X34.505 Y73.728 E.72771
G3 X34.058 Y73.814 I-.662 J-2.234 E.01403
G1 X50.709 Y90.465 E.72396
G1 X50.175 Y90.465 E.0164
G1 X33.539 Y73.829 E.72332
G3 X32.908 Y73.731 I.164 J-3.152 E.01967
G1 X49.641 Y90.465 E.72756
G1 X49.108 Y90.465 E.0164
G1 X20.935 Y62.292 E1.22492
G1 X20.935 Y61.759 E.0164
G1 X30.669 Y71.492 E.42321
G3 X30.571 Y70.861 I3.055 J-.795 E.01967
G1 X20.935 Y61.225 E.41897
G1 X20.935 Y60.691 E.0164
G1 X30.586 Y70.342 E.41961
G3 X30.672 Y69.895 I2.325 J.215 E.01403
G1 X20.935 Y60.158 E.42335
G1 X20.935 Y59.624 E.0164
G1 X30.805 Y69.494 E.42913
G3 X30.983 Y69.139 I1.979 J.772 E.01224
G1 X20.935 Y59.091 E.43688
G1 X20.935 Y58.557 E.0164
G1 X31.196 Y68.818 E.44612
G3 X31.44 Y68.529 I1.589 J1.095 E.01166
G1 X20.935 Y58.024 E.45674
G1 X20.935 Y57.49 E.0164
G1 X31.716 Y68.271 E.46875
G3 X32.028 Y68.05 I1.279 J1.472 E.01179
G1 X20.935 Y56.956 E.48232
G1 X20.935 Y56.423 E.0164
G1 X32.374 Y67.862 E.49735
G3 X32.756 Y67.71 I.962 J1.871 E.01266
G1 X20.935 Y55.889 E.51397
G1 X20.935 Y55.356 E.0164
G1 X33.191 Y67.611 E.53287
G3 X33.685 Y67.572 I.397 J1.852 E.01528
G1 X20.935 Y54.822 E.55435
G1 X20.935 Y54.289 E.0164
G1 X34.263 Y67.617 E.57949
G3 X35.056 Y67.876 I-.418 J2.617 E.02576
G1 X20.766 Y53.585 E.62135
G1 X21.532 Y90.634 F30000
G1 F15000
G1 X20.935 Y90.038 E.02594
G1 X20.935 Y89.504 E.0164
G1 X21.896 Y90.465 E.04176
G1 X22.429 Y90.465 E.0164
G1 X20.935 Y88.971 E.06496
G1 X20.935 Y88.437 E.0164
G1 X22.963 Y90.465 E.08816
G1 X23.497 Y90.465 E.0164
G1 X20.935 Y87.903 E.11136
G1 X20.935 Y87.37 E.0164
G1 X24.03 Y90.465 E.13456
G1 X24.564 Y90.465 E.0164
G1 X20.935 Y86.836 E.15776
G1 X20.935 Y86.303 E.0164
G1 X25.097 Y90.465 E.18096
G1 X25.631 Y90.465 E.0164
G1 X20.935 Y85.769 E.20416
G1 X20.935 Y85.236 E.0164
G1 X26.164 Y90.465 E.22736
G1 X26.698 Y90.465 E.0164
G1 X20.935 Y84.702 E.25055
G1 X20.935 Y84.168 E.0164
G1 X27.232 Y90.465 E.27375
G1 X27.765 Y90.465 E.0164
G1 X20.935 Y83.635 E.29695
G1 X20.935 Y83.101 E.0164
G1 X28.299 Y90.465 E.32015
G1 X28.832 Y90.465 E.0164
G1 X20.935 Y82.568 E.34335
G1 X20.935 Y82.034 E.0164
G1 X29.366 Y90.465 E.36655
G1 X29.899 Y90.465 E.0164
G1 X20.935 Y81.501 E.38975
G1 X20.935 Y80.967 E.0164
G1 X30.433 Y90.465 E.41295
G1 X30.967 Y90.465 E.0164
G1 X20.935 Y80.433 E.43615
G1 X20.935 Y79.9 E.0164
G1 X31.5 Y90.465 E.45935
G1 X32.034 Y90.465 E.0164
G1 X20.935 Y79.366 E.48255
G1 X20.935 Y78.833 E.0164
G1 X32.567 Y90.465 E.50574
G1 X33.101 Y90.465 E.0164
G1 X20.935 Y78.299 E.52894
G1 X20.935 Y77.766 E.0164
G1 X33.634 Y90.465 E.55214
G1 X34.168 Y90.465 E.0164
G1 X20.935 Y77.232 E.57534
G1 X20.935 Y76.699 E.0164
G1 X34.701 Y90.465 E.59854
G1 X35.235 Y90.465 E.0164
G1 X20.935 Y76.165 E.62174
G1 X20.935 Y75.631 E.0164
G1 X35.769 Y90.465 E.64494
G1 X36.302 Y90.465 E.0164
G1 X20.935 Y75.098 E.66814
G1 X20.935 Y74.564 E.0164
G1 X36.836 Y90.465 E.69134
G1 X37.369 Y90.465 E.0164
G1 X20.935 Y74.031 E.71454
G1 X20.935 Y73.497 E.0164
G1 X37.903 Y90.465 E.73774
G1 X38.436 Y90.465 E.0164
G1 X20.935 Y72.964 E.76093
G1 X20.935 Y72.43 E.0164
G1 X38.97 Y90.465 E.78413
G1 X39.504 Y90.465 E.0164
G1 X20.935 Y71.896 E.80733
G1 X20.935 Y71.363 E.0164
G1 X40.037 Y90.465 E.83053
G1 X40.571 Y90.465 E.0164
G1 X20.935 Y70.829 E.85373
G1 X20.935 Y70.296 E.0164
G1 X41.104 Y90.465 E.87693
G1 X41.638 Y90.465 E.0164
G1 X20.935 Y69.762 E.90013
G1 X20.935 Y69.229 E.0164
G1 X42.171 Y90.465 E.92333
G1 X42.705 Y90.465 E.0164
G1 X20.935 Y68.695 E.94653
G1 X20.935 Y68.161 E.0164
G1 X43.239 Y90.465 E.96973
G1 X43.772 Y90.465 E.0164
G1 X20.935 Y67.628 E.99293
G1 X20.935 Y67.094 E.0164
G1 X44.306 Y90.465 E1.01612
G1 X44.839 Y90.465 E.0164
G1 X20.935 Y66.561 E1.03932
G1 X20.935 Y66.027 E.0164
G1 X45.373 Y90.465 E1.06252
G1 X45.906 Y90.465 E.0164
G1 X20.935 Y65.494 E1.08572
G1 X20.935 Y64.96 E.0164
G1 X46.44 Y90.465 E1.10892
G1 X46.974 Y90.465 E.0164
G1 X20.935 Y64.426 E1.13212
G1 X20.935 Y63.893 E.0164
G1 X47.507 Y90.465 E1.15532
G1 X48.041 Y90.465 E.0164
G1 X20.935 Y63.359 E1.17852
G1 X20.935 Y62.826 E.0164
G1 X48.744 Y90.634 E1.20909
G1 X67.455 Y4.766 F30000
G1 F15000
G1 X90.665 Y27.976 E1.00915
G1 X90.665 Y27.442 E.0164
G1 X68.158 Y4.935 E.97857
G1 X68.692 Y4.935 E.0164
G1 X90.665 Y26.908 E.95537
G1 X90.665 Y26.375 E.0164
G1 X69.225 Y4.935 E.93217
G1 X69.759 Y4.935 E.0164
G1 X90.665 Y25.841 E.90897
G1 X90.665 Y25.308 E.0164
G1 X70.292 Y4.935 E.88578
G1 X70.826 Y4.935 E.0164
G1 X90.665 Y24.774 E.86258
G1 X90.665 Y24.241 E.0164
G1 X71.359 Y4.935 E.83938
G1 X71.893 Y4.935 E.0164
G1 X90.665 Y23.707 E.81618
G1 X90.665 Y23.174 E.0164
G1 X72.427 Y4.935 E.79298
G1 X72.96 Y4.935 E.0164
G1 X90.665 Y22.64 E.76978
G1 X90.665 Y22.106 E.0164
G1 X73.494 Y4.935 E.74658
G1 X74.027 Y4.935 E.0164
G1 X91.157 Y22.065 E.74477
G1 X91.69 Y22.065 E.0164
G1 X74.561 Y4.935 E.74477
G1 X75.094 Y4.935 E.0164
G1 X92.215 Y22.056 E.74438
G1 X92.215 Y21.765 E.00895
G1 X92.457 Y21.765 E.00746
G1 X75.628 Y4.935 E.73172
G1 X76.161 Y4.935 E.0164
G1 X92.991 Y21.765 E.73172
G1 X93.524 Y21.765 E.0164
G1 X76.695 Y4.935 E.73172
G1 X77.229 Y4.935 E.0164
G1 X94.058 Y21.765 E.73172
G1 X94.592 Y21.765 E.0164
G1 X77.762 Y4.935 E.73172
G1 X78.296 Y4.935 E.0164
G1 X95.125 Y21.765 E.73172
G1 X95.659 Y21.765 E.0164
G1 X78.829 Y4.935 E.73172
G1 X79.363 Y4.935 E.0164
G1 X96.192 Y21.765 E.73172
G1 X96.726 Y21.765 E.0164
G1 X79.896 Y4.935 E.73172
G1 X80.43 Y4.935 E.0164
G1 X97.259 Y21.765 E.73172
G1 X97.585 Y21.765 E.01002
G1 X97.585 Y22.065 E.00922
G1 X98.093 Y22.065 E.01561
G1 X80.964 Y4.935 E.74477
G1 X81.497 Y4.935 E.0164
M73 P78 R7
G1 X98.796 Y22.234 E.75215
; WIPE_START
G1 X97.382 Y20.82 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.459 Y27.367 Z2.2 F30000
G1 X92.384 Y29.162 Z2.2
G1 Z1.8
G1 E.8 F1800
G1 F15000
G1 X91.858 Y28.635 E.02289
G1 X91.324 Y28.635 E.0164
G1 X92.215 Y29.526 E.03871
G1 X92.215 Y30.059 E.0164
G1 X67.091 Y4.935 E1.09236
G1 X66.557 Y4.935 E.0164
G1 X92.215 Y30.593 E1.11556
G1 X92.215 Y31.126 E.0164
G1 X66.024 Y4.935 E1.13876
G1 X65.49 Y4.935 E.0164
G1 X92.215 Y31.66 E1.16196
G1 X92.215 Y32.193 E.0164
G1 X64.957 Y4.935 E1.18516
G1 X64.423 Y4.935 E.0164
G1 X92.215 Y32.727 E1.20836
G1 X92.215 Y33.261 E.0164
G1 X63.889 Y4.935 E1.23156
G1 X63.356 Y4.935 E.0164
G1 X92.215 Y33.794 E1.25476
G1 X92.215 Y34.328 E.0164
G1 X62.822 Y4.935 E1.27796
G1 X62.289 Y4.935 E.0164
G1 X92.215 Y34.861 E1.30115
G1 X92.215 Y35.395 E.0164
G1 X61.755 Y4.935 E1.32435
G1 X61.222 Y4.935 E.0164
G1 X92.215 Y35.928 E1.34755
G1 X92.215 Y36.462 E.0164
G1 X60.688 Y4.935 E1.37075
G1 X60.154 Y4.935 E.0164
G1 X92.215 Y36.996 E1.39395
G1 X92.215 Y37.529 E.0164
G1 X59.621 Y4.935 E1.41715
G1 X59.087 Y4.935 E.0164
G1 X92.215 Y38.063 E1.44035
G1 X92.215 Y38.596 E.0164
G1 X58.554 Y4.935 E1.46355
G1 X58.02 Y4.935 E.0164
G1 X92.215 Y39.13 E1.48675
G1 X92.215 Y39.663 E.0164
G1 X57.487 Y4.935 E1.50995
G1 X56.953 Y4.935 E.0164
G1 X91.965 Y39.947 E1.52228
G1 X91.965 Y40.481 E.0164
G1 X56.419 Y4.935 E1.54547
G1 X55.886 Y4.935 E.0164
G1 X91.965 Y41.014 E1.56867
G1 X91.965 Y41.548 E.0164
G1 X55.352 Y4.935 E1.59187
G1 X54.819 Y4.935 E.0164
G1 X91.965 Y42.081 E1.61507
G1 X91.965 Y42.615 E.0164
G1 X54.285 Y4.935 E1.63827
G1 X53.752 Y4.935 E.0164
G1 X91.965 Y43.148 E1.66147
G1 X91.965 Y43.682 E.0164
G1 X53.218 Y4.935 E1.68467
G1 X52.684 Y4.935 E.0164
G1 X91.965 Y44.216 E1.70787
G1 X91.965 Y44.749 E.0164
G1 X52.151 Y4.935 E1.73107
G1 X51.617 Y4.935 E.0164
G1 X91.965 Y45.283 E1.75427
G1 X91.965 Y45.816 E.0164
G1 X51.084 Y4.935 E1.77747
G1 X50.55 Y4.935 E.0164
G1 X106.465 Y60.85 E2.43111
G1 X106.465 Y60.316 E.0164
G1 X92.784 Y46.635 E.59483
G1 X93.317 Y46.635 E.0164
G1 X106.465 Y59.783 E.57164
G1 X106.465 Y59.249 E.0164
G1 X93.851 Y46.635 E.54844
G1 X94.384 Y46.635 E.0164
G1 X106.465 Y58.716 E.52524
G1 X106.465 Y58.182 E.0164
G1 X94.918 Y46.635 E.50204
G1 X95.452 Y46.635 E.0164
G1 X106.465 Y57.648 E.47884
G1 X106.465 Y57.115 E.0164
G1 X95.985 Y46.635 E.45564
G1 X96.519 Y46.635 E.0164
G1 X106.465 Y56.581 E.43244
G1 X106.465 Y56.048 E.0164
G1 X97.052 Y46.635 E.40924
G1 X97.586 Y46.635 E.0164
G1 X106.465 Y55.514 E.38604
G1 X106.465 Y54.981 E.0164
G1 X97.835 Y46.351 E.3752
G1 X97.835 Y45.818 E.0164
G1 X106.465 Y54.447 E.3752
G1 X106.465 Y53.913 E.0164
G1 X97.835 Y45.284 E.3752
G1 X97.835 Y44.751 E.0164
G1 X106.465 Y53.38 E.3752
G1 X106.465 Y52.846 E.0164
G1 X97.835 Y44.217 E.3752
G1 X97.835 Y43.683 E.0164
G1 X106.465 Y52.313 E.3752
G1 X106.465 Y51.779 E.0164
G1 X97.835 Y43.15 E.3752
G1 X97.835 Y42.616 E.0164
G1 X106.465 Y51.246 E.3752
G1 X106.465 Y50.712 E.0164
G1 X97.835 Y42.083 E.3752
G1 X97.835 Y41.549 E.0164
G1 X106.465 Y50.178 E.3752
G1 X106.465 Y49.645 E.0164
G1 X97.835 Y41.016 E.3752
G1 X97.835 Y40.482 E.0164
G1 X106.465 Y49.111 E.3752
G1 X106.465 Y48.578 E.0164
G1 X97.585 Y39.698 E.38607
G1 X97.585 Y39.165 E.0164
G1 X106.465 Y48.044 E.38607
G1 X106.465 Y47.511 E.0164
G1 X97.585 Y38.631 E.38607
G1 X97.585 Y38.098 E.0164
G1 X106.465 Y46.977 E.38607
G1 X106.465 Y46.443 E.0164
G1 X97.585 Y37.564 E.38607
G1 X97.585 Y37.031 E.0164
G1 X106.465 Y45.91 E.38607
G1 X106.465 Y45.376 E.0164
G1 X97.585 Y36.497 E.38607
G1 X97.585 Y35.963 E.0164
G1 X106.465 Y44.843 E.38607
G1 X106.465 Y44.309 E.0164
G1 X97.585 Y35.43 E.38607
G1 X97.585 Y34.896 E.0164
G1 X106.465 Y43.776 E.38607
G1 X106.465 Y43.242 E.0164
G1 X97.585 Y34.363 E.38607
G1 X97.585 Y33.829 E.0164
G1 X106.465 Y42.708 E.38607
G1 X106.465 Y42.175 E.0164
G1 X97.585 Y33.296 E.38607
G1 X97.585 Y32.762 E.0164
G1 X106.465 Y41.641 E.38607
G1 X106.465 Y41.108 E.0164
G1 X97.585 Y32.228 E.38607
G1 X97.585 Y31.695 E.0164
G1 X106.465 Y40.574 E.38607
G1 X106.465 Y40.041 E.0164
G1 X97.585 Y31.161 E.38607
G1 X97.585 Y30.628 E.0164
G1 X106.465 Y39.507 E.38607
G1 X106.465 Y38.974 E.0164
G1 X97.585 Y30.094 E.38607
G1 X97.585 Y29.561 E.0164
G1 X106.465 Y38.44 E.38607
G1 X106.465 Y37.906 E.0164
G1 X97.585 Y29.027 E.38607
G1 X97.585 Y28.635 E.01204
G1 X97.727 Y28.635 E.00436
G1 X106.465 Y37.373 E.3799
G1 X106.465 Y36.839 E.0164
G1 X98.261 Y28.635 E.3567
G1 X98.794 Y28.635 E.0164
G1 X106.465 Y36.306 E.3335
G1 X106.465 Y35.772 E.0164
G1 X99.135 Y28.443 E.31867
G1 X99.135 Y27.909 E.0164
G1 X106.465 Y35.239 E.31867
G1 X106.465 Y34.705 E.0164
G1 X99.135 Y27.376 E.31867
G1 X99.135 Y26.842 E.0164
G1 X106.465 Y34.171 E.31867
G1 X106.465 Y33.638 E.0164
G1 X99.135 Y26.308 E.31867
G1 X99.135 Y25.775 E.0164
G1 X106.465 Y33.104 E.31867
G1 X106.465 Y32.571 E.0164
G1 X99.135 Y25.241 E.31867
G1 X99.135 Y24.708 E.0164
G1 X106.465 Y32.037 E.31867
G1 X106.465 Y31.504 E.0164
G1 X99.135 Y24.174 E.31867
G1 X99.135 Y23.641 E.0164
G1 X106.465 Y30.97 E.31867
G1 X106.465 Y30.436 E.0164
G1 X99.135 Y23.107 E.31867
G1 X99.135 Y22.573 E.0164
G1 X106.465 Y29.903 E.31867
G1 X106.465 Y29.369 E.0164
G1 X82.031 Y4.935 E1.06237
G1 X82.564 Y4.935 E.0164
G1 X106.465 Y28.836 E1.03917
G1 X106.465 Y28.302 E.0164
G1 X83.098 Y4.935 E1.01597
G1 X83.631 Y4.935 E.0164
G1 X106.465 Y27.769 E.99277
G1 X106.465 Y27.235 E.0164
G1 X84.165 Y4.935 E.96957
G1 X84.699 Y4.935 E.0164
G1 X106.465 Y26.701 E.94637
G1 X106.465 Y26.168 E.0164
G1 X85.232 Y4.935 E.92317
G1 X85.766 Y4.935 E.0164
G1 X106.465 Y25.634 E.89997
G1 X106.465 Y25.101 E.0164
G1 X86.299 Y4.935 E.87677
G1 X86.833 Y4.935 E.0164
G1 X106.465 Y24.567 E.85357
G1 X106.465 Y24.034 E.0164
G1 X87.366 Y4.935 E.83037
G1 X87.9 Y4.935 E.0164
G1 X106.465 Y23.5 E.80718
G1 X106.465 Y22.966 E.0164
G1 X88.434 Y4.935 E.78398
G1 X88.967 Y4.935 E.0164
G1 X106.465 Y22.433 E.76078
G1 X106.465 Y21.899 E.0164
G1 X89.501 Y4.935 E.73758
G1 X90.034 Y4.935 E.0164
G1 X106.465 Y21.366 E.71438
G1 X106.465 Y20.832 E.0164
G1 X90.568 Y4.935 E.69118
G1 X91.101 Y4.935 E.0164
G1 X106.465 Y20.299 E.66798
G1 X106.465 Y19.765 E.0164
G1 X91.635 Y4.935 E.64478
G1 X92.169 Y4.935 E.0164
G1 X106.465 Y19.231 E.62158
G1 X106.465 Y18.698 E.0164
G1 X92.702 Y4.935 E.59838
G1 X93.236 Y4.935 E.0164
G1 X106.465 Y18.164 E.57519
G1 X106.465 Y17.631 E.0164
G1 X93.769 Y4.935 E.55199
G1 X94.303 Y4.935 E.0164
G1 X106.465 Y17.097 E.52879
G1 X106.465 Y16.564 E.0164
G1 X94.836 Y4.935 E.50559
G1 X95.37 Y4.935 E.0164
G1 X106.465 Y16.03 E.48239
G1 X106.465 Y15.496 E.0164
G1 X95.904 Y4.935 E.45919
G1 X96.437 Y4.935 E.0164
G1 X106.465 Y14.963 E.43599
G1 X106.465 Y14.429 E.0164
G1 X96.971 Y4.935 E.41279
G1 X97.504 Y4.935 E.0164
G1 X106.465 Y13.896 E.38959
G1 X106.465 Y13.362 E.0164
G1 X98.038 Y4.935 E.36639
G1 X98.571 Y4.935 E.0164
G1 X106.465 Y12.829 E.34319
G1 X106.465 Y12.295 E.0164
G1 X99.105 Y4.935 E.32
G1 X99.639 Y4.935 E.0164
G1 X106.465 Y11.761 E.2968
G1 X106.465 Y11.228 E.0164
G1 X100.172 Y4.935 E.2736
G1 X100.706 Y4.935 E.0164
G1 X106.465 Y10.694 E.2504
G1 X106.465 Y10.161 E.0164
G1 X101.239 Y4.935 E.2272
G1 X101.773 Y4.935 E.0164
G1 X106.465 Y9.627 E.204
G1 X106.465 Y9.094 E.0164
G1 X102.306 Y4.935 E.1808
G1 X102.84 Y4.935 E.0164
G1 X106.465 Y8.56 E.1576
G1 X106.465 Y8.027 E.0164
G1 X103.373 Y4.935 E.1344
G1 X103.907 Y4.935 E.0164
G1 X106.465 Y7.493 E.1112
G1 X106.465 Y6.959 E.0164
G1 X104.441 Y4.935 E.088
G1 X104.974 Y4.935 E.0164
G1 X106.465 Y6.426 E.06481
G1 X106.465 Y5.892 E.0164
G1 X105.508 Y4.935 E.04161
G1 X106.041 Y4.935 E.0164
G1 X106.634 Y5.528 E.02578
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X106.041 Y4.935 E-.3187
G1 X105.508 Y4.935 E-.20276
G1 X105.952 Y5.379 E-.23854
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 10/40
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
G17
G3 Z2.2 I1.217 J0 P1  F30000
; object ids of layer 10 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer10 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
M73 P79 R7
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z2.4 F30000
G1 X160.4 Y8 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z2.4 F30000
G1 X114.002 Y8.498 Z2.4
M73 P79 R6
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X129.41 Y13.907 Z2.4 F30000
G1 X93.11 Y73.11 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y67.898 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X84.278 Y67.898 E.29298
G1 X84.278 Y67.278 E.02057
G1 X93.122 Y67.278 E.29339
G1 X93.122 Y67.85 E.01899
; WIPE_START
G1 X91.122 Y67.861 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y73.502 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X93.122 Y73.502 E.00041
G1 X93.122 Y74.122 E.02057
G1 X84.278 Y74.122 E.29339
G1 X84.278 Y73.502 E.02057
G1 X93.05 Y73.502 E.29099
; WIPE_START
G1 X93.122 Y73.502 E-.02745
G1 X93.122 Y74.122 E-.23566
G1 X91.815 Y74.122 E-.49689
; WIPE_END
G1 E-.04 F1800
G1 X84.477 Y76.223 Z2.4 F30000
G1 X65.622 Y81.622 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X61.778 Y81.622 E.12753
G1 X61.778 Y77.778 E.12753
G1 X65.622 Y77.778 E.12753
G1 X65.622 Y81.562 E.12554
; WIPE_START
G1 X63.622 Y81.593 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X56.253 Y79.606 Z2.4 F30000
G1 X33.6 Y73.498 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X33.425 Y73.488 E.00579
G3 X33.591 Y67.903 I.284 J-2.787 E.27856
G3 X34.514 Y68.018 I.128 J2.724 E.03098
G3 X33.7 Y73.503 I-.804 J2.684 E.26522
G1 X33.66 Y73.501 E.00134
G1 X33.619 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.096 E.00476
G3 X33.611 Y68.294 I.244 J-2.396 E.22194
G3 X34.4 Y68.393 I-.039 J3.496 E.02449
G3 X33.936 Y73.098 I-.691 J2.307 E.20392
G1 X33.679 Y73.098 E.0079
; WIPE_START
M204 S10000
G1 X33.464 Y73.096 E-.08172
G1 X33 Y73.007 E-.17944
G1 X32.564 Y72.826 E-.1796
G1 X32.171 Y72.563 E-.17954
G1 X31.911 Y72.303 E-.13969
; WIPE_END
G1 E-.04 F1800
G1 X33.619 Y74.122 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X30.278 Y74.122 E.11084
G1 X30.278 Y67.278 E.22704
G1 X37.122 Y67.278 E.22704
G1 X37.122 Y74.122 E.22704
G1 X33.679 Y74.122 E.11422
; WIPE_START
G1 X31.679 Y74.122 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.222 Y66.509 Z2.4 F30000
G1 X34.852 Y29.622 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X34.852 Y28.102 E.05043
G1 X36.202 Y28.102 E.04478
G1 X36.202 Y22.778 E.17662
G1 X37.922 Y22.778 E.05706
G1 X37.922 Y29.622 E.22704
G1 X34.912 Y29.622 E.09985
; WIPE_START
G1 X34.852 Y28.102 E-.57811
G1 X35.331 Y28.102 E-.18189
; WIPE_END
G1 E-.04 F1800
G1 X35.065 Y35.73 Z2.4 F30000
G1 X34.71 Y45.91 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X30.29 Y45.91 E.13581
G1 X30.29 Y40.49 E.16654
G1 X30.54 Y40.49 E.00768
G1 X30.54 Y28.669 E.36323
G1 X30.54 Y28.269 E.01229
G1 F9901.871
G1 X30.54 Y27.869 E.01229
G1 F3789.734
G1 X30.54 Y27.71 E.00489
G1 F2160
G1 X29.19 Y27.71 E.04148
G1 X29.19 Y22.831 E.14992
G1 F2536.674
G1 X29.19 Y22.79 E.00126
G1 F7799.139
G1 X29.59 Y22.79 E.01229
G1 F12000
G1 X29.99 Y22.79 E.01229
G1 X30.54 Y22.79 E.0169
G1 X30.54 Y22.49 E.00922
G1 X34.46 Y22.49 E.12045
G1 X34.46 Y22.79 E.00922
G1 X35.01 Y22.79 E.0169
G1 X35.41 Y22.79 E.01229
G1 F7799.139
G1 X35.81 Y22.79 E.01229
G1 F2536.674
G1 X35.81 Y22.831 E.00126
G1 F2160
G1 X35.81 Y27.71 E.14992
G1 X34.46 Y27.71 E.04148
G1 F3789.734
G1 X34.46 Y27.869 E.00489
G1 F9901.871
G1 X34.46 Y28.269 E.01229
G1 F12000
G1 X34.46 Y28.669 E.01229
G1 X34.46 Y40.49 E.36323
G1 X34.71 Y40.49 E.00768
G1 X34.71 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X32.71 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.522 Y38.338 Z2.4 F30000
G1 X30.148 Y29.622 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X27.078 Y29.622 E.10184
G1 X27.078 Y22.778 E.22704
G1 X28.798 Y22.778 E.05706
G1 X28.798 Y28.102 E.17662
G1 X30.148 Y28.102 E.04478
G1 X30.148 Y29.562 E.04844
; WIPE_START
G1 X28.148 Y29.601 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.321 Y22.659 Z2.4 F30000
G1 X33.622 Y17.622 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X29.778 Y17.622 E.12753
G1 X29.778 Y13.778 E.12753
G1 X33.622 Y13.778 E.12753
G1 X33.622 Y17.562 E.12554
; WIPE_START
G1 X31.622 Y17.593 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.255 Y17.597 Z2.4 F30000
G1 X97.11 Y17.622 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X93.778 Y17.622 E.11054
G1 X93.778 Y13.778 E.12753
G1 X97.622 Y13.778 E.12753
G1 X97.622 Y17.622 E.12753
G1 X97.17 Y17.622 E.015
; WIPE_START
G1 X95.17 Y17.622 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.541 Y25.079 Z2.4 F30000
G1 X92.548 Y29.622 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X89.478 Y29.622 E.10184
G1 X89.478 Y22.778 E.22704
G1 X91.198 Y22.778 E.05706
G1 X91.198 Y28.102 E.17662
G1 X92.548 Y28.102 E.04478
G1 X92.548 Y29.562 E.04844
; WIPE_START
G1 X90.548 Y29.601 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.397 Y36.682 Z2.4 F30000
G1 X97.11 Y45.91 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.69 Y45.91 E.13581
G1 X92.69 Y40.49 E.16654
G1 X92.94 Y40.49 E.00768
G1 X92.94 Y28.669 E.36323
G1 X92.94 Y28.269 E.01229
G1 F9901.871
G1 X92.94 Y27.869 E.01229
G1 F3789.734
G1 X92.94 Y27.71 E.00489
G1 F2160
G1 X91.59 Y27.71 E.04148
G1 X91.59 Y22.831 E.14992
G1 F2536.674
G1 X91.59 Y22.79 E.00126
G1 F7799.139
G1 X91.99 Y22.79 E.01229
G1 F12000
G1 X92.39 Y22.79 E.01229
G1 X92.94 Y22.79 E.0169
G1 X92.94 Y22.49 E.00922
G1 X96.86 Y22.49 E.12045
G1 X96.86 Y22.79 E.00922
G1 X97.41 Y22.79 E.0169
G1 X97.81 Y22.79 E.01229
G1 F7799.139
G1 X98.21 Y22.79 E.01229
G1 F2536.674
G1 X98.21 Y22.831 E.00126
G1 F2160
G1 X98.21 Y27.71 E.14992
G1 X96.86 Y27.71 E.04148
G1 F3789.734
G1 X96.86 Y27.869 E.00489
G1 F9901.871
G1 X96.86 Y28.269 E.01229
G1 F12000
G1 X96.86 Y28.669 E.01229
G1 X96.86 Y40.49 E.36323
G1 X97.11 Y40.49 E.00768
G1 X97.11 Y45.85 E.1647
; WIPE_START
M204 S10000
G1 X95.11 Y45.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X96.107 Y38.31 Z2.4 F30000
G1 X97.252 Y29.622 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X97.252 Y28.102 E.05043
G1 X98.602 Y28.102 E.04478
G1 X98.602 Y22.778 E.17662
G1 X100.322 Y22.778 E.05706
G1 X100.322 Y29.622 E.22704
G1 X97.312 Y29.622 E.09985
; WIPE_START
G1 X97.252 Y28.102 E-.57812
G1 X97.731 Y28.102 E-.18188
; WIPE_END
G1 E-.04 F1800
G1 X98.862 Y35.65 Z2.4 F30000
G1 X107.19 Y91.19 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y91.19 E2.67265
G1 X20.21 Y4.21 E2.67265
G1 X107.19 Y4.21 E2.67265
G1 X107.19 Y91.13 E2.67081
M204 S10000
G1 X106.538 Y90.983 F30000
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X106.983 Y90.538 E.0193
G1 X106.983 Y90.005
G1 X106.005 Y90.983 E.04248
G1 X105.472 Y90.983
G1 X106.983 Y89.472 E.06565
G1 X106.983 Y88.939
G1 X104.939 Y90.983 E.08882
G1 X104.405 Y90.983
G1 X106.983 Y88.405 E.11199
G1 X106.983 Y87.872
G1 X103.872 Y90.983 E.13517
G1 X103.339 Y90.983
G1 X106.983 Y87.339 E.15834
G1 X106.983 Y86.806
G1 X102.806 Y90.983 E.18151
G1 X102.272 Y90.983
G1 X106.983 Y86.272 E.20468
G1 X106.983 Y85.739
G1 X101.739 Y90.983 E.22786
G1 X101.206 Y90.983
G1 X106.983 Y85.206 E.25103
G1 X106.983 Y84.673
G1 X100.673 Y90.983 E.2742
G1 X100.139 Y90.983
G1 X106.983 Y84.139 E.29737
G1 X106.983 Y83.606
G1 X99.606 Y90.983 E.32055
G1 X99.073 Y90.983
G1 X106.983 Y83.073 E.34372
G1 X106.983 Y82.54
G1 X98.54 Y90.983 E.36689
G1 X98.006 Y90.983
G1 X106.983 Y82.006 E.39007
G1 X106.983 Y81.473
G1 X97.473 Y90.983 E.41324
G1 X96.94 Y90.983
G1 X106.983 Y80.94 E.43641
G1 X106.983 Y80.407
G1 X96.407 Y90.983 E.45958
G1 X95.873 Y90.983
G1 X106.983 Y79.873 E.48276
G1 X106.983 Y79.34
G1 X95.34 Y90.983 E.50593
G1 X94.807 Y90.983
G1 X106.983 Y78.807 E.5291
G1 X106.983 Y78.273
G1 X94.273 Y90.983 E.55227
G1 X93.74 Y90.983
G1 X106.983 Y77.74 E.57545
G1 X106.983 Y77.207
G1 X93.207 Y90.983 E.59862
G1 X92.674 Y90.983
G1 X106.983 Y76.674 E.62179
G1 X106.983 Y76.14
G1 X92.14 Y90.983 E.64496
G1 X91.607 Y90.983
G1 X106.983 Y75.607 E.66814
G1 X106.983 Y75.074
G1 X91.074 Y90.983 E.69131
G1 X90.541 Y90.983
G1 X106.983 Y74.541 E.71448
G1 X106.983 Y74.007
G1 X90.007 Y90.983 E.73765
G1 X89.474 Y90.983
G1 X106.983 Y73.474 E.76083
G1 X106.983 Y72.941
G1 X88.941 Y90.983 E.784
G1 X88.408 Y90.983
G1 X106.983 Y72.408 E.80717
G1 X106.983 Y71.874
G1 X87.874 Y90.983 E.83035
G1 X87.341 Y90.983
G1 X106.983 Y71.341 E.85352
G1 X106.983 Y70.808
G1 X86.808 Y90.983 E.87669
G1 X86.275 Y90.983
G1 X106.983 Y70.275 E.89986
G1 X106.983 Y69.741
G1 X85.741 Y90.983 E.92304
G1 X85.208 Y90.983
G1 X106.983 Y69.208 E.94621
G1 X106.983 Y68.675
G1 X84.675 Y90.983 E.96938
G1 X84.142 Y90.983
G1 X106.983 Y68.142 E.99255
G1 X106.983 Y67.608
G1 X83.608 Y90.983 E1.01573
G1 X83.075 Y90.983
G1 X106.983 Y67.075 E1.0389
G1 X106.983 Y66.542
G1 X82.542 Y90.983 E1.06207
G1 X82.009 Y90.983
G1 X106.983 Y66.009 E1.08524
G1 X106.983 Y65.475
G1 X81.475 Y90.983 E1.10842
G1 X80.942 Y90.983
G1 X106.983 Y64.942 E1.13159
G1 X106.983 Y64.409
G1 X80.409 Y90.983 E1.15476
G1 X79.876 Y90.983
G1 X106.983 Y63.876 E1.17793
G1 X106.983 Y63.342
G1 X79.342 Y90.983 E1.20111
G1 X78.809 Y90.983
G1 X106.983 Y62.809 E1.22428
G1 X106.983 Y62.276
G1 X78.276 Y90.983 E1.24745
G1 X77.742 Y90.983
G1 X106.983 Y61.743 E1.27062
G1 X106.983 Y61.209
G1 X77.209 Y90.983 E1.2938
G1 X76.676 Y90.983
G1 X93.266 Y74.393 E.7209
G1 X92.732 Y74.393
G1 X76.143 Y90.983 E.7209
G1 X75.609 Y90.983
G1 X92.199 Y74.393 E.7209
G1 X91.666 Y74.393
G1 X75.076 Y90.983 E.7209
G1 X74.543 Y90.983
G1 X91.133 Y74.393 E.7209
G1 X90.599 Y74.393
G1 X74.01 Y90.983 E.7209
G1 X73.476 Y90.983
G1 X90.066 Y74.393 E.7209
G1 X89.533 Y74.393
G1 X72.943 Y90.983 E.7209
G1 X72.41 Y90.983
G1 X89 Y74.393 E.7209
G1 X88.466 Y74.393
G1 X71.877 Y90.983 E.7209
G1 X71.343 Y90.983
G1 X87.933 Y74.393 E.7209
G1 X87.4 Y74.393
G1 X70.81 Y90.983 E.7209
G1 X70.277 Y90.983
G1 X86.867 Y74.393 E.7209
G1 X86.333 Y74.393
G1 X69.744 Y90.983 E.7209
G1 X69.21 Y90.983
G1 X85.8 Y74.393 E.7209
G1 X85.267 Y74.393
G1 X68.677 Y90.983 E.7209
G1 X68.144 Y90.983
G1 X84.734 Y74.393 E.7209
G1 X84.2 Y74.393
M73 P80 R6
G1 X67.611 Y90.983 E.7209
G1 X67.077 Y90.983
G1 X84.007 Y74.053 E.73568
G1 X84.055 Y73.471
G1 X66.544 Y90.983 E.76095
G1 X66.011 Y90.983
G1 X84.055 Y72.938 E.78412
G1 X84.055 Y72.405
G1 X65.478 Y90.983 E.80729
G1 X64.944 Y90.983
G1 X84.055 Y71.872 E.83046
G1 X84.055 Y71.338
G1 X64.411 Y90.983 E.85364
G1 X63.878 Y90.983
G1 X84.055 Y70.805 E.87681
G1 X84.055 Y70.272
G1 X63.345 Y90.983 E.89998
G1 X62.811 Y90.983
G1 X84.055 Y69.739 E.92315
G1 X84.055 Y69.205
G1 X62.278 Y90.983 E.94633
G1 X61.745 Y90.983
G1 X84.055 Y68.672 E.9695
G1 X84.055 Y68.139
G1 X61.212 Y90.983 E.99267
G1 X60.678 Y90.983
G1 X84.029 Y67.632 E1.0147
G1 X84.007 Y67.12
G1 X60.145 Y90.983 E1.03693
; WIPE_START
M204 S10000
G1 X61.559 Y89.568 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X68.438 Y86.262 Z2.4 F30000
G1 X93.393 Y74.266 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X106.983 Y60.676 E.59054
G1 X106.983 Y60.143
G1 X93.367 Y73.758 E.59166
G1 X93.345 Y73.247
G1 X106.983 Y59.609 E.59263
G1 X106.983 Y59.076
G1 X93.345 Y72.714 E.59263
G1 X93.345 Y72.181
G1 X106.983 Y58.543 E.59263
G1 X106.983 Y58.01
G1 X93.345 Y71.648 E.59263
G1 X93.345 Y71.114
G1 X106.983 Y57.476 E.59263
G1 X106.983 Y56.943
G1 X93.345 Y70.581 E.59263
G1 X93.345 Y70.048
G1 X106.983 Y56.41 E.59263
G1 X106.983 Y55.877
G1 X93.345 Y69.515 E.59263
G1 X93.345 Y68.981
G1 X106.983 Y55.343 E.59263
G1 X106.983 Y54.81
G1 X93.345 Y68.448 E.59263
G1 X93.345 Y67.915
G1 X106.983 Y54.277 E.59263
G1 X106.983 Y53.744
G1 X93.393 Y67.333 E.59054
G1 X93.186 Y67.007
G1 X106.983 Y53.21 E.59954
G1 X106.983 Y52.677
G1 X92.653 Y67.007 E.62271
G1 X92.119 Y67.007
G1 X106.983 Y52.144 E.64588
G1 X106.983 Y51.611
G1 X91.586 Y67.007 E.66905
G1 X91.053 Y67.007
G1 X106.983 Y51.077 E.69223
G1 X106.983 Y50.544
G1 X90.52 Y67.007 E.7154
G1 X89.986 Y67.007
G1 X106.983 Y50.011 E.73857
G1 X106.983 Y49.478
G1 X89.453 Y67.007 E.76174
G1 X88.92 Y67.007
G1 X106.983 Y48.944 E.78492
G1 X106.983 Y48.411
G1 X88.387 Y67.007 E.80809
G1 X87.853 Y67.007
G1 X106.983 Y47.878 E.83126
G1 X106.983 Y47.345
G1 X87.32 Y67.007 E.85443
G1 X86.787 Y67.007
G1 X106.983 Y46.811 E.87761
G1 X106.983 Y46.278
G1 X86.254 Y67.007 E.90078
G1 X85.72 Y67.007
G1 X106.983 Y45.745 E.92395
G1 X106.983 Y45.212
G1 X85.187 Y67.007 E.94712
G1 X84.654 Y67.007
G1 X106.983 Y44.678 E.9703
G1 X106.983 Y44.145
G1 X84.12 Y67.007 E.99347
; WIPE_START
M204 S10000
G1 X85.535 Y65.593 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X90.865 Y60.13 Z2.4 F30000
G1 X106.983 Y43.612 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X59.612 Y90.983 E2.05849
G1 X59.078 Y90.983
G1 X106.983 Y43.078 E2.08167
G1 X106.983 Y42.545
G1 X58.545 Y90.983 E2.10484
G1 X58.012 Y90.983
G1 X106.983 Y42.012 E2.12801
G1 X106.983 Y41.479
G1 X57.479 Y90.983 E2.15118
G1 X56.945 Y90.983
G1 X106.983 Y40.945 E2.17436
G1 X106.983 Y40.412
G1 X65.893 Y81.502 E1.78555
G1 X65.893 Y80.969
G1 X106.983 Y39.879 E1.78555
G1 X106.983 Y39.346
G1 X65.893 Y80.435 E1.78555
G1 X65.893 Y79.902
G1 X106.983 Y38.812 E1.78555
G1 X106.983 Y38.279
G1 X65.893 Y79.369 E1.78555
G1 X65.893 Y78.836
G1 X106.983 Y37.746 E1.78555
G1 X106.983 Y37.213
G1 X65.893 Y78.302 E1.78555
G1 X65.893 Y77.769
G1 X106.983 Y36.679 E1.78555
G1 X106.983 Y36.146
G1 X97.317 Y45.811 E.42
G1 X97.317 Y45.278
G1 X106.983 Y35.613 E.42
G1 X106.983 Y35.08
G1 X97.317 Y44.745 E.42
G1 X97.317 Y44.212
G1 X106.983 Y34.546 E.42
G1 X106.983 Y34.013
G1 X97.317 Y43.678 E.42
G1 X97.317 Y43.145
G1 X106.983 Y33.48 E.42
G1 X106.983 Y32.947
G1 X97.317 Y42.612 E.42
G1 X97.317 Y42.079
G1 X106.983 Y32.413 E.42
G1 X106.983 Y31.88
G1 X97.317 Y41.545 E.42
G1 X97.317 Y41.012
G1 X106.983 Y31.347 E.42
G1 X106.983 Y30.814
G1 X97.317 Y40.479 E.42
G1 X97.067 Y40.196
G1 X106.983 Y30.28 E.43086
G1 X106.983 Y29.747
G1 X97.067 Y39.662 E.43086
G1 X97.067 Y39.129
G1 X106.983 Y29.214 E.43086
G1 X106.983 Y28.681
G1 X97.067 Y38.596 E.43086
G1 X97.067 Y38.063
G1 X106.983 Y28.147 E.43086
G1 X106.983 Y27.614
G1 X97.067 Y37.529 E.43086
G1 X97.067 Y36.996
M73 P81 R6
G1 X106.983 Y27.081 E.43086
G1 X106.983 Y26.548
G1 X97.067 Y36.463 E.43086
G1 X97.067 Y35.929
G1 X106.983 Y26.014 E.43086
G1 X106.983 Y25.481
G1 X97.067 Y35.396 E.43086
G1 X97.067 Y34.863
G1 X106.983 Y24.948 E.43086
G1 X106.983 Y24.414
G1 X97.067 Y34.33 E.43086
G1 X97.067 Y33.796
G1 X106.983 Y23.881 E.43086
G1 X106.983 Y23.348
G1 X100.593 Y29.738 E.27767
G1 X100.593 Y29.204
G1 X106.983 Y22.815 E.27767
G1 X106.983 Y22.281
G1 X100.593 Y28.671 E.27766
G1 X100.593 Y28.138
G1 X106.983 Y21.748 E.27766
G1 X106.983 Y21.215
G1 X100.593 Y27.605 E.27766
G1 X100.593 Y27.071
G1 X106.983 Y20.682 E.27767
G1 X106.983 Y20.148
G1 X100.593 Y26.538 E.27766
G1 X100.593 Y26.005
G1 X106.983 Y19.615 E.27766
G1 X106.983 Y19.082
G1 X100.593 Y25.472 E.27766
G1 X100.593 Y24.938
G1 X106.983 Y18.549 E.27767
G1 X106.983 Y18.015
G1 X100.593 Y24.405 E.27766
G1 X100.593 Y23.872
G1 X106.983 Y17.482 E.27766
G1 X106.983 Y16.949
G1 X100.593 Y23.339 E.27766
G1 X100.593 Y22.805
G1 X106.983 Y16.416 E.27767
G1 X106.983 Y15.882
G1 X100.358 Y22.507 E.28788
G1 X99.825 Y22.507
G1 X106.983 Y15.349 E.31105
G1 X106.983 Y14.816
G1 X99.271 Y22.528 E.33512
G1 X98.71 Y22.555
G1 X106.983 Y14.283 E.35949
G1 X106.983 Y13.749
G1 X98.177 Y22.555 E.38266
G1 X97.643 Y22.555
G1 X106.983 Y13.216 E.40583
G1 X106.983 Y12.683
G1 X97.11 Y22.555 E.42901
G1 X96.85 Y22.283
G1 X106.983 Y12.15 E.44033
G1 X106.983 Y11.616
G1 X96.316 Y22.283 E.4635
G1 X95.783 Y22.283
G1 X106.983 Y11.083 E.48668
G1 X106.983 Y10.55
G1 X95.25 Y22.283 E.50985
G1 X94.717 Y22.283
G1 X106.983 Y10.017 E.53302
G1 X106.983 Y9.483
G1 X94.183 Y22.283 E.55619
G1 X93.65 Y22.283
G1 X106.983 Y8.95 E.57937
G1 X106.983 Y8.417
G1 X97.893 Y17.507 E.39499
G1 X97.893 Y16.973
G1 X106.983 Y7.883 E.39499
G1 X106.983 Y7.35
G1 X97.893 Y16.44 E.39499
G1 X97.893 Y15.907
G1 X106.983 Y6.817 E.39499
G1 X106.983 Y6.284
G1 X97.893 Y15.373 E.39499
G1 X97.893 Y14.84
G1 X106.983 Y5.75 E.39499
G1 X106.983 Y5.217
G1 X97.893 Y14.307 E.39499
G1 X97.893 Y13.774
G1 X106.983 Y4.684 E.39499
G1 X106.716 Y4.417
G1 X97.626 Y13.507 E.39499
G1 X97.093 Y13.507
G1 X106.183 Y4.417 E.39499
G1 X105.649 Y4.417
G1 X96.56 Y13.507 E.39499
G1 X96.026 Y13.507
G1 X105.116 Y4.417 E.39499
G1 X104.583 Y4.417
G1 X95.493 Y13.507 E.39499
G1 X94.96 Y13.507
G1 X104.05 Y4.417 E.39499
G1 X103.516 Y4.417
G1 X94.427 Y13.507 E.39499
G1 X93.893 Y13.507
G1 X102.983 Y4.417 E.39499
; WIPE_START
M204 S10000
G1 X101.569 Y5.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.133 Y13.065 Z2.4 F30000
G1 X97.507 Y17.893 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X93.117 Y22.283 E.19076
G1 X92.311 Y22.555
G1 X96.973 Y17.893 E.2026
G1 X96.44 Y17.893
G1 X91.778 Y22.555 E.2026
G1 X91.244 Y22.555
G1 X95.907 Y17.893 E.2026
G1 X95.373 Y17.893
G1 X90.711 Y22.555 E.2026
G1 X90.226 Y22.507
G1 X94.84 Y17.893 E.20051
G1 X94.307 Y17.893
G1 X89.693 Y22.507 E.20051
; WIPE_START
M204 S10000
G1 X91.107 Y21.093 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X96.66 Y26.33 Z2.4 F30000
G1 X100.438 Y29.893 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X97.067 Y33.263 E.14646
G1 X97.067 Y32.73
G1 X99.904 Y29.893 E.12328
G1 X99.371 Y29.893
G1 X97.067 Y32.197 E.10011
G1 X97.067 Y31.663
G1 X98.838 Y29.893 E.07694
G1 X98.305 Y29.893
G1 X97.067 Y31.13 E.05377
G1 X97.067 Y30.597
G1 X97.771 Y29.893 E.03059
; WIPE_START
M204 S10000
G1 X97.067 Y30.597 E-.37835
G1 X97.067 Y31.13 E-.20264
G1 X97.4 Y30.797 E-.17901
; WIPE_END
G1 E-.04 F1800
G1 X97.207 Y38.427 Z2.4 F30000
G1 X97.011 Y46.117 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X65.622 Y77.507 E1.36404
G1 X65.088 Y77.507
G1 X96.478 Y46.117 E1.36404
G1 X95.945 Y46.117
G1 X64.555 Y77.507 E1.36404
G1 X64.022 Y77.507
G1 X95.412 Y46.117 E1.36404
G1 X94.878 Y46.117
G1 X63.489 Y77.507 E1.36404
G1 X62.955 Y77.507
G1 X94.345 Y46.117 E1.36404
G1 X93.812 Y46.117
G1 X62.422 Y77.507 E1.36404
G1 X61.889 Y77.507
G1 X93.279 Y46.117 E1.36404
; WIPE_START
M204 S10000
G1 X91.864 Y47.532 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.218 Y53.587 Z2.4 F30000
G1 X65.502 Y81.893 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X56.412 Y90.983 E.39499
G1 X55.879 Y90.983
G1 X64.969 Y81.893 E.39499
G1 X64.435 Y81.893
G1 X55.346 Y90.983 E.39499
G1 X54.812 Y90.983
G1 X63.902 Y81.893 E.39499
G1 X63.369 Y81.893
G1 X54.279 Y90.983 E.39499
G1 X53.746 Y90.983
G1 X62.836 Y81.893 E.39499
G1 X62.302 Y81.893
G1 X53.213 Y90.983 E.39499
G1 X52.679 Y90.983
M73 P82 R6
G1 X61.769 Y81.893 E.39499
G1 X61.507 Y81.622
G1 X52.146 Y90.983 E.40678
G1 X51.613 Y90.983
G1 X61.507 Y81.088 E.42995
G1 X61.507 Y80.555
G1 X51.08 Y90.983 E.45313
G1 X50.546 Y90.983
G1 X61.507 Y80.022 E.4763
G1 X61.507 Y79.489
G1 X50.013 Y90.983 E.49947
G1 X49.48 Y90.983
G1 X61.507 Y78.955 E.52264
G1 X61.507 Y78.422
G1 X48.947 Y90.983 E.54582
G1 X48.413 Y90.983
G1 X61.507 Y77.889 E.56899
; WIPE_START
M204 S10000
G1 X60.093 Y79.303 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X65.446 Y73.863 Z2.4 F30000
G1 X92.745 Y46.117 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X47.88 Y90.983 E1.94961
G1 X47.347 Y90.983
G1 X92.483 Y45.847 E1.96137
G1 X92.483 Y45.314
G1 X46.814 Y90.983 E1.98454
G1 X46.28 Y90.983
G1 X92.483 Y44.78 E2.00771
G1 X92.483 Y44.247
G1 X45.747 Y90.983 E2.03089
G1 X45.214 Y90.983
G1 X92.483 Y43.714 E2.05406
G1 X92.483 Y43.181
G1 X44.681 Y90.983 E2.07723
G1 X44.147 Y90.983
G1 X92.483 Y42.647 E2.1004
G1 X92.483 Y42.114
G1 X43.614 Y90.983 E2.12358
G1 X43.081 Y90.983
G1 X92.483 Y41.581 E2.14675
G1 X92.483 Y41.048
G1 X42.547 Y90.983 E2.16992
G1 X42.014 Y90.983
G1 X92.483 Y40.514 E2.1931
G1 X92.733 Y39.731
G1 X41.481 Y90.983 E2.22713
G1 X40.948 Y90.983
G1 X92.733 Y39.198 E2.2503
G1 X92.733 Y38.664
G1 X40.414 Y90.983 E2.27348
G1 X39.881 Y90.983
G1 X92.733 Y38.131 E2.29665
G1 X92.733 Y37.598
G1 X39.348 Y90.983 E2.31982
M73 P82 R5
G1 X38.815 Y90.983
G1 X92.733 Y37.065 E2.34299
G1 X92.733 Y36.531
G1 X38.281 Y90.983 E2.36617
G1 X37.748 Y90.983
G1 X92.733 Y35.998 E2.38934
G1 X92.733 Y35.465
G1 X37.215 Y90.983 E2.41251
G1 X36.682 Y90.983
G1 X92.733 Y34.932 E2.43569
G1 X92.733 Y34.398
G1 X36.148 Y90.983 E2.45886
G1 X35.615 Y90.983
G1 X92.733 Y33.865 E2.48203
G1 X92.733 Y33.332
G1 X35.082 Y90.983 E2.5052
G1 X34.549 Y90.983
G1 X92.733 Y32.799 E2.52838
G1 X92.733 Y32.265
G1 X34.015 Y90.983 E2.55155
G1 X33.482 Y90.983
G1 X92.733 Y31.732 E2.57472
G1 X92.733 Y31.199
G1 X32.949 Y90.983 E2.59789
G1 X32.416 Y90.983
G1 X92.733 Y30.666 E2.62107
G1 X92.733 Y30.132
G1 X31.882 Y90.983 E2.64424
G1 X31.349 Y90.983
G1 X92.487 Y29.845 E2.65674
G1 X91.906 Y29.893
G1 X30.816 Y90.983 E2.65465
G1 X30.283 Y90.983
G1 X91.372 Y29.893 E2.65465
G1 X90.839 Y29.893
G1 X29.749 Y90.983 E2.65465
G1 X29.216 Y90.983
G1 X90.306 Y29.893 E2.65465
G1 X89.773 Y29.893
G1 X28.683 Y90.983 E2.65465
G1 X28.15 Y90.983
G1 X89.275 Y29.857 E2.6562
G1 X89.207 Y29.392
G1 X27.616 Y90.983 E2.67642
G1 X27.083 Y90.983
G1 X89.207 Y28.859 E2.69959
G1 X89.207 Y28.325
G1 X26.55 Y90.983 E2.72277
G1 X26.017 Y90.983
G1 X89.207 Y27.792 E2.74594
G1 X89.207 Y27.259
G1 X25.483 Y90.983 E2.76911
G1 X24.95 Y90.983
G1 X89.207 Y26.726 E2.79228
G1 X89.207 Y26.192
G1 X24.417 Y90.983 E2.81546
G1 X23.883 Y90.983
G1 X89.207 Y25.659 E2.83863
G1 X89.207 Y25.126
G1 X23.35 Y90.983 E2.8618
G1 X22.817 Y90.983
G1 X89.207 Y24.592 E2.88497
G1 X89.207 Y24.059
G1 X22.284 Y90.983 E2.90815
G1 X21.75 Y90.983
G1 X89.207 Y23.526 E2.93132
G1 X89.207 Y22.993
G1 X21.217 Y90.983 E2.95449
G1 X20.684 Y90.983
G1 X37.274 Y74.393 E.7209
G1 X36.74 Y74.393
G1 X20.417 Y90.716 E.70931
G1 X20.417 Y90.183
G1 X36.207 Y74.393 E.68614
G1 X35.674 Y74.393
G1 X20.417 Y89.649 E.66297
G1 X20.417 Y89.116
G1 X35.141 Y74.393 E.6398
G1 X34.607 Y74.393
G1 X20.417 Y88.583 E.61662
G1 X20.417 Y88.05
G1 X34.074 Y74.393 E.59345
G1 X33.541 Y74.393
G1 X20.417 Y87.516 E.57028
G1 X20.417 Y86.983
G1 X33.008 Y74.393 E.54711
G1 X32.474 Y74.393
G1 X20.417 Y86.45 E.52393
G1 X20.417 Y85.917
G1 X31.941 Y74.393 E.50076
G1 X31.408 Y74.393
G1 X20.417 Y85.383 E.47759
G1 X20.417 Y84.85
G1 X30.875 Y74.393 E.45442
G1 X30.341 Y74.393
G1 X20.417 Y84.317 E.43124
G1 X20.417 Y83.784
G1 X30.007 Y74.194 E.41672
G1 X30.007 Y73.661
G1 X20.417 Y83.25 E.41672
G1 X20.417 Y82.717
G1 X30.007 Y73.127 E.41672
G1 X30.007 Y72.594
G1 X20.417 Y82.184 E.41672
G1 X20.417 Y81.651
G1 X30.007 Y72.061 E.41672
G1 X30.007 Y71.528
G1 X20.417 Y81.117 E.41672
G1 X20.417 Y80.584
G1 X30.007 Y70.994 E.41672
G1 X30.007 Y70.461
M73 P83 R5
G1 X20.417 Y80.051 E.41672
G1 X20.417 Y79.518
G1 X30.007 Y69.928 E.41672
G1 X30.007 Y69.395
G1 X20.417 Y78.984 E.41672
G1 X20.417 Y78.451
G1 X30.007 Y68.861 E.41672
G1 X30.007 Y68.328
G1 X20.417 Y77.918 E.41672
G1 X20.417 Y77.384
G1 X30.007 Y67.795 E.41672
G1 X30.007 Y67.261
G1 X20.417 Y76.851 E.41672
; WIPE_START
M204 S10000
G1 X21.832 Y75.437 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X29.443 Y74.868 Z2.4 F30000
G1 X37.393 Y74.274 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X93.774 Y17.893 E2.45002
G1 X93.507 Y17.626
G1 X37.393 Y73.74 E2.43844
G1 X37.393 Y73.207
G1 X93.507 Y17.093 E2.43844
G1 X93.507 Y16.56
G1 X37.393 Y72.674 E2.43844
G1 X37.393 Y72.141
G1 X93.507 Y16.026 E2.43844
G1 X93.507 Y15.493
G1 X37.393 Y71.607 E2.43844
G1 X37.393 Y71.074
G1 X93.507 Y14.96 E2.43844
G1 X93.507 Y14.427
G1 X37.393 Y70.541 E2.43844
G1 X37.393 Y70.008
G1 X93.507 Y13.893 E2.43844
; WIPE_START
M204 S10000
G1 X92.093 Y15.308 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X97.353 Y9.777 Z2.4 F30000
G1 X102.45 Y4.417 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X37.393 Y69.474 E2.82704
G1 X37.393 Y68.941
G1 X101.917 Y4.417 E2.80387
G1 X101.383 Y4.417
G1 X37.393 Y68.408 E2.7807
G1 X37.393 Y67.875
G1 X100.85 Y4.417 E2.75752
G1 X100.317 Y4.417
G1 X37.393 Y67.341 E2.73435
G1 X37.194 Y67.007
G1 X99.784 Y4.417 E2.71983
G1 X99.25 Y4.417
G1 X36.661 Y67.007 E2.71983
G1 X36.127 Y67.007
G1 X98.717 Y4.417 E2.71983
G1 X98.184 Y4.417
G1 X35.594 Y67.007 E2.71983
G1 X35.061 Y67.007
G1 X97.651 Y4.417 E2.71983
G1 X97.117 Y4.417
G1 X34.528 Y67.007 E2.71983
G1 X33.994 Y67.007
G1 X96.584 Y4.417 E2.71983
G1 X96.051 Y4.417
G1 X33.461 Y67.007 E2.71983
G1 X32.928 Y67.007
G1 X95.518 Y4.417 E2.71983
G1 X94.984 Y4.417
G1 X32.395 Y67.007 E2.71983
G1 X31.861 Y67.007
G1 X94.451 Y4.417 E2.71983
G1 X93.918 Y4.417
G1 X31.328 Y67.007 E2.71983
G1 X30.795 Y67.007
G1 X93.385 Y4.417 E2.71983
G1 X92.851 Y4.417
G1 X30.261 Y67.007 E2.71983
; WIPE_START
M204 S10000
G1 X31.676 Y65.593 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X26.149 Y70.857 Z2.4 F30000
G1 X20.417 Y76.318 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X92.318 Y4.417 E3.12443
G1 X91.785 Y4.417
G1 X20.417 Y75.785 E3.10126
G1 X20.417 Y75.251
G1 X91.251 Y4.417 E3.07808
G1 X90.718 Y4.417
G1 X20.417 Y74.718 E3.05491
G1 X20.417 Y74.185
G1 X90.185 Y4.417 E3.03174
G1 X89.652 Y4.417
G1 X20.417 Y73.652 E3.00857
G1 X20.417 Y73.118
G1 X89.118 Y4.417 E2.98539
G1 X88.585 Y4.417
G1 X20.417 Y72.585 E2.96222
G1 X20.417 Y72.052
M73 P84 R5
G1 X88.052 Y4.417 E2.93905
G1 X87.519 Y4.417
G1 X20.417 Y71.519 E2.91588
G1 X20.417 Y70.985
G1 X86.985 Y4.417 E2.8927
G1 X86.452 Y4.417
G1 X20.417 Y70.452 E2.86953
G1 X20.417 Y69.919
G1 X85.919 Y4.417 E2.84636
G1 X85.386 Y4.417
G1 X20.417 Y69.386 E2.82318
G1 X20.417 Y68.852
G1 X84.852 Y4.417 E2.80001
G1 X84.319 Y4.417
G1 X20.417 Y68.319 E2.77684
G1 X20.417 Y67.786
G1 X83.786 Y4.417 E2.75367
G1 X83.253 Y4.417
G1 X20.417 Y67.253 E2.73049
G1 X20.417 Y66.719
G1 X82.719 Y4.417 E2.70732
G1 X82.186 Y4.417
G1 X20.417 Y66.186 E2.68415
G1 X20.417 Y65.653
G1 X81.653 Y4.417 E2.66098
G1 X81.12 Y4.417
G1 X20.417 Y65.12 E2.6378
G1 X20.417 Y64.586
G1 X80.586 Y4.417 E2.61463
G1 X80.053 Y4.417
G1 X20.417 Y64.053 E2.59146
G1 X20.417 Y63.52
G1 X79.52 Y4.417 E2.56829
G1 X78.987 Y4.417
G1 X20.417 Y62.987 E2.54511
G1 X20.417 Y62.453
G1 X78.453 Y4.417 E2.52194
G1 X77.92 Y4.417
G1 X20.417 Y61.92 E2.49877
G1 X20.417 Y61.387
G1 X77.387 Y4.417 E2.4756
G1 X76.854 Y4.417
G1 X20.417 Y60.854 E2.45242
G1 X20.417 Y60.32
G1 X34.62 Y46.117 E.61718
G1 X34.087 Y46.117
G1 X20.417 Y59.787 E.59401
G1 X20.417 Y59.254
G1 X33.554 Y46.117 E.57084
G1 X33.02 Y46.117
G1 X20.417 Y58.72 E.54767
G1 X20.417 Y58.187
G1 X32.487 Y46.117 E.52449
G1 X31.954 Y46.117
G1 X20.417 Y57.654 E.50132
G1 X20.417 Y57.121
G1 X31.421 Y46.117 E.47815
G1 X30.887 Y46.117
G1 X20.417 Y56.587 E.45497
G1 X20.417 Y56.054
G1 X30.354 Y46.117 E.4318
G1 X30.083 Y45.856
G1 X20.417 Y55.521 E.42
G1 X20.417 Y54.988
G1 X30.083 Y45.322 E.42
G1 X30.083 Y44.789
G1 X20.417 Y54.454 E.42
G1 X20.417 Y53.921
G1 X30.083 Y44.256 E.42
G1 X30.083 Y43.723
G1 X20.417 Y53.388 E.42
G1 X20.417 Y52.855
G1 X30.083 Y43.189 E.42
G1 X30.083 Y42.656
G1 X20.417 Y52.321 E.42
G1 X20.417 Y51.788
G1 X30.083 Y42.123 E.42
G1 X30.083 Y41.59
G1 X20.417 Y51.255 E.42
G1 X20.417 Y50.722
G1 X30.083 Y41.056 E.42
G1 X30.083 Y40.523
G1 X20.417 Y50.188 E.42
G1 X20.417 Y49.655
G1 X30.333 Y39.74 E.43086
G1 X30.333 Y39.207
G1 X20.417 Y49.122 E.43086
G1 X20.417 Y48.589
G1 X30.333 Y38.673 E.43086
G1 X30.333 Y38.14
G1 X20.417 Y48.055 E.43086
G1 X20.417 Y47.522
G1 X30.333 Y37.607 E.43086
G1 X30.333 Y37.074
M73 P85 R5
G1 X20.417 Y46.989 E.43086
G1 X20.417 Y46.456
G1 X30.333 Y36.54 E.43086
G1 X30.333 Y36.007
G1 X20.417 Y45.922 E.43086
G1 X20.417 Y45.389
G1 X30.333 Y35.474 E.43086
G1 X30.333 Y34.941
M73 P85 R4
G1 X20.417 Y44.856 E.43086
G1 X20.417 Y44.323
G1 X30.333 Y34.407 E.43086
G1 X30.333 Y33.874
G1 X20.417 Y43.789 E.43086
G1 X20.417 Y43.256
G1 X30.333 Y33.341 E.43086
G1 X30.333 Y32.808
G1 X20.417 Y42.723 E.43086
G1 X20.417 Y42.189
G1 X30.333 Y32.274 E.43086
G1 X30.333 Y31.741
G1 X20.417 Y41.656 E.43086
G1 X20.417 Y41.123
G1 X30.333 Y31.208 E.43086
G1 X30.333 Y30.675
G1 X20.417 Y40.59 E.43086
G1 X20.417 Y40.056
G1 X30.333 Y30.141 E.43086
G1 X30.096 Y29.845
G1 X20.417 Y39.523 E.42058
G1 X20.417 Y38.99
G1 X29.514 Y29.893 E.39531
G1 X28.981 Y29.893
G1 X20.417 Y38.457 E.37214
G1 X20.417 Y37.923
G1 X28.448 Y29.893 E.34897
G1 X27.915 Y29.893
G1 X20.417 Y37.39 E.32579
G1 X20.417 Y36.857
G1 X27.381 Y29.893 E.30262
G1 X26.88 Y29.861
G1 X20.417 Y36.324 E.28081
G1 X20.417 Y35.79
G1 X26.807 Y29.401 E.27767
G1 X26.807 Y28.867
G1 X20.417 Y35.257 E.27767
G1 X20.417 Y34.724
G1 X26.807 Y28.334 E.27767
G1 X26.807 Y27.801
G1 X20.417 Y34.191 E.27767
G1 X20.417 Y33.657
G1 X26.807 Y27.268 E.27767
G1 X26.807 Y26.734
G1 X20.417 Y33.124 E.27767
G1 X20.417 Y32.591
G1 X26.807 Y26.201 E.27767
G1 X26.807 Y25.668
G1 X20.417 Y32.058 E.27767
G1 X20.417 Y31.524
G1 X26.807 Y25.135 E.27767
G1 X26.807 Y24.601
G1 X20.417 Y30.991 E.27766
G1 X20.417 Y30.458
G1 X26.807 Y24.068 E.27766
G1 X26.807 Y23.535
G1 X20.417 Y29.925 E.27767
G1 X20.417 Y29.391
G1 X26.807 Y23.002 E.27767
; WIPE_START
M204 S10000
G1 X25.393 Y24.416 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.496 Y31.389 Z2.4 F30000
G1 X34.917 Y45.82 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X76.32 Y4.417 E1.79916
G1 X75.787 Y4.417
G1 X34.917 Y45.287 E1.77598
G1 X34.917 Y44.754
G1 X75.254 Y4.417 E1.75281
G1 X74.72 Y4.417
G1 X34.917 Y44.22 E1.72964
G1 X34.917 Y43.687
G1 X74.187 Y4.417 E1.70646
G1 X73.654 Y4.417
G1 X34.917 Y43.154 E1.68329
G1 X34.917 Y42.621
G1 X73.121 Y4.417 E1.66012
G1 X72.587 Y4.417
G1 X34.917 Y42.087 E1.63695
G1 X34.917 Y41.554
G1 X72.054 Y4.417 E1.61377
G1 X71.521 Y4.417
G1 X34.917 Y41.021 E1.5906
G1 X34.917 Y40.488
G1 X70.988 Y4.417 E1.56743
G1 X70.454 Y4.417
G1 X34.667 Y40.204 E1.55512
G1 X34.667 Y39.671
G1 X69.921 Y4.417 E1.53195
G1 X69.388 Y4.417
G1 X34.667 Y39.138 E1.50877
G1 X34.667 Y38.605
G1 X68.855 Y4.417 E1.4856
G1 X68.321 Y4.417
G1 X34.667 Y38.071 E1.46243
G1 X34.667 Y37.538
G1 X67.788 Y4.417 E1.43926
G1 X67.255 Y4.417
G1 X34.667 Y37.005 E1.41608
G1 X34.667 Y36.472
G1 X66.722 Y4.417 E1.39291
G1 X66.188 Y4.417
G1 X34.667 Y35.938 E1.36974
G1 X34.667 Y35.405
G1 X65.655 Y4.417 E1.34657
G1 X65.122 Y4.417
G1 X34.667 Y34.872 E1.32339
G1 X34.667 Y34.339
G1 X64.589 Y4.417 E1.30022
G1 X64.055 Y4.417
G1 X34.667 Y33.805 E1.27705
G1 X34.667 Y33.272
M73 P86 R4
G1 X38.047 Y29.893 E.14684
G1 X37.513 Y29.893
G1 X34.667 Y32.739 E.12367
G1 X34.667 Y32.206
G1 X36.98 Y29.893 E.1005
G1 X36.447 Y29.893
G1 X34.667 Y31.672 E.07732
G1 X34.667 Y31.139
G1 X35.914 Y29.893 E.05415
G1 X35.38 Y29.893
G1 X34.667 Y30.606 E.03098
M204 S10000
G1 X38.193 Y29.747 F30000
G1 F12000
M204 S2000
G1 X63.522 Y4.417 E1.10068
G1 X62.989 Y4.417
G1 X38.193 Y29.213 E1.0775
G1 X38.193 Y28.68
G1 X62.456 Y4.417 E1.05433
G1 X61.922 Y4.417
G1 X38.193 Y28.147 E1.03116
G1 X38.193 Y27.614
G1 X61.389 Y4.417 E1.00799
G1 X60.856 Y4.417
G1 X38.193 Y27.08 E.98481
G1 X38.193 Y26.547
G1 X60.323 Y4.417 E.96164
G1 X59.789 Y4.417
G1 X38.193 Y26.014 E.93847
G1 X38.193 Y25.481
G1 X59.256 Y4.417 E.9153
G1 X58.723 Y4.417
G1 X38.193 Y24.947 E.89212
G1 X38.193 Y24.414
G1 X58.19 Y4.417 E.86895
G1 X57.656 Y4.417
G1 X38.193 Y23.881 E.84578
G1 X38.193 Y23.347
G1 X57.123 Y4.417 E.82261
G1 X56.59 Y4.417
G1 X38.193 Y22.814 E.79943
G1 X37.967 Y22.507
G1 X56.056 Y4.417 E.78609
G1 X55.523 Y4.417
G1 X37.433 Y22.507 E.78609
G1 X36.886 Y22.522
G1 X54.99 Y4.417 E.78672
G1 X54.457 Y4.417
G1 X36.319 Y22.555 E.78818
G1 X35.786 Y22.555
G1 X53.923 Y4.417 E.78818
G1 X53.39 Y4.417
G1 X35.252 Y22.555 E.78818
G1 X34.719 Y22.555
G1 X52.857 Y4.417 E.78818
G1 X52.324 Y4.417
G1 X34.458 Y22.283 E.77633
G1 X33.925 Y22.283
G1 X51.79 Y4.417 E.77633
G1 X51.257 Y4.417
G1 X33.392 Y22.283 E.77633
G1 X32.859 Y22.283
G1 X50.724 Y4.417 E.77633
G1 X50.191 Y4.417
G1 X32.325 Y22.283 E.77633
G1 X31.792 Y22.283
G1 X49.657 Y4.417 E.77633
G1 X49.124 Y4.417
G1 X31.259 Y22.283 E.77633
G1 X30.726 Y22.283
G1 X48.591 Y4.417 E.77633
G1 X48.058 Y4.417
G1 X29.92 Y22.555 E.78818
G1 X29.386 Y22.555
G1 X47.524 Y4.417 E.78818
G1 X46.991 Y4.417
G1 X33.893 Y17.516 E.56918
G1 X33.893 Y16.982
G1 X46.458 Y4.417 E.54601
G1 X45.925 Y4.417
G1 X33.893 Y16.449 E.52284
G1 X33.893 Y15.916
G1 X45.391 Y4.417 E.49966
G1 X44.858 Y4.417
G1 X33.893 Y15.383 E.47649
G1 X33.893 Y14.849
G1 X44.325 Y4.417 E.45332
G1 X43.792 Y4.417
G1 X33.893 Y14.316 E.43015
G1 X33.893 Y13.783
G1 X43.258 Y4.417 E.40697
G1 X42.725 Y4.417
G1 X33.635 Y13.507 E.39499
G1 X33.102 Y13.507
G1 X42.192 Y4.417 E.39499
G1 X41.659 Y4.417
G1 X32.569 Y13.507 E.39499
G1 X32.036 Y13.507
G1 X41.125 Y4.417 E.39499
G1 X40.592 Y4.417
G1 X31.502 Y13.507 E.39499
G1 X30.969 Y13.507
G1 X40.059 Y4.417 E.39499
G1 X39.525 Y4.417
G1 X30.436 Y13.507 E.39499
G1 X29.902 Y13.507
G1 X38.992 Y4.417 E.39499
; WIPE_START
M204 S10000
G1 X37.578 Y5.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.142 Y13.065 Z2.4 F30000
G1 X33.516 Y17.893 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X28.853 Y22.555 E.2026
G1 X28.32 Y22.555
G1 X32.982 Y17.893 E.2026
G1 X32.449 Y17.893
G1 X27.835 Y22.507 E.20051
G1 X27.302 Y22.507
G1 X31.916 Y17.893 E.20051
G1 X31.383 Y17.893
G1 X20.417 Y28.858 E.47649
G1 X20.417 Y28.325
G1 X30.849 Y17.893 E.45332
G1 X30.316 Y17.893
G1 X20.417 Y27.792 E.43015
G1 X20.417 Y27.258
G1 X29.783 Y17.893 E.40697
G1 X29.507 Y17.635
G1 X20.417 Y26.725 E.39499
G1 X20.417 Y26.192
G1 X29.507 Y17.102 E.39499
G1 X29.507 Y16.569
G1 X20.417 Y25.659 E.39499
G1 X20.417 Y25.125
G1 X29.507 Y16.036 E.39499
G1 X29.507 Y15.502
G1 X20.417 Y24.592 E.39499
G1 X20.417 Y24.059
G1 X29.507 Y14.969 E.39499
G1 X29.507 Y14.436
G1 X20.417 Y23.525 E.39499
G1 X20.417 Y22.992
G1 X29.507 Y13.902 E.39499
; WIPE_START
M204 S10000
G1 X28.093 Y15.317 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.505 Y20.516 Z2.4 F30000
G1 X20.417 Y22.459 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X38.459 Y4.417 E.78399
G1 X37.926 Y4.417
G1 X20.417 Y21.926 E.76082
G1 X20.417 Y21.392
G1 X37.392 Y4.417 E.73765
G1 X36.859 Y4.417
G1 X20.417 Y20.859 E.71448
G1 X20.417 Y20.326
G1 X36.326 Y4.417 E.6913
G1 X35.793 Y4.417
G1 X20.417 Y19.793 E.66813
G1 X20.417 Y19.259
G1 X35.259 Y4.417 E.64496
G1 X34.726 Y4.417
G1 X20.417 Y18.726 E.62179
G1 X20.417 Y18.193
G1 X34.193 Y4.417 E.59861
G1 X33.66 Y4.417
M73 P87 R4
G1 X20.417 Y17.66 E.57544
G1 X20.417 Y17.126
G1 X33.126 Y4.417 E.55227
G1 X32.593 Y4.417
G1 X20.417 Y16.593 E.5291
G1 X20.417 Y16.06
G1 X32.06 Y4.417 E.50592
G1 X31.527 Y4.417
G1 X20.417 Y15.527 E.48275
G1 X20.417 Y14.993
G1 X30.993 Y4.417 E.45958
G1 X30.46 Y4.417
G1 X20.417 Y14.46 E.43641
G1 X20.417 Y13.927
G1 X29.927 Y4.417 E.41323
G1 X29.394 Y4.417
G1 X20.417 Y13.394 E.39006
G1 X20.417 Y12.86
G1 X28.86 Y4.417 E.36689
G1 X28.327 Y4.417
G1 X20.417 Y12.327 E.34371
G1 X20.417 Y11.794
G1 X27.794 Y4.417 E.32054
G1 X27.261 Y4.417
G1 X20.417 Y11.261 E.29737
G1 X20.417 Y10.727
G1 X26.727 Y4.417 E.2742
G1 X26.194 Y4.417
G1 X20.417 Y10.194 E.25102
G1 X20.417 Y9.661
G1 X25.661 Y4.417 E.22785
G1 X25.128 Y4.417
G1 X20.417 Y9.128 E.20468
G1 X20.417 Y8.594
G1 X24.594 Y4.417 E.18151
G1 X24.061 Y4.417
G1 X20.417 Y8.061 E.15833
G1 X20.417 Y7.528
G1 X23.528 Y4.417 E.13516
G1 X22.995 Y4.417
G1 X20.417 Y6.995 E.11199
G1 X20.417 Y6.461
G1 X22.461 Y4.417 E.08882
G1 X21.928 Y4.417
G1 X20.417 Y5.928 E.06564
G1 X20.417 Y5.395
G1 X21.395 Y4.417 E.04247
G1 X20.861 Y4.417
G1 X20.417 Y4.861 E.0193
; WIPE_START
M204 S10000
G1 X20.861 Y4.417 E-.23865
G1 X21.395 Y4.417 E-.20264
G1 X20.802 Y5.01 E-.31871
; WIPE_END
G1 E-.04 F1800
G1 X21.946 Y12.557 Z2.4 F30000
G1 X30.191 Y66.937 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.154652
G1 F15000
G2 X29.937 Y67.191 I.155 J.409 E.00338
; WIPE_START
G1 X29.99 Y67.083 E-.24612
G1 X30.083 Y66.99 E-.26774
G1 X30.191 Y66.937 E-.24614
; WIPE_END
G1 E-.04 F1800
G1 X30.237 Y59.305 Z2.4 F30000
G1 X30.351 Y40.025 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.0956636
G1 F15000
G1 X29.968 Y40.409 E.00233
; WIPE_START
G1 X30.351 Y40.025 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.025 Y32.876 Z2.4 F30000
G1 X36.895 Y22.531 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.12039
G1 F15000
G2 X36.615 Y22.526 I-.166 J1.542 E.00177
; WIPE_START
G1 X36.895 Y22.531 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.14 Y29.866 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.113414
G1 F15000
G3 X34.649 Y29.87 I-.268 J-2.713 E.00283
; WIPE_START
G1 X35.14 Y29.866 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X37.53 Y29.23 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X37.53 Y23.17 E.18621
G1 X36.594 Y23.17 E.02876
G1 X36.594 Y28.306 E.1578
G1 X36.563 Y28.41 E.00335
G1 X36.406 Y28.494 E.00547
G1 X35.244 Y28.494 E.03569
G1 X35.244 Y29.23 E.02262
G1 X37.47 Y29.23 E.0684
G1 X35.612 Y28.862 F30000
; LINE_WIDTH: 0.40189
G1 F15000
G1 X36.406 Y28.862 E.02321
; LINE_WIDTH: 0.424725
G1 X36.491 Y28.839 E.00275
; LINE_WIDTH: 0.470413
G1 F14737.088
G1 X36.576 Y28.816 E.00307
; LINE_WIDTH: 0.516102
G1 F13314.132
G1 X36.661 Y28.794 E.0034
; LINE_WIDTH: 0.56179
G1 F12141.77
G1 X36.747 Y28.771 E.00373
; LINE_WIDTH: 0.607479
G1 F11159.162
G1 X36.832 Y28.748 E.00406
; LINE_WIDTH: 0.653167
G1 F10323.686
G1 X36.917 Y28.725 E.00439
; LINE_WIDTH: 0.698856
G1 F9604.6
G1 X37.002 Y28.702 E.00472
; LINE_WIDTH: 0.701734
G1 F9562.648
G1 X37.022 Y28.57 E.00718
; LINE_WIDTH: 0.6618
G1 F10179.68
G1 X37.042 Y28.438 E.00674
; LINE_WIDTH: 0.602463
G1 F11259.187
G1 X37.062 Y28.306 E.0061
G1 X37.062 Y23.698 E.21009
; WIPE_START
G1 X37.062 Y25.698 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.191 Y29.02 Z2.4 F30000
G1 X29.756 Y29.23 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.756 Y28.494 E.02262
G1 X28.594 Y28.494 E.03569
G1 X28.437 Y28.41 E.00547
G1 X28.406 Y28.306 E.00335
G1 X28.406 Y23.17 E.1578
G1 X27.47 Y23.17 E.02876
G1 X27.47 Y29.23 E.18621
G1 X29.696 Y29.23 E.0684
; WIPE_START
G1 X27.696 Y29.23 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X27.938 Y23.638 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.60188
G1 F11270.933
G1 X27.938 Y28.306 E.21261
; LINE_WIDTH: 0.621847
G1 F10882.207
G1 X27.958 Y28.438 E.00631
; LINE_WIDTH: 0.66178
G1 F10180.008
G1 X27.978 Y28.57 E.00674
; LINE_WIDTH: 0.701714
G1 F9562.939
G1 X27.998 Y28.702 E.00718
; LINE_WIDTH: 0.698837
G1 F9604.873
G1 X28.083 Y28.725 E.00472
; LINE_WIDTH: 0.653152
G1 F10323.952
G1 X28.168 Y28.748 E.00439
; LINE_WIDTH: 0.607466
G1 F11159.416
G1 X28.253 Y28.771 E.00406
; LINE_WIDTH: 0.56178
G1 F12142.005
G1 X28.339 Y28.794 E.00373
; LINE_WIDTH: 0.516095
G1 F13314.334
G1 X28.424 Y28.816 E.0034
; LINE_WIDTH: 0.470409
G1 F14737.236
G1 X28.509 Y28.839 E.00307
; LINE_WIDTH: 0.404342
G1 F15000
G1 X28.594 Y28.862 E.0026
G1 X29.328 Y28.862 E.0216
; WIPE_START
G1 X28.594 Y28.862 E-.67839
G1 X28.509 Y28.839 E-.08161
; WIPE_END
G1 E-.04 F1800
G1 X30.318 Y21.424 Z2.4 F30000
G1 X31.726 Y15.654 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.46376
G1 F14970.06
G2 X31.719 Y15.746 I-.026 J.044 E.00711
G1 X32.099 Y16.099 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X32.099 Y15.301 E.02452
G1 X31.301 Y15.301 E.02452
G1 X31.301 Y16.099 E.02452
G1 X32.039 Y16.099 E.02267
G1 X32.476 Y16.476 F30000
G1 F15000
G1 X32.476 Y14.924 E.04769
G1 X30.924 Y14.924 E.04769
G1 X30.924 Y16.476 E.04769
G1 X32.416 Y16.476 E.04585
G1 X32.853 Y16.853 F30000
G1 F15000
G1 X32.853 Y14.547 E.07086
G1 X30.547 Y14.547 E.07086
G1 X30.547 Y16.853 E.07086
G1 X32.793 Y16.853 E.06902
G1 X33.23 Y17.23 F30000
G1 F15000
G1 X33.23 Y14.17 E.09403
G1 X30.17 Y14.17 E.09403
G1 X30.17 Y17.23 E.09403
G1 X33.17 Y17.23 E.09219
; WIPE_START
G1 X31.17 Y17.23 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.506 Y24.855 Z2.4 F30000
G1 X33.389 Y67.595 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.293525
G1 F15000
G1 X33.08 Y67.618 E.00632
; LINE_WIDTH: 0.335108
G1 X32.933 Y67.636 E.00354
; LINE_WIDTH: 0.373625
G1 X32.768 Y67.657 E.00447
; LINE_WIDTH: 0.41147
G1 X32.568 Y67.692 E.0061
; LINE_WIDTH: 0.44493
G1 X32.368 Y67.727 E.00665
G1 X31.96 Y67.67 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X30.67 Y67.67 E.03965
G1 X30.67 Y68.96 E.03965
G1 X30.996 Y69.017 E.01018
G1 X31.243 Y68.659 E.01334
G1 X31.659 Y68.243 E.0181
G1 X32.017 Y67.996 E.01334
G1 X31.97 Y67.729 E.00834
G1 X31.161 Y68.069 F30000
; LINE_WIDTH: 0.58096
G1 F11709.167
G2 X31.165 Y68.179 I-.029 J.056 E.01154
G1 X30.727 Y69.368 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.444948
G1 F15000
G1 X30.692 Y69.568 E.00665
; LINE_WIDTH: 0.409951
G1 X30.655 Y69.785 E.00659
; LINE_WIDTH: 0.371458
G1 X30.636 Y69.933 E.00398
; LINE_WIDTH: 0.3335
G1 X30.617 Y70.094 E.00384
; LINE_WIDTH: 0.291737
G1 X30.595 Y70.4 E.00623
; LINE_WIDTH: 0.262452
G1 X30.595 Y71.011 E.01094
; LINE_WIDTH: 0.293545
G1 X30.618 Y71.32 E.00632
; LINE_WIDTH: 0.335122
G1 X30.636 Y71.467 E.00354
; LINE_WIDTH: 0.373629
G1 X30.657 Y71.632 E.00447
; LINE_WIDTH: 0.41147
G1 X30.692 Y71.832 E.0061
; LINE_WIDTH: 0.444944
G1 X30.727 Y72.032 E.00665
G1 X32.017 Y73.404 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X31.659 Y73.157 E.01334
G1 X31.243 Y72.741 E.0181
G1 X30.996 Y72.383 E.01334
G1 X30.67 Y72.44 E.01018
G1 X30.67 Y73.73 E.03965
G1 X31.96 Y73.73 E.03965
G1 X32.007 Y73.463 E.00834
G1 X31.161 Y73.214 F30000
; LINE_WIDTH: 0.58096
G1 F11709.167
G2 X31.165 Y73.325 I-.029 J.056 E.01154
G1 X32.368 Y73.673 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.444948
G1 F15000
G1 X32.568 Y73.708 E.00665
; LINE_WIDTH: 0.411476
G1 X32.768 Y73.743 E.0061
; LINE_WIDTH: 0.373632
G1 X32.933 Y73.764 E.00447
; LINE_WIDTH: 0.335113
G1 X33.08 Y73.782 E.00354
; LINE_WIDTH: 0.29355
G1 X33.389 Y73.805 E.00632
; LINE_WIDTH: 0.262452
G1 X34 Y73.805 E.01094
; LINE_WIDTH: 0.291732
G1 X34.307 Y73.783 E.00623
; LINE_WIDTH: 0.333508
G1 X34.467 Y73.764 E.00384
; LINE_WIDTH: 0.371454
G1 X34.615 Y73.745 E.00398
; LINE_WIDTH: 0.409947
G1 X34.832 Y73.708 E.00659
; LINE_WIDTH: 0.444944
G1 X35.032 Y73.673 E.00665
G1 X36.73 Y72.44 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X36.404 Y72.383 E.01018
G1 X36.157 Y72.741 E.01334
G1 X35.741 Y73.157 E.0181
G1 X35.383 Y73.404 E.01334
G1 X35.44 Y73.73 E.01018
G1 X36.73 Y73.73 E.03965
G1 X36.73 Y72.5 E.0378
G1 X36.306 Y73.214 F30000
; LINE_WIDTH: 0.58098
G1 F11708.731
G2 X36.31 Y73.325 I-.029 J.056 E.01154
G1 X36.673 Y72.032 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.44494
G1 F15000
G1 X36.708 Y71.832 E.00665
; LINE_WIDTH: 0.409949
G1 X36.745 Y71.615 E.00659
; LINE_WIDTH: 0.371458
G1 X36.764 Y71.467 E.00398
; LINE_WIDTH: 0.333501
G1 X36.783 Y71.307 E.00384
; LINE_WIDTH: 0.291728
G1 X36.805 Y71 E.00623
; LINE_WIDTH: 0.262432
G1 X36.805 Y70.389 E.01094
; LINE_WIDTH: 0.293535
G1 X36.782 Y70.08 E.00632
; LINE_WIDTH: 0.335122
G1 X36.764 Y69.933 E.00354
; LINE_WIDTH: 0.37363
G1 X36.743 Y69.768 E.00447
; LINE_WIDTH: 0.41147
G1 X36.708 Y69.568 E.0061
; LINE_WIDTH: 0.44493
G1 X36.673 Y69.368 E.00665
G1 X36.73 Y67.67 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X35.44 Y67.67 E.03965
G1 X35.383 Y67.996 E.01018
G1 X35.741 Y68.243 E.01334
G1 X36.157 Y68.659 E.01811
G1 X36.404 Y69.017 E.01334
G1 X36.73 Y68.96 E.01018
G1 X36.73 Y67.73 E.0378
G1 X36.306 Y68.069 F30000
; LINE_WIDTH: 0.581
G1 F11708.297
G2 X36.31 Y68.179 I-.029 J.056 E.01154
G1 X35.032 Y67.727 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.44494
G1 F15000
G1 X34.832 Y67.692 E.00665
; LINE_WIDTH: 0.409949
G1 X34.615 Y67.655 E.00659
; LINE_WIDTH: 0.371458
G1 X34.467 Y67.636 E.00398
; LINE_WIDTH: 0.333501
G1 X34.307 Y67.617 E.00384
; LINE_WIDTH: 0.291728
G1 X34 Y67.595 E.00623
; LINE_WIDTH: 0.262431
G1 X33.389 Y67.595 E.01094
; WIPE_START
G1 X34 Y67.595 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.073 Y70.464 Z2.4 F30000
G1 X63.726 Y79.654 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46376
G1 F14970.06
G2 X63.719 Y79.746 I-.026 J.044 E.00711
G1 X63.301 Y79.301 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X63.301 Y80.099 E.02452
G1 X64.099 Y80.099 E.02452
G1 X64.099 Y79.301 E.02452
G1 X63.361 Y79.301 E.02267
G1 X62.924 Y78.924 F30000
G1 F15000
G1 X62.924 Y80.476 E.04769
G1 X64.476 Y80.476 E.04769
G1 X64.476 Y78.924 E.04769
G1 X62.984 Y78.924 E.04585
G1 X62.547 Y78.547 F30000
G1 F15000
G1 X62.547 Y80.853 E.07086
G1 X64.853 Y80.853 E.07086
G1 X64.853 Y78.547 E.07086
G1 X62.607 Y78.547 E.06902
G1 X62.17 Y78.17 F30000
G1 F15000
G1 X62.17 Y81.23 E.09403
G1 X65.23 Y81.23 E.09403
G1 X65.23 Y78.17 E.09403
G1 X62.23 Y78.17 E.09219
; WIPE_START
G1 X64.23 Y78.17 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X71.691 Y76.564 Z2.4 F30000
G1 X84.481 Y73.812 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.25601
G1 F15000
G1 X92.919 Y73.812 E.14651
; WIPE_START
G1 X90.919 Y73.812 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X92.919 Y67.588 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.25602
G1 F15000
G1 X84.481 Y67.588 E.14651
; WIPE_START
G1 X86.481 Y67.588 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.153 Y59.985 Z2.4 F30000
G1 X89.87 Y29.23 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X92.156 Y29.23 E.07024
G1 X92.156 Y28.494 E.02262
G1 X90.994 Y28.494 E.03569
G1 X90.837 Y28.41 E.00547
G1 X90.806 Y28.306 E.00335
G1 X90.806 Y23.17 E.1578
G1 X89.87 Y23.17 E.02876
G1 X89.87 Y29.17 E.18437
G1 X90.338 Y23.638 F30000
; LINE_WIDTH: 0.60188
G1 F11270.933
G1 X90.338 Y28.306 E.21261
; LINE_WIDTH: 0.62185
G1 F10882.145
G1 X90.358 Y28.438 E.00631
; LINE_WIDTH: 0.66179
G1 F10179.845
G1 X90.378 Y28.57 E.00674
; LINE_WIDTH: 0.70173
G1 F9562.697
G1 X90.398 Y28.702 E.00718
; LINE_WIDTH: 0.698856
G1 F9604.6
G1 X90.483 Y28.725 E.00472
; LINE_WIDTH: 0.653167
G1 F10323.686
G1 X90.568 Y28.748 E.00439
; LINE_WIDTH: 0.607479
G1 F11159.162
G1 X90.653 Y28.771 E.00406
; LINE_WIDTH: 0.56179
G1 F12141.77
G1 X90.739 Y28.794 E.00373
; LINE_WIDTH: 0.516102
G1 F13314.132
G1 X90.824 Y28.816 E.0034
; LINE_WIDTH: 0.470413
G1 F14737.088
G1 X90.909 Y28.839 E.00307
; LINE_WIDTH: 0.404343
G1 F15000
G1 X90.994 Y28.862 E.0026
G1 X91.728 Y28.862 E.0216
; WIPE_START
G1 X90.994 Y28.862 E-.67838
G1 X90.909 Y28.839 E-.08162
; WIPE_END
G1 E-.04 F1800
G1 X97.644 Y29.23 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.41999
G1 F15000
G1 X99.93 Y29.23 E.07024
G1 X99.93 Y23.17 E.18621
G1 X98.994 Y23.17 E.02876
G1 X98.994 Y28.306 E.1578
G1 X98.963 Y28.41 E.00335
G1 X98.806 Y28.494 E.00547
G1 X97.644 Y28.494 E.03569
G1 X97.644 Y29.17 E.02077
G1 X98.012 Y28.862 F30000
; LINE_WIDTH: 0.40189
G1 F15000
G1 X98.806 Y28.862 E.02321
; LINE_WIDTH: 0.424725
G1 X98.891 Y28.839 E.00275
; LINE_WIDTH: 0.470413
G1 F14737.088
G1 X98.976 Y28.816 E.00307
; LINE_WIDTH: 0.516102
G1 F13314.132
G1 X99.061 Y28.794 E.0034
; LINE_WIDTH: 0.56179
G1 F12141.77
G1 X99.147 Y28.771 E.00373
; LINE_WIDTH: 0.607479
G1 F11159.162
G1 X99.232 Y28.748 E.00406
; LINE_WIDTH: 0.653167
G1 F10323.686
G1 X99.317 Y28.725 E.00439
; LINE_WIDTH: 0.698856
G1 F9604.6
G1 X99.402 Y28.702 E.00472
; LINE_WIDTH: 0.70173
G1 F9562.697
G1 X99.422 Y28.57 E.00718
; LINE_WIDTH: 0.66179
G1 F10179.845
G1 X99.442 Y28.438 E.00674
; LINE_WIDTH: 0.602444
G1 F11259.588
G1 X99.462 Y28.306 E.0061
G1 X99.462 Y23.698 E.21009
; WIPE_START
G1 X99.462 Y25.698 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X96.801 Y18.544 Z2.4 F30000
G1 X95.726 Y15.654 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.46376
G1 F14970.06
G2 X95.719 Y15.746 I-.026 J.044 E.00711
G1 X95.301 Y16.099 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X96.099 Y16.099 E.02452
G1 X96.099 Y15.301 E.02452
G1 X95.301 Y15.301 E.02452
G1 X95.301 Y16.039 E.02267
G1 X94.924 Y16.476 F30000
G1 F15000
G1 X96.476 Y16.476 E.04769
G1 X96.476 Y14.924 E.04769
G1 X94.924 Y14.924 E.04769
G1 X94.924 Y16.416 E.04585
G1 X94.547 Y16.853 F30000
G1 F15000
G1 X96.853 Y16.853 E.07086
G1 X96.853 Y14.547 E.07086
G1 X94.547 Y14.547 E.07086
G1 X94.547 Y16.793 E.06902
G1 X94.17 Y17.23 F30000
G1 F15000
G1 X97.23 Y17.23 E.09403
G1 X97.23 Y14.17 E.09403
G1 X94.17 Y14.17 E.09403
G1 X94.17 Y17.17 E.09219
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X94.17 Y15.17 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 11/40
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
G17
G3 Z2.4 I1.217 J0 P1  F30000
; object ids of layer 11 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer11 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z2.6 F30000
G1 X160.4 Y8 Z2.6
G1 Z2.2
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z2.6 F30000
G1 X114.002 Y8.498 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X125.811 Y8.218 Z2.6 F30000
G1 X34.098 Y18.098 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.302 Y18.098 E.15909
G1 X29.302 Y13.302 E.15909
G1 X34.098 Y13.302 E.15909
G1 X34.098 Y18.038 E.1571
G1 X34.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X28.91 Y18.49 E.17146
G1 X28.91 Y12.91 E.17146
G1 X34.49 Y12.91 E.17146
G1 X34.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X32.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.706 Y17.706 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X33.706 Y13.694 E.12327
G1 X29.694 Y13.694 E.12327
G1 X29.694 Y17.706 E.12327
G1 X33.646 Y17.706 E.12142
G1 X33.329 Y17.329 F30000
G1 F15000
G1 X33.329 Y14.071 E.10009
G1 X30.071 Y14.071 E.10009
G1 X30.071 Y17.329 E.10009
G1 X33.269 Y17.329 E.09825
G1 X32.952 Y16.952 F30000
G1 F15000
G1 X32.952 Y14.448 E.07692
G1 X30.448 Y14.448 E.07692
G1 X30.448 Y16.952 E.07692
G1 X32.892 Y16.952 E.07508
G1 X32.575 Y16.575 F30000
G1 F15000
G1 X32.575 Y14.825 E.05375
G1 X30.825 Y14.825 E.05375
G1 X30.825 Y16.575 E.05375
G1 X32.515 Y16.575 E.05191
G1 X32.198 Y16.198 F30000
G1 F15000
G1 X32.198 Y15.202 E.03058
G1 X31.202 Y15.202 E.03058
G1 X31.202 Y16.198 E.03058
G1 X32.138 Y16.198 E.02874
G1 X31.855 Y15.855 F30000
; LINE_WIDTH: 0.35198
G1 F15000
G1 X31.855 Y15.545 E.00778
G1 X31.545 Y15.545 E.00778
G1 X31.545 Y15.855 E.00778
G1 X31.795 Y15.855 E.00627
; WIPE_START
G1 X31.545 Y15.855 E-.16093
M73 P88 R4
G1 X31.545 Y15.545 E-.19969
G1 X31.855 Y15.545 E-.19969
G1 X31.855 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
G1 X35.041 Y22.79 Z2.6 F30000
G1 X38.398 Y30.098 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X34.852 Y30.098 E.11762
G1 X34.852 Y27.902 E.07284
G1 X36.002 Y27.902 E.03815
G1 X36.002 Y22.302 E.18576
G1 X38.398 Y22.302 E.07948
G1 X38.398 Y30.038 E.25661
; WIPE_START
G1 X36.398 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.148 Y30.098 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
G1 F15476.087
G1 X26.602 Y30.098 E.11762
G1 X26.602 Y22.302 E.2586
G1 X28.998 Y22.302 E.07948
G1 X28.998 Y27.902 E.18576
G1 X30.148 Y27.902 E.03815
G1 X30.148 Y30.038 E.07085
; WIPE_START
G1 X28.148 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.775 Y30.371 Z2.6 F30000
G1 X38.79 Y30.49 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X34.46 Y30.49 E.13305
G1 X34.46 Y28.469 E.0621
G1 X34.46 Y28.069 E.01229
G1 F9901.871
G1 X34.46 Y27.669 E.01229
G1 F3789.734
G1 X34.46 Y27.51 E.00489
G1 F2160
G1 X35.61 Y27.51 E.03534
G1 X35.61 Y22.831 E.14377
G1 F2536.674
G1 X35.61 Y22.79 E.00126
G1 F7799.139
G1 X35.21 Y22.79 E.01229
G1 F12000
G1 X34.81 Y22.79 E.01229
G1 X34.46 Y22.79 E.01075
G1 X34.46 Y22.49 E.00922
G1 X30.54 Y22.49 E.12045
G1 X30.54 Y22.79 E.00922
G1 X30.19 Y22.79 E.01075
G1 X29.79 Y22.79 E.01229
G1 F7799.139
G1 X29.39 Y22.79 E.01229
G1 F2536.674
G1 X29.39 Y22.831 E.00126
G1 F2160
G1 X29.39 Y27.51 E.14377
G1 X30.54 Y27.51 E.03534
G1 F3789.734
G1 X30.54 Y27.669 E.00489
G1 F9901.871
G1 X30.54 Y28.069 E.01229
G1 F12000
G1 X30.54 Y28.469 E.01229
M73 P88 R3
G1 X30.54 Y30.49 E.0621
G1 X26.21 Y30.49 E.13305
G1 X26.21 Y21.91 E.26364
G1 X38.79 Y21.91 E.38655
G1 X38.79 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X36.79 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X37.192 Y28.279 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.523736
G1 F13102.723
G1 X37.2 Y23.56 E.18488
G1 X37.262 Y28.962 F30000
; LINE_WIDTH: 0.422225
G1 F15000
G1 X37.239 Y28.734 E.00708
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X37.216 Y28.507 E.00795
; LINE_WIDTH: 0.515245
G1 F13338.273
G1 X37.192 Y28.279 E.00882
G1 X37.109 Y28.411 E.00601
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X37.026 Y28.543 E.00542
; LINE_WIDTH: 0.401484
G1 F15000
G1 X36.943 Y28.675 E.00456
G1 X36.468 Y28.962 E.01621
G1 X37.202 Y28.962 E.02144
G1 X37.629 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X37.629 Y23.071 E.19227
G1 X36.771 Y23.071 E.02635
G1 X36.771 Y28.106 E.15469
G1 X36.653 Y28.451 E.01122
; LINE_WIDTH: 0.444499
G1 X36.541 Y28.546 E.00481
; LINE_WIDTH: 0.493515
G1 F13981.513
G1 X36.428 Y28.641 E.00539
; LINE_WIDTH: 0.559989
G1 F12184.067
G1 X36.316 Y28.735 E.00619
G1 X35.691 Y28.741 E.02632
G1 X35.691 Y29.259 E.0218
G1 X36.206 Y29.259 E.02167
; LINE_WIDTH: 0.536874
G1 F12754.241
G1 X36.498 Y29.282 E.01183
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X36.791 Y29.305 E.01071
; LINE_WIDTH: 0.428814
G1 F15000
G2 X37.569 Y29.329 I.535 J-4.858 E.02448
G1 X38.006 Y29.706 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X38.006 Y22.694 E.21545
G1 X36.394 Y22.694 E.04952
G1 X36.394 Y28.106 E.16628
G1 X36.355 Y28.221 E.00374
G1 X36.206 Y28.294 E.00511
G1 X35.244 Y28.294 E.02954
G1 X35.244 Y29.706 E.04338
G1 X37.946 Y29.706 E.08302
; WIPE_START
G1 X35.946 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X34.656 Y22.35 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X35.806 Y22.35 E.04572
G1 X35.444 Y22.594 F30000
; LINE_WIDTH: 0.395308
G1 F15000
G1 X35.247 Y22.495 E.00632
; LINE_WIDTH: 0.348323
G1 X35.05 Y22.397 E.00548
; LINE_WIDTH: 0.301338
G1 X34.853 Y22.298 E.00464
; LINE_WIDTH: 0.232002
G1 X34.656 Y22.2 E.00339
G1 X30.344 Y22.2 E.06644
; LINE_WIDTH: 0.254353
G1 X30.147 Y22.298 E.00379
; LINE_WIDTH: 0.301338
G1 X29.95 Y22.397 E.00464
; LINE_WIDTH: 0.348323
G1 X29.753 Y22.495 E.00548
; LINE_WIDTH: 0.395308
G1 X29.556 Y22.594 E.00632
G1 X29.194 Y22.35 F30000
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X30.344 Y22.35 E.04572
; WIPE_START
G1 X29.194 Y22.35 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X27.8 Y23.5 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.523641
G1 F13105.322
G1 X27.805 Y28.219 E.18485
G1 X28.641 Y28.962 F30000
; LINE_WIDTH: 0.39895
G1 F15000
G1 X28.057 Y28.675 E.01888
; LINE_WIDTH: 0.422212
G1 X27.974 Y28.543 E.00483
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X27.891 Y28.411 E.00542
; LINE_WIDTH: 0.515259
G1 F13337.898
G1 X27.808 Y28.279 E.00601
G1 X27.784 Y28.447 E.00655
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X27.761 Y28.616 E.0059
; LINE_WIDTH: 0.402272
G1 F15000
G2 X27.738 Y28.962 I1.243 J.258 E.0102
G1 X28.581 Y28.962 E.02468
G1 X29.309 Y29.259 F30000
; LINE_WIDTH: 0.560258
G1 F12177.737
G1 X29.309 Y28.741 E.02181
G1 X28.794 Y28.741 E.02168
; LINE_WIDTH: 0.536874
G1 F12754.241
G1 X28.645 Y28.645 E.00716
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X28.496 Y28.548 E.00648
; LINE_WIDTH: 0.420304
G1 F15000
G1 X28.347 Y28.451 E.00547
G1 X28.229 Y28.106 E.01123
G1 X28.229 Y23.071 E.15482
G1 X27.371 Y23.071 E.02637
G1 X27.371 Y29.329 E.19243
G1 X27.916 Y29.329 E.01675
; LINE_WIDTH: 0.443367
G1 X28.209 Y29.305 E.00959
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X28.502 Y29.282 E.01071
; LINE_WIDTH: 0.551072
G1 F12397.869
G3 X29.249 Y29.259 I.52 J4.668 E.03099
G1 X29.756 Y29.706 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.756 Y28.294 E.04338
G1 X28.794 Y28.294 E.02954
G1 X28.645 Y28.221 E.00511
G1 X28.606 Y28.106 E.00374
G1 X28.606 Y22.694 E.16628
G1 X26.994 Y22.694 E.04952
G1 X26.994 Y29.706 E.21545
G1 X29.696 Y29.706 E.08302
; WIPE_START
G1 X27.696 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.712 Y37.27 Z2.6 F30000
G1 X33.579 Y73.497 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.486 E.00509
G3 X33.425 Y67.911 I.274 J-2.788 E.27367
G1 X33.7 Y67.897 E.00912
G3 X33.7 Y73.499 I0 J2.801 E.29191
G1 X33.639 Y73.498 E.00204
G1 X33.598 Y73.1 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.23 Y73.061 E.01137
G3 X33.464 Y68.301 I.47 J-2.363 E.21072
G1 X33.7 Y68.29 E.00727
G3 X33.7 Y73.107 I0 J2.409 E.23253
G1 X33.658 Y73.104 E.00129
; WIPE_START
M204 S10000
G1 X33.23 Y73.061 E-.16335
G1 X32.778 Y72.927 E-.17942
G1 X32.361 Y72.704 E-.17956
G1 X31.996 Y72.404 E-.17954
G1 X31.899 Y72.286 E-.05813
; WIPE_END
G1 E-.04 F1800
G1 X37.598 Y74.598 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.802 Y74.598 E.2586
G1 X29.802 Y66.802 E.2586
G1 X37.598 Y66.802 E.2586
G1 X37.598 Y74.538 E.25661
G1 X37.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X29.41 Y74.99 E.26364
G1 X29.41 Y66.41 E.26364
G1 X37.99 Y66.41 E.26364
G1 X37.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X35.99 Y74.944 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.551 Y68.736 Z2.6 F30000
G1 X30.945 Y67.889 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y67.924 E.00191
G1 X30.929 Y67.951 E.00141
G1 X32.006 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X30.571 Y67.571 E.0441
G1 X30.571 Y69.006 E.0441
G1 X30.763 Y68.671 E.01188
G1 X31.137 Y68.215 E.01811
G1 X31.671 Y67.763 E.0215
G1 X31.954 Y67.601 E.01004
G1 X37.206 Y67.194 F30000
; LINE_WIDTH: 0.416411
G1 F15000
G2 X32.413 Y67.194 I-2.396 J295.898 E.14586
G1 X30.194 Y67.194 E.06754
G2 X30.194 Y71.987 I296.236 J2.396 E.14586
G1 X30.194 Y74.206 E.06754
G2 X34.987 Y74.206 I2.396 J-296.118 E.14586
G1 X37.206 Y74.206 E.06754
G2 X37.206 Y69.413 I-308.81 J-2.396 E.14586
G1 X37.206 Y67.254 E.06572
G1 X36.829 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X35.394 Y67.571 E.0441
G1 X35.729 Y67.763 E.01188
G1 X36.185 Y68.137 E.01811
G1 X36.637 Y68.671 E.0215
G1 X36.829 Y69.006 E.01188
G1 X36.829 Y67.631 E.04226
G1 X36.496 Y67.889 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y67.924 E.00191
G1 X36.48 Y67.951 E.00141
G1 X36.346 Y68.91 F30000
; LINE_WIDTH: 0.41532
G1 F15000
G1 X36.644 Y69.461 E.019
G1 X36.828 Y70.059 E.019
G3 X36.835 Y71.305 I-4.117 J.645 E.03795
G1 X36.658 Y71.905 E.01899
G1 X36.366 Y72.459 E.019
G1 X35.972 Y72.946 E.019
G1 X35.49 Y73.346 E.019
G1 X34.939 Y73.644 E.019
G1 X34.341 Y73.829 E.019
G3 X33.095 Y73.835 I-.643 J-4.15 E.03795
G1 X32.495 Y73.658 E.01899
G1 X31.941 Y73.366 E.019
G1 X31.454 Y72.972 E.019
G1 X31.054 Y72.49 E.019
G1 X30.756 Y71.939 E.019
G1 X30.571 Y71.341 E.019
G3 X30.565 Y70.095 I4.15 J-.643 E.03795
G1 X30.742 Y69.495 E.01899
G1 X31.034 Y68.941 E.019
G1 X31.428 Y68.454 E.019
G1 X31.91 Y68.054 E.019
G1 X32.461 Y67.756 E.019
G1 X33.059 Y67.571 E.019
G3 X34.305 Y67.565 I.643 J4.15 E.03795
G1 X34.905 Y67.742 E.01899
G1 X35.459 Y68.034 E.019
G1 X35.946 Y68.428 E.019
G1 X36.307 Y68.864 E.01718
G1 X36.829 Y72.394 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X36.637 Y72.729 E.01188
G1 X36.263 Y73.185 E.01811
G1 X35.729 Y73.637 E.0215
G1 X35.394 Y73.829 E.01188
G1 X36.829 Y73.829 E.0441
G1 X36.829 Y72.454 E.04226
G1 X36.496 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y73.476 E.00191
G1 X36.48 Y73.502 E.00141
G1 X32.006 Y73.829 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X31.671 Y73.637 E.01188
G1 X31.215 Y73.263 E.01811
G1 X30.763 Y72.729 E.0215
G1 X30.571 Y72.394 E.01188
G1 X30.571 Y73.829 E.0441
G1 X31.946 Y73.829 E.04226
G1 X30.945 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y73.476 E.00191
G1 X30.929 Y73.502 E.00141
; WIPE_START
G1 X30.883 Y73.476 E-.32216
G1 X30.945 Y73.44 E-.43784
; WIPE_END
G1 E-.04 F1800
G1 X38.356 Y75.265 Z2.6 F30000
G1 X66.098 Y82.098 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X61.302 Y82.098 E.15909
G1 X61.302 Y77.302 E.15909
G1 X66.098 Y77.302 E.15909
G1 X66.098 Y82.038 E.1571
G1 X66.49 Y82.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X60.91 Y82.49 E.17146
G1 X60.91 Y76.91 E.17146
G1 X66.49 Y76.91 E.17146
G1 X66.49 Y82.43 E.16961
; WIPE_START
M204 S10000
G1 X64.49 Y82.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X63.855 Y79.545 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.35197
G1 F15000
G1 X63.545 Y79.545 E.00778
G1 X63.545 Y79.855 E.00778
G1 X63.855 Y79.855 E.00778
G1 X63.855 Y79.605 E.00627
G1 X64.198 Y79.202 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X63.202 Y79.202 E.03058
G1 X63.202 Y80.198 E.03058
G1 X64.198 Y80.198 E.03058
G1 X64.198 Y79.262 E.02873
G1 X64.575 Y78.825 F30000
G1 F15000
G1 X62.825 Y78.825 E.05375
G1 X62.825 Y80.575 E.05375
G1 X64.575 Y80.575 E.05375
G1 X64.575 Y78.885 E.05191
G1 X64.952 Y78.448 F30000
G1 F15000
G1 X62.448 Y78.448 E.07692
G1 X62.448 Y80.952 E.07692
G1 X64.952 Y80.952 E.07692
G1 X64.952 Y78.508 E.07508
G1 X65.329 Y78.071 F30000
G1 F15000
G1 X62.071 Y78.071 E.10009
G1 X62.071 Y81.329 E.10009
G1 X65.329 Y81.329 E.10009
G1 X65.329 Y78.131 E.09825
G1 X65.706 Y77.694 F30000
G1 F15000
G1 X61.694 Y77.694 E.12327
G1 X61.694 Y81.706 E.12327
G1 X65.706 Y81.706 E.12327
G1 X65.706 Y77.754 E.12142
; WIPE_START
G1 X65.706 Y79.754 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X73.123 Y77.956 Z2.6 F30000
G1 X93.11 Y73.11 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y67.898 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X83.802 Y67.898 E.30876
G1 X83.802 Y66.802 E.03635
G1 X93.598 Y66.802 E.32495
G1 X93.598 Y67.898 E.03635
G1 X93.17 Y67.898 E.0142
; WIPE_START
G1 X91.17 Y67.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.598 Y74.598 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
G1 F15476.087
G1 X83.802 Y74.598 E.32495
G1 X83.802 Y73.502 E.03635
G1 X93.598 Y73.502 E.32495
G1 X93.598 Y74.538 E.03436
G1 X93.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X83.41 Y74.99 E.32509
G1 X83.41 Y66.41 E.26364
G1 X93.99 Y66.41 E.32509
G1 X93.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X91.99 Y74.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.55 Y73.306 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X93.55 Y68.094 E.20723
; WIPE_START
G1 X93.55 Y70.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.262 Y67.826 Z2.6 F30000
G1 X84.178 Y67.178 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y67.522 E.00967
G1 X93.222 Y67.522 E.25382
G1 X93.222 Y67.178 E.00967
G1 X84.238 Y67.178 E.25214
G1 X83.85 Y68.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X83.85 Y73.306 E.20723
G1 X84.178 Y73.878 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y74.222 E.00967
G1 X93.222 Y74.222 E.25382
G1 X93.222 Y73.878 E.00967
G1 X84.238 Y73.878 E.25214
; WIPE_START
G1 X86.238 Y73.878 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.327 Y66.323 Z2.6 F30000
G1 X92.548 Y30.098 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X89.002 Y30.098 E.11762
G1 X89.002 Y22.302 E.2586
G1 X91.398 Y22.302 E.07948
G1 X91.398 Y27.902 E.18576
G1 X92.548 Y27.902 E.03815
G1 X92.548 Y30.038 E.07085
; WIPE_START
G1 X90.548 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.181 Y30.091 Z2.6 F30000
G1 X100.798 Y30.098 Z2.6
G1 Z2.2
G1 E.8 F1800
G1 F15476.087
G1 X97.252 Y30.098 E.11762
G1 X97.252 Y27.902 E.07284
G1 X98.402 Y27.902 E.03815
G1 X98.402 Y22.302 E.18576
G1 X100.798 Y22.302 E.07948
G1 X100.798 Y30.038 E.25661
G1 X101.19 Y30.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X96.86 Y30.49 E.13305
G1 X96.86 Y28.469 E.0621
G1 X96.86 Y28.069 E.01229
G1 F9901.871
G1 X96.86 Y27.669 E.01229
G1 F3789.734
G1 X96.86 Y27.51 E.00489
G1 F2160
G1 X98.01 Y27.51 E.03534
G1 X98.01 Y22.831 E.14377
G1 F2536.674
G1 X98.01 Y22.79 E.00126
G1 F7799.139
G1 X97.61 Y22.79 E.01229
G1 F12000
G1 X97.21 Y22.79 E.01229
G1 X96.86 Y22.79 E.01075
G1 X96.86 Y22.49 E.00922
G1 X92.94 Y22.49 E.12045
G1 X92.94 Y22.79 E.00922
G1 X92.59 Y22.79 E.01075
G1 X92.19 Y22.79 E.01229
G1 F7799.139
G1 X91.79 Y22.79 E.01229
G1 F2536.674
G1 X91.79 Y22.831 E.00126
G1 F2160
G1 X91.79 Y27.51 E.14377
G1 X92.94 Y27.51 E.03534
G1 F3789.734
G1 X92.94 Y27.669 E.00489
G1 F9901.871
G1 X92.94 Y28.069 E.01229
G1 F12000
G1 X92.94 Y28.469 E.01229
G1 X92.94 Y30.49 E.0621
G1 X88.61 Y30.49 E.13305
G1 X88.61 Y21.91 E.26364
G1 X101.19 Y21.91 E.38655
G1 X101.19 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X99.19 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.592 Y28.279 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.523717
G1 F13103.257
G1 X99.6 Y23.56 E.18487
G1 X98.868 Y28.962 F30000
; LINE_WIDTH: 0.39897
G1 F15000
G1 X99.662 Y28.962 E.02303
; LINE_WIDTH: 0.422225
G1 X99.639 Y28.734 E.00708
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X99.616 Y28.507 E.00795
; LINE_WIDTH: 0.515245
G1 F13338.273
G1 X99.592 Y28.279 E.00882
G1 X99.509 Y28.411 E.00601
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X99.426 Y28.543 E.00542
; LINE_WIDTH: 0.404549
G1 F15000
G1 X99.343 Y28.675 E.0046
G1 X98.92 Y28.931 E.01458
G1 X98.091 Y29.259 F30000
; LINE_WIDTH: 0.560255
G1 F12177.796
G1 X98.606 Y29.259 E.02168
; LINE_WIDTH: 0.536874
G1 F12754.241
G1 X98.898 Y29.282 E.01183
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X99.191 Y29.305 E.01071
; LINE_WIDTH: 0.420505
G1 F15000
G2 X100.029 Y29.329 I.565 J-5.234 E.0258
G1 X100.029 Y23.071 E.19254
G1 X99.171 Y23.071 E.02639
G1 X99.171 Y28.106 E.1549
G1 X99.053 Y28.451 E.01124
; LINE_WIDTH: 0.444499
G1 X98.941 Y28.546 E.00481
; LINE_WIDTH: 0.493515
G1 F13981.513
G1 X98.828 Y28.641 E.00539
; LINE_WIDTH: 0.559864
G1 F12187.006
G1 X98.716 Y28.735 E.00619
G1 X98.091 Y28.741 E.02632
G1 X98.091 Y29.199 E.01926
G1 X97.644 Y29.706 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X100.406 Y29.706 E.08486
G1 X100.406 Y22.694 E.21545
G1 X98.794 Y22.694 E.04952
G1 X98.794 Y28.106 E.16628
G1 X98.755 Y28.221 E.00374
G1 X98.606 Y28.294 E.00511
G1 X97.644 Y28.294 E.02954
G1 X97.644 Y29.646 E.04153
; WIPE_START
G1 X97.644 Y28.294 E-.51367
G1 X98.292 Y28.294 E-.24634
; WIPE_END
G1 E-.04 F1800
G1 X97.056 Y22.35 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X98.206 Y22.35 E.04572
G1 X97.844 Y22.594 F30000
; LINE_WIDTH: 0.395308
G1 F15000
G1 X97.647 Y22.495 E.00632
; LINE_WIDTH: 0.348323
G1 X97.45 Y22.397 E.00548
; LINE_WIDTH: 0.301338
G1 X97.253 Y22.298 E.00464
; LINE_WIDTH: 0.232002
G1 X97.056 Y22.2 E.00339
G1 X92.744 Y22.2 E.06644
; LINE_WIDTH: 0.254353
G1 X92.547 Y22.298 E.00379
; LINE_WIDTH: 0.301338
G1 X92.35 Y22.397 E.00464
; LINE_WIDTH: 0.348323
G1 X92.153 Y22.495 E.00548
; LINE_WIDTH: 0.395308
G1 X91.956 Y22.594 E.00632
G1 X91.594 Y22.35 F30000
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X92.744 Y22.35 E.04572
; WIPE_START
G1 X91.594 Y22.35 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X90.2 Y23.5 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.523621
G1 F13105.859
G1 X90.205 Y28.219 E.18484
G1 X90.138 Y28.962 F30000
; LINE_WIDTH: 0.39895
G1 F15000
G1 X91.041 Y28.962 E.0262
G1 X90.457 Y28.675 E.01888
; LINE_WIDTH: 0.422212
G1 X90.374 Y28.543 E.00483
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X90.291 Y28.411 E.00542
; LINE_WIDTH: 0.515259
G1 F13337.898
G1 X90.208 Y28.279 E.00601
G1 X90.184 Y28.447 E.00655
; LINE_WIDTH: 0.468735
G1 F14795.158
G1 X90.161 Y28.616 E.0059
; LINE_WIDTH: 0.412683
G1 F15000
G2 X90.138 Y28.902 I1.027 J.228 E.00869
G1 X89.771 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X90.316 Y29.329 E.01673
; LINE_WIDTH: 0.443367
G1 X90.609 Y29.305 E.00959
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X90.902 Y29.282 E.01071
; LINE_WIDTH: 0.556517
G1 F12266.438
G3 X91.709 Y29.259 I.55 J5.044 E.03383
G1 X91.709 Y28.741 E.02165
G1 X91.194 Y28.741 E.02152
; LINE_WIDTH: 0.536874
G1 F12754.241
G1 X91.045 Y28.645 E.00716
; LINE_WIDTH: 0.49012
G1 F14087.657
G1 X90.896 Y28.548 E.00648
; LINE_WIDTH: 0.420319
G1 F15000
G1 X90.747 Y28.451 E.00547
G1 X90.629 Y28.106 E.01123
G1 X90.629 Y23.071 E.15482
G1 X89.771 Y23.071 E.02637
G1 X89.771 Y29.269 E.1906
G1 X89.394 Y29.706 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X92.156 Y29.706 E.08486
G1 X92.156 Y28.294 E.04338
G1 X91.194 Y28.294 E.02954
G1 X91.045 Y28.221 E.00511
G1 X91.006 Y28.106 E.00374
G1 X91.006 Y22.694 E.16627
G1 X89.394 Y22.694 E.04952
G1 X89.394 Y29.646 E.2136
; WIPE_START
G1 X89.394 Y27.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.536 Y22.005 Z2.6 F30000
G1 X98.098 Y18.098 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.302 Y18.098 E.15909
G1 X93.302 Y13.302 E.15909
G1 X98.098 Y13.302 E.15909
G1 X98.098 Y18.038 E.1571
G1 X98.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.91 Y18.49 E.17146
G1 X92.91 Y12.91 E.17146
G1 X98.49 Y12.91 E.17146
G1 X98.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X96.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.694 Y17.706 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X97.706 Y17.706 E.12327
G1 X97.706 Y13.694 E.12327
G1 X93.694 Y13.694 E.12327
G1 X93.694 Y17.646 E.12142
G1 X94.071 Y17.329 F30000
G1 F15000
G1 X97.329 Y17.329 E.10009
G1 X97.329 Y14.071 E.10009
G1 X94.071 Y14.071 E.10009
G1 X94.071 Y17.269 E.09825
G1 X94.448 Y16.952 F30000
G1 F15000
G1 X96.952 Y16.952 E.07692
G1 X96.952 Y14.448 E.07692
G1 X94.448 Y14.448 E.07692
G1 X94.448 Y16.892 E.07508
G1 X94.825 Y16.575 F30000
G1 F15000
G1 X96.575 Y16.575 E.05375
G1 X96.575 Y14.825 E.05375
G1 X94.825 Y14.825 E.05375
G1 X94.825 Y16.515 E.05191
G1 X95.202 Y16.198 F30000
G1 F15000
G1 X96.198 Y16.198 E.03058
G1 X96.198 Y15.202 E.03058
G1 X95.202 Y15.202 E.03058
G1 X95.202 Y16.138 E.02873
G1 X95.545 Y15.855 F30000
; LINE_WIDTH: 0.35197
G1 F15000
G1 X95.855 Y15.855 E.00778
G1 X95.855 Y15.545 E.00778
G1 X95.545 Y15.545 E.00778
G1 X95.545 Y15.795 E.00627
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X95.545 Y15.545 E-.16092
G1 X95.855 Y15.545 E-.19969
G1 X95.855 Y15.855 E-.19969
G1 X95.545 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 12/40
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
G17
G3 Z2.6 I1.217 J0 P1  F30000
; object ids of layer 12 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer12 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y8.398 E.03304
G1 X160.002 Y8.398 E.0264
G1 X160.002 Y7.798 E.0199
G1 X142.798 Y7.798 E.57069
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.79 E.0547
G1 X159.61 Y8.79 E.04855
G1 X159.61 Y8.19 E.01844
G1 X143.19 Y8.19 E.50454
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
G1 X149.689 Y7.766 Z2.8 F30000
G1 X160.4 Y8 Z2.8
G1 Z2.4
G1 E.8 F1800
; LINE_WIDTH: 0.43172
G1 F15000
G1 X160.4 Y7.86 E.00444
; OBJECT_ID: 12
; WIPE_START
G1 X160.4 Y8 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X152.768 Y8.082 Z2.8 F30000
G1 X114.002 Y8.498 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.002 Y7.402 E.57069
G1 X133.002 Y6.802 E.0199
G1 X133.798 Y6.802 E.0264
G1 X133.798 Y7.798 E.03304
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X132.61 Y7.01 E.50454
G1 X132.61 Y6.41 E.01844
G1 X134.19 Y6.41 E.04855
G1 X134.19 Y8.19 E.0547
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
G1 X133.4 Y7.4 F30000
; LINE_WIDTH: 0.43172
G1 F15000
G1 X133.4 Y7.26 E.00444
; OBJECT_ID: 8
; WIPE_START
G1 X133.4 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X125.811 Y8.218 Z2.8 F30000
G1 X34.098 Y18.098 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.302 Y18.098 E.15909
G1 X29.302 Y13.302 E.15909
G1 X34.098 Y13.302 E.15909
G1 X34.098 Y18.038 E.1571
G1 X34.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X28.91 Y18.49 E.17146
G1 X28.91 Y12.91 E.17146
G1 X34.49 Y12.91 E.17146
G1 X34.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X32.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.706 Y17.706 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X33.706 Y13.694 E.12327
G1 X29.694 Y13.694 E.12327
G1 X29.694 Y17.706 E.12327
G1 X33.646 Y17.706 E.12142
G1 X33.329 Y17.329 F30000
G1 F15000
G1 X33.329 Y14.071 E.10009
G1 X30.071 Y14.071 E.10009
G1 X30.071 Y17.329 E.10009
G1 X33.269 Y17.329 E.09825
G1 X32.952 Y16.952 F30000
G1 F15000
G1 X32.952 Y14.448 E.07692
G1 X30.448 Y14.448 E.07692
G1 X30.448 Y16.952 E.07692
G1 X32.892 Y16.952 E.07508
G1 X32.575 Y16.575 F30000
G1 F15000
G1 X32.575 Y14.825 E.05375
G1 X30.825 Y14.825 E.05375
G1 X30.825 Y16.575 E.05375
G1 X32.515 Y16.575 E.05191
G1 X32.198 Y16.198 F30000
G1 F15000
G1 X32.198 Y15.202 E.03058
G1 X31.202 Y15.202 E.03058
G1 X31.202 Y16.198 E.03058
G1 X32.138 Y16.198 E.02874
G1 X31.855 Y15.855 F30000
; LINE_WIDTH: 0.35198
G1 F15000
G1 X31.855 Y15.545 E.00778
G1 X31.545 Y15.545 E.00778
G1 X31.545 Y15.855 E.00778
G1 X31.795 Y15.855 E.00627
; WIPE_START
G1 X31.545 Y15.855 E-.16093
G1 X31.545 Y15.545 E-.19969
G1 X31.855 Y15.545 E-.19969
G1 X31.855 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
G1 X35.041 Y22.79 Z2.8 F30000
G1 X38.398 Y30.098 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X34.852 Y30.098 E.11762
G1 X34.852 Y27.702 E.07948
G1 X35.802 Y27.702 E.03151
G1 X35.802 Y22.302 E.17913
G1 X38.398 Y22.302 E.08611
G1 X38.398 Y30.038 E.25661
; WIPE_START
G1 X36.398 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.148 Y30.098 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
G1 F15476.087
G1 X26.602 Y30.098 E.11762
G1 X26.602 Y22.302 E.2586
G1 X29.198 Y22.302 E.08611
G1 X29.198 Y27.702 E.17913
G1 X30.148 Y27.702 E.03151
G1 X30.148 Y30.038 E.07749
; WIPE_START
G1 X28.148 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.775 Y30.371 Z2.8 F30000
G1 X38.79 Y30.49 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X34.46 Y30.49 E.13305
G1 X34.46 Y28.269 E.06825
G1 X34.46 Y27.869 E.01229
G1 F9901.871
G1 X34.46 Y27.469 E.01229
G1 F3789.734
G1 X34.46 Y27.31 E.00489
G1 F2160
M73 P89 R3
G1 X35.41 Y27.31 E.02919
G1 X35.41 Y22.831 E.13763
G1 F2536.674
G1 X35.41 Y22.79 E.00126
G1 F7799.139
G1 X35.01 Y22.79 E.01229
G1 F12000
G1 X34.46 Y22.79 E.0169
G1 X34.46 Y22.49 E.00922
G1 X30.54 Y22.49 E.12045
G1 X30.54 Y22.79 E.00922
G1 X29.99 Y22.79 E.0169
G1 F7799.139
G1 X29.59 Y22.79 E.01229
G1 F2536.674
G1 X29.59 Y22.831 E.00126
G1 F2160
G1 X29.59 Y27.31 E.13763
G1 X30.54 Y27.31 E.02919
G1 F3789.734
G1 X30.54 Y27.469 E.00489
G1 F9901.871
G1 X30.54 Y27.869 E.01229
G1 F12000
G1 X30.54 Y28.269 E.01229
G1 X30.54 Y30.49 E.06825
G1 X26.21 Y30.49 E.13305
G1 X26.21 Y21.91 E.26364
G1 X38.79 Y21.91 E.38655
G1 X38.79 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X36.79 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.051 Y28.899 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.53149
G1 F12894.776
G1 X36.119 Y28.896 E.00272
G1 X37.204 Y28.904 F30000
; LINE_WIDTH: 0.495045
G1 F13934.2
G1 X37.225 Y28.635 E.00995
; LINE_WIDTH: 0.453615
G1 F15000
G1 X37.245 Y28.365 E.00904
; LINE_WIDTH: 0.384127
G2 X37.27 Y27.906 I-4.16 J-.455 E.01281
G1 X37.27 Y23.43 E.12444
G1 X36.93 Y23.43 E.00946
G1 X36.92 Y28.066 E.1289
; LINE_WIDTH: 0.412185
G1 X36.874 Y28.218 E.00477
; LINE_WIDTH: 0.453615
G1 X36.828 Y28.369 E.0053
; LINE_WIDTH: 0.495045
G1 F13934.2
G1 X36.782 Y28.521 E.00583
; LINE_WIDTH: 0.525941
G1 F13042.922
G1 X36.179 Y28.892 E.0279
G2 X37.144 Y28.904 I.877 J-33.44 E.03799
G1 X37.629 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X37.629 Y23.071 E.19227
G1 X36.571 Y23.071 E.0325
G1 X36.571 Y27.906 E.14854
G1 X36.449 Y28.257 E.01143
G1 X36.103 Y28.463 E.01236
G1 X35.621 Y28.471 E.01482
G1 X35.621 Y29.329 E.02635
G1 X37.569 Y29.329 E.05984
G1 X38.006 Y29.706 F30000
G1 F15000
G1 X38.006 Y22.694 E.21545
G1 X36.194 Y22.694 E.05567
G1 X36.194 Y27.906 E.16013
G1 X36.153 Y28.023 E.00381
G1 X36.006 Y28.094 E.00504
G1 X35.244 Y28.094 E.0234
G1 X35.244 Y29.706 E.04952
G1 X37.946 Y29.706 E.08302
; WIPE_START
G1 X35.946 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.444 Y22.594 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X35.247 Y22.495 E.00632
; LINE_WIDTH: 0.348323
G1 X35.05 Y22.397 E.00548
; LINE_WIDTH: 0.301338
G1 X34.853 Y22.298 E.00464
; LINE_WIDTH: 0.232002
G1 X34.656 Y22.2 E.00339
G1 X30.344 Y22.2 E.06644
; LINE_WIDTH: 0.254353
G1 X30.147 Y22.298 E.00379
; LINE_WIDTH: 0.301338
G1 X29.95 Y22.397 E.00464
; LINE_WIDTH: 0.348323
G1 X29.753 Y22.495 E.00548
; LINE_WIDTH: 0.395308
G1 X29.556 Y22.594 E.00632
; WIPE_START
G1 X29.753 Y22.495 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.949 Y28.899 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51576
G1 F13323.746
G1 X28.218 Y28.521 E.03174
; LINE_WIDTH: 0.495047
G1 F13934.148
G1 X28.172 Y28.369 E.00583
; LINE_WIDTH: 0.45362
G1 F15000
G1 X28.126 Y28.218 E.0053
; LINE_WIDTH: 0.383738
G3 X28.07 Y27.906 I.628 J-.273 E.00888
G1 X28.07 Y23.43 E.1243
G1 X27.73 Y23.43 E.00945
G1 X27.73 Y27.906 E.1243
; LINE_WIDTH: 0.405285
G1 X27.752 Y28.16 E.00753
; LINE_WIDTH: 0.449475
G1 X27.774 Y28.413 E.00844
; LINE_WIDTH: 0.512206
G1 F13424.648
G3 X27.796 Y28.904 I-2.808 J.372 E.01879
G1 X28.89 Y28.9 E.04181
G1 X29.379 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.379 Y28.471 E.02635
G1 X28.969 Y28.471 E.0126
G1 X28.551 Y28.257 E.01442
G1 X28.429 Y27.906 E.01143
G1 X28.429 Y23.071 E.14854
G1 X27.371 Y23.071 E.0325
G1 X27.371 Y29.329 E.19227
G1 X29.319 Y29.329 E.05984
G1 X29.756 Y29.706 F30000
G1 F15000
G1 X29.756 Y28.094 E.04952
G1 X28.994 Y28.094 E.0234
G1 X28.847 Y28.023 E.00504
G1 X28.806 Y27.906 E.00381
G1 X28.806 Y22.694 E.16013
G1 X26.994 Y22.694 E.05567
G1 X26.994 Y29.706 E.21545
G1 X29.696 Y29.706 E.08302
; WIPE_START
G1 X27.696 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.708 Y37.271 Z2.8 F30000
G1 X33.554 Y73.496 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.486 E.00428
G3 X33.62 Y67.901 I.283 J-2.786 E.27949
G3 X34.514 Y68.018 I.098 J2.731 E.03003
G3 X33.7 Y73.501 I-.805 J2.682 E.26506
G1 X33.614 Y73.498 E.00284
G1 X33.574 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.097 E.00338
G3 X33.639 Y68.293 I.246 J-2.396 E.22279
G3 X34.17 Y68.336 I.047 J2.7 E.01639
G3 X33.936 Y73.099 I-.46 J2.364 E.21133
G1 X33.634 Y73.099 E.00928
; WIPE_START
M204 S10000
G1 X33.464 Y73.097 E-.06461
G1 X33 Y73.007 E-.17948
G1 X32.564 Y72.826 E-.1796
G1 X32.171 Y72.563 E-.17956
G1 X31.879 Y72.271 E-.15675
; WIPE_END
G1 E-.04 F1800
G1 X37.598 Y74.598 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.802 Y74.598 E.2586
G1 X29.802 Y66.802 E.2586
G1 X37.598 Y66.802 E.2586
G1 X37.598 Y74.538 E.25661
G1 X37.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X29.41 Y74.99 E.26364
G1 X29.41 Y66.41 E.26364
G1 X37.99 Y66.41 E.26364
G1 X37.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X35.99 Y74.944 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.551 Y68.736 Z2.8 F30000
G1 X30.945 Y67.889 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y67.924 E.00191
G1 X30.929 Y67.951 E.00141
G1 X32.006 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X30.571 Y67.571 E.0441
G1 X30.571 Y69.007 E.0441
G1 X30.763 Y68.671 E.01188
G1 X31.137 Y68.215 E.0181
G1 X31.671 Y67.763 E.0215
G1 X31.954 Y67.601 E.01004
G1 X37.206 Y67.194 F30000
; LINE_WIDTH: 0.41644
G1 F15000
G2 X32.414 Y67.194 I-2.396 J304.598 E.14586
G1 X30.194 Y67.194 E.06755
G2 X30.194 Y71.987 I296.461 J2.396 E.14587
G1 X30.194 Y74.206 E.06755
G2 X34.987 Y74.206 I2.397 J-296.343 E.14587
G1 X37.206 Y74.206 E.06755
G2 X37.206 Y69.413 I-308.81 J-2.396 E.14587
G1 X37.206 Y67.254 E.06572
G1 X36.829 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X35.394 Y67.571 E.0441
G1 X35.729 Y67.763 E.01188
G1 X36.185 Y68.137 E.01811
G1 X36.637 Y68.671 E.0215
G1 X36.829 Y69.006 E.01188
G1 X36.829 Y67.631 E.04226
G1 X36.496 Y67.889 F30000
; LINE_WIDTH: 0.37222
G1 F15000
G1 X36.434 Y67.924 E.00191
G1 X36.48 Y67.951 E.00141
G1 X36.346 Y68.91 F30000
; LINE_WIDTH: 0.415363
G1 F15000
G1 X36.644 Y69.461 E.01901
G1 X36.828 Y70.059 E.01901
G3 X36.835 Y71.305 I-4.117 J.645 E.03795
G1 X36.658 Y71.905 E.019
G1 X36.366 Y72.459 E.019
G1 X35.972 Y72.945 E.019
G1 X35.49 Y73.346 E.019
G1 X34.939 Y73.644 E.01901
G1 X34.341 Y73.829 E.01901
G3 X33.095 Y73.835 I-.643 J-4.15 E.03795
G1 X32.495 Y73.658 E.019
G1 X31.941 Y73.366 E.01901
G1 X31.454 Y72.972 E.019
G1 X31.054 Y72.49 E.019
G1 X30.756 Y71.939 E.01901
G1 X30.571 Y71.341 E.01901
G3 X30.565 Y70.095 I4.149 J-.643 E.03795
G1 X30.742 Y69.495 E.019
G1 X31.034 Y68.941 E.01901
G1 X31.428 Y68.455 E.019
G1 X31.91 Y68.054 E.019
G1 X32.461 Y67.756 E.01901
G1 X33.063 Y67.571 E.01913
G1 X33.594 Y67.525 E.01616
G1 X34.301 Y67.565 E.02152
G1 X34.905 Y67.742 E.0191
G1 X35.459 Y68.034 E.019
G1 X35.945 Y68.428 E.019
G1 X36.307 Y68.864 E.01718
G1 X36.829 Y72.394 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X36.637 Y72.729 E.01188
G1 X36.263 Y73.185 E.01811
G1 X35.729 Y73.637 E.0215
G1 X35.394 Y73.829 E.01188
G1 X36.829 Y73.829 E.0441
G1 X36.829 Y72.454 E.04226
G1 X36.496 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y73.476 E.00191
G1 X36.48 Y73.502 E.00141
G1 X32.007 Y73.829 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X31.671 Y73.637 E.01188
G1 X31.215 Y73.263 E.01811
G1 X30.763 Y72.729 E.0215
G1 X30.571 Y72.394 E.01188
G1 X30.571 Y73.829 E.0441
G1 X31.947 Y73.829 E.04226
G1 X30.945 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y73.476 E.00191
G1 X30.929 Y73.502 E.00141
; WIPE_START
G1 X30.883 Y73.476 E-.32216
G1 X30.945 Y73.44 E-.43784
; WIPE_END
G1 E-.04 F1800
G1 X38.356 Y75.265 Z2.8 F30000
G1 X66.098 Y82.098 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X61.302 Y82.098 E.15909
G1 X61.302 Y77.302 E.15909
G1 X66.098 Y77.302 E.15909
G1 X66.098 Y82.038 E.1571
G1 X66.49 Y82.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X60.91 Y82.49 E.17146
G1 X60.91 Y76.91 E.17146
G1 X66.49 Y76.91 E.17146
G1 X66.49 Y82.43 E.16961
; WIPE_START
M204 S10000
G1 X64.49 Y82.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X63.855 Y79.545 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.35197
G1 F15000
G1 X63.545 Y79.545 E.00778
G1 X63.545 Y79.855 E.00778
G1 X63.855 Y79.855 E.00778
G1 X63.855 Y79.605 E.00627
G1 X64.198 Y79.202 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X63.202 Y79.202 E.03058
G1 X63.202 Y80.198 E.03058
G1 X64.198 Y80.198 E.03058
G1 X64.198 Y79.262 E.02873
G1 X64.575 Y78.825 F30000
G1 F15000
G1 X62.825 Y78.825 E.05375
G1 X62.825 Y80.575 E.05375
G1 X64.575 Y80.575 E.05375
G1 X64.575 Y78.885 E.05191
G1 X64.952 Y78.448 F30000
G1 F15000
G1 X62.448 Y78.448 E.07692
G1 X62.448 Y80.952 E.07692
G1 X64.952 Y80.952 E.07692
G1 X64.952 Y78.508 E.07508
G1 X65.329 Y78.071 F30000
G1 F15000
G1 X62.071 Y78.071 E.10009
G1 X62.071 Y81.329 E.10009
G1 X65.329 Y81.329 E.10009
G1 X65.329 Y78.131 E.09825
G1 X65.706 Y77.694 F30000
G1 F15000
G1 X61.694 Y77.694 E.12327
G1 X61.694 Y81.706 E.12327
G1 X65.706 Y81.706 E.12327
G1 X65.706 Y77.754 E.12142
; WIPE_START
G1 X65.706 Y79.754 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X73.123 Y77.956 Z2.8 F30000
G1 X93.11 Y73.11 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y67.898 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X83.802 Y67.898 E.30876
G1 X83.802 Y66.802 E.03635
G1 X93.598 Y66.802 E.32495
G1 X93.598 Y67.898 E.03635
G1 X93.17 Y67.898 E.0142
; WIPE_START
G1 X91.17 Y67.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.598 Y74.598 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
G1 F15476.087
G1 X83.802 Y74.598 E.32495
G1 X83.802 Y73.502 E.03635
G1 X93.598 Y73.502 E.32495
G1 X93.598 Y74.538 E.03436
G1 X93.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X83.41 Y74.99 E.32509
G1 X83.41 Y66.41 E.26364
G1 X93.99 Y66.41 E.32509
G1 X93.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X91.99 Y74.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.55 Y73.306 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X93.55 Y68.094 E.20723
; WIPE_START
G1 X93.55 Y70.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.262 Y67.826 Z2.8 F30000
G1 X84.178 Y67.178 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y67.522 E.00967
G1 X93.222 Y67.522 E.25382
G1 X93.222 Y67.178 E.00967
G1 X84.238 Y67.178 E.25214
G1 X83.85 Y68.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X83.85 Y73.306 E.20723
G1 X84.178 Y73.878 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y74.222 E.00967
G1 X93.222 Y74.222 E.25382
G1 X93.222 Y73.878 E.00967
G1 X84.238 Y73.878 E.25214
; WIPE_START
G1 X86.238 Y73.878 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.327 Y66.323 Z2.8 F30000
G1 X92.548 Y30.098 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X89.002 Y30.098 E.11762
G1 X89.002 Y22.302 E.2586
G1 X91.598 Y22.302 E.08611
G1 X91.598 Y27.702 E.17913
G1 X92.548 Y27.702 E.03151
G1 X92.548 Y30.038 E.07749
; WIPE_START
G1 X90.548 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.181 Y30.091 Z2.8 F30000
G1 X100.798 Y30.098 Z2.8
G1 Z2.4
G1 E.8 F1800
G1 F15476.087
G1 X97.252 Y30.098 E.11762
G1 X97.252 Y27.702 E.07948
G1 X98.202 Y27.702 E.03151
G1 X98.202 Y22.302 E.17913
G1 X100.798 Y22.302 E.08611
G1 X100.798 Y30.038 E.25661
G1 X101.19 Y30.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X96.86 Y30.49 E.13305
G1 X96.86 Y28.269 E.06825
G1 X96.86 Y27.869 E.01229
G1 F9901.871
G1 X96.86 Y27.469 E.01229
G1 F3789.734
G1 X96.86 Y27.31 E.00489
G1 F2160
G1 X97.81 Y27.31 E.02919
G1 X97.81 Y22.831 E.13763
G1 F2536.674
G1 X97.81 Y22.79 E.00126
G1 F7799.139
G1 X97.41 Y22.79 E.01229
G1 F12000
G1 X96.86 Y22.79 E.0169
G1 X96.86 Y22.49 E.00922
G1 X92.94 Y22.49 E.12045
G1 X92.94 Y22.79 E.00922
G1 X92.39 Y22.79 E.0169
G1 F7799.139
G1 X91.99 Y22.79 E.01229
G1 F2536.674
G1 X91.99 Y22.831 E.00126
G1 F2160
G1 X91.99 Y27.31 E.13763
G1 X92.94 Y27.31 E.02919
G1 F3789.734
G1 X92.94 Y27.469 E.00489
G1 F9901.871
G1 X92.94 Y27.869 E.01229
G1 F12000
G1 X92.94 Y28.269 E.01229
G1 X92.94 Y30.49 E.06825
G1 X88.61 Y30.49 E.13305
G1 X88.61 Y21.91 E.26364
G1 X101.19 Y21.91 E.38655
G1 X101.19 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X99.19 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.579 Y28.892 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.524516
G1 F13081.512
G2 X99.604 Y28.904 I.907 J-35.52 E.04023
; LINE_WIDTH: 0.495045
G1 F13934.2
G1 X99.625 Y28.635 E.00995
; LINE_WIDTH: 0.453615
G1 F15000
G1 X99.645 Y28.365 E.00904
; LINE_WIDTH: 0.384117
G2 X99.67 Y27.906 I-4.161 J-.456 E.01281
G1 X99.67 Y23.43 E.12444
G1 X99.33 Y23.43 E.00946
G1 X99.32 Y28.066 E.1289
; LINE_WIDTH: 0.412185
G1 X99.274 Y28.218 E.00477
; LINE_WIDTH: 0.453615
G1 X99.228 Y28.369 E.0053
; LINE_WIDTH: 0.495045
G1 F13934.2
G1 X99.182 Y28.521 E.00583
; LINE_WIDTH: 0.52714
G1 F13010.615
G1 X98.63 Y28.861 E.0256
G1 X98.451 Y28.899 F30000
; LINE_WIDTH: 0.53149
G1 F12894.776
G1 X98.519 Y28.896 E.00272
G1 X98.021 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X100.029 Y29.329 E.06169
G1 X100.029 Y23.071 E.19227
G1 X98.971 Y23.071 E.0325
G1 X98.971 Y27.906 E.14854
G1 X98.849 Y28.257 E.01143
G1 X98.503 Y28.463 E.01236
G1 X98.021 Y28.471 E.01482
G1 X98.021 Y29.269 E.02451
G1 X97.644 Y29.706 F30000
G1 F15000
G1 X100.406 Y29.706 E.08486
G1 X100.406 Y22.694 E.21545
G1 X98.594 Y22.694 E.05567
G1 X98.594 Y27.906 E.16013
G1 X98.553 Y28.023 E.00381
G1 X98.406 Y28.094 E.00504
G1 X97.644 Y28.094 E.0234
G1 X97.644 Y29.646 E.04768
; WIPE_START
G1 X97.644 Y28.094 E-.58967
G1 X98.092 Y28.094 E-.17034
; WIPE_END
G1 E-.04 F1800
G1 X97.844 Y22.594 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X97.647 Y22.495 E.00632
; LINE_WIDTH: 0.348323
G1 X97.45 Y22.397 E.00548
; LINE_WIDTH: 0.301338
G1 X97.253 Y22.298 E.00464
; LINE_WIDTH: 0.232002
G1 X97.056 Y22.2 E.00339
G1 X92.744 Y22.2 E.06644
; LINE_WIDTH: 0.254353
G1 X92.547 Y22.298 E.00379
; LINE_WIDTH: 0.301338
G1 X92.35 Y22.397 E.00464
; LINE_WIDTH: 0.348323
G1 X92.153 Y22.495 E.00548
; LINE_WIDTH: 0.395308
G1 X91.956 Y22.594 E.00632
; WIPE_START
G1 X92.153 Y22.495 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X90.196 Y28.904 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51576
G1 F13323.746
G1 X91.35 Y28.899 E.04444
G1 X90.618 Y28.521 E.03174
; LINE_WIDTH: 0.495047
G1 F13934.148
G1 X90.572 Y28.369 E.00583
; LINE_WIDTH: 0.45362
G1 F15000
G1 X90.526 Y28.218 E.0053
; LINE_WIDTH: 0.383728
G3 X90.47 Y27.906 I.628 J-.273 E.00888
G1 X90.47 Y23.43 E.1243
G1 X90.13 Y23.43 E.00945
G1 X90.13 Y27.906 E.1243
; LINE_WIDTH: 0.405277
G1 X90.152 Y28.16 E.00753
; LINE_WIDTH: 0.44947
G1 X90.174 Y28.413 E.00844
; LINE_WIDTH: 0.502702
G1 F13702.155
G3 X90.196 Y28.844 I-2.462 J.342 E.01617
G1 X89.771 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X91.779 Y29.329 E.06169
G1 X91.779 Y28.471 E.02635
G1 X91.369 Y28.471 E.0126
G1 X90.951 Y28.257 E.01442
G1 X90.829 Y27.906 E.01143
G1 X90.829 Y23.071 E.14854
G1 X89.771 Y23.071 E.0325
G1 X89.771 Y29.269 E.19043
G1 X89.394 Y29.706 F30000
G1 F15000
G1 X92.156 Y29.706 E.08486
G1 X92.156 Y28.094 E.04952
G1 X91.394 Y28.094 E.0234
G1 X91.247 Y28.023 E.00504
G1 X91.206 Y27.906 E.00381
G1 X91.206 Y22.694 E.16013
G1 X89.394 Y22.694 E.05567
G1 X89.394 Y29.646 E.2136
; WIPE_START
G1 X89.394 Y27.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.536 Y22.005 Z2.8 F30000
G1 X98.098 Y18.098 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.302 Y18.098 E.15909
G1 X93.302 Y13.302 E.15909
G1 X98.098 Y13.302 E.15909
G1 X98.098 Y18.038 E.1571
G1 X98.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.91 Y18.49 E.17146
G1 X92.91 Y12.91 E.17146
G1 X98.49 Y12.91 E.17146
G1 X98.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X96.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.694 Y17.706 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X97.706 Y17.706 E.12327
G1 X97.706 Y13.694 E.12327
G1 X93.694 Y13.694 E.12327
G1 X93.694 Y17.646 E.12142
G1 X94.071 Y17.329 F30000
G1 F15000
G1 X97.329 Y17.329 E.10009
G1 X97.329 Y14.071 E.10009
G1 X94.071 Y14.071 E.10009
G1 X94.071 Y17.269 E.09825
G1 X94.448 Y16.952 F30000
G1 F15000
G1 X96.952 Y16.952 E.07692
G1 X96.952 Y14.448 E.07692
G1 X94.448 Y14.448 E.07692
G1 X94.448 Y16.892 E.07508
G1 X94.825 Y16.575 F30000
G1 F15000
G1 X96.575 Y16.575 E.05375
G1 X96.575 Y14.825 E.05375
G1 X94.825 Y14.825 E.05375
G1 X94.825 Y16.515 E.05191
G1 X95.202 Y16.198 F30000
G1 F15000
G1 X96.198 Y16.198 E.03058
G1 X96.198 Y15.202 E.03058
G1 X95.202 Y15.202 E.03058
G1 X95.202 Y16.138 E.02873
G1 X95.545 Y15.855 F30000
; LINE_WIDTH: 0.35197
G1 F15000
G1 X95.855 Y15.855 E.00778
G1 X95.855 Y15.545 E.00778
G1 X95.545 Y15.545 E.00778
G1 X95.545 Y15.795 E.00627
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X95.545 Y15.545 E-.16092
G1 X95.855 Y15.545 E-.19969
G1 X95.855 Y15.855 E-.19969
G1 X95.545 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 13/40
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
G17
G3 Z2.8 I1.217 J0 P1  F30000
; object ids of layer 13 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer13 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z3 F30000
G1 X114.002 Y8.498 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; OBJECT_ID: 8
; WIPE_START
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X107.49 Y8.581 Z3 F30000
G1 X34.098 Y18.098 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.302 Y18.098 E.15909
G1 X29.302 Y13.302 E.15909
G1 X34.098 Y13.302 E.15909
G1 X34.098 Y18.038 E.1571
G1 X34.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X28.91 Y18.49 E.17146
G1 X28.91 Y12.91 E.17146
G1 X34.49 Y12.91 E.17146
G1 X34.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X32.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.706 Y17.706 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X33.706 Y13.694 E.12327
G1 X29.694 Y13.694 E.12327
G1 X29.694 Y17.706 E.12327
G1 X33.646 Y17.706 E.12142
G1 X33.329 Y17.329 F30000
G1 F15000
G1 X33.329 Y14.071 E.10009
G1 X30.071 Y14.071 E.10009
G1 X30.071 Y17.329 E.10009
G1 X33.269 Y17.329 E.09825
G1 X32.952 Y16.952 F30000
G1 F15000
G1 X32.952 Y14.448 E.07692
G1 X30.448 Y14.448 E.07692
G1 X30.448 Y16.952 E.07692
G1 X32.892 Y16.952 E.07508
G1 X32.575 Y16.575 F30000
G1 F15000
G1 X32.575 Y14.825 E.05375
G1 X30.825 Y14.825 E.05375
G1 X30.825 Y16.575 E.05375
G1 X32.515 Y16.575 E.05191
G1 X32.198 Y16.198 F30000
G1 F15000
G1 X32.198 Y15.202 E.03058
G1 X31.202 Y15.202 E.03058
G1 X31.202 Y16.198 E.03058
G1 X32.138 Y16.198 E.02874
G1 X31.855 Y15.855 F30000
; LINE_WIDTH: 0.35198
G1 F15000
G1 X31.855 Y15.545 E.00778
G1 X31.545 Y15.545 E.00778
G1 X31.545 Y15.855 E.00778
G1 X31.795 Y15.855 E.00627
; WIPE_START
G1 X31.545 Y15.855 E-.16093
G1 X31.545 Y15.545 E-.19969
G1 X31.855 Y15.545 E-.19969
G1 X31.855 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
G1 X35.041 Y22.79 Z3 F30000
G1 X38.398 Y30.098 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X34.852 Y30.098 E.11762
G1 X34.852 Y27.502 E.08611
G1 X35.602 Y27.502 E.02488
G1 X35.602 Y22.302 E.17249
G1 X38.398 Y22.302 E.09274
G1 X38.398 Y30.038 E.25661
; WIPE_START
G1 X36.398 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.148 Y30.098 Z3 F30000
G1 Z2.6
G1 E.8 F1800
G1 F15476.087
G1 X26.602 Y30.098 E.11762
G1 X26.602 Y22.302 E.2586
G1 X29.398 Y22.302 E.09274
G1 X29.398 Y27.502 E.17249
G1 X30.148 Y27.502 E.02488
G1 X30.148 Y30.038 E.08412
; WIPE_START
G1 X28.148 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.775 Y30.371 Z3 F30000
G1 X38.79 Y30.49 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X34.46 Y30.49 E.13305
G1 X34.46 Y28.069 E.07439
G1 X34.46 Y27.669 E.01229
G1 F9901.871
G1 X34.46 Y27.269 E.01229
G1 F3789.734
G1 X34.46 Y27.11 E.00489
G1 F2160
G1 X35.21 Y27.11 E.02305
G1 X35.21 Y22.831 E.13148
G1 F2536.674
G1 X35.21 Y22.79 E.00126
G1 F7799.139
G1 X34.81 Y22.79 E.01229
G1 F12000
G1 X34.46 Y22.79 E.01075
G1 X34.46 Y22.49 E.00922
G1 X30.54 Y22.49 E.12045
G1 X30.54 Y22.79 E.00922
G1 X30.19 Y22.79 E.01075
G1 F7799.139
G1 X29.79 Y22.79 E.01229
G1 F2536.674
G1 X29.79 Y22.831 E.00126
G1 F2160
G1 X29.79 Y27.11 E.13148
G1 X30.54 Y27.11 E.02305
G1 F3789.734
G1 X30.54 Y27.269 E.00489
G1 F9901.871
G1 X30.54 Y27.669 E.01229
G1 F12000
G1 X30.54 Y28.069 E.01229
G1 X30.54 Y30.49 E.07439
G1 X26.21 Y30.49 E.13305
G1 X26.21 Y21.91 E.26364
G1 X38.79 Y21.91 E.38655
G1 X38.79 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X36.79 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.877 Y28.505 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46818
G1 F14814.467
G2 X36.87 Y28.597 I-.027 J.044 E.00729
G1 X37.252 Y28.952 F30000
; LINE_WIDTH: 0.438048
G1 F15000
G1 X37.234 Y28.433 E.01672
; LINE_WIDTH: 0.482885
G1 F14319.319
G3 X37.22 Y27.706 I6.425 J-.483 E.02608
G1 X37.22 Y23.48 E.1515
G1 X36.78 Y23.48 E.01578
G1 X36.77 Y27.875 E.15756
; LINE_WIDTH: 0.474163
G1 F14608.949
G1 X36.654 Y28.087 E.00848
; LINE_WIDTH: 0.4218
G1 F15000
G1 X36.539 Y28.298 E.00745
G1 X36.121 Y28.594 E.0158
G1 X35.998 Y28.615 E.00384
G1 X35.998 Y28.952 E.01039
G1 X37.192 Y28.952 E.03685
G1 X37.629 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X37.629 Y23.071 E.19227
G1 X36.371 Y23.071 E.03864
G1 X36.371 Y27.706 E.1424
G1 X36.245 Y28.061 E.01159
G1 X35.995 Y28.239 E.00944
G1 X35.621 Y28.271 E.01152
G1 X35.621 Y29.329 E.0325
M73 P90 R3
G1 X37.569 Y29.329 E.05984
G1 X38.006 Y29.706 F30000
G1 F15000
G1 X38.006 Y22.694 E.21545
G1 X35.994 Y22.694 E.06181
G1 X35.994 Y27.706 E.15398
G1 X35.952 Y27.824 E.00386
G1 X35.806 Y27.894 E.00499
G1 X35.244 Y27.894 E.01725
G1 X35.244 Y29.706 E.05567
G1 X37.946 Y29.706 E.08302
; WIPE_START
G1 X35.946 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.406 Y22.575 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X35.218 Y22.481 E.00602
; LINE_WIDTH: 0.348323
G1 X35.031 Y22.387 E.00522
; LINE_WIDTH: 0.301338
G1 X34.844 Y22.294 E.00441
; LINE_WIDTH: 0.231949
G1 X34.656 Y22.2 E.00323
G1 X30.344 Y22.2 E.06642
; LINE_WIDTH: 0.254353
G1 X30.156 Y22.294 E.00361
; LINE_WIDTH: 0.301338
G1 X29.969 Y22.387 E.00441
; LINE_WIDTH: 0.348323
G1 X29.782 Y22.481 E.00522
; LINE_WIDTH: 0.395308
G1 X29.594 Y22.575 E.00602
; WIPE_START
G1 X29.782 Y22.481 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.176 Y28.505 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4682
G1 F14813.771
G2 X28.169 Y28.597 I-.027 J.044 E.0073
G1 X29.002 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.002 Y28.615 E.01034
G1 X28.879 Y28.594 E.00382
G1 X28.461 Y28.298 E.01573
; LINE_WIDTH: 0.438053
G1 X28.346 Y28.087 E.00777
; LINE_WIDTH: 0.483039
G1 F14314.322
G1 X28.23 Y27.875 E.00865
G1 X28.22 Y27.706 E.00608
G1 X28.22 Y23.48 E.15155
G1 X27.78 Y23.48 E.01579
G1 X27.78 Y27.706 E.15155
; LINE_WIDTH: 0.46739
G1 F14842.038
G1 X27.764 Y28.128 E.01462
; LINE_WIDTH: 0.423301
G1 F15000
G2 X27.748 Y28.952 I11.004 J.623 E.02554
G1 X28.942 Y28.952 E.03699
G1 X29.379 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.379 Y28.271 E.0325
G1 X29.005 Y28.239 E.01152
G1 X28.755 Y28.061 E.00944
G1 X28.629 Y27.706 E.01159
G1 X28.629 Y23.071 E.1424
G1 X27.371 Y23.071 E.03864
G1 X27.371 Y29.329 E.19227
G1 X29.319 Y29.329 E.05984
G1 X29.756 Y29.706 F30000
G1 F15000
G1 X29.756 Y27.894 E.05567
G1 X29.194 Y27.894 E.01725
G1 X29.048 Y27.824 E.00499
G1 X29.006 Y27.706 E.00386
G1 X29.006 Y22.694 E.15398
G1 X26.994 Y22.694 E.06181
G1 X26.994 Y29.706 E.21545
G1 X29.696 Y29.706 E.08302
; WIPE_START
G1 X27.696 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.704 Y37.271 Z3 F30000
G1 X33.533 Y73.495 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.486 E.00359
G3 X33.634 Y67.9 I.282 J-2.786 E.28003
G3 X34.514 Y68.018 I.082 J2.738 E.02955
G3 X33.7 Y73.501 I-.806 J2.682 E.26501
G1 X33.593 Y73.497 E.00354
G1 X33.553 Y73.099 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.464 Y73.097 E.00275
G3 X33.654 Y68.292 I.244 J-2.397 E.22334
G3 X34.17 Y68.336 I.023 J2.785 E.01595
G3 X33.936 Y73.099 I-.462 J2.364 E.21126
G1 X33.613 Y73.099 E.00992
; WIPE_START
M204 S10000
G1 X33.464 Y73.097 E-.05675
G1 X33 Y73.006 E-.17951
G1 X32.564 Y72.826 E-.17955
G1 X32.171 Y72.563 E-.17956
G1 X31.865 Y72.257 E-.16463
; WIPE_END
G1 E-.04 F1800
G1 X37.598 Y74.598 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.802 Y74.598 E.2586
G1 X29.802 Y66.802 E.2586
G1 X37.598 Y66.802 E.2586
G1 X37.598 Y74.538 E.25661
G1 X37.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X29.41 Y74.99 E.26364
G1 X29.41 Y66.41 E.26364
G1 X37.99 Y66.41 E.26364
G1 X37.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X35.99 Y74.944 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.551 Y68.736 Z3 F30000
G1 X30.945 Y67.889 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y67.924 E.00191
G1 X30.929 Y67.951 E.00141
G1 X32.006 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X30.571 Y67.571 E.0441
G1 X30.571 Y69.006 E.0441
G1 X30.763 Y68.671 E.01188
G1 X31.137 Y68.215 E.01811
G1 X31.671 Y67.763 E.0215
G1 X31.954 Y67.601 E.01004
G1 X37.206 Y67.194 F30000
; LINE_WIDTH: 0.416433
G1 F15000
G2 X32.414 Y67.194 I-2.396 J303.044 E.14586
G1 X30.194 Y67.194 E.06755
G2 X30.194 Y71.987 I296.107 J2.396 E.14587
G1 X30.194 Y74.206 E.06755
G2 X34.987 Y74.206 I2.396 J-296.446 E.14587
G1 X37.206 Y74.206 E.06755
G2 X37.206 Y69.413 I-308.81 J-2.396 E.14587
G1 X37.206 Y67.254 E.06572
G1 X36.829 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X35.394 Y67.571 E.0441
G1 X35.729 Y67.763 E.01188
G1 X36.185 Y68.137 E.01811
G1 X36.637 Y68.671 E.0215
G1 X36.829 Y69.006 E.01188
G1 X36.829 Y67.631 E.04226
G1 X36.496 Y67.889 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y67.924 E.00191
G1 X36.48 Y67.951 E.00141
G1 X36.346 Y68.91 F30000
; LINE_WIDTH: 0.415353
G1 F15000
G1 X36.644 Y69.461 E.019
G1 X36.828 Y70.059 E.019
G3 X36.835 Y71.305 I-4.115 J.646 E.03795
G1 X36.658 Y71.905 E.01899
G1 X36.366 Y72.459 E.019
G1 X35.972 Y72.946 E.019
G1 X35.49 Y73.346 E.019
G1 X34.939 Y73.644 E.019
G1 X34.341 Y73.829 E.01901
G3 X33.095 Y73.835 I-.643 J-4.15 E.03795
G1 X32.495 Y73.658 E.019
G1 X31.941 Y73.366 E.019
G1 X31.454 Y72.972 E.019
G1 X31.054 Y72.49 E.019
G1 X30.756 Y71.939 E.019
G1 X30.571 Y71.341 E.01901
G3 X30.565 Y70.095 I4.15 J-.643 E.03795
G1 X30.742 Y69.495 E.019
G1 X31.034 Y68.941 E.019
G1 X31.428 Y68.454 E.019
G1 X31.91 Y68.054 E.019
G1 X32.461 Y67.756 E.019
G1 X33.063 Y67.571 E.01914
G1 X33.609 Y67.524 E.01661
G1 X34.302 Y67.565 E.02108
G1 X34.905 Y67.742 E.01908
G1 X35.459 Y68.034 E.019
G1 X35.946 Y68.428 E.019
G1 X36.307 Y68.864 E.01718
G1 X36.829 Y72.394 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X36.637 Y72.729 E.01188
G1 X36.263 Y73.185 E.01811
G1 X35.729 Y73.637 E.0215
G1 X35.394 Y73.829 E.01188
G1 X36.829 Y73.829 E.0441
G1 X36.829 Y72.454 E.04226
G1 X36.496 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y73.476 E.00191
G1 X36.48 Y73.502 E.00141
G1 X32.006 Y73.829 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X31.671 Y73.637 E.01188
G1 X31.215 Y73.263 E.01811
G1 X30.763 Y72.729 E.0215
G1 X30.571 Y72.394 E.01188
G1 X30.571 Y73.829 E.0441
G1 X31.946 Y73.829 E.04226
G1 X30.945 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y73.476 E.00191
G1 X30.929 Y73.502 E.00141
; WIPE_START
G1 X30.883 Y73.476 E-.32216
G1 X30.945 Y73.44 E-.43784
; WIPE_END
G1 E-.04 F1800
G1 X38.356 Y75.265 Z3 F30000
G1 X66.098 Y82.098 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X61.302 Y82.098 E.15909
G1 X61.302 Y77.302 E.15909
G1 X66.098 Y77.302 E.15909
G1 X66.098 Y82.038 E.1571
G1 X66.49 Y82.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X60.91 Y82.49 E.17146
G1 X60.91 Y76.91 E.17146
G1 X66.49 Y76.91 E.17146
G1 X66.49 Y82.43 E.16961
; WIPE_START
M204 S10000
G1 X64.49 Y82.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X63.855 Y79.545 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.35197
G1 F15000
G1 X63.545 Y79.545 E.00778
G1 X63.545 Y79.855 E.00778
G1 X63.855 Y79.855 E.00778
G1 X63.855 Y79.605 E.00627
G1 X64.198 Y79.202 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X63.202 Y79.202 E.03058
G1 X63.202 Y80.198 E.03058
G1 X64.198 Y80.198 E.03058
G1 X64.198 Y79.262 E.02873
G1 X64.575 Y78.825 F30000
G1 F15000
G1 X62.825 Y78.825 E.05375
G1 X62.825 Y80.575 E.05375
G1 X64.575 Y80.575 E.05375
G1 X64.575 Y78.885 E.05191
G1 X64.952 Y78.448 F30000
G1 F15000
G1 X62.448 Y78.448 E.07692
G1 X62.448 Y80.952 E.07692
G1 X64.952 Y80.952 E.07692
G1 X64.952 Y78.508 E.07508
G1 X65.329 Y78.071 F30000
G1 F15000
G1 X62.071 Y78.071 E.10009
G1 X62.071 Y81.329 E.10009
G1 X65.329 Y81.329 E.10009
G1 X65.329 Y78.131 E.09825
G1 X65.706 Y77.694 F30000
G1 F15000
G1 X61.694 Y77.694 E.12327
G1 X61.694 Y81.706 E.12327
G1 X65.706 Y81.706 E.12327
G1 X65.706 Y77.754 E.12142
; WIPE_START
G1 X65.706 Y79.754 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X73.123 Y77.956 Z3 F30000
G1 X93.11 Y73.11 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y67.898 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X83.802 Y67.898 E.30876
G1 X83.802 Y66.802 E.03635
G1 X93.598 Y66.802 E.32495
G1 X93.598 Y67.898 E.03635
G1 X93.17 Y67.898 E.0142
; WIPE_START
G1 X91.17 Y67.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.598 Y74.598 Z3 F30000
G1 Z2.6
G1 E.8 F1800
G1 F15476.087
G1 X83.802 Y74.598 E.32495
G1 X83.802 Y73.502 E.03635
G1 X93.598 Y73.502 E.32495
G1 X93.598 Y74.538 E.03436
G1 X93.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X83.41 Y74.99 E.32509
G1 X83.41 Y66.41 E.26364
G1 X93.99 Y66.41 E.32509
G1 X93.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X91.99 Y74.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.55 Y73.306 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X93.55 Y68.094 E.20723
; WIPE_START
G1 X93.55 Y70.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.262 Y67.826 Z3 F30000
G1 X84.178 Y67.178 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y67.522 E.00967
G1 X93.222 Y67.522 E.25382
G1 X93.222 Y67.178 E.00967
G1 X84.238 Y67.178 E.25214
G1 X83.85 Y68.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X83.85 Y73.306 E.20723
G1 X84.178 Y73.878 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y74.222 E.00967
G1 X93.222 Y74.222 E.25382
G1 X93.222 Y73.878 E.00967
G1 X84.238 Y73.878 E.25214
; WIPE_START
G1 X86.238 Y73.878 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.327 Y66.323 Z3 F30000
G1 X92.548 Y30.098 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X89.002 Y30.098 E.11762
G1 X89.002 Y22.302 E.2586
G1 X91.798 Y22.302 E.09274
G1 X91.798 Y27.502 E.17249
G1 X92.548 Y27.502 E.02488
G1 X92.548 Y30.038 E.08412
; WIPE_START
G1 X90.548 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.181 Y30.091 Z3 F30000
G1 X100.798 Y30.098 Z3
G1 Z2.6
G1 E.8 F1800
G1 F15476.087
G1 X97.252 Y30.098 E.11762
G1 X97.252 Y27.502 E.08611
G1 X98.002 Y27.502 E.02488
G1 X98.002 Y22.302 E.17249
G1 X100.798 Y22.302 E.09274
G1 X100.798 Y30.038 E.25661
G1 X101.19 Y30.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X96.86 Y30.49 E.13305
G1 X96.86 Y28.069 E.07439
G1 X96.86 Y27.669 E.01229
G1 F9901.871
G1 X96.86 Y27.269 E.01229
G1 F3789.734
G1 X96.86 Y27.11 E.00489
G1 F2160
G1 X97.61 Y27.11 E.02305
G1 X97.61 Y22.831 E.13148
G1 F2536.674
G1 X97.61 Y22.79 E.00126
G1 F7799.139
G1 X97.21 Y22.79 E.01229
G1 F12000
G1 X96.86 Y22.79 E.01075
G1 X96.86 Y22.49 E.00922
G1 X92.94 Y22.49 E.12045
G1 X92.94 Y22.79 E.00922
G1 X92.59 Y22.79 E.01075
G1 F7799.139
G1 X92.19 Y22.79 E.01229
G1 F2536.674
G1 X92.19 Y22.831 E.00126
G1 F2160
G1 X92.19 Y27.11 E.13148
G1 X92.94 Y27.11 E.02305
G1 F3789.734
G1 X92.94 Y27.269 E.00489
G1 F9901.871
G1 X92.94 Y27.669 E.01229
G1 F12000
G1 X92.94 Y28.069 E.01229
G1 X92.94 Y30.49 E.07439
G1 X88.61 Y30.49 E.13305
G1 X88.61 Y21.91 E.26364
G1 X101.19 Y21.91 E.38655
G1 X101.19 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X99.19 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.277 Y28.505 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46818
G1 F14814.467
G2 X99.27 Y28.597 I-.027 J.044 E.00729
G1 X98.398 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X99.652 Y28.952 E.03851
; LINE_WIDTH: 0.438048
G1 X99.634 Y28.433 E.01672
; LINE_WIDTH: 0.482876
G1 F14319.621
G3 X99.62 Y27.706 I6.421 J-.483 E.02608
G1 X99.62 Y23.48 E.1515
G1 X99.18 Y23.48 E.01578
G1 X99.17 Y27.875 E.15756
; LINE_WIDTH: 0.474163
G1 F14608.949
G1 X99.054 Y28.087 E.00848
; LINE_WIDTH: 0.423765
G1 F15000
G1 X98.939 Y28.298 E.00749
G1 X98.521 Y28.594 E.01588
G1 X98.398 Y28.615 E.00386
G1 X98.398 Y28.892 E.00858
G1 X98.021 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X100.029 Y29.329 E.06169
G1 X100.029 Y23.071 E.19227
G1 X98.771 Y23.071 E.03864
G1 X98.771 Y27.706 E.1424
G1 X98.645 Y28.061 E.01159
G1 X98.395 Y28.239 E.00944
G1 X98.021 Y28.271 E.01152
G1 X98.021 Y29.269 E.03065
G1 X97.644 Y29.706 F30000
G1 F15000
G1 X100.406 Y29.706 E.08486
G1 X100.406 Y22.694 E.21545
G1 X98.394 Y22.694 E.06181
G1 X98.394 Y27.706 E.15398
G1 X98.352 Y27.824 E.00386
G1 X98.206 Y27.894 E.00499
G1 X97.644 Y27.894 E.01725
G1 X97.644 Y29.646 E.05383
; WIPE_START
G1 X97.644 Y27.894 E-.66567
G1 X97.892 Y27.894 E-.09434
; WIPE_END
G1 E-.04 F1800
G1 X97.806 Y22.575 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X97.618 Y22.481 E.00602
; LINE_WIDTH: 0.348323
G1 X97.431 Y22.387 E.00522
; LINE_WIDTH: 0.301338
G1 X97.244 Y22.294 E.00441
; LINE_WIDTH: 0.231949
G1 X97.056 Y22.2 E.00323
G1 X92.744 Y22.2 E.06642
; LINE_WIDTH: 0.254353
G1 X92.557 Y22.294 E.00361
; LINE_WIDTH: 0.301338
G1 X92.369 Y22.387 E.00441
; LINE_WIDTH: 0.348323
G1 X92.182 Y22.481 E.00522
; LINE_WIDTH: 0.395308
G1 X91.994 Y22.575 E.00602
; WIPE_START
G1 X92.182 Y22.481 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X90.576 Y28.505 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4682
G1 F14813.771
G2 X90.569 Y28.597 I-.027 J.044 E.0073
G1 X90.148 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X91.402 Y28.952 E.03851
G1 X91.402 Y28.615 E.01034
G1 X91.279 Y28.594 E.00382
G1 X90.861 Y28.298 E.01573
; LINE_WIDTH: 0.438053
G1 X90.746 Y28.087 E.00777
; LINE_WIDTH: 0.483029
G1 F14314.636
G1 X90.63 Y27.875 E.00865
G1 X90.62 Y27.706 E.00608
G1 X90.62 Y23.48 E.15155
G1 X90.18 Y23.48 E.01579
G1 X90.18 Y27.706 E.15155
; LINE_WIDTH: 0.467383
G1 F14842.301
G1 X90.164 Y28.128 E.01462
; LINE_WIDTH: 0.428733
G1 F15000
G2 X90.148 Y28.892 I10.202 J.593 E.02402
G1 X89.771 Y29.329 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X91.779 Y29.329 E.06169
G1 X91.779 Y28.271 E.0325
G1 X91.405 Y28.239 E.01152
G1 X91.155 Y28.061 E.00944
G1 X91.029 Y27.706 E.01159
G1 X91.029 Y23.071 E.1424
G1 X89.771 Y23.071 E.03864
G1 X89.771 Y29.269 E.19043
G1 X89.394 Y29.706 F30000
G1 F15000
G1 X92.156 Y29.706 E.08486
G1 X92.156 Y27.894 E.05567
G1 X91.594 Y27.894 E.01725
G1 X91.448 Y27.824 E.00499
G1 X91.406 Y27.706 E.00386
G1 X91.406 Y22.694 E.15398
G1 X89.394 Y22.694 E.06181
G1 X89.394 Y29.646 E.2136
; WIPE_START
G1 X89.394 Y27.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.536 Y22.005 Z3 F30000
G1 X98.098 Y18.098 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.302 Y18.098 E.15909
G1 X93.302 Y13.302 E.15909
G1 X98.098 Y13.302 E.15909
G1 X98.098 Y18.038 E.1571
G1 X98.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.91 Y18.49 E.17146
G1 X92.91 Y12.91 E.17146
G1 X98.49 Y12.91 E.17146
G1 X98.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X96.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.694 Y17.706 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X97.706 Y17.706 E.12327
G1 X97.706 Y13.694 E.12327
G1 X93.694 Y13.694 E.12327
G1 X93.694 Y17.646 E.12142
G1 X94.071 Y17.329 F30000
G1 F15000
G1 X97.329 Y17.329 E.10009
G1 X97.329 Y14.071 E.10009
G1 X94.071 Y14.071 E.10009
G1 X94.071 Y17.269 E.09825
G1 X94.448 Y16.952 F30000
G1 F15000
G1 X96.952 Y16.952 E.07692
G1 X96.952 Y14.448 E.07692
G1 X94.448 Y14.448 E.07692
G1 X94.448 Y16.892 E.07508
G1 X94.825 Y16.575 F30000
G1 F15000
G1 X96.575 Y16.575 E.05375
G1 X96.575 Y14.825 E.05375
G1 X94.825 Y14.825 E.05375
G1 X94.825 Y16.515 E.05191
G1 X95.202 Y16.198 F30000
G1 F15000
G1 X96.198 Y16.198 E.03058
G1 X96.198 Y15.202 E.03058
G1 X95.202 Y15.202 E.03058
G1 X95.202 Y16.138 E.02873
G1 X95.545 Y15.855 F30000
; LINE_WIDTH: 0.35197
G1 F15000
G1 X95.855 Y15.855 E.00778
G1 X95.855 Y15.545 E.00778
G1 X95.545 Y15.545 E.00778
G1 X95.545 Y15.795 E.00627
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X95.545 Y15.545 E-.16092
G1 X95.855 Y15.545 E-.19969
G1 X95.855 Y15.855 E-.19969
G1 X95.545 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 14/40
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
G17
G3 Z3 I1.217 J0 P1  F30000
; object ids of layer 14 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer14 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z3.2 F30000
G1 X114.002 Y8.498 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; OBJECT_ID: 8
; WIPE_START
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X107.49 Y8.581 Z3.2 F30000
G1 X34.098 Y18.098 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.302 Y18.098 E.15909
G1 X29.302 Y13.302 E.15909
G1 X34.098 Y13.302 E.15909
G1 X34.098 Y18.038 E.1571
G1 X34.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X28.91 Y18.49 E.17146
G1 X28.91 Y12.91 E.17146
G1 X34.49 Y12.91 E.17146
G1 X34.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X32.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.706 Y17.706 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X33.706 Y13.694 E.12327
G1 X29.694 Y13.694 E.12327
G1 X29.694 Y17.706 E.12327
G1 X33.646 Y17.706 E.12142
G1 X33.329 Y17.329 F30000
G1 F15000
G1 X33.329 Y14.071 E.10009
G1 X30.071 Y14.071 E.10009
G1 X30.071 Y17.329 E.10009
G1 X33.269 Y17.329 E.09825
G1 X32.952 Y16.952 F30000
G1 F15000
G1 X32.952 Y14.448 E.07692
G1 X30.448 Y14.448 E.07692
G1 X30.448 Y16.952 E.07692
G1 X32.892 Y16.952 E.07508
G1 X32.575 Y16.575 F30000
G1 F15000
G1 X32.575 Y14.825 E.05375
G1 X30.825 Y14.825 E.05375
G1 X30.825 Y16.575 E.05375
G1 X32.515 Y16.575 E.05191
G1 X32.198 Y16.198 F30000
G1 F15000
G1 X32.198 Y15.202 E.03058
G1 X31.202 Y15.202 E.03058
G1 X31.202 Y16.198 E.03058
G1 X32.138 Y16.198 E.02874
G1 X31.855 Y15.855 F30000
; LINE_WIDTH: 0.35198
G1 F15000
G1 X31.855 Y15.545 E.00778
G1 X31.545 Y15.545 E.00778
G1 X31.545 Y15.855 E.00778
G1 X31.795 Y15.855 E.00627
; WIPE_START
G1 X31.545 Y15.855 E-.16093
G1 X31.545 Y15.545 E-.19969
G1 X31.855 Y15.545 E-.19969
G1 X31.855 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
G1 X35.041 Y22.79 Z3.2 F30000
G1 X38.398 Y30.098 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X34.852 Y30.098 E.11762
G1 X34.852 Y27.302 E.09274
G1 X35.402 Y27.302 E.01824
G1 X35.402 Y22.302 E.16586
G1 X38.398 Y22.302 E.09938
G1 X38.398 Y30.038 E.25661
; WIPE_START
G1 X36.398 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.148 Y30.098 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
G1 F15476.087
G1 X26.602 Y30.098 E.11762
G1 X26.602 Y22.302 E.2586
G1 X29.598 Y22.302 E.09938
G1 X29.598 Y27.302 E.16586
G1 X30.148 Y27.302 E.01824
G1 X30.148 Y30.038 E.09075
; WIPE_START
G1 X28.148 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.775 Y30.371 Z3.2 F30000
G1 X38.79 Y30.49 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X34.46 Y30.49 E.13305
G1 X34.46 Y27.869 E.08054
G1 X34.46 Y27.469 E.01229
G1 F9901.871
G1 X34.46 Y27.069 E.01229
G1 F3789.734
G1 X34.46 Y26.91 E.00489
G1 F2160
G1 X35.01 Y26.91 E.0169
G1 X35.01 Y22.831 E.12534
G1 F2536.674
G1 X35.01 Y22.79 E.00126
G1 F10515.063
G1 X34.46 Y22.79 E.0169
G1 F12000
G1 X34.46 Y22.49 E.00922
G1 X30.54 Y22.49 E.12045
G1 X30.54 Y22.79 E.00922
G1 F10515.063
G1 X29.99 Y22.79 E.0169
G1 F2536.674
G1 X29.99 Y22.831 E.00126
G1 F2160
G1 X29.99 Y26.91 E.12534
G1 X30.54 Y26.91 E.0169
G1 F3789.734
G1 X30.54 Y27.069 E.00489
G1 F9901.871
G1 X30.54 Y27.469 E.01229
G1 F12000
G1 X30.54 Y27.869 E.01229
G1 X30.54 Y30.49 E.08054
G1 X26.21 Y30.49 E.13305
G1 X26.21 Y21.91 E.26364
G1 X38.79 Y21.91 E.38655
G1 X38.79 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X36.79 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.89 Y27.731 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.369891
G1 F15000
G1 X36.9 Y23.86 E.10314
G1 X36.898 Y28.598 F30000
; LINE_WIDTH: 0.377727
G1 F15000
G1 X36.89 Y27.731 E.02367
G1 X36.606 Y28.329 E.01806
G1 X36.352 Y28.598 E.01012
G1 X36.838 Y28.598 E.01328
G1 X37.252 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X37.252 Y23.448 E.1691
G1 X36.548 Y23.448 E.02162
G1 X36.548 Y27.506 E.12467
G1 X36.534 Y27.668 E.00502
G1 X36.334 Y28.105 E.01475
G1 X36.155 Y28.272 E.00752
G1 X35.998 Y28.322 E.00505
G1 X35.998 Y28.952 E.01935
G1 X37.192 Y28.952 E.03667
G1 X37.629 Y29.329 F30000
G1 F15000
G1 X37.629 Y23.071 E.19227
G1 X36.171 Y23.071 E.04479
G1 X36.171 Y27.506 E.13625
G1 X36.042 Y27.865 E.01173
G1 X35.935 Y27.965 E.00451
G1 X35.621 Y28.066 E.01013
G1 X35.621 Y29.329 E.0388
G1 X37.569 Y29.329 E.05984
G1 X38.006 Y29.706 F30000
G1 F15000
G1 X38.006 Y22.694 E.21545
G1 X35.794 Y22.694 E.06796
G1 X35.794 Y27.506 E.14784
G1 X35.715 Y27.659 E.00529
G1 X35.606 Y27.694 E.00355
G1 X35.244 Y27.694 E.01111
G1 X35.244 Y29.706 E.06181
G1 X37.946 Y29.706 E.08302
; WIPE_START
G1 X35.946 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.206 Y22.475 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X35.068 Y22.406 E.00441
; LINE_WIDTH: 0.348323
G1 X34.931 Y22.337 E.00383
; LINE_WIDTH: 0.301338
G1 X34.794 Y22.269 E.00324
; LINE_WIDTH: 0.231669
G1 X34.656 Y22.2 E.00236
G1 X30.344 Y22.2 E.06632
; LINE_WIDTH: 0.254353
G1 X30.206 Y22.269 E.00265
; LINE_WIDTH: 0.301338
G1 X30.069 Y22.337 E.00324
; LINE_WIDTH: 0.348323
G1 X29.932 Y22.406 E.00383
; LINE_WIDTH: 0.395308
G1 X29.794 Y22.475 E.00441
; WIPE_START
G1 X29.932 Y22.406 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.1 Y23.8 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.36974
G1 F15000
G1 X28.107 Y27.671 E.10309
G1 X28.648 Y28.598 F30000
; LINE_WIDTH: 0.377149
G1 F15000
G1 X28.648 Y28.562 E.001
G1 X28.394 Y28.329 E.0094
G1 X28.11 Y27.731 E.01803
G2 X28.102 Y28.598 I37.032 J.785 E.02363
G1 X28.588 Y28.598 E.01326
G1 X29.002 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X29.002 Y28.322 E.01935
G1 X28.845 Y28.272 E.00505
G1 X28.666 Y28.105 E.00752
G1 X28.466 Y27.668 E.01475
G1 X28.452 Y27.506 E.00502
G1 X28.452 Y23.448 E.12467
G1 X27.748 Y23.448 E.02162
G1 X27.748 Y28.952 E.1691
G1 X28.942 Y28.952 E.03667
G1 X29.379 Y29.329 F30000
G1 F15000
G1 X29.379 Y28.066 E.0388
G1 X29.065 Y27.965 E.01013
G1 X28.958 Y27.865 E.00451
G1 X28.829 Y27.506 E.01173
G1 X28.829 Y23.071 E.13625
G1 X27.371 Y23.071 E.04479
G1 X27.371 Y29.329 E.19227
G1 X29.319 Y29.329 E.05984
G1 X29.756 Y29.706 F30000
G1 F15000
G1 X29.756 Y27.694 E.06181
G1 X29.394 Y27.694 E.01111
M73 P91 R3
G1 X29.249 Y27.625 E.00495
G1 X29.206 Y27.506 E.00391
G1 X29.206 Y22.694 E.14784
G1 X26.994 Y22.694 E.06796
G1 X26.994 Y29.706 E.21545
G1 X29.696 Y29.706 E.08302
; WIPE_START
G1 X27.696 Y29.706 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.702 Y37.272 Z3.2 F30000
G1 X33.516 Y73.494 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X33.426 Y73.486 E.00302
G3 X33.425 Y67.911 I.274 J-2.788 E.27367
G1 X33.7 Y67.897 E.00912
G3 X33.7 Y73.499 I0 J2.801 E.29191
G1 X33.576 Y73.496 E.00411
G1 X33.536 Y73.094 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X33.23 Y73.061 E.00943
G3 X33.464 Y68.301 I.47 J-2.363 E.21072
G1 X33.7 Y68.29 E.00727
G3 X33.7 Y73.107 I0 J2.409 E.23253
G1 X33.595 Y73.099 E.00323
; WIPE_START
M204 S10000
G1 X33.23 Y73.061 E-.13945
G1 X32.778 Y72.927 E-.17942
G1 X32.361 Y72.704 E-.17956
G1 X31.996 Y72.404 E-.17954
G1 X31.859 Y72.237 E-.08204
; WIPE_END
G1 E-.04 F1800
G1 X37.598 Y74.598 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X29.802 Y74.598 E.2586
G1 X29.802 Y66.802 E.2586
G1 X37.598 Y66.802 E.2586
G1 X37.598 Y74.538 E.25661
G1 X37.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X29.41 Y74.99 E.26364
G1 X29.41 Y66.41 E.26364
G1 X37.99 Y66.41 E.26364
G1 X37.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X35.99 Y74.944 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.551 Y68.736 Z3.2 F30000
G1 X30.945 Y67.889 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y67.924 E.00191
G1 X30.929 Y67.951 E.00141
G1 X32.006 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X30.571 Y67.571 E.0441
G1 X30.571 Y69.006 E.0441
G1 X30.763 Y68.671 E.01188
G1 X31.137 Y68.215 E.01811
G1 X31.671 Y67.763 E.0215
G1 X31.954 Y67.601 E.01004
G1 X37.206 Y67.194 F30000
; LINE_WIDTH: 0.416411
G1 F15000
G2 X32.413 Y67.194 I-2.396 J295.898 E.14586
G1 X30.194 Y67.194 E.06754
G2 X30.194 Y71.987 I296.236 J2.396 E.14586
G1 X30.194 Y74.206 E.06754
G2 X34.987 Y74.206 I2.396 J-296.118 E.14586
G1 X37.206 Y74.206 E.06754
G2 X37.206 Y69.413 I-308.81 J-2.396 E.14586
G1 X37.206 Y67.254 E.06572
G1 X36.829 Y67.571 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X35.394 Y67.571 E.0441
G1 X35.729 Y67.763 E.01188
G1 X36.185 Y68.137 E.01811
G1 X36.637 Y68.671 E.0215
G1 X36.829 Y69.006 E.01188
G1 X36.829 Y67.631 E.04226
G1 X36.496 Y67.889 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y67.924 E.00191
G1 X36.48 Y67.951 E.00141
G1 X36.346 Y68.91 F30000
; LINE_WIDTH: 0.41532
G1 F15000
G1 X36.644 Y69.461 E.019
G1 X36.828 Y70.059 E.019
G3 X36.835 Y71.305 I-4.117 J.645 E.03795
G1 X36.658 Y71.905 E.01899
G1 X36.366 Y72.459 E.019
G1 X35.972 Y72.946 E.019
G1 X35.49 Y73.346 E.019
G1 X34.939 Y73.644 E.019
G1 X34.341 Y73.829 E.019
G3 X33.095 Y73.835 I-.643 J-4.15 E.03795
G1 X32.495 Y73.658 E.01899
G1 X31.941 Y73.366 E.019
G1 X31.454 Y72.972 E.019
G1 X31.054 Y72.49 E.019
G1 X30.756 Y71.939 E.019
G1 X30.571 Y71.341 E.019
M73 P91 R2
G3 X30.565 Y70.095 I4.15 J-.643 E.03795
G1 X30.742 Y69.495 E.01899
G1 X31.034 Y68.941 E.019
G1 X31.428 Y68.454 E.019
G1 X31.91 Y68.054 E.019
G1 X32.461 Y67.756 E.019
G1 X33.059 Y67.571 E.019
G3 X34.305 Y67.565 I.643 J4.15 E.03795
G1 X34.905 Y67.742 E.01899
G1 X35.459 Y68.034 E.019
G1 X35.946 Y68.428 E.019
G1 X36.307 Y68.864 E.01718
G1 X36.829 Y72.394 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X36.637 Y72.729 E.01188
G1 X36.263 Y73.185 E.01811
G1 X35.729 Y73.637 E.0215
G1 X35.394 Y73.829 E.01188
G1 X36.829 Y73.829 E.0441
G1 X36.829 Y72.454 E.04226
G1 X36.496 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X36.434 Y73.476 E.00191
G1 X36.48 Y73.502 E.00141
G1 X32.006 Y73.829 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X31.671 Y73.637 E.01188
G1 X31.215 Y73.263 E.01811
G1 X30.763 Y72.729 E.0215
G1 X30.571 Y72.394 E.01188
G1 X30.571 Y73.829 E.0441
G1 X31.946 Y73.829 E.04226
G1 X30.945 Y73.44 F30000
; LINE_WIDTH: 0.37224
G1 F15000
G1 X30.883 Y73.476 E.00191
G1 X30.929 Y73.502 E.00141
; WIPE_START
G1 X30.883 Y73.476 E-.32216
G1 X30.945 Y73.44 E-.43784
; WIPE_END
G1 E-.04 F1800
G1 X38.356 Y75.265 Z3.2 F30000
G1 X66.098 Y82.098 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X61.302 Y82.098 E.15909
G1 X61.302 Y77.302 E.15909
G1 X66.098 Y77.302 E.15909
G1 X66.098 Y82.038 E.1571
G1 X66.49 Y82.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X60.91 Y82.49 E.17146
G1 X60.91 Y76.91 E.17146
G1 X66.49 Y76.91 E.17146
G1 X66.49 Y82.43 E.16961
; WIPE_START
M204 S10000
G1 X64.49 Y82.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X63.855 Y79.545 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.35197
G1 F15000
G1 X63.545 Y79.545 E.00778
G1 X63.545 Y79.855 E.00778
G1 X63.855 Y79.855 E.00778
G1 X63.855 Y79.605 E.00627
G1 X64.198 Y79.202 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X63.202 Y79.202 E.03058
G1 X63.202 Y80.198 E.03058
G1 X64.198 Y80.198 E.03058
G1 X64.198 Y79.262 E.02873
G1 X64.575 Y78.825 F30000
G1 F15000
G1 X62.825 Y78.825 E.05375
G1 X62.825 Y80.575 E.05375
G1 X64.575 Y80.575 E.05375
G1 X64.575 Y78.885 E.05191
G1 X64.952 Y78.448 F30000
G1 F15000
G1 X62.448 Y78.448 E.07692
G1 X62.448 Y80.952 E.07692
G1 X64.952 Y80.952 E.07692
G1 X64.952 Y78.508 E.07508
G1 X65.329 Y78.071 F30000
G1 F15000
G1 X62.071 Y78.071 E.10009
G1 X62.071 Y81.329 E.10009
G1 X65.329 Y81.329 E.10009
G1 X65.329 Y78.131 E.09825
G1 X65.706 Y77.694 F30000
G1 F15000
G1 X61.694 Y77.694 E.12327
G1 X61.694 Y81.706 E.12327
G1 X65.706 Y81.706 E.12327
G1 X65.706 Y77.754 E.12142
; WIPE_START
G1 X65.706 Y79.754 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X73.123 Y77.956 Z3.2 F30000
G1 X93.11 Y73.11 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.11 Y67.898 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X83.802 Y67.898 E.30876
G1 X83.802 Y66.802 E.03635
G1 X93.598 Y66.802 E.32495
G1 X93.598 Y67.898 E.03635
G1 X93.17 Y67.898 E.0142
; WIPE_START
G1 X91.17 Y67.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.598 Y74.598 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
G1 F15476.087
G1 X83.802 Y74.598 E.32495
G1 X83.802 Y73.502 E.03635
G1 X93.598 Y73.502 E.32495
G1 X93.598 Y74.538 E.03436
G1 X93.99 Y74.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X83.41 Y74.99 E.32509
G1 X83.41 Y66.41 E.26364
G1 X93.99 Y66.41 E.32509
G1 X93.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X91.99 Y74.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.55 Y73.306 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X93.55 Y68.094 E.20723
; WIPE_START
G1 X93.55 Y70.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.262 Y67.826 Z3.2 F30000
G1 X84.178 Y67.178 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y67.522 E.00967
G1 X93.222 Y67.522 E.25382
G1 X93.222 Y67.178 E.00967
G1 X84.238 Y67.178 E.25214
G1 X83.85 Y68.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X83.85 Y73.306 E.20723
G1 X84.178 Y73.878 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38732
G1 F15000
G1 X84.178 Y74.222 E.00967
G1 X93.222 Y74.222 E.25382
G1 X93.222 Y73.878 E.00967
G1 X84.238 Y73.878 E.25214
; WIPE_START
G1 X86.238 Y73.878 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.327 Y66.323 Z3.2 F30000
G1 X92.548 Y30.098 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X89.002 Y30.098 E.11762
G1 X89.002 Y22.302 E.2586
G1 X91.998 Y22.302 E.09938
G1 X91.998 Y27.302 E.16586
G1 X92.548 Y27.302 E.01824
G1 X92.548 Y30.038 E.09075
; WIPE_START
G1 X90.548 Y30.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.181 Y30.091 Z3.2 F30000
G1 X100.798 Y30.098 Z3.2
G1 Z2.8
G1 E.8 F1800
G1 F15476.087
G1 X97.252 Y30.098 E.11762
G1 X97.252 Y27.302 E.09274
G1 X97.802 Y27.302 E.01824
G1 X97.802 Y22.302 E.16586
G1 X100.798 Y22.302 E.09938
G1 X100.798 Y30.038 E.25661
G1 X101.19 Y30.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X96.86 Y30.49 E.13305
G1 X96.86 Y27.869 E.08054
G1 X96.86 Y27.469 E.01229
G1 F9901.871
G1 X96.86 Y27.069 E.01229
G1 F3789.734
G1 X96.86 Y26.91 E.00489
G1 F2160
G1 X97.41 Y26.91 E.0169
G1 X97.41 Y22.831 E.12534
G1 F2536.674
G1 X97.41 Y22.79 E.00126
G1 F10515.063
G1 X96.86 Y22.79 E.0169
G1 F12000
G1 X96.86 Y22.49 E.00922
G1 X92.94 Y22.49 E.12045
G1 X92.94 Y22.79 E.00922
G1 F10515.063
G1 X92.39 Y22.79 E.0169
G1 F2536.674
G1 X92.39 Y22.831 E.00126
G1 F2160
G1 X92.39 Y26.91 E.12534
G1 X92.94 Y26.91 E.0169
G1 F3789.734
G1 X92.94 Y27.069 E.00489
G1 F9901.871
G1 X92.94 Y27.469 E.01229
G1 F12000
G1 X92.94 Y27.869 E.01229
G1 X92.94 Y30.49 E.08054
G1 X88.61 Y30.49 E.13305
G1 X88.61 Y21.91 E.26364
G1 X101.19 Y21.91 E.38655
G1 X101.19 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X99.19 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.29 Y27.731 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.369871
G1 F15000
G1 X99.3 Y23.86 E.10313
G1 X98.752 Y28.598 F30000
; LINE_WIDTH: 0.377727
G1 F15000
G1 X99.298 Y28.598 E.01492
G1 X99.29 Y27.731 E.02367
G1 X99.006 Y28.329 E.01806
G1 X98.793 Y28.555 E.00848
G1 X98.398 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X99.652 Y28.952 E.03851
G1 X99.652 Y23.448 E.1691
G1 X98.948 Y23.448 E.02161
G1 X98.948 Y27.506 E.12467
G1 X98.934 Y27.668 E.00502
G1 X98.734 Y28.105 E.01475
G1 X98.555 Y28.272 E.00752
G1 X98.398 Y28.322 E.00505
G1 X98.398 Y28.892 E.0175
G1 X98.021 Y29.329 F30000
G1 F15000
G1 X100.029 Y29.329 E.06169
G1 X100.029 Y23.071 E.19227
G1 X98.571 Y23.071 E.04479
G1 X98.571 Y27.506 E.13625
G1 X98.442 Y27.865 E.01173
G1 X98.335 Y27.965 E.00451
G1 X98.021 Y28.066 E.01013
G1 X98.021 Y29.269 E.03695
G1 X97.644 Y29.706 F30000
G1 F15000
G1 X100.406 Y29.706 E.08486
G1 X100.406 Y22.694 E.21545
G1 X98.194 Y22.694 E.06796
G1 X98.194 Y27.506 E.14784
G1 X98.115 Y27.659 E.00529
G1 X98.006 Y27.694 E.00355
G1 X97.644 Y27.694 E.01111
G1 X97.644 Y29.646 E.05997
; WIPE_START
G1 X97.644 Y27.694 E-.74167
G1 X97.692 Y27.694 E-.01834
; WIPE_END
G1 E-.04 F1800
G1 X97.606 Y22.475 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.395308
G1 F15000
G1 X97.468 Y22.406 E.00441
; LINE_WIDTH: 0.348323
G1 X97.331 Y22.337 E.00383
; LINE_WIDTH: 0.301338
G1 X97.194 Y22.269 E.00324
; LINE_WIDTH: 0.231669
G1 X97.056 Y22.2 E.00236
G1 X92.744 Y22.2 E.06632
; LINE_WIDTH: 0.254353
G1 X92.607 Y22.269 E.00265
; LINE_WIDTH: 0.301338
G1 X92.469 Y22.337 E.00324
; LINE_WIDTH: 0.348323
G1 X92.332 Y22.406 E.00383
; LINE_WIDTH: 0.395308
G1 X92.194 Y22.475 E.00441
; WIPE_START
G1 X92.332 Y22.406 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X90.5 Y23.8 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.36972
G1 F15000
G1 X90.507 Y27.671 E.10309
G1 X90.502 Y28.598 F30000
; LINE_WIDTH: 0.377149
G1 F15000
G1 X91.048 Y28.598 E.01489
G1 X91.048 Y28.562 E.001
G1 X90.794 Y28.329 E.0094
G1 X90.51 Y27.731 E.01803
G2 X90.502 Y28.538 I34.47 J.755 E.02199
G1 X90.148 Y28.952 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X91.402 Y28.952 E.03851
G1 X91.402 Y28.322 E.01935
G1 X91.245 Y28.272 E.00505
G1 X91.066 Y28.105 E.00752
G1 X90.866 Y27.668 E.01475
G1 X90.852 Y27.506 E.00502
G1 X90.852 Y23.448 E.12467
G1 X90.148 Y23.448 E.02161
G1 X90.148 Y28.892 E.16726
G1 X89.771 Y29.329 F30000
G1 F15000
G1 X91.779 Y29.329 E.06169
G1 X91.779 Y28.066 E.0388
G1 X91.465 Y27.965 E.01013
G1 X91.358 Y27.865 E.00451
G1 X91.229 Y27.506 E.01173
G1 X91.229 Y23.071 E.13625
G1 X89.771 Y23.071 E.04479
G1 X89.771 Y29.269 E.19043
G1 X89.394 Y29.706 F30000
G1 F15000
G1 X92.156 Y29.706 E.08486
G1 X92.156 Y27.694 E.06181
G1 X91.794 Y27.694 E.01111
G1 X91.649 Y27.625 E.00495
G1 X91.606 Y27.506 E.00391
G1 X91.606 Y22.694 E.14784
G1 X89.394 Y22.694 E.06796
G1 X89.394 Y29.646 E.2136
; WIPE_START
G1 X89.394 Y27.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.536 Y22.005 Z3.2 F30000
G1 X98.098 Y18.098 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X93.302 Y18.098 E.15909
G1 X93.302 Y13.302 E.15909
G1 X98.098 Y13.302 E.15909
G1 X98.098 Y18.038 E.1571
G1 X98.49 Y18.49 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X92.91 Y18.49 E.17146
G1 X92.91 Y12.91 E.17146
G1 X98.49 Y12.91 E.17146
G1 X98.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X96.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.694 Y17.706 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X97.706 Y17.706 E.12327
G1 X97.706 Y13.694 E.12327
G1 X93.694 Y13.694 E.12327
G1 X93.694 Y17.646 E.12142
G1 X94.071 Y17.329 F30000
G1 F15000
G1 X97.329 Y17.329 E.10009
G1 X97.329 Y14.071 E.10009
G1 X94.071 Y14.071 E.10009
G1 X94.071 Y17.269 E.09825
G1 X94.448 Y16.952 F30000
G1 F15000
G1 X96.952 Y16.952 E.07692
G1 X96.952 Y14.448 E.07692
G1 X94.448 Y14.448 E.07692
G1 X94.448 Y16.892 E.07508
G1 X94.825 Y16.575 F30000
G1 F15000
G1 X96.575 Y16.575 E.05375
G1 X96.575 Y14.825 E.05375
G1 X94.825 Y14.825 E.05375
G1 X94.825 Y16.515 E.05191
G1 X95.202 Y16.198 F30000
G1 F15000
G1 X96.198 Y16.198 E.03058
G1 X96.198 Y15.202 E.03058
G1 X95.202 Y15.202 E.03058
G1 X95.202 Y16.138 E.02873
G1 X95.545 Y15.855 F30000
; LINE_WIDTH: 0.35197
G1 F15000
G1 X95.855 Y15.855 E.00778
G1 X95.855 Y15.545 E.00778
G1 X95.545 Y15.545 E.00778
G1 X95.545 Y15.795 E.00627
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X95.545 Y15.545 E-.16092
G1 X95.855 Y15.545 E-.19969
G1 X95.855 Y15.855 E-.19969
G1 X95.545 Y15.855 E-.19969
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 15/40
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
G17
G3 Z3.2 I1.217 J0 P1  F30000
; object ids of layer 15 start: 8,12,16
M624 BwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer15 end: 8,12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z3.4 F30000
G1 X114.002 Y8.498 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; OBJECT_ID: 8
; WIPE_START
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X107.495 Y8.622 Z3.4 F30000
G1 X34.49 Y18.49 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X28.91 Y18.49 E.17146
G1 X28.91 Y12.91 E.17146
G1 X34.49 Y12.91 E.17146
G1 X34.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X32.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.65 Y13.117 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X34.283 Y13.75 E.02749
G1 X34.283 Y14.283
G1 X33.117 Y13.117 E.05066
G1 X32.583 Y13.117
G1 X34.283 Y14.817 E.07384
G1 X34.283 Y15.35
G1 X32.05 Y13.117 E.09701
G1 X31.517 Y13.117
G1 X34.283 Y15.883 E.12018
G1 X34.283 Y16.416
G1 X30.984 Y13.117 E.14335
G1 X30.45 Y13.117
G1 X34.283 Y16.95 E.16653
G1 X34.283 Y17.483
G1 X29.917 Y13.117 E.1897
G1 X29.384 Y13.117
G1 X34.283 Y18.016 E.21287
G1 X34.016 Y18.283
G1 X29.117 Y13.384 E.21287
G1 X29.117 Y13.917
G1 X33.483 Y18.283 E.18969
G1 X32.949 Y18.283
G1 X29.117 Y14.451 E.16652
G1 X29.117 Y14.984
G1 X32.416 Y18.283 E.14335
G1 X31.883 Y18.283
G1 X29.117 Y15.517 E.12018
G1 X29.117 Y16.05
G1 X31.35 Y18.283 E.097
G1 X30.816 Y18.283
G1 X29.117 Y16.584 E.07383
G1 X29.117 Y17.117
G1 X30.283 Y18.283 E.05066
G1 X29.75 Y18.283
G1 X29.117 Y17.65 E.02748
; WIPE_START
M204 S10000
G1 X29.75 Y18.283 E-.3399
G1 X30.283 Y18.283 E-.20264
G1 X29.878 Y17.878 E-.21746
; WIPE_END
G1 E-.04 F1800
G1 X34.283 Y24.111 Z3.4 F30000
G1 X38.79 Y30.49 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
G1 F12000
M204 S5000
G1 X34.46 Y30.49 E.13305
G1 X34.46 Y27.669 E.08668
G1 X34.46 Y27.269 E.01229
G1 F9901.871
G1 X34.46 Y26.869 E.01229
G1 F3789.734
G1 X34.46 Y26.71 E.00489
G1 F2160
G1 X34.81 Y26.71 E.01075
G1 X34.81 Y22.831 E.11919
G1 F2536.674
G1 X34.81 Y22.79 E.00126
G1 F6983.831
G1 X34.46 Y22.79 E.01075
G1 F12000
G1 X34.46 Y22.49 E.00922
G1 X30.54 Y22.49 E.12045
G1 X30.54 Y22.79 E.00922
G1 F6983.831
G1 X30.19 Y22.79 E.01075
G1 F2536.674
G1 X30.19 Y22.831 E.00126
G1 F2160
G1 X30.19 Y26.71 E.11919
G1 X30.54 Y26.71 E.01075
G1 F3789.734
G1 X30.54 Y26.869 E.00489
G1 F9901.871
G1 X30.54 Y27.269 E.01229
G1 F12000
G1 X30.54 Y27.669 E.01229
G1 X30.54 Y30.49 E.08668
G1 X26.21 Y30.49 E.13305
G1 X26.21 Y21.91 E.26364
G1 X38.79 Y21.91 E.38655
G1 X38.79 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X36.79 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X38.54 Y23.029 Z3.4 F30000
G1 X38.583 Y22.849 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X37.851 Y22.117 E.03181
G1 X37.317 Y22.117
G1 X38.583 Y23.383 E.05498
G1 X38.583 Y23.916
G1 X36.784 Y22.117 E.07815
G1 X36.251 Y22.117
G1 X38.583 Y24.449 E.10132
G1 X38.583 Y24.982
G1 X35.718 Y22.117 E.1245
G1 X35.235 Y22.167
G1 X38.583 Y25.516 E.14549
G1 X38.583 Y26.049
G1 X35.235 Y22.701 E.14547
G1 X35.017 Y23.017
G1 X38.583 Y26.582 E.15493
G1 X38.583 Y27.115
G1 X35.017 Y23.55 E.15493
G1 X35.017 Y24.083
G1 X38.583 Y27.649 E.15493
G1 X38.583 Y28.182
G1 X35.017 Y24.617 E.15493
G1 X35.017 Y25.15
G1 X38.583 Y28.715 E.15493
G1 X38.583 Y29.248
G1 X35.017 Y25.683 E.15493
G1 X35.017 Y26.216
G1 X38.583 Y29.782 E.15493
G1 X38.55 Y30.283
G1 X35.017 Y26.75 E.15352
G1 X34.667 Y26.933
G1 X38.017 Y30.283 E.14556
G1 X37.484 Y30.283
G1 X34.667 Y27.466 E.12239
G1 X34.667 Y27.999
G1 X36.951 Y30.283 E.09922
G1 X36.417 Y30.283
G1 X34.667 Y28.533 E.07604
G1 X34.667 Y29.066
G1 X35.884 Y30.283 E.05287
G1 X35.351 Y30.283
G1 X34.667 Y29.599 E.0297
; WIPE_START
M204 S10000
G1 X35.351 Y30.283 E-.36726
G1 X35.884 Y30.283 E-.20264
G1 X35.53 Y29.929 E-.1901
; WIPE_END
G1 E-.04 F1800
G1 X34.831 Y22.594 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.39283
G1 F15000
G1 X34.831 Y22.281 E.00892
; LINE_WIDTH: 0.372987
G1 X34.787 Y22.261 E.0013
; LINE_WIDTH: 0.33238
G1 X34.743 Y22.241 E.00114
; LINE_WIDTH: 0.291772
G1 X34.7 Y22.22 E.00098
; LINE_WIDTH: 0.231085
G1 X34.656 Y22.2 E.00074
G1 X30.344 Y22.2 E.06612
; LINE_WIDTH: 0.251163
G1 X30.3 Y22.22 E.00082
; LINE_WIDTH: 0.291768
G1 X30.257 Y22.241 E.00098
; LINE_WIDTH: 0.332373
G1 X30.213 Y22.261 E.00114
; LINE_WIDTH: 0.390181
G1 X30.169 Y22.281 E.00136
G1 X30.169 Y22.594 E.00885
G1 X29.319 Y22.117 F30000
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X29.767 Y22.565 E.01947
G1 X29.983 Y23.315
G1 X28.785 Y22.117 E.05203
G1 X28.252 Y22.117
G1 X29.983 Y23.848 E.0752
G1 X29.983 Y24.381
G1 X27.719 Y22.117 E.09837
G1 X27.186 Y22.117
G1 X29.983 Y24.914 E.12155
G1 X29.983 Y25.448
G1 X26.652 Y22.117 E.14472
G1 X26.417 Y22.416
G1 X29.983 Y25.981 E.15493
G1 X29.983 Y26.514
G1 X26.417 Y22.949 E.15493
G1 X26.417 Y23.482
G1 X30.333 Y27.397 E.17014
G1 X30.333 Y27.931
G1 X26.417 Y24.016 E.17014
G1 X26.417 Y24.549
G1 X30.333 Y28.464 E.17014
G1 X30.333 Y28.997
G1 X26.417 Y25.082 E.17014
G1 X26.417 Y25.615
G1 X30.333 Y29.531 E.17014
G1 X30.333 Y30.064
G1 X26.417 Y26.149 E.17014
G1 X26.417 Y26.682
G1 X30.018 Y30.283 E.15647
G1 X29.485 Y30.283
G1 X26.417 Y27.215 E.1333
G1 X26.417 Y27.748
G1 X28.952 Y30.283 E.11013
G1 X28.418 Y30.283
G1 X26.417 Y28.282 E.08696
G1 X26.417 Y28.815
G1 X27.885 Y30.283 E.06378
G1 X27.352 Y30.283
G1 X26.417 Y29.348 E.04061
G1 X26.417 Y29.881
G1 X26.819 Y30.283 E.01744
; WIPE_START
M204 S10000
G1 X26.417 Y29.881 E-.21565
G1 X26.417 Y29.348 E-.20264
G1 X27.053 Y29.984 E-.34172
; WIPE_END
G1 E-.04 F1800
G1 X28.185 Y37.532 Z3.4 F30000
G1 X33.517 Y73.099 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
G1 F12000
M204 S5000
G1 X33.464 Y73.096 E.00163
G3 X33.464 Y68.301 I.232 J-2.397 E.21821
G1 X33.692 Y68.29 E.00703
G3 X33.936 Y73.096 I.004 J2.409 E.22527
G1 X33.577 Y73.098 E.01103
; WIPE_START
M204 S10000
G1 X33.464 Y73.096 E-.04295
M73 P92 R2
G1 X33 Y73.007 E-.17946
G1 X32.564 Y72.826 E-.17962
G1 X32.171 Y72.563 E-.17957
G1 X31.839 Y72.231 E-.17841
; WIPE_END
G1 E-.04 F1800
G1 X37.99 Y74.99 Z3.4 F30000
G1 Z3
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X29.41 Y74.99 E.26364
G1 X29.41 Y66.41 E.26364
G1 X37.99 Y66.41 E.26364
G1 X37.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X35.99 Y74.944 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X37.749 Y67.517 Z3.4 F30000
G1 X37.783 Y67.376 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X37.024 Y66.617 E.03297
G1 X36.491 Y66.617
G1 X37.783 Y67.909 E.05615
G1 X37.783 Y68.443
G1 X35.957 Y66.617 E.07932
G1 X35.424 Y66.617
G1 X37.783 Y68.976 E.10249
G1 X37.783 Y69.509
G1 X34.891 Y66.617 E.12566
G1 X34.358 Y66.617
G1 X37.783 Y70.042 E.14884
G1 X37.783 Y70.576
G1 X33.824 Y66.617 E.17201
G1 X33.291 Y66.617
G1 X35.326 Y68.652 E.08841
G1 X34.303 Y68.163
G1 X32.758 Y66.617 E.06716
G1 X32.224 Y66.617
G1 X33.701 Y68.094 E.06416
G1 X33.214 Y68.14
G1 X31.691 Y66.617 E.06615
G1 X31.158 Y66.617
G1 X32.795 Y68.254 E.07113
G1 X32.425 Y68.418
G1 X30.625 Y66.617 E.07823
G1 X30.091 Y66.617
G1 X32.105 Y68.631 E.08751
G1 X31.828 Y68.887
G1 X29.617 Y66.677 E.09605
G1 X29.617 Y67.21
G1 X31.584 Y69.176 E.08545
G1 X31.376 Y69.501
G1 X29.617 Y67.743 E.07641
G1 X29.617 Y68.276
G1 X31.22 Y69.878 E.06962
G1 X31.12 Y70.312
G1 X29.617 Y68.81 E.0653
G1 X29.617 Y69.343
G1 X31.094 Y70.819 E.06417
G1 X31.192 Y71.451
G1 X29.617 Y69.876 E.06844
; WIPE_START
M204 S10000
G1 X31.032 Y71.29 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.748 Y69.074 Z3.4 F30000
G1 Z3
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X37.783 Y71.109 E.08841
G1 X37.783 Y71.642
G1 X36.237 Y70.097 E.06716
G1 X36.306 Y70.699
G1 X37.783 Y72.176 E.06416
G1 X37.783 Y72.709
G1 X36.26 Y71.186 E.06615
G1 X36.146 Y71.605
G1 X37.783 Y73.242 E.07113
G1 X37.783 Y73.775
G1 X35.982 Y71.975 E.07823
G1 X35.769 Y72.295
G1 X37.783 Y74.309 E.08751
G1 X37.723 Y74.783
G1 X35.513 Y72.572 E.09605
G1 X35.224 Y72.816
G1 X37.19 Y74.783 E.08545
G1 X36.657 Y74.783
G1 X34.899 Y73.024 E.07641
G1 X34.522 Y73.18
G1 X36.124 Y74.783 E.06962
G1 X35.59 Y74.783
G1 X34.088 Y73.28 E.0653
G1 X33.581 Y73.306
G1 X35.057 Y74.783 E.06417
G1 X34.524 Y74.783
G1 X32.949 Y73.208 E.06844
; WIPE_START
M204 S10000
G1 X34.363 Y74.622 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.991 Y74.783 Z3.4 F30000
G1 Z3
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X29.617 Y70.409 E.19004
G1 X29.617 Y70.943
G1 X33.457 Y74.783 E.16687
G1 X32.924 Y74.783
G1 X29.617 Y71.476 E.14369
G1 X29.617 Y72.009
G1 X32.391 Y74.783 E.12052
G1 X31.858 Y74.783
G1 X29.617 Y72.542 E.09735
G1 X29.617 Y73.076
G1 X31.324 Y74.783 E.07418
G1 X30.791 Y74.783
G1 X29.617 Y73.609 E.051
G1 X29.617 Y74.142
G1 X30.258 Y74.783 E.02783
; WIPE_START
M204 S10000
G1 X29.617 Y74.142 E-.34419
G1 X29.617 Y73.609 E-.20264
G1 X30.014 Y74.006 E-.21317
; WIPE_END
G1 E-.04 F1800
G1 X32.886 Y73.271 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.188584
G1 F15000
G1 X32.771 Y73.194 E.00165
; LINE_WIDTH: 0.148421
G1 X32.655 Y73.117 E.00119
; LINE_WIDTH: 0.108257
G1 X32.54 Y73.04 E.00074
; WIPE_START
G1 X32.655 Y73.117 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.303 Y70.031 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.178615
G1 F15000
G1 X36.244 Y69.922 E.00137
; LINE_WIDTH: 0.144901
G1 X36.184 Y69.832 E.0009
; LINE_WIDTH: 0.107084
G1 X36.123 Y69.742 E.00057
G1 X35.811 Y69.012 F30000
; LINE_WIDTH: 0.241791
G1 F15000
G1 X35.388 Y68.589 E.00969
; WIPE_START
G1 X35.811 Y69.012 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.002 Y68.195 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.108883
G1 F15000
G1 X32.928 Y68.177 E.00041
G1 X32.838 Y68.237 E.00058
; WIPE_START
G1 X32.928 Y68.177 E-.44696
G1 X33.002 Y68.195 E-.31304
; WIPE_END
G1 E-.04 F1800
G1 X31.36 Y71.86 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.108253
G1 F15000
G1 X31.283 Y71.745 E.00074
; LINE_WIDTH: 0.148408
G1 X31.206 Y71.629 E.00119
; LINE_WIDTH: 0.188563
G1 X31.129 Y71.514 E.00165
; WIPE_START
G1 X31.206 Y71.629 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X38.501 Y73.875 Z3.4 F30000
G1 X66.49 Y82.49 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X60.91 Y82.49 E.17146
G1 X60.91 Y76.91 E.17146
G1 X66.49 Y76.91 E.17146
G1 X66.49 Y82.43 E.16961
; WIPE_START
M204 S10000
G1 X64.49 Y82.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X65.655 Y77.117 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X66.283 Y77.745 E.02729
G1 X66.283 Y78.279
G1 X65.121 Y77.117 E.05047
G1 X64.588 Y77.117
G1 X66.283 Y78.812 E.07364
G1 X66.283 Y79.345
G1 X64.055 Y77.117 E.09681
G1 X63.522 Y77.117
G1 X66.283 Y79.878 E.11998
G1 X66.283 Y80.412
G1 X62.988 Y77.117 E.14316
G1 X62.455 Y77.117
G1 X66.283 Y80.945 E.16633
G1 X66.283 Y81.478
G1 X61.922 Y77.117 E.1895
G1 X61.389 Y77.117
G1 X66.283 Y82.012 E.21267
G1 X66.02 Y82.283
G1 X61.117 Y77.38 E.21306
G1 X61.117 Y77.913
G1 X65.487 Y82.283 E.18989
G1 X64.954 Y82.283
G1 X61.117 Y78.446 E.16672
G1 X61.117 Y78.979
G1 X64.421 Y82.283 E.14355
G1 X63.887 Y82.283
G1 X61.117 Y79.513 E.12037
G1 X61.117 Y80.046
G1 X63.354 Y82.283 E.0972
G1 X62.821 Y82.283
G1 X61.117 Y80.579 E.07403
G1 X61.117 Y81.112
G1 X62.288 Y82.283 E.05086
G1 X61.754 Y82.283
G1 X61.117 Y81.646 E.02768
; WIPE_START
M204 S10000
G1 X61.754 Y82.283 E-.34236
G1 X62.288 Y82.283 E-.20264
G1 X61.888 Y81.883 E-.21501
; WIPE_END
G1 E-.04 F1800
G1 X69.236 Y79.818 Z3.4 F30000
G1 X93.11 Y73.11 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
G1 F12000
M204 S5000
G1 X84.29 Y73.11 E.27101
G1 X84.29 Y68.29 E.1481
G1 X93.11 Y68.29 E.27101
G1 X93.11 Y73.05 E.14626
; WIPE_START
M204 S10000
G1 X91.11 Y73.064 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.99 Y74.99 Z3.4 F30000
G1 Z3
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X83.41 Y74.99 E.32509
G1 X83.41 Y66.41 E.26364
G1 X93.99 Y66.41 E.32509
G1 X93.99 Y74.93 E.2618
; WIPE_START
M204 S10000
G1 X91.99 Y74.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.55 Y73.306 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X93.55 Y68.094 E.20723
; WIPE_START
G1 X93.55 Y70.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X93.016 Y66.617 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X93.783 Y67.384 E.03332
G1 X93.752 Y67.887
G1 X92.483 Y66.617 E.05516
G1 X91.949 Y66.617
G1 X93.219 Y67.887 E.05516
G1 X92.881 Y68.083
G1 X91.416 Y66.617 E.06367
G1 X90.883 Y66.617
G1 X92.348 Y68.083 E.06367
G1 X91.815 Y68.083
G1 X90.35 Y66.617 E.06367
G1 X89.816 Y66.617
G1 X91.282 Y68.083 E.06367
G1 X90.748 Y68.083
G1 X89.283 Y66.617 E.06367
G1 X88.75 Y66.617
G1 X90.215 Y68.083 E.06367
G1 X89.682 Y68.083
G1 X88.217 Y66.617 E.06367
G1 X87.683 Y66.617
G1 X89.149 Y68.083 E.06367
G1 X88.615 Y68.083
G1 X87.15 Y66.617 E.06367
G1 X86.617 Y66.617
G1 X88.082 Y68.083 E.06367
G1 X87.549 Y68.083
G1 X86.083 Y66.617 E.06367
G1 X85.55 Y66.617
G1 X87.015 Y68.083 E.06367
G1 X86.482 Y68.083
G1 X85.017 Y66.617 E.06367
G1 X84.484 Y66.617
G1 X85.949 Y68.083 E.06367
G1 X85.416 Y68.083
G1 X83.95 Y66.617 E.06367
G1 X83.617 Y66.818
G1 X84.882 Y68.083 E.05497
G1 X84.153 Y67.887
G1 X83.617 Y67.351 E.02329
M204 S10000
G1 X83.85 Y68.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53086
G1 F12911.423
G1 X83.85 Y73.306 E.20723
; WIPE_START
G1 X83.85 Y71.306 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X91.296 Y72.982 Z3.4 F30000
G1 X92.783 Y73.317 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X93.783 Y74.317 E.04342
G1 X93.715 Y74.783
G1 X92.25 Y73.317 E.06367
G1 X91.717 Y73.317
G1 X93.182 Y74.783 E.06367
G1 X92.649 Y74.783
G1 X91.184 Y73.317 E.06367
G1 X90.65 Y73.317
G1 X92.116 Y74.783 E.06367
G1 X91.582 Y74.783
G1 X90.117 Y73.317 E.06367
G1 X89.584 Y73.317
G1 X91.049 Y74.783 E.06367
G1 X90.516 Y74.783
G1 X89.051 Y73.317 E.06367
G1 X88.517 Y73.317
G1 X89.983 Y74.783 E.06367
G1 X89.449 Y74.783
G1 X87.984 Y73.317 E.06367
G1 X87.451 Y73.317
G1 X88.916 Y74.783 E.06367
G1 X88.383 Y74.783
G1 X86.918 Y73.317 E.06367
G1 X86.384 Y73.317
G1 X87.85 Y74.783 E.06367
G1 X87.316 Y74.783
G1 X85.851 Y73.317 E.06367
G1 X85.318 Y73.317
G1 X86.783 Y74.783 E.06367
G1 X86.25 Y74.783
G1 X84.785 Y73.317 E.06367
G1 X84.323 Y73.389
G1 X85.717 Y74.783 E.06056
G1 X85.183 Y74.783
G1 X83.914 Y73.513 E.05516
G1 X83.617 Y73.75
G1 X84.65 Y74.783 E.04488
G1 X84.117 Y74.783
G1 X83.617 Y74.283 E.0217
; WIPE_START
M204 S10000
G1 X84.117 Y74.783 E-.26841
G1 X84.65 Y74.783 E-.20264
G1 X84.112 Y74.245 E-.28896
; WIPE_END
G1 E-.04 F1800
G1 X86.887 Y67.135 Z3.4 F30000
G1 X101.19 Y30.49 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
G1 F12000
M204 S5000
G1 X96.86 Y30.49 E.13305
G1 X96.86 Y27.669 E.08668
G1 X96.86 Y27.269 E.01229
G1 F9901.871
G1 X96.86 Y26.869 E.01229
G1 F3789.734
G1 X96.86 Y26.71 E.00489
G1 F2160
G1 X97.21 Y26.71 E.01075
G1 X97.21 Y22.831 E.11919
G1 F2536.674
G1 X97.21 Y22.79 E.00126
G1 F6983.831
G1 X96.86 Y22.79 E.01075
G1 F12000
G1 X96.86 Y22.49 E.00922
G1 X92.94 Y22.49 E.12045
G1 X92.94 Y22.79 E.00922
G1 F6983.831
G1 X92.59 Y22.79 E.01075
G1 F2536.674
G1 X92.59 Y22.831 E.00126
G1 F2160
G1 X92.59 Y26.71 E.11919
G1 X92.94 Y26.71 E.01075
G1 F3789.734
G1 X92.94 Y26.869 E.00489
G1 F9901.871
G1 X92.94 Y27.269 E.01229
G1 F12000
G1 X92.94 Y27.669 E.01229
G1 X92.94 Y30.49 E.08668
G1 X88.61 Y30.49 E.13305
G1 X88.61 Y21.91 E.26364
G1 X101.19 Y21.91 E.38655
G1 X101.19 Y30.43 E.2618
; WIPE_START
M204 S10000
G1 X99.19 Y30.458 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X100.942 Y23.029 Z3.4 F30000
G1 X100.983 Y22.858 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X100.242 Y22.117 E.03219
G1 X99.709 Y22.117
G1 X100.983 Y23.391 E.05536
G1 X100.983 Y23.925
G1 X99.175 Y22.117 E.07854
G1 X98.642 Y22.117
G1 X100.983 Y24.458 E.10171
G1 X100.983 Y24.991
G1 X98.109 Y22.117 E.12488
G1 X97.635 Y22.176
G1 X100.983 Y25.524 E.14549
G1 X100.983 Y26.058
G1 X97.635 Y22.71 E.14547
G1 X97.417 Y23.026
G1 X100.983 Y26.591 E.15493
G1 X100.983 Y27.124
G1 X97.417 Y23.559 E.15493
G1 X97.417 Y24.092
G1 X100.983 Y27.658 E.15493
G1 X100.983 Y28.191
G1 X97.417 Y24.626 E.15493
G1 X97.417 Y25.159
G1 X100.983 Y28.724 E.15493
G1 X100.983 Y29.257
G1 X97.417 Y25.692 E.15493
G1 X97.417 Y26.225
G1 X100.983 Y29.791 E.15493
G1 X100.941 Y30.283
G1 X97.417 Y26.759 E.15314
G1 X97.067 Y26.942
G1 X100.408 Y30.283 E.14517
G1 X99.875 Y30.283
G1 X97.067 Y27.475 E.122
G1 X97.067 Y28.008
G1 X99.342 Y30.283 E.09883
G1 X98.808 Y30.283
G1 X97.067 Y28.542 E.07566
G1 X97.067 Y29.075
G1 X98.275 Y30.283 E.05248
G1 X97.742 Y30.283
G1 X97.067 Y29.608 E.02931
; WIPE_START
M204 S10000
G1 X97.742 Y30.283 E-.36249
G1 X98.275 Y30.283 E-.20264
G1 X97.913 Y29.92 E-.19487
; WIPE_END
G1 E-.04 F1800
G1 X97.231 Y22.594 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.39283
G1 F15000
G1 X97.231 Y22.281 E.00892
; LINE_WIDTH: 0.372987
G1 X97.187 Y22.261 E.0013
; LINE_WIDTH: 0.33238
G1 X97.143 Y22.241 E.00114
; LINE_WIDTH: 0.291772
G1 X97.1 Y22.22 E.00098
; LINE_WIDTH: 0.231085
G1 X97.056 Y22.2 E.00074
G1 X92.744 Y22.2 E.06612
; LINE_WIDTH: 0.251163
G1 X92.7 Y22.22 E.00082
; LINE_WIDTH: 0.291768
G1 X92.657 Y22.241 E.00098
; LINE_WIDTH: 0.332373
G1 X92.613 Y22.261 E.00114
; LINE_WIDTH: 0.390181
G1 X92.569 Y22.281 E.00136
G1 X92.569 Y22.594 E.00885
G1 X91.71 Y22.117 F30000
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X92.167 Y22.574 E.01985
G1 X92.383 Y23.324
G1 X91.176 Y22.117 E.05242
G1 X90.643 Y22.117
G1 X92.383 Y23.857 E.07559
G1 X92.383 Y24.39
G1 X90.11 Y22.117 E.09876
G1 X89.577 Y22.117
G1 X92.383 Y24.923 E.12193
G1 X92.383 Y25.457
G1 X89.043 Y22.117 E.14511
G1 X88.817 Y22.425
G1 X92.383 Y25.99 E.15493
G1 X92.383 Y26.523
G1 X88.817 Y22.958 E.15493
G1 X88.817 Y23.491
G1 X92.733 Y27.406 E.17014
G1 X92.733 Y27.94
G1 X88.817 Y24.024 E.17014
G1 X88.817 Y24.558
G1 X92.733 Y28.473 E.17014
G1 X92.733 Y29.006
G1 X88.817 Y25.091 E.17014
G1 X88.817 Y25.624
G1 X92.733 Y29.539 E.17014
G1 X92.733 Y30.073
G1 X88.817 Y26.157 E.17014
G1 X88.817 Y26.691
G1 X92.409 Y30.283 E.15609
G1 X91.876 Y30.283
G1 X88.817 Y27.224 E.13291
G1 X88.817 Y27.757
G1 X91.343 Y30.283 E.10974
G1 X90.81 Y30.283
G1 X88.817 Y28.29 E.08657
G1 X88.817 Y28.824
G1 X90.276 Y30.283 E.0634
G1 X89.743 Y30.283
G1 X88.817 Y29.357 E.04022
G1 X88.817 Y29.89
G1 X89.21 Y30.283 E.01705
; WIPE_START
M204 S10000
G1 X88.817 Y29.89 E-.21088
G1 X88.817 Y29.357 E-.20264
G1 X89.462 Y30.002 E-.34649
; WIPE_END
G1 E-.04 F1800
G1 X94.172 Y23.996 Z3.4 F30000
G1 X98.49 Y18.49 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
G1 F12000
M204 S5000
G1 X92.91 Y18.49 E.17146
G1 X92.91 Y12.91 E.17146
G1 X98.49 Y12.91 E.17146
G1 X98.49 Y18.43 E.16961
; WIPE_START
M204 S10000
G1 X96.49 Y18.452 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X97.641 Y13.117 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X98.283 Y13.759 E.02789
G1 X98.283 Y14.292
G1 X97.108 Y13.117 E.05106
G1 X96.574 Y13.117
G1 X98.283 Y14.826 E.07423
G1 X98.283 Y15.359
G1 X96.041 Y13.117 E.0974
G1 X95.508 Y13.117
G1 X98.283 Y15.892 E.12058
G1 X98.283 Y16.425
G1 X94.975 Y13.117 E.14375
G1 X94.441 Y13.117
G1 X98.283 Y16.959 E.16692
G1 X98.283 Y17.492
G1 X93.908 Y13.117 E.19009
G1 X93.375 Y13.117
G1 X98.283 Y18.025 E.21327
G1 X98.007 Y18.283
G1 X93.117 Y13.393 E.21247
G1 X93.117 Y13.926
G1 X97.474 Y18.283 E.1893
G1 X96.94 Y18.283
G1 X93.117 Y14.46 E.16612
G1 X93.117 Y14.993
G1 X96.407 Y18.283 E.14295
G1 X95.874 Y18.283
G1 X93.117 Y15.526 E.11978
G1 X93.117 Y16.059
G1 X95.341 Y18.283 E.09661
G1 X94.807 Y18.283
G1 X93.117 Y16.593 E.07343
G1 X93.117 Y17.126
G1 X94.274 Y18.283 E.05026
G1 X93.741 Y18.283
G1 X93.117 Y17.659 E.02709
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12000
M204 S10000
G1 X93.741 Y18.283 E-.33501
G1 X94.274 Y18.283 E-.20264
G1 X93.86 Y17.869 E-.22235
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 16/40
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
G17
G3 Z3.4 I1.217 J0 P1  F30000
; object ids of layer 16 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer16 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3144
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P93 R2
G1 F3144
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3144
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3144
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z3.6 F30000
G1 X114.002 Y8.498 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3144
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3144
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3144
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3144
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 17/40
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
G17
G3 Z3.6 I1.217 J0 P1  F30000
; object ids of layer 17 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer17 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z3.8 F30000
G1 X114.002 Y8.498 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 18/40
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
G17
G3 Z3.8 I1.217 J0 P1  F30000
; object ids of layer 18 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer18 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z4 F30000
G1 X114.002 Y8.498 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 19/40
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
G17
G3 Z4 I1.217 J0 P1  F30000
; object ids of layer 19 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer19 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z4.2 F30000
G1 X114.002 Y8.498 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 20/40
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
G17
G3 Z4.2 I1.217 J0 P1  F30000
; object ids of layer 20 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer20 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
M73 P94 R2
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z4.4 F30000
G1 X114.002 Y8.498 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
M73 P94 R1
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 4.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 21/40
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
G17
G3 Z4.4 I1.217 J0 P1  F30000
; object ids of layer 21 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer21 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z4.6 F30000
G1 X114.002 Y8.498 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 4.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 22/40
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
G17
G3 Z4.6 I1.217 J0 P1  F30000
; object ids of layer 22 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer22 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z4.8 F30000
G1 X114.002 Y8.498 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 4.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 23/40
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
G17
G3 Z4.8 I1.217 J0 P1  F30000
; object ids of layer 23 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer23 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z5 F30000
G1 X114.002 Y8.498 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 4.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 24/40
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
G17
G3 Z5 I1.217 J0 P1  F30000
; object ids of layer 24 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer24 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.498
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X141.002 Y6.702 E.05957
G1 X142.798 Y6.702 E.05957
G1 X142.798 Y7.402 E.02322
G1 X160.798 Y7.402 E.59709
G1 X160.798 Y7.798 E.01313
G1 X142.798 Y7.798 E.59709
G1 X142.798 Y8.498 E.02322
G1 X141.062 Y8.498 E.05758
G1 X140.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
G1 X140.61 Y6.31 E.07928
G1 X143.19 Y6.31 E.07928
G1 X143.19 Y7.01 E.02151
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.89 E.02151
G1 X140.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X140.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.406 Y7.6 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X142.406 Y7.094 E.01554
G1 X141.394 Y7.094 E.03109
G1 X141.394 Y8.106 E.03109
G1 X142.406 Y8.106 E.03109
G1 X142.406 Y7.66 E.0137
G1 X142.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X142.059 Y7.441 E.0041
G1 X141.741 Y7.441 E.00821
G1 X141.741 Y7.759 E.00821
G1 X142.059 Y7.759 E.00821
G1 X142.059 Y7.66 E.00255
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.059 Y7.759 E-.062
G1 X141.741 Y7.759 E-.19943
G1 X141.741 Y7.441 E-.19943
G1 X142.059 Y7.441 E-.19943
G1 X142.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.43 Y7.844 Z5.2 F30000
G1 X114.002 Y8.498 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3102
G1 X114.002 Y6.702 E.05957
G1 X115.798 Y6.702 E.05957
G1 X115.798 Y7.402 E.02322
G1 X133.798 Y7.402 E.59709
G1 X133.798 Y7.798 E.01313
G1 X115.798 Y7.798 E.59709
G1 X115.798 Y8.498 E.02322
G1 X114.062 Y8.498 E.05758
G1 X113.61 Y8.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3102
M204 S5000
M73 P95 R1
G1 X113.61 Y6.31 E.07928
G1 X116.19 Y6.31 E.07928
G1 X116.19 Y7.01 E.02151
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.89 E.02151
G1 X113.67 Y8.89 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X113.624 Y6.891 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.406 Y7.6 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3102
G1 X115.406 Y7.094 E.01554
G1 X114.394 Y7.094 E.03109
G1 X114.394 Y8.106 E.03109
G1 X115.406 Y8.106 E.03109
G1 X115.406 Y7.66 E.0137
G1 X115.059 Y7.6 F30000
; LINE_WIDTH: 0.36026
G1 F3102
G1 X115.059 Y7.441 E.0041
G1 X114.741 Y7.441 E.00821
G1 X114.741 Y7.759 E.00821
G1 X115.059 Y7.759 E.00821
G1 X115.059 Y7.66 E.00255
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.059 Y7.759 E-.062
G1 X114.741 Y7.759 E-.19943
G1 X114.741 Y7.441 E-.19943
G1 X115.059 Y7.441 E-.19943
G1 X115.059 Y7.6 E-.09972
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 25/40
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
G17
G3 Z5.2 I1.217 J0 P1  F30000
; object ids of layer 25 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer25 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.698
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4217
G1 X141.002 Y6.502 E.07284
G1 X142.422 Y6.502 E.04711
G1 X142.422 Y8.698 E.07284
G1 X141.062 Y8.698 E.04512
G1 X140.61 Y8.931 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4217
M204 S5000
G1 X140.61 Y7.069 E.05721
G1 X140.61 Y6.669 E.01229
G1 X140.61 Y6.269 E.01229
G1 F3789.734
G1 X140.61 Y6.11 E.00489
G1 F2160
G1 X143.19 Y6.11 E.07928
G1 F3789.734
G1 X143.19 Y6.269 E.00489
G1 F4217
G1 X143.19 Y6.669 E.01229
G1 X143.19 Y7.01 E.01048
G1 X161.19 Y7.01 E.55309
G1 X161.19 Y8.19 E.03626
G1 X143.19 Y8.19 E.55309
G1 X143.19 Y8.531 E.01048
G1 X143.19 Y8.931 E.01229
G1 F3789.734
G1 X143.19 Y9.09 E.00489
G1 F2160
G1 X140.61 Y9.09 E.07928
G1 F3121.313
G1 X140.61 Y8.991 E.00304
; WIPE_START
M204 S10000
G1 X140.61 Y7.069 E-.73036
G1 X140.61 Y6.991 E-.02964
; WIPE_END
G1 E-.04 F1800
G1 X141.965 Y7.212 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.54947
G1 F4217
G1 X141.965 Y6.959 E.01045
G1 X141.459 Y6.959 E.02091
G1 X141.459 Y8.241 E.05293
G1 X141.965 Y8.241 E.02091
G1 X141.965 Y7.272 E.04
; WIPE_START
G1 F12437.074
G1 X141.965 Y8.241 E-.36822
G1 X141.459 Y8.241 E-.19249
G1 X141.459 Y7.717 E-.19929
; WIPE_END
G1 E-.04 F1800
G1 X149.089 Y7.515 Z5.4 F30000
G1 X160.383 Y7.217 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F4217
M204 S2000
G1 X160.983 Y7.817 E.02607
G1 X160.615 Y7.983
G1 X159.849 Y7.217 E.03325
G1 X159.316 Y7.217
G1 X160.081 Y7.983 E.03325
G1 X159.548 Y7.983
G1 X158.783 Y7.217 E.03325
G1 X158.25 Y7.217
G1 X159.015 Y7.983 E.03325
G1 X158.482 Y7.983
G1 X157.716 Y7.217 E.03325
G1 X157.183 Y7.217
G1 X157.948 Y7.983 E.03325
G1 X157.415 Y7.983
G1 X156.65 Y7.217 E.03325
G1 X156.117 Y7.217
G1 X156.882 Y7.983 E.03325
G1 X156.349 Y7.983
G1 X155.583 Y7.217 E.03325
G1 X155.05 Y7.217
G1 X155.815 Y7.983 E.03325
G1 X155.282 Y7.983
G1 X154.517 Y7.217 E.03325
G1 X153.983 Y7.217
G1 X154.749 Y7.983 E.03325
G1 X154.215 Y7.983
G1 X153.45 Y7.217 E.03325
G1 X152.917 Y7.217
G1 X153.682 Y7.983 E.03325
G1 X153.149 Y7.983
G1 X152.384 Y7.217 E.03325
G1 X151.85 Y7.217
G1 X152.616 Y7.983 E.03325
G1 X152.082 Y7.983
G1 X151.317 Y7.217 E.03325
G1 X150.784 Y7.217
G1 X151.549 Y7.983 E.03325
G1 X151.016 Y7.983
G1 X150.251 Y7.217 E.03325
G1 X149.717 Y7.217
G1 X150.483 Y7.983 E.03325
G1 X149.949 Y7.983
G1 X149.184 Y7.217 E.03325
G1 X148.651 Y7.217
G1 X149.416 Y7.983 E.03325
G1 X148.883 Y7.983
G1 X148.118 Y7.217 E.03325
G1 X147.584 Y7.217
G1 X148.35 Y7.983 E.03325
G1 X147.816 Y7.983
G1 X147.051 Y7.217 E.03325
G1 X146.518 Y7.217
G1 X147.283 Y7.983 E.03325
G1 X146.75 Y7.983
G1 X145.985 Y7.217 E.03325
G1 X145.451 Y7.217
G1 X146.217 Y7.983 E.03325
G1 X145.683 Y7.983
G1 X144.918 Y7.217 E.03325
G1 X144.385 Y7.217
G1 X145.15 Y7.983 E.03325
G1 X144.617 Y7.983
G1 X143.852 Y7.217 E.03325
G1 X143.318 Y7.217
G1 X144.084 Y7.983 E.03325
G1 X143.55 Y7.983
G1 X142.785 Y7.217 E.03325
G1 X142.645 Y7.61
G1 X143.017 Y7.983 E.01618
; OBJECT_ID: 12
; WIPE_START
G1 F12000
M204 S10000
G1 X142.645 Y7.61 E-.2001
G1 X142.785 Y7.217 E-.15854
G1 X143.532 Y7.964 E-.40136
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.902 Y8.154 Z5.4 F30000
G1 X114.002 Y8.698 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4217
G1 X114.002 Y6.502 E.07284
G1 X115.422 Y6.502 E.04711
G1 X115.422 Y8.698 E.07284
G1 X114.062 Y8.698 E.04512
G1 X113.61 Y8.931 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4217
M204 S5000
G1 X113.61 Y7.069 E.05721
G1 X113.61 Y6.669 E.01229
G1 X113.61 Y6.269 E.01229
G1 F3789.734
G1 X113.61 Y6.11 E.00489
G1 F2160
G1 X116.19 Y6.11 E.07928
G1 F3789.734
G1 X116.19 Y6.269 E.00489
G1 F4217
G1 X116.19 Y6.669 E.01229
G1 X116.19 Y7.01 E.01048
G1 X134.19 Y7.01 E.55309
G1 X134.19 Y8.19 E.03626
G1 X116.19 Y8.19 E.55309
G1 X116.19 Y8.531 E.01048
G1 X116.19 Y8.931 E.01229
G1 F3789.734
G1 X116.19 Y9.09 E.00489
G1 F2160
G1 X113.61 Y9.09 E.07928
G1 F3121.313
G1 X113.61 Y8.991 E.00304
; WIPE_START
M204 S10000
G1 X113.61 Y7.069 E-.73036
G1 X113.61 Y6.991 E-.02964
; WIPE_END
G1 E-.04 F1800
G1 X114.965 Y7.212 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.54947
G1 F4217
G1 X114.965 Y6.959 E.01045
G1 X114.459 Y6.959 E.02091
G1 X114.459 Y8.241 E.05293
G1 X114.965 Y8.241 E.02091
G1 X114.965 Y7.272 E.04
; WIPE_START
G1 F12437.074
G1 X114.965 Y8.241 E-.36822
G1 X114.459 Y8.241 E-.19249
G1 X114.459 Y7.717 E-.19929
; WIPE_END
G1 E-.04 F1800
G1 X122.089 Y7.515 Z5.4 F30000
G1 X133.383 Y7.217 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F4217
M204 S2000
G1 X133.983 Y7.817 E.02607
G1 X133.615 Y7.983
G1 X132.849 Y7.217 E.03325
G1 X132.316 Y7.217
G1 X133.081 Y7.983 E.03325
G1 X132.548 Y7.983
G1 X131.783 Y7.217 E.03325
G1 X131.25 Y7.217
G1 X132.015 Y7.983 E.03325
G1 X131.482 Y7.983
G1 X130.716 Y7.217 E.03325
G1 X130.183 Y7.217
G1 X130.948 Y7.983 E.03325
G1 X130.415 Y7.983
G1 X129.65 Y7.217 E.03325
G1 X129.117 Y7.217
G1 X129.882 Y7.983 E.03325
G1 X129.349 Y7.983
G1 X128.583 Y7.217 E.03325
G1 X128.05 Y7.217
G1 X128.815 Y7.983 E.03325
G1 X128.282 Y7.983
G1 X127.517 Y7.217 E.03325
G1 X126.983 Y7.217
G1 X127.749 Y7.983 E.03325
G1 X127.215 Y7.983
G1 X126.45 Y7.217 E.03325
G1 X125.917 Y7.217
G1 X126.682 Y7.983 E.03325
G1 X126.149 Y7.983
G1 X125.384 Y7.217 E.03325
G1 X124.85 Y7.217
G1 X125.616 Y7.983 E.03325
G1 X125.082 Y7.983
G1 X124.317 Y7.217 E.03325
G1 X123.784 Y7.217
G1 X124.549 Y7.983 E.03325
G1 X124.016 Y7.983
G1 X123.251 Y7.217 E.03325
G1 X122.717 Y7.217
G1 X123.483 Y7.983 E.03325
G1 X122.949 Y7.983
G1 X122.184 Y7.217 E.03325
G1 X121.651 Y7.217
G1 X122.416 Y7.983 E.03325
G1 X121.883 Y7.983
G1 X121.118 Y7.217 E.03325
G1 X120.584 Y7.217
G1 X121.35 Y7.983 E.03325
G1 X120.816 Y7.983
G1 X120.051 Y7.217 E.03325
G1 X119.518 Y7.217
G1 X120.283 Y7.983 E.03325
G1 X119.75 Y7.983
G1 X118.985 Y7.217 E.03325
G1 X118.451 Y7.217
G1 X119.217 Y7.983 E.03325
G1 X118.683 Y7.983
G1 X117.918 Y7.217 E.03325
G1 X117.385 Y7.217
G1 X118.15 Y7.983 E.03325
G1 X117.617 Y7.983
G1 X116.852 Y7.217 E.03325
G1 X116.318 Y7.217
G1 X117.084 Y7.983 E.03325
G1 X116.55 Y7.983
G1 X115.785 Y7.217 E.03325
G1 X115.645 Y7.61
G1 X116.017 Y7.983 E.01618
; CHANGE_LAYER
; Z_HEIGHT: 5.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12000
M204 S10000
G1 X115.645 Y7.61 E-.2001
G1 X115.785 Y7.217 E-.15854
G1 X116.532 Y7.964 E-.40136
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 26/40
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
G17
G3 Z5.4 I1.217 J0 P1  F30000
; object ids of layer 26 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer26 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y8.898
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X141.002 Y6.302 E.08611
G1 X142.898 Y6.302 E.06289
G1 X142.898 Y8.898 E.08611
G1 X141.062 Y8.898 E.0609
G1 X140.61 Y9.131 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X140.61 Y6.869 E.0695
G1 X140.61 Y6.469 E.01229
G1 X140.61 Y6.069 E.01229
G1 X140.61 Y5.91 E.00489
G1 X143.29 Y5.91 E.08235
G1 X143.29 Y6.31 E.01229
G1 X143.29 Y6.71 E.01229
G1 X143.29 Y6.969 E.00796
G1 X143.29 Y7.369 E.01229
G1 X143.29 Y7.831 E.0142
G1 X143.29 Y8.231 E.01229
G1 X143.29 Y8.49 E.00796
G1 X143.29 Y8.89 E.01229
G1 X143.29 Y9.29 E.01229
G1 X140.61 Y9.29 E.08235
G1 X140.61 Y9.191 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y7.191 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.506 Y7.25 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X142.506 Y6.694 E.01708
G1 X141.394 Y6.694 E.03416
G1 X141.394 Y8.506 E.05567
G1 X142.506 Y8.506 E.03416
G1 X142.506 Y7.31 E.03675
G1 X142.134 Y7.25 F30000
; LINE_WIDTH: 0.41026
G1 F1200
G1 X142.134 Y7.066 E.0055
G1 X141.766 Y7.066 E.011
G1 X141.766 Y8.134 E.03195
G1 X142.134 Y8.134 E.011
G1 X142.134 Y7.31 E.02466
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.134 Y8.134 E-.313
G1 X141.766 Y8.134 E-.13959
G1 X141.766 Y7.325 E-.30741
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.146 Y7.756 Z5.6 F30000
G1 X114.002 Y8.898 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X114.002 Y6.302 E.08611
G1 X115.898 Y6.302 E.06289
G1 X115.898 Y8.898 E.08611
G1 X114.062 Y8.898 E.0609
G1 X113.61 Y9.131 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X113.61 Y6.869 E.0695
G1 X113.61 Y6.469 E.01229
G1 X113.61 Y6.069 E.01229
G1 X113.61 Y5.91 E.00489
G1 X116.29 Y5.91 E.08235
G1 X116.29 Y6.31 E.01229
G1 X116.29 Y6.71 E.01229
G1 X116.29 Y6.969 E.00796
G1 X116.29 Y7.369 E.01229
G1 X116.29 Y7.831 E.0142
G1 X116.29 Y8.231 E.01229
G1 X116.29 Y8.49 E.00796
G1 X116.29 Y8.89 E.01229
G1 X116.29 Y9.29 E.01229
G1 X113.61 Y9.29 E.08235
G1 X113.61 Y9.191 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y7.191 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.506 Y7.25 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X115.506 Y6.694 E.01708
G1 X114.394 Y6.694 E.03416
G1 X114.394 Y8.506 E.05567
G1 X115.506 Y8.506 E.03416
G1 X115.506 Y7.31 E.03675
G1 X115.134 Y7.25 F30000
; LINE_WIDTH: 0.41026
G1 F1200
G1 X115.134 Y7.066 E.0055
G1 X114.766 Y7.066 E.011
G1 X114.766 Y8.134 E.03195
G1 X115.134 Y8.134 E.011
G1 X115.134 Y7.31 E.02466
; CHANGE_LAYER
; Z_HEIGHT: 5.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.134 Y8.134 E-.313
G1 X114.766 Y8.134 E-.13959
G1 X114.766 Y7.325 E-.30741
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 27/40
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
G17
G3 Z5.6 I1.217 J0 P1  F30000
; object ids of layer 27 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer27 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y9.098
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X141.002 Y6.102 E.09938
G1 X143.098 Y6.102 E.06952
G1 X143.098 Y9.098 E.09938
G1 X141.062 Y9.098 E.06753
G1 X140.61 Y9.331 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X140.61 Y6.669 E.0818
G1 X140.61 Y6.269 E.01229
G1 X140.61 Y5.869 E.01229
G1 X140.61 Y5.71 E.00489
G1 X143.49 Y5.71 E.08849
G1 X143.49 Y9.49 E.11615
G1 X140.61 Y9.49 E.08849
G1 X140.61 Y9.391 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y7.391 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.706 Y7.15 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X142.706 Y6.494 E.02015
G1 X141.394 Y6.494 E.04031
G1 X141.394 Y8.706 E.06796
G1 X142.706 Y8.706 E.04031
G1 X142.706 Y7.21 E.04596
G1 X142.284 Y7.15 F30000
; LINE_WIDTH: 0.51025
G1 F1200
G1 X142.284 Y6.916 E.0089
G1 X141.816 Y6.916 E.0178
G1 X141.816 Y8.284 E.05207
G1 X142.284 Y8.284 E.0178
G1 X142.284 Y7.21 E.04089
; OBJECT_ID: 12
; WIPE_START
G1 F13480.839
G1 X142.284 Y8.284 E-.408
G1 X141.816 Y8.284 E-.17759
G1 X141.816 Y7.825 E-.17441
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X134.192 Y8.174 Z5.8 F30000
G1 X114.002 Y9.098 Z5.8
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X114.002 Y6.102 E.09938
G1 X116.098 Y6.102 E.06952
G1 X116.098 Y9.098 E.09938
G1 X114.062 Y9.098 E.06753
G1 X113.61 Y9.331 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X113.61 Y6.669 E.0818
G1 X113.61 Y6.269 E.01229
G1 X113.61 Y5.869 E.01229
G1 X113.61 Y5.71 E.00489
G1 X116.49 Y5.71 E.08849
G1 X116.49 Y9.49 E.11615
G1 X113.61 Y9.49 E.08849
G1 X113.61 Y9.391 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y7.391 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.706 Y7.15 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X115.706 Y6.494 E.02015
G1 X114.394 Y6.494 E.04031
G1 X114.394 Y8.706 E.06796
G1 X115.706 Y8.706 E.04031
G1 X115.706 Y7.21 E.04596
G1 X115.284 Y7.15 F30000
; LINE_WIDTH: 0.51025
G1 F1200
G1 X115.284 Y6.916 E.0089
G1 X114.816 Y6.916 E.0178
G1 X114.816 Y8.284 E.05207
G1 X115.284 Y8.284 E.0178
G1 X115.284 Y7.21 E.04089
; CHANGE_LAYER
; Z_HEIGHT: 5.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F13480.839
G1 X115.284 Y8.284 E-.408
G1 X114.816 Y8.284 E-.17759
G1 X114.816 Y7.825 E-.17441
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 28/40
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
G17
G3 Z5.8 I1.217 J0 P1  F30000
; object ids of layer 28 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer28 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y9.298
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1387
G1 X141.002 Y5.902 E.11265
G1 X143.298 Y5.902 E.07616
G1 X143.298 Y9.298 E.11265
G1 X141.062 Y9.298 E.07417
G1 X140.61 Y9.531 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1387
M204 S5000
G1 X140.61 Y6.469 E.09409
G1 X140.61 Y6.069 E.01229
G1 X140.61 Y5.669 E.01229
G1 X140.61 Y5.51 E.00489
G1 X143.69 Y5.51 E.09464
G1 X143.69 Y9.69 E.12844
G1 X140.61 Y9.69 E.09464
G1 X140.61 Y9.591 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y7.591 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.15 Y8.15 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42346
G1 F1387
G1 X142.15 Y7.11 E.03225
G1 X142.529 Y7.05 F30000
; LINE_WIDTH: 0.41999
G1 F1387
G1 X142.529 Y6.671 E.01164
G1 X141.771 Y6.671 E.02328
G1 X141.771 Y8.529 E.05708
G1 X142.529 Y8.529 E.02328
G1 X142.529 Y7.11 E.0436
G1 X142.906 Y7.05 F30000
G1 F1387
G1 X142.906 Y6.294 E.02323
G1 X141.394 Y6.294 E.04645
G1 X141.394 Y8.906 E.08025
G1 X142.906 Y8.906 E.04645
G1 X142.906 Y7.11 E.05518
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.906 Y8.906 E-.68244
G1 X142.702 Y8.906 E-.07756
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.07 Y9.01 Z6 F30000
G1 X114.002 Y9.298 Z6
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1387
G1 X114.002 Y5.902 E.11265
G1 X116.298 Y5.902 E.07616
G1 X116.298 Y9.298 E.11265
G1 X114.062 Y9.298 E.07417
G1 X113.61 Y9.531 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1387
M204 S5000
G1 X113.61 Y6.469 E.09409
G1 X113.61 Y6.069 E.01229
G1 X113.61 Y5.669 E.01229
G1 X113.61 Y5.51 E.00489
G1 X116.69 Y5.51 E.09464
G1 X116.69 Y9.69 E.12844
G1 X113.61 Y9.69 E.09464
M73 P96 R1
G1 X113.61 Y9.591 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y7.591 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.15 Y8.15 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42346
G1 F1387
G1 X115.15 Y7.11 E.03225
G1 X115.529 Y7.05 F30000
; LINE_WIDTH: 0.41999
G1 F1387
G1 X115.529 Y6.671 E.01164
G1 X114.771 Y6.671 E.02328
G1 X114.771 Y8.529 E.05708
G1 X115.529 Y8.529 E.02328
G1 X115.529 Y7.11 E.0436
G1 X115.906 Y7.05 F30000
G1 F1387
G1 X115.906 Y6.294 E.02323
G1 X114.394 Y6.294 E.04645
G1 X114.394 Y8.906 E.08025
G1 X115.906 Y8.906 E.04645
G1 X115.906 Y7.11 E.05518
; CHANGE_LAYER
; Z_HEIGHT: 5.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.906 Y8.906 E-.68244
G1 X115.702 Y8.906 E-.07756
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 29/40
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
G17
G3 Z6 I1.217 J0 P1  F30000
; object ids of layer 29 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer29 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y9.498
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1553
G1 X141.002 Y5.702 E.12592
G1 X143.498 Y5.702 E.08279
G1 X143.498 Y9.498 E.12592
G1 X141.062 Y9.498 E.0808
G1 X140.61 Y9.731 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1553
M204 S5000
G1 X140.61 Y6.269 E.10638
G1 X140.61 Y5.869 E.01229
G1 X140.61 Y5.469 E.01229
G1 X140.61 Y5.31 E.00489
G1 X143.89 Y5.31 E.10079
G1 X143.89 Y9.89 E.14073
G1 X140.61 Y9.89 E.10079
G1 X140.61 Y9.791 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y7.791 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.25 Y8.25 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.62346
G1 F1553
G1 X142.25 Y7.01 E.05866
G1 X142.729 Y6.95 F30000
; LINE_WIDTH: 0.41999
G1 F1553
G1 X142.729 Y6.471 E.01471
G1 X141.771 Y6.471 E.02942
G1 X141.771 Y8.729 E.06937
G1 X142.729 Y8.729 E.02942
G1 X142.729 Y7.01 E.05281
G1 X143.106 Y6.95 F30000
G1 F1553
G1 X143.106 Y6.094 E.0263
G1 X141.394 Y6.094 E.0526
G1 X141.394 Y9.106 E.09254
G1 X143.106 Y9.106 E.0526
G1 X143.106 Y7.01 E.0644
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X143.106 Y9.01 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.474 Y9.138 Z6.2 F30000
G1 X114.002 Y9.498 Z6.2
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1553
G1 X114.002 Y5.702 E.12592
G1 X116.498 Y5.702 E.08279
G1 X116.498 Y9.498 E.12592
G1 X114.062 Y9.498 E.0808
G1 X113.61 Y9.731 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1553
M204 S5000
G1 X113.61 Y6.269 E.10638
G1 X113.61 Y5.869 E.01229
G1 X113.61 Y5.469 E.01229
G1 X113.61 Y5.31 E.00489
G1 X116.89 Y5.31 E.10079
G1 X116.89 Y9.89 E.14073
G1 X113.61 Y9.89 E.10079
G1 X113.61 Y9.791 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y7.791 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.25 Y8.25 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.62346
G1 F1553
G1 X115.25 Y7.01 E.05866
G1 X115.729 Y6.95 F30000
; LINE_WIDTH: 0.41999
G1 F1553
G1 X115.729 Y6.471 E.01471
G1 X114.771 Y6.471 E.02942
G1 X114.771 Y8.729 E.06937
G1 X115.729 Y8.729 E.02942
G1 X115.729 Y7.01 E.05281
G1 X116.106 Y6.95 F30000
G1 F1553
G1 X116.106 Y6.094 E.0263
G1 X114.394 Y6.094 E.0526
G1 X114.394 Y9.106 E.09254
G1 X116.106 Y9.106 E.0526
G1 X116.106 Y7.01 E.0644
; CHANGE_LAYER
; Z_HEIGHT: 6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X116.106 Y9.01 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 30/40
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
G17
G3 Z6.2 I1.217 J0 P1  F30000
; object ids of layer 30 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer30 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y9.698
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1819
G1 X141.002 Y5.502 E.13919
G1 X143.698 Y5.502 E.08943
G1 X143.698 Y9.698 E.13919
G1 X141.062 Y9.698 E.08744
G1 X140.61 Y9.931 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1819
M204 S5000
G1 X140.61 Y6.069 E.11867
G1 X140.61 Y5.669 E.01229
G1 X140.61 Y5.269 E.01229
G1 X140.61 Y5.11 E.00489
G1 X144.09 Y5.11 E.10693
G1 X144.09 Y10.09 E.15302
G1 X140.61 Y10.09 E.10693
G1 X140.61 Y9.991 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y7.991 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.545 Y6.85 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43319
G1 F1819
G1 X142.545 Y6.655 E.00621
G1 X142.155 Y6.655 E.01241
G1 X142.155 Y8.545 E.06011
G1 X142.545 Y8.545 E.01241
G1 X142.545 Y6.91 E.052
G1 X142.929 Y6.85 F30000
; LINE_WIDTH: 0.41999
G1 F1819
G1 X142.929 Y6.271 E.01778
G1 X141.771 Y6.271 E.03557
G1 X141.771 Y8.929 E.08166
G1 X142.929 Y8.929 E.03557
G1 X142.929 Y6.91 E.06203
G1 X143.306 Y6.85 F30000
G1 F1819
G1 X143.306 Y5.894 E.02937
G1 X141.394 Y5.894 E.05874
G1 X141.394 Y9.306 E.10483
G1 X143.306 Y9.306 E.05874
G1 X143.306 Y6.91 E.07362
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X143.306 Y8.91 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.676 Y9.115 Z6.4 F30000
G1 X114.002 Y9.698 Z6.4
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1819
G1 X114.002 Y5.502 E.13919
G1 X116.698 Y5.502 E.08943
G1 X116.698 Y9.698 E.13919
G1 X114.062 Y9.698 E.08744
G1 X113.61 Y9.931 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1819
M204 S5000
G1 X113.61 Y6.069 E.11867
G1 X113.61 Y5.669 E.01229
G1 X113.61 Y5.269 E.01229
G1 X113.61 Y5.11 E.00489
G1 X117.09 Y5.11 E.10693
G1 X117.09 Y10.09 E.15302
G1 X113.61 Y10.09 E.10693
G1 X113.61 Y9.991 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y7.991 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.545 Y6.85 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43319
G1 F1819
G1 X115.545 Y6.655 E.00621
G1 X115.155 Y6.655 E.01241
G1 X115.155 Y8.545 E.06011
G1 X115.545 Y8.545 E.01241
G1 X115.545 Y6.91 E.052
G1 X115.929 Y6.85 F30000
; LINE_WIDTH: 0.41999
G1 F1819
G1 X115.929 Y6.271 E.01778
G1 X114.771 Y6.271 E.03557
G1 X114.771 Y8.929 E.08166
G1 X115.929 Y8.929 E.03557
G1 X115.929 Y6.91 E.06203
G1 X116.306 Y6.85 F30000
G1 F1819
G1 X116.306 Y5.894 E.02937
G1 X114.394 Y5.894 E.05874
G1 X114.394 Y9.306 E.10483
G1 X116.306 Y9.306 E.05874
G1 X116.306 Y6.91 E.07362
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X116.306 Y8.91 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 31/40
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
G17
G3 Z6.4 I1.217 J0 P1  F30000
; object ids of layer 31 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer31 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y9.898
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2006
G1 X141.002 Y5.302 E.15245
G1 X143.898 Y5.302 E.09606
G1 X143.898 Y9.898 E.15245
G1 X141.062 Y9.898 E.09407
G1 X140.61 Y10.131 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2006
M204 S5000
G1 X140.61 Y5.869 E.13096
G1 X140.61 Y5.469 E.01229
G1 X140.61 Y5.069 E.01229
G1 X140.61 Y4.91 E.00489
G1 X144.29 Y4.91 E.11308
G1 X144.29 Y10.29 E.16531
G1 X140.61 Y10.29 E.11308
G1 X140.61 Y10.191 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y8.191 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.695 Y6.75 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.53319
G1 F2006
G1 X142.695 Y6.505 E.00979
G1 X142.205 Y6.505 E.01959
G1 X142.205 Y8.695 E.0875
G1 X142.695 Y8.695 E.01959
G1 X142.695 Y6.81 E.07531
G1 X143.129 Y6.75 F30000
; LINE_WIDTH: 0.41999
G1 F2006
G1 X143.129 Y6.071 E.02086
G1 X141.771 Y6.071 E.04171
G1 X141.771 Y9.129 E.09395
G1 X143.129 Y9.129 E.04171
G1 X143.129 Y6.81 E.07125
G1 X143.506 Y6.75 F30000
G1 F2006
G1 X143.506 Y5.694 E.03244
G1 X141.394 Y5.694 E.06489
G1 X141.394 Y9.506 E.11712
G1 X143.506 Y9.506 E.06489
G1 X143.506 Y6.81 E.08284
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X143.506 Y8.81 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.879 Y9.091 Z6.6 F30000
G1 X114.002 Y9.898 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2006
G1 X114.002 Y5.302 E.15245
G1 X116.898 Y5.302 E.09606
G1 X116.898 Y9.898 E.15245
G1 X114.062 Y9.898 E.09407
G1 X113.61 Y10.131 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2006
M204 S5000
G1 X113.61 Y5.869 E.13096
G1 X113.61 Y5.469 E.01229
G1 X113.61 Y5.069 E.01229
G1 X113.61 Y4.91 E.00489
G1 X117.29 Y4.91 E.11308
G1 X117.29 Y10.29 E.16531
G1 X113.61 Y10.29 E.11308
G1 X113.61 Y10.191 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y8.191 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.695 Y6.75 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.53319
G1 F2006
G1 X115.695 Y6.505 E.00979
G1 X115.205 Y6.505 E.01959
G1 X115.205 Y8.695 E.0875
G1 X115.695 Y8.695 E.01959
G1 X115.695 Y6.81 E.07531
G1 X116.129 Y6.75 F30000
; LINE_WIDTH: 0.41999
G1 F2006
G1 X116.129 Y6.071 E.02086
G1 X114.771 Y6.071 E.04171
G1 X114.771 Y9.129 E.09395
G1 X116.129 Y9.129 E.04171
G1 X116.129 Y6.81 E.07125
G1 X116.506 Y6.75 F30000
G1 F2006
G1 X116.506 Y5.694 E.03244
G1 X114.394 Y5.694 E.06489
G1 X114.394 Y9.506 E.11712
G1 X116.506 Y9.506 E.06489
G1 X116.506 Y6.81 E.08284
; CHANGE_LAYER
; Z_HEIGHT: 6.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X116.506 Y8.81 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 32/40
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
G17
G3 Z6.6 I1.217 J0 P1  F30000
; object ids of layer 32 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer32 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y10.098
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2313
G1 X141.002 Y5.102 E.16572
G1 X144.098 Y5.102 E.1027
G1 X144.098 Y10.098 E.16572
G1 X141.062 Y10.098 E.10071
G1 X140.61 Y10.331 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2313
M204 S5000
G1 X140.61 Y5.669 E.14325
G1 X140.61 Y5.269 E.01229
G1 X140.61 Y4.869 E.01229
G1 X140.61 Y4.71 E.00489
G1 F2160
G1 X144.49 Y4.71 E.11922
G1 X144.49 Y10.49 E.1776
G1 X140.61 Y10.49 E.11922
G1 F2313
G1 X140.61 Y10.391 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y8.391 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.55 Y8.55 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46932
G1 F2313
G1 X142.55 Y6.71 E.06393
G1 X142.952 Y6.65 F30000
; LINE_WIDTH: 0.41999
G1 F2313
G1 X142.952 Y6.248 E.01234
G1 X142.148 Y6.248 E.02469
G1 X142.148 Y8.952 E.08307
G1 X142.952 Y8.952 E.02469
G1 X142.952 Y6.71 E.06888
G1 X143.329 Y6.65 F30000
G1 F2313
G1 X143.329 Y5.871 E.02393
G1 X141.771 Y5.871 E.04786
G1 X141.771 Y9.329 E.10624
G1 X143.329 Y9.329 E.04786
G1 X143.329 Y6.71 E.08047
G1 X143.706 Y6.65 F30000
G1 F2313
G1 X143.706 Y5.494 E.03552
G1 X141.394 Y5.494 E.07103
G1 X141.394 Y9.706 E.12941
G1 X143.706 Y9.706 E.07103
G1 X143.706 Y6.71 E.09205
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X143.706 Y8.71 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.082 Y9.066 Z6.8 F30000
G1 X114.002 Y10.098 Z6.8
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2313
G1 X114.002 Y5.102 E.16572
G1 X117.098 Y5.102 E.1027
G1 X117.098 Y10.098 E.16572
G1 X114.062 Y10.098 E.10071
G1 X113.61 Y10.331 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2313
M204 S5000
G1 X113.61 Y5.669 E.14325
G1 X113.61 Y5.269 E.01229
G1 X113.61 Y4.869 E.01229
G1 X113.61 Y4.71 E.00489
G1 F2160
G1 X117.49 Y4.71 E.11922
G1 X117.49 Y10.49 E.1776
G1 X113.61 Y10.49 E.11922
G1 F2313
G1 X113.61 Y10.391 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y8.391 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.55 Y8.55 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46932
G1 F2313
G1 X115.55 Y6.71 E.06393
G1 X115.952 Y6.65 F30000
; LINE_WIDTH: 0.41999
G1 F2313
G1 X115.952 Y6.248 E.01234
G1 X115.148 Y6.248 E.02469
G1 X115.148 Y8.952 E.08307
G1 X115.952 Y8.952 E.02469
G1 X115.952 Y6.71 E.06888
G1 X116.329 Y6.65 F30000
G1 F2313
G1 X116.329 Y5.871 E.02393
G1 X114.771 Y5.871 E.04786
G1 X114.771 Y9.329 E.10624
G1 X116.329 Y9.329 E.04786
G1 X116.329 Y6.71 E.08047
G1 X116.706 Y6.65 F30000
G1 F2313
G1 X116.706 Y5.494 E.03552
G1 X114.394 Y5.494 E.07103
G1 X114.394 Y9.706 E.12941
G1 X116.706 Y9.706 E.07103
G1 X116.706 Y6.71 E.09205
; CHANGE_LAYER
; Z_HEIGHT: 6.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X116.706 Y8.71 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 33/40
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
G17
G3 Z6.8 I1.217 J0 P1  F30000
; object ids of layer 33 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer33 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y10.298
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2727
G1 X141.002 Y4.902 E.17899
G1 X144.298 Y4.902 E.10933
G1 X144.298 Y10.298 E.17899
G1 X141.062 Y10.298 E.10734
M73 P97 R1
G1 X140.61 Y10.531 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2727
M204 S5000
G1 X140.61 Y5.469 E.15554
G1 X140.61 Y5.069 E.01229
G1 X140.61 Y4.669 E.01229
G1 X140.61 Y4.51 E.00489
G1 F2160
G1 X144.69 Y4.51 E.12537
G1 X144.69 Y10.69 E.18989
G1 X140.61 Y10.69 E.12537
G1 F2727
G1 X140.61 Y10.591 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y8.591 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.906 Y6.55 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2727
G1 X143.906 Y5.294 E.03859
G1 X141.394 Y5.294 E.07718
G1 X141.394 Y9.906 E.1417
G1 X143.906 Y9.906 E.07718
G1 X143.906 Y6.61 E.10127
G1 X143.529 Y6.55 F30000
M73 P97 R0
G1 F2727
G1 X143.529 Y5.671 E.027
G1 X141.771 Y5.671 E.05401
G1 X141.771 Y9.529 E.11853
G1 X143.529 Y9.529 E.05401
G1 X143.529 Y6.61 E.08968
G1 X143.152 Y6.55 F30000
G1 F2727
G1 X143.152 Y6.048 E.01542
G1 X142.148 Y6.048 E.03083
G1 X142.148 Y9.152 E.09536
G1 X143.152 Y9.152 E.03083
G1 X143.152 Y6.61 E.0781
G1 X142.807 Y6.55 F30000
; LINE_WIDTH: 0.35612
G1 F2727
G1 X142.807 Y6.393 E.004
G1 X142.493 Y6.393 E.00799
G1 X142.493 Y8.807 E.06159
G1 X142.807 Y8.807 E.00799
G1 X142.807 Y6.61 E.05606
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X142.807 Y8.61 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X135.187 Y9.056 Z7 F30000
G1 X114.002 Y10.298 Z7
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2727
G1 X114.002 Y4.902 E.17899
G1 X117.298 Y4.902 E.10933
G1 X117.298 Y10.298 E.17899
G1 X114.062 Y10.298 E.10734
G1 X113.61 Y10.531 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2727
M204 S5000
G1 X113.61 Y5.469 E.15554
G1 X113.61 Y5.069 E.01229
G1 X113.61 Y4.669 E.01229
G1 X113.61 Y4.51 E.00489
G1 F2160
G1 X117.69 Y4.51 E.12537
G1 X117.69 Y10.69 E.18989
G1 X113.61 Y10.69 E.12537
G1 F2727
G1 X113.61 Y10.591 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y8.591 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.906 Y6.55 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2727
G1 X116.906 Y5.294 E.03859
G1 X114.394 Y5.294 E.07718
G1 X114.394 Y9.906 E.1417
G1 X116.906 Y9.906 E.07718
G1 X116.906 Y6.61 E.10127
G1 X116.529 Y6.55 F30000
G1 F2727
G1 X116.529 Y5.671 E.027
G1 X114.771 Y5.671 E.05401
G1 X114.771 Y9.529 E.11853
G1 X116.529 Y9.529 E.05401
G1 X116.529 Y6.61 E.08968
G1 X116.152 Y6.55 F30000
G1 F2727
G1 X116.152 Y6.048 E.01542
G1 X115.148 Y6.048 E.03083
G1 X115.148 Y9.152 E.09536
G1 X116.152 Y9.152 E.03083
G1 X116.152 Y6.61 E.0781
G1 X115.807 Y6.55 F30000
; LINE_WIDTH: 0.35612
G1 F2727
G1 X115.807 Y6.393 E.004
G1 X115.493 Y6.393 E.00799
G1 X115.493 Y8.807 E.06159
G1 X115.807 Y8.807 E.00799
G1 X115.807 Y6.61 E.05606
; CHANGE_LAYER
; Z_HEIGHT: 6.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.807 Y8.61 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 34/40
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
G17
G3 Z7 I1.217 J0 P1  F30000
; object ids of layer 34 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer34 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X141.002 Y10.498
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3032
G1 X141.002 Y4.702 E.19226
G1 X144.498 Y4.702 E.11596
G1 X144.498 Y10.498 E.19226
G1 X141.062 Y10.498 E.11397
G1 X140.61 Y10.731 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3032
M204 S5000
G1 X140.61 Y5.269 E.16783
G1 X140.61 Y4.869 E.01229
G1 X140.61 Y4.469 E.01229
G1 X140.61 Y4.31 E.00489
G1 F2160
G1 X144.89 Y4.31 E.13151
G1 X144.89 Y10.89 E.20219
G1 X140.61 Y10.89 E.13151
G1 F3032
G1 X140.61 Y10.791 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X140.61 Y8.791 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.957 Y6.45 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45612
G1 F3032
G1 X142.957 Y6.243 E.00696
G1 X142.543 Y6.243 E.01391
G1 X142.543 Y8.957 E.09136
G1 X142.957 Y8.957 E.01391
G1 X142.957 Y6.51 E.08238
G1 X143.352 Y6.45 F30000
; LINE_WIDTH: 0.41999
G1 F3032
G1 X143.352 Y5.848 E.01849
G1 X142.148 Y5.848 E.03698
G1 X142.148 Y9.352 E.10765
G1 X143.352 Y9.352 E.03698
G1 X143.352 Y6.51 E.08732
G1 X143.729 Y6.45 F30000
G1 F3032
G1 X143.729 Y5.471 E.03008
G1 X141.771 Y5.471 E.06015
G1 X141.771 Y9.729 E.13082
G1 X143.729 Y9.729 E.06015
G1 X143.729 Y6.51 E.0989
G1 X144.106 Y6.45 F30000
G1 F3032
G1 X144.106 Y5.094 E.04166
G1 X141.394 Y5.094 E.08332
G1 X141.394 Y10.106 E.15399
G1 X144.106 Y10.106 E.08332
G1 X144.106 Y6.51 E.11049
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.106 Y8.51 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.49 Y9.013 Z7.2 F30000
G1 X114.002 Y10.498 Z7.2
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3032
G1 X114.002 Y4.702 E.19226
G1 X117.498 Y4.702 E.11596
G1 X117.498 Y10.498 E.19226
G1 X114.062 Y10.498 E.11397
G1 X113.61 Y10.731 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3032
M204 S5000
G1 X113.61 Y5.269 E.16783
G1 X113.61 Y4.869 E.01229
G1 X113.61 Y4.469 E.01229
G1 X113.61 Y4.31 E.00489
G1 F2160
G1 X117.89 Y4.31 E.13151
G1 X117.89 Y10.89 E.20219
G1 X113.61 Y10.89 E.13151
G1 F3032
G1 X113.61 Y10.791 E.00304
; WIPE_START
G1 F3121.313
M204 S10000
G1 X113.61 Y8.791 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.957 Y6.45 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45612
G1 F3032
G1 X115.957 Y6.243 E.00696
G1 X115.543 Y6.243 E.01391
G1 X115.543 Y8.957 E.09136
G1 X115.957 Y8.957 E.01391
G1 X115.957 Y6.51 E.08238
G1 X116.352 Y6.45 F30000
; LINE_WIDTH: 0.41999
G1 F3032
G1 X116.352 Y5.848 E.01849
G1 X115.148 Y5.848 E.03698
G1 X115.148 Y9.352 E.10765
G1 X116.352 Y9.352 E.03698
G1 X116.352 Y6.51 E.08732
G1 X116.729 Y6.45 F30000
G1 F3032
G1 X116.729 Y5.471 E.03008
G1 X114.771 Y5.471 E.06015
G1 X114.771 Y9.729 E.13082
G1 X116.729 Y9.729 E.06015
G1 X116.729 Y6.51 E.0989
G1 X117.106 Y6.45 F30000
G1 F3032
G1 X117.106 Y5.094 E.04166
G1 X114.394 Y5.094 E.08332
G1 X114.394 Y10.106 E.15399
G1 X117.106 Y10.106 E.08332
G1 X117.106 Y6.51 E.11049
; CHANGE_LAYER
; Z_HEIGHT: 7
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.106 Y8.51 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 35/40
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
G17
G3 Z7.2 I1.217 J0 P1  F30000
; object ids of layer 35 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer35 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.598 Y10.598
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2901
G1 X141.002 Y10.598 E.11928
G1 X141.002 Y4.602 E.19889
G1 X144.598 Y4.602 E.11928
G1 X144.598 Y10.538 E.1969
G1 X144.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2901
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y10.931 E.00181
G1 X140.61 Y10.531 E.01229
G1 X140.61 Y4.669 E.18012
G1 X140.61 Y4.269 E.01229
G1 X140.61 Y4.21 E.00181
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
; WIPE_START
G1 F9300
M204 S10000
G1 X142.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.032 Y6.4 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2901
G1 X143.032 Y6.168 E.00874
G1 X142.568 Y6.168 E.01748
G1 X142.568 Y9.032 E.10807
G1 X143.032 Y9.032 E.01748
G1 X143.032 Y6.46 E.09707
G1 X143.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2901
G1 X143.452 Y5.748 E.02003
G1 X142.148 Y5.748 E.04005
G1 X142.148 Y9.452 E.11379
G1 X143.452 Y9.452 E.04005
G1 X143.452 Y6.46 E.09193
G1 X143.829 Y6.4 F30000
G1 F2901
G1 X143.829 Y5.371 E.03161
G1 X141.771 Y5.371 E.06322
G1 X141.771 Y9.829 E.13697
G1 X143.829 Y9.829 E.06322
G1 X143.829 Y6.46 E.10351
G1 X144.206 Y6.4 F30000
G1 F2901
G1 X144.206 Y4.994 E.0432
G1 X141.394 Y4.994 E.0864
G1 X141.394 Y10.206 E.16014
G1 X144.206 Y10.206 E.0864
G1 X144.206 Y6.46 E.1151
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.598 Y9.071 Z7.4 F30000
G1 X117.598 Y10.598 Z7.4
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2901
G1 X114.002 Y10.598 E.11928
G1 X114.002 Y4.602 E.19889
G1 X117.598 Y4.602 E.11928
G1 X117.598 Y10.538 E.1969
G1 X117.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2901
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y10.931 E.00181
G1 X113.61 Y10.531 E.01229
G1 X113.61 Y4.669 E.18012
G1 X113.61 Y4.269 E.01229
G1 X113.61 Y4.21 E.00181
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
; WIPE_START
G1 F9300
M204 S10000
G1 X115.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.032 Y6.4 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2901
G1 X116.032 Y6.168 E.00874
G1 X115.568 Y6.168 E.01748
G1 X115.568 Y9.032 E.10807
G1 X116.032 Y9.032 E.01748
G1 X116.032 Y6.46 E.09707
G1 X116.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2901
G1 X116.452 Y5.748 E.02003
G1 X115.148 Y5.748 E.04005
G1 X115.148 Y9.452 E.11379
G1 X116.452 Y9.452 E.04005
G1 X116.452 Y6.46 E.09193
G1 X116.829 Y6.4 F30000
G1 F2901
G1 X116.829 Y5.371 E.03161
G1 X114.771 Y5.371 E.06322
G1 X114.771 Y9.829 E.13697
G1 X116.829 Y9.829 E.06322
G1 X116.829 Y6.46 E.10351
G1 X117.206 Y6.4 F30000
G1 F2901
G1 X117.206 Y4.994 E.0432
G1 X114.394 Y4.994 E.0864
G1 X114.394 Y10.206 E.16014
G1 X117.206 Y10.206 E.0864
G1 X117.206 Y6.46 E.1151
; CHANGE_LAYER
; Z_HEIGHT: 7.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 36/40
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
G17
G3 Z7.4 I1.217 J0 P1  F30000
; object ids of layer 36 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer36 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.598 Y10.598
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X141.002 Y10.598 E.11928
G1 X141.002 Y4.602 E.19889
G1 X144.598 Y4.602 E.11928
G1 X144.598 Y10.538 E.1969
G1 X144.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y4.21 E.20833
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X142.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.032 Y6.4 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X143.032 Y6.168 E.00874
G1 X142.568 Y6.168 E.01748
G1 X142.568 Y9.032 E.10807
G1 X143.032 Y9.032 E.01748
G1 X143.032 Y6.46 E.09707
G1 X143.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X143.452 Y5.748 E.02003
G1 X142.148 Y5.748 E.04005
G1 X142.148 Y9.452 E.11379
G1 X143.452 Y9.452 E.04005
G1 X143.452 Y6.46 E.09193
G1 X143.829 Y6.4 F30000
G1 F2885
G1 X143.829 Y5.371 E.03161
G1 X141.771 Y5.371 E.06322
G1 X141.771 Y9.829 E.13697
G1 X143.829 Y9.829 E.06322
G1 X143.829 Y6.46 E.10351
G1 X144.206 Y6.4 F30000
G1 F2885
G1 X144.206 Y4.994 E.0432
G1 X141.394 Y4.994 E.0864
G1 X141.394 Y10.206 E.16014
G1 X144.206 Y10.206 E.0864
G1 X144.206 Y6.46 E.1151
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.598 Y9.071 Z7.6 F30000
G1 X117.598 Y10.598 Z7.6
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X114.002 Y10.598 E.11928
G1 X114.002 Y4.602 E.19889
G1 X117.598 Y4.602 E.11928
G1 X117.598 Y10.538 E.1969
G1 X117.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y4.21 E.20833
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X115.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.032 Y6.4 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X116.032 Y6.168 E.00874
G1 X115.568 Y6.168 E.01748
G1 X115.568 Y9.032 E.10807
G1 X116.032 Y9.032 E.01748
G1 X116.032 Y6.46 E.09707
G1 X116.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X116.452 Y5.748 E.02003
G1 X115.148 Y5.748 E.04005
G1 X115.148 Y9.452 E.11379
G1 X116.452 Y9.452 E.04005
G1 X116.452 Y6.46 E.09193
G1 X116.829 Y6.4 F30000
G1 F2885
G1 X116.829 Y5.371 E.03161
G1 X114.771 Y5.371 E.06322
G1 X114.771 Y9.829 E.13697
G1 X116.829 Y9.829 E.06322
G1 X116.829 Y6.46 E.10351
G1 X117.206 Y6.4 F30000
G1 F2885
G1 X117.206 Y4.994 E.0432
G1 X114.394 Y4.994 E.0864
G1 X114.394 Y10.206 E.16014
G1 X117.206 Y10.206 E.0864
G1 X117.206 Y6.46 E.1151
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 37/40
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
G17
G3 Z7.6 I1.217 J0 P1  F30000
; object ids of layer 37 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer37 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.598 Y10.598
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X141.002 Y10.598 E.11928
G1 X141.002 Y4.602 E.19889
G1 X144.598 Y4.602 E.11928
G1 X144.598 Y10.538 E.1969
G1 X144.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y4.21 E.20833
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X142.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.032 Y6.4 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X143.032 Y6.168 E.00874
G1 X142.568 Y6.168 E.01748
G1 X142.568 Y9.032 E.10807
G1 X143.032 Y9.032 E.01748
G1 X143.032 Y6.46 E.09707
G1 X143.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X143.452 Y5.748 E.02003
G1 X142.148 Y5.748 E.04005
G1 X142.148 Y9.452 E.11379
G1 X143.452 Y9.452 E.04005
G1 X143.452 Y6.46 E.09193
G1 X143.829 Y6.4 F30000
G1 F2885
G1 X143.829 Y5.371 E.03161
G1 X141.771 Y5.371 E.06322
G1 X141.771 Y9.829 E.13697
G1 X143.829 Y9.829 E.06322
G1 X143.829 Y6.46 E.10351
G1 X144.206 Y6.4 F30000
G1 F2885
G1 X144.206 Y4.994 E.0432
G1 X141.394 Y4.994 E.0864
G1 X141.394 Y10.206 E.16014
G1 X144.206 Y10.206 E.0864
G1 X144.206 Y6.46 E.1151
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.598 Y9.071 Z7.8 F30000
G1 X117.598 Y10.598 Z7.8
M73 P98 R0
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X114.002 Y10.598 E.11928
G1 X114.002 Y4.602 E.19889
G1 X117.598 Y4.602 E.11928
G1 X117.598 Y10.538 E.1969
G1 X117.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y4.21 E.20833
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X115.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.032 Y6.4 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X116.032 Y6.168 E.00874
G1 X115.568 Y6.168 E.01748
G1 X115.568 Y9.032 E.10807
G1 X116.032 Y9.032 E.01748
G1 X116.032 Y6.46 E.09707
G1 X116.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X116.452 Y5.748 E.02003
G1 X115.148 Y5.748 E.04005
G1 X115.148 Y9.452 E.11379
G1 X116.452 Y9.452 E.04005
G1 X116.452 Y6.46 E.09193
G1 X116.829 Y6.4 F30000
G1 F2885
G1 X116.829 Y5.371 E.03161
G1 X114.771 Y5.371 E.06322
G1 X114.771 Y9.829 E.13697
G1 X116.829 Y9.829 E.06322
G1 X116.829 Y6.46 E.10351
G1 X117.206 Y6.4 F30000
G1 F2885
G1 X117.206 Y4.994 E.0432
G1 X114.394 Y4.994 E.0864
G1 X114.394 Y10.206 E.16014
G1 X117.206 Y10.206 E.0864
G1 X117.206 Y6.46 E.1151
; CHANGE_LAYER
; Z_HEIGHT: 7.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 38/40
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
G17
G3 Z7.8 I1.217 J0 P1  F30000
; object ids of layer 38 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer38 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.598 Y10.598
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X141.002 Y10.598 E.11928
G1 X141.002 Y4.602 E.19889
G1 X144.598 Y4.602 E.11928
G1 X144.598 Y10.538 E.1969
G1 X144.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y4.21 E.20833
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X142.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.032 Y6.4 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X143.032 Y6.168 E.00874
G1 X142.568 Y6.168 E.01748
G1 X142.568 Y9.032 E.10807
G1 X143.032 Y9.032 E.01748
G1 X143.032 Y6.46 E.09707
G1 X143.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X143.452 Y5.748 E.02003
G1 X142.148 Y5.748 E.04005
G1 X142.148 Y9.452 E.11379
G1 X143.452 Y9.452 E.04005
G1 X143.452 Y6.46 E.09193
G1 X143.829 Y6.4 F30000
G1 F2885
G1 X143.829 Y5.371 E.03161
G1 X141.771 Y5.371 E.06322
G1 X141.771 Y9.829 E.13697
G1 X143.829 Y9.829 E.06322
G1 X143.829 Y6.46 E.10351
G1 X144.206 Y6.4 F30000
G1 F2885
G1 X144.206 Y4.994 E.0432
G1 X141.394 Y4.994 E.0864
G1 X141.394 Y10.206 E.16014
G1 X144.206 Y10.206 E.0864
G1 X144.206 Y6.46 E.1151
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.598 Y9.071 Z8 F30000
G1 X117.598 Y10.598 Z8
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X114.002 Y10.598 E.11928
G1 X114.002 Y4.602 E.19889
G1 X117.598 Y4.602 E.11928
G1 X117.598 Y10.538 E.1969
G1 X117.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y4.21 E.20833
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X115.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.032 Y6.4 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X116.032 Y6.168 E.00874
G1 X115.568 Y6.168 E.01748
G1 X115.568 Y9.032 E.10807
G1 X116.032 Y9.032 E.01748
G1 X116.032 Y6.46 E.09707
G1 X116.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X116.452 Y5.748 E.02003
G1 X115.148 Y5.748 E.04005
G1 X115.148 Y9.452 E.11379
G1 X116.452 Y9.452 E.04005
G1 X116.452 Y6.46 E.09193
G1 X116.829 Y6.4 F30000
G1 F2885
G1 X116.829 Y5.371 E.03161
G1 X114.771 Y5.371 E.06322
G1 X114.771 Y9.829 E.13697
G1 X116.829 Y9.829 E.06322
G1 X116.829 Y6.46 E.10351
G1 X117.206 Y6.4 F30000
G1 F2885
G1 X117.206 Y4.994 E.0432
G1 X114.394 Y4.994 E.0864
G1 X114.394 Y10.206 E.16014
G1 X117.206 Y10.206 E.0864
G1 X117.206 Y6.46 E.1151
; CHANGE_LAYER
; Z_HEIGHT: 7.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 39/40
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
G17
G3 Z8 I1.217 J0 P1  F30000
; object ids of layer 39 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer39 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.598 Y10.598
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X141.002 Y10.598 E.11928
G1 X141.002 Y4.602 E.19889
G1 X144.598 Y4.602 E.11928
G1 X144.598 Y10.538 E.1969
G1 X144.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y4.21 E.20833
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X142.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X143.032 Y6.4 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X143.032 Y6.168 E.00874
G1 X142.568 Y6.168 E.01748
G1 X142.568 Y9.032 E.10807
G1 X143.032 Y9.032 E.01748
G1 X143.032 Y6.46 E.09707
G1 X143.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X143.452 Y5.748 E.02003
G1 X142.148 Y5.748 E.04005
G1 X142.148 Y9.452 E.11379
G1 X143.452 Y9.452 E.04005
G1 X143.452 Y6.46 E.09193
G1 X143.829 Y6.4 F30000
G1 F2885
G1 X143.829 Y5.371 E.03161
G1 X141.771 Y5.371 E.06322
G1 X141.771 Y9.829 E.13697
G1 X143.829 Y9.829 E.06322
G1 X143.829 Y6.46 E.10351
G1 X144.206 Y6.4 F30000
G1 F2885
G1 X144.206 Y4.994 E.0432
G1 X141.394 Y4.994 E.0864
G1 X141.394 Y10.206 E.16014
G1 X144.206 Y10.206 E.0864
G1 X144.206 Y6.46 E.1151
; OBJECT_ID: 12
; WIPE_START
G1 F15000
G1 X144.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X136.598 Y9.071 Z8.2 F30000
G1 X117.598 Y10.598 Z8.2
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2885
G1 X114.002 Y10.598 E.11928
G1 X114.002 Y4.602 E.19889
G1 X117.598 Y4.602 E.11928
G1 X117.598 Y10.538 E.1969
G1 X117.99 Y10.99 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2885
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y4.21 E.20833
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
; WIPE_START
G1 F12000
M204 S10000
G1 X115.99 Y10.957 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.032 Y6.4 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50612
G1 F2885
G1 X116.032 Y6.168 E.00874
G1 X115.568 Y6.168 E.01748
G1 X115.568 Y9.032 E.10807
G1 X116.032 Y9.032 E.01748
G1 X116.032 Y6.46 E.09707
G1 X116.452 Y6.4 F30000
; LINE_WIDTH: 0.41999
G1 F2885
G1 X116.452 Y5.748 E.02003
G1 X115.148 Y5.748 E.04005
G1 X115.148 Y9.452 E.11379
G1 X116.452 Y9.452 E.04005
G1 X116.452 Y6.46 E.09193
G1 X116.829 Y6.4 F30000
G1 F2885
G1 X116.829 Y5.371 E.03161
G1 X114.771 Y5.371 E.06322
G1 X114.771 Y9.829 E.13697
G1 X116.829 Y9.829 E.06322
G1 X116.829 Y6.46 E.10351
G1 X117.206 Y6.4 F30000
G1 F2885
G1 X117.206 Y4.994 E.0432
G1 X114.394 Y4.994 E.0864
G1 X114.394 Y10.206 E.16014
G1 X117.206 Y10.206 E.0864
G1 X117.206 Y6.46 E.1151
; CHANGE_LAYER
; Z_HEIGHT: 8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X117.206 Y8.46 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; layer num/total_layer_count: 40/40
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
G17
G3 Z8.2 I1.217 J0 P1  F30000
; object ids of layer 40 start: 12,16
M624 BgAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer40 end: 12,16
M625
; OBJECT_ID: 16
; start printing object, unique label id: 16
M624 BAAAAAAAAAA=
G1 X144.99 Y10.99
G1 Z8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3242
M204 S5000
G1 X140.61 Y10.99 E.13459
G1 X140.61 Y4.21 E.20833
G1 X144.99 Y4.21 E.13459
G1 X144.99 Y10.93 E.20649
M204 S10000
G1 X144.783 Y10.251 F30000
; FEATURE: Top surface
G1 F3242
M204 S2000
G1 X144.251 Y10.783 E.0231
G1 X143.718 Y10.783
G1 X144.783 Y9.718 E.04627
G1 X144.783 Y9.185
G1 X143.185 Y10.783 E.06944
G1 X142.651 Y10.783
G1 X144.783 Y8.651 E.09261
G1 X144.783 Y8.118
G1 X142.118 Y10.783 E.11579
G1 X141.585 Y10.783
G1 X144.783 Y7.585 E.13896
G1 X144.783 Y7.052
G1 X141.052 Y10.783 E.16213
G1 X140.817 Y10.484
G1 X144.783 Y6.518 E.17231
G1 X144.783 Y5.985
G1 X140.817 Y9.95 E.17231
G1 X140.817 Y9.417
G1 X144.783 Y5.452 E.17231
G1 X144.783 Y4.919
G1 X140.817 Y8.884 E.17231
G1 X140.817 Y8.351
G1 X144.751 Y4.417 E.17092
G1 X144.217 Y4.417
G1 X140.817 Y7.817 E.14774
G1 X140.817 Y7.284
G1 X143.684 Y4.417 E.12457
G1 X143.151 Y4.417
G1 X140.817 Y6.751 E.1014
G1 X140.817 Y6.218
G1 X142.618 Y4.417 E.07823
G1 X142.084 Y4.417
G1 X140.817 Y5.684 E.05505
G1 X140.817 Y5.151
G1 X141.551 Y4.417 E.03188
; OBJECT_ID: 12
; WIPE_START
G1 F12000
M204 S10000
G1 X140.817 Y5.151 E-.39426
G1 X140.817 Y5.684 E-.20264
G1 X141.121 Y5.381 E-.1631
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 16
M625
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X133.703 Y7.18 Z8.4 F30000
G1 X117.99 Y10.99 Z8.4
G1 Z8
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3242
M204 S5000
G1 X113.61 Y10.99 E.13459
G1 X113.61 Y4.21 E.20833
G1 X117.99 Y4.21 E.13459
G1 X117.99 Y10.93 E.20649
M204 S10000
G1 X117.783 Y10.251 F30000
; FEATURE: Top surface
G1 F3242
M204 S2000
G1 X117.251 Y10.783 E.0231
G1 X116.718 Y10.783
G1 X117.783 Y9.718 E.04627
G1 X117.783 Y9.185
G1 X116.185 Y10.783 E.06944
G1 X115.651 Y10.783
G1 X117.783 Y8.651 E.09261
G1 X117.783 Y8.118
G1 X115.118 Y10.783 E.11579
G1 X114.585 Y10.783
G1 X117.783 Y7.585 E.13896
G1 X117.783 Y7.052
G1 X114.052 Y10.783 E.16213
G1 X113.817 Y10.484
G1 X117.783 Y6.518 E.17231
G1 X117.783 Y5.985
G1 X113.817 Y9.95 E.17231
G1 X113.817 Y9.417
G1 X117.783 Y5.452 E.17231
G1 X117.783 Y4.919
G1 X113.817 Y8.884 E.17231
G1 X113.817 Y8.351
G1 X117.751 Y4.417 E.17092
G1 X117.217 Y4.417
G1 X113.817 Y7.817 E.14774
G1 X113.817 Y7.284
G1 X116.684 Y4.417 E.12457
G1 X116.151 Y4.417
G1 X113.817 Y6.751 E.1014
G1 X113.817 Y6.218
G1 X115.618 Y4.417 E.07823
G1 X115.084 Y4.417
G1 X113.817 Y5.684 E.05505
G1 X113.817 Y5.151
G1 X114.551 Y4.417 E.03188
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F12000
M204 S10000
G1 X113.817 Y5.151 E-.39426
G1 X113.817 Y5.684 E-.20264
G1 X114.121 Y5.381 E-.1631
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
M106 S0
M106 P2 S0
M981 S0 P20000 ; close spaghetti detector
; FEATURE: Custom
; MACHINE_END_GCODE_START
; filament end gcode 

;===== date: 20240528 =====================
M400 ; wait for buffer to clear
G92 E0 ; zero the extruder
G1 E-0.8 F1800 ; retract
G1 Z8.5 F900 ; lower z a little
G1 X65 Y245 F12000 ; move to safe pos
G1 Y265 F3000

G1 X65 Y245 F12000
G1 Y265 F3000
M140 S0 ; turn off bed
M106 S0 ; turn off fan
M106 P2 S0 ; turn off remote part cooling fan
M106 P3 S0 ; turn off chamber cooling fan

G1 X100 F12000 ; wipe
; pull back filament to AMS
M620 S255
G1 X20 Y50 F12000
G1 Y-3
T255
G1 X65 F12000
G1 Y265
G1 X100 F12000 ; wipe
M621 S255
M104 S0 ; turn off hotend

M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S3 ;wait for last picture to be taken
M623; end of "timelapse_record_flag"

M400 ; wait all motion done
M17 S
M17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom

    G1 Z108 F600
    G1 Z106

M400 P100
M17 R ; restore z current

M220 S100  ; Reset feedrate magnitude
M201.2 K1.0 ; Reset acc magnitude
M73.2   R1.0 ;Reset left time magnitude
M1002 set_gcode_claim_speed_level : 0
;=====printer finish  sound=========
M17
M400 S1
M1006 S1
M1006 A0 B20 L100 C37 D20 M40 E42 F20 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C46 D10 M80 E46 F10 N80
M1006 A44 B20 L100 C39 D20 M60 E48 F20 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C39 D10 M60 E39 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C39 D10 M60 E39 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C48 D10 M60 E44 F10 N100
M1006 A0 B10 L100 C0 D10 M60 E0 F10  N100
M1006 A49 B20 L100 C44 D20 M100 E41 F20 N100
M1006 A0 B20 L100 C0 D20 M60 E0 F20 N100
M1006 A0 B20 L100 C37 D20 M30 E37 F20 N60
M1006 W

M17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power
M960 S5 P0 ; turn off logo lamp
M73 P100 R0
; EXECUTABLE_BLOCK_END

