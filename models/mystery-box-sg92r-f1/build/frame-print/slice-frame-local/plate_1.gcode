; HEADER_BLOCK_START
; BambuStudio 02.03.01.51
; model printing time: 18m 41s; total estimated time: 25m 57s
; total layer number: 220
; total filament length [mm] : 3354.28
; total filament volume [cm^3] : 8068.00
; total filament weight [g] : 10.17
; filament_density: 1.26
; filament_diameter: 1.75
; max_z_height: 44.00
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
M73 P0 R25
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
M73 P2 R25
G1 E50 F200
M400
M104 S220
G92 E0
M73 P18 R21
G1 E50 F200
M400
M106 P1 S255
G92 E0
M73 P19 R21
G1 E5 F300
M109 S200 ; drop nozzle temp, make filament shink a bit
G92 E0
M73 P20 R20
G1 E-0.5 F300

G1 X70 F9000
M73 P21 R20
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
    G29 A X20 Y5.99999 I24 J24
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
M73 P22 R20
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
M73 P23 R19
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
M73 P24 R19
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
M73 P25 R19
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
; layer num/total_layer_count: 1/220
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
M204 S6000
G1 Z.4 F30000
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

; OBJECT_ID: 8
G1 X42.45 Y24.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X36.6 Y24.6 E.21789
G1 X36.6 Y7.4 E.64063
G1 X42.45 Y7.4 E.21789
G1 X42.45 Y24.54 E.6384
M204 S6000
G1 X42.45 Y25.057 F30000
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X43.143 Y25.057 E.02581
G1 X43.143 Y27.143 E.07769
G1 X20.857 Y27.143 E.83006
G1 X20.857 Y25.057 E.07769
G1 X27.857 Y25.057 E.26072
G1 X27.857 Y6.943 E.67468
G1 X20.857 Y6.943 E.26072
G1 X20.857 Y4.857 E.07769
G1 X43.143 Y4.857 E.83006
G1 X43.143 Y6.943 E.07769
G1 X36.143 Y6.943 E.26072
G1 X36.143 Y25.057 E.67468
G1 X42.39 Y25.057 E.23268
; WIPE_START
G1 X43.143 Y25.057 E-.28612
G1 X43.143 Y26.304 E-.47388
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X35.555 Y25.483 Z.6 F30000
G1 X27.4 Y24.6 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X21.55 Y24.6 E.21789
G1 X21.55 Y7.4 E.64063
G1 X27.4 Y7.4 E.21789
G1 X27.4 Y24.54 E.6384
; WIPE_START
G1 X25.4 Y24.561 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X32.928 Y25.818 Z.6 F30000
G1 X43.6 Y27.6 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X20.4 Y27.6 E.86411
G1 X20.4 Y4.4 E.86411
G1 X43.6 Y4.4 E.86411
G1 X43.6 Y27.54 E.86188
; WIPE_START
G1 X41.6 Y27.545 E-.76
; WIPE_END
M73 P26 R19
G1 E-.04 F1800
M204 S6000
G1 X43.025 Y24.828 Z.6 F30000
M73 P27 R18
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.73586
G1 F3000
M204 S500
G1 X43.025 Y7.172 E.99701
; WIPE_START
G1 X43.025 Y9.172 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X42.96 Y5.978 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50656
G1 F6300
M204 S500
G1 X42.228 Y5.246 E.03912
G1 X41.572 Y5.246 E.02477
G1 X42.754 Y6.428 E.06317
G1 X42.754 Y6.554 E.00478
G1 X42.225 Y6.554 E.01999
G1 X40.917 Y5.246 E.06993
G1 X40.261 Y5.246 E.02477
G1 X41.57 Y6.554 E.06993
G1 X40.914 Y6.554 E.02477
G1 X39.605 Y5.246 E.06993
G1 X38.949 Y5.246 E.02477
G1 X40.258 Y6.554 E.06993
G1 X39.603 Y6.554 E.02477
G1 X38.294 Y5.246 E.06993
G1 X37.638 Y5.246 E.02477
G1 X38.947 Y6.554 E.06993
G1 X38.291 Y6.554 E.02477
G1 X36.982 Y5.246 E.06993
G1 X36.327 Y5.246 E.02477
G1 X37.636 Y6.554 E.06993
G1 X36.98 Y6.554 E.02477
G1 X35.671 Y5.246 E.06993
G1 X35.015 Y5.246 E.02477
G1 X36.324 Y6.554 E.06993
G1 X35.754 Y6.554 E.02153
G1 X35.754 Y6.64 E.00325
G1 X34.36 Y5.246 E.07452
G1 X33.704 Y5.246 E.02477
G1 X35.754 Y7.296 E.10956
G1 X35.754 Y7.952 E.02477
G1 X33.048 Y5.246 E.14459
G1 X32.393 Y5.246 E.02477
G1 X35.754 Y8.607 E.17962
G1 X35.754 Y9.263 E.02477
G1 X31.737 Y5.246 E.21466
G1 X31.081 Y5.246 E.02477
G1 X35.754 Y9.919 E.24969
G1 X35.754 Y10.574 E.02477
G1 X30.426 Y5.246 E.28472
G1 X29.77 Y5.246 E.02477
G1 X35.754 Y11.23 E.31976
G1 X35.754 Y11.886 E.02477
G1 X29.114 Y5.246 E.35479
G1 X28.458 Y5.246 E.02477
M73 P28 R18
G1 X35.754 Y12.542 E.38982
G1 X35.754 Y13.197 E.02477
G1 X27.803 Y5.246 E.42486
G1 X27.147 Y5.246 E.02477
G1 X35.754 Y13.853 E.45989
G1 X35.754 Y14.509 E.02477
G1 X28.246 Y7 E.4012
G1 X28.246 Y6.554 E.01682
G1 X27.8 Y6.554 E.01682
G1 X26.491 Y5.246 E.06993
G1 X25.836 Y5.246 E.02477
G1 X27.145 Y6.554 E.06993
G1 X26.489 Y6.554 E.02477
G1 X25.18 Y5.246 E.06993
G1 X24.524 Y5.246 E.02477
G1 X25.833 Y6.554 E.06993
G1 X25.178 Y6.554 E.02477
G1 X23.869 Y5.246 E.06993
G1 X23.213 Y5.246 E.02477
G1 X24.522 Y6.554 E.06993
G1 X23.866 Y6.554 E.02477
G1 X22.557 Y5.246 E.06993
G1 X21.902 Y5.246 E.02477
G1 X23.21 Y6.554 E.06993
G1 X22.555 Y6.554 E.02477
G1 X21.246 Y5.246 E.06994
G1 X21.246 Y5.901 E.02476
G1 X22.105 Y6.76 E.04591
; WIPE_START
G1 X21.246 Y5.901 E-.46174
G1 X21.246 Y5.246 E-.24902
G1 X21.337 Y5.337 E-.04924
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X28.04 Y7.45 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X35.754 Y15.164 E.41219
G1 X35.754 Y15.82 E.02477
G1 X28.246 Y8.311 E.4012
G1 X28.246 Y8.967 E.02477
G1 X35.754 Y16.476 E.4012
G1 X35.754 Y17.131 E.02477
G1 X28.246 Y9.622 E.4012
G1 X28.246 Y10.278 E.02477
G1 X35.754 Y17.787 E.4012
G1 X35.754 Y18.443 E.02477
G1 X28.246 Y10.934 E.4012
G1 X28.246 Y11.59 E.02477
G1 X35.754 Y19.098 E.4012
G1 X35.754 Y19.754 E.02477
G1 X28.246 Y12.245 E.4012
G1 X28.246 Y12.901 E.02477
G1 X35.754 Y20.41 E.4012
G1 X35.754 Y21.065 E.02477
G1 X28.246 Y13.557 E.4012
G1 X28.246 Y14.212 E.02477
G1 X35.754 Y21.721 E.4012
G1 X35.754 Y22.377 E.02477
G1 X28.246 Y14.868 E.4012
G1 X28.246 Y15.524 E.02477
G1 X35.754 Y23.032 E.4012
G1 X35.754 Y23.688 E.02477
G1 X28.246 Y16.179 E.4012
G1 X28.246 Y16.835 E.02477
G1 X35.96 Y24.55 E.41219
; WIPE_START
G1 X34.546 Y23.135 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X41.883 Y25.236 Z.6 F30000
G1 X41.896 Y25.24 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X42.754 Y26.098 E.04587
G1 X42.754 Y26.754 E.02477
G1 X41.446 Y25.446 E.06991
G1 X40.79 Y25.446 E.02477
G1 X42.099 Y26.754 E.06993
G1 X41.443 Y26.754 E.02477
G1 X40.135 Y25.446 E.06993
G1 X39.479 Y25.446 E.02477
G1 X40.788 Y26.754 E.06993
G1 X40.132 Y26.754 E.02477
G1 X38.823 Y25.446 E.06993
G1 X38.168 Y25.446 E.02477
G1 X39.476 Y26.754 E.06993
G1 X38.821 Y26.754 E.02477
G1 X37.512 Y25.446 E.06993
G1 X36.856 Y25.446 E.02477
G1 X38.165 Y26.754 E.06993
G1 X37.509 Y26.754 E.02477
G1 X36.2 Y25.446 E.06993
G1 X35.754 Y25.446 E.01685
G1 X35.754 Y25 E.01685
G1 X28.246 Y17.491 E.4012
G1 X28.246 Y18.146 E.02477
G1 X36.854 Y26.754 E.45993
G1 X36.198 Y26.754 E.02477
G1 X28.246 Y18.802 E.4249
G1 X28.246 Y19.458 E.02477
G1 X35.542 Y26.754 E.38986
G1 X34.887 Y26.754 E.02477
G1 X28.246 Y20.113 E.35483
G1 X28.246 Y20.769 E.02477
G1 X34.231 Y26.754 E.3198
G1 X33.575 Y26.754 E.02477
G1 X28.246 Y21.425 E.28476
G1 X28.246 Y22.08 E.02477
G1 X32.919 Y26.754 E.24973
G1 X32.264 Y26.754 E.02477
G1 X28.246 Y22.736 E.2147
G1 X28.246 Y23.392 E.02477
G1 X31.608 Y26.754 E.17966
G1 X30.952 Y26.754 E.02477
G1 X28.246 Y24.048 E.14463
G1 X28.246 Y24.703 E.02477
G1 X30.297 Y26.754 E.1096
G1 X29.641 Y26.754 E.02477
G1 X28.246 Y25.359 E.07456
G1 X28.246 Y25.446 E.00327
G1 X27.677 Y25.446 E.0215
G1 X28.985 Y26.754 E.06993
G1 X28.33 Y26.754 E.02477
G1 X27.021 Y25.446 E.06993
G1 X26.365 Y25.446 E.02477
G1 X27.674 Y26.754 E.06993
G1 X27.018 Y26.754 E.02477
G1 X25.709 Y25.446 E.06993
G1 X25.054 Y25.446 E.02477
G1 X26.363 Y26.754 E.06993
G1 X25.707 Y26.754 E.02477
G1 X24.398 Y25.446 E.06993
G1 X23.742 Y25.446 E.02477
G1 X25.051 Y26.754 E.06993
G1 X24.396 Y26.754 E.02477
G1 X23.087 Y25.446 E.06993
G1 X22.431 Y25.446 E.02477
G1 X23.74 Y26.754 E.06993
G1 X23.084 Y26.754 E.02477
G1 X21.775 Y25.446 E.06993
G1 X21.246 Y25.446 E.02002
M73 P29 R18
G1 X21.246 Y25.571 E.00476
G1 X22.429 Y26.754 E.0632
G1 X21.773 Y26.754 E.02477
G1 X21.04 Y26.021 E.03916
; WIPE_START
G1 X21.773 Y26.754 E-.39389
G1 X22.429 Y26.754 E-.24916
G1 X22.211 Y26.537 E-.11696
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X20.975 Y24.828 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.73586
G1 F3000
M204 S500
G1 X20.975 Y7.172 E.99701
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X20.975 Y9.172 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/220
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

; OBJECT_ID: 8
G1 X42.652 Y24.41
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X42.652 Y24.802 E.01301
G1 X36.398 Y24.802 E.20746
G1 X36.398 Y7.198 E.58396
G1 X42.652 Y7.198 E.20746
G1 X42.652 Y24.35 E.56897
G1 X42.26 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X40.26 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.628 Y24.395 Z.8 F30000
G1 X27.602 Y24.41 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X27.602 Y24.802 E.01301
G1 X21.348 Y24.802 E.20746
G1 X21.348 Y7.198 E.58396
G1 X27.602 Y7.198 E.20746
G1 X27.602 Y24.35 E.56897
G1 X27.21 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.625 Z.8 F30000
G1 X43.398 Y27.398 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.468 Y27.234 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X43.065 Y26.638 E.02605
G1 X43.065 Y26.102 E.01655
G1 X42.102 Y27.065 E.04204
G1 X41.566 Y27.065 E.01655
G1 X43.065 Y25.566 E.06543
G1 X43.065 Y25.339 E.00702
G1 X42.756 Y25.339 E.00952
G1 X41.03 Y27.065 E.07536
G1 X40.494 Y27.065 E.01655
G1 X42.424 Y25.135 E.08425
G1 X41.888 Y25.135 E.01655
G1 X39.959 Y27.065 E.08425
G1 X39.423 Y27.065 E.01655
G1 X41.352 Y25.135 E.08425
G1 X40.816 Y25.135 E.01655
G1 X38.887 Y27.065 E.08425
G1 X38.351 Y27.065 E.01655
G1 X40.28 Y25.135 E.08425
G1 X39.744 Y25.135 E.01655
G1 X37.815 Y27.065 E.08425
G1 X37.279 Y27.065 E.01655
G1 X39.209 Y25.135 E.08425
G1 X38.673 Y25.135 E.01655
G1 X36.743 Y27.065 E.08425
G1 X36.208 Y27.065 E.01655
G1 X38.137 Y25.135 E.08425
G1 X37.601 Y25.135 E.01655
G1 X35.672 Y27.065 E.08425
G1 X35.136 Y27.065 E.01655
G1 X37.065 Y25.135 E.08425
G1 X36.529 Y25.135 E.01655
G1 X34.6 Y27.065 E.08425
G1 X34.064 Y27.065 E.01655
G1 X36.065 Y25.064 E.08736
G1 X36.065 Y24.528 E.01655
G1 X33.528 Y27.065 E.11075
G1 X32.992 Y27.065 E.01655
G1 X36.065 Y23.992 E.13415
G1 X36.065 Y23.457 E.01655
G1 X32.457 Y27.065 E.15755
G1 X31.921 Y27.065 E.01655
G1 X36.065 Y22.921 E.18095
G1 X36.065 Y22.385 E.01655
G1 X31.385 Y27.065 E.20435
G1 X30.849 Y27.065 E.01655
G1 X36.065 Y21.849 E.22775
G1 X36.065 Y21.313 E.01655
G1 X30.313 Y27.065 E.25115
G1 X29.777 Y27.065 E.01655
G1 X36.065 Y20.777 E.27455
G1 X36.065 Y20.241 E.01655
G1 X29.241 Y27.065 E.29794
G1 X28.706 Y27.065 E.01655
G1 X36.065 Y19.706 E.32134
G1 X36.065 Y19.17 E.01655
G1 X28.17 Y27.065 E.34474
G1 X27.634 Y27.065 E.01655
G1 X36.065 Y18.634 E.36814
G1 X36.065 Y18.098 E.01655
G1 X27.098 Y27.065 E.39154
G1 X26.562 Y27.065 E.01655
G1 X36.065 Y17.562 E.41494
G1 X36.065 Y17.026 E.01655
G1 X26.026 Y27.065 E.43834
G1 X25.49 Y27.065 E.01655
G1 X27.42 Y25.135 E.08425
G1 X26.884 Y25.135 E.01655
G1 X24.955 Y27.065 E.08425
G1 X24.419 Y27.065 E.01655
G1 X26.348 Y25.135 E.08425
G1 X25.812 Y25.135 E.01655
G1 X23.883 Y27.065 E.08425
G1 X23.347 Y27.065 E.01655
G1 X25.276 Y25.135 E.08425
G1 X24.74 Y25.135 E.01655
G1 X22.811 Y27.065 E.08425
G1 X22.275 Y27.065 E.01655
G1 X24.205 Y25.135 E.08425
G1 X23.669 Y25.135 E.01655
G1 X21.739 Y27.065 E.08425
G1 X21.203 Y27.065 E.01655
G1 X23.133 Y25.135 E.08425
G1 X22.597 Y25.135 E.01655
G1 X20.935 Y26.797 E.07256
G1 X20.935 Y26.261 E.01655
G1 X22.061 Y25.135 E.04916
G1 X21.525 Y25.135 E.01655
G1 X20.766 Y25.895 E.03317
G1 X20.975 Y25.006 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F15000
G1 X20.975 Y6.994 E.49725
G1 X21.532 Y4.766 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X20.935 Y5.363 E.02607
G1 X20.935 Y5.898 E.01655
G1 X21.898 Y4.935 E.04206
G1 X22.434 Y4.935 E.01655
G1 X20.935 Y6.434 E.06546
G1 X20.935 Y6.661 E.00701
G1 X21.244 Y6.661 E.00954
G1 X22.97 Y4.935 E.07536
G1 X23.506 Y4.935 E.01655
G1 X21.577 Y6.865 E.08425
G1 X22.113 Y6.865 E.01655
G1 X24.042 Y4.935 E.08425
G1 X24.578 Y4.935 E.01655
G1 X22.648 Y6.865 E.08425
G1 X23.184 Y6.865 E.01655
G1 X25.114 Y4.935 E.08425
G1 X25.649 Y4.935 E.01655
G1 X23.72 Y6.865 E.08425
G1 X24.256 Y6.865 E.01655
G1 X26.185 Y4.935 E.08425
G1 X26.721 Y4.935 E.01655
G1 X24.792 Y6.865 E.08425
G1 X25.328 Y6.865 E.01655
G1 X27.257 Y4.935 E.08425
G1 X27.793 Y4.935 E.01655
G1 X25.864 Y6.865 E.08425
G1 X26.399 Y6.865 E.01655
G1 X28.329 Y4.935 E.08425
G1 X28.865 Y4.935 E.01655
G1 X26.935 Y6.865 E.08425
G1 X27.471 Y6.865 E.01655
G1 X29.401 Y4.935 E.08425
G1 X29.936 Y4.935 E.01655
G1 X27.935 Y6.936 E.08738
G1 X27.935 Y7.472 E.01655
G1 X30.472 Y4.935 E.11078
G1 X31.008 Y4.935 E.01655
G1 X27.935 Y8.008 E.13417
G1 X27.935 Y8.544 E.01655
G1 X31.544 Y4.935 E.15757
G1 X32.08 Y4.935 E.01655
G1 X27.935 Y9.08 E.18097
G1 X27.935 Y9.616 E.01655
G1 X32.616 Y4.935 E.20437
G1 X33.152 Y4.935 E.01655
G1 X27.935 Y10.152 E.22777
G1 X27.935 Y10.687 E.01655
G1 X33.687 Y4.935 E.25117
G1 X34.223 Y4.935 E.01655
G1 X27.935 Y11.223 E.27457
G1 X27.935 Y11.759 E.01655
G1 X34.759 Y4.935 E.29797
G1 X35.295 Y4.935 E.01655
G1 X27.935 Y12.295 E.32136
G1 X27.935 Y12.831 E.01655
G1 X35.831 Y4.935 E.34476
G1 X36.367 Y4.935 E.01655
G1 X27.935 Y13.367 E.36816
G1 X27.935 Y13.903 E.01655
G1 X36.903 Y4.935 E.39156
G1 X37.438 Y4.935 E.01655
G1 X27.766 Y14.608 E.42237
G1 X27.766 Y24.789 F30000
G1 F15000
G1 X36.065 Y16.49 E.36238
G1 X36.065 Y15.955 E.01655
G1 X27.935 Y24.084 E.35498
G1 X27.935 Y23.548 E.01655
G1 X36.065 Y15.419 E.35498
G1 X36.065 Y14.883 E.01655
G1 X27.935 Y23.012 E.35498
G1 X27.935 Y22.476 E.01655
G1 X36.065 Y14.347 E.35498
G1 X36.065 Y13.811 E.01655
G1 X27.935 Y21.94 E.35498
G1 X27.935 Y21.405 E.01655
G1 X36.065 Y13.275 E.35498
G1 X36.065 Y12.739 E.01655
G1 X27.935 Y20.869 E.35498
G1 X27.935 Y20.333 E.01655
G1 X36.065 Y12.203 E.35498
M73 P30 R18
G1 X36.065 Y11.668 E.01655
G1 X27.935 Y19.797 E.35497
G1 X27.935 Y19.261 E.01655
G1 X36.065 Y11.132 E.35497
G1 X36.065 Y10.596 E.01655
G1 X27.935 Y18.725 E.35497
G1 X27.935 Y18.189 E.01655
G1 X36.065 Y10.06 E.35497
G1 X36.065 Y9.524 E.01655
G1 X27.935 Y17.654 E.35497
G1 X27.935 Y17.118 E.01655
G1 X36.065 Y8.988 E.35497
G1 X36.065 Y8.452 E.01655
G1 X27.935 Y16.582 E.35497
G1 X27.935 Y16.046 E.01655
G1 X36.065 Y7.917 E.35497
G1 X36.065 Y7.381 E.01655
G1 X27.935 Y15.51 E.35497
G1 X27.935 Y14.974 E.01655
G1 X37.974 Y4.935 E.43836
G1 X38.51 Y4.935 E.01655
G1 X36.581 Y6.865 E.08425
G1 X37.117 Y6.865 E.01655
G1 X39.046 Y4.935 E.08425
G1 X39.582 Y4.935 E.01655
G1 X37.652 Y6.865 E.08425
G1 X38.188 Y6.865 E.01655
G1 X40.118 Y4.935 E.08425
G1 X40.654 Y4.935 E.01655
G1 X38.724 Y6.865 E.08425
G1 X39.26 Y6.865 E.01655
G1 X41.189 Y4.935 E.08425
G1 X41.725 Y4.935 E.01655
G1 X39.796 Y6.865 E.08425
G1 X40.332 Y6.865 E.01655
G1 X42.261 Y4.935 E.08425
G1 X42.797 Y4.935 E.01655
G1 X40.868 Y6.865 E.08425
G1 X41.403 Y6.865 E.01655
G1 X43.065 Y5.203 E.07254
G1 X43.065 Y5.739 E.01655
G1 X41.939 Y6.865 E.04914
G1 X42.475 Y6.865 E.01655
G1 X43.234 Y6.106 E.03315
G1 X43.025 Y6.994 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F15000
G1 X43.025 Y25.006 E.49725
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X43.025 Y23.006 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/220
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
G17
G3 Z.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.652 Y24.41
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X42.652 Y24.802 E.01301
G1 X36.398 Y24.802 E.20746
G1 X36.398 Y7.198 E.58396
G1 X42.652 Y7.198 E.20746
G1 X42.652 Y24.35 E.56897
G1 X42.26 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X40.26 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.628 Y24.395 Z1 F30000
G1 X27.602 Y24.41 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X27.602 Y24.802 E.01301
G1 X21.348 Y24.802 E.20746
G1 X21.348 Y7.198 E.58396
G1 X27.602 Y7.198 E.20746
G1 X27.602 Y24.35 E.56897
G1 X27.21 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.625 Z1 F30000
G1 X43.398 Y27.398 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.025 Y25.006 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F15000
G1 X43.025 Y6.994 E.49725
G1 X43.234 Y5.532 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X42.638 Y4.935 E.02605
G1 X42.102 Y4.935 E.01655
G1 X43.065 Y5.898 E.04204
G1 X43.065 Y6.434 E.01655
G1 X41.566 Y4.935 E.06543
G1 X41.03 Y4.935 E.01655
G1 X42.756 Y6.661 E.07536
G1 X42.501 Y6.661 E.00789
G1 X42.501 Y6.865 E.00628
G1 X42.424 Y6.865 E.00238
G1 X40.494 Y4.935 E.08425
G1 X39.959 Y4.935 E.01655
G1 X41.888 Y6.865 E.08425
G1 X41.352 Y6.865 E.01655
G1 X39.423 Y4.935 E.08425
G1 X38.887 Y4.935 E.01655
G1 X40.816 Y6.865 E.08425
G1 X40.28 Y6.865 E.01655
G1 X38.351 Y4.935 E.08425
G1 X37.815 Y4.935 E.01655
G1 X39.744 Y6.865 E.08425
G1 X39.209 Y6.865 E.01655
G1 X37.279 Y4.935 E.08425
G1 X36.743 Y4.935 E.01655
G1 X38.673 Y6.865 E.08425
G1 X38.137 Y6.865 E.01655
G1 X36.208 Y4.935 E.08425
G1 X35.672 Y4.935 E.01655
G1 X37.601 Y6.865 E.08425
G1 X37.065 Y6.865 E.01655
G1 X35.136 Y4.935 E.08425
G1 X34.6 Y4.935 E.01655
G1 X36.529 Y6.865 E.08425
G1 X36.065 Y6.865 E.01435
G1 X36.065 Y6.936 E.0022
G1 X34.064 Y4.935 E.08736
G1 X33.528 Y4.935 E.01655
G1 X36.065 Y7.472 E.11075
G1 X36.065 Y8.008 E.01655
G1 X32.992 Y4.935 E.13415
G1 X32.457 Y4.935 E.01655
G1 X36.065 Y8.543 E.15755
G1 X36.065 Y9.079 E.01655
G1 X31.921 Y4.935 E.18095
G1 X31.385 Y4.935 E.01655
G1 X36.065 Y9.615 E.20435
G1 X36.065 Y10.151 E.01655
G1 X30.849 Y4.935 E.22775
G1 X30.313 Y4.935 E.01655
G1 X36.065 Y10.687 E.25115
G1 X36.065 Y11.223 E.01655
G1 X29.777 Y4.935 E.27455
G1 X29.241 Y4.935 E.01655
G1 X36.065 Y11.759 E.29794
G1 X36.065 Y12.294 E.01655
G1 X28.706 Y4.935 E.32134
G1 X28.17 Y4.935 E.01655
G1 X36.065 Y12.83 E.34474
G1 X36.065 Y13.366 E.01655
G1 X27.634 Y4.935 E.36814
G1 X27.098 Y4.935 E.01655
G1 X36.065 Y13.902 E.39154
G1 X36.065 Y14.438 E.01655
G1 X26.562 Y4.935 E.41494
G1 X26.026 Y4.935 E.01655
G1 X36.065 Y14.974 E.43834
G1 X36.065 Y15.51 E.01655
G1 X27.935 Y7.38 E.35498
G1 X27.935 Y7.916 E.01655
G1 X36.065 Y16.045 E.35498
G1 X36.065 Y16.581 E.01655
G1 X27.935 Y8.452 E.35498
G1 X27.935 Y8.988 E.01655
G1 X36.065 Y17.117 E.35498
G1 X36.065 Y17.653 E.01655
G1 X27.935 Y9.524 E.35498
G1 X27.935 Y10.06 E.01655
G1 X36.065 Y18.189 E.35498
G1 X36.065 Y18.725 E.01655
G1 X27.935 Y10.595 E.35498
G1 X27.935 Y11.131 E.01655
G1 X36.065 Y19.261 E.35498
G1 X36.065 Y19.797 E.01655
G1 X27.935 Y11.667 E.35498
G1 X27.935 Y12.203 E.01655
G1 X36.065 Y20.332 E.35498
G1 X36.065 Y20.868 E.01655
G1 X27.935 Y12.739 E.35498
G1 X27.935 Y13.275 E.01655
G1 X36.065 Y21.404 E.35497
G1 X36.065 Y21.94 E.01655
G1 X27.935 Y13.811 E.35497
G1 X27.935 Y14.346 E.01655
G1 X36.065 Y22.476 E.35497
G1 X36.065 Y23.012 E.01655
G1 X27.935 Y14.882 E.35497
G1 X27.935 Y15.418 E.01655
G1 X36.065 Y23.548 E.35497
G1 X36.065 Y24.083 E.01655
G1 X27.935 Y15.954 E.35497
G1 X27.935 Y16.49 E.01655
G1 X36.065 Y24.619 E.35497
G1 X36.065 Y25.135 E.01593
G1 X36.581 Y25.135 E.01593
G1 X38.51 Y27.065 E.08425
G1 X39.046 Y27.065 E.01655
G1 X37.117 Y25.135 E.08425
G1 X37.652 Y25.135 E.01655
G1 X39.582 Y27.065 E.08425
G1 X40.118 Y27.065 E.01655
G1 X38.188 Y25.135 E.08425
G1 X38.724 Y25.135 E.01655
G1 X40.654 Y27.065 E.08425
G1 X41.189 Y27.065 E.01655
G1 X39.26 Y25.135 E.08425
G1 X39.796 Y25.135 E.01655
G1 X41.725 Y27.065 E.08425
G1 X42.261 Y27.065 E.01655
G1 X40.332 Y25.135 E.08425
G1 X40.868 Y25.135 E.01655
G1 X42.797 Y27.065 E.08425
G1 X43.065 Y27.065 E.00826
G1 X43.065 Y26.796 E.00828
G1 X41.403 Y25.135 E.07254
G1 X41.939 Y25.135 E.01655
G1 X43.065 Y26.261 E.04914
G1 X43.065 Y25.725 E.01655
G1 X42.306 Y24.966 E.03315
G1 X38.144 Y27.234 F30000
G1 F15000
G1 X27.935 Y17.026 E.44577
G1 X27.935 Y17.562 E.01655
G1 X37.438 Y27.065 E.41496
G1 X36.903 Y27.065 E.01655
G1 X27.935 Y18.097 E.39156
G1 X27.935 Y18.633 E.01655
G1 X36.367 Y27.065 E.36816
G1 X35.831 Y27.065 E.01655
G1 X27.935 Y19.169 E.34476
G1 X27.935 Y19.705 E.01655
G1 X35.295 Y27.065 E.32136
G1 X34.759 Y27.065 E.01655
G1 X27.935 Y20.241 E.29797
G1 X27.935 Y20.777 E.01655
G1 X34.223 Y27.065 E.27457
G1 X33.687 Y27.065 E.01655
G1 X27.935 Y21.313 E.25117
G1 X27.935 Y21.848 E.01655
G1 X33.152 Y27.065 E.22777
G1 X32.616 Y27.065 E.01655
G1 X27.935 Y22.384 E.20437
G1 X27.935 Y22.92 E.01655
G1 X32.08 Y27.065 E.18097
G1 X31.544 Y27.065 E.01655
G1 X27.935 Y23.456 E.15757
G1 X27.935 Y23.992 E.01655
G1 X31.008 Y27.065 E.13417
G1 X30.472 Y27.065 E.01655
G1 X27.935 Y24.528 E.11078
G1 X27.935 Y25.064 E.01655
G1 X29.936 Y27.065 E.08738
G1 X29.401 Y27.065 E.01655
G1 X27.471 Y25.135 E.08425
G1 X26.935 Y25.135 E.01655
G1 X28.865 Y27.065 E.08425
G1 X28.329 Y27.065 E.01655
G1 X26.399 Y25.135 E.08425
G1 X25.864 Y25.135 E.01655
G1 X27.793 Y27.065 E.08425
G1 X27.257 Y27.065 E.01655
G1 X25.328 Y25.135 E.08425
G1 X24.792 Y25.135 E.01655
G1 X26.721 Y27.065 E.08425
G1 X26.185 Y27.065 E.01655
G1 X24.256 Y25.135 E.08425
G1 X23.72 Y25.135 E.01655
G1 X25.649 Y27.065 E.08425
G1 X25.114 Y27.065 E.01655
G1 X23.184 Y25.135 E.08425
G1 X22.648 Y25.135 E.01655
G1 X24.578 Y27.065 E.08425
G1 X24.042 Y27.065 E.01655
G1 X22.113 Y25.135 E.08425
G1 X21.577 Y25.135 E.01655
G1 X23.506 Y27.065 E.08425
G1 X22.97 Y27.065 E.01655
G1 X21.244 Y25.339 E.07536
G1 X20.935 Y25.339 E.00954
G1 X20.935 Y25.566 E.00701
G1 X22.434 Y27.065 E.06546
G1 X21.898 Y27.065 E.01655
G1 X20.935 Y26.102 E.04206
G1 X20.935 Y26.637 E.01655
G1 X21.532 Y27.234 E.02607
G1 X20.975 Y25.006 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F15000
G1 X20.975 Y6.994 E.49725
G1 X21.695 Y7.034 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X20.935 Y6.275 E.03317
G1 X20.935 Y5.739 E.01655
G1 X22.061 Y6.865 E.04916
G1 X22.597 Y6.865 E.01655
G1 X20.935 Y5.203 E.07256
G1 X20.935 Y4.935 E.00826
G1 X21.203 Y4.935 E.00828
G1 X23.133 Y6.865 E.08425
G1 X23.669 Y6.865 E.01655
G1 X21.739 Y4.935 E.08425
G1 X22.275 Y4.935 E.01655
G1 X24.205 Y6.865 E.08425
G1 X24.74 Y6.865 E.01655
M73 P30 R17
G1 X22.811 Y4.935 E.08425
G1 X23.347 Y4.935 E.01655
G1 X25.276 Y6.865 E.08425
G1 X25.812 Y6.865 E.01655
G1 X23.883 Y4.935 E.08425
G1 X24.419 Y4.935 E.01655
G1 X26.348 Y6.865 E.08425
G1 X26.884 Y6.865 E.01655
G1 X24.955 Y4.935 E.08425
G1 X25.49 Y4.935 E.01655
G1 X27.589 Y7.034 E.09166
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X26.175 Y5.62 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/220
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
G17
G3 Z1 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.652 Y24.41
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8727
G1 X42.652 Y24.802 E.01301
G1 X36.398 Y24.802 E.20746
G1 X36.398 Y7.198 E.58396
G1 X42.652 Y7.198 E.20746
G1 X42.652 Y24.35 E.56897
G1 X42.26 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8727
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X40.26 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.628 Y24.395 Z1.2 F30000
G1 X27.602 Y24.41 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8727
G1 X27.602 Y24.802 E.01301
G1 X21.348 Y24.802 E.20746
G1 X21.348 Y7.198 E.58396
G1 X27.602 Y7.198 E.20746
G1 X27.602 Y24.35 E.56897
G1 X27.21 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8727
M204 S5000
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.625 Z1.2 F30000
G1 X43.398 Y27.398 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8727
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8727
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.025 Y25.006 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F8727
G1 X43.025 Y6.994 E.49725
G1 X22.579 Y4.95 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8727
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F8727
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
G1 X20.975 Y6.994 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F8727
G1 X20.975 Y25.006 E.49725
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.975 Y23.006 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/220
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
G17
G3 Z1.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.652 Y24.41
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8557
G1 X42.652 Y24.802 E.01301
G1 X36.398 Y24.802 E.20746
G1 X36.398 Y7.198 E.58396
G1 X42.652 Y7.198 E.20746
G1 X42.652 Y24.35 E.56897
G1 X42.26 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8557
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X40.26 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.628 Y24.395 Z1.4 F30000
G1 X27.602 Y24.41 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8557
G1 X27.602 Y24.802 E.01301
G1 X21.348 Y24.802 E.20746
G1 X21.348 Y7.198 E.58396
G1 X27.602 Y7.198 E.20746
G1 X27.602 Y24.35 E.56897
G1 X27.21 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8557
M204 S5000
M73 P31 R17
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.625 Z1.4 F30000
G1 X43.398 Y27.398 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8557
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8557
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y27.05 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8557
G1 X43.05 Y27.05 E.05401
G1 X41.15 Y25.15 E.0891
G1 X38.202 Y25.15 E.09782
G1 X36.302 Y27.05 E.0891
G1 X35.374 Y27.05 E.0308
G1 X27.95 Y19.626 E.34825
G1 X27.95 Y20.05 E.01405
G1 X36.05 Y11.95 E.37996
G1 X36.05 Y12.374 E.01405
G1 X28.626 Y4.95 E.34825
G1 X27.698 Y4.95 E.0308
G1 X25.798 Y6.85 E.0891
G1 X22.85 Y6.85 E.09782
G1 X20.95 Y4.95 E.0891
G1 X22.579 Y4.95 E.05401
G1 X20.975 Y6.994 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F8557
G1 X20.975 Y25.006 E.49725
G1 X43.025 Y25.006 F30000
G1 F8557
G1 X43.025 Y6.994 E.49725
G1 X41.421 Y4.95 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8557
G1 X43.05 Y4.95 E.05401
G1 X41.15 Y6.85 E.0891
G1 X38.202 Y6.85 E.09782
G1 X36.302 Y4.95 E.0891
G1 X35.374 Y4.95 E.0308
G1 X27.95 Y12.374 E.34825
G1 X27.95 Y11.95 E.01405
G1 X36.05 Y20.05 E.37996
G1 X36.05 Y19.626 E.01405
G1 X28.626 Y27.05 E.34825
G1 X27.698 Y27.05 E.0308
G1 X25.798 Y25.15 E.0891
G1 X22.85 Y25.15 E.09782
G1 X20.95 Y27.05 E.0891
G1 X22.579 Y27.05 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X20.95 Y27.05 E-.61876
G1 X21.213 Y26.787 E-.14124
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/220
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
G17
G3 Z1.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.652 Y24.41
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F8710
G1 X42.652 Y24.802 E.01301
G1 X36.398 Y24.802 E.20746
G1 X36.398 Y7.198 E.58396
G1 X42.652 Y7.198 E.20746
G1 X42.652 Y24.35 E.56897
G1 X42.26 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8710
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X40.26 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.628 Y24.395 Z1.6 F30000
G1 X27.602 Y24.41 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8710
G1 X27.602 Y24.802 E.01301
G1 X21.348 Y24.802 E.20746
G1 X21.348 Y7.198 E.58396
G1 X27.602 Y7.198 E.20746
G1 X27.602 Y24.35 E.56897
G1 X27.21 Y24.41 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8710
M204 S5000
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.625 Z1.6 F30000
G1 X43.398 Y27.398 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8710
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8710
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.025 Y25.006 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F8710
G1 X43.025 Y6.994 E.49725
G1 X22.579 Y4.95 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8710
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F8710
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
G1 X20.975 Y6.994 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.38172
G1 F8710
G1 X20.975 Y25.006 E.49725
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.975 Y23.006 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/220
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
G17
G3 Z1.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.26 Y24.41
G1 Z1.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10535
M204 S5000
G1 X36.79 Y24.41 E.16808
G1 X36.79 Y7.59 E.51683
G1 X42.26 Y7.59 E.16808
G1 X42.26 Y24.35 E.51499
M204 S10000
G1 X42.26 Y25.278 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F10535
G1 X43.398 Y25.278 E.03775
G1 X43.398 Y27.398 E.07033
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y25.278 E.07033
G1 X23.268 Y25.278 E.08843
G1 X23.268 Y24.802 E.01578
G1 X27.602 Y24.802 E.14377
G1 X27.602 Y7.198 E.58396
G1 X23.268 Y7.198 E.14377
G1 X23.268 Y6.722 E.01578
G1 X20.602 Y6.722 E.08843
G1 X20.602 Y4.602 E.07033
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y6.722 E.07033
G1 X40.732 Y6.722 E.08843
G1 X40.732 Y7.198 E.01578
G1 X36.398 Y7.198 E.14377
G1 X36.398 Y24.802 E.58396
G1 X40.732 Y24.802 E.14377
G1 X40.732 Y25.278 E.01578
G1 X42.2 Y25.278 E.04869
; WIPE_START
G1 F15476.087
G1 X43.398 Y25.278 E-.45522
G1 X43.398 Y26.08 E-.30478
; WIPE_END
G1 E-.04 F1800
G1 X35.806 Y25.297 Z1.8 F30000
G1 X27.21 Y24.41 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F10535
M204 S5000
G1 X21.74 Y24.41 E.16808
G1 X21.74 Y7.59 E.51683
G1 X27.21 Y7.59 E.16808
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.717 Y25.753 Z1.8 F30000
G1 X43.79 Y27.79 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F10535
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y27.05 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10535
G1 X43.05 Y27.05 E.05401
G1 X41.626 Y25.626 E.06679
G1 X40.384 Y25.626 E.0412
G1 X40.384 Y25.15 E.01578
G1 X38.202 Y25.15 E.07239
G1 X36.302 Y27.05 E.0891
G1 X35.374 Y27.05 E.0308
G1 X27.95 Y19.626 E.34825
G1 X27.95 Y20.05 E.01405
G1 X36.05 Y11.95 E.37996
G1 X36.05 Y12.374 E.01405
G1 X28.626 Y4.95 E.34825
G1 X27.698 Y4.95 E.0308
G1 X25.798 Y6.85 E.0891
G1 X23.616 Y6.85 E.07239
G1 X23.616 Y6.374 E.01578
G1 X22.374 Y6.374 E.0412
G1 X20.95 Y4.95 E.06679
G1 X22.579 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X20.95 Y4.95 E-.61876
G1 X21.213 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X22.193 Y6.993 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F10535
M204 S2000
G1 X22.583 Y7.383 E.01694
G1 X22.049 Y7.383
G1 X21.66 Y6.993 E.01694
G1 X21.078 Y6.945
G1 X21.533 Y7.399 E.01974
G1 X21.533 Y7.932
G1 X20.545 Y6.945 E.04292
G1 X20.417 Y7.35
G1 X21.533 Y8.466 E.04846
G1 X21.533 Y8.999
G1 X20.417 Y7.884 E.04846
G1 X20.417 Y8.417
G1 X21.533 Y9.532 E.04846
G1 X21.533 Y10.065
G1 X20.417 Y8.95 E.04846
G1 X20.417 Y9.483
G1 X21.533 Y10.599 E.04846
G1 X21.533 Y11.132
G1 X20.417 Y10.017 E.04846
G1 X20.417 Y10.55
G1 X21.533 Y11.665 E.04846
G1 X21.533 Y12.198
G1 X20.417 Y11.083 E.04846
G1 X20.417 Y11.616
G1 X21.533 Y12.732 E.04846
G1 X21.533 Y13.265
G1 X20.417 Y12.15 E.04846
G1 X20.417 Y12.683
G1 X21.533 Y13.798 E.04846
G1 X21.533 Y14.331
G1 X20.417 Y13.216 E.04846
G1 X20.417 Y13.749
M73 P32 R17
G1 X21.533 Y14.865 E.04846
G1 X21.533 Y15.398
G1 X20.417 Y14.283 E.04846
G1 X20.417 Y14.816
G1 X21.533 Y15.931 E.04846
G1 X21.533 Y16.464
G1 X20.417 Y15.349 E.04846
G1 X20.417 Y15.882
G1 X21.533 Y16.998 E.04846
G1 X21.533 Y17.531
G1 X20.417 Y16.416 E.04846
G1 X20.417 Y16.949
G1 X21.533 Y18.064 E.04846
G1 X21.533 Y18.597
G1 X20.417 Y17.482 E.04846
G1 X20.417 Y18.016
G1 X21.533 Y19.131 E.04846
G1 X21.533 Y19.664
G1 X20.417 Y18.549 E.04846
G1 X20.417 Y19.082
G1 X21.533 Y20.197 E.04846
G1 X21.533 Y20.731
G1 X20.417 Y19.615 E.04846
G1 X20.417 Y20.149
G1 X21.533 Y21.264 E.04846
G1 X21.533 Y21.797
G1 X20.417 Y20.682 E.04846
G1 X20.417 Y21.215
G1 X21.533 Y22.33 E.04846
G1 X21.533 Y22.864
G1 X20.417 Y21.748 E.04846
G1 X20.417 Y22.282
G1 X21.533 Y23.397 E.04846
G1 X21.533 Y23.93
G1 X20.417 Y22.815 E.04846
G1 X20.417 Y23.348
G1 X21.533 Y24.463 E.04846
G1 X22.22 Y24.617
G1 X22.535 Y24.932 E.01369
G1 X22.076 Y25.007
G1 X21.687 Y24.617 E.01694
G1 X21.543 Y25.007
G1 X20.417 Y23.881 E.04892
G1 X20.417 Y24.415
G1 X21.058 Y25.055 E.02784
; WIPE_START
G1 F12000
M204 S10000
G1 X20.417 Y24.415 E-.3443
G1 X20.417 Y23.881 E-.20264
G1 X20.814 Y24.278 E-.21306
; WIPE_END
G1 E-.04 F1800
G1 X21.176 Y16.654 Z1.8 F30000
G1 X21.62 Y7.312 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.103666
G1 F10535
G1 X21.733 Y7.373 E.00064
; LINE_WIDTH: 0.0868654
G1 X21.728 Y7.387 E.00005
; LINE_WIDTH: 0.0607554
G1 X21.723 Y7.401 E.00002
G1 X21.554 Y6.95 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.51852
G1 F10535
G3 X21.465 Y6.899 I-.059 J0 E.00961
; WIPE_START
G1 F12000
G1 X21.435 Y6.95 E-.18865
G1 X21.465 Y7.002 E-.19045
G1 X21.525 Y7.002 E-.19044
G1 X21.554 Y6.95 E-.19046
; WIPE_END
G1 E-.04 F1800
G1 X22.112 Y14.562 Z1.8 F30000
G1 X22.861 Y24.792 Z1.8
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.50744
G1 F10535
G2 X22.859 Y24.892 I-.029 J.05 E.00907
G1 X21.553 Y25.05 F30000
G1 F10535
G3 X21.465 Y25.001 I-.058 J0 E.00907
; WIPE_START
G1 F12000
G1 X21.437 Y25.05 E-.1852
G1 X21.466 Y25.1 E-.1916
G1 X21.524 Y25.1 E-.1916
G1 X21.553 Y25.05 E-.1916
; WIPE_END
G1 E-.04 F1800
G1 X29.185 Y25.05 Z1.8 F30000
G1 X42.565 Y25.05 Z1.8
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.5185
G1 F10535
G3 X42.475 Y24.999 I-.059 J0 E.00961
; WIPE_START
G1 F12000
G1 X42.446 Y25.05 E-.18867
G1 X42.475 Y25.101 E-.19045
G1 X42.535 Y25.101 E-.19044
G1 X42.565 Y25.05 E-.19045
; WIPE_END
G1 E-.04 F1800
G1 X42.564 Y17.417 Z1.8 F30000
G1 X42.563 Y6.95 Z1.8
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.50742
G1 F10535
G3 X42.475 Y6.901 I-.058 J0 E.00907
G1 X41.197 Y7.108 F30000
G1 F10535
G2 X41.195 Y7.208 I-.029 J.05 E.00907
G1 X42.942 Y6.945 F30000
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F10535
M204 S2000
G1 X43.583 Y7.586 E.02785
G1 X43.583 Y8.119
G1 X42.457 Y6.993 E.04893
G1 X42.313 Y7.383
G1 X41.923 Y6.993 E.01694
G1 X41.465 Y7.068
G1 X41.78 Y7.383 E.01368
G1 X42.467 Y7.537
G1 X43.583 Y8.652 E.04846
G1 X43.583 Y9.185
G1 X42.467 Y8.07 E.04846
G1 X42.467 Y8.603
G1 X43.583 Y9.719 E.04846
G1 X43.583 Y10.252
G1 X42.467 Y9.137 E.04846
G1 X42.467 Y9.67
G1 X43.583 Y10.785 E.04846
G1 X43.583 Y11.318
G1 X42.467 Y10.203 E.04846
G1 X42.467 Y10.736
G1 X43.583 Y11.852 E.04846
G1 X43.583 Y12.385
G1 X42.467 Y11.27 E.04846
G1 X42.467 Y11.803
G1 X43.583 Y12.918 E.04846
G1 X43.583 Y13.451
G1 X42.467 Y12.336 E.04846
G1 X42.467 Y12.869
G1 X43.583 Y13.985 E.04846
G1 X43.583 Y14.518
G1 X42.467 Y13.403 E.04846
G1 X42.467 Y13.936
G1 X43.583 Y15.051 E.04846
G1 X43.583 Y15.584
G1 X42.467 Y14.469 E.04846
G1 X42.467 Y15.002
G1 X43.583 Y16.118 E.04846
G1 X43.583 Y16.651
G1 X42.467 Y15.536 E.04846
G1 X42.467 Y16.069
G1 X43.583 Y17.184 E.04846
G1 X43.583 Y17.717
G1 X42.467 Y16.602 E.04846
G1 X42.467 Y17.135
G1 X43.583 Y18.251 E.04846
G1 X43.583 Y18.784
G1 X42.467 Y17.669 E.04846
G1 X42.467 Y18.202
G1 X43.583 Y19.317 E.04846
G1 X43.583 Y19.85
G1 X42.467 Y18.735 E.04846
G1 X42.467 Y19.268
G1 X43.583 Y20.384 E.04846
G1 X43.583 Y20.917
G1 X42.467 Y19.802 E.04846
G1 X42.467 Y20.335
G1 X43.583 Y21.45 E.04846
G1 X43.583 Y21.983
G1 X42.467 Y20.868 E.04846
G1 X42.467 Y21.402
G1 X43.583 Y22.517 E.04846
G1 X43.583 Y23.05
G1 X42.467 Y21.935 E.04846
G1 X42.467 Y22.468
G1 X43.583 Y23.583 E.04846
G1 X43.583 Y24.117
G1 X42.467 Y23.001 E.04846
G1 X42.467 Y23.535
G1 X43.583 Y24.65 E.04846
G1 X43.455 Y25.055
G1 X42.467 Y24.068 E.04291
G1 X42.467 Y24.601
G1 X42.922 Y25.055 E.01974
G1 X42.34 Y25.007
G1 X41.95 Y24.617 E.01694
G1 X41.417 Y24.617
G1 X41.807 Y25.007 E.01694
M204 S10000
G1 X42.38 Y24.688 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.103603
G1 F10535
G1 X42.267 Y24.627 E.00064
; LINE_WIDTH: 0.0868404
G1 X42.272 Y24.613 E.00005
; LINE_WIDTH: 0.0609204
G1 X42.277 Y24.599 E.00002
; WIPE_START
G1 F15000
G1 X42.272 Y24.613 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.942 Y16.987 Z1.8 F30000
G1 X41.421 Y4.95 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F10535
G1 X43.05 Y4.95 E.05401
G1 X41.626 Y6.374 E.06679
G1 X40.384 Y6.374 E.0412
G1 X40.384 Y6.85 E.01578
G1 X38.202 Y6.85 E.07239
G1 X36.302 Y4.95 E.0891
G1 X35.374 Y4.95 E.0308
G1 X27.95 Y12.374 E.34825
G1 X27.95 Y11.95 E.01405
G1 X36.05 Y20.05 E.37996
G1 X36.05 Y19.626 E.01405
G1 X28.626 Y27.05 E.34825
G1 X27.698 Y27.05 E.0308
G1 X25.798 Y25.15 E.0891
G1 X23.616 Y25.15 E.07239
G1 X23.616 Y25.626 E.01578
G1 X22.374 Y25.626 E.0412
G1 X20.95 Y27.05 E.06679
G1 X22.579 Y27.05 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X20.95 Y27.05 E-.61876
G1 X21.213 Y26.787 E-.14124
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/220
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
G17
G3 Z1.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z1.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7787
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z2 F30000
G1 X27.21 Y24.41 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z2 F30000
G1 X43.79 Y27.79 Z2
G1 Z1.6
G1 E.8 F1800
G1 F7787
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y24.606 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.936 Y7.801 Z2 F30000
G1 X22.579 Y4.95 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7787
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F7787
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X43.05 Y4.95 E-.61876
G1 X42.787 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X35.191 Y5.96 Z2 F30000
G1 X20.6 Y7.394 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X20.6 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/220
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
G17
G3 Z2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z1.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z2.2 F30000
G1 X27.21 Y24.41 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z2.2 F30000
G1 X43.79 Y27.79 Z2.2
G1 Z1.8
G1 E.8 F1800
G1 F7739
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y27.05 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y27.05 E.05401
G1 X41.15 Y25.15 E.0891
G1 X38.202 Y25.15 E.09782
G1 X36.302 Y27.05 E.0891
G1 X35.374 Y27.05 E.0308
G1 X27.95 Y19.626 E.34825
G1 X27.95 Y20.05 E.01405
G1 X36.05 Y11.95 E.37996
G1 X36.05 Y12.374 E.01405
G1 X28.626 Y4.95 E.34825
G1 X27.698 Y4.95 E.0308
G1 X25.798 Y6.85 E.0891
G1 X22.85 Y6.85 E.09782
G1 X20.95 Y4.95 E.0891
G1 X22.579 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X20.95 Y4.95 E-.61876
G1 X21.213 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y7.394 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7739
G1 X20.6 Y24.606 E.54411
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.203 Y23.273 Z2.2 F30000
G1 X43.4 Y24.606 Z2.2
G1 Z1.8
G1 E.8 F1800
G1 F7739
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y4.95 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y4.95 E.05401
G1 X41.15 Y6.85 E.0891
G1 X38.202 Y6.85 E.09782
G1 X36.302 Y4.95 E.0891
G1 X35.374 Y4.95 E.0308
G1 X27.95 Y12.374 E.34825
G1 X27.95 Y11.95 E.01405
G1 X36.05 Y20.05 E.37996
G1 X36.05 Y19.626 E.01405
G1 X28.626 Y27.05 E.34825
M73 P33 R17
G1 X27.698 Y27.05 E.0308
G1 X25.798 Y25.15 E.0891
G1 X22.85 Y25.15 E.09782
G1 X20.95 Y27.05 E.0891
G1 X22.579 Y27.05 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X20.95 Y27.05 E-.61876
G1 X21.213 Y26.787 E-.14124
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/220
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
G17
G3 Z2.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7787
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z2.4 F30000
G1 X27.21 Y24.41 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z2.4 F30000
G1 X43.79 Y27.79 Z2.4
G1 Z2
G1 E.8 F1800
G1 F7787
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y24.606 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.936 Y7.801 Z2.4 F30000
G1 X22.579 Y4.95 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7787
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F7787
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X43.05 Y4.95 E-.61876
G1 X42.787 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X35.191 Y5.96 Z2.4 F30000
G1 X20.6 Y7.394 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X20.6 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/220
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
G17
G3 Z2.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z2.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z2.6 F30000
G1 X27.21 Y24.41 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z2.6 F30000
G1 X43.79 Y27.79 Z2.6
G1 Z2.2
G1 E.8 F1800
G1 F7739
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y27.05 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y27.05 E.05401
G1 X41.15 Y25.15 E.0891
G1 X38.202 Y25.15 E.09782
G1 X36.302 Y27.05 E.0891
G1 X35.374 Y27.05 E.0308
G1 X27.95 Y19.626 E.34825
G1 X27.95 Y20.05 E.01405
G1 X36.05 Y11.95 E.37996
G1 X36.05 Y12.374 E.01405
G1 X28.626 Y4.95 E.34825
G1 X27.698 Y4.95 E.0308
G1 X25.798 Y6.85 E.0891
G1 X22.85 Y6.85 E.09782
G1 X20.95 Y4.95 E.0891
G1 X22.579 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X20.95 Y4.95 E-.61876
G1 X21.213 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y7.394 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7739
G1 X20.6 Y24.606 E.54411
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.203 Y23.273 Z2.6 F30000
G1 X43.4 Y24.606 Z2.6
G1 Z2.2
G1 E.8 F1800
G1 F7739
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y4.95 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y4.95 E.05401
G1 X41.15 Y6.85 E.0891
G1 X38.202 Y6.85 E.09782
G1 X36.302 Y4.95 E.0891
G1 X35.374 Y4.95 E.0308
G1 X27.95 Y12.374 E.34825
G1 X27.95 Y11.95 E.01405
G1 X36.05 Y20.05 E.37996
G1 X36.05 Y19.626 E.01405
G1 X28.626 Y27.05 E.34825
G1 X27.698 Y27.05 E.0308
G1 X25.798 Y25.15 E.0891
G1 X22.85 Y25.15 E.09782
G1 X20.95 Y27.05 E.0891
G1 X22.579 Y27.05 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X20.95 Y27.05 E-.61876
G1 X21.213 Y26.787 E-.14124
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/220
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
G17
G3 Z2.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z2.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7787
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z2.8 F30000
G1 X27.21 Y24.41 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z2.8 F30000
G1 X43.79 Y27.79 Z2.8
G1 Z2.4
G1 E.8 F1800
G1 F7787
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y24.606 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.936 Y7.801 Z2.8 F30000
G1 X22.579 Y4.95 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7787
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F7787
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
M73 P34 R17
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X43.05 Y4.95 E-.61876
G1 X42.787 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X35.191 Y5.96 Z2.8 F30000
G1 X20.6 Y7.394 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X20.6 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/220
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
G17
G3 Z2.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z2.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z3 F30000
G1 X27.21 Y24.41 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7739
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z3 F30000
G1 X43.79 Y27.79 Z3
G1 Z2.6
G1 E.8 F1800
G1 F7739
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y27.05 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y27.05 E.05401
G1 X41.15 Y25.15 E.0891
G1 X38.202 Y25.15 E.09782
G1 X36.302 Y27.05 E.0891
G1 X35.374 Y27.05 E.0308
G1 X27.95 Y19.626 E.34825
G1 X27.95 Y20.05 E.01405
G1 X36.05 Y11.95 E.37996
G1 X36.05 Y12.374 E.01405
G1 X28.626 Y4.95 E.34825
G1 X27.698 Y4.95 E.0308
G1 X25.798 Y6.85 E.0891
G1 X22.85 Y6.85 E.09782
G1 X20.95 Y4.95 E.0891
G1 X22.579 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X20.95 Y4.95 E-.61876
G1 X21.213 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y7.394 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7739
G1 X20.6 Y24.606 E.54411
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.203 Y23.273 Z3 F30000
G1 X43.4 Y24.606 Z3
G1 Z2.6
G1 E.8 F1800
G1 F7739
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.421 Y4.95 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7739
G1 X43.05 Y4.95 E.05401
G1 X41.15 Y6.85 E.0891
G1 X38.202 Y6.85 E.09782
G1 X36.302 Y4.95 E.0891
G1 X35.374 Y4.95 E.0308
G1 X27.95 Y12.374 E.34825
G1 X27.95 Y11.95 E.01405
G1 X36.05 Y20.05 E.37996
G1 X36.05 Y19.626 E.01405
G1 X28.626 Y27.05 E.34825
G1 X27.698 Y27.05 E.0308
G1 X25.798 Y25.15 E.0891
G1 X22.85 Y25.15 E.09782
G1 X20.95 Y27.05 E.0891
G1 X22.579 Y27.05 E.05401
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X20.95 Y27.05 E-.61876
G1 X21.213 Y26.787 E-.14124
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/220
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
G17
G3 Z3 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z2.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7787
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 F15476.087
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z3.2 F30000
M73 P34 R16
G1 X27.21 Y24.41 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7787
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
G1 F12000
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z3.2 F30000
G1 X43.79 Y27.79 Z3.2
G1 Z2.8
G1 E.8 F1800
G1 F7787
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y24.606 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 F15000
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.936 Y7.801 Z3.2 F30000
G1 X22.579 Y4.95 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F7787
G1 X20.95 Y4.95 E.05401
G1 X22.85 Y6.85 E.0891
G1 X25.798 Y6.85 E.09782
G1 X27.698 Y4.95 E.0891
G1 X28.626 Y4.95 E.0308
G1 X36.05 Y12.374 E.34825
G1 X36.05 Y11.95 E.01405
G1 X27.95 Y20.05 E.37996
G1 X27.95 Y19.626 E.01405
G1 X35.374 Y27.05 E.34825
G1 X36.302 Y27.05 E.0308
G1 X38.202 Y25.15 E.0891
G1 X41.15 Y25.15 E.09782
G1 X43.05 Y27.05 E.0891
G1 X41.421 Y27.05 E.05401
G1 X22.579 Y27.05 F30000
G1 F7787
G1 X20.95 Y27.05 E.05401
G1 X22.85 Y25.15 E.0891
G1 X25.798 Y25.15 E.09782
G1 X27.698 Y27.05 E.0891
G1 X28.626 Y27.05 E.0308
G1 X36.05 Y19.626 E.34825
G1 X36.05 Y20.05 E.01405
G1 X27.95 Y11.95 E.37996
G1 X27.95 Y12.374 E.01405
G1 X35.374 Y4.95 E.34825
G1 X36.302 Y4.95 E.0308
G1 X38.202 Y6.85 E.0891
G1 X41.15 Y6.85 E.09782
G1 X43.05 Y4.95 E.0891
G1 X41.421 Y4.95 E.05401
; WIPE_START
G1 F15476.087
G1 X43.05 Y4.95 E-.61876
G1 X42.787 Y5.213 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X35.191 Y5.96 Z3.2 F30000
G1 X20.6 Y7.394 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F7787
G1 X20.6 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.6 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/220
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
G17
G3 Z3.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z3.4 F30000
G1 X27.21 Y24.41 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z3.4 F30000
G1 X43.79 Y27.79 Z3.4
G1 Z3
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.228 Y26.716 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X41.894 Y27.05 E.01567
G1 X43.05 Y27.05 E.03834
G1 X41.527 Y25.527 E.07141
G1 X37.824 Y25.527 E.12284
G1 X36.679 Y26.672 E.05371
G1 X34.997 Y26.672 E.05582
G1 X28.327 Y20.003 E.31286
G1 X28.327 Y19.673 E.01098
G1 X35.673 Y12.327 E.34457
M73 P35 R16
G1 X35.673 Y11.997 E.01098
G1 X29.003 Y5.327 E.31286
G1 X27.321 Y5.327 E.05582
G1 X26.176 Y6.472 E.05371
G1 X22.472 Y6.472 E.12284
G1 X20.95 Y4.95 E.07141
G1 X22.369 Y4.95 E.04706
G1 X22.221 Y5.098 E.00695
G1 X22.867 Y4.965 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.383255
G1 F3000;_EXTRUDE_SET_SPEED
G1 X29.097 Y4.965 E.17277
G1 X29.275 Y5.073 E.00577
G1 X29.767 Y4.965 E.01398
G1 X36.754 Y4.965 E.19376
G1 X36.933 Y5.064 E.00567
G1 X37.389 Y4.965 E.01295
G1 X42.876 Y4.965 E.15217
G1 X43.008 Y4.992 E.00374
G1 X43.035 Y5.124 E.00374
G1 X43.035 Y6.622 E.04154
G1 X42.944 Y6.772 E.00489
G1 X42.822 Y6.835 E.0038
G1 X36.194 Y6.835 E.1838
G1 X36.062 Y6.862 E.00374
G1 X36.035 Y6.994 E.00374
G1 X36.035 Y25.006 E.4995
G1 X36.062 Y25.138 E.00374
G1 X36.194 Y25.165 E.00374
G1 X42.876 Y25.165 E.1853
G1 X43.008 Y25.192 E.00374
G1 X43.027 Y25.336 E.00402
; Slow Down End
G1 X43.4 Y24.606 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X43.4 Y7.394 E.54411
; WIPE_START
G1 X43.4 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.044 Y5.327 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X42.673 Y5.327 E.05401
G1 X41.527 Y6.472 E.05371
G1 X37.824 Y6.472 E.12284
G1 X36.679 Y5.327 E.05371
G1 X34.997 Y5.327 E.05582
G1 X28.327 Y11.997 E.31286
G1 X28.327 Y12.327 E.01098
G1 X35.673 Y19.673 E.34457
G1 X35.673 Y20.003 E.01098
G1 X29.003 Y26.673 E.31286
G1 X27.321 Y26.673 E.05582
G1 X26.176 Y25.527 E.05371
G1 X22.472 Y25.527 E.12284
G1 X21.327 Y26.673 E.05371
G1 X22.956 Y26.673 E.05401
G1 X41.395 Y27.035 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38292
G1 F3000;_EXTRUDE_SET_SPEED
G1 X34.933 Y27.035 E.17904
; Slow Down End
G1 X34.159 Y27.035 F30000
; Slow Down Start
G1 F3000;_EXTRUDE_SET_SPEED
G1 X27.278 Y27.035 E.19062
; Slow Down End
G1 X26.535 Y27.035 F30000
; Slow Down Start
; LINE_WIDTH: 0.396898
G1 F3000;_EXTRUDE_SET_SPEED
G1 X21.124 Y27.035 E.15608
G1 X20.992 Y27.008 E.00389
G1 X20.965 Y26.876 E.00389
G1 X20.965 Y25.994 E.02544
; Slow Down End
; WIPE_START
G1 X20.965 Y26.876 E-.3351
G1 X20.992 Y27.008 E-.05119
G1 X21.124 Y27.035 E-.05119
G1 X21.973 Y27.035 E-.32252
; WIPE_END
G1 E-.04 F1800
G1 X21.617 Y19.411 Z3.4 F30000
G1 X21.03 Y6.821 Z3.4
G1 Z3
G1 E.8 F1800
; Slow Down Start
; LINE_WIDTH: 0.38322
G1 F3000;_EXTRUDE_SET_SPEED
G1 X21.124 Y6.835 E.00263
G1 X27.806 Y6.835 E.18528
G1 X27.937 Y6.862 E.00374
G1 X27.965 Y6.994 E.00374
G1 X27.965 Y25.006 E.49945
G1 X27.937 Y25.138 E.00374
G1 X27.806 Y25.165 E.00374
G1 X21.424 Y25.165 E.17695
; Slow Down End
G1 X20.6 Y24.606 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X20.6 Y7.394 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X20.6 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/220
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
G17
G3 Z3.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z3.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z3.6 F30000
G1 X27.21 Y24.41 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z3.6 F30000
G1 X43.79 Y27.79 Z3.6
G1 Z3.2
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.472 Y26.472 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X42.65 Y26.65 E.00837
G1 X43.024 Y25.872 F30000
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.402574
G1 F3000;_EXTRUDE_SET_SPEED
G1 X43.024 Y26.169 E.00868
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.44016
;_EXTRUDE_SET_SPEED
G1 X43.024 Y26.465 E.00959
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.477747
;_EXTRUDE_SET_SPEED
G1 X43.024 Y26.761 E.01049
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.41197
;_EXTRUDE_SET_SPEED
G1 X42.968 Y26.968 E.00644
G1 X42.761 Y27.024 E.00644
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.38378
;_EXTRUDE_SET_SPEED
G1 X41.932 Y27.024 E.02301
; Slow Down End
G1 X41.104 Y27.231 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40351
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X43.028 Y25.306 E.14179
G1 X43.028 Y25.172 E.00701
G1 X42.521 Y25.172 E.0264
G1 X40.665 Y27.028 E.13679
G1 X40.024 Y27.028 E.03342
G1 X41.88 Y25.172 E.13679
G1 X41.239 Y25.172 E.03342
G1 X39.382 Y27.028 E.13679
G1 X38.741 Y27.028 E.03342
G1 X40.597 Y25.172 E.13679
G1 X39.956 Y25.172 E.03342
G1 X38.1 Y27.028 E.13679
G1 X37.458 Y27.028 E.03342
G1 X39.315 Y25.172 E.13679
G1 X38.673 Y25.172 E.03342
G1 X36.817 Y27.028 E.13679
G1 X36.176 Y27.028 E.03342
G1 X38.032 Y25.172 E.13679
G1 X37.391 Y25.172 E.03342
G1 X35.534 Y27.028 E.13679
G1 X34.939 Y27.028 E.03102
G1 X34.935 Y26.986 E.00222
G1 X36.749 Y25.172 E.13365
G1 X36.108 Y25.172 E.03342
G1 X34.465 Y26.815 E.12107
G1 X34.021 Y27.028 E.02568
G1 X33.61 Y27.028 E.02138
G1 X36.028 Y24.61 E.17818
G1 X36.028 Y23.969 E.03342
G1 X32.969 Y27.028 E.22543
G1 X32.327 Y27.028 E.03342
G1 X36.028 Y23.327 E.27269
G1 X36.028 Y22.686 E.03342
G1 X31.686 Y27.028 E.31995
G1 X31.045 Y27.028 E.03342
G1 X36.028 Y22.045 E.36721
G1 X36.028 Y21.403 E.03342
G1 X30.403 Y27.028 E.41447
G1 X29.762 Y27.028 E.03342
G1 X36.028 Y20.762 E.46172
G1 X36.028 Y20.121 E.03342
G1 X29.121 Y27.028 E.50898
G1 X28.479 Y27.028 E.03342
G1 X36.028 Y19.479 E.55624
G1 X36.028 Y18.838 E.03342
G1 X27.838 Y27.028 E.6035
G1 X27.284 Y27.028 E.02886
G1 X27.275 Y26.95 E.0041
G1 X36.028 Y18.197 E.645
G1 X36.028 Y17.555 E.03342
G1 X26.698 Y26.885 E.68749
G1 X26.395 Y27.028 E.01745
G1 X25.914 Y27.028 E.02508
G1 X36.028 Y16.914 E.74527
G1 X36.028 Y16.272 E.03342
G1 X27.972 Y24.329 E.59363
G1 X27.972 Y23.687 E.03342
G1 X36.028 Y15.631 E.59363
G1 X36.028 Y14.99 E.03342
G1 X27.972 Y23.046 E.59363
G1 X27.972 Y22.405 E.03342
G1 X36.028 Y14.348 E.59363
G1 X36.028 Y13.707 E.03342
G1 X27.972 Y21.763 E.59363
G1 X27.972 Y21.122 E.03342
G1 X36.028 Y13.066 E.59363
G1 X36.028 Y12.424 E.03342
G1 X27.972 Y20.481 E.59363
G1 X27.972 Y19.839 E.03342
G1 X36.028 Y11.783 E.59363
G1 X36.028 Y11.142 E.03342
G1 X27.972 Y19.198 E.59363
G1 X27.972 Y18.557 E.03342
G1 X36.028 Y10.5 E.59363
G1 X36.028 Y9.859 E.03342
G1 X27.972 Y17.915 E.59363
G1 X27.972 Y17.274 E.03342
G1 X36.028 Y9.217 E.59363
G1 X36.028 Y8.576 E.03342
G1 X27.972 Y16.633 E.59363
G1 X27.972 Y15.991 E.03342
G1 X36.028 Y7.935 E.59363
G1 X36.028 Y7.293 E.03342
G1 X27.972 Y15.35 E.59363
G1 X27.972 Y14.708 E.03342
G1 X37.708 Y4.972 E.71744
G1 X38.35 Y4.972 E.03342
G1 X36.493 Y6.828 E.13679
G1 X37.135 Y6.828 E.03342
G1 X38.991 Y4.972 E.13679
G1 X39.633 Y4.972 E.03342
G1 X37.776 Y6.828 E.13679
G1 X38.417 Y6.828 E.03342
G1 X40.274 Y4.972 E.13679
G1 X40.915 Y4.972 E.03342
G1 X39.059 Y6.828 E.13679
G1 X39.7 Y6.828 E.03342
G1 X41.557 Y4.972 E.13679
G1 X42.198 Y4.972 E.03342
G1 X40.342 Y6.828 E.13679
G1 X40.983 Y6.828 E.03342
G1 X42.839 Y4.972 E.13679
G1 X43.028 Y4.972 E.00984
G1 X43.028 Y5.424 E.02358
G1 X41.624 Y6.828 E.10345
G1 X42.266 Y6.828 E.03342
G1 X43.231 Y5.863 E.07111
G1 X43.147 Y6.904 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38292
; LAYER_HEIGHT: 0.2
G1 F12000
G1 X43.126 Y6.941 E.00118
G1 X43.062 Y6.904 E.00204
G1 X43.074 Y6.898 E.00038
G1 X43.4 Y7.394 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X43.4 Y24.606 E.54411
; WIPE_START
G1 X43.4 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X36.611 Y26.094 Z3.6 F30000
G1 X34.665 Y27.095 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38292
G1 F12000
G1 X34.644 Y27.131 E.00118
G1 X34.58 Y27.095 E.00204
G1 X34.592 Y27.088 E.00038
G1 X27.019 Y27.101 F30000
G1 F12000
G1 X26.998 Y27.138 E.00118
G1 X26.934 Y27.101 E.00204
G1 X26.946 Y27.094 E.00038
G1 X25.07 Y27.231 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40351
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X27.129 Y25.172 E.15171
G1 X26.487 Y25.172 E.03342
G1 X24.631 Y27.028 E.13679
G1 X23.99 Y27.028 E.03342
G1 X25.846 Y25.172 E.13679
G1 X25.205 Y25.172 E.03342
G1 X23.348 Y27.028 E.13679
G1 X22.707 Y27.028 E.03342
G1 X24.563 Y25.172 E.13679
G1 X23.922 Y25.172 E.03342
G1 X22.066 Y27.028 E.13679
G1 X21.424 Y27.028 E.03342
G1 X23.281 Y25.172 E.13679
G1 X22.639 Y25.172 E.03342
G1 X20.972 Y26.839 E.12287
G1 X20.972 Y26.198 E.03342
G1 X22.2 Y24.969 E.09053
; WIPE_START
G1 X20.972 Y26.198 E-.66029
G1 X20.972 Y26.46 E-.09971
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y24.606 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
; LAYER_HEIGHT: 0.2
G1 F15000
G1 X20.6 Y7.394 E.54411
; WIPE_START
G1 X20.6 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X20.976 Y6.391 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38378
G1 F3000;_EXTRUDE_SET_SPEED
M73 P36 R16
G1 X20.976 Y5.239 E.03198
G1 X21.032 Y5.032 E.00595
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.49654
;_EXTRUDE_SET_SPEED
G1 X21.239 Y4.976 E.00792
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.38378
;_EXTRUDE_SET_SPEED
G1 X22.331 Y4.976 E.03032
; Slow Down End
G1 X23.16 Y4.769 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40351
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X21.101 Y6.828 E.15171
G1 X21.742 Y6.828 E.03342
G1 X23.599 Y4.972 E.13679
G1 X24.24 Y4.972 E.03342
G1 X22.383 Y6.828 E.13679
G1 X23.025 Y6.828 E.03342
G1 X24.881 Y4.972 E.13679
G1 X25.523 Y4.972 E.03342
G1 X23.666 Y6.828 E.13679
G1 X24.308 Y6.828 E.03342
G1 X26.164 Y4.972 E.13679
G1 X26.805 Y4.972 E.03342
G1 X24.949 Y6.828 E.13679
G1 X25.59 Y6.828 E.03342
G1 X27.447 Y4.972 E.13679
G1 X28.088 Y4.972 E.03342
G1 X26.232 Y6.828 E.13679
G1 X26.873 Y6.828 E.03342
G1 X28.729 Y4.972 E.13679
G1 X29.032 Y4.972 E.01574
G1 X29.072 Y5.27 E.0157
G1 X27.514 Y6.828 E.11479
G1 X27.972 Y6.828 E.02383
G1 X27.972 Y7.012 E.00958
G1 X30.012 Y4.972 E.15034
G1 X30.653 Y4.972 E.03342
G1 X27.972 Y7.653 E.1976
G1 X27.972 Y8.295 E.03342
G1 X31.295 Y4.972 E.24486
G1 X31.936 Y4.972 E.03342
G1 X27.972 Y8.936 E.29211
G1 X27.972 Y9.578 E.03342
G1 X32.578 Y4.972 E.33937
G1 X33.219 Y4.972 E.03342
G1 X27.972 Y10.219 E.38663
G1 X27.972 Y10.86 E.03342
G1 X33.86 Y4.972 E.43389
G1 X34.502 Y4.972 E.03342
G1 X27.972 Y11.502 E.48115
G1 X27.972 Y12.143 E.03342
G1 X35.143 Y4.972 E.5284
G1 X35.784 Y4.972 E.03342
G1 X27.972 Y12.784 E.57566
G1 X27.972 Y13.426 E.03342
G1 X36.426 Y4.972 E.62292
G1 X36.688 Y4.972 E.01366
G1 X36.745 Y5.294 E.01704
G1 X27.769 Y14.27 E.66136
G1 X29.377 Y4.891 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.38292
; LAYER_HEIGHT: 0.2
G1 F12000
G1 X29.356 Y4.928 E.00118
G1 X29.292 Y4.891 E.00204
G1 X29.304 Y4.885 E.00038
G1 X37.024 Y4.885 F30000
G1 F12000
G1 X37.003 Y4.922 E.00118
G1 X36.939 Y4.885 E.00204
G1 X36.951 Y4.878 E.00038
G1 X21.35 Y5.35 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X21.66 Y5.66 E.01453
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15476.087
G1 X21.35 Y5.35 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/220
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
G17
G3 Z3.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z3.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z3.8 F30000
G1 X27.21 Y24.41 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z3.8 F30000
G1 X43.79 Y27.79 Z3.8
G1 Z3.4
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.234 Y25.359 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X43.011 Y25.135 E.00975
G1 X42.475 Y25.135 E.01655
G1 X43.065 Y25.725 E.02574
G1 X43.065 Y26.261 E.01655
G1 X41.939 Y25.135 E.04914
G1 X41.403 Y25.135 E.01655
G1 X43.065 Y26.796 E.07254
G1 X43.065 Y27.065 E.00828
G1 X42.797 Y27.065 E.00826
G1 X40.868 Y25.135 E.08425
G1 X40.332 Y25.135 E.01655
G1 X42.261 Y27.065 E.08425
G1 X41.725 Y27.065 E.01655
G1 X39.796 Y25.135 E.08425
G1 X39.26 Y25.135 E.01655
G1 X41.189 Y27.065 E.08425
G1 X40.654 Y27.065 E.01655
G1 X38.724 Y25.135 E.08425
G1 X38.188 Y25.135 E.01655
G1 X40.118 Y27.065 E.08425
G1 X39.582 Y27.065 E.01655
G1 X37.652 Y25.135 E.08425
G1 X37.117 Y25.135 E.01655
G1 X39.046 Y27.065 E.08425
G1 X38.51 Y27.065 E.01655
G1 X36.581 Y25.135 E.08425
G1 X36.065 Y25.135 E.01593
G1 X36.065 Y24.619 E.01593
G1 X27.935 Y16.49 E.35497
G1 X27.935 Y15.954 E.01655
G1 X36.065 Y24.083 E.35497
G1 X36.065 Y23.548 E.01655
G1 X27.935 Y15.418 E.35497
G1 X27.935 Y14.882 E.01655
G1 X36.065 Y23.012 E.35497
G1 X36.065 Y22.476 E.01655
G1 X27.935 Y14.346 E.35497
G1 X27.935 Y13.811 E.01655
G1 X36.065 Y21.94 E.35497
G1 X36.065 Y21.404 E.01655
G1 X27.935 Y13.275 E.35497
G1 X27.935 Y12.739 E.01655
G1 X36.065 Y20.868 E.35498
G1 X36.065 Y20.332 E.01655
G1 X27.935 Y12.203 E.35498
G1 X27.935 Y11.667 E.01655
G1 X36.065 Y19.797 E.35498
G1 X36.065 Y19.261 E.01655
G1 X27.935 Y11.131 E.35498
G1 X27.935 Y10.595 E.01655
G1 X36.065 Y18.725 E.35498
G1 X36.065 Y18.189 E.01655
G1 X27.935 Y10.06 E.35498
G1 X27.935 Y9.524 E.01655
G1 X36.065 Y17.653 E.35498
G1 X36.065 Y17.117 E.01655
G1 X27.935 Y8.988 E.35498
G1 X27.935 Y8.452 E.01655
G1 X36.065 Y16.581 E.35498
G1 X36.065 Y16.045 E.01655
G1 X27.935 Y7.916 E.35498
G1 X27.935 Y7.38 E.01655
G1 X36.065 Y15.51 E.35498
G1 X36.065 Y14.974 E.01655
G1 X26.026 Y4.935 E.43834
G1 X26.562 Y4.935 E.01655
G1 X36.065 Y14.438 E.41494
G1 X36.065 Y13.902 E.01655
G1 X27.098 Y4.935 E.39154
G1 X27.634 Y4.935 E.01655
G1 X36.065 Y13.366 E.36814
G1 X36.065 Y12.83 E.01655
G1 X28.17 Y4.935 E.34474
G1 X28.706 Y4.935 E.01655
G1 X36.065 Y12.294 E.32134
G1 X36.065 Y11.759 E.01655
G1 X29.241 Y4.935 E.29794
G1 X29.777 Y4.935 E.01655
G1 X36.065 Y11.223 E.27455
G1 X36.065 Y10.687 E.01655
G1 X30.313 Y4.935 E.25115
G1 X30.849 Y4.935 E.01655
G1 X36.065 Y10.151 E.22775
G1 X36.065 Y9.615 E.01655
G1 X31.385 Y4.935 E.20435
G1 X31.921 Y4.935 E.01655
G1 X36.065 Y9.079 E.18095
G1 X36.065 Y8.543 E.01655
G1 X32.457 Y4.935 E.15755
G1 X32.992 Y4.935 E.01655
G1 X36.065 Y8.008 E.13415
G1 X36.065 Y7.472 E.01655
G1 X33.528 Y4.935 E.11075
G1 X34.064 Y4.935 E.01655
G1 X36.065 Y6.936 E.08736
G1 X36.065 Y6.865 E.0022
G1 X36.529 Y6.865 E.01435
G1 X34.6 Y4.935 E.08425
G1 X35.136 Y4.935 E.01655
G1 X37.065 Y6.865 E.08425
G1 X37.601 Y6.865 E.01655
G1 X35.672 Y4.935 E.08425
G1 X36.208 Y4.935 E.01655
G1 X38.137 Y6.865 E.08425
G1 X38.673 Y6.865 E.01655
G1 X36.743 Y4.935 E.08425
G1 X37.279 Y4.935 E.01655
G1 X39.209 Y6.865 E.08425
G1 X39.744 Y6.865 E.01655
G1 X37.815 Y4.935 E.08425
G1 X38.351 Y4.935 E.01655
G1 X40.28 Y6.865 E.08425
G1 X40.816 Y6.865 E.01655
G1 X38.887 Y4.935 E.08425
G1 X39.423 Y4.935 E.01655
G1 X41.352 Y6.865 E.08425
G1 X41.888 Y6.865 E.01655
G1 X39.959 Y4.935 E.08425
G1 X40.494 Y4.935 E.01655
G1 X42.424 Y6.865 E.08425
G1 X42.96 Y6.865 E.01655
G1 X41.03 Y4.935 E.08425
G1 X41.566 Y4.935 E.01655
G1 X43.065 Y6.434 E.06543
G1 X43.065 Y5.898 E.01655
G1 X42.102 Y4.935 E.04204
G1 X42.638 Y4.935 E.01655
G1 X43.234 Y5.532 E.02605
; WIPE_START
G1 X42.638 Y4.935 E-.32055
G1 X42.102 Y4.935 E-.20363
G1 X42.541 Y5.374 E-.23583
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y7.394 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X43.4 Y24.606 E.54411
; WIPE_START
G1 X43.4 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X38.144 Y27.234 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X27.935 Y17.026 E.44577
G1 X27.935 Y17.562 E.01655
G1 X37.438 Y27.065 E.41496
G1 X36.903 Y27.065 E.01655
G1 X27.935 Y18.097 E.39156
G1 X27.935 Y18.633 E.01655
G1 X36.367 Y27.065 E.36816
G1 X35.831 Y27.065 E.01655
G1 X27.935 Y19.169 E.34476
G1 X27.935 Y19.705 E.01655
G1 X35.295 Y27.065 E.32136
G1 X34.759 Y27.065 E.01655
G1 X27.935 Y20.241 E.29797
G1 X27.935 Y20.777 E.01655
G1 X34.223 Y27.065 E.27457
G1 X33.687 Y27.065 E.01655
G1 X27.935 Y21.313 E.25117
G1 X27.935 Y21.848 E.01655
G1 X33.152 Y27.065 E.22777
G1 X32.616 Y27.065 E.01655
G1 X27.935 Y22.384 E.20437
G1 X27.935 Y22.92 E.01655
G1 X32.08 Y27.065 E.18097
G1 X31.544 Y27.065 E.01655
G1 X27.935 Y23.456 E.15757
G1 X27.935 Y23.992 E.01655
G1 X31.008 Y27.065 E.13417
G1 X30.472 Y27.065 E.01655
G1 X27.935 Y24.528 E.11078
G1 X27.935 Y25.064 E.01655
G1 X29.936 Y27.065 E.08738
G1 X29.401 Y27.065 E.01655
G1 X27.471 Y25.135 E.08425
G1 X26.935 Y25.135 E.01655
G1 X28.865 Y27.065 E.08425
G1 X28.329 Y27.065 E.01655
G1 X26.399 Y25.135 E.08425
G1 X25.864 Y25.135 E.01655
G1 X27.793 Y27.065 E.08425
G1 X27.257 Y27.065 E.01655
G1 X25.328 Y25.135 E.08425
G1 X24.792 Y25.135 E.01655
G1 X26.721 Y27.065 E.08425
G1 X26.185 Y27.065 E.01655
G1 X24.256 Y25.135 E.08425
G1 X23.72 Y25.135 E.01655
G1 X25.649 Y27.065 E.08425
G1 X25.114 Y27.065 E.01655
G1 X23.184 Y25.135 E.08425
G1 X22.648 Y25.135 E.01655
G1 X24.578 Y27.065 E.08425
G1 X24.042 Y27.065 E.01655
G1 X22.113 Y25.135 E.08425
G1 X21.577 Y25.135 E.01655
G1 X23.506 Y27.065 E.08425
G1 X22.97 Y27.065 E.01655
G1 X21.041 Y25.135 E.08425
G1 X20.935 Y25.135 E.00326
G1 X20.935 Y25.566 E.01329
G1 X22.434 Y27.065 E.06546
G1 X21.898 Y27.065 E.01655
G1 X20.935 Y26.102 E.04206
G1 X20.935 Y26.637 E.01655
G1 X21.532 Y27.234 E.02607
; WIPE_START
G1 X20.935 Y26.637 E-.32081
G1 X20.935 Y26.102 E-.20363
G1 X21.374 Y26.54 E-.23556
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y24.606 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X20.6 Y7.394 E.54411
G1 X20.766 Y6.641 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X20.989 Y6.865 E.00977
G1 X21.525 Y6.865 E.01655
G1 X20.935 Y6.275 E.02576
G1 X20.935 Y5.739 E.01655
G1 X22.061 Y6.865 E.04916
G1 X22.597 Y6.865 E.01655
G1 X20.935 Y5.203 E.07256
G1 X20.935 Y4.935 E.00826
G1 X21.203 Y4.935 E.00828
G1 X23.133 Y6.865 E.08425
G1 X23.669 Y6.865 E.01655
G1 X21.739 Y4.935 E.08425
G1 X22.275 Y4.935 E.01655
G1 X24.205 Y6.865 E.08425
G1 X24.74 Y6.865 E.01655
G1 X22.811 Y4.935 E.08425
G1 X23.347 Y4.935 E.01655
G1 X25.276 Y6.865 E.08425
G1 X25.812 Y6.865 E.01655
G1 X23.883 Y4.935 E.08425
G1 X24.419 Y4.935 E.01655
G1 X26.348 Y6.865 E.08425
G1 X26.884 Y6.865 E.01655
G1 X24.955 Y4.935 E.08425
G1 X25.49 Y4.935 E.01655
G1 X27.589 Y7.034 E.09166
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X26.175 Y5.62 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/220
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
G17
G3 Z3.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z3.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
M73 P37 R16
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z4 F30000
G1 X27.21 Y24.41 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z4 F30000
G1 X43.79 Y27.79 Z4
G1 Z3.6
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.468 Y27.234 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X43.065 Y26.638 E.02605
G1 X43.065 Y26.102 E.01655
G1 X42.102 Y27.065 E.04204
G1 X41.566 Y27.065 E.01655
G1 X43.065 Y25.566 E.06543
G1 X43.065 Y25.135 E.0133
G1 X42.96 Y25.135 E.00324
G1 X41.03 Y27.065 E.08425
G1 X40.494 Y27.065 E.01655
G1 X42.424 Y25.135 E.08425
G1 X41.888 Y25.135 E.01655
G1 X39.959 Y27.065 E.08425
G1 X39.423 Y27.065 E.01655
G1 X41.352 Y25.135 E.08425
G1 X40.816 Y25.135 E.01655
G1 X38.887 Y27.065 E.08425
G1 X38.351 Y27.065 E.01655
G1 X40.28 Y25.135 E.08425
G1 X39.744 Y25.135 E.01655
G1 X37.815 Y27.065 E.08425
G1 X37.279 Y27.065 E.01655
G1 X39.209 Y25.135 E.08425
G1 X38.673 Y25.135 E.01655
G1 X36.743 Y27.065 E.08425
G1 X36.208 Y27.065 E.01655
G1 X38.137 Y25.135 E.08425
G1 X37.601 Y25.135 E.01655
G1 X35.672 Y27.065 E.08425
G1 X35.136 Y27.065 E.01655
G1 X37.065 Y25.135 E.08425
G1 X36.529 Y25.135 E.01655
G1 X34.6 Y27.065 E.08425
G1 X34.064 Y27.065 E.01655
G1 X36.065 Y25.064 E.08736
G1 X36.065 Y24.528 E.01655
G1 X33.528 Y27.065 E.11075
G1 X32.992 Y27.065 E.01655
G1 X36.065 Y23.992 E.13415
G1 X36.065 Y23.457 E.01655
G1 X32.457 Y27.065 E.15755
G1 X31.921 Y27.065 E.01655
G1 X36.065 Y22.921 E.18095
G1 X36.065 Y22.385 E.01655
G1 X31.385 Y27.065 E.20435
G1 X30.849 Y27.065 E.01655
G1 X36.065 Y21.849 E.22775
G1 X36.065 Y21.313 E.01655
G1 X30.313 Y27.065 E.25115
G1 X29.777 Y27.065 E.01655
G1 X36.065 Y20.777 E.27455
G1 X36.065 Y20.241 E.01655
G1 X29.241 Y27.065 E.29794
G1 X28.706 Y27.065 E.01655
G1 X36.065 Y19.706 E.32134
G1 X36.065 Y19.17 E.01655
G1 X28.17 Y27.065 E.34474
G1 X27.634 Y27.065 E.01655
G1 X36.065 Y18.634 E.36814
G1 X36.065 Y18.098 E.01655
G1 X27.098 Y27.065 E.39154
G1 X26.562 Y27.065 E.01655
G1 X36.065 Y17.562 E.41494
G1 X36.065 Y17.026 E.01655
G1 X26.026 Y27.065 E.43834
G1 X25.49 Y27.065 E.01655
G1 X27.42 Y25.135 E.08425
G1 X26.884 Y25.135 E.01655
G1 X24.955 Y27.065 E.08425
G1 X24.419 Y27.065 E.01655
G1 X26.348 Y25.135 E.08425
G1 X25.812 Y25.135 E.01655
G1 X23.883 Y27.065 E.08425
G1 X23.347 Y27.065 E.01655
G1 X25.276 Y25.135 E.08425
G1 X24.74 Y25.135 E.01655
G1 X22.811 Y27.065 E.08425
G1 X22.275 Y27.065 E.01655
G1 X24.205 Y25.135 E.08425
G1 X23.669 Y25.135 E.01655
G1 X21.739 Y27.065 E.08425
G1 X21.203 Y27.065 E.01655
G1 X23.133 Y25.135 E.08425
G1 X22.597 Y25.135 E.01655
G1 X20.935 Y26.797 E.07256
G1 X20.935 Y26.261 E.01655
G1 X22.061 Y25.135 E.04916
G1 X21.525 Y25.135 E.01655
G1 X20.935 Y25.725 E.02576
G1 X20.935 Y25.189 E.01655
G1 X21.159 Y24.966 E.00977
G1 X20.6 Y24.606 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X20.6 Y7.394 E.54411
; WIPE_START
G1 X20.6 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.532 Y4.766 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X20.935 Y5.363 E.02607
G1 X20.935 Y5.898 E.01655
G1 X21.898 Y4.935 E.04206
G1 X22.434 Y4.935 E.01655
G1 X20.935 Y6.434 E.06546
G1 X20.935 Y6.865 E.01329
G1 X21.041 Y6.865 E.00326
G1 X22.97 Y4.935 E.08425
G1 X23.506 Y4.935 E.01655
G1 X21.577 Y6.865 E.08425
G1 X22.113 Y6.865 E.01655
G1 X24.042 Y4.935 E.08425
G1 X24.578 Y4.935 E.01655
G1 X22.648 Y6.865 E.08425
G1 X23.184 Y6.865 E.01655
G1 X25.114 Y4.935 E.08425
G1 X25.649 Y4.935 E.01655
G1 X23.72 Y6.865 E.08425
G1 X24.256 Y6.865 E.01655
G1 X26.185 Y4.935 E.08425
G1 X26.721 Y4.935 E.01655
G1 X24.792 Y6.865 E.08425
G1 X25.328 Y6.865 E.01655
G1 X27.257 Y4.935 E.08425
G1 X27.793 Y4.935 E.01655
G1 X25.864 Y6.865 E.08425
G1 X26.399 Y6.865 E.01655
G1 X28.329 Y4.935 E.08425
G1 X28.865 Y4.935 E.01655
G1 X26.935 Y6.865 E.08425
G1 X27.471 Y6.865 E.01655
G1 X29.401 Y4.935 E.08425
G1 X29.936 Y4.935 E.01655
G1 X27.935 Y6.936 E.08738
G1 X27.935 Y7.472 E.01655
G1 X30.472 Y4.935 E.11078
G1 X31.008 Y4.935 E.01655
G1 X27.935 Y8.008 E.13417
G1 X27.935 Y8.544 E.01655
G1 X31.544 Y4.935 E.15757
G1 X32.08 Y4.935 E.01655
G1 X27.935 Y9.08 E.18097
G1 X27.935 Y9.616 E.01655
G1 X32.616 Y4.935 E.20437
G1 X33.152 Y4.935 E.01655
G1 X27.935 Y10.152 E.22777
G1 X27.935 Y10.687 E.01655
G1 X33.687 Y4.935 E.25117
G1 X34.223 Y4.935 E.01655
G1 X27.935 Y11.223 E.27457
G1 X27.935 Y11.759 E.01655
G1 X34.759 Y4.935 E.29797
G1 X35.295 Y4.935 E.01655
G1 X27.935 Y12.295 E.32136
G1 X27.935 Y12.831 E.01655
G1 X35.831 Y4.935 E.34476
G1 X36.367 Y4.935 E.01655
G1 X27.935 Y13.367 E.36816
G1 X27.935 Y13.903 E.01655
G1 X36.903 Y4.935 E.39156
G1 X37.438 Y4.935 E.01655
G1 X27.766 Y14.608 E.42237
G1 X27.766 Y24.789 F30000
G1 F15000
G1 X36.065 Y16.49 E.36238
G1 X36.065 Y15.955 E.01655
G1 X27.935 Y24.084 E.35498
G1 X27.935 Y23.548 E.01655
G1 X36.065 Y15.419 E.35498
G1 X36.065 Y14.883 E.01655
G1 X27.935 Y23.012 E.35498
G1 X27.935 Y22.476 E.01655
G1 X36.065 Y14.347 E.35498
G1 X36.065 Y13.811 E.01655
G1 X27.935 Y21.94 E.35498
G1 X27.935 Y21.405 E.01655
G1 X36.065 Y13.275 E.35498
G1 X36.065 Y12.739 E.01655
G1 X27.935 Y20.869 E.35498
G1 X27.935 Y20.333 E.01655
G1 X36.065 Y12.203 E.35498
G1 X36.065 Y11.668 E.01655
G1 X27.935 Y19.797 E.35497
G1 X27.935 Y19.261 E.01655
G1 X36.065 Y11.132 E.35497
G1 X36.065 Y10.596 E.01655
G1 X27.935 Y18.725 E.35497
G1 X27.935 Y18.189 E.01655
G1 X36.065 Y10.06 E.35497
G1 X36.065 Y9.524 E.01655
G1 X27.935 Y17.654 E.35497
G1 X27.935 Y17.118 E.01655
G1 X36.065 Y8.988 E.35497
G1 X36.065 Y8.452 E.01655
G1 X27.935 Y16.582 E.35497
G1 X27.935 Y16.046 E.01655
G1 X36.065 Y7.917 E.35497
G1 X36.065 Y7.381 E.01655
G1 X27.935 Y15.51 E.35497
G1 X27.935 Y14.974 E.01655
G1 X37.974 Y4.935 E.43836
G1 X38.51 Y4.935 E.01655
G1 X36.581 Y6.865 E.08425
G1 X37.117 Y6.865 E.01655
G1 X39.046 Y4.935 E.08425
G1 X39.582 Y4.935 E.01655
G1 X37.652 Y6.865 E.08425
G1 X38.188 Y6.865 E.01655
G1 X40.118 Y4.935 E.08425
G1 X40.654 Y4.935 E.01655
G1 X38.724 Y6.865 E.08425
G1 X39.26 Y6.865 E.01655
G1 X41.189 Y4.935 E.08425
G1 X41.725 Y4.935 E.01655
G1 X39.796 Y6.865 E.08425
G1 X40.332 Y6.865 E.01655
G1 X42.261 Y4.935 E.08425
G1 X42.797 Y4.935 E.01655
G1 X40.868 Y6.865 E.08425
G1 X41.403 Y6.865 E.01655
G1 X43.065 Y5.203 E.07254
G1 X43.065 Y5.739 E.01655
G1 X41.939 Y6.865 E.04914
G1 X42.475 Y6.865 E.01655
G1 X43.065 Y6.275 E.02574
G1 X43.065 Y6.811 E.01655
G1 X42.841 Y7.034 E.00975
G1 X43.4 Y7.394 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X43.4 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X43.4 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/220
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
G17
G3 Z4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z3.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
M204 S10000
G1 X43.01 Y24.802 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.398 Y24.802 E.01287
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X27.602 Y24.802 E.2322
G1 X27.602 Y7.198 E.58396
G1 X20.602 Y7.198 E.2322
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X36.398 Y7.198 E.2322
G1 X36.398 Y24.802 E.58396
G1 X42.95 Y24.802 E.21734
; WIPE_START
G1 X43.398 Y24.802 E-.17022
G1 X43.398 Y26.354 E-.58978
; WIPE_END
G1 E-.04 F1800
G1 X35.82 Y25.444 Z4.2 F30000
G1 X27.21 Y24.41 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.716 Y25.751 Z4.2 F30000
G1 X43.79 Y27.79 Z4.2
G1 Z3.8
G1 E.8 F1800
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.234 Y25.359 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X43.011 Y25.135 E.00975
G1 X42.475 Y25.135 E.01655
G1 X43.065 Y25.725 E.02574
G1 X43.065 Y26.261 E.01655
G1 X41.939 Y25.135 E.04914
G1 X41.403 Y25.135 E.01655
G1 X43.065 Y26.796 E.07254
G1 X43.065 Y27.065 E.00828
G1 X42.797 Y27.065 E.00826
G1 X40.868 Y25.135 E.08425
G1 X40.332 Y25.135 E.01655
G1 X42.261 Y27.065 E.08425
G1 X41.725 Y27.065 E.01655
G1 X39.796 Y25.135 E.08425
G1 X39.26 Y25.135 E.01655
G1 X41.189 Y27.065 E.08425
G1 X40.654 Y27.065 E.01655
G1 X38.724 Y25.135 E.08425
G1 X38.188 Y25.135 E.01655
G1 X40.118 Y27.065 E.08425
G1 X39.582 Y27.065 E.01655
G1 X37.652 Y25.135 E.08425
G1 X37.117 Y25.135 E.01655
G1 X39.046 Y27.065 E.08425
G1 X38.51 Y27.065 E.01655
G1 X36.581 Y25.135 E.08425
G1 X36.065 Y25.135 E.01593
G1 X36.065 Y24.619 E.01593
G1 X27.935 Y16.49 E.35497
G1 X27.935 Y15.954 E.01655
G1 X36.065 Y24.083 E.35497
G1 X36.065 Y23.548 E.01655
G1 X27.935 Y15.418 E.35497
G1 X27.935 Y14.882 E.01655
G1 X36.065 Y23.012 E.35497
G1 X36.065 Y22.476 E.01655
G1 X27.935 Y14.346 E.35497
G1 X27.935 Y13.811 E.01655
G1 X36.065 Y21.94 E.35497
G1 X36.065 Y21.404 E.01655
G1 X27.935 Y13.275 E.35497
G1 X27.935 Y12.739 E.01655
G1 X36.065 Y20.868 E.35498
G1 X36.065 Y20.332 E.01655
G1 X27.935 Y12.203 E.35498
G1 X27.935 Y11.667 E.01655
G1 X36.065 Y19.797 E.35498
G1 X36.065 Y19.261 E.01655
G1 X27.935 Y11.131 E.35498
G1 X27.935 Y10.595 E.01655
G1 X36.065 Y18.725 E.35498
G1 X36.065 Y18.189 E.01655
G1 X27.935 Y10.06 E.35498
G1 X27.935 Y9.524 E.01655
G1 X36.065 Y17.653 E.35498
G1 X36.065 Y17.117 E.01655
G1 X27.935 Y8.988 E.35498
G1 X27.935 Y8.452 E.01655
G1 X36.065 Y16.581 E.35498
G1 X36.065 Y16.045 E.01655
G1 X27.935 Y7.916 E.35498
G1 X27.935 Y7.38 E.01655
G1 X36.065 Y15.51 E.35498
G1 X36.065 Y14.974 E.01655
G1 X26.026 Y4.935 E.43834
G1 X26.562 Y4.935 E.01655
G1 X36.065 Y14.438 E.41494
G1 X36.065 Y13.902 E.01655
G1 X27.098 Y4.935 E.39154
G1 X27.634 Y4.935 E.01655
G1 X36.065 Y13.366 E.36814
G1 X36.065 Y12.83 E.01655
G1 X28.17 Y4.935 E.34474
G1 X28.706 Y4.935 E.01655
G1 X36.065 Y12.294 E.32134
G1 X36.065 Y11.759 E.01655
G1 X29.241 Y4.935 E.29794
G1 X29.777 Y4.935 E.01655
G1 X36.065 Y11.223 E.27455
G1 X36.065 Y10.687 E.01655
G1 X30.313 Y4.935 E.25115
G1 X30.849 Y4.935 E.01655
G1 X36.065 Y10.151 E.22775
G1 X36.065 Y9.615 E.01655
G1 X31.385 Y4.935 E.20435
G1 X31.921 Y4.935 E.01655
G1 X36.065 Y9.079 E.18095
G1 X36.065 Y8.543 E.01655
G1 X32.457 Y4.935 E.15755
G1 X32.992 Y4.935 E.01655
G1 X36.065 Y8.008 E.13415
G1 X36.065 Y7.472 E.01655
G1 X33.528 Y4.935 E.11075
G1 X34.064 Y4.935 E.01655
G1 X36.065 Y6.936 E.08736
G1 X36.065 Y6.865 E.0022
G1 X36.529 Y6.865 E.01435
G1 X34.6 Y4.935 E.08425
G1 X35.136 Y4.935 E.01655
G1 X37.065 Y6.865 E.08425
G1 X37.601 Y6.865 E.01655
G1 X35.672 Y4.935 E.08425
G1 X36.208 Y4.935 E.01655
G1 X38.137 Y6.865 E.08425
G1 X38.673 Y6.865 E.01655
G1 X36.743 Y4.935 E.08425
G1 X37.279 Y4.935 E.01655
G1 X39.209 Y6.865 E.08425
G1 X39.744 Y6.865 E.01655
G1 X37.815 Y4.935 E.08425
G1 X38.351 Y4.935 E.01655
G1 X40.28 Y6.865 E.08425
G1 X40.816 Y6.865 E.01655
G1 X38.887 Y4.935 E.08425
G1 X39.423 Y4.935 E.01655
G1 X41.352 Y6.865 E.08425
G1 X41.888 Y6.865 E.01655
G1 X39.959 Y4.935 E.08425
G1 X40.494 Y4.935 E.01655
G1 X42.424 Y6.865 E.08425
G1 X42.96 Y6.865 E.01655
G1 X41.03 Y4.935 E.08425
G1 X41.566 Y4.935 E.01655
G1 X43.065 Y6.434 E.06543
G1 X43.065 Y5.898 E.01655
G1 X42.102 Y4.935 E.04204
G1 X42.638 Y4.935 E.01655
G1 X43.234 Y5.532 E.02605
; WIPE_START
G1 X42.638 Y4.935 E-.32055
G1 X42.102 Y4.935 E-.20363
G1 X42.541 Y5.374 E-.23583
; WIPE_END
G1 E-.04 F1800
G1 X43.4 Y7.394 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X43.4 Y24.606 E.54411
; WIPE_START
G1 X43.4 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X38.144 Y27.234 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X27.935 Y17.026 E.44577
G1 X27.935 Y17.562 E.01655
G1 X37.438 Y27.065 E.41496
G1 X36.903 Y27.065 E.01655
G1 X27.935 Y18.097 E.39156
M73 P38 R16
G1 X27.935 Y18.633 E.01655
G1 X36.367 Y27.065 E.36816
G1 X35.831 Y27.065 E.01655
G1 X27.935 Y19.169 E.34476
G1 X27.935 Y19.705 E.01655
G1 X35.295 Y27.065 E.32136
G1 X34.759 Y27.065 E.01655
G1 X27.935 Y20.241 E.29797
G1 X27.935 Y20.777 E.01655
G1 X34.223 Y27.065 E.27457
G1 X33.687 Y27.065 E.01655
G1 X27.935 Y21.313 E.25117
G1 X27.935 Y21.848 E.01655
G1 X33.152 Y27.065 E.22777
G1 X32.616 Y27.065 E.01655
G1 X27.935 Y22.384 E.20437
G1 X27.935 Y22.92 E.01655
G1 X32.08 Y27.065 E.18097
G1 X31.544 Y27.065 E.01655
G1 X27.935 Y23.456 E.15757
G1 X27.935 Y23.992 E.01655
G1 X31.008 Y27.065 E.13417
G1 X30.472 Y27.065 E.01655
G1 X27.935 Y24.528 E.11078
G1 X27.935 Y25.064 E.01655
G1 X29.936 Y27.065 E.08738
G1 X29.401 Y27.065 E.01655
G1 X27.471 Y25.135 E.08425
G1 X26.935 Y25.135 E.01655
G1 X28.865 Y27.065 E.08425
G1 X28.329 Y27.065 E.01655
G1 X26.399 Y25.135 E.08425
G1 X25.864 Y25.135 E.01655
G1 X27.793 Y27.065 E.08425
G1 X27.257 Y27.065 E.01655
G1 X25.328 Y25.135 E.08425
G1 X24.792 Y25.135 E.01655
G1 X26.721 Y27.065 E.08425
G1 X26.185 Y27.065 E.01655
G1 X24.256 Y25.135 E.08425
G1 X23.72 Y25.135 E.01655
G1 X25.649 Y27.065 E.08425
G1 X25.114 Y27.065 E.01655
G1 X23.184 Y25.135 E.08425
G1 X22.648 Y25.135 E.01655
G1 X24.578 Y27.065 E.08425
G1 X24.042 Y27.065 E.01655
G1 X22.113 Y25.135 E.08425
G1 X21.577 Y25.135 E.01655
G1 X23.506 Y27.065 E.08425
G1 X22.97 Y27.065 E.01655
G1 X21.041 Y25.135 E.08425
G1 X20.935 Y25.135 E.00326
G1 X20.935 Y25.566 E.01329
G1 X22.434 Y27.065 E.06546
G1 X21.898 Y27.065 E.01655
G1 X20.935 Y26.102 E.04206
G1 X20.935 Y26.637 E.01655
G1 X21.532 Y27.234 E.02607
; WIPE_START
G1 X20.935 Y26.637 E-.32081
G1 X20.935 Y26.102 E-.20363
G1 X21.374 Y26.54 E-.23556
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y24.606 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.43086
G1 F15000
G1 X20.6 Y7.394 E.54411
G1 X20.766 Y6.641 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42183
G1 F15000
G1 X20.989 Y6.865 E.00977
G1 X21.525 Y6.865 E.01655
G1 X20.935 Y6.275 E.02576
G1 X20.935 Y5.739 E.01655
G1 X22.061 Y6.865 E.04916
G1 X22.597 Y6.865 E.01655
G1 X20.935 Y5.203 E.07256
G1 X20.935 Y4.935 E.00826
G1 X21.203 Y4.935 E.00828
G1 X23.133 Y6.865 E.08425
G1 X23.669 Y6.865 E.01655
G1 X21.739 Y4.935 E.08425
G1 X22.275 Y4.935 E.01655
G1 X24.205 Y6.865 E.08425
G1 X24.74 Y6.865 E.01655
G1 X22.811 Y4.935 E.08425
G1 X23.347 Y4.935 E.01655
G1 X25.276 Y6.865 E.08425
G1 X25.812 Y6.865 E.01655
G1 X23.883 Y4.935 E.08425
G1 X24.419 Y4.935 E.01655
G1 X26.348 Y6.865 E.08425
G1 X26.884 Y6.865 E.01655
G1 X24.955 Y4.935 E.08425
G1 X25.49 Y4.935 E.01655
G1 X27.589 Y7.034 E.09166
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X26.175 Y5.62 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/220
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
G17
G3 Z4.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X43.01 Y24.41
G1 Z4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X36.79 Y24.41 E.19112
G1 X36.79 Y7.59 E.51683
G1 X43.01 Y7.59 E.19112
G1 X43.01 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X41.01 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X41.923 Y16.792 Z4.4 F30000
G1 X43.078 Y7.198 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X43.078 Y4.922 E.07549
G1 X20.922 Y4.922 E.73494
G1 X20.922 Y7.198 E.07549
G1 X20.602 Y7.198 E.01062
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X43.138 Y7.198 E.00863
; WIPE_START
G1 X43.085 Y5.199 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X38.223 Y11.082 Z4.4 F30000
G1 X27.21 Y24.41 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.99 Y24.41 E.19112
G1 X20.99 Y7.59 E.51683
G1 X27.21 Y7.59 E.19112
G1 X27.21 Y24.35 E.51499
; WIPE_START
M204 S10000
G1 X25.21 Y24.369 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.739 Y25.623 Z4.4 F30000
G1 X43.398 Y27.398 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X20.922 Y24.802 E.01062
G1 X20.922 Y27.078 E.07549
G1 X43.078 Y27.078 E.73494
G1 X43.078 Y24.802 E.07549
G1 X43.398 Y24.802 E.01062
G1 X43.398 Y27.338 E.08412
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.208 Y26.855 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Top surface
G1 F12000
M204 S2000
G1 X42.855 Y26.208 E.02811
G1 X42.855 Y25.675
G1 X41.675 Y26.855 E.05129
G1 X41.142 Y26.855
G1 X42.855 Y25.142 E.07446
G1 X42.846 Y24.617
G1 X40.609 Y26.855 E.09725
G1 X40.075 Y26.855
G1 X42.313 Y24.617 E.09725
G1 X41.78 Y24.617
G1 X39.542 Y26.855 E.09725
G1 X39.009 Y26.855
G1 X41.247 Y24.617 E.09725
G1 X40.713 Y24.617
G1 X38.476 Y26.855 E.09725
G1 X37.942 Y26.855
G1 X40.18 Y24.617 E.09725
G1 X39.647 Y24.617
G1 X37.409 Y26.855 E.09725
G1 X36.876 Y26.855
G1 X39.114 Y24.617 E.09725
G1 X38.58 Y24.617
G1 X36.342 Y26.855 E.09725
G1 X35.809 Y26.855
G1 X38.047 Y24.617 E.09725
G1 X37.514 Y24.617
G1 X35.276 Y26.855 E.09725
G1 X34.743 Y26.855
G1 X36.981 Y24.617 E.09725
G1 X36.583 Y24.482
G1 X34.209 Y26.855 E.10313
G1 X33.676 Y26.855
G1 X36.583 Y23.949 E.1263
G1 X36.583 Y23.416
G1 X33.143 Y26.855 E.14947
G1 X32.61 Y26.855
G1 X36.583 Y22.882 E.17264
G1 X36.583 Y22.349
G1 X32.076 Y26.855 E.19582
G1 X31.543 Y26.855
G1 X36.583 Y21.816 E.21899
G1 X36.583 Y21.283
G1 X31.01 Y26.855 E.24216
G1 X30.477 Y26.855
G1 X36.583 Y20.749 E.26533
G1 X36.583 Y20.216
G1 X29.943 Y26.855 E.28851
G1 X29.41 Y26.855
G1 X36.583 Y19.683 E.31168
G1 X36.583 Y19.15
G1 X28.877 Y26.855 E.33485
G1 X28.344 Y26.855
G1 X36.583 Y18.616 E.35802
G1 X36.583 Y18.083
G1 X27.81 Y26.855 E.3812
G1 X27.277 Y26.855
G1 X36.583 Y17.55 E.40437
M73 P38 R15
G1 X36.583 Y17.017
G1 X26.744 Y26.855 E.42754
G1 X26.211 Y26.855
G1 X36.583 Y16.483 E.45071
G1 X36.583 Y15.95
G1 X25.677 Y26.855 E.47389
G1 X25.144 Y26.855
G1 X27.382 Y24.617 E.09725
G1 X26.849 Y24.617
G1 X24.611 Y26.855 E.09725
G1 X24.078 Y26.855
G1 X26.315 Y24.617 E.09725
G1 X25.782 Y24.617
G1 X23.544 Y26.855 E.09725
G1 X23.011 Y26.855
G1 X25.249 Y24.617 E.09725
G1 X24.716 Y24.617
G1 X22.478 Y26.855 E.09725
G1 X21.945 Y26.855
G1 X24.182 Y24.617 E.09725
G1 X23.649 Y24.617
G1 X21.411 Y26.855 E.09725
G1 X21.145 Y26.589
G1 X23.116 Y24.617 E.08566
G1 X22.583 Y24.617
G1 X21.145 Y26.055 E.06249
G1 X21.145 Y25.522
G1 X22.049 Y24.617 E.03931
G1 X21.516 Y24.617
G1 X21.145 Y24.989 E.01614
; WIPE_START
M204 S10000
G1 X21.516 Y24.617 E-.1996
G1 X22.049 Y24.617 E-.20264
G1 X21.384 Y25.283 E-.35777
; WIPE_END
G1 E-.04 F1800
G1 X27.417 Y24.582 Z4.4 F30000
G1 Z4
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X36.583 Y15.417 E.39827
G1 X36.583 Y14.883
G1 X27.417 Y24.049 E.39827
G1 X27.417 Y23.515
G1 X36.583 Y14.35 E.39827
G1 X36.583 Y13.817
G1 X27.417 Y22.982 E.39827
G1 X27.417 Y22.449
G1 X36.583 Y13.284 E.39827
G1 X36.583 Y12.75
G1 X27.417 Y21.916 E.39827
G1 X27.417 Y21.382
G1 X36.583 Y12.217 E.39827
G1 X36.583 Y11.684
G1 X27.417 Y20.849 E.39827
G1 X27.417 Y20.316
G1 X36.583 Y11.151 E.39827
G1 X36.583 Y10.617
G1 X27.417 Y19.783 E.39827
G1 X27.417 Y19.249
G1 X36.583 Y10.084 E.39827
G1 X36.583 Y9.551
G1 X27.417 Y18.716 E.39827
G1 X27.417 Y18.183
G1 X36.583 Y9.018 E.39827
G1 X36.583 Y8.484
G1 X27.417 Y17.65 E.39827
G1 X27.417 Y17.116
G1 X36.583 Y7.951 E.39827
G1 X36.583 Y7.418
G1 X27.417 Y16.583 E.39827
; WIPE_START
M204 S10000
G1 X28.832 Y15.169 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X35.429 Y11.331 Z4.4 F30000
G1 X42.855 Y7.011 Z4.4
G1 Z4
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X42.484 Y7.383 E.01615
G1 X41.95 Y7.383
G1 X42.855 Y6.478 E.03932
G1 X42.855 Y5.945
G1 X41.417 Y7.383 E.06249
G1 X40.884 Y7.383
G1 X42.855 Y5.411 E.08566
G1 X42.589 Y5.145
G1 X40.351 Y7.383 E.09725
G1 X39.817 Y7.383
G1 X42.055 Y5.145 E.09725
G1 X41.522 Y5.145
G1 X39.284 Y7.383 E.09725
G1 X38.751 Y7.383
G1 X40.989 Y5.145 E.09725
G1 X40.456 Y5.145
G1 X38.218 Y7.383 E.09725
G1 X37.684 Y7.383
G1 X39.922 Y5.145 E.09725
G1 X39.389 Y5.145
G1 X37.151 Y7.383 E.09725
G1 X36.618 Y7.383
G1 X38.856 Y5.145 E.09725
G1 X38.323 Y5.145
G1 X27.417 Y16.05 E.47388
G1 X27.417 Y15.517
G1 X37.789 Y5.145 E.45071
G1 X37.256 Y5.145
G1 X27.417 Y14.983 E.42754
G1 X27.417 Y14.45
G1 X36.723 Y5.145 E.40436
G1 X36.189 Y5.145
G1 X27.417 Y13.917 E.38119
G1 X27.417 Y13.384
G1 X35.656 Y5.145 E.35802
G1 X35.123 Y5.145
G1 X27.417 Y12.85 E.33485
G1 X27.417 Y12.317
G1 X34.59 Y5.145 E.31167
G1 X34.056 Y5.145
G1 X27.417 Y11.784 E.2885
G1 X27.417 Y11.251
G1 X33.523 Y5.145 E.26533
G1 X32.99 Y5.145
G1 X27.417 Y10.717 E.24216
G1 X27.417 Y10.184
G1 X32.457 Y5.145 E.21898
G1 X31.923 Y5.145
G1 X27.417 Y9.651 E.19581
G1 X27.417 Y9.118
G1 X31.39 Y5.145 E.17264
G1 X30.857 Y5.145
G1 X27.417 Y8.584 E.14946
G1 X27.417 Y8.051
G1 X30.324 Y5.145 E.12629
G1 X29.79 Y5.145
G1 X27.417 Y7.518 E.10312
G1 X27.019 Y7.383
G1 X29.257 Y5.145 E.09725
G1 X28.724 Y5.145
G1 X26.486 Y7.383 E.09725
G1 X25.953 Y7.383
G1 X28.191 Y5.145 E.09725
G1 X27.657 Y5.145
G1 X25.419 Y7.383 E.09725
G1 X24.886 Y7.383
G1 X27.124 Y5.145 E.09725
G1 X26.591 Y5.145
G1 X24.353 Y7.383 E.09725
G1 X23.82 Y7.383
G1 X26.058 Y5.145 E.09725
G1 X25.524 Y5.145
G1 X23.286 Y7.383 E.09725
G1 X22.753 Y7.383
G1 X24.991 Y5.145 E.09725
G1 X24.458 Y5.145
G1 X22.22 Y7.383 E.09725
G1 X21.687 Y7.383
G1 X23.925 Y5.145 E.09725
G1 X23.391 Y5.145
G1 X21.153 Y7.383 E.09725
G1 X21.145 Y6.858
G1 X22.858 Y5.145 E.07445
G1 X22.325 Y5.145
G1 X21.145 Y6.325 E.05128
M73 P39 R15
G1 X21.145 Y5.792
G1 X21.792 Y5.145 E.02811
; WIPE_START
M204 S10000
G1 X21.145 Y5.792 E-.3476
G1 X21.145 Y6.325 E-.20264
G1 X21.535 Y5.934 E-.20976
; WIPE_END
G1 E-.04 F1800
G1 X29.132 Y6.666 Z4.4 F30000
G1 X36.584 Y7.384 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.0928122
G1 F15000
G1 X36.467 Y7.267 E.00067
; WIPE_START
G1 X36.584 Y7.384 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X33.054 Y14.151 Z4.4 F30000
G1 X27.533 Y24.733 Z4.4
G1 Z4
G1 E.8 F1800
; LINE_WIDTH: 0.0908421
G1 F15000
G1 X27.416 Y24.616 E.00064
G1 X27.409 Y24.574 E.00017
; WIPE_START
G1 X27.416 Y24.616 E-.15811
G1 X27.533 Y24.733 E-.60189
; WIPE_END
G1 E-.04 F1800
G1 X20.6 Y24.606 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; LINE_WIDTH: 0.43086
G1 F15000
G1 X20.6 Y7.394 E.54411
; WIPE_START
G1 X20.6 Y9.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.203 Y8.727 Z4.4 F30000
G1 X43.4 Y7.394 Z4.4
G1 Z4
G1 E.8 F1800
G1 F15000
G1 X43.4 Y24.606 E.54411
; CHANGE_LAYER
; Z_HEIGHT: 4.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X43.4 Y22.606 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/220
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
G17
G3 Z4.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y7.198
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6086
G1 X42.602 Y5.398 E.05971
G1 X21.398 Y5.398 E.70338
G1 X21.398 Y7.198 E.05971
G1 X20.602 Y7.198 E.0264
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X42.662 Y7.198 E.02441
; WIPE_START
G1 F15476.087
G1 X42.602 Y5.398 E-.68438
G1 X42.403 Y5.398 E-.07562
; WIPE_END
G1 E-.04 F1800
G1 X42.332 Y13.03 Z4.6 F30000
G1 X42.21 Y26.21 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6086
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.41 E.05531
G1 X20.99 Y24.41 E.02458
G1 X20.99 Y7.59 E.51683
G1 X21.79 Y7.59 E.02458
G1 X21.79 Y5.79 E.05531
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.59 E.05531
G1 X43.01 Y7.59 E.02458
G1 X43.01 Y24.41 E.51683
G1 X42.21 Y24.41 E.02458
G1 X42.21 Y26.15 E.05347
M204 S10000
G1 X42.21 Y26.602 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6086
G1 X42.602 Y26.602 E.01301
G1 X42.602 Y24.802 E.05971
G1 X43.398 Y24.802 E.0264
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X21.398 Y24.802 E.0264
G1 X21.398 Y26.602 E.05971
G1 X42.15 Y26.602 E.68838
; WIPE_START
G1 F15476.087
G1 X42.602 Y26.602 E-.17179
G1 X42.602 Y25.054 E-.58821
; WIPE_END
G1 E-.04 F1800
G1 X43.79 Y27.79 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6086
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.4484
G1 F6086
G1 X43 Y26.806 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y25.006 E.05703
G1 X43.4 Y24.606 F30000
; LINE_WIDTH: 0.43086
G1 F6086
G1 X43.4 Y7.394 E.54411
G1 X43 Y6.994 F30000
; LINE_WIDTH: 0.43172
G1 F6086
G1 X43 Y5.194 E.05703
; LINE_WIDTH: 0.448395
G1 X42.983 Y5.114 E.00272
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00287
G1 X42.806 Y5 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y5 E.68469
; LINE_WIDTH: 0.448395
G1 X21.114 Y5.017 E.00272
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00287
G1 X21 Y5.194 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y6.994 E.05703
G1 X20.6 Y7.394 F30000
; LINE_WIDTH: 0.43086
G1 F6086
G1 X20.6 Y24.606 E.54411
G1 X21 Y25.006 F30000
; LINE_WIDTH: 0.43172
G1 F6086
G1 X21 Y26.806 E.05703
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00573
G1 X21.114 Y26.983 E.00287
; LINE_WIDTH: 0.4484
G1 X21.194 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y27 E.68469
; LINE_WIDTH: 0.470633
G1 X42.967 Y26.967 E.00573
G1 X42.983 Y26.886 E.00287
; CHANGE_LAYER
; Z_HEIGHT: 4.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.502
G1 X42.967 Y26.967 E-.25334
G1 X42.806 Y27 E-.50666
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/220
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
G17
G3 Z4.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y7.198
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6085
G1 X42.602 Y5.398 E.05971
G1 X21.398 Y5.398 E.70338
G1 X21.398 Y7.198 E.05971
G1 X20.602 Y7.198 E.0264
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X42.662 Y7.198 E.02441
; WIPE_START
G1 F15476.087
G1 X42.602 Y5.398 E-.68438
G1 X42.403 Y5.398 E-.07562
; WIPE_END
G1 E-.04 F1800
G1 X42.332 Y13.03 Z4.8 F30000
G1 X42.21 Y26.21 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6085
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.41 E.05531
G1 X20.99 Y24.41 E.02458
G1 X20.99 Y7.59 E.51683
G1 X21.79 Y7.59 E.02458
G1 X21.79 Y5.79 E.05531
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.59 E.05531
G1 X43.01 Y7.59 E.02458
G1 X43.01 Y24.41 E.51683
G1 X42.21 Y24.41 E.02458
G1 X42.21 Y26.15 E.05347
M204 S10000
G1 X42.21 Y26.602 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6085
G1 X42.602 Y26.602 E.01301
G1 X42.602 Y24.802 E.05971
G1 X43.398 Y24.802 E.0264
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X21.398 Y24.802 E.0264
G1 X21.398 Y26.602 E.05971
G1 X42.15 Y26.602 E.68838
; WIPE_START
G1 F15476.087
G1 X42.602 Y26.602 E-.17179
G1 X42.602 Y25.054 E-.58821
; WIPE_END
G1 E-.04 F1800
G1 X43.79 Y27.79 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6085
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.4484
G1 F6085
G1 X43 Y26.806 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y25.006 E.05703
G1 X43.4 Y24.606 F30000
; LINE_WIDTH: 0.43086
G1 F6085
G1 X43.4 Y7.394 E.54411
G1 X43 Y6.994 F30000
; LINE_WIDTH: 0.43172
G1 F6085
G1 X43 Y5.194 E.05703
; LINE_WIDTH: 0.448395
G1 X42.983 Y5.114 E.00272
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00287
G1 X42.806 Y5 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y5 E.68469
; LINE_WIDTH: 0.448395
G1 X21.114 Y5.017 E.00272
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00287
G1 X21 Y5.194 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y6.994 E.05703
G1 X20.6 Y7.394 F30000
; LINE_WIDTH: 0.43086
G1 F6085
G1 X20.6 Y24.606 E.54411
G1 X21 Y25.006 F30000
; LINE_WIDTH: 0.43172
G1 F6085
G1 X21 Y26.806 E.05703
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00573
G1 X21.114 Y26.983 E.00287
; LINE_WIDTH: 0.4484
G1 X21.194 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y27 E.68469
; LINE_WIDTH: 0.470633
G1 X42.967 Y26.967 E.00573
G1 X42.983 Y26.886 E.00287
; CHANGE_LAYER
; Z_HEIGHT: 4.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.502
G1 X42.967 Y26.967 E-.25334
G1 X42.806 Y27 E-.50666
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/220
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
G17
G3 Z4.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.21 Y26.21
G1 Z4.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6855
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.41 E.05531
G1 X21.54 Y24.41 E.00768
G1 X21.14 Y24.41 E.01229
G1 F3312.605
G1 X21.14 Y24.369 E.00126
G1 F2880
G1 X21.14 Y7.631 E.51431
G1 F3312.605
G1 X21.14 Y7.59 E.00126
G1 F6855
G1 X21.54 Y7.59 E.01229
G1 X21.79 Y7.59 E.00768
G1 X21.79 Y5.79 E.05531
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.59 E.05531
G1 X42.46 Y7.59 E.00768
G1 X42.86 Y7.59 E.01229
G1 F3312.605
G1 X42.86 Y7.631 E.00126
G1 F2880
G1 X42.86 Y24.369 E.51431
G1 F3312.605
G1 X42.86 Y24.41 E.00126
G1 F6855
G1 X42.46 Y24.41 E.01229
G1 X42.21 Y24.41 E.00768
G1 X42.21 Y26.15 E.05347
M204 S10000
G1 X42.21 Y26.602 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6855
G1 X42.602 Y26.602 E.01301
G1 X42.602 Y24.802 E.05971
G1 X43.398 Y24.802 E.0264
G1 X43.398 Y27.398 E.08611
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y24.802 E.08611
G1 X21.398 Y24.802 E.0264
G1 X21.398 Y26.602 E.05971
G1 X42.15 Y26.602 E.68838
; WIPE_START
G1 F15476.087
G1 X42.602 Y26.602 E-.17179
G1 X42.602 Y25.054 E-.58821
; WIPE_END
G1 E-.04 F1800
G1 X42.602 Y17.422 Z5 F30000
G1 X42.602 Y7.198 Z5
G1 Z4.6
G1 E.8 F1800
G1 F6855
G1 X42.602 Y5.398 E.05971
G1 X21.398 Y5.398 E.70338
G1 X21.398 Y7.198 E.05971
G1 X20.602 Y7.198 E.0264
G1 X20.602 Y4.602 E.08611
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y7.198 E.08611
G1 X42.662 Y7.198 E.02441
; WIPE_START
G1 F15476.087
G1 X42.602 Y5.398 E-.68438
G1 X42.403 Y5.398 E-.07562
; WIPE_END
G1 E-.04 F1800
G1 X42.875 Y13.016 Z5 F30000
G1 X43.79 Y27.79 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6855
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
M73 P40 R15
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.4484
G1 F6855
G1 X43 Y26.806 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y25.006 E.05703
G1 X43.325 Y24.606 F30000
; LINE_WIDTH: 0.58086
G1 F6855
G1 X43.325 Y7.394 E.75449
G1 X43 Y6.994 F30000
; LINE_WIDTH: 0.43172
G1 F6855
G1 X43 Y5.194 E.05703
; LINE_WIDTH: 0.448395
G1 X42.983 Y5.114 E.00272
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00287
G1 X42.806 Y5 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y5 E.68469
; LINE_WIDTH: 0.448395
G1 X21.114 Y5.017 E.00272
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00287
G1 X21 Y5.194 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y6.994 E.05703
G1 X20.675 Y7.394 F30000
; LINE_WIDTH: 0.58086
G1 F6855
G1 X20.675 Y24.606 E.75449
G1 X21 Y25.006 F30000
; LINE_WIDTH: 0.43172
G1 F6855
G1 X21 Y26.806 E.05703
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00573
G1 X21.114 Y26.983 E.00287
; LINE_WIDTH: 0.4484
G1 X21.194 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y27 E.68469
; LINE_WIDTH: 0.470633
G1 X42.967 Y26.967 E.00573
G1 X42.983 Y26.886 E.00287
; CHANGE_LAYER
; Z_HEIGHT: 4.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.502
G1 X42.967 Y26.967 E-.25334
G1 X42.806 Y27 E-.50666
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/220
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
G17
G3 Z5 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8051
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y24.802 E.05971
G1 X20.948 Y24.802 E.01493
G1 X20.948 Y7.198 E.58396
G1 X21.398 Y7.198 E.01493
G1 X21.398 Y5.398 E.05971
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y7.198 E.05971
G1 X43.052 Y7.198 E.01493
G1 X43.052 Y24.802 E.58396
G1 X42.602 Y24.802 E.01493
G1 X42.602 Y26.15 E.04471
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8051
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.81 E.04302
G1 X21.79 Y24.41 E.01229
G1 X21.34 Y24.41 E.01383
G1 F2536.674
G1 X21.34 Y24.369 E.00126
G1 F2160
G1 X21.34 Y7.631 E.51431
G1 F2536.674
G1 X21.34 Y7.59 E.00126
G1 F8051
G1 X21.79 Y7.59 E.01383
G1 X21.79 Y7.19 E.01229
G1 X21.79 Y5.79 E.04302
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.19 E.04302
G1 X42.21 Y7.59 E.01229
G1 X42.66 Y7.59 E.01383
G1 F2536.674
G1 X42.66 Y7.631 E.00126
G1 F2160
G1 X42.66 Y24.369 E.51431
G1 F2536.674
G1 X42.66 Y24.41 E.00126
G1 F8051
G1 X42.21 Y24.41 E.01383
G1 X42.21 Y24.81 E.01229
G1 X42.21 Y26.15 E.04117
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8051
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8051
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.4484
G1 F8051
G1 X43 Y26.806 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y25.006 E.05703
G1 X42.983 Y26.886 F30000
; LINE_WIDTH: 0.470633
G1 F8051
G1 X42.967 Y26.967 E.00287
G1 X42.806 Y27 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.4484
G1 X21.114 Y26.983 E.00272
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00287
G1 X21 Y26.806 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y25.006 E.05703
; WIPE_START
G1 F15000
G1 X21 Y26.806 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21 Y19.173 Z5.2 F30000
G1 X21 Y6.994 Z5.2
G1 Z4.8
G1 E.8 F1800
G1 F8051
G1 X21 Y5.194 E.05703
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00573
G1 X21.114 Y5.017 E.00287
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y6.994 E.05703
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X43 Y5.194 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/220
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
G17
G3 Z5.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8676
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y24.802 E.05971
G1 X21.148 Y24.802 E.00829
G1 X21.148 Y7.198 E.58396
G1 X21.398 Y7.198 E.00829
G1 X21.398 Y5.398 E.05971
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y7.198 E.05971
G1 X42.852 Y7.198 E.00829
G1 X42.852 Y24.802 E.58396
G1 X42.602 Y24.802 E.00829
G1 X42.602 Y26.15 E.04471
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8676
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.81 E.04302
G1 X21.79 Y24.41 E.01229
G1 F5488.214
G1 X21.54 Y24.41 E.00768
G1 F2536.674
G1 X21.54 Y24.369 E.00126
G1 F2160
G1 X21.54 Y7.631 E.51431
G1 F2536.674
G1 X21.54 Y7.59 E.00126
G1 F5488.214
G1 X21.79 Y7.59 E.00768
G1 F8676
G1 X21.79 Y7.19 E.01229
G1 X21.79 Y5.79 E.04302
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.19 E.04302
G1 X42.21 Y7.59 E.01229
G1 F5488.214
G1 X42.46 Y7.59 E.00768
G1 F2536.674
G1 X42.46 Y7.631 E.00126
G1 F2160
G1 X42.46 Y24.369 E.51431
G1 F2536.674
G1 X42.46 Y24.41 E.00126
G1 F5488.214
G1 X42.21 Y24.41 E.00768
G1 F8676
G1 X42.21 Y24.81 E.01229
G1 X42.21 Y26.15 E.04117
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8676
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8676
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470633
G1 F8676
G1 X42.967 Y26.967 E.00287
G1 X42.806 Y27 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.4484
G1 X21.114 Y26.983 E.00272
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00287
G1 X21 Y26.806 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y25.2 E.05087
G1 X20.944 Y25.144 F30000
; LINE_WIDTH: 0.297387
G1 F8676
G1 X20.921 Y25.098 E.00107
; LINE_WIDTH: 0.25112
G1 X20.898 Y25.052 E.00088
; LINE_WIDTH: 0.204854
G1 X20.875 Y25.006 E.00068
; LINE_WIDTH: 0.181787
G1 X20.875 Y6.994 E.20381
G1 X20.898 Y6.948 E.00059
; LINE_WIDTH: 0.25112
G1 X20.921 Y6.902 E.00088
; LINE_WIDTH: 0.297387
G1 X20.944 Y6.856 E.00107
G1 X21 Y6.8 F30000
; LINE_WIDTH: 0.43172
G1 F8676
G1 X21 Y5.194 E.05087
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00573
G1 X21.114 Y5.017 E.00287
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y6.8 E.05087
G1 X43.056 Y6.856 F30000
; LINE_WIDTH: 0.297387
G1 F8676
G1 X43.079 Y6.902 E.00107
; LINE_WIDTH: 0.25112
G1 X43.102 Y6.948 E.00088
; LINE_WIDTH: 0.204854
G1 X43.125 Y6.994 E.00068
; LINE_WIDTH: 0.181787
G1 X43.125 Y25.006 E.20381
G1 X43.102 Y25.052 E.00059
; LINE_WIDTH: 0.25112
G1 X43.079 Y25.098 E.00088
; LINE_WIDTH: 0.297387
G1 X43.056 Y25.144 E.00107
G1 X43 Y25.2 F30000
; LINE_WIDTH: 0.43172
G1 F8676
G1 X43 Y26.806 E.05087
; LINE_WIDTH: 0.4484
G1 X42.983 Y26.886 E.00272
; CHANGE_LAYER
; Z_HEIGHT: 5.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X43 Y26.806 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/220
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
G17
G3 Z5.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8801
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y24.802 E.05971
G1 X21.348 Y24.802 E.00166
G1 X21.348 Y7.198 E.58396
G1 X21.398 Y7.198 E.00166
G1 X21.398 Y5.398 E.05971
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y7.198 E.05971
G1 X42.652 Y7.198 E.00166
G1 X42.652 Y24.802 E.58396
G1 X42.602 Y24.802 E.00166
G1 X42.602 Y26.15 E.04471
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8801
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y25.21 E.03073
G1 X21.79 Y24.81 E.01229
G1 F8659.447
G1 X21.79 Y24.41 E.01229
G1 F3036.982
G1 X21.74 Y24.41 E.00154
G1 F2536.674
G1 X21.74 Y24.369 E.00126
G1 F2160
G1 X21.74 Y7.631 E.51431
G1 F2536.674
G1 X21.74 Y7.59 E.00126
G1 F3036.982
G1 X21.79 Y7.59 E.00154
G1 F8659.447
G1 X21.79 Y7.19 E.01229
G1 F8801
G1 X21.79 Y6.79 E.01229
G1 X21.79 Y5.79 E.03073
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y6.79 E.03073
G1 X42.21 Y7.19 E.01229
G1 F8659.447
G1 X42.21 Y7.59 E.01229
G1 F3036.982
G1 X42.26 Y7.59 E.00154
G1 F2536.674
G1 X42.26 Y7.631 E.00126
G1 F2160
G1 X42.26 Y24.369 E.51431
G1 F2536.674
G1 X42.26 Y24.41 E.00126
G1 F3036.982
G1 X42.21 Y24.41 E.00154
G1 F8659.447
G1 X42.21 Y24.81 E.01229
G1 F8801
G1 X42.21 Y25.21 E.01229
G1 X42.21 Y26.15 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8801
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8801
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.983 Y26.886 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.4484
G1 F8801
G1 X43 Y26.806 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y25.136 E.0529
G1 X42.856 Y25.056 F30000
; LINE_WIDTH: 0.166987
G1 F8801
G1 X42.88 Y25.069 E.00028
; LINE_WIDTH: 0.21512
G1 X42.904 Y25.082 E.00039
; LINE_WIDTH: 0.263254
G1 X42.928 Y25.096 E.00049
; LINE_WIDTH: 0.311387
G1 X42.952 Y25.109 E.0006
; LINE_WIDTH: 0.35952
G1 X42.976 Y25.122 E.00071
; LINE_WIDTH: 0.382121
G1 X43 Y25.136 E.00076
G1 X43.025 Y25.006 E.00366
G1 X43.025 Y6.994 E.49784
G1 X43 Y6.864 E.00366
G1 X42.856 Y6.944 F30000
; LINE_WIDTH: 0.166987
M73 P41 R15
G1 F8801
G1 X42.88 Y6.931 E.00028
; LINE_WIDTH: 0.215119
G1 X42.904 Y6.918 E.00039
; LINE_WIDTH: 0.263252
G1 X42.928 Y6.904 E.00049
; LINE_WIDTH: 0.311384
G1 X42.952 Y6.891 E.0006
; LINE_WIDTH: 0.359517
G1 X42.976 Y6.878 E.00071
; LINE_WIDTH: 0.407649
G1 X43 Y6.864 E.00082
; LINE_WIDTH: 0.43172
G1 X43 Y5.194 E.0529
; LINE_WIDTH: 0.448395
G1 X42.983 Y5.114 E.00272
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00287
G1 X42.806 Y5 E.00573
; LINE_WIDTH: 0.43172
G1 X21.194 Y5 E.68469
; LINE_WIDTH: 0.448395
G1 X21.114 Y5.017 E.00272
; LINE_WIDTH: 0.470635
G1 X21.033 Y5.033 E.00287
G1 X21 Y5.194 E.00573
; LINE_WIDTH: 0.43172
G1 X21 Y6.864 E.0529
; LINE_WIDTH: 0.382083
G1 X20.975 Y6.994 E.00366
G1 X20.975 Y25.006 E.49778
G1 X21 Y25.136 E.00366
G1 X21.144 Y25.056 F30000
; LINE_WIDTH: 0.166987
G1 F8801
G1 X21.12 Y25.069 E.00028
; LINE_WIDTH: 0.215119
G1 X21.096 Y25.082 E.00039
; LINE_WIDTH: 0.263252
G1 X21.072 Y25.096 E.00049
; LINE_WIDTH: 0.311384
G1 X21.048 Y25.109 E.0006
; LINE_WIDTH: 0.359517
G1 X21.024 Y25.122 E.00071
; LINE_WIDTH: 0.407649
G1 X21 Y25.136 E.00082
; LINE_WIDTH: 0.43172
G1 X21 Y26.806 E.0529
; LINE_WIDTH: 0.470633
G1 X21.033 Y26.967 E.00573
G1 X21.114 Y26.983 E.00287
; LINE_WIDTH: 0.4484
G1 X21.194 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y27 E.68469
; LINE_WIDTH: 0.470633
G1 X42.967 Y26.967 E.00573
G1 X42.983 Y26.886 E.00287
; WIPE_START
G1 F14729.502
G1 X42.967 Y26.967 E-.25334
G1 X42.806 Y27 E-.50666
; WIPE_END
G1 E-.04 F1800
G1 X37.205 Y21.815 Z5.6 F30000
G1 X21.144 Y6.944 Z5.6
G1 Z5.2
G1 E.8 F1800
; LINE_WIDTH: 0.166987
G1 F8801
G1 X21.12 Y6.931 E.00028
; LINE_WIDTH: 0.21512
G1 X21.096 Y6.918 E.00039
; LINE_WIDTH: 0.263254
G1 X21.072 Y6.904 E.00049
; LINE_WIDTH: 0.311387
G1 X21.048 Y6.891 E.0006
; LINE_WIDTH: 0.35952
G1 X21.024 Y6.878 E.00071
; LINE_WIDTH: 0.407654
G1 X21 Y6.864 E.00082
; CHANGE_LAYER
; Z_HEIGHT: 5.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.024 Y6.878 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/220
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
G17
G3 Z5.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7035
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7035
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y24.369 E.05657
G1 X21.79 Y7.631 E.51431
G1 X21.79 Y5.79 E.05657
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y7.631 E.05657
G1 X42.21 Y24.369 E.51431
G1 X42.21 Y26.15 E.05473
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F7035
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F7035
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F7035
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 5.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/220
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
G17
G3 Z5.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 5.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/220
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
G17
G3 Z6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/220
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
G17
G3 Z6.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
M73 P42 R15
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/220
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
G17
G3 Z6.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
M73 P42 R14
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 6.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/220
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
G17
G3 Z6.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 6.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/220
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
G17
G3 Z6.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 6.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/220
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
G17
G3 Z7 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
M73 P43 R14
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 7
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/220
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
G17
G3 Z7.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 7.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/220
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
G17
G3 Z7.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/220
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
G17
G3 Z7.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
M73 P44 R14
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 7.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/220
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
G17
G3 Z7.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 7.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/220
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
G17
G3 Z8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/220
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
G17
G3 Z8.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z8.4 F30000
G1 Z8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z8.4 F30000
G1 Z8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 8.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/220
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
G17
M73 P45 R14
G3 Z8.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z8.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z8.6 F30000
G1 Z8.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z8.6 F30000
G1 Z8.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 8.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 42/220
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
G17
G3 Z8.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z8.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z8.8 F30000
G1 Z8.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z8.8 F30000
G1 Z8.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/220
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
G17
G3 Z8.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z9 F30000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z9 F30000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 8.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/220
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
G17
G3 Z9 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z8.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z9.2 F30000
G1 Z8.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
M73 P46 R14
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z9.2 F30000
G1 Z8.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
M73 P46 R13
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 9
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 45/220
; update layer progress
M73 L45
M991 S0 P44 ;notify layer change
G17
G3 Z9.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z9
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z9.4 F30000
G1 Z9
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z9.4 F30000
G1 Z9
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 9.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 46/220
; update layer progress
M73 L46
M991 S0 P45 ;notify layer change
G17
G3 Z9.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z9.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z9.6 F30000
G1 Z9.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z9.6 F30000
G1 Z9.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 9.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 47/220
; update layer progress
M73 L47
M991 S0 P46 ;notify layer change
G17
G3 Z9.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z9.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z9.8 F30000
G1 Z9.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z9.8 F30000
G1 Z9.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
M73 P47 R13
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 9.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 48/220
; update layer progress
M73 L48
M991 S0 P47 ;notify layer change
G17
G3 Z9.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z9.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z10 F30000
G1 Z9.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z10 F30000
G1 Z9.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 49/220
; update layer progress
M73 L49
M991 S0 P48 ;notify layer change
G17
G3 Z10 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z10.2 F30000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z10.2 F30000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 10
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 50/220
; update layer progress
M73 L50
M991 S0 P49 ;notify layer change
G17
G3 Z10.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z10
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z10.4 F30000
G1 Z10
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z10.4 F30000
G1 Z10
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 10.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 51/220
; update layer progress
M73 L51
M991 S0 P50 ;notify layer change
G17
G3 Z10.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z10.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
M73 P48 R13
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z10.6 F30000
G1 Z10.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z10.6 F30000
G1 Z10.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 10.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 52/220
; update layer progress
M73 L52
M991 S0 P51 ;notify layer change
G17
G3 Z10.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z10.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z10.8 F30000
G1 Z10.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z10.8 F30000
G1 Z10.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 10.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 53/220
; update layer progress
M73 L53
M991 S0 P52 ;notify layer change
G17
G3 Z10.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z10.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z11 F30000
G1 Z10.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z11 F30000
G1 Z10.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 10.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 54/220
; update layer progress
M73 L54
M991 S0 P53 ;notify layer change
G17
G3 Z11 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z10.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z11.2 F30000
G1 Z10.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z11.2 F30000
G1 Z10.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
M73 P49 R13
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 55/220
; update layer progress
M73 L55
M991 S0 P54 ;notify layer change
G17
G3 Z11.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z11.4 F30000
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z11.4 F30000
G1 Z11
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 11.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 56/220
; update layer progress
M73 L56
M991 S0 P55 ;notify layer change
G17
G3 Z11.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z11.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z11.6 F30000
G1 Z11.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z11.6 F30000
G1 Z11.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 11.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 57/220
; update layer progress
M73 L57
M991 S0 P56 ;notify layer change
G17
G3 Z11.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z11.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z11.8 F30000
G1 Z11.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z11.8 F30000
G1 Z11.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 11.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
M73 P49 R12
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 58/220
; update layer progress
M73 L58
M991 S0 P57 ;notify layer change
G17
G3 Z11.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z11.6
M73 P50 R12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z12 F30000
G1 Z11.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z12 F30000
G1 Z11.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 11.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 59/220
; update layer progress
M73 L59
M991 S0 P58 ;notify layer change
G17
G3 Z12 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z11.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z12.2 F30000
G1 Z11.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z12.2 F30000
G1 Z11.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 12
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 60/220
; update layer progress
M73 L60
M991 S0 P59 ;notify layer change
G17
G3 Z12.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z12.4 F30000
G1 Z12
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z12.4 F30000
G1 Z12
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 12.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 61/220
; update layer progress
M73 L61
M991 S0 P60 ;notify layer change
G17
G3 Z12.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z12.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z12.6 F30000
G1 Z12.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z12.6 F30000
G1 Z12.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
M73 P51 R12
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 12.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 62/220
; update layer progress
M73 L62
M991 S0 P61 ;notify layer change
G17
G3 Z12.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z12.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z12.8 F30000
G1 Z12.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z12.8 F30000
G1 Z12.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 12.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 63/220
; update layer progress
M73 L63
M991 S0 P62 ;notify layer change
G17
G3 Z12.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z12.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z13 F30000
G1 Z12.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z13 F30000
G1 Z12.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 12.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 64/220
; update layer progress
M73 L64
M991 S0 P63 ;notify layer change
G17
G3 Z13 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z12.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z13.2 F30000
G1 Z12.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z13.2 F30000
G1 Z12.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 13
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
M73 P52 R12
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 65/220
; update layer progress
M73 L65
M991 S0 P64 ;notify layer change
G17
G3 Z13.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z13
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z13.4 F30000
G1 Z13
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z13.4 F30000
G1 Z13
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 13.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 66/220
; update layer progress
M73 L66
M991 S0 P65 ;notify layer change
G17
G3 Z13.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z13.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z13.6 F30000
G1 Z13.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z13.6 F30000
G1 Z13.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 13.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 67/220
; update layer progress
M73 L67
M991 S0 P66 ;notify layer change
G17
G3 Z13.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z13.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z13.8 F30000
G1 Z13.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z13.8 F30000
G1 Z13.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 13.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 68/220
; update layer progress
M73 L68
M991 S0 P67 ;notify layer change
G17
G3 Z13.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z13.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
M73 P53 R12
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z14 F30000
G1 Z13.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z14 F30000
G1 Z13.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 13.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 69/220
; update layer progress
M73 L69
M991 S0 P68 ;notify layer change
G17
G3 Z14 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z13.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z14.2 F30000
G1 Z13.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z14.2 F30000
G1 Z13.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 14
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 70/220
; update layer progress
M73 L70
M991 S0 P69 ;notify layer change
G17
G3 Z14.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z14
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z14.4 F30000
G1 Z14
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z14.4 F30000
G1 Z14
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 14.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 71/220
; update layer progress
M73 L71
M991 S0 P70 ;notify layer change
G17
G3 Z14.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z14.2
M73 P53 R11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z14.6 F30000
G1 Z14.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z14.6 F30000
G1 Z14.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
M73 P54 R11
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 14.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 72/220
; update layer progress
M73 L72
M991 S0 P71 ;notify layer change
G17
G3 Z14.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z14.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z14.8 F30000
G1 Z14.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z14.8 F30000
G1 Z14.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 14.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 73/220
; update layer progress
M73 L73
M991 S0 P72 ;notify layer change
G17
G3 Z14.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z14.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z15 F30000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z15 F30000
G1 Z14.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 14.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 74/220
; update layer progress
M73 L74
M991 S0 P73 ;notify layer change
G17
G3 Z15 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z14.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z15.2 F30000
G1 Z14.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z15.2 F30000
G1 Z14.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 15
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 75/220
; update layer progress
M73 L75
M991 S0 P74 ;notify layer change
G17
G3 Z15.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z15
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P55 R11
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z15.4 F30000
G1 Z15
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z15.4 F30000
G1 Z15
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 15.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 76/220
; update layer progress
M73 L76
M991 S0 P75 ;notify layer change
G17
G3 Z15.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z15.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z15.6 F30000
G1 Z15.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z15.6 F30000
G1 Z15.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 15.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 77/220
; update layer progress
M73 L77
M991 S0 P76 ;notify layer change
G17
G3 Z15.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z15.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z15.8 F30000
G1 Z15.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z15.8 F30000
G1 Z15.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 15.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 78/220
; update layer progress
M73 L78
M991 S0 P77 ;notify layer change
G17
G3 Z15.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z15.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z16 F30000
G1 Z15.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z16 F30000
G1 Z15.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
M73 P56 R11
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 15.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 79/220
; update layer progress
M73 L79
M991 S0 P78 ;notify layer change
G17
G3 Z16 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z15.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z16.2 F30000
G1 Z15.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z16.2 F30000
G1 Z15.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 16
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 80/220
; update layer progress
M73 L80
M991 S0 P79 ;notify layer change
G17
G3 Z16.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z16.4 F30000
G1 Z16
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z16.4 F30000
G1 Z16
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 16.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 81/220
; update layer progress
M73 L81
M991 S0 P80 ;notify layer change
G17
G3 Z16.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z16.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z16.6 F30000
G1 Z16.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z16.6 F30000
G1 Z16.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 16.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
M73 P57 R11
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 82/220
; update layer progress
M73 L82
M991 S0 P81 ;notify layer change
G17
G3 Z16.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z16.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z16.8 F30000
G1 Z16.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z16.8 F30000
G1 Z16.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 16.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 83/220
; update layer progress
M73 L83
M991 S0 P82 ;notify layer change
G17
G3 Z16.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z16.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z17 F30000
G1 Z16.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z17 F30000
G1 Z16.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 16.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 84/220
; update layer progress
M73 L84
M991 S0 P83 ;notify layer change
G17
G3 Z17 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z16.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
M73 P57 R10
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z17.2 F30000
G1 Z16.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z17.2 F30000
G1 Z16.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 17
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 85/220
; update layer progress
M73 L85
M991 S0 P84 ;notify layer change
G17
G3 Z17.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z17
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z17.4 F30000
G1 Z17
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
M73 P58 R10
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z17.4 F30000
G1 Z17
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 17.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 86/220
; update layer progress
M73 L86
M991 S0 P85 ;notify layer change
G17
G3 Z17.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z17.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z17.6 F30000
G1 Z17.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z17.6 F30000
G1 Z17.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 17.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 87/220
; update layer progress
M73 L87
M991 S0 P86 ;notify layer change
G17
G3 Z17.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z17.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z17.8 F30000
G1 Z17.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z17.8 F30000
G1 Z17.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 17.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 88/220
; update layer progress
M73 L88
M991 S0 P87 ;notify layer change
G17
G3 Z17.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z17.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z18 F30000
G1 Z17.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z18 F30000
G1 Z17.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
M73 P59 R10
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 17.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 89/220
; update layer progress
M73 L89
M991 S0 P88 ;notify layer change
G17
G3 Z18 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z17.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z18.2 F30000
G1 Z17.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z18.2 F30000
G1 Z17.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 18
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 90/220
; update layer progress
M73 L90
M991 S0 P89 ;notify layer change
G17
G3 Z18.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z18
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z18.4 F30000
G1 Z18
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z18.4 F30000
G1 Z18
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 18.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 91/220
; update layer progress
M73 L91
M991 S0 P90 ;notify layer change
G17
G3 Z18.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z18.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z18.6 F30000
G1 Z18.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z18.6 F30000
G1 Z18.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 18.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 92/220
; update layer progress
M73 L92
M991 S0 P91 ;notify layer change
G17
G3 Z18.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z18.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
M73 P60 R10
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z18.8 F30000
G1 Z18.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z18.8 F30000
G1 Z18.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 18.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 93/220
; update layer progress
M73 L93
M991 S0 P92 ;notify layer change
G17
G3 Z18.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z18.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z19 F30000
G1 Z18.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z19 F30000
G1 Z18.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 18.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 94/220
; update layer progress
M73 L94
M991 S0 P93 ;notify layer change
G17
G3 Z19 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z18.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z19.2 F30000
G1 Z18.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z19.2 F30000
G1 Z18.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 19
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 95/220
; update layer progress
M73 L95
M991 S0 P94 ;notify layer change
G17
G3 Z19.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z19
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z19.4 F30000
G1 Z19
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z19.4 F30000
G1 Z19
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
M73 P61 R10
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 19.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 96/220
; update layer progress
M73 L96
M991 S0 P95 ;notify layer change
G17
G3 Z19.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z19.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z19.6 F30000
G1 Z19.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z19.6 F30000
G1 Z19.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 19.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 97/220
; update layer progress
M73 L97
M991 S0 P96 ;notify layer change
G17
G3 Z19.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z19.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z19.8 F30000
M73 P61 R9
G1 Z19.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z19.8 F30000
G1 Z19.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 19.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 98/220
; update layer progress
M73 L98
M991 S0 P97 ;notify layer change
G17
G3 Z19.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z19.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z20 F30000
G1 Z19.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z20 F30000
G1 Z19.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 19.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 99/220
; update layer progress
M73 L99
M991 S0 P98 ;notify layer change
G17
M73 P62 R9
G3 Z20 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z19.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z20.2 F30000
G1 Z19.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z20.2 F30000
G1 Z19.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 20
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 100/220
; update layer progress
M73 L100
M991 S0 P99 ;notify layer change
G17
G3 Z20.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z20
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z20.4 F30000
G1 Z20
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z20.4 F30000
G1 Z20
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 20.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 101/220
; update layer progress
M73 L101
M991 S0 P100 ;notify layer change
G17
G3 Z20.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z20.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z20.6 F30000
G1 Z20.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z20.6 F30000
G1 Z20.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 20.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 102/220
; update layer progress
M73 L102
M991 S0 P101 ;notify layer change
G17
G3 Z20.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z20.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z20.8 F30000
G1 Z20.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
M73 P63 R9
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z20.8 F30000
G1 Z20.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 20.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 103/220
; update layer progress
M73 L103
M991 S0 P102 ;notify layer change
G17
G3 Z20.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z20.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z21 F30000
G1 Z20.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z21 F30000
G1 Z20.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 20.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 104/220
; update layer progress
M73 L104
M991 S0 P103 ;notify layer change
G17
G3 Z21 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z20.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z21.2 F30000
G1 Z20.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z21.2 F30000
G1 Z20.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 21
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 105/220
; update layer progress
M73 L105
M991 S0 P104 ;notify layer change
G17
G3 Z21.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z21
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z21.4 F30000
G1 Z21
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z21.4 F30000
G1 Z21
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
M73 P64 R9
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 21.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 106/220
; update layer progress
M73 L106
M991 S0 P105 ;notify layer change
G17
G3 Z21.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z21.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z21.6 F30000
G1 Z21.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z21.6 F30000
G1 Z21.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 21.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 107/220
; update layer progress
M73 L107
M991 S0 P106 ;notify layer change
G17
G3 Z21.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z21.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z21.8 F30000
G1 Z21.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z21.8 F30000
G1 Z21.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 21.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 108/220
; update layer progress
M73 L108
M991 S0 P107 ;notify layer change
G17
G3 Z21.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z21.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z22 F30000
G1 Z21.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z22 F30000
G1 Z21.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 21.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 109/220
; update layer progress
M73 L109
M991 S0 P108 ;notify layer change
G17
G3 Z22 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z21.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
M73 P65 R9
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z22.2 F30000
G1 Z21.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z22.2 F30000
G1 Z21.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 22
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 110/220
; update layer progress
M73 L110
M991 S0 P109 ;notify layer change
G17
G3 Z22.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z22
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z22.4 F30000
G1 Z22
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z22.4 F30000
G1 Z22
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
M73 P65 R8
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 22.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 111/220
; update layer progress
M73 L111
M991 S0 P110 ;notify layer change
G17
G3 Z22.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z22.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z22.6 F30000
G1 Z22.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z22.6 F30000
G1 Z22.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 22.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 112/220
; update layer progress
M73 L112
M991 S0 P111 ;notify layer change
G17
G3 Z22.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z22.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z22.8 F30000
G1 Z22.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z22.8 F30000
G1 Z22.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
M73 P66 R8
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 22.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 113/220
; update layer progress
M73 L113
M991 S0 P112 ;notify layer change
G17
G3 Z22.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z22.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z23 F30000
G1 Z22.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z23 F30000
G1 Z22.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 22.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 114/220
; update layer progress
M73 L114
M991 S0 P113 ;notify layer change
G17
G3 Z23 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z22.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z23.2 F30000
G1 Z22.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z23.2 F30000
G1 Z22.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 23
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 115/220
; update layer progress
M73 L115
M991 S0 P114 ;notify layer change
G17
G3 Z23.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z23
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z23.4 F30000
G1 Z23
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z23.4 F30000
G1 Z23
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 23.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 116/220
; update layer progress
M73 L116
M991 S0 P115 ;notify layer change
G17
G3 Z23.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z23.2
M73 P67 R8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z23.6 F30000
G1 Z23.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z23.6 F30000
G1 Z23.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 23.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 117/220
; update layer progress
M73 L117
M991 S0 P116 ;notify layer change
G17
G3 Z23.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z23.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z23.8 F30000
G1 Z23.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z23.8 F30000
G1 Z23.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 23.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 118/220
; update layer progress
M73 L118
M991 S0 P117 ;notify layer change
G17
G3 Z23.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z23.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z24 F30000
G1 Z23.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z24 F30000
G1 Z23.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 23.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 119/220
; update layer progress
M73 L119
M991 S0 P118 ;notify layer change
G17
G3 Z24 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z23.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z24.2 F30000
G1 Z23.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z24.2 F30000
M73 P68 R8
G1 Z23.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 24
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 120/220
; update layer progress
M73 L120
M991 S0 P119 ;notify layer change
G17
G3 Z24.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z24.4 F30000
G1 Z24
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z24.4 F30000
G1 Z24
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 24.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 121/220
; update layer progress
M73 L121
M991 S0 P120 ;notify layer change
G17
G3 Z24.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z24.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z24.6 F30000
G1 Z24.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z24.6 F30000
G1 Z24.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 24.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 122/220
; update layer progress
M73 L122
M991 S0 P121 ;notify layer change
G17
G3 Z24.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z24.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z24.8 F30000
G1 Z24.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z24.8 F30000
G1 Z24.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 24.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
M73 P69 R8
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 123/220
; update layer progress
M73 L123
M991 S0 P122 ;notify layer change
G17
G3 Z24.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z24.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z25 F30000
G1 Z24.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z25 F30000
G1 Z24.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
M73 P69 R7
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 24.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 124/220
; update layer progress
M73 L124
M991 S0 P123 ;notify layer change
G17
G3 Z25 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z24.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z25.2 F30000
G1 Z24.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z25.2 F30000
G1 Z24.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 25
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 125/220
; update layer progress
M73 L125
M991 S0 P124 ;notify layer change
G17
G3 Z25.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z25
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z25.4 F30000
G1 Z25
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z25.4 F30000
G1 Z25
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 25.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 126/220
; update layer progress
M73 L126
M991 S0 P125 ;notify layer change
G17
G3 Z25.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z25.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
M73 P70 R7
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z25.6 F30000
G1 Z25.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z25.6 F30000
G1 Z25.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 25.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 127/220
; update layer progress
M73 L127
M991 S0 P126 ;notify layer change
G17
G3 Z25.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z25.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z25.8 F30000
G1 Z25.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z25.8 F30000
G1 Z25.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 25.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 128/220
; update layer progress
M73 L128
M991 S0 P127 ;notify layer change
G17
G3 Z25.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z25.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z26 F30000
G1 Z25.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z26 F30000
G1 Z25.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 25.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 129/220
; update layer progress
M73 L129
M991 S0 P128 ;notify layer change
G17
G3 Z26 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z25.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z26.2 F30000
G1 Z25.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z26.2 F30000
G1 Z25.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
M73 P71 R7
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 26
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 130/220
; update layer progress
M73 L130
M991 S0 P129 ;notify layer change
G17
G3 Z26.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z26
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z26.4 F30000
G1 Z26
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z26.4 F30000
G1 Z26
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 26.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 131/220
; update layer progress
M73 L131
M991 S0 P130 ;notify layer change
G17
G3 Z26.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z26.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z26.6 F30000
G1 Z26.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z26.6 F30000
G1 Z26.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 26.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 132/220
; update layer progress
M73 L132
M991 S0 P131 ;notify layer change
G17
G3 Z26.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z26.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z26.8 F30000
G1 Z26.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z26.8 F30000
G1 Z26.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 26.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 133/220
; update layer progress
M73 L133
M991 S0 P132 ;notify layer change
G17
G3 Z26.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z26.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P72 R7
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z27 F30000
G1 Z26.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z27 F30000
G1 Z26.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 26.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 134/220
; update layer progress
M73 L134
M991 S0 P133 ;notify layer change
G17
G3 Z27 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z26.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z27.2 F30000
G1 Z26.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z27.2 F30000
G1 Z26.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 27
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 135/220
; update layer progress
M73 L135
M991 S0 P134 ;notify layer change
G17
G3 Z27.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z27
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z27.4 F30000
G1 Z27
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z27.4 F30000
G1 Z27
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 27.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 136/220
; update layer progress
M73 L136
M991 S0 P135 ;notify layer change
G17
G3 Z27.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z27.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z27.6 F30000
G1 Z27.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z27.6 F30000
G1 Z27.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
M73 P73 R7
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
M73 P73 R6
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 27.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 137/220
; update layer progress
M73 L137
M991 S0 P136 ;notify layer change
G17
G3 Z27.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z27.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z27.8 F30000
G1 Z27.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z27.8 F30000
G1 Z27.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 27.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 138/220
; update layer progress
M73 L138
M991 S0 P137 ;notify layer change
G17
G3 Z27.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z27.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z28 F30000
G1 Z27.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z28 F30000
G1 Z27.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 27.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 139/220
; update layer progress
M73 L139
M991 S0 P138 ;notify layer change
G17
G3 Z28 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z27.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z28.2 F30000
G1 Z27.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z28.2 F30000
G1 Z27.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 28
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
M73 P74 R6
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 140/220
; update layer progress
M73 L140
M991 S0 P139 ;notify layer change
G17
G3 Z28.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z28.4 F30000
G1 Z28
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z28.4 F30000
G1 Z28
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 28.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 141/220
; update layer progress
M73 L141
M991 S0 P140 ;notify layer change
G17
G3 Z28.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z28.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z28.6 F30000
G1 Z28.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z28.6 F30000
G1 Z28.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 28.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 142/220
; update layer progress
M73 L142
M991 S0 P141 ;notify layer change
G17
G3 Z28.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z28.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z28.8 F30000
G1 Z28.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z28.8 F30000
G1 Z28.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 28.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 143/220
; update layer progress
M73 L143
M991 S0 P142 ;notify layer change
G17
G3 Z28.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z28.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z29 F30000
M73 P75 R6
G1 Z28.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z29 F30000
G1 Z28.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 28.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 144/220
; update layer progress
M73 L144
M991 S0 P143 ;notify layer change
G17
G3 Z29 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z28.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z29.2 F30000
G1 Z28.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z29.2 F30000
G1 Z28.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 29
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 145/220
; update layer progress
M73 L145
M991 S0 P144 ;notify layer change
G17
G3 Z29.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z29
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z29.4 F30000
G1 Z29
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z29.4 F30000
G1 Z29
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 29.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 146/220
; update layer progress
M73 L146
M991 S0 P145 ;notify layer change
G17
G3 Z29.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z29.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z29.6 F30000
G1 Z29.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z29.6 F30000
G1 Z29.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
M73 P76 R6
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 29.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 147/220
; update layer progress
M73 L147
M991 S0 P146 ;notify layer change
G17
G3 Z29.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z29.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z29.8 F30000
G1 Z29.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z29.8 F30000
G1 Z29.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 29.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 148/220
; update layer progress
M73 L148
M991 S0 P147 ;notify layer change
G17
G3 Z29.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z29.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z30 F30000
G1 Z29.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z30 F30000
G1 Z29.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 29.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 149/220
; update layer progress
M73 L149
M991 S0 P148 ;notify layer change
G17
G3 Z30 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z29.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z30.2 F30000
G1 Z29.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z30.2 F30000
G1 Z29.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 30
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
M73 P76 R5
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 150/220
; update layer progress
M73 L150
M991 S0 P149 ;notify layer change
G17
G3 Z30.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z30
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
M73 P77 R5
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z30.4 F30000
G1 Z30
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z30.4 F30000
G1 Z30
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 30.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 151/220
; update layer progress
M73 L151
M991 S0 P150 ;notify layer change
G17
G3 Z30.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z30.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z30.6 F30000
G1 Z30.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z30.6 F30000
G1 Z30.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 30.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 152/220
; update layer progress
M73 L152
M991 S0 P151 ;notify layer change
G17
G3 Z30.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z30.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z30.8 F30000
G1 Z30.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z30.8 F30000
G1 Z30.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 30.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 153/220
; update layer progress
M73 L153
M991 S0 P152 ;notify layer change
G17
G3 Z30.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z30.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z31 F30000
G1 Z30.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z31 F30000
G1 Z30.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
M73 P78 R5
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 30.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 154/220
; update layer progress
M73 L154
M991 S0 P153 ;notify layer change
G17
G3 Z31 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z30.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z31.2 F30000
G1 Z30.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z31.2 F30000
G1 Z30.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 31
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 155/220
; update layer progress
M73 L155
M991 S0 P154 ;notify layer change
G17
G3 Z31.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z31
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z31.4 F30000
G1 Z31
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z31.4 F30000
G1 Z31
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 31.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 156/220
; update layer progress
M73 L156
M991 S0 P155 ;notify layer change
G17
G3 Z31.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z31.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z31.6 F30000
G1 Z31.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z31.6 F30000
G1 Z31.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 31.4
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
M73 P79 R5
G1 E-.04 F1800
; layer num/total_layer_count: 157/220
; update layer progress
M73 L157
M991 S0 P156 ;notify layer change
G17
G3 Z31.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z31.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z31.8 F30000
G1 Z31.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z31.8 F30000
G1 Z31.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 31.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 158/220
; update layer progress
M73 L158
M991 S0 P157 ;notify layer change
G17
G3 Z31.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z31.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z32 F30000
G1 Z31.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z32 F30000
G1 Z31.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 31.8
; LAYER_HEIGHT: 0.199999
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 159/220
; update layer progress
M73 L159
M991 S0 P158 ;notify layer change
G17
G3 Z32 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z31.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z32.2 F30000
G1 Z31.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z32.2 F30000
G1 Z31.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 32
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 160/220
; update layer progress
M73 L160
M991 S0 P159 ;notify layer change
G17
G3 Z32.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z32.4 F30000
G1 Z32
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
M73 P80 R5
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z32.4 F30000
G1 Z32
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 32.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 161/220
; update layer progress
M73 L161
M991 S0 P160 ;notify layer change
G17
G3 Z32.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z32.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z32.6 F30000
G1 Z32.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z32.6 F30000
G1 Z32.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 32.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 162/220
; update layer progress
M73 L162
M991 S0 P161 ;notify layer change
G17
G3 Z32.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z32.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z32.8 F30000
G1 Z32.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z32.8 F30000
G1 Z32.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 32.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 163/220
; update layer progress
M73 L163
M991 S0 P162 ;notify layer change
G17
M73 P80 R4
G3 Z32.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z32.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z33 F30000
G1 Z32.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z33 F30000
G1 Z32.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
M73 P81 R4
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 32.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 164/220
; update layer progress
M73 L164
M991 S0 P163 ;notify layer change
G17
G3 Z33 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z32.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z33.2 F30000
G1 Z32.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z33.2 F30000
G1 Z32.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 33
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 165/220
; update layer progress
M73 L165
M991 S0 P164 ;notify layer change
G17
G3 Z33.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z33
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z33.4 F30000
G1 Z33
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z33.4 F30000
G1 Z33
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 33.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 166/220
; update layer progress
M73 L166
M991 S0 P165 ;notify layer change
G17
G3 Z33.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z33.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z33.6 F30000
G1 Z33.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z33.6 F30000
G1 Z33.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 33.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 167/220
; update layer progress
M73 L167
M991 S0 P166 ;notify layer change
G17
G3 Z33.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z33.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
M73 P82 R4
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z33.8 F30000
G1 Z33.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z33.8 F30000
G1 Z33.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 33.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 168/220
; update layer progress
M73 L168
M991 S0 P167 ;notify layer change
G17
G3 Z33.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z33.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z34 F30000
G1 Z33.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z34 F30000
G1 Z33.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 33.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 169/220
; update layer progress
M73 L169
M991 S0 P168 ;notify layer change
G17
G3 Z34 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z33.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z34.2 F30000
G1 Z33.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z34.2 F30000
G1 Z33.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 34
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 170/220
; update layer progress
M73 L170
M991 S0 P169 ;notify layer change
G17
G3 Z34.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z34
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z34.4 F30000
G1 Z34
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z34.4 F30000
G1 Z34
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
M73 P83 R4
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 34.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 171/220
; update layer progress
M73 L171
M991 S0 P170 ;notify layer change
G17
G3 Z34.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z34.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z34.6 F30000
G1 Z34.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z34.6 F30000
G1 Z34.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 34.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 172/220
; update layer progress
M73 L172
M991 S0 P171 ;notify layer change
G17
G3 Z34.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z34.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z34.8 F30000
G1 Z34.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z34.8 F30000
G1 Z34.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 34.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 173/220
; update layer progress
M73 L173
M991 S0 P172 ;notify layer change
G17
G3 Z34.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z34.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z35 F30000
G1 Z34.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z35 F30000
G1 Z34.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 34.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 174/220
; update layer progress
M73 L174
M991 S0 P173 ;notify layer change
G17
M73 P84 R4
G3 Z35 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z34.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z35.2 F30000
G1 Z34.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z35.2 F30000
G1 Z34.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 35
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 175/220
; update layer progress
M73 L175
M991 S0 P174 ;notify layer change
G17
G3 Z35.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z35
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z35.4 F30000
G1 Z35
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z35.4 F30000
G1 Z35
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 35.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 176/220
; update layer progress
M73 L176
M991 S0 P175 ;notify layer change
G17
G3 Z35.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z35.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
M73 P84 R3
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z35.6 F30000
G1 Z35.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z35.6 F30000
G1 Z35.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 35.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 177/220
; update layer progress
M73 L177
M991 S0 P176 ;notify layer change
G17
G3 Z35.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z35.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z35.8 F30000
G1 Z35.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
M73 P85 R3
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z35.8 F30000
G1 Z35.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 35.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 178/220
; update layer progress
M73 L178
M991 S0 P177 ;notify layer change
G17
G3 Z35.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z35.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z36 F30000
G1 Z35.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z36 F30000
G1 Z35.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 35.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 179/220
; update layer progress
M73 L179
M991 S0 P178 ;notify layer change
G17
G3 Z36 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z35.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z36.2 F30000
G1 Z35.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z36.2 F30000
G1 Z35.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 36
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 180/220
; update layer progress
M73 L180
M991 S0 P179 ;notify layer change
G17
G3 Z36.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z36.4 F30000
G1 Z36
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z36.4 F30000
G1 Z36
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 36.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
M73 P86 R3
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 181/220
; update layer progress
M73 L181
M991 S0 P180 ;notify layer change
G17
G3 Z36.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z36.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z36.6 F30000
G1 Z36.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z36.6 F30000
G1 Z36.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 36.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 182/220
; update layer progress
M73 L182
M991 S0 P181 ;notify layer change
G17
G3 Z36.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z36.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z36.8 F30000
G1 Z36.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z36.8 F30000
G1 Z36.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 36.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 183/220
; update layer progress
M73 L183
M991 S0 P182 ;notify layer change
G17
G3 Z36.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z36.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z37 F30000
G1 Z36.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z37 F30000
G1 Z36.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 36.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 184/220
; update layer progress
M73 L184
M991 S0 P183 ;notify layer change
G17
G3 Z37 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z36.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
M73 P87 R3
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z37.2 F30000
G1 Z36.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z37.2 F30000
G1 Z36.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 37
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 185/220
; update layer progress
M73 L185
M991 S0 P184 ;notify layer change
G17
G3 Z37.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z37
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z37.4 F30000
G1 Z37
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z37.4 F30000
G1 Z37
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 37.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 186/220
; update layer progress
M73 L186
M991 S0 P185 ;notify layer change
G17
G3 Z37.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z37.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z37.6 F30000
G1 Z37.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z37.6 F30000
G1 Z37.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 37.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 187/220
; update layer progress
M73 L187
M991 S0 P186 ;notify layer change
G17
G3 Z37.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z37.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z37.8 F30000
G1 Z37.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z37.8 F30000
G1 Z37.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
M73 P88 R3
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 37.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 188/220
; update layer progress
M73 L188
M991 S0 P187 ;notify layer change
G17
G3 Z37.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z37.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z38 F30000
G1 Z37.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z38 F30000
G1 Z37.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 37.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 189/220
; update layer progress
M73 L189
M991 S0 P188 ;notify layer change
G17
G3 Z38 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z37.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
M73 P88 R2
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z38.2 F30000
G1 Z37.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z38.2 F30000
G1 Z37.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 38
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 190/220
; update layer progress
M73 L190
M991 S0 P189 ;notify layer change
G17
G3 Z38.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z38
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z38.4 F30000
G1 Z38
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z38.4 F30000
G1 Z38
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 38.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 191/220
; update layer progress
M73 L191
M991 S0 P190 ;notify layer change
G17
G3 Z38.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z38.2
M73 P89 R2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z38.6 F30000
G1 Z38.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z38.6 F30000
G1 Z38.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 38.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 192/220
; update layer progress
M73 L192
M991 S0 P191 ;notify layer change
G17
G3 Z38.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z38.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z38.8 F30000
G1 Z38.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z38.8 F30000
G1 Z38.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 38.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 193/220
; update layer progress
M73 L193
M991 S0 P192 ;notify layer change
G17
G3 Z38.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z38.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z39 F30000
G1 Z38.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z39 F30000
G1 Z38.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 38.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 194/220
; update layer progress
M73 L194
M991 S0 P193 ;notify layer change
G17
G3 Z39 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z38.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z39.2 F30000
G1 Z38.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z39.2 F30000
G1 Z38.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
M73 P90 R2
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 39
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 195/220
; update layer progress
M73 L195
M991 S0 P194 ;notify layer change
G17
G3 Z39.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z39
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z39.4 F30000
G1 Z39
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z39.4 F30000
G1 Z39
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 39.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 196/220
; update layer progress
M73 L196
M991 S0 P195 ;notify layer change
G17
G3 Z39.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z39.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z39.6 F30000
G1 Z39.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z39.6 F30000
G1 Z39.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 39.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 197/220
; update layer progress
M73 L197
M991 S0 P196 ;notify layer change
G17
G3 Z39.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z39.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z39.8 F30000
G1 Z39.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z39.8 F30000
G1 Z39.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 39.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
M73 P91 R2
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 198/220
; update layer progress
M73 L198
M991 S0 P197 ;notify layer change
G17
G3 Z39.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z39.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z40 F30000
G1 Z39.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z40 F30000
G1 Z39.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 39.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 199/220
; update layer progress
M73 L199
M991 S0 P198 ;notify layer change
G17
G3 Z40 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z39.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z40.2 F30000
G1 Z39.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z40.2 F30000
G1 Z39.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 40
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 200/220
; update layer progress
M73 L200
M991 S0 P199 ;notify layer change
G17
G3 Z40.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z40
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z40.4 F30000
G1 Z40
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z40.4 F30000
G1 Z40
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 40.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 201/220
; update layer progress
M73 L201
M991 S0 P200 ;notify layer change
G17
G3 Z40.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z40.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z40.6 F30000
M73 P92 R2
G1 Z40.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z40.6 F30000
G1 Z40.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 40.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 202/220
; update layer progress
M73 L202
M991 S0 P201 ;notify layer change
G17
G3 Z40.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z40.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z40.8 F30000
G1 Z40.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
M73 P92 R1
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z40.8 F30000
G1 Z40.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 40.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 203/220
; update layer progress
M73 L203
M991 S0 P202 ;notify layer change
G17
G3 Z40.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z40.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z41 F30000
G1 Z40.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z41 F30000
G1 Z40.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 40.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 204/220
; update layer progress
M73 L204
M991 S0 P203 ;notify layer change
G17
G3 Z41 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z40.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z41.2 F30000
G1 Z40.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z41.2 F30000
G1 Z40.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
M73 P93 R1
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 41
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 205/220
; update layer progress
M73 L205
M991 S0 P204 ;notify layer change
G17
G3 Z41.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z41
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z41.4 F30000
G1 Z41
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z41.4 F30000
G1 Z41
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 41.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 206/220
; update layer progress
M73 L206
M991 S0 P205 ;notify layer change
G17
G3 Z41.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z41.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z41.6 F30000
G1 Z41.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z41.6 F30000
G1 Z41.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 41.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 207/220
; update layer progress
M73 L207
M991 S0 P206 ;notify layer change
G17
G3 Z41.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z41.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z41.8 F30000
G1 Z41.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z41.8 F30000
G1 Z41.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 41.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 208/220
; update layer progress
M73 L208
M991 S0 P207 ;notify layer change
G17
G3 Z41.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z41.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
M73 P94 R1
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z42 F30000
G1 Z41.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z42 F30000
G1 Z41.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 41.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 209/220
; update layer progress
M73 L209
M991 S0 P208 ;notify layer change
G17
G3 Z42 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z41.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z42.2 F30000
G1 Z41.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z42.2 F30000
G1 Z41.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 42
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 210/220
; update layer progress
M73 L210
M991 S0 P209 ;notify layer change
G17
G3 Z42.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z42
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z42.4 F30000
G1 Z42
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z42.4 F30000
G1 Z42
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 42.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 211/220
; update layer progress
M73 L211
M991 S0 P210 ;notify layer change
G17
G3 Z42.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z42.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z42.6 F30000
G1 Z42.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z42.6 F30000
G1 Z42.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
M73 P95 R1
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 42.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 212/220
; update layer progress
M73 L212
M991 S0 P211 ;notify layer change
G17
G3 Z42.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z42.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z42.8 F30000
G1 Z42.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z42.8 F30000
G1 Z42.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 42.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 213/220
; update layer progress
M73 L213
M991 S0 P212 ;notify layer change
G17
G3 Z42.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z42.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z43 F30000
G1 Z42.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z43 F30000
G1 Z42.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 42.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 214/220
; update layer progress
M73 L214
M991 S0 P213 ;notify layer change
G17
G3 Z43 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z42.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z43.2 F30000
G1 Z42.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z43.2 F30000
G1 Z42.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 43
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
M73 P96 R1
G1 E-.04 F1800
; layer num/total_layer_count: 215/220
; update layer progress
M73 L215
M991 S0 P214 ;notify layer change
G17
G3 Z43.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z43
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z43.4 F30000
G1 Z43
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z43.4 F30000
G1 Z43
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
M73 P96 R0
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 43.2
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 216/220
; update layer progress
M73 L216
M991 S0 P215 ;notify layer change
G17
G3 Z43.4 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z43.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z43.6 F30000
G1 Z43.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z43.6 F30000
G1 Z43.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 43.4
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 217/220
; update layer progress
M73 L217
M991 S0 P216 ;notify layer change
G17
G3 Z43.6 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z43.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z43.8 F30000
G1 Z43.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z43.8 F30000
G1 Z43.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 43.6
; LAYER_HEIGHT: 0.199997
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 218/220
; update layer progress
M73 L218
M991 S0 P217 ;notify layer change
G17
G3 Z43.8 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z43.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z44 F30000
G1 Z43.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
M73 P97 R0
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z44 F30000
G1 Z43.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 43.8
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 219/220
; update layer progress
M73 L219
M991 S0 P218 ;notify layer change
G17
G3 Z44 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.602 Y26.21
G1 Z43.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X42.602 Y26.602 E.01301
G1 X21.398 Y26.602 E.70338
G1 X21.398 Y5.398 E.70338
G1 X42.602 Y5.398 E.70338
G1 X42.602 Y26.15 E.68838
G1 X42.21 Y26.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.398 Y27.398 Z44.2 F30000
G1 Z43.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6937
G1 X20.602 Y27.398 E.75618
G1 X20.602 Y4.602 E.75618
G1 X43.398 Y4.602 E.75618
G1 X43.398 Y27.338 E.75419
G1 X43.79 Y27.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6937
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
; WIPE_START
G1 F12000
M204 S10000
G1 X41.79 Y27.735 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.967 Y26.967 Z44.2 F30000
G1 Z43.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.470635
G1 F6937
G1 X42.886 Y26.983 E.00287
; LINE_WIDTH: 0.448395
G1 X42.806 Y27 E.00272
; LINE_WIDTH: 0.43172
G1 X21.194 Y27 E.68469
; LINE_WIDTH: 0.470635
G1 X21.033 Y26.967 E.00573
G1 X21.017 Y26.886 E.00287
; LINE_WIDTH: 0.448395
G1 X21 Y26.806 E.00272
; LINE_WIDTH: 0.431784
G1 X21 Y5.194 E.6848
G1 X21.017 Y5.114 E.00261
; LINE_WIDTH: 0.481759
G1 X21.033 Y5.033 E.00294
; LINE_WIDTH: 0.481745
G1 X21.114 Y5.017 E.00294
; LINE_WIDTH: 0.448395
G1 X21.194 Y5 E.00272
; LINE_WIDTH: 0.43172
G1 X42.806 Y5 E.68469
; LINE_WIDTH: 0.470635
G1 X42.967 Y5.033 E.00573
G1 X42.983 Y5.114 E.00287
; LINE_WIDTH: 0.448395
G1 X43 Y5.194 E.00272
; LINE_WIDTH: 0.43172
G1 X43 Y26.806 E.68469
; LINE_WIDTH: 0.470635
G1 X42.979 Y26.908 E.00364
; CHANGE_LAYER
; Z_HEIGHT: 44
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F14729.449
G1 X42.886 Y26.983 E-.04541
G1 X42.806 Y27 E-.03125
G1 X41.007 Y27 E-.68334
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 220/220
; update layer progress
M73 L220
M991 S0 P219 ;notify layer change
G17
G3 Z44.2 I1.217 J0 P1  F30000
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

; OBJECT_ID: 8
G1 X42.21 Y26.21
G1 Z44
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8835
M204 S5000
G1 X21.79 Y26.21 E.62745
G1 X21.79 Y5.79 E.62745
G1 X42.21 Y5.79 E.62745
G1 X42.21 Y26.15 E.62561
; WIPE_START
G1 F12000
M204 S10000
G1 X40.21 Y26.156 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X43.79 Y27.79 Z44.4 F30000
G1 Z44
G1 E.8 F1800
G1 F8835
M204 S5000
G1 X20.21 Y27.79 E.72455
G1 X20.21 Y4.21 E.72455
G1 X43.79 Y4.21 E.72455
G1 X43.79 Y27.73 E.7227
M204 S10000
G1 X43.583 Y27.081 F30000
; FEATURE: Top surface
G1 F8835
M204 S2000
G1 X43.081 Y27.583 E.02181
G1 X42.547 Y27.583
G1 X43.583 Y26.547 E.04498
G1 X43.583 Y26.014
G1 X42.014 Y27.583 E.06815
G1 X41.481 Y27.583
G1 X43.583 Y25.481 E.09133
G1 X43.583 Y24.948
G1 X42.417 Y26.113 E.05064
G1 X42.417 Y25.58
G1 X43.583 Y24.414 E.05064
G1 X43.583 Y23.881
G1 X42.417 Y25.046 E.05064
G1 X42.417 Y24.513
G1 X43.583 Y23.348 E.05064
G1 X43.583 Y22.815
G1 X42.417 Y23.98 E.05064
G1 X42.417 Y23.447
G1 X43.583 Y22.281 E.05064
G1 X43.583 Y21.748
G1 X42.417 Y22.913 E.05064
G1 X42.417 Y22.38
G1 X43.583 Y21.215 E.05064
G1 X43.583 Y20.682
G1 X42.417 Y21.847 E.05064
G1 X42.417 Y21.314
G1 X43.583 Y20.148 E.05064
G1 X43.583 Y19.615
G1 X42.417 Y20.78 E.05064
G1 X42.417 Y20.247
G1 X43.583 Y19.082 E.05064
G1 X43.583 Y18.549
G1 X42.417 Y19.714 E.05064
G1 X42.417 Y19.181
G1 X43.583 Y18.015 E.05064
G1 X43.583 Y17.482
G1 X42.417 Y18.647 E.05064
G1 X42.417 Y18.114
G1 X43.583 Y16.949 E.05064
G1 X43.583 Y16.416
G1 X42.417 Y17.581 E.05064
G1 X42.417 Y17.048
G1 X43.583 Y15.882 E.05064
G1 X43.583 Y15.349
G1 X42.417 Y16.514 E.05064
G1 X42.417 Y15.981
G1 X43.583 Y14.816 E.05064
G1 X43.583 Y14.283
G1 X42.417 Y15.448 E.05064
G1 X42.417 Y14.915
G1 X43.583 Y13.749 E.05064
G1 X43.583 Y13.216
G1 X42.417 Y14.381 E.05064
G1 X42.417 Y13.848
G1 X43.583 Y12.683 E.05064
G1 X43.583 Y12.15
G1 X42.417 Y13.315 E.05064
G1 X42.417 Y12.782
G1 X43.583 Y11.616 E.05064
G1 X43.583 Y11.083
G1 X42.417 Y12.248 E.05064
G1 X42.417 Y11.715
G1 X43.583 Y10.55 E.05064
G1 X43.583 Y10.017
G1 X42.417 Y11.182 E.05064
G1 X42.417 Y10.648
G1 X43.583 Y9.483 E.05064
G1 X43.583 Y8.95
G1 X42.417 Y10.115 E.05064
G1 X42.417 Y9.582
G1 X43.583 Y8.417 E.05064
G1 X43.583 Y7.883
G1 X42.417 Y9.049 E.05064
G1 X42.417 Y8.515
G1 X43.583 Y7.35 E.05064
G1 X43.583 Y6.817
G1 X42.417 Y7.982 E.05064
G1 X42.417 Y7.449
G1 X43.583 Y6.284 E.05064
G1 X43.583 Y5.75
G1 X42.417 Y6.916 E.05064
G1 X42.417 Y6.382
G1 X43.583 Y5.217 E.05064
G1 X43.583 Y4.684
G1 X42.417 Y5.849 E.05064
G1 X42.151 Y5.583
G1 X43.316 Y4.417 E.05064
G1 X42.783 Y4.417
G1 X41.617 Y5.583 E.05064
G1 X41.084 Y5.583
G1 X42.249 Y4.417 E.05064
G1 X41.716 Y4.417
G1 X40.551 Y5.583 E.05064
G1 X40.018 Y5.583
G1 X41.183 Y4.417 E.05064
M73 P98 R0
G1 X40.65 Y4.417
G1 X39.484 Y5.583 E.05064
G1 X38.951 Y5.583
G1 X40.116 Y4.417 E.05064
G1 X39.583 Y4.417
G1 X38.418 Y5.583 E.05064
G1 X37.885 Y5.583
G1 X39.05 Y4.417 E.05064
G1 X38.517 Y4.417
G1 X37.351 Y5.583 E.05064
G1 X36.818 Y5.583
G1 X37.983 Y4.417 E.05064
G1 X37.45 Y4.417
G1 X36.285 Y5.583 E.05064
G1 X35.752 Y5.583
G1 X36.917 Y4.417 E.05064
G1 X36.384 Y4.417
G1 X35.218 Y5.583 E.05064
G1 X34.685 Y5.583
G1 X35.85 Y4.417 E.05064
G1 X35.317 Y4.417
G1 X34.152 Y5.583 E.05064
G1 X33.619 Y5.583
G1 X34.784 Y4.417 E.05064
G1 X34.251 Y4.417
G1 X33.085 Y5.583 E.05064
G1 X32.552 Y5.583
G1 X33.717 Y4.417 E.05064
G1 X33.184 Y4.417
G1 X32.019 Y5.583 E.05064
G1 X31.486 Y5.583
G1 X32.651 Y4.417 E.05064
G1 X32.118 Y4.417
G1 X30.952 Y5.583 E.05064
G1 X30.419 Y5.583
G1 X31.584 Y4.417 E.05064
G1 X31.051 Y4.417
G1 X29.886 Y5.583 E.05064
G1 X29.353 Y5.583
G1 X30.518 Y4.417 E.05064
G1 X29.984 Y4.417
G1 X28.819 Y5.583 E.05064
G1 X28.286 Y5.583
G1 X29.451 Y4.417 E.05064
G1 X28.918 Y4.417
G1 X27.753 Y5.583 E.05064
G1 X27.219 Y5.583
G1 X28.385 Y4.417 E.05064
G1 X27.851 Y4.417
G1 X26.686 Y5.583 E.05064
G1 X26.153 Y5.583
G1 X27.318 Y4.417 E.05064
G1 X26.785 Y4.417
G1 X25.62 Y5.583 E.05064
G1 X25.086 Y5.583
G1 X26.252 Y4.417 E.05064
G1 X25.718 Y4.417
G1 X24.553 Y5.583 E.05064
G1 X24.02 Y5.583
G1 X25.185 Y4.417 E.05064
G1 X24.652 Y4.417
G1 X23.487 Y5.583 E.05064
G1 X22.953 Y5.583
G1 X24.119 Y4.417 E.05064
G1 X23.585 Y4.417
G1 X22.42 Y5.583 E.05064
G1 X21.887 Y5.583
G1 X23.052 Y4.417 E.05064
; WIPE_START
G1 F12000
M204 S10000
G1 X21.887 Y5.583 E-.62621
G1 X22.239 Y5.583 E-.13379
; WIPE_END
G1 E-.04 F1800
G1 X27.507 Y11.105 Z44.4 F30000
G1 X42.113 Y26.417 Z44.4
G1 Z44
G1 E.8 F1800
G1 F8835
M204 S2000
G1 X40.948 Y27.583 E.05064
G1 X40.414 Y27.583
G1 X41.58 Y26.417 E.05064
G1 X41.046 Y26.417
G1 X39.881 Y27.583 E.05064
G1 X39.348 Y27.583
G1 X40.513 Y26.417 E.05064
G1 X39.98 Y26.417
G1 X38.815 Y27.583 E.05064
G1 X38.281 Y27.583
G1 X39.447 Y26.417 E.05064
G1 X38.913 Y26.417
G1 X37.748 Y27.583 E.05064
G1 X37.215 Y27.583
G1 X38.38 Y26.417 E.05064
G1 X37.847 Y26.417
G1 X36.682 Y27.583 E.05064
G1 X36.148 Y27.583
G1 X37.314 Y26.417 E.05064
G1 X36.78 Y26.417
G1 X35.615 Y27.583 E.05064
G1 X35.082 Y27.583
G1 X36.247 Y26.417 E.05064
G1 X35.714 Y26.417
G1 X34.549 Y27.583 E.05064
G1 X34.015 Y27.583
G1 X35.181 Y26.417 E.05064
G1 X34.647 Y26.417
G1 X33.482 Y27.583 E.05064
G1 X32.949 Y27.583
G1 X34.114 Y26.417 E.05064
G1 X33.581 Y26.417
G1 X32.416 Y27.583 E.05064
G1 X31.882 Y27.583
G1 X33.048 Y26.417 E.05064
G1 X32.514 Y26.417
G1 X31.349 Y27.583 E.05064
G1 X30.816 Y27.583
G1 X31.981 Y26.417 E.05064
G1 X31.448 Y26.417
G1 X30.283 Y27.583 E.05064
G1 X29.749 Y27.583
G1 X30.915 Y26.417 E.05064
G1 X30.381 Y26.417
G1 X29.216 Y27.583 E.05064
G1 X28.683 Y27.583
G1 X29.848 Y26.417 E.05064
G1 X29.315 Y26.417
G1 X28.15 Y27.583 E.05064
G1 X27.616 Y27.583
G1 X28.782 Y26.417 E.05064
G1 X28.248 Y26.417
G1 X27.083 Y27.583 E.05064
G1 X26.55 Y27.583
G1 X27.715 Y26.417 E.05064
G1 X27.182 Y26.417
G1 X26.017 Y27.583 E.05064
G1 X25.483 Y27.583
G1 X26.648 Y26.417 E.05064
G1 X26.115 Y26.417
G1 X24.95 Y27.583 E.05064
G1 X24.417 Y27.583
G1 X25.582 Y26.417 E.05064
G1 X25.049 Y26.417
G1 X23.883 Y27.583 E.05064
G1 X23.35 Y27.583
G1 X24.515 Y26.417 E.05064
G1 X23.982 Y26.417
G1 X22.817 Y27.583 E.05064
G1 X22.284 Y27.583
G1 X23.449 Y26.417 E.05064
G1 X22.916 Y26.417
G1 X21.75 Y27.583 E.05064
G1 X21.217 Y27.583
G1 X22.382 Y26.417 E.05064
G1 X21.849 Y26.417
G1 X20.684 Y27.583 E.05064
G1 X20.417 Y27.316
G1 X21.583 Y26.151 E.05064
G1 X21.583 Y25.617
G1 X20.417 Y26.783 E.05064
G1 X20.417 Y26.249
G1 X21.583 Y25.084 E.05064
G1 X21.583 Y24.551
G1 X20.417 Y25.716 E.05064
G1 X20.417 Y25.183
G1 X21.583 Y24.018 E.05064
G1 X21.583 Y23.484
G1 X20.417 Y24.65 E.05064
G1 X20.417 Y24.116
G1 X21.583 Y22.951 E.05064
G1 X21.583 Y22.418
G1 X20.417 Y23.583 E.05064
G1 X20.417 Y23.05
G1 X21.583 Y21.885 E.05064
G1 X21.583 Y21.351
G1 X20.417 Y22.517 E.05064
G1 X20.417 Y21.983
G1 X21.583 Y20.818 E.05064
G1 X21.583 Y20.285
G1 X20.417 Y21.45 E.05064
G1 X20.417 Y20.917
G1 X21.583 Y19.752 E.05064
G1 X21.583 Y19.218
G1 X20.417 Y20.384 E.05064
G1 X20.417 Y19.85
G1 X21.583 Y18.685 E.05064
G1 X21.583 Y18.152
G1 X20.417 Y19.317 E.05064
G1 X20.417 Y18.784
G1 X21.583 Y17.619 E.05064
G1 X21.583 Y17.085
G1 X20.417 Y18.251 E.05064
G1 X20.417 Y17.717
G1 X21.583 Y16.552 E.05064
G1 X21.583 Y16.019
G1 X20.417 Y17.184 E.05064
G1 X20.417 Y16.651
G1 X21.583 Y15.486 E.05064
G1 X21.583 Y14.952
G1 X20.417 Y16.118 E.05064
G1 X20.417 Y15.584
G1 X21.583 Y14.419 E.05064
G1 X21.583 Y13.886
G1 X20.417 Y15.051 E.05064
G1 X20.417 Y14.518
G1 X21.583 Y13.353 E.05064
G1 X21.583 Y12.819
G1 X20.417 Y13.984 E.05064
G1 X20.417 Y13.451
G1 X21.583 Y12.286 E.05064
G1 X21.583 Y11.753
G1 X20.417 Y12.918 E.05064
G1 X20.417 Y12.385
G1 X21.583 Y11.219 E.05064
G1 X21.583 Y10.686
G1 X20.417 Y11.851 E.05064
G1 X20.417 Y11.318
G1 X21.583 Y10.153 E.05064
G1 X21.583 Y9.62
G1 X20.417 Y10.785 E.05064
G1 X20.417 Y10.252
G1 X21.583 Y9.086 E.05064
G1 X21.583 Y8.553
G1 X20.417 Y9.718 E.05064
G1 X20.417 Y9.185
G1 X21.583 Y8.02 E.05064
G1 X21.583 Y7.487
G1 X20.417 Y8.652 E.05064
G1 X20.417 Y8.119
G1 X21.583 Y6.953 E.05064
G1 X21.583 Y6.42
G1 X20.417 Y7.585 E.05064
G1 X20.417 Y7.052
G1 X21.583 Y5.887 E.05064
; WIPE_START
G1 F12000
M204 S10000
G1 X20.417 Y7.052 E-.62621
G1 X20.417 Y7.404 E-.13379
; WIPE_END
G1 E-.04 F1800
G1 X20.417 Y6.519 Z44.4 F30000
G1 Z44
G1 E.8 F1800
G1 F8835
M204 S2000
G1 X22.519 Y4.417 E.09132
G1 X21.986 Y4.417
G1 X20.417 Y5.986 E.06815
G1 X20.417 Y5.452
G1 X21.452 Y4.417 E.04498
G1 X20.919 Y4.417
G1 X20.417 Y4.919 E.0218
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F12000
M204 S10000
G1 X20.919 Y4.417 E-.26964
G1 X21.452 Y4.417 E-.20264
G1 X20.917 Y4.953 E-.28772
; WIPE_END
G1 E-.04 F1800
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
G1 Z44.5 F900 ; lower z a little
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

    G1 Z144 F600
    G1 Z142

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

