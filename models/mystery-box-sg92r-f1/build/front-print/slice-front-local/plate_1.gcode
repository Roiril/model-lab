; HEADER_BLOCK_START
; BambuStudio 02.03.01.51
; model printing time: 8m 35s; total estimated time: 15m 51s
; total layer number: 58
; total filament length [mm] : 1197.60
; total filament volume [cm^3] : 2880.57
; total filament weight [g] : 3.63
; filament_density: 1.26
; filament_diameter: 1.75
; max_z_height: 11.60
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
M73 P0 R15
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
M73 P3 R15
G1 E50 F200
M400
M104 S220
G92 E0
M73 P31 R10
G1 E50 F200
M400
M106 P1 S255
G92 E0
G1 E5 F300
M109 S200 ; drop nozzle temp, make filament shink a bit
G92 E0
M73 P32 R10
G1 E-0.5 F300

M73 P34 R10
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
M73 P35 R10
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
    G29 A X20 Y6 I39.45 J35.1
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
M73 P36 R10
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
M73 P37 R9
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
M73 P38 R9
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
M73 P39 R9
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
M73 P40 R9
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
    G1 X180.000 E0.31181 F1508.32
    G1 X185.000 E0.31181 F6033.27
    G1 X190.000 E0.31181 F1508.32
    G1 X195.000 E0.31181 F6033.27
    G1 X200.000 E0.31181 F1508.32
M73 P41 R9
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
; layer num/total_layer_count: 1/58
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
G1 X55.143 Y38.243
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X20.857 Y38.243 E1.27702
G1 X20.857 Y9.957 E1.05354
G1 X22.857 Y9.957 E.07449
G1 X22.857 Y5.766 E.1561
G1 X24.143 Y5.766 E.04789
G1 X24.143 Y9.957 E.1561
G1 X51.857 Y9.957 E1.03225
G1 X51.857 Y5.766 E.1561
G1 X53.143 Y5.766 E.04789
G1 X53.143 Y9.957 E.1561
G1 X55.143 Y9.957 E.07449
G1 X55.143 Y18.457 E.31659
G1 X57.307 Y18.457 E.08061
G1 X57.307 Y7.21 E.4189
G1 X58.593 Y7.21 E.04789
G1 X58.593 Y23.743 E.61578
G1 X55.143 Y23.743 E.1285
G1 X55.143 Y38.183 E.53784
M204 S6000
G1 X55.6 Y38.7 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X20.4 Y38.7 E1.31107
G1 X20.4 Y9.5 E1.08759
G1 X22.4 Y9.5 E.07449
G1 X22.4 Y5.309 E.1561
G1 X24.6 Y5.309 E.08194
G1 X24.6 Y9.5 E.1561
G1 X51.4 Y9.5 E.9982
G1 X51.4 Y5.309 E.1561
G1 X53.6 Y5.309 E.08194
G1 X53.6 Y9.5 E.1561
G1 X55.6 Y9.5 E.07449
G1 X55.6 Y18 E.31659
G1 X56.85 Y18 E.04656
G1 X56.85 Y6.753 E.4189
G1 X59.05 Y6.753 E.08194
M73 P42 R9
G1 X59.05 Y24.2 E.64983
G1 X55.6 Y24.2 E.1285
G1 X55.6 Y38.64 E.53784
; WIPE_START
G1 X53.6 Y38.643 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X53.811 Y31.014 Z.6 F30000
G1 X54.39 Y10.14 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50172
G1 F6300
M204 S500
M73 P44 R8
G1 X54.754 Y10.505 E.01928
G1 X54.754 Y11.153 E.02426
G1 X53.741 Y10.14 E.05359
; WIPE_START
G1 X54.754 Y11.153 E-.5447
G1 X54.754 Y10.587 E-.2153
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X52.96 Y6.764 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X52.351 Y6.154 E.03221
G1 X52.246 Y6.154 E.00393
G1 X52.246 Y6.698 E.02032
M73 P45 R8
G1 X52.754 Y7.207 E.0269
G1 X52.754 Y7.856 E.02426
G1 X52.246 Y7.347 E.0269
G1 X52.246 Y7.996 E.02426
G1 X52.754 Y8.505 E.0269
G1 X52.754 Y9.153 E.02426
G1 X52.246 Y8.645 E.0269
G1 X52.246 Y9.293 E.02426
G1 X52.754 Y9.802 E.0269
G1 X52.754 Y10.346 E.02031
G1 X53.298 Y10.346 E.02031
G1 X54.754 Y11.802 E.07702
G1 X54.754 Y12.451 E.02426
G1 X52.246 Y9.942 E.13265
G1 X52.246 Y10.346 E.01508
G1 X52 Y10.346 E.00918
G1 X54.754 Y13.1 E.14563
G1 X54.754 Y13.749 E.02426
G1 X51.351 Y10.346 E.17994
G1 X50.702 Y10.346 E.02426
G1 X54.754 Y14.398 E.21424
G1 X54.754 Y15.047 E.02426
G1 X50.053 Y10.346 E.24855
G1 X49.405 Y10.346 E.02426
G1 X54.754 Y15.695 E.28286
G1 X54.754 Y16.344 E.02426
G1 X48.756 Y10.346 E.31716
G1 X48.107 Y10.346 E.02426
G1 X54.754 Y16.993 E.35147
G1 X54.754 Y17.642 E.02426
G1 X47.252 Y10.14 E.39665
; WIPE_START
G1 X48.667 Y11.554 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X55.572 Y8.303 Z.6 F30000
G1 X57.49 Y7.401 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X58.204 Y8.115 E.03778
G1 X58.204 Y8.764 E.02426
G1 X57.696 Y8.255 E.0269
G1 X57.696 Y8.904 E.02426
G1 X58.204 Y9.413 E.0269
G1 X58.204 Y10.062 E.02426
G1 X57.696 Y9.553 E.0269
G1 X57.696 Y10.202 E.02426
M73 P46 R8
G1 X58.204 Y10.71 E.0269
G1 X58.204 Y11.359 E.02426
G1 X57.696 Y10.85 E.0269
G1 X57.696 Y11.499 E.02426
G1 X58.204 Y12.008 E.0269
G1 X58.204 Y12.657 E.02426
G1 X57.696 Y12.148 E.0269
G1 X57.696 Y12.797 E.02426
G1 X58.204 Y13.306 E.0269
G1 X58.204 Y13.955 E.02426
G1 X57.696 Y13.446 E.0269
G1 X57.696 Y14.095 E.02426
G1 X58.204 Y14.603 E.0269
G1 X58.204 Y15.252 E.02426
G1 X57.696 Y14.743 E.0269
G1 X57.696 Y15.392 E.02426
G1 X58.204 Y15.901 E.0269
G1 X58.204 Y16.55 E.02426
G1 X57.696 Y16.041 E.0269
G1 X57.696 Y16.69 E.02426
G1 X58.204 Y17.199 E.0269
G1 X58.204 Y17.848 E.02426
G1 X57.696 Y17.339 E.0269
G1 X57.696 Y17.988 E.02426
G1 X58.204 Y18.497 E.0269
G1 X58.204 Y19.145 E.02426
G1 X57.696 Y18.637 E.0269
G1 X57.696 Y18.846 E.00782
G1 X57.256 Y18.846 E.01644
G1 X58.204 Y19.794 E.05016
G1 X58.204 Y20.443 E.02426
G1 X56.607 Y18.846 E.08446
G1 X55.958 Y18.846 E.02426
G1 X58.204 Y21.092 E.11877
G1 X58.204 Y21.741 E.02426
G1 X55.309 Y18.846 E.15307
G1 X54.754 Y18.846 E.02074
G1 X54.754 Y18.291 E.02074
G1 X46.809 Y10.346 E.42008
G1 X46.16 Y10.346 E.02426
G1 X58.204 Y22.39 E.63679
G1 X58.204 Y23.038 E.02426
G1 X45.512 Y10.346 E.6711
G1 X44.863 Y10.346 E.02426
G1 X57.872 Y23.354 E.68781
G1 X57.223 Y23.354 E.02426
G1 X44.214 Y10.346 E.68781
G1 X43.565 Y10.346 E.02426
G1 X56.574 Y23.354 E.68781
G1 X55.925 Y23.354 E.02426
G1 X42.916 Y10.346 E.68781
G1 X42.267 Y10.346 E.02426
G1 X55.276 Y23.354 E.68781
G1 X54.754 Y23.354 E.01951
G1 X54.754 Y23.481 E.00475
G1 X41.619 Y10.346 E.69452
G1 X40.97 Y10.346 E.02426
G1 X54.754 Y24.13 E.72883
G1 X54.754 Y24.779 E.02426
G1 X40.321 Y10.346 E.76314
G1 X39.672 Y10.346 E.02426
G1 X54.754 Y25.428 E.79744
G1 X54.754 Y26.077 E.02426
G1 X39.023 Y10.346 E.83175
G1 X38.374 Y10.346 E.02426
G1 X54.754 Y26.726 E.86605
G1 X54.754 Y27.374 E.02426
G1 X37.726 Y10.346 E.90036
G1 X37.077 Y10.346 E.02426
G1 X54.754 Y28.023 E.93466
G1 X54.754 Y28.672 E.02426
G1 X36.428 Y10.346 E.96897
G1 X35.779 Y10.346 E.02426
G1 X54.754 Y29.321 E1.00328
M73 P47 R8
G1 X54.754 Y29.97 E.02426
G1 X35.13 Y10.346 E1.03758
G1 X34.481 Y10.346 E.02426
G1 X54.754 Y30.619 E1.07189
G1 X54.754 Y31.268 E.02426
G1 X33.832 Y10.346 E1.10619
G1 X33.184 Y10.346 E.02426
G1 X54.754 Y31.916 E1.1405
G1 X54.754 Y32.565 E.02426
G1 X32.535 Y10.346 E1.1748
G1 X31.886 Y10.346 E.02426
G1 X54.754 Y33.214 E1.20911
G1 X54.754 Y33.863 E.02426
G1 X31.237 Y10.346 E1.24342
G1 X30.588 Y10.346 E.02426
G1 X54.754 Y34.512 E1.27772
G1 X54.754 Y35.161 E.02426
G1 X29.939 Y10.346 E1.31203
G1 X29.291 Y10.346 E.02426
G1 X54.754 Y35.809 E1.34633
G1 X54.754 Y36.458 E.02426
G1 X28.642 Y10.346 E1.38064
G1 X27.993 Y10.346 E.02426
G1 X54.754 Y37.107 E1.41494
G1 X54.754 Y37.756 E.02426
G1 X27.344 Y10.346 E1.44925
G1 X26.695 Y10.346 E.02426
G1 X54.204 Y37.854 E1.45446
G1 X53.555 Y37.854 E.02426
G1 X26.046 Y10.346 E1.45446
G1 X25.398 Y10.346 E.02426
G1 X52.906 Y37.854 E1.45446
G1 X52.258 Y37.854 E.02426
G1 X24.543 Y10.14 E1.46533
; WIPE_START
G1 X25.957 Y11.554 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X23.96 Y6.962 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X23.246 Y6.247 E.03778
G1 X23.246 Y6.896 E.02426
G1 X23.754 Y7.405 E.0269
G1 X23.754 Y8.054 E.02426
G1 X23.246 Y7.545 E.0269
G1 X23.246 Y8.194 E.02426
G1 X23.754 Y8.702 E.0269
G1 X23.754 Y9.351 E.02426
G1 X23.246 Y8.842 E.0269
G1 X23.246 Y9.491 E.02426
G1 X51.609 Y37.854 E1.49962
G1 X50.96 Y37.854 E.02426
G1 X23.246 Y10.14 E1.46532
G1 X23.246 Y10.346 E.00768
G1 X22.802 Y10.346 E.01658
G1 X50.311 Y37.854 E1.45446
G1 X49.662 Y37.854 E.02426
G1 X22.153 Y10.346 E1.45446
G1 X21.504 Y10.346 E.02426
G1 X49.013 Y37.854 E1.45446
G1 X48.364 Y37.854 E.02426
G1 X21.246 Y10.736 E1.43384
G1 X21.246 Y11.384 E.02426
G1 X47.716 Y37.854 E1.39953
G1 X47.067 Y37.854 E.02426
G1 X21.246 Y12.033 E1.36523
G1 X21.246 Y12.682 E.02426
G1 X46.418 Y37.854 E1.33092
G1 X45.769 Y37.854 E.02426
G1 X21.246 Y13.331 E1.29662
G1 X21.246 Y13.98 E.02426
G1 X45.12 Y37.854 E1.26231
G1 X44.471 Y37.854 E.02426
G1 X21.246 Y14.629 E1.22801
G1 X21.246 Y15.277 E.02426
G1 X43.823 Y37.854 E1.1937
G1 X43.174 Y37.854 E.02426
G1 X21.246 Y15.926 E1.15939
G1 X21.246 Y16.575 E.02426
G1 X42.525 Y37.854 E1.12509
G1 X41.876 Y37.854 E.02426
G1 X21.246 Y17.224 E1.09078
G1 X21.246 Y17.873 E.02426
G1 X41.227 Y37.854 E1.05648
G1 X40.578 Y37.854 E.02426
G1 X21.246 Y18.522 E1.02217
G1 X21.246 Y19.17 E.02426
G1 X39.93 Y37.854 E.98787
G1 X39.281 Y37.854 E.02426
G1 X21.246 Y19.819 E.95356
G1 X21.246 Y20.468 E.02426
G1 X38.632 Y37.854 E.91925
G1 X37.983 Y37.854 E.02426
M73 P48 R8
G1 X21.246 Y21.117 E.88495
G1 X21.246 Y21.766 E.02426
G1 X37.334 Y37.854 E.85064
G1 X36.685 Y37.854 E.02426
G1 X21.246 Y22.415 E.81634
G1 X21.246 Y23.063 E.02426
G1 X36.037 Y37.854 E.78203
G1 X35.388 Y37.854 E.02426
G1 X21.246 Y23.712 E.74772
G1 X21.246 Y24.361 E.02426
G1 X34.739 Y37.854 E.71342
G1 X34.09 Y37.854 E.02426
G1 X21.246 Y25.01 E.67911
G1 X21.246 Y25.659 E.02426
G1 X33.441 Y37.854 E.64481
G1 X32.792 Y37.854 E.02426
G1 X21.246 Y26.308 E.6105
G1 X21.246 Y26.957 E.02426
G1 X32.143 Y37.854 E.5762
G1 X31.495 Y37.854 E.02426
G1 X21.246 Y27.605 E.54189
G1 X21.246 Y28.254 E.02426
G1 X30.846 Y37.854 E.50758
G1 X30.197 Y37.854 E.02426
G1 X21.246 Y28.903 E.47328
G1 X21.246 Y29.552 E.02426
G1 X29.548 Y37.854 E.43897
G1 X28.899 Y37.854 E.02426
G1 X21.246 Y30.201 E.40467
G1 X21.246 Y30.85 E.02426
G1 X28.25 Y37.854 E.37036
G1 X27.602 Y37.854 E.02426
G1 X21.246 Y31.498 E.33606
G1 X21.246 Y32.147 E.02426
G1 X26.953 Y37.854 E.30175
G1 X26.304 Y37.854 E.02426
M73 P49 R8
G1 X21.246 Y32.796 E.26744
G1 X21.246 Y33.445 E.02426
G1 X25.655 Y37.854 E.23314
G1 X25.006 Y37.854 E.02426
G1 X21.246 Y34.094 E.19883
G1 X21.246 Y34.743 E.02426
G1 X24.357 Y37.854 E.16453
G1 X23.709 Y37.854 E.02426
G1 X21.246 Y35.391 E.13022
G1 X21.246 Y36.04 E.02426
G1 X23.06 Y37.854 E.09592
G1 X22.411 Y37.854 E.02426
G1 X21.246 Y36.689 E.06161
G1 X21.246 Y37.338 E.02426
G1 X21.968 Y38.06 E.03818
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6300
G1 X21.246 Y37.338 E-.38805
G1 X21.246 Y36.689 E-.24656
G1 X21.479 Y36.922 E-.12539
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/58
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
G1 X55.398 Y38.498
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.196 E.90567
G1 X55.398 Y11.196 E1.15424
G1 X55.398 Y18.202 E.23242
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.196 E.23242
G1 X58.848 Y11.196 E.05957
M73 P49 R7
G1 X58.848 Y23.998 E.42468
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
; WIPE_START
G1 X53.398 Y38.441 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y30.809 Z.8 F30000
G1 X53.398 Y7.004 Z.8
G1 Z.4
G1 E.8 F1800
G1 F15476.087
G1 X51.602 Y7.004 E.05957
G1 X51.602 Y5.382 E.05383
G1 X53.398 Y5.382 E.05957
G1 X53.398 Y6.944 E.05184
; WIPE_START
M73 P50 R7
G1 X51.602 Y7.004 E-.68281
G1 X51.602 Y6.801 E-.07719
; WIPE_END
G1 E-.04 F1800
G1 X43.97 Y6.858 Z.8 F30000
G1 X24.398 Y7.004 Z.8
G1 Z.4
G1 E.8 F1800
G1 F15476.087
G1 X22.602 Y7.004 E.05957
G1 X22.602 Y5.382 E.05383
G1 X24.398 Y5.382 E.05957
G1 X24.398 Y6.944 E.05184
; WIPE_START
G1 X22.602 Y7.004 E-.68281
G1 X22.602 Y6.801 E-.07719
; WIPE_END
G1 E-.04 F1800
G1 X28.089 Y12.107 Z.8 F30000
G1 X55.79 Y38.89 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y9.31 E.90891
G1 X22.21 Y9.31 E.06145
G1 X22.21 Y5.878 E.10546
G1 X22.21 Y5.478 E.01229
G1 F11833.268
G1 X22.21 Y5.078 E.01229
G1 F5017.384
G1 X22.21 Y4.99 E.00272
G1 F3900
G1 X24.79 Y4.99 E.07928
G1 F5017.384
G1 X24.79 Y5.078 E.00272
G1 F11833.268
G1 X24.79 Y5.478 E.01229
G1 F12000
G1 X24.79 Y5.878 E.01229
G1 X24.79 Y9.31 E.10546
G1 X51.21 Y9.31 E.81181
G1 X51.21 Y5.878 E.10546
G1 X51.21 Y5.478 E.01229
G1 F11833.268
G1 X51.21 Y5.078 E.01229
G1 F5017.384
G1 X51.21 Y4.99 E.00272
G1 F3900
G1 X53.79 Y4.99 E.07928
G1 F5017.384
G1 X53.79 Y5.078 E.00272
M73 P51 R7
G1 F11833.268
G1 X53.79 Y5.478 E.01229
G1 F12000
G1 X53.79 Y5.878 E.01229
G1 X53.79 Y9.31 E.10546
G1 X55.79 Y9.31 E.06145
G1 X55.79 Y17.81 E.26118
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y7.322 E.32226
G1 X56.66 Y6.922 E.01229
G1 F10046.535
G1 X56.66 Y6.522 E.01229
G1 F3879.43
G1 X56.66 Y6.369 E.00471
G1 F2280
G1 X59.24 Y6.369 E.07928
G1 F3879.43
G1 X59.24 Y6.522 E.00471
G1 F10046.535
G1 X59.24 Y6.922 E.01229
G1 F12000
G1 X59.24 Y7.322 E.01229
G1 X59.24 Y24.39 E.52445
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X54.47 Y38.334 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42118
G1 F15000
G1 X55.065 Y37.739 E.02594
G1 X55.065 Y37.204 E.01649
G1 X54.104 Y38.165 E.04186
G1 X53.569 Y38.165 E.01649
G1 X55.065 Y36.669 E.06518
G1 X55.065 Y36.135 E.01649
G1 X53.035 Y38.165 E.0885
G1 X52.5 Y38.165 E.01649
G1 X55.065 Y35.6 E.11182
G1 X55.065 Y35.065 E.01649
G1 X51.965 Y38.165 E.13514
G1 X51.43 Y38.165 E.01649
G1 X55.065 Y34.53 E.15846
G1 X55.065 Y33.995 E.01649
G1 X50.895 Y38.165 E.18177
G1 X50.36 Y38.165 E.01649
G1 X55.065 Y33.46 E.20509
G1 X55.065 Y32.925 E.01649
G1 X49.825 Y38.165 E.22841
G1 X49.29 Y38.165 E.01649
G1 X55.065 Y32.39 E.25173
G1 X55.065 Y31.855 E.01649
G1 X48.755 Y38.165 E.27505
G1 X48.22 Y38.165 E.01649
G1 X55.065 Y31.32 E.29837
G1 X55.065 Y30.785 E.01649
G1 X47.685 Y38.165 E.32169
G1 X47.15 Y38.165 E.01649
G1 X55.065 Y30.25 E.345
G1 X55.065 Y29.715 E.01649
G1 X46.615 Y38.165 E.36832
G1 X46.08 Y38.165 E.01649
G1 X55.065 Y29.18 E.39164
G1 X55.065 Y28.645 E.01649
G1 X45.545 Y38.165 E.41496
G1 X45.01 Y38.165 E.01649
G1 X55.065 Y28.11 E.43828
G1 X55.065 Y27.575 E.01649
G1 X44.475 Y38.165 E.4616
G1 X43.941 Y38.165 E.01649
G1 X55.065 Y27.041 E.48491
G1 X55.065 Y26.506 E.01649
G1 X43.406 Y38.165 E.50823
G1 X42.871 Y38.165 E.01649
G1 X55.065 Y25.971 E.53155
G1 X55.065 Y25.436 E.01649
G1 X42.336 Y38.165 E.55487
G1 X41.801 Y38.165 E.01649
G1 X55.065 Y24.901 E.57819
G1 X55.065 Y24.366 E.01649
G1 X41.266 Y38.165 E.60151
G1 X40.731 Y38.165 E.01649
G1 X58.515 Y20.381 E.77521
G1 X58.515 Y20.916 E.01649
G1 X55.766 Y23.665 E.11983
G1 X56.301 Y23.665 E.01649
G1 X58.515 Y21.451 E.09651
G1 X58.515 Y21.986 E.01649
G1 X56.836 Y23.665 E.07319
G1 X57.371 Y23.665 E.01649
G1 X58.515 Y22.521 E.04987
G1 X58.515 Y23.056 E.01649
G1 X57.906 Y23.665 E.02655
G1 X58.441 Y23.665 E.01649
G1 X58.684 Y23.421 E.01063
G1 X57.216 Y17.936 F30000
G1 F15000
G1 X58.515 Y16.636 E.05663
G1 X58.515 Y16.101 E.01649
G1 X57.385 Y17.231 E.04924
G1 X57.385 Y16.696 E.01649
G1 X58.515 Y15.566 E.04924
G1 X58.515 Y15.032 E.01649
G1 X57.385 Y16.161 E.04924
G1 X57.385 Y15.626 E.01649
G1 X58.515 Y14.497 E.04924
G1 X58.515 Y13.962 E.01649
G1 X57.385 Y15.091 E.04924
G1 X57.385 Y14.556 E.01649
G1 X58.515 Y13.427 E.04924
G1 X58.515 Y12.892 E.01649
G1 X57.385 Y14.021 E.04924
G1 X57.385 Y13.486 E.01649
G1 X58.515 Y12.357 E.04924
G1 X58.515 Y11.822 E.01649
G1 X57.385 Y12.951 E.04924
G1 X57.385 Y12.416 E.01649
G1 X58.273 Y11.529 E.0387
G1 X57.738 Y11.529 E.01649
G1 X57.216 Y12.051 E.02277
; WIPE_START
G1 X57.738 Y11.529 E-.28077
G1 X58.273 Y11.529 E-.20328
G1 X57.759 Y12.042 E-.27596
; WIPE_END
G1 E-.04 F1800
G1 X58.567 Y10.973 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X59.033 Y10.508 E.02022
G1 X59.033 Y9.975
G1 X58.034 Y10.973 E.04339
G1 X57.501 Y10.973
G1 X59.033 Y9.441 E.06656
G1 X59.033 Y8.908
G1 X56.968 Y10.973 E.08974
G1 X56.867 Y10.54
G1 X59.033 Y8.375 E.09409
G1 X59.033 Y7.842
G1 X56.867 Y10.007 E.09409
G1 X56.867 Y9.473
G1 X59.033 Y7.308 E.09409
G1 X58.581 Y7.227
G1 X56.867 Y8.94 E.07445
G1 X56.867 Y8.407
G1 X58.047 Y7.227 E.05128
G1 X57.514 Y7.227
G1 X56.867 Y7.874 E.02811
M204 S10000
G1 X56.856 Y6.883 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.67833
G1 F9914.858
G1 X59.044 Y6.883 E.11329
; WIPE_START
G1 X57.044 Y6.883 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.583 Y10.225 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X54.835 Y10.973 E.03251
G1 X54.301 Y10.973
G1 X55.583 Y9.692 E.05568
G1 X55.224 Y9.517
G1 X53.768 Y10.973 E.06326
G1 X53.235 Y10.973
G1 X54.69 Y9.517 E.06326
G1 X54.157 Y9.517
G1 X52.702 Y10.973 E.06326
G1 X52.168 Y10.973
G1 X53.624 Y9.517 E.06326
G1 X53.583 Y9.025
G1 X51.635 Y10.973 E.08463
G1 X51.102 Y10.973
G1 X53.583 Y8.492 E.10781
G1 X53.583 Y7.959
G1 X50.568 Y10.973 E.13098
G1 X50.035 Y10.973
G1 X53.583 Y7.426 E.15415
G1 X53.248 Y7.227
G1 X51.417 Y9.058 E.07956
G1 X51.417 Y8.524
G1 X52.715 Y7.227 E.05638
G1 X52.182 Y7.227
G1 X51.417 Y7.991 E.03321
; WIPE_START
M204 S10000
G1 X52.182 Y7.227 E-.41071
G1 X52.715 Y7.227 E-.20264
G1 X52.442 Y7.5 E-.14666
; WIPE_END
G1 E-.04 F1800
G1 X50.958 Y9.517 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X49.502 Y10.973 E.06326
G1 X48.969 Y10.973
G1 X50.424 Y9.517 E.06326
G1 X49.891 Y9.517
G1 X48.435 Y10.973 E.06326
G1 X47.902 Y10.973
G1 X49.358 Y9.517 E.06326
G1 X48.825 Y9.517
G1 X47.369 Y10.973 E.06326
G1 X46.836 Y10.973
G1 X48.291 Y9.517 E.06326
G1 X47.758 Y9.517
G1 X46.302 Y10.973 E.06326
G1 X45.769 Y10.973
G1 X47.225 Y9.517 E.06326
G1 X46.692 Y9.517
G1 X45.236 Y10.973 E.06326
G1 X44.703 Y10.973
G1 X46.158 Y9.517 E.06326
G1 X45.625 Y9.517
G1 X44.169 Y10.973 E.06326
G1 X43.636 Y10.973
G1 X45.092 Y9.517 E.06326
G1 X44.559 Y9.517
G1 X43.103 Y10.973 E.06326
G1 X42.57 Y10.973
G1 X44.025 Y9.517 E.06326
G1 X43.492 Y9.517
G1 X42.036 Y10.973 E.06326
G1 X41.503 Y10.973
G1 X42.959 Y9.517 E.06326
G1 X42.426 Y9.517
G1 X40.97 Y10.973 E.06326
G1 X40.437 Y10.973
G1 X41.892 Y9.517 E.06326
G1 X41.359 Y9.517
G1 X39.903 Y10.973 E.06326
G1 X39.37 Y10.973
G1 X40.826 Y9.517 E.06326
G1 X40.293 Y9.517
G1 X38.837 Y10.973 E.06326
G1 X38.304 Y10.973
G1 X39.759 Y9.517 E.06326
G1 X39.226 Y9.517
G1 X37.77 Y10.973 E.06326
G1 X37.237 Y10.973
G1 X38.693 Y9.517 E.06326
G1 X38.16 Y9.517
G1 X36.704 Y10.973 E.06326
G1 X36.171 Y10.973
G1 X37.626 Y9.517 E.06326
G1 X37.093 Y9.517
G1 X35.637 Y10.973 E.06326
G1 X35.104 Y10.973
G1 X36.56 Y9.517 E.06326
G1 X36.026 Y9.517
G1 X34.571 Y10.973 E.06326
G1 X34.037 Y10.973
G1 X35.493 Y9.517 E.06326
G1 X34.96 Y9.517
G1 X33.504 Y10.973 E.06326
G1 X32.971 Y10.973
G1 X34.427 Y9.517 E.06326
G1 X33.893 Y9.517
G1 X32.438 Y10.973 E.06326
G1 X31.904 Y10.973
G1 X33.36 Y9.517 E.06326
G1 X32.827 Y9.517
G1 X31.371 Y10.973 E.06326
G1 X30.838 Y10.973
G1 X32.294 Y9.517 E.06326
G1 X31.76 Y9.517
G1 X30.305 Y10.973 E.06326
G1 X29.771 Y10.973
G1 X31.227 Y9.517 E.06326
G1 X30.694 Y9.517
G1 X29.238 Y10.973 E.06326
G1 X28.705 Y10.973
G1 X30.161 Y9.517 E.06326
M73 P52 R7
G1 X29.627 Y9.517
G1 X28.172 Y10.973 E.06326
G1 X27.638 Y10.973
G1 X29.094 Y9.517 E.06326
G1 X28.561 Y9.517
G1 X27.105 Y10.973 E.06326
G1 X26.572 Y10.973
G1 X28.028 Y9.517 E.06326
G1 X27.494 Y9.517
G1 X26.039 Y10.973 E.06326
G1 X25.505 Y10.973
G1 X26.961 Y9.517 E.06326
G1 X26.428 Y9.517
G1 X24.972 Y10.973 E.06326
G1 X24.439 Y10.973
G1 X25.895 Y9.517 E.06326
G1 X25.361 Y9.517
G1 X23.906 Y10.973 E.06326
G1 X23.372 Y10.973
G1 X24.828 Y9.517 E.06326
G1 X24.583 Y9.23
G1 X22.839 Y10.973 E.07576
G1 X22.306 Y10.973
G1 X24.583 Y8.696 E.09894
G1 X24.583 Y8.163
G1 X21.773 Y10.973 E.12211
G1 X21.239 Y10.973
G1 X24.583 Y7.63 E.14528
G1 X24.452 Y7.227
G1 X22.417 Y9.262 E.08843
G1 X22.417 Y8.728
G1 X23.919 Y7.227 E.06525
G1 X23.386 Y7.227
G1 X22.417 Y8.195 E.04208
G1 X22.417 Y7.662
G1 X22.852 Y7.227 E.01891
; WIPE_START
M204 S10000
G1 X22.417 Y7.662 E-.23382
G1 X22.417 Y8.195 E-.20264
G1 X23.019 Y7.593 E-.32354
; WIPE_END
G1 E-.04 F1800
G1 X22.162 Y9.517 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X20.706 Y10.973 E.06326
G1 X20.417 Y10.729
G1 X21.629 Y9.517 E.05263
G1 X21.095 Y9.517
G1 X20.417 Y10.195 E.02946
; WIPE_START
M204 S10000
G1 X21.095 Y9.517 E-.36428
G1 X21.629 Y9.517 E-.20264
G1 X21.269 Y9.877 E-.19307
; WIPE_END
G1 E-.04 F1800
G1 X28.901 Y9.812 Z.8 F30000
G1 X53.707 Y9.601 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.115132
G1 F15000
G1 X53.826 Y9.533 E.00081
; LINE_WIDTH: 0.0959805
G1 X53.82 Y9.516 E.00008
; LINE_WIDTH: 0.0643804
G1 X53.814 Y9.499 E.00003
; WIPE_START
G1 X53.82 Y9.516 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.612 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y6.612 E.03109
G1 X53.006 Y5.774 E.02577
G1 X51.994 Y5.774 E.03109
G1 X51.994 Y6.552 E.02393
G1 X52.413 Y6.193 F30000
; LINE_WIDTH: 0.50452
G1 F13648.18
G1 X52.527 Y6.193 E.00425
; WIPE_START
G1 X52.413 Y6.193 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X44.782 Y6.306 Z.8 F30000
G1 X24.006 Y6.612 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.774 E.02577
G1 X22.994 Y5.774 E.03109
G1 X22.994 Y6.612 E.02577
G1 X23.946 Y6.612 E.02924
G1 X23.413 Y6.193 F30000
; LINE_WIDTH: 0.50451
G1 F13648.476
G1 X23.527 Y6.193 E.00425
; WIPE_START
G1 X23.413 Y6.193 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X20.766 Y12.125 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.42118
G1 F15000
G1 X21.362 Y11.529 E.026
G1 X21.897 Y11.529 E.01649
G1 X20.935 Y12.491 E.04193
G1 X20.935 Y13.025 E.01649
G1 X22.432 Y11.529 E.06524
G1 X22.967 Y11.529 E.01649
G1 X20.935 Y13.56 E.08856
G1 X20.935 Y14.095 E.01649
G1 X23.502 Y11.529 E.11188
G1 X24.037 Y11.529 E.01649
G1 X20.935 Y14.63 E.1352
G1 X20.935 Y15.165 E.01649
G1 X24.572 Y11.529 E.15852
G1 X25.107 Y11.529 E.01649
G1 X20.935 Y15.7 E.18184
G1 X20.935 Y16.235 E.01649
G1 X25.642 Y11.529 E.20515
G1 X26.177 Y11.529 E.01649
G1 X20.935 Y16.77 E.22847
G1 X20.935 Y17.305 E.01649
G1 X26.711 Y11.529 E.25179
G1 X27.246 Y11.529 E.01649
G1 X20.935 Y17.84 E.27511
G1 X20.935 Y18.375 E.01649
G1 X27.781 Y11.529 E.29843
G1 X28.316 Y11.529 E.01649
G1 X20.935 Y18.91 E.32175
G1 X20.935 Y19.445 E.01649
G1 X28.851 Y11.529 E.34507
G1 X29.386 Y11.529 E.01649
G1 X20.935 Y19.98 E.36838
G1 X20.935 Y20.515 E.01649
G1 X29.921 Y11.529 E.3917
G1 X30.456 Y11.529 E.01649
G1 X20.935 Y21.05 E.41502
G1 X20.935 Y21.585 E.01649
G1 X30.991 Y11.529 E.43834
G1 X31.526 Y11.529 E.01649
G1 X20.935 Y22.119 E.46166
G1 X20.935 Y22.654 E.01649
G1 X32.061 Y11.529 E.48498
G1 X32.596 Y11.529 E.01649
G1 X20.935 Y23.189 E.5083
G1 X20.935 Y23.724 E.01649
G1 X33.131 Y11.529 E.53161
G1 X33.666 Y11.529 E.01649
G1 X20.935 Y24.259 E.55493
G1 X20.935 Y24.794 E.01649
G1 X34.201 Y11.529 E.57825
G1 X34.736 Y11.529 E.01649
G1 X20.935 Y25.329 E.60157
G1 X20.935 Y25.864 E.01649
G1 X35.271 Y11.529 E.62489
G1 X35.805 Y11.529 E.01649
G1 X20.935 Y26.399 E.64821
G1 X20.935 Y26.934 E.01649
G1 X36.34 Y11.529 E.67152
G1 X36.875 Y11.529 E.01649
G1 X20.935 Y27.469 E.69484
G1 X20.935 Y28.004 E.01649
G1 X37.41 Y11.529 E.71816
G1 X37.945 Y11.529 E.01649
G1 X20.935 Y28.539 E.74148
G1 X20.935 Y29.074 E.01649
G1 X38.48 Y11.529 E.7648
G1 X39.015 Y11.529 E.01649
G1 X20.935 Y29.609 E.78812
G1 X20.935 Y30.144 E.01649
G1 X39.55 Y11.529 E.81144
G1 X40.085 Y11.529 E.01649
G1 X20.935 Y30.678 E.83475
G1 X20.935 Y31.213 E.01649
G1 X40.62 Y11.529 E.85807
G1 X41.155 Y11.529 E.01649
G1 X20.935 Y31.748 E.88139
G1 X20.935 Y32.283 E.01649
G1 X41.69 Y11.529 E.90471
G1 X42.225 Y11.529 E.01649
G1 X20.935 Y32.818 E.92803
G1 X20.935 Y33.353 E.01649
G1 X42.76 Y11.529 E.95135
G1 X43.295 Y11.529 E.01649
G1 X20.935 Y33.888 E.97466
G1 X20.935 Y34.423 E.01649
G1 X43.83 Y11.529 E.99798
G1 X44.364 Y11.529 E.01649
G1 X20.935 Y34.958 E1.0213
G1 X20.935 Y35.493 E.01649
G1 X44.899 Y11.529 E1.04462
G1 X45.434 Y11.529 E.01649
G1 X20.935 Y36.028 E1.06794
G1 X20.935 Y36.563 E.01649
G1 X45.969 Y11.529 E1.09126
G1 X46.504 Y11.529 E.01649
G1 X20.935 Y37.098 E1.11458
G1 X20.935 Y37.633 E.01649
G1 X47.039 Y11.529 E1.13789
G1 X47.574 Y11.529 E.01649
G1 X20.938 Y38.165 E1.16109
G1 X21.473 Y38.165 E.01649
G1 X48.109 Y11.529 E1.16109
G1 X48.644 Y11.529 E.01649
G1 X22.008 Y38.165 E1.16109
G1 X22.543 Y38.165 E.01649
G1 X49.179 Y11.529 E1.16109
G1 X49.714 Y11.529 E.01649
G1 X23.078 Y38.165 E1.16109
G1 X23.613 Y38.165 E.01649
G1 X50.249 Y11.529 E1.16109
G1 X50.784 Y11.529 E.01649
G1 X24.148 Y38.165 E1.16109
G1 X24.683 Y38.165 E.01649
G1 X51.319 Y11.529 E1.16109
G1 X51.854 Y11.529 E.01649
G1 X25.218 Y38.165 E1.16109
G1 X25.753 Y38.165 E.01649
G1 X52.389 Y11.529 E1.16109
G1 X52.924 Y11.529 E.01649
G1 X26.288 Y38.165 E1.16109
G1 X26.822 Y38.165 E.01649
G1 X53.458 Y11.529 E1.16109
G1 X53.993 Y11.529 E.01649
G1 X27.357 Y38.165 E1.16109
G1 X27.892 Y38.165 E.01649
G1 X54.528 Y11.529 E1.16109
G1 X55.063 Y11.529 E.01649
G1 X28.427 Y38.165 E1.16109
G1 X28.962 Y38.165 E.01649
G1 X55.065 Y12.062 E1.13783
G1 X55.065 Y12.597 E.01649
G1 X29.497 Y38.165 E1.11451
G1 X30.032 Y38.165 E.01649
G1 X55.065 Y13.132 E1.0912
G1 X55.065 Y13.667 E.01649
G1 X30.567 Y38.165 E1.06788
G1 X31.102 Y38.165 E.01649
G1 X55.065 Y14.202 E1.04456
G1 X55.065 Y14.737 E.01649
G1 X31.637 Y38.165 E1.02124
G1 X32.172 Y38.165 E.01649
G1 X55.065 Y15.272 E.99792
G1 X55.065 Y15.807 E.01649
G1 X32.707 Y38.165 E.9746
G1 X33.242 Y38.165 E.01649
G1 X55.065 Y16.342 E.95129
G1 X55.065 Y16.877 E.01649
G1 X33.777 Y38.165 E.92797
G1 X34.312 Y38.165 E.01649
G1 X55.065 Y17.412 E.90465
G1 X55.065 Y17.947 E.01649
G1 X34.847 Y38.165 E.88133
G1 X35.381 Y38.165 E.01649
G1 X55.065 Y18.482 E.85801
G1 X55.065 Y18.535 E.00166
G1 X55.546 Y18.535 E.01483
G1 X35.916 Y38.165 E.85567
G1 X36.451 Y38.165 E.01649
G1 X56.081 Y18.535 E.85567
G1 X56.616 Y18.535 E.01649
G1 X36.986 Y38.165 E.85567
G1 X37.521 Y38.165 E.01649
G1 X58.515 Y17.171 E.91513
G1 X58.515 Y17.706 E.01649
G1 X38.056 Y38.165 E.89181
G1 X38.591 Y38.165 E.01649
G1 X58.515 Y18.241 E.86849
M73 P53 R7
G1 X58.515 Y18.776 E.01649
G1 X39.126 Y38.165 E.84517
G1 X39.661 Y38.165 E.01649
G1 X58.515 Y19.311 E.82185
G1 X58.515 Y19.846 E.01649
G1 X40.026 Y38.334 E.80593
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X41.441 Y36.92 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/58
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
G1 X22.602 Y7.48
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y5.262 E.07359
G1 X24.398 Y5.262 E.05957
G1 X24.398 Y7.48 E.07359
G1 X22.662 Y7.48 E.05758
G1 X22.21 Y7.872 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y5.349 E.07754
G1 X22.21 Y4.949 E.01229
G1 F6885.939
G1 X22.21 Y4.87 E.00242
G1 F5700
G1 X24.79 Y4.87 E.07928
G1 F6885.939
G1 X24.79 Y4.949 E.00242
G1 F12000
G1 X24.79 Y5.349 E.01229
G1 X24.79 Y7.872 E.07754
G1 X22.27 Y7.872 E.07743
; WIPE_START
M204 S10000
G1 X22.222 Y5.873 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.088 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.654 E.04407
G1 X22.994 Y5.654 E.03109
G1 X22.994 Y7.088 E.04407
G1 X23.946 Y7.088 E.02924
G1 X23.659 Y6.741 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X23.659 Y6.001 E.01913
G1 X23.341 Y6.001 E.00821
G1 X23.341 Y6.741 E.01913
G1 X23.599 Y6.741 E.00665
; WIPE_START
G1 X23.341 Y6.741 E-.09779
G1 X23.341 Y6.001 E-.28114
G1 X23.659 Y6.001 E-.12059
G1 X23.659 Y6.687 E-.26049
; WIPE_END
G1 E-.04 F1800
G1 X29.049 Y12.09 Z1 F30000
G1 X55.398 Y38.498 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y10.72 E.92145
G1 X55.398 Y10.72 E1.15424
G1 X55.398 Y18.202 E.2482
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y10.72 E.2482
G1 X58.848 Y10.72 E.05957
G1 X58.848 Y23.998 E.44046
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y10.328 E.87764
G1 X55.79 Y10.328 E1.09327
G1 X55.79 Y17.81 E.22991
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y10.328 E.22991
G1 X59.24 Y10.328 E.07928
G1 X59.24 Y24.39 E.43209
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X54.515 Y31.235 Z1 F30000
G1 X55.744 Y18.366 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42223
G1 F15000
G1 X58.515 Y21.136 E.12112
G1 X58.515 Y20.6 E.01658
G1 X56.45 Y18.535 E.09025
G1 X56.987 Y18.535 E.01658
G1 X58.515 Y20.063 E.0668
G1 X58.515 Y19.527 E.01658
G1 X57.385 Y18.398 E.04937
G1 X57.385 Y17.861 E.01658
G1 X58.515 Y18.991 E.04938
G1 X58.515 Y18.454 E.01658
G1 X57.385 Y17.325 E.04937
G1 X57.385 Y16.788 E.01658
G1 X58.515 Y17.918 E.04938
G1 X58.515 Y17.381 E.01658
G1 X57.385 Y16.252 E.04937
G1 X57.385 Y15.715 E.01658
G1 X58.515 Y16.845 E.04938
G1 X58.515 Y16.309 E.01658
G1 X57.385 Y15.179 E.04937
G1 X57.385 Y14.643 E.01658
G1 X58.515 Y15.772 E.04938
G1 X58.515 Y15.236 E.01658
G1 X57.385 Y14.106 E.04937
G1 X57.385 Y13.57 E.01658
G1 X58.515 Y14.699 E.04938
G1 X58.515 Y14.163 E.01658
G1 X57.385 Y13.033 E.04937
G1 X57.385 Y12.497 E.01658
G1 X58.515 Y13.626 E.04937
G1 X58.515 Y13.09 E.01658
G1 X57.385 Y11.96 E.04937
G1 X57.385 Y11.424 E.01658
G1 X58.515 Y12.554 E.04937
G1 X58.515 Y12.017 E.01658
G1 X57.551 Y11.053 E.04214
G1 X58.087 Y11.053 E.01658
G1 X58.684 Y11.65 E.02611
; WIPE_START
G1 X58.087 Y11.053 E-.321
G1 X57.551 Y11.053 E-.20384
G1 X57.988 Y11.491 E-.23516
; WIPE_END
G1 E-.04 F1800
G1 X55.234 Y11.419 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F15000
G1 X54.869 Y11.053 E.01599
G1 X54.332 Y11.053 E.01658
G1 X55.065 Y11.786 E.03202
G1 X55.065 Y12.322 E.01658
G1 X53.796 Y11.053 E.05547
G1 X53.259 Y11.053 E.01658
G1 X55.065 Y12.859 E.07892
G1 X55.065 Y13.395 E.01658
G1 X52.723 Y11.053 E.10237
G1 X52.186 Y11.053 E.01658
G1 X55.065 Y13.931 E.12582
G1 X55.065 Y14.468 E.01658
G1 X51.65 Y11.053 E.14927
G1 X51.114 Y11.053 E.01658
G1 X55.065 Y15.004 E.17271
G1 X55.065 Y15.541 E.01658
G1 X50.577 Y11.053 E.19616
G1 X50.041 Y11.053 E.01658
G1 X55.065 Y16.077 E.21961
G1 X55.065 Y16.613 E.01658
M73 P54 R7
G1 X49.504 Y11.053 E.24306
G1 X48.968 Y11.053 E.01658
G1 X55.065 Y17.15 E.26651
G1 X55.065 Y17.686 E.01658
G1 X48.431 Y11.053 E.28995
G1 X47.895 Y11.053 E.01658
G1 X58.515 Y21.673 E.46421
G1 X58.515 Y22.209 E.01658
G1 X47.359 Y11.053 E.48766
G1 X46.822 Y11.053 E.01658
G1 X58.515 Y22.746 E.51111
G1 X58.515 Y23.282 E.01658
G1 X46.286 Y11.053 E.53455
G1 X45.749 Y11.053 E.01658
G1 X58.361 Y23.665 E.55128
G1 X57.825 Y23.665 E.01658
G1 X45.213 Y11.053 E.55128
G1 X44.676 Y11.053 E.01658
G1 X57.288 Y23.665 E.55128
G1 X56.752 Y23.665 E.01658
G1 X44.14 Y11.053 E.55128
G1 X43.604 Y11.053 E.01658
G1 X56.215 Y23.665 E.55128
G1 X55.679 Y23.665 E.01658
G1 X43.067 Y11.053 E.55128
G1 X42.531 Y11.053 E.01658
G1 X55.143 Y23.665 E.55128
G1 X55.065 Y23.665 E.0024
G1 X55.065 Y24.123 E.01418
G1 X41.994 Y11.053 E.57133
G1 X41.458 Y11.053 E.01658
G1 X55.065 Y24.66 E.59478
G1 X55.065 Y25.196 E.01658
G1 X40.922 Y11.053 E.61823
G1 X40.385 Y11.053 E.01658
G1 X55.065 Y25.733 E.64168
G1 X55.065 Y26.269 E.01658
G1 X39.849 Y11.053 E.66512
G1 X39.312 Y11.053 E.01658
G1 X55.065 Y26.806 E.68857
G1 X55.065 Y27.342 E.01658
G1 X38.776 Y11.053 E.71202
G1 X38.239 Y11.053 E.01658
G1 X55.065 Y27.878 E.73547
G1 X55.065 Y28.415 E.01658
G1 X37.703 Y11.053 E.75892
G1 X37.167 Y11.053 E.01658
G1 X55.065 Y28.951 E.78237
G1 X55.065 Y29.488 E.01658
G1 X36.63 Y11.053 E.80581
G1 X36.094 Y11.053 E.01658
G1 X55.065 Y30.024 E.82926
G1 X55.065 Y30.561 E.01658
G1 X35.557 Y11.053 E.85271
G1 X35.021 Y11.053 E.01658
G1 X55.065 Y31.097 E.87616
G1 X55.065 Y31.633 E.01658
G1 X34.484 Y11.053 E.89961
G1 X33.948 Y11.053 E.01658
G1 X55.065 Y32.17 E.92305
G1 X55.065 Y32.706 E.01658
G1 X33.412 Y11.053 E.9465
G1 X32.875 Y11.053 E.01658
G1 X55.065 Y33.243 E.96995
G1 X55.065 Y33.779 E.01658
G1 X32.339 Y11.053 E.9934
G1 X31.802 Y11.053 E.01658
G1 X55.065 Y34.316 E1.01685
G1 X55.065 Y34.852 E.01658
G1 X31.266 Y11.053 E1.0403
G1 X30.729 Y11.053 E.01658
G1 X55.065 Y35.388 E1.06374
G1 X55.065 Y35.925 E.01658
G1 X30.193 Y11.053 E1.08719
G1 X29.657 Y11.053 E.01658
G1 X55.065 Y36.461 E1.11064
G1 X55.065 Y36.998 E.01658
G1 X29.12 Y11.053 E1.13409
G1 X28.584 Y11.053 E.01658
G1 X55.065 Y37.534 E1.15754
G1 X55.065 Y38.071 E.01658
G1 X28.047 Y11.053 E1.18098
G1 X27.511 Y11.053 E.01658
G1 X54.623 Y38.165 E1.1851
G1 X54.086 Y38.165 E.01658
G1 X26.974 Y11.053 E1.1851
G1 X26.438 Y11.053 E.01658
G1 X53.55 Y38.165 E1.1851
G1 X53.013 Y38.165 E.01658
G1 X25.902 Y11.053 E1.1851
G1 X25.365 Y11.053 E.01658
G1 X52.477 Y38.165 E1.1851
G1 X51.941 Y38.165 E.01658
G1 X24.829 Y11.053 E1.1851
G1 X24.292 Y11.053 E.01658
G1 X51.404 Y38.165 E1.1851
G1 X50.868 Y38.165 E.01658
G1 X23.756 Y11.053 E1.1851
G1 X23.219 Y11.053 E.01658
G1 X50.331 Y38.165 E1.1851
G1 X49.795 Y38.165 E.01658
G1 X22.683 Y11.053 E1.1851
G1 X22.147 Y11.053 E.01658
G1 X49.258 Y38.165 E1.1851
G1 X48.722 Y38.165 E.01658
G1 X21.61 Y11.053 E1.1851
G1 X21.074 Y11.053 E.01658
G1 X48.186 Y38.165 E1.1851
G1 X47.649 Y38.165 E.01658
G1 X20.935 Y11.451 E1.16771
G1 X20.935 Y11.987 E.01658
G1 X47.113 Y38.165 E1.14427
G1 X46.576 Y38.165 E.01658
G1 X20.935 Y12.524 E1.12082
G1 X20.935 Y13.06 E.01658
G1 X46.04 Y38.165 E1.09737
G1 X45.503 Y38.165 E.01658
G1 X20.935 Y13.597 E1.07392
G1 X20.935 Y14.133 E.01658
G1 X44.967 Y38.165 E1.05047
G1 X44.431 Y38.165 E.01658
G1 X20.935 Y14.669 E1.02702
G1 X20.935 Y15.206 E.01658
G1 X43.894 Y38.165 E1.00358
G1 X43.358 Y38.165 E.01658
G1 X20.935 Y15.742 E.98013
G1 X20.935 Y16.279 E.01658
G1 X42.821 Y38.165 E.95668
G1 X42.285 Y38.165 E.01658
G1 X20.935 Y16.815 E.93323
G1 X20.935 Y17.352 E.01658
G1 X41.748 Y38.165 E.90978
G1 X41.212 Y38.165 E.01658
G1 X20.935 Y17.888 E.88634
G1 X20.935 Y18.424 E.01658
G1 X40.676 Y38.165 E.86289
G1 X40.139 Y38.165 E.01658
G1 X20.935 Y18.961 E.83944
G1 X20.935 Y19.497 E.01658
G1 X39.603 Y38.165 E.81599
G1 X39.066 Y38.165 E.01658
G1 X20.935 Y20.034 E.79254
G1 X20.935 Y20.57 E.01658
G1 X38.53 Y38.165 E.7691
G1 X37.993 Y38.165 E.01658
G1 X20.935 Y21.107 E.74565
G1 X20.935 Y21.643 E.01658
G1 X37.457 Y38.165 E.7222
G1 X36.921 Y38.165 E.01658
G1 X20.935 Y22.179 E.69875
G1 X20.935 Y22.716 E.01658
G1 X36.384 Y38.165 E.6753
G1 X35.848 Y38.165 E.01658
G1 X20.935 Y23.252 E.65185
G1 X20.935 Y23.789 E.01658
G1 X35.311 Y38.165 E.62841
G1 X34.775 Y38.165 E.01658
G1 X20.935 Y24.325 E.60496
G1 X20.935 Y24.862 E.01658
G1 X34.238 Y38.165 E.58151
G1 X33.702 Y38.165 E.01658
G1 X20.935 Y25.398 E.55806
G1 X20.935 Y25.934 E.01658
G1 X33.166 Y38.165 E.53461
G1 X32.629 Y38.165 E.01658
G1 X20.935 Y26.471 E.51117
G1 X20.935 Y27.007 E.01658
G1 X32.093 Y38.165 E.48772
G1 X31.556 Y38.165 E.01658
G1 X20.935 Y27.544 E.46427
G1 X20.935 Y28.08 E.01658
G1 X31.02 Y38.165 E.44082
G1 X30.483 Y38.165 E.01658
G1 X20.935 Y28.617 E.41737
G1 X20.935 Y29.153 E.01658
G1 X29.947 Y38.165 E.39392
G1 X29.411 Y38.165 E.01658
G1 X20.935 Y29.689 E.37048
G1 X20.935 Y30.226 E.01658
G1 X28.874 Y38.165 E.34703
G1 X28.338 Y38.165 E.01658
G1 X20.935 Y30.762 E.32358
G1 X20.935 Y31.299 E.01658
G1 X27.801 Y38.165 E.30013
G1 X27.265 Y38.165 E.01658
M73 P55 R7
G1 X20.935 Y31.835 E.27668
G1 X20.935 Y32.371 E.01658
G1 X26.729 Y38.165 E.25324
G1 X26.192 Y38.165 E.01658
G1 X20.935 Y32.908 E.22979
G1 X20.935 Y33.444 E.01658
G1 X25.656 Y38.165 E.20634
G1 X25.119 Y38.165 E.01658
G1 X20.935 Y33.981 E.18289
G1 X20.935 Y34.517 E.01658
G1 X24.583 Y38.165 E.15944
G1 X24.046 Y38.165 E.01658
G1 X20.935 Y35.054 E.136
G1 X20.935 Y35.59 E.01658
G1 X23.51 Y38.165 E.11255
G1 X22.974 Y38.165 E.01658
G1 X20.935 Y36.126 E.0891
G1 X20.935 Y36.663 E.01658
G1 X22.437 Y38.165 E.06565
G1 X21.901 Y38.165 E.01658
G1 X20.935 Y37.199 E.0422
G1 X20.935 Y37.736 E.01658
G1 X21.534 Y38.334 E.02617
; WIPE_START
G1 X20.935 Y37.736 E-.32176
G1 X20.935 Y37.199 E-.20384
G1 X21.371 Y37.635 E-.2344
; WIPE_END
G1 E-.04 F1800
G1 X26.928 Y32.403 Z1 F30000
G1 X53.398 Y7.48 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y7.48 E.05957
G1 X51.602 Y5.262 E.07359
G1 X53.398 Y5.262 E.05957
G1 X53.398 Y7.42 E.0716
G1 X53.79 Y7.872 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y7.872 E.07928
G1 X51.21 Y5.349 E.07754
G1 X51.21 Y4.949 E.01229
G1 F6885.939
G1 X51.21 Y4.87 E.00242
G1 F5700
G1 X53.79 Y4.87 E.07928
G1 F6885.939
G1 X53.79 Y4.949 E.00242
G1 F12000
G1 X53.79 Y5.349 E.01229
G1 X53.79 Y7.812 E.0757
; WIPE_START
M204 S10000
G1 X51.791 Y7.859 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.088 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y7.088 E.03109
G1 X53.006 Y5.654 E.04407
G1 X51.994 Y5.654 E.03109
G1 X51.994 Y7.028 E.04223
G1 X52.341 Y6.741 F30000
; LINE_WIDTH: 0.36025
G1 F15000
G1 X52.659 Y6.741 E.00821
G1 X52.659 Y6.001 E.01913
G1 X52.341 Y6.001 E.00821
G1 X52.341 Y6.681 E.01758
; WIPE_START
G1 X52.341 Y6.001 E-.25834
G1 X52.659 Y6.001 E-.12059
G1 X52.659 Y6.741 E-.28114
G1 X52.396 Y6.741 E-.09992
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y7.48 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X57.052 Y7.48 E.05957
G1 X57.052 Y6.586 E.02967
G1 X58.848 Y6.586 E.05957
G1 X58.848 Y7.42 E.02768
G1 X59.24 Y7.872 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y7.872 E.07928
G1 X56.66 Y7.128 E.02287
G1 X56.66 Y6.728 E.01229
G1 F10180.444
G1 X56.66 Y6.328 E.01229
G1 F3962.81
G1 X56.66 Y6.194 E.00413
G1 F2520
G1 X59.24 Y6.194 E.07928
G1 F3962.81
G1 X59.24 Y6.328 E.00413
G1 F10180.444
G1 X59.24 Y6.728 E.01229
G1 F12000
G1 X59.24 Y7.128 E.01229
G1 X59.24 Y7.812 E.02102
M204 S10000
G1 X58.644 Y7.033 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.53029
G1 F12926.524
G1 X57.256 Y7.033 E.05516
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12926.524
G1 X58.644 Y7.033 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/58
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
G1 X22.602 Y7.09
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y5.155 E.06418
G1 X24.398 Y5.155 E.05957
G1 X24.398 Y7.09 E.06418
G1 X22.662 Y7.09 E.05758
G1 X22.21 Y7.482 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y5.229 E.06923
G1 X22.21 Y4.829 E.01229
G1 F8618.938
G1 X22.21 Y4.763 E.00202
G1 F7500
G1 X24.79 Y4.763 E.07928
G1 F8618.938
G1 X24.79 Y4.829 E.00202
G1 F12000
G1 X24.79 Y5.229 E.01229
G1 X24.79 Y7.482 E.06923
G1 X22.27 Y7.482 E.07743
; WIPE_START
M204 S10000
G1 X22.217 Y5.482 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.698 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.547 E.03535
G1 X22.994 Y5.547 E.03109
G1 X22.994 Y6.698 E.03535
G1 X23.946 Y6.698 E.02924
G1 X23.659 Y6.35 F30000
; LINE_WIDTH: 0.36026
G1 F15000
G1 X23.659 Y5.894 E.0118
G1 X23.341 Y5.894 E.00821
G1 X23.341 Y6.35 E.0118
G1 X23.599 Y6.35 E.00665
; WIPE_START
G1 X23.341 Y6.35 E-.13153
G1 X23.341 Y5.894 E-.23314
G1 X23.659 Y5.894 E-.16219
G1 X23.659 Y6.35 E-.23314
; WIPE_END
G1 E-.04 F1800
G1 X29.021 Y11.782 Z1.2 F30000
G1 X55.398 Y38.498 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.11 E.9085
G1 X55.398 Y11.11 E1.15424
G1 X55.398 Y18.202 E.23525
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.11 E.23525
G1 X58.848 Y11.11 E.05957
G1 X58.848 Y23.998 E.42751
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y10.718 E.86564
G1 X55.79 Y10.718 E1.09327
G1 X55.79 Y17.81 E.21791
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y10.718 E.21791
G1 X59.24 Y10.718 E.07928
G1 X59.24 Y24.39 E.4201
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.201 Y38.15 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X53.829 Y38.15 E.05401
G1 X55.05 Y36.875 E.05855
G1 X30.55 Y12.375 E1.14934
G1 X33.548 Y12.375 E.09947
G1 X20.95 Y24.973 E.591
G1 X20.95 Y25.803 E.02755
G1 X33.297 Y38.15 E.5792
G1 X30.801 Y38.15 E.08278
G1 X55.05 Y13.901 E1.13754
G1 X53.578 Y12.375 E.07035
G1 X48.9 Y12.375 E.15515
M73 P55 R6
G1 X23.125 Y38.15 E1.20916
G1 X25.621 Y38.15 E.08278
G1 X20.95 Y33.479 E.2191
G1 X20.95 Y32.649 E.02755
G1 X41.224 Y12.375 E.9511
G1 X38.226 Y12.375 E.09947
G1 X55.05 Y29.199 E.78925
G1 X46.153 Y38.15 E.41863
G1 X48.649 Y38.15 E.08278
G1 X22.874 Y12.375 E1.20916
G1 X25.872 Y12.375 E.09947
G1 X20.95 Y17.297 E.23091
G1 X20.95 Y18.127 E.02755
G1 X40.973 Y38.15 E.93929
G1 X38.477 Y38.15 E.08278
G1 X55.698 Y20.929 E.80788
G1 X55.698 Y22.171 E.04123
G1 X45.902 Y12.375 E.45958
G1 X44.273 Y12.375 E.05401
G1 X54.98 Y11.957 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.471635
G1 F14695.078
G1 X54.98 Y11.528 E.01498
G1 X21.02 Y11.528 E1.18639
G1 X21.02 Y11.957 E.01498
G1 X54.92 Y11.957 E1.18429
G1 X55.07 Y18.541 F30000
; LINE_WIDTH: 0.39629
G1 F15000
G1 X55.902 Y18.565 E.02395
; LINE_WIDTH: 0.407665
G1 X55.956 Y18.591 E.00181
; LINE_WIDTH: 0.457155
G1 X56.011 Y18.618 E.00205
; LINE_WIDTH: 0.506645
G1 F13585.637
G1 X56.066 Y18.644 E.0023
; LINE_WIDTH: 0.556135
G1 F12275.557
G1 X56.12 Y18.671 E.00254
; LINE_WIDTH: 0.605625
G1 F11195.92
G1 X56.175 Y18.698 E.00279
; LINE_WIDTH: 0.655115
G1 F10290.84
G1 X56.23 Y18.724 E.00303
G1 X56.283 Y18.698 E.00296
; LINE_WIDTH: 0.605625
G1 F11195.92
M73 P56 R6
G1 X56.336 Y18.671 E.00272
; LINE_WIDTH: 0.556135
G1 F12275.557
G1 X56.389 Y18.644 E.00248
; LINE_WIDTH: 0.506645
G1 F13585.637
G1 X56.442 Y18.618 E.00224
; LINE_WIDTH: 0.457155
G1 F15000
G1 X56.495 Y18.591 E.002
; LINE_WIDTH: 0.393249
G1 X56.548 Y18.565 E.00169
G1 X57.256 Y18.565 E.02019
G1 X57.388 Y18.537 E.00385
G1 X57.413 Y17.637 E.02571
G1 X57.34 Y23.635 F30000
; LINE_WIDTH: 0.38292
G1 F15000
G1 X56.548 Y23.635 E.02195
; LINE_WIDTH: 0.40481
G1 X56.51 Y23.616 E.00127
; LINE_WIDTH: 0.44859
G1 X56.471 Y23.596 E.00143
; LINE_WIDTH: 0.49237
G1 F14017.132
G1 X56.433 Y23.577 E.00158
; LINE_WIDTH: 0.53615
G1 F12772.947
G1 X56.394 Y23.557 E.00174
; LINE_WIDTH: 0.57993
G1 F11731.625
G1 X56.356 Y23.537 E.00189
; LINE_WIDTH: 0.62371
G1 F10847.295
G1 X56.317 Y23.518 E.00204
; LINE_WIDTH: 0.66749
G1 F10086.94
G1 X56.279 Y23.498 E.0022
; WIPE_START
G1 X56.317 Y23.518 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.035 Y24.349 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.393459
G1 F15000
G1 X55.035 Y23.794 E.01585
G1 X55.063 Y23.662 E.00385
G1 X55.902 Y23.635 E.02399
; LINE_WIDTH: 0.40481
G1 X55.948 Y23.612 E.00153
; LINE_WIDTH: 0.44859
G1 X55.994 Y23.588 E.00171
; LINE_WIDTH: 0.49237
G1 F14017.132
G1 X56.04 Y23.565 E.0019
; LINE_WIDTH: 0.53615
G1 F12772.947
G1 X56.086 Y23.541 E.00208
; LINE_WIDTH: 0.57993
G1 F11731.625
G1 X56.133 Y23.518 E.00227
; LINE_WIDTH: 0.62371
G1 F10847.295
G1 X56.179 Y23.495 E.00245
; LINE_WIDTH: 0.689141
G1 F9748.993
G1 X56.225 Y23.471 E.00273
G1 X56.225 Y18.789 E.24657
G1 X56.752 Y21.504 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X56.752 Y19.875 E.05401
G1 X57.699 Y18.927 E.04446
G1 X57.778 Y18.927 E.00259
G1 X57.778 Y18.849 E.00259
G1 X58.123 Y18.504 E.01619
G1 X58.123 Y16.92 E.05257
G1 X57.4 Y16.197 E.03388
G1 X57.4 Y14.569 E.05401
G1 X58.485 Y22.49 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38292
G1 F15000
G1 X58.485 Y17.019 E.15158
; WIPE_START
G1 X58.485 Y19.019 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.491 Y11.998 Z1.2 F30000
G1 X53.398 Y7.09 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y7.09 E.05957
G1 X51.602 Y5.155 E.06418
G1 X53.398 Y5.155 E.05957
G1 X53.398 Y7.03 E.06219
G1 X53.79 Y7.482 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y7.482 E.07928
G1 X51.21 Y5.229 E.06923
G1 X51.21 Y4.829 E.01229
G1 F8618.938
G1 X51.21 Y4.763 E.00202
G1 F7500
G1 X53.79 Y4.763 E.07928
G1 F8618.938
G1 X53.79 Y4.829 E.00202
G1 F12000
G1 X53.79 Y5.229 E.01229
G1 X53.79 Y7.422 E.06739
; WIPE_START
M204 S10000
G1 X51.791 Y7.468 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.698 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y6.698 E.03109
G1 X53.006 Y5.547 E.03535
G1 X51.994 Y5.547 E.03109
G1 X51.994 Y6.638 E.03351
G1 X52.341 Y6.35 F30000
; LINE_WIDTH: 0.36025
G1 F15000
G1 X52.659 Y6.35 E.00821
G1 X52.659 Y5.894 E.01179
G1 X52.341 Y5.894 E.00821
G1 X52.341 Y6.29 E.01024
; WIPE_START
G1 X52.341 Y5.894 E-.20247
G1 X52.659 Y5.894 E-.1622
G1 X52.659 Y6.35 E-.23314
G1 X52.341 Y6.35 E-.1622
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y7.09 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X57.052 Y7.09 E.05957
G1 X57.052 Y6.438 E.0216
G1 X58.848 Y6.438 E.05957
G1 X58.848 Y7.03 E.01961
G1 X59.24 Y7.482 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y7.482 E.07928
G1 X56.66 Y6.953 E.01626
G1 X56.66 Y6.553 E.01229
G1 F10341.024
G1 X56.66 Y6.153 E.01229
G1 F4063.233
G1 X56.66 Y6.046 E.00326
G1 F2880
G1 X59.24 Y6.046 E.07928
G1 F4063.233
G1 X59.24 Y6.153 E.00326
G1 F10341.024
G1 X59.24 Y6.553 E.01229
G1 F12000
G1 X59.24 Y6.953 E.01229
G1 X59.24 Y7.422 E.01442
M204 S10000
G1 X58.644 Y6.764 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.28709
G1 F15000
G1 X57.256 Y6.764 E.02763
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.644 Y6.764 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/58
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
G1 X22.602 Y6.802
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y5.06 E.05779
G1 X24.398 Y5.06 E.05957
G1 X24.398 Y6.802 E.05779
G1 X22.662 Y6.802 E.05758
G1 X22.21 Y7.194 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y5.122 E.06368
G1 X22.21 Y4.722 E.01229
G1 F10306.99
G1 X22.21 Y4.668 E.00165
G1 F9300
G1 X24.79 Y4.668 E.07928
G1 F10306.99
G1 X24.79 Y4.722 E.00165
G1 F12000
G1 X24.79 Y5.122 E.01229
G1 X24.79 Y7.194 E.06368
G1 X22.27 Y7.194 E.07743
; WIPE_START
M204 S10000
G1 X22.212 Y5.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.41 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.452 E.02943
G1 X22.994 Y5.452 E.03109
G1 X22.994 Y6.41 E.02943
G1 X23.946 Y6.41 E.02924
; WIPE_START
G1 X22.994 Y6.41 E-.36167
G1 X22.994 Y5.452 E-.364
G1 X23.084 Y5.452 E-.03433
; WIPE_END
G1 E-.04 F1800
G1 X30.709 Y5.792 Z1.4 F30000
G1 X53.398 Y6.802 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.802 E.05957
G1 X51.602 Y5.06 E.05779
G1 X53.398 Y5.06 E.05957
G1 X53.398 Y6.742 E.0558
G1 X53.79 Y7.194 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y7.194 E.07928
G1 X51.21 Y5.122 E.06368
G1 X51.21 Y4.722 E.01229
G1 F10306.99
G1 X51.21 Y4.668 E.00165
G1 F9300
G1 X53.79 Y4.668 E.07928
G1 F10306.99
G1 X53.79 Y4.722 E.00165
G1 F12000
G1 X53.79 Y5.122 E.01229
G1 X53.79 Y7.134 E.06184
; WIPE_START
M204 S10000
G1 X51.791 Y7.181 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.41 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y6.41 E.03109
G1 X53.006 Y5.452 E.02943
G1 X51.994 Y5.452 E.03109
G1 X51.994 Y6.35 E.02759
; WIPE_START
G1 X51.994 Y5.452 E-.3412
G1 X53.006 Y5.452 E-.38447
G1 X53.006 Y5.543 E-.03433
; WIPE_END
G1 E-.04 F1800
G1 X53.558 Y13.155 Z1.4 F30000
G1 X55.398 Y38.498 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.398 E.89897
G1 X55.398 Y11.398 E1.15424
G1 X55.398 Y18.202 E.22572
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.398 E.22572
G1 X58.848 Y11.398 E.05957
G1 X58.848 Y23.998 E.41798
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.005 E.85681
G1 X55.79 Y11.005 E1.09327
G1 X55.79 Y17.81 E.20908
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y11.005 E.20908
G1 X59.24 Y11.005 E.07928
G1 X59.24 Y24.39 E.41127
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.578 Y37.773 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X54.206 Y37.773 E.05401
G1 X54.673 Y37.306 E.02187
G1 X54.673 Y36.498 E.02683
G1 X30.67 Y12.495 E1.12603
G1 X33.429 Y12.495 E.09152
G1 X21.327 Y24.596 E.56768
G1 X21.327 Y26.18 E.05257
G1 X32.92 Y37.773 E.54381
G1 X31.178 Y37.773 E.05776
G1 X54.673 Y14.278 E1.10215
G1 X54.673 Y13.47 E.02683
G1 X53.697 Y12.495 E.04574
G1 X52.069 Y12.495 E.05401
; WIPE_START
G1 X53.697 Y12.495 E-.61876
G1 X53.96 Y12.757 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X58.015 Y16.812 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F15476.087
G1 X57.4 Y16.197 E.02883
G1 X58.681 Y16.885 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.41876
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X57.219 Y18.346 E.11598
G1 X53.285 Y20.292 F30000
G1 F3000
G1 X55.005 Y18.572 E.1365
G1 X55.668 Y18.572 E.0372
G1 X53.759 Y20.48 E.15144
G1 X54.091 Y20.812 E.0263
G1 X56.331 Y18.572 E.17775
G1 X56.994 Y18.572 E.0372
G1 X54.422 Y21.143 E.20405
G1 X54.694 Y21.415 E.02157
G1 X50.856 Y25.253 E.30458
G1 X50.916 Y25.312 E.00474
G1 X58.478 Y17.75 E.60014
G1 X58.478 Y18.413 E.0372
G1 X51.247 Y25.644 E.57384
G1 X51.579 Y25.975 E.0263
G1 X58.478 Y19.076 E.54754
G1 X58.478 Y19.739 E.0372
G1 X51.91 Y26.307 E.52123
G1 X52.242 Y26.638 E.0263
G1 X58.478 Y20.402 E.49493
G1 X58.478 Y21.065 E.0372
G1 X55.915 Y23.628 E.20344
G1 X56.578 Y23.628 E.0372
G1 X58.478 Y21.728 E.15083
G1 X58.478 Y22.391 E.0372
G1 X57.038 Y23.831 E.11429
; WIPE_START
G1 X58.452 Y22.416 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.035 Y24.799 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; Slow Down Start
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.39932
; LAYER_HEIGHT: 0.2
G1 F3000;_EXTRUDE_SET_SPEED
G1 X55.035 Y37.976 E.38268
G1 X55.008 Y38.108 E.00391
G1 X54.876 Y38.135 E.00391
G1 X21.124 Y38.135 E.98023
G1 X20.992 Y38.108 E.00391
G1 X20.965 Y37.976 E.00391
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.407917
;_EXTRUDE_SET_SPEED
G1 X20.965 Y34.307 E.10913
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.457912
;_EXTRUDE_SET_SPEED
G1 X20.965 Y30.637 E.12408
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.507906
;_EXTRUDE_SET_SPEED
G1 X20.965 Y26.968 E.13903
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.5579
;_EXTRUDE_SET_SPEED
G1 X20.965 Y23.299 E.15398
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.607895
;_EXTRUDE_SET_SPEED
G1 X20.965 Y19.63 E.16893
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.657889
;_EXTRUDE_SET_SPEED
G1 X20.965 Y15.96 E.18388
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.707883
;_EXTRUDE_SET_SPEED
G1 X20.965 Y12.291 E.19882
; Slow Down End
; LINE_WIDTH: 0.403207
G1 F12000
G1 X20.986 Y12.251 E.00133
; LINE_WIDTH: 0.44378
G1 X21.008 Y12.211 E.00148
; LINE_WIDTH: 0.484354
G1 X21.029 Y12.171 E.00163
; LINE_WIDTH: 0.527465
G1 X21.054 Y12.126 E.00202
; LINE_WIDTH: 0.573113
G1 F11882.484
G1 X21.078 Y12.081 E.00221
; LINE_WIDTH: 0.61876
G1 F10940.537
G1 X21.102 Y12.036 E.0024
; LINE_WIDTH: 0.664408
G1 F10136.96
G1 X21.126 Y11.991 E.00259
; LINE_WIDTH: 0.710056
G1 F9443.352
G1 X21.151 Y11.946 E.00278
; LINE_WIDTH: 0.707883
M73 P57 R6
G1 F9474.213
G1 X25.965 Y11.946 E.26086
; LINE_WIDTH: 0.657889
G1 F10244.427
G1 X30.779 Y11.946 E.24125
; LINE_WIDTH: 0.607895
G1 F11150.95
G1 X35.593 Y11.946 E.22163
; LINE_WIDTH: 0.5579
G1 F12000
G1 X40.407 Y11.946 E.20202
; LINE_WIDTH: 0.507906
G1 X45.221 Y11.946 E.18241
; LINE_WIDTH: 0.457912
G1 X50.035 Y11.946 E.1628
; LINE_WIDTH: 0.407917
G1 X54.849 Y11.946 E.14318
; LINE_WIDTH: 0.710056
G1 F9443.352
G1 X54.874 Y11.991 E.00278
; LINE_WIDTH: 0.664408
G1 F10136.96
G1 X54.898 Y12.036 E.00259
; LINE_WIDTH: 0.61876
G1 F10940.537
G1 X54.922 Y12.081 E.0024
; LINE_WIDTH: 0.573113
G1 F11882.484
G1 X54.946 Y12.126 E.00221
; Slow Down Start
; LINE_WIDTH: 0.527465
G1 F3000;_EXTRUDE_SET_SPEED
G1 X54.971 Y12.171 E.00202
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.484354
;_EXTRUDE_SET_SPEED
G1 X54.992 Y12.211 E.00163
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.44378
;_EXTRUDE_SET_SPEED
G1 X55.014 Y12.251 E.00148
; Slow Down End
; Slow Down Start
; LINE_WIDTH: 0.383077
;_EXTRUDE_SET_SPEED
G1 X55.035 Y12.291 E.00126
G1 X55.035 Y18.138 E.16208
; Slow Down End
G1 X53.54 Y20.866 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X52.815 Y20.142 E.03399
G1 X53.242 Y19.715 E.02003
G1 X46.022 Y12.495 E.33873
G1 X48.78 Y12.495 E.09152
G1 X23.502 Y37.773 E1.18584
G1 X25.244 Y37.773 E.05776
G1 X21.327 Y33.856 E.18372
G1 X21.327 Y32.272 E.05257
G1 X41.104 Y12.495 E.92778
G1 X38.346 Y12.495 E.09152
G1 X50.677 Y24.826 E.57848
G1 X50.25 Y25.253 E.02003
G1 X50.812 Y25.815 E.02637
G1 X38.854 Y37.773 E.56096
G1 X40.596 Y37.773 E.05776
G1 X21.327 Y18.504 E.90391
G1 X21.327 Y16.92 E.05257
G1 X25.753 Y12.495 E.20759
G1 X22.994 Y12.495 E.09152
G1 X48.272 Y37.773 E1.18584
G1 X46.53 Y37.773 E.05776
G1 X54.673 Y29.63 E.38197
G1 X54.673 Y28.822 E.02683
G1 X52.874 Y27.023 E.08437
G1 X54.026 Y25.872 E.05401
; WIPE_START
G1 X52.874 Y27.023 E-.61876
G1 X53.137 Y27.286 E-.14124
; WIPE_END
G1 E-.04 F1800
G1 X55.187 Y19.934 Z1.4 F30000
G1 X58.848 Y6.802 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
G1 F15476.087
G1 X57.052 Y6.802 E.05957
G1 X57.052 Y6.305 E.01651
G1 X58.848 Y6.305 E.05957
G1 X58.848 Y6.742 E.01452
G1 X59.24 Y7.194 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y7.194 E.07928
G1 X56.66 Y6.805 E.01196
G1 X56.66 Y6.405 E.01229
G1 F10304.298
G1 X56.66 Y6.005 E.01229
G1 F4040.224
G1 X56.66 Y5.913 E.00285
G1 F3000
G1 X59.24 Y5.913 E.07928
G1 F4040.224
G1 X59.24 Y6.005 E.00285
G1 F10304.298
G1 X59.24 Y6.405 E.01229
G1 F12000
G1 X59.24 Y6.805 E.01229
G1 X59.24 Y7.134 E.01011
M204 S10000
G1 X58.644 Y6.554 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13348
G1 F15000
G1 X57.256 Y6.554 E.01025
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.644 Y6.554 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/58
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
G1 X22.602 Y6.58
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y4.972 E.05336
G1 X24.398 Y4.972 E.05957
G1 X24.398 Y6.58 E.05336
G1 X22.662 Y6.58 E.05758
G1 X22.21 Y6.972 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y4.627 E.07206
G1 X22.21 Y4.58 E.00146
G1 F11100
G1 X24.79 Y4.58 E.07928
G1 F12000
G1 X24.79 Y4.627 E.00146
G1 X24.79 Y6.972 E.07206
G1 X22.27 Y6.972 E.07743
; WIPE_START
M204 S10000
G1 X22.219 Y4.973 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.188 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.364 E.02533
G1 X22.994 Y5.364 E.03109
G1 X22.994 Y6.188 E.02533
G1 X23.946 Y6.188 E.02924
G1 X23.406 Y5.776 F30000
; LINE_WIDTH: 0.49036
G1 F14080.099
G1 X23.534 Y5.776 E.00464
; WIPE_START
G1 X23.406 Y5.776 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.742 Y11.234 Z1.6 F30000
G1 X55.398 Y38.498 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.62 E.8916
G1 X55.398 Y11.62 E1.15424
G1 X55.398 Y18.202 E.21835
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.62 E.21835
G1 X58.848 Y11.62 E.05957
G1 X58.848 Y23.998 E.41061
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.228 E.84999
G1 X55.79 Y11.228 E1.09327
G1 X55.79 Y17.81 E.20226
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y11.228 E.20226
G1 X59.24 Y11.228 E.07928
G1 X59.24 Y24.39 E.40445
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X54.321 Y38.331 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.4
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X55.028 Y37.624 E.0512
G1 X55.028 Y36.987 E.03258
G1 X53.887 Y38.128 E.08262
G1 X53.251 Y38.128 E.03258
G1 X55.028 Y36.351 E.1287
G1 X55.028 Y35.714 E.03258
G1 X52.614 Y38.128 E.17478
G1 X51.978 Y38.128 E.03258
G1 X55.028 Y35.078 E.22086
G1 X55.028 Y34.442 E.03258
G1 X51.342 Y38.128 E.26694
G1 X50.705 Y38.128 E.03258
G1 X55.028 Y33.805 E.31302
G1 X55.028 Y33.169 E.03258
G1 X50.069 Y38.128 E.3591
G1 X49.432 Y38.128 E.03258
G1 X55.028 Y32.532 E.40518
G1 X55.028 Y31.896 E.03258
G1 X48.796 Y38.128 E.45126
G1 X48.16 Y38.128 E.03258
G1 X55.028 Y31.26 E.49734
G1 X55.028 Y30.623 E.03258
G1 X47.523 Y38.128 E.54342
G1 X46.887 Y38.128 E.03258
G1 X55.028 Y29.987 E.5895
G1 X55.028 Y29.35 E.03258
G1 X46.25 Y38.128 E.63558
G1 X45.614 Y38.128 E.03258
G1 X55.028 Y28.714 E.68166
G1 X55.028 Y28.078 E.03258
G1 X44.978 Y38.128 E.72774
G1 X44.341 Y38.128 E.03258
G1 X55.028 Y27.441 E.77382
G1 X55.028 Y26.805 E.03258
G1 X43.705 Y38.128 E.8199
G1 X43.068 Y38.128 E.03258
G1 X55.028 Y26.168 E.86598
G1 X55.028 Y25.532 E.03258
G1 X42.432 Y38.128 E.91206
G1 X41.796 Y38.128 E.03258
G1 X55.028 Y24.896 E.95814
G1 X55.028 Y24.259 E.03258
G1 X41.159 Y38.128 E1.00422
G1 X40.523 Y38.128 E.03258
G1 X52.286 Y26.365 E.85177
G1 X51.968 Y26.047 E.02304
G1 X39.886 Y38.128 E.87481
G1 X39.25 Y38.128 E.03258
G1 X51.65 Y25.728 E.89784
G1 X51.332 Y25.41 E.02304
G1 X38.614 Y38.128 E.92088
G1 X37.977 Y38.128 E.03258
G1 X54.851 Y21.254 E1.22182
G1 X54.533 Y20.936 E.02304
G1 X37.341 Y38.128 E1.24486
G1 X36.704 Y38.128 E.03258
G1 X54.215 Y20.618 E1.2679
G1 X53.897 Y20.299 E.02304
G1 X36.068 Y38.128 E1.29094
G1 X35.432 Y38.128 E.03258
G1 X55.028 Y18.532 E1.41894
G1 X55.028 Y17.895 E.03258
G1 X34.795 Y38.128 E1.46502
G1 X34.159 Y38.128 E.03258
G1 X55.028 Y17.259 E1.5111
G1 X55.028 Y16.622 E.03258
G1 X33.522 Y38.128 E1.55718
G1 X32.886 Y38.128 E.03258
G1 X55.028 Y15.986 E1.60326
G1 X55.028 Y15.35 E.03258
G1 X32.25 Y38.128 E1.64934
G1 X31.613 Y38.128 E.03258
G1 X55.028 Y14.713 E1.69542
G1 X55.028 Y14.077 E.03258
G1 X30.977 Y38.128 E1.7415
G1 X30.341 Y38.128 E.03258
G1 X55.028 Y13.44 E1.78758
G1 X55.028 Y12.804 E.03258
G1 X29.704 Y38.128 E1.83366
G1 X29.068 Y38.128 E.03258
G1 X55.028 Y12.168 E1.87974
G1 X55.028 Y11.989 E.00913
G1 X54.57 Y11.989 E.02345
M73 P58 R6
G1 X28.431 Y38.128 E1.89266
G1 X27.795 Y38.128 E.03258
G1 X53.934 Y11.989 E1.89266
G1 X53.297 Y11.989 E.03258
G1 X27.159 Y38.128 E1.89266
G1 X26.522 Y38.128 E.03258
G1 X52.661 Y11.989 E1.89266
G1 X52.025 Y11.989 E.03258
G1 X25.886 Y38.128 E1.89266
G1 X25.249 Y38.128 E.03258
G1 X51.388 Y11.989 E1.89266
G1 X50.752 Y11.989 E.03258
G1 X24.613 Y38.128 E1.89266
G1 X23.977 Y38.128 E.03258
G1 X50.115 Y11.989 E1.89266
G1 X49.479 Y11.989 E.03258
G1 X23.34 Y38.128 E1.89266
G1 X22.704 Y38.128 E.03258
G1 X48.843 Y11.989 E1.89266
G1 X48.206 Y11.989 E.03258
G1 X22.067 Y38.128 E1.89266
G1 X21.431 Y38.128 E.03258
G1 X47.57 Y11.989 E1.89266
G1 X46.933 Y11.989 E.03258
G1 X20.972 Y37.951 E1.87982
G1 X20.972 Y37.315 E.03258
G1 X46.297 Y11.989 E1.83374
G1 X45.661 Y11.989 E.03258
G1 X20.972 Y36.678 E1.78766
G1 X20.972 Y36.042 E.03258
G1 X45.024 Y11.989 E1.74158
G1 X44.388 Y11.989 E.03258
G1 X20.972 Y35.405 E1.6955
G1 X20.972 Y34.769 E.03258
G1 X43.751 Y11.989 E1.64942
G1 X43.115 Y11.989 E.03258
G1 X20.972 Y34.133 E1.60334
G1 X20.972 Y33.496 E.03258
G1 X42.479 Y11.989 E1.55726
G1 X41.842 Y11.989 E.03258
G1 X20.972 Y32.86 E1.51118
G1 X20.972 Y32.223 E.03258
G1 X41.206 Y11.989 E1.4651
G1 X40.569 Y11.989 E.03258
G1 X20.972 Y31.587 E1.41902
G1 X20.972 Y30.951 E.03258
G1 X39.933 Y11.989 E1.37294
G1 X39.297 Y11.989 E.03258
G1 X20.972 Y30.314 E1.32686
G1 X20.972 Y29.678 E.03258
G1 X38.66 Y11.989 E1.28078
G1 X38.024 Y11.989 E.03258
G1 X20.972 Y29.041 E1.2347
G1 X20.972 Y28.405 E.03258
G1 X37.387 Y11.989 E1.18862
G1 X36.751 Y11.989 E.03258
G1 X20.972 Y27.769 E1.14254
G1 X20.972 Y27.132 E.03258
G1 X36.115 Y11.989 E1.09646
G1 X35.478 Y11.989 E.03258
G1 X20.972 Y26.496 E1.05038
G1 X20.972 Y25.859 E.03258
G1 X34.842 Y11.989 E1.0043
G1 X34.206 Y11.989 E.03258
G1 X20.972 Y25.223 E.95822
G1 X20.972 Y24.587 E.03258
G1 X33.569 Y11.989 E.91214
G1 X32.933 Y11.989 E.03258
G1 X20.972 Y23.95 E.86606
G1 X20.972 Y23.314 E.03258
G1 X32.296 Y11.989 E.81998
G1 X31.66 Y11.989 E.03258
G1 X20.972 Y22.677 E.7739
G1 X20.972 Y22.041 E.03258
G1 X31.024 Y11.989 E.72782
M73 P59 R6
G1 X30.387 Y11.989 E.03258
G1 X20.972 Y21.405 E.68174
G1 X20.972 Y20.768 E.03258
G1 X29.751 Y11.989 E.63566
G1 X29.114 Y11.989 E.03258
G1 X20.972 Y20.132 E.58958
G1 X20.972 Y19.495 E.03258
G1 X28.478 Y11.989 E.5435
G1 X27.842 Y11.989 E.03258
G1 X20.972 Y18.859 E.49742
G1 X20.972 Y18.223 E.03258
G1 X27.205 Y11.989 E.45134
G1 X26.569 Y11.989 E.03258
G1 X20.972 Y17.586 E.40526
G1 X20.972 Y16.95 E.03258
G1 X25.932 Y11.989 E.35918
G1 X25.296 Y11.989 E.03258
G1 X20.972 Y16.314 E.3131
G1 X20.972 Y15.677 E.03258
G1 X24.66 Y11.989 E.26702
G1 X24.023 Y11.989 E.03258
G1 X20.972 Y15.041 E.22094
G1 X20.972 Y14.404 E.03258
G1 X23.387 Y11.989 E.17486
G1 X22.75 Y11.989 E.03258
G1 X20.972 Y13.768 E.12878
G1 X20.972 Y13.132 E.03258
G1 X22.114 Y11.989 E.0827
G1 X21.478 Y11.989 E.03258
M73 P60 R6
G1 X20.769 Y12.698 E.05129
; WIPE_START
G1 X21.478 Y11.989 E-.38065
G1 X22.114 Y11.989 E-.24183
G1 X21.858 Y12.245 E-.13752
; WIPE_END
G1 E-.04 F1800
G1 X29.379 Y13.547 Z1.6 F30000
G1 X57.444 Y18.406 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.41999
; LAYER_HEIGHT: 0.2
G1 F12000
G1 X57.369 Y18.556 E.00518
G1 X57.256 Y18.594 E.00366
G1 X55.442 Y18.594 E.05573
G1 X55.442 Y18.946 E.01083
G1 X55.387 Y19.08 E.00443
G1 X54.324 Y20.142 E.04616
G1 X55.464 Y21.281 E.04951
G1 X55.516 Y21.447 E.00535
G1 X55.385 Y21.627 E.00684
G1 X51.759 Y25.253 E.15755
G1 X52.447 Y25.941 E.0299
G1 X55.12 Y23.268 E.11614
G1 X55.28 Y23.215 E.00517
G1 X55.386 Y23.268 E.00366
G3 X55.442 Y23.606 I-.379 J.236 E.0108
G1 X58.456 Y23.606 E.09261
M73 P61 R6
G1 X58.456 Y12.012 E.35625
G1 X57.444 Y12.012 E.03109
G1 X57.444 Y18.346 E.19462
G1 X57.791 Y18.406 F30000
; LINE_WIDTH: 0.36288
G1 F12000
G1 X57.786 Y18.499 E.00243
; LINE_WIDTH: 0.37913
G1 X57.69 Y18.678 E.00558
; LINE_WIDTH: 0.41956
G1 X57.595 Y18.858 E.00625
G1 X57.256 Y18.971 E.01098
G1 X55.809 Y18.971 E.0444
G1 X55.653 Y19.346 E.01247
G1 X54.858 Y20.142 E.03453
G1 X55.73 Y21.015 E.03789
G1 X55.89 Y21.331 E.01086
G1 X55.853 Y21.631 E.00927
G1 X55.651 Y21.894 E.01018
G1 X55.175 Y22.37 E.02068
; LINE_WIDTH: 0.441889
G1 X55.095 Y22.481 E.00444
; LINE_WIDTH: 0.485687
G1 X55.015 Y22.592 E.00493
; LINE_WIDTH: 0.529485
G1 X54.935 Y22.703 E.00541
; LINE_WIDTH: 0.573283
G1 F11878.656
G1 X54.856 Y22.813 E.0059
; LINE_WIDTH: 0.617081
G1 F10972.532
G1 X54.776 Y22.924 E.00639
G1 X54.887 Y22.908 E.00526
; LINE_WIDTH: 0.573283
G1 F11878.656
G1 X54.998 Y22.891 E.00486
; LINE_WIDTH: 0.529485
G1 F12000
G1 X55.11 Y22.875 E.00446
; LINE_WIDTH: 0.485687
G1 X55.221 Y22.858 E.00406
; LINE_WIDTH: 0.420334
G1 X55.332 Y22.841 E.00346
G1 X55.652 Y23.001 E.011
G1 X55.747 Y23.229 E.00759
G1 X58.079 Y23.229 E.07171
G1 X58.079 Y19.1 E.12698
; LINE_WIDTH: 0.40637
G1 X58.092 Y18.813 E.0085
; LINE_WIDTH: 0.3607
M73 P62 R6
G2 X58.109 Y18.406 I-7.918 J-.52 E.01057
G1 X58.109 Y12.359 E.15658
G1 X57.791 Y12.359 E.00822
G1 X57.791 Y18.346 E.15503
G1 X57.702 Y19.2 F30000
; LINE_WIDTH: 0.41999
G1 F12000
G1 X57.256 Y19.348 E.01445
G1 X56.036 Y19.348 E.03749
G1 X55.92 Y19.613 E.00888
G1 X55.391 Y20.142 E.02299
G3 X56.07 Y20.83 I-5.566 J6.173 E.02972
G1 X56.263 Y21.275 E.0149
G1 X56.259 Y21.578 E.0093
G1 X56.202 Y21.775 E.0063
M73 P62 R5
G3 X55.535 Y22.543 I-2.854 J-1.802 E.03137
G1 X55.919 Y22.734 E.01315
G1 X55.968 Y22.852 E.00393
G1 X57.702 Y22.852 E.05329
G1 X57.702 Y19.26 E.11037
G1 X57.325 Y19.702 F30000
G1 F12000
G3 X56.262 Y19.725 I-.8 J-12.392 E.03267
G1 X56.186 Y19.88 E.00528
G1 X55.924 Y20.142 E.0114
G1 X56.366 Y20.596 E.01946
; LINE_WIDTH: 0.440145
G1 X56.452 Y20.74 E.00543
; LINE_WIDTH: 0.480455
G1 X56.538 Y20.884 E.00599
; LINE_WIDTH: 0.520765
G1 X56.624 Y21.029 E.00654
; LINE_WIDTH: 0.569276
G1 F11969.096
G1 X56.71 Y21.173 E.0072
G1 X56.725 Y21.415 E.0104
; LINE_WIDTH: 0.543899
G1 F12000
G1 X56.666 Y21.583 E.00725
; LINE_WIDTH: 0.494335
G1 X56.608 Y21.751 E.00654
; LINE_WIDTH: 0.421648
G1 X56.55 Y21.919 E.00548
G1 X56.264 Y22.348 E.01593
G1 X56.158 Y22.453 E.0046
G2 X57.325 Y22.475 I.965 J-20.918 E.03601
G1 X57.325 Y21.827 E.01997
; LINE_WIDTH: 0.444772
G1 X57.3 Y21.69 E.00458
; LINE_WIDTH: 0.494335
G1 X57.275 Y21.552 E.00514
; LINE_WIDTH: 0.543899
G1 X57.25 Y21.415 E.00571
G1 X57.275 Y21.031 E.01571
; LINE_WIDTH: 0.494335
G1 X57.3 Y20.647 E.01415
; LINE_WIDTH: 0.430762
G2 X57.325 Y19.762 I-6.841 J-.634 E.02798
G1 X56.962 Y20.088 F30000
; LINE_WIDTH: 0.39184
G1 F12000
G1 X56.474 Y20.105 E.01388
G1 X56.443 Y20.148 E.00149
G1 X56.65 Y20.371 E.00866
G1 X56.962 Y21.066 E.02164
G1 X56.962 Y20.148 E.02608
G1 X56.922 Y22.072 F30000
; LINE_WIDTH: 0.45327
G1 F12000
G1 X56.935 Y21.98 E.00313
; LINE_WIDTH: 0.41833
G1 X56.949 Y21.887 E.00286
G1 X52.447 Y25.253 F30000
; LINE_WIDTH: 0.63896
G1 F10569.76
G1 X54.733 Y22.967 E.15703
; WIPE_START
G1 X53.319 Y24.381 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.353 Y16.748 Z1.6 F30000
G1 X53.398 Y6.58 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.58 E.05957
G1 X51.602 Y4.972 E.05336
G1 X53.398 Y4.972 E.05957
G1 X53.398 Y6.52 E.05137
G1 X53.79 Y6.972 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y6.972 E.07928
G1 X51.21 Y4.627 E.07206
G1 X51.21 Y4.58 E.00146
G1 F11100
G1 X53.79 Y4.58 E.07928
G1 F12000
G1 X53.79 Y4.627 E.00146
G1 X53.79 Y6.912 E.07022
; WIPE_START
M204 S10000
G1 X51.791 Y6.959 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.188 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y6.188 E.03109
G1 X53.006 Y5.364 E.02533
G1 X51.994 Y5.364 E.03109
G1 X51.994 Y6.128 E.02349
G1 X52.406 Y5.776 F30000
; LINE_WIDTH: 0.49036
G1 F14080.099
G1 X52.534 Y5.776 E.00464
; WIPE_START
G1 X52.406 Y5.776 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y6.58 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X57.052 Y6.58 E.05957
G1 X57.052 Y6.189 E.013
G1 X58.848 Y6.189 E.05957
G1 X58.848 Y6.52 E.01101
G1 X59.24 Y6.972 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y6.972 E.07928
G1 X56.66 Y6.272 E.02153
G1 X56.66 Y5.872 E.01229
G1 F7809.211
G1 X56.66 Y5.797 E.00231
G1 F6600
G1 X59.24 Y5.797 E.07928
G1 F7809.211
G1 X59.24 Y5.872 E.00231
G1 F12000
G1 X59.24 Y6.272 E.01229
G1 X59.24 Y6.912 E.01969
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y6.959 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/58
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
G1 X22.602 Y6.401
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y4.9 E.04979
G1 X24.398 Y4.9 E.05957
G1 X24.398 Y6.401 E.04979
G1 X22.662 Y6.401 E.05758
G1 X22.21 Y6.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y4.539 E.06928
G1 X22.21 Y4.508 E.00094
G1 X24.79 Y4.508 E.07928
G1 X24.79 Y4.539 E.00094
G1 X24.79 Y6.793 E.06928
G1 X22.27 Y6.793 E.07743
; WIPE_START
M204 S10000
G1 X22.217 Y4.794 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.009 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X24.006 Y5.292 E.02203
G1 X22.994 Y5.292 E.03109
G1 X22.994 Y6.009 E.02203
G1 X23.946 Y6.009 E.02924
G1 X23.353 Y5.651 F30000
; LINE_WIDTH: 0.38278
G1 F15000
G1 X23.587 Y5.651 E.0065
; WIPE_START
G1 X23.353 Y5.651 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.682 Y11.114 Z1.8 F30000
G1 X55.398 Y38.498 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.799 E.88566
G1 X55.398 Y11.799 E1.15424
G1 X55.398 Y18.202 E.21241
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.799 E.21241
G1 X58.848 Y11.799 E.05957
G1 X58.848 Y23.998 E.40467
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.407 E.84449
G1 X55.79 Y11.407 E1.09327
G1 X55.79 Y17.81 E.19676
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y11.407 E.19676
G1 X59.24 Y11.407 E.07928
G1 X59.24 Y24.39 E.39894
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X54.513 Y31.235 Z1.8 F30000
G1 X55.739 Y18.366 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4222
G1 F15000
G1 X58.515 Y21.142 E.12134
G1 X58.515 Y20.605 E.01658
G1 X56.445 Y18.535 E.09048
G1 X56.981 Y18.535 E.01658
G1 X58.515 Y20.069 E.06703
G1 X58.515 Y19.532 E.01658
G1 X57.385 Y18.403 E.04937
G1 X57.385 Y17.867 E.01658
G1 X58.515 Y18.996 E.04937
G1 X58.515 Y18.46 E.01658
G1 X57.385 Y17.33 E.04937
G1 X57.385 Y16.794 E.01658
G1 X58.515 Y17.923 E.04937
G1 X58.515 Y17.387 E.01658
G1 X57.385 Y16.257 E.04937
G1 X57.385 Y15.721 E.01658
G1 X58.515 Y16.851 E.04937
G1 X58.515 Y16.314 E.01658
G1 X57.385 Y15.185 E.04937
G1 X57.385 Y14.648 E.01658
G1 X58.515 Y15.778 E.04937
G1 X58.515 Y15.241 E.01658
G1 X57.385 Y14.112 E.04937
G1 X57.385 Y13.575 E.01658
G1 X58.515 Y14.705 E.04937
G1 X58.515 Y14.169 E.01658
G1 X57.385 Y13.039 E.04937
G1 X57.385 Y12.503 E.01658
G1 X58.515 Y13.632 E.04937
G1 X58.515 Y13.096 E.01658
G1 X57.551 Y12.132 E.04213
G1 X58.087 Y12.132 E.01658
G1 X58.684 Y12.729 E.02611
; WIPE_START
G1 X58.087 Y12.132 E-.32097
G1 X57.551 Y12.132 E-.20382
G1 X57.988 Y12.57 E-.23521
; WIPE_END
G1 E-.04 F1800
G1 X55.234 Y12.497 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F15000
G1 X54.869 Y12.132 E.01598
G1 X54.333 Y12.132 E.01658
G1 X55.065 Y12.864 E.03201
G1 X55.065 Y13.401 E.01658
G1 X53.796 Y12.132 E.05545
G1 X53.26 Y12.132 E.01658
G1 X55.065 Y13.937 E.07889
G1 X55.065 Y14.473 E.01658
G1 X52.723 Y12.132 E.10234
G1 X52.187 Y12.132 E.01658
G1 X55.065 Y15.01 E.12578
G1 X55.065 Y15.546 E.01658
G1 X51.651 Y12.132 E.14923
G1 X51.114 Y12.132 E.01658
G1 X55.065 Y16.082 E.17267
G1 X55.065 Y16.619 E.01658
G1 X50.578 Y12.132 E.19612
G1 X50.041 Y12.132 E.01658
G1 X55.065 Y17.155 E.21956
G1 X55.065 Y17.692 E.01658
G1 X49.505 Y12.132 E.24301
G1 X48.969 Y12.132 E.01658
G1 X58.515 Y21.678 E.41725
G1 X58.515 Y22.214 E.01658
G1 X48.432 Y12.132 E.44069
G1 X47.896 Y12.132 E.01658
G1 X58.515 Y22.751 E.46413
G1 X58.515 Y23.287 E.01658
G1 X47.36 Y12.132 E.48758
G1 X46.823 Y12.132 E.01658
G1 X58.356 Y23.665 E.50408
G1 X57.82 Y23.665 E.01658
G1 X46.287 Y12.132 E.50408
G1 X45.75 Y12.132 E.01658
G1 X57.283 Y23.665 E.50408
G1 X56.747 Y23.665 E.01658
G1 X45.214 Y12.132 E.50408
G1 X44.678 Y12.132 E.01658
G1 X56.211 Y23.665 E.50408
G1 X55.674 Y23.665 E.01658
G1 X44.141 Y12.132 E.50408
G1 X43.605 Y12.132 E.01658
G1 X55.138 Y23.665 E.50408
G1 X55.065 Y23.665 E.00225
G1 X55.065 Y24.128 E.01432
G1 X43.068 Y12.132 E.52434
G1 X42.532 Y12.132 E.01658
G1 X55.065 Y24.665 E.54778
G1 X55.065 Y25.201 E.01658
G1 X41.996 Y12.132 E.57123
G1 X41.459 Y12.132 E.01658
G1 X55.065 Y25.737 E.59467
G1 X55.065 Y26.274 E.01658
G1 X40.923 Y12.132 E.61812
G1 X40.387 Y12.132 E.01658
G1 X55.065 Y26.81 E.64156
G1 X55.065 Y27.346 E.01658
G1 X39.85 Y12.132 E.66501
G1 X39.314 Y12.132 E.01658
G1 X55.065 Y27.883 E.68845
G1 X55.065 Y28.419 E.01658
G1 X38.777 Y12.132 E.7119
G1 X38.241 Y12.132 E.01658
G1 X55.065 Y28.956 E.73534
G1 X55.065 Y29.492 E.01658
G1 X37.705 Y12.132 E.75878
G1 X37.168 Y12.132 E.01658
G1 X55.065 Y30.028 E.78223
G1 X55.065 Y30.565 E.01658
M73 P63 R5
G1 X36.632 Y12.132 E.80567
G1 X36.095 Y12.132 E.01658
G1 X55.065 Y31.101 E.82912
G1 X55.065 Y31.638 E.01658
G1 X35.559 Y12.132 E.85256
G1 X35.023 Y12.132 E.01658
G1 X55.065 Y32.174 E.87601
G1 X55.065 Y32.71 E.01658
G1 X34.486 Y12.132 E.89945
G1 X33.95 Y12.132 E.01658
G1 X55.065 Y33.247 E.9229
G1 X55.065 Y33.783 E.01658
G1 X33.414 Y12.132 E.94634
G1 X32.877 Y12.132 E.01658
G1 X55.065 Y34.319 E.96978
G1 X55.065 Y34.856 E.01658
G1 X32.341 Y12.132 E.99323
G1 X31.804 Y12.132 E.01658
G1 X55.065 Y35.392 E1.01667
G1 X55.065 Y35.929 E.01658
G1 X31.268 Y12.132 E1.04012
G1 X30.732 Y12.132 E.01658
G1 X55.065 Y36.465 E1.06356
G1 X55.065 Y37.001 E.01658
G1 X30.195 Y12.132 E1.08701
G1 X29.659 Y12.132 E.01658
G1 X55.065 Y37.538 E1.11045
G1 X55.065 Y38.074 E.01658
G1 X29.123 Y12.132 E1.1339
G1 X28.586 Y12.132 E.01658
G1 X54.619 Y38.165 E1.13786
G1 X54.083 Y38.165 E.01658
G1 X28.05 Y12.132 E1.13786
G1 X27.513 Y12.132 E.01658
G1 X53.546 Y38.165 E1.13786
G1 X53.01 Y38.165 E.01658
G1 X26.977 Y12.132 E1.13786
G1 X26.441 Y12.132 E.01658
G1 X52.473 Y38.165 E1.13786
G1 X51.937 Y38.165 E.01658
G1 X25.904 Y12.132 E1.13786
G1 X25.368 Y12.132 E.01658
G1 X51.401 Y38.165 E1.13786
G1 X50.864 Y38.165 E.01658
G1 X24.831 Y12.132 E1.13786
G1 X24.295 Y12.132 E.01658
G1 X50.328 Y38.165 E1.13786
G1 X49.792 Y38.165 E.01658
G1 X23.759 Y12.132 E1.13786
G1 X23.222 Y12.132 E.01658
G1 X49.255 Y38.165 E1.13786
G1 X48.719 Y38.165 E.01658
G1 X22.686 Y12.132 E1.13786
G1 X22.15 Y12.132 E.01658
G1 X48.182 Y38.165 E1.13786
G1 X47.646 Y38.165 E.01658
G1 X21.613 Y12.132 E1.13786
G1 X21.077 Y12.132 E.01658
G1 X47.11 Y38.165 E1.13786
G1 X46.573 Y38.165 E.01658
G1 X20.935 Y12.527 E1.1206
G1 X20.935 Y13.063 E.01658
G1 X46.037 Y38.165 E1.09715
G1 X45.501 Y38.165 E.01658
G1 X20.935 Y13.599 E1.07371
G1 X20.935 Y14.136 E.01658
G1 X44.964 Y38.165 E1.05027
G1 X44.428 Y38.165 E.01658
G1 X20.935 Y14.672 E1.02682
G1 X20.935 Y15.209 E.01658
G1 X43.891 Y38.165 E1.00338
G1 X43.355 Y38.165 E.01658
G1 X20.935 Y15.745 E.97993
G1 X20.935 Y16.281 E.01658
G1 X42.819 Y38.165 E.95649
G1 X42.282 Y38.165 E.01658
G1 X20.935 Y16.818 E.93304
G1 X20.935 Y17.354 E.01658
G1 X41.746 Y38.165 E.9096
G1 X41.209 Y38.165 E.01658
G1 X20.935 Y17.891 E.88615
G1 X20.935 Y18.427 E.01658
G1 X40.673 Y38.165 E.86271
G1 X40.137 Y38.165 E.01658
G1 X20.935 Y18.963 E.83927
G1 X20.935 Y19.5 E.01658
G1 X39.6 Y38.165 E.81582
G1 X39.064 Y38.165 E.01658
G1 X20.935 Y20.036 E.79238
G1 X20.935 Y20.572 E.01658
G1 X38.528 Y38.165 E.76893
G1 X37.991 Y38.165 E.01658
G1 X20.935 Y21.109 E.74549
G1 X20.935 Y21.645 E.01658
G1 X37.455 Y38.165 E.72204
G1 X36.918 Y38.165 E.01658
G1 X20.935 Y22.182 E.6986
G1 X20.935 Y22.718 E.01658
G1 X36.382 Y38.165 E.67515
G1 X35.846 Y38.165 E.01658
G1 X20.935 Y23.254 E.65171
G1 X20.935 Y23.791 E.01658
G1 X35.309 Y38.165 E.62827
G1 X34.773 Y38.165 E.01658
G1 X20.935 Y24.327 E.60482
G1 X20.935 Y24.864 E.01658
G1 X34.236 Y38.165 E.58138
G1 X33.7 Y38.165 E.01658
G1 X20.935 Y25.4 E.55793
G1 X20.935 Y25.936 E.01658
G1 X33.164 Y38.165 E.53449
G1 X32.627 Y38.165 E.01658
G1 X20.935 Y26.473 E.51104
G1 X20.935 Y27.009 E.01658
G1 X32.091 Y38.165 E.4876
G1 X31.555 Y38.165 E.01658
G1 X20.935 Y27.545 E.46415
G1 X20.935 Y28.082 E.01658
G1 X31.018 Y38.165 E.44071
G1 X30.482 Y38.165 E.01658
G1 X20.935 Y28.618 E.41727
G1 X20.935 Y29.155 E.01658
G1 X29.945 Y38.165 E.39382
G1 X29.409 Y38.165 E.01658
G1 X20.935 Y29.691 E.37038
G1 X20.935 Y30.227 E.01658
G1 X28.873 Y38.165 E.34693
G1 X28.336 Y38.165 E.01658
G1 X20.935 Y30.764 E.32349
G1 X20.935 Y31.3 E.01658
G1 X27.8 Y38.165 E.30004
G1 X27.263 Y38.165 E.01658
G1 X20.935 Y31.836 E.2766
G1 X20.935 Y32.373 E.01658
G1 X26.727 Y38.165 E.25315
G1 X26.191 Y38.165 E.01658
G1 X20.935 Y32.909 E.22971
G1 X20.935 Y33.446 E.01658
G1 X25.654 Y38.165 E.20627
G1 X25.118 Y38.165 E.01658
G1 X20.935 Y33.982 E.18282
G1 X20.935 Y34.518 E.01658
G1 X24.582 Y38.165 E.15938
G1 X24.045 Y38.165 E.01658
G1 X20.935 Y35.055 E.13593
G1 X20.935 Y35.591 E.01658
G1 X23.509 Y38.165 E.11249
G1 X22.972 Y38.165 E.01658
G1 X20.935 Y36.128 E.08904
G1 X20.935 Y36.664 E.01658
G1 X22.436 Y38.165 E.0656
G1 X21.9 Y38.165 E.01658
G1 X20.935 Y37.2 E.04215
G1 X20.935 Y37.737 E.01658
G1 X21.533 Y38.334 E.02613
; WIPE_START
G1 X20.935 Y37.737 E-.32123
G1 X20.935 Y37.2 E-.20382
G1 X21.372 Y37.638 E-.23494
; WIPE_END
G1 E-.04 F1800
G1 X26.836 Y32.308 Z1.8 F30000
G1 X53.398 Y6.401 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.401 E.05957
G1 X51.602 Y4.9 E.04979
M73 P64 R5
G1 X53.398 Y4.9 E.05957
G1 X53.398 Y6.341 E.0478
G1 X53.79 Y6.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y6.793 E.07928
G1 X51.21 Y4.539 E.06928
G1 X51.21 Y4.508 E.00094
G1 X53.79 Y4.508 E.07928
G1 X53.79 Y4.539 E.00094
G1 X53.79 Y6.733 E.06743
; WIPE_START
M204 S10000
G1 X51.791 Y6.78 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.009 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X53.006 Y6.009 E.03109
G1 X53.006 Y5.292 E.02203
G1 X51.994 Y5.292 E.03109
G1 X51.994 Y5.949 E.02019
G1 X52.353 Y5.651 F30000
; LINE_WIDTH: 0.38278
G1 F15000
G1 X52.587 Y5.651 E.0065
; WIPE_START
G1 X52.353 Y5.651 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y6.401 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X57.052 Y6.401 E.05957
G1 X57.052 Y6.09 E.01032
G1 X58.848 Y6.09 E.05957
G1 X58.848 Y6.341 E.00833
G1 X59.24 Y6.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y6.793 E.07928
G1 X56.66 Y6.156 E.0196
G1 X56.66 Y5.756 E.01229
G1 F10384.185
G1 X56.66 Y5.698 E.00177
G1 F9300
G1 X59.24 Y5.698 E.07928
G1 F10384.185
G1 X59.24 Y5.756 E.00177
G1 F12000
G1 X59.24 Y6.156 E.01229
G1 X59.24 Y6.733 E.01775
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y6.78 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/58
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
G1 X22.602 Y6.253
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y4.829 E.04725
G1 X24.398 Y4.829 E.05957
G1 X24.398 Y6.253 E.04725
G1 X22.662 Y6.253 E.05758
G1 X22.21 Y6.645 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y4.467 E.06692
G1 X22.21 Y4.437 E.00094
G1 X24.79 Y4.437 E.07928
G1 X24.79 Y4.467 E.00094
G1 X24.79 Y6.645 E.06692
G1 X22.27 Y6.645 E.07743
; WIPE_START
M204 S10000
G1 X22.215 Y4.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.94 Y5.795 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55154
G1 F12386.459
G1 X23.94 Y5.286 E.02108
G1 X23.06 Y5.286 E.03648
G1 X23.06 Y5.795 E.02108
G1 X23.88 Y5.795 E.03399
; WIPE_START
G1 X23.06 Y5.795 E-.31167
G1 X23.06 Y5.286 E-.19327
G1 X23.731 Y5.286 E-.25506
; WIPE_END
G1 E-.04 F1800
G1 X28.998 Y10.81 Z2 F30000
G1 X55.398 Y38.498 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y11.947 E.88074
G1 X55.398 Y11.947 E1.15424
G1 X55.398 Y18.202 E.20749
G1 X57.052 Y18.202 E.05487
G1 X57.052 Y11.947 E.20749
G1 X58.848 Y11.947 E.05957
G1 X58.848 Y23.998 E.39975
G1 X55.398 Y23.998 E.11444
G1 X55.398 Y38.438 E.479
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.555 E.83993
G1 X55.79 Y11.555 E1.09327
G1 X55.79 Y17.81 E.1922
G1 X56.66 Y17.81 E.02673
G1 X56.66 Y11.555 E.1922
G1 X59.24 Y11.555 E.07928
G1 X59.24 Y24.39 E.39438
G1 X55.79 Y24.39 E.10601
G1 X55.79 Y38.83 E.4437
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X54.465 Y38.334 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42318
G1 F15000
G1 X55.065 Y37.735 E.02626
G1 X55.065 Y37.197 E.01666
G1 X54.097 Y38.165 E.04239
G1 X53.56 Y38.165 E.01666
G1 X55.065 Y36.66 E.06596
G1 X55.065 Y36.122 E.01666
G1 X53.022 Y38.165 E.08953
G1 X52.484 Y38.165 E.01666
G1 X55.065 Y35.584 E.11309
G1 X55.065 Y35.046 E.01666
G1 X51.946 Y38.165 E.13666
G1 X51.409 Y38.165 E.01666
G1 X55.065 Y34.509 E.16022
G1 X55.065 Y33.971 E.01666
G1 X50.871 Y38.165 E.18379
G1 X50.333 Y38.165 E.01666
G1 X55.065 Y33.433 E.20735
G1 X55.065 Y32.895 E.01666
G1 X49.795 Y38.165 E.23092
G1 X49.257 Y38.165 E.01666
G1 X55.065 Y32.357 E.25449
G1 X55.065 Y31.82 E.01666
G1 X48.72 Y38.165 E.27805
G1 X48.182 Y38.165 E.01666
G1 X55.065 Y31.282 E.30162
G1 X55.065 Y30.744 E.01666
G1 X47.644 Y38.165 E.32518
G1 X47.106 Y38.165 E.01666
G1 X55.065 Y30.206 E.34875
G1 X55.065 Y29.669 E.01666
G1 X46.569 Y38.165 E.37231
G1 X46.031 Y38.165 E.01666
G1 X55.065 Y29.131 E.39588
G1 X55.065 Y28.593 E.01666
G1 X45.493 Y38.165 E.41945
G1 X44.955 Y38.165 E.01666
G1 X55.065 Y28.055 E.44301
G1 X55.065 Y27.518 E.01666
G1 X44.418 Y38.165 E.46658
G1 X43.88 Y38.165 E.01666
G1 X55.065 Y26.98 E.49014
G1 X55.065 Y26.442 E.01666
G1 X43.342 Y38.165 E.51371
G1 X42.804 Y38.165 E.01666
G1 X55.065 Y25.904 E.53727
G1 X55.065 Y25.366 E.01666
G1 X42.266 Y38.165 E.56084
G1 X41.729 Y38.165 E.01666
G1 X55.065 Y24.829 E.58441
G1 X55.065 Y24.649 E.00558
G3 X54.815 Y24.541 I.107 J-.594 E.00851
G1 X41.191 Y38.165 E.59701
G1 X40.653 Y38.165 E.01666
G1 X54.548 Y24.27 E.6089
G3 X54.406 Y23.874 I1.224 J-.663 E.01308
G1 X40.115 Y38.165 E.62624
G1 X39.578 Y38.165 E.01666
G1 X54.406 Y23.337 E.64979
G1 X54.406 Y22.799 E.01666
G1 X39.04 Y38.165 E.67335
G1 X38.502 Y38.165 E.01666
G1 X54.406 Y22.261 E.69692
G1 X54.406 Y21.723 E.01666
G1 X37.964 Y38.165 E.72048
G1 X37.427 Y38.165 E.01666
G1 X54.406 Y21.186 E.74405
G1 X54.406 Y20.648 E.01666
G1 X36.889 Y38.165 E.76762
G1 X36.351 Y38.165 E.01666
G1 X54.406 Y20.11 E.79118
G1 X54.406 Y19.572 E.01666
G1 X35.813 Y38.165 E.81475
G1 X35.275 Y38.165 E.01666
G1 X54.406 Y19.035 E.83831
G1 X54.406 Y18.497 E.01666
G1 X34.738 Y38.165 E.86188
G1 X34.2 Y38.165 E.01666
G1 X55.065 Y17.3 E.91433
G1 X55.065 Y16.762 E.01666
G1 X33.662 Y38.165 E.93789
G1 X33.124 Y38.165 E.01666
G1 X55.065 Y16.224 E.96146
G1 X55.065 Y15.687 E.01666
G1 X32.587 Y38.165 E.98502
G1 X32.049 Y38.165 E.01666
G1 X55.065 Y15.149 E1.00859
G1 X55.065 Y14.611 E.01666
G1 X31.511 Y38.165 E1.03216
G1 X30.973 Y38.165 E.01666
G1 X55.065 Y14.073 E1.05572
G1 X55.065 Y13.536 E.01666
G1 X30.436 Y38.165 E1.07929
G1 X29.898 Y38.165 E.01666
G1 X55.065 Y12.998 E1.10285
G1 X55.065 Y12.46 E.01666
G1 X29.36 Y38.165 E1.12642
G1 X28.822 Y38.165 E.01666
G1 X54.707 Y12.28 E1.1343
G1 X54.169 Y12.28 E.01666
G1 X28.284 Y38.165 E1.1343
G1 X27.747 Y38.165 E.01666
G1 X53.631 Y12.28 E1.1343
G1 X53.093 Y12.28 E.01666
G1 X27.209 Y38.165 E1.1343
G1 X26.671 Y38.165 E.01666
G1 X52.556 Y12.28 E1.1343
G1 X52.018 Y12.28 E.01666
G1 X26.133 Y38.165 E1.1343
G1 X25.596 Y38.165 E.01666
G1 X51.48 Y12.28 E1.1343
G1 X50.942 Y12.28 E.01666
G1 X25.058 Y38.165 E1.1343
G1 X24.52 Y38.165 E.01666
G1 X50.405 Y12.28 E1.1343
G1 X49.867 Y12.28 E.01666
G1 X23.982 Y38.165 E1.1343
G1 X23.445 Y38.165 E.01666
G1 X49.329 Y12.28 E1.1343
G1 X48.791 Y12.28 E.01666
G1 X22.907 Y38.165 E1.1343
G1 X22.369 Y38.165 E.01666
G1 X48.254 Y12.28 E1.1343
G1 X47.716 Y12.28 E.01666
G1 X21.831 Y38.165 E1.1343
G1 X21.293 Y38.165 E.01666
G1 X47.178 Y12.28 E1.1343
G1 X46.64 Y12.28 E.01666
G1 X20.935 Y37.985 E1.12643
G1 X20.935 Y37.447 E.01666
G1 X46.102 Y12.28 E1.10286
M73 P65 R5
G1 X45.565 Y12.28 E.01666
G1 X20.935 Y36.91 E1.0793
G1 X20.935 Y36.372 E.01666
G1 X45.027 Y12.28 E1.05573
G1 X44.489 Y12.28 E.01666
G1 X20.935 Y35.834 E1.03217
G1 X20.935 Y35.296 E.01666
G1 X43.951 Y12.28 E1.0086
G1 X43.414 Y12.28 E.01666
G1 X20.935 Y34.759 E.98503
G1 X20.935 Y34.221 E.01666
G1 X42.876 Y12.28 E.96147
G1 X42.338 Y12.28 E.01666
G1 X20.935 Y33.683 E.9379
G1 X20.935 Y33.145 E.01666
G1 X41.8 Y12.28 E.91434
G1 X41.263 Y12.28 E.01666
G1 X20.935 Y32.608 E.89077
G1 X20.935 Y32.07 E.01666
G1 X40.725 Y12.28 E.86721
G1 X40.187 Y12.28 E.01666
G1 X20.935 Y31.532 E.84364
G1 X20.935 Y30.994 E.01666
G1 X39.649 Y12.28 E.82007
G1 X39.111 Y12.28 E.01666
G1 X20.935 Y30.456 E.79651
G1 X20.935 Y29.919 E.01666
G1 X38.574 Y12.28 E.77294
G1 X38.036 Y12.28 E.01666
G1 X20.935 Y29.381 E.74938
G1 X20.935 Y28.843 E.01666
G1 X37.498 Y12.28 E.72581
G1 X36.96 Y12.28 E.01666
G1 X20.935 Y28.305 E.70225
G1 X20.935 Y27.768 E.01666
G1 X36.423 Y12.28 E.67868
G1 X35.885 Y12.28 E.01666
G1 X20.935 Y27.23 E.65511
G1 X20.935 Y26.692 E.01666
G1 X35.347 Y12.28 E.63155
G1 X34.809 Y12.28 E.01666
G1 X20.935 Y26.154 E.60798
G1 X20.935 Y25.617 E.01666
G1 X34.272 Y12.28 E.58442
G1 X33.734 Y12.28 E.01666
G1 X20.935 Y25.079 E.56085
G1 X20.935 Y24.541 E.01666
G1 X33.196 Y12.28 E.53729
G1 X32.658 Y12.28 E.01666
G1 X20.935 Y24.003 E.51372
G1 X20.935 Y23.465 E.01666
G1 X32.12 Y12.28 E.49015
G1 X31.583 Y12.28 E.01666
G1 X20.935 Y22.928 E.46659
G1 X20.935 Y22.39 E.01666
G1 X31.045 Y12.28 E.44302
G1 X30.507 Y12.28 E.01666
G1 X20.935 Y21.852 E.41946
G1 X20.935 Y21.314 E.01666
G1 X29.969 Y12.28 E.39589
G1 X29.432 Y12.28 E.01666
G1 X20.935 Y20.777 E.37232
G1 X20.935 Y20.239 E.01666
G1 X28.894 Y12.28 E.34876
G1 X28.356 Y12.28 E.01666
G1 X20.935 Y19.701 E.32519
G1 X20.935 Y19.163 E.01666
G1 X27.818 Y12.28 E.30163
G1 X27.281 Y12.28 E.01666
G1 X20.935 Y18.626 E.27806
G1 X20.935 Y18.088 E.01666
G1 X26.743 Y12.28 E.2545
G1 X26.205 Y12.28 E.01666
G1 X20.935 Y17.55 E.23093
G1 X20.935 Y17.012 E.01666
G1 X25.667 Y12.28 E.20736
G1 X25.129 Y12.28 E.01666
G1 X20.935 Y16.474 E.1838
G1 X20.935 Y15.937 E.01666
G1 X24.592 Y12.28 E.16023
G1 X24.054 Y12.28 E.01666
G1 X20.935 Y15.399 E.13667
G1 X20.935 Y14.861 E.01666
G1 X23.516 Y12.28 E.1131
G1 X22.978 Y12.28 E.01666
G1 X20.935 Y14.323 E.08954
G1 X20.935 Y13.786 E.01666
G1 X22.441 Y12.28 E.06597
G1 X21.903 Y12.28 E.01666
G1 X20.935 Y13.248 E.0424
G1 X20.935 Y12.71 E.01666
G1 X21.535 Y12.111 E.02627
; WIPE_START
G1 X20.935 Y12.71 E-.32221
G1 X20.935 Y13.248 E-.20435
G1 X21.37 Y12.813 E-.23344
; WIPE_END
G1 E-.04 F1800
G1 X28.943 Y13.757 Z2 F30000
G1 X57.791 Y17.353 Z2
G1 Z1.6
G1 E.8 F1800
; LINE_WIDTH: 0.361807
G1 F15000
G1 X57.857 Y17.389 E.00195
G1 X58.093 Y17.823 E.01282
G1 X58.109 Y17.261 E.0146
G1 X58.109 Y12.686 E.11887
G1 X57.791 Y12.686 E.00825
G1 X57.791 Y17.293 E.1197
G1 X58.093 Y23.243 F30000
; LINE_WIDTH: 0.3916
G1 F15000
G1 X58.093 Y17.883 E.15231
G1 X57.73 Y23.606 F30000
; LINE_WIDTH: 0.41999
G1 F15000
G1 X58.456 Y23.606 E.0223
G1 X58.456 Y12.339 E.34619
G1 X57.444 Y12.339 E.03109
G1 X57.444 Y17.578 E.16098
G1 X57.652 Y17.67 E.007
G1 X57.73 Y17.823 E.00526
G1 X57.73 Y23.546 E.17586
G1 X56.963 Y23.776 F30000
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X57.523 Y23.216 E.02432
G1 X57.523 Y22.683
G1 X56.43 Y23.776 E.04749
G1 X55.897 Y23.776
G1 X57.523 Y22.149 E.07066
G1 X57.523 Y21.616
M73 P66 R5
G1 X55.364 Y23.776 E.09384
G1 X55.176 Y23.964
G1 X54.841 Y24.298 E.01454
G1 X54.639 Y23.967
G1 X57.523 Y21.083 E.12532
G1 X57.523 Y20.55
G1 X54.613 Y23.46 E.12645
G1 X54.613 Y22.926
G1 X57.523 Y20.016 E.12645
G1 X57.523 Y19.483
G1 X54.613 Y22.393 E.12645
G1 X54.613 Y21.86
G1 X57.523 Y18.95 E.12645
G1 X57.523 Y18.417
G1 X54.613 Y21.327 E.12645
G1 X54.613 Y20.793
G1 X56.982 Y18.424 E.10294
G1 X56.449 Y18.424
G1 X54.613 Y20.26 E.07977
G1 X54.613 Y19.727
G1 X55.915 Y18.424 E.05659
G1 X55.382 Y18.424
G1 X54.613 Y19.194 E.03342
G1 X54.613 Y18.66
G1 X55.176 Y18.098 E.02445
; WIPE_START
M204 S10000
G1 X54.613 Y18.66 E-.30235
G1 X54.613 Y19.194 E-.20264
G1 X55.087 Y18.719 E-.25501
; WIPE_END
G1 E-.04 F1800
G1 X57.542 Y18.352 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.239251
G1 F15000
G1 X57.494 Y18.282 E.00136
; LINE_WIDTH: 0.275191
G1 X57.446 Y18.211 E.00161
; LINE_WIDTH: 0.324306
G1 X57.399 Y18.14 E.00195
G1 X57.399 Y17.906 E.00537
; LINE_WIDTH: 0.315097
G1 X57.463 Y17.86 E.00176
; LINE_WIDTH: 0.287073
G1 X57.528 Y17.814 E.00158
; WIPE_START
G1 X57.463 Y17.86 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.194 Y18.074 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; LINE_WIDTH: 0.240159
G1 F15000
G1 X55.089 Y17.87 E.00369
G2 X54.833 Y18.029 I.094 J.439 E.00494
G1 X54.778 Y18.096 E.0014
; LINE_WIDTH: 0.211969
G1 X54.686 Y18.233 E.00227
; LINE_WIDTH: 0.17363
G1 X54.594 Y18.37 E.00176
; WIPE_START
G1 X54.686 Y18.233 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.87 Y10.644 Z2 F30000
G1 X53.398 Y6.253 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.253 E.05957
G1 X51.602 Y4.829 E.04725
G1 X53.398 Y4.829 E.05957
G1 X53.398 Y6.193 E.04526
G1 X53.79 Y6.645 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y6.645 E.07928
G1 X51.21 Y4.467 E.06692
G1 X51.21 Y4.437 E.00094
G1 X53.79 Y4.437 E.07928
G1 X53.79 Y4.467 E.00094
G1 X53.79 Y6.585 E.06508
; WIPE_START
M204 S10000
G1 X51.791 Y6.631 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.06 Y5.795 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551535
G1 F12386.582
G1 X52.94 Y5.795 E.03648
G1 X52.94 Y5.286 E.02108
G1 X52.06 Y5.286 E.03648
G1 X52.06 Y5.735 E.01859
; WIPE_START
G1 X52.06 Y5.286 E-.17047
G1 X52.94 Y5.286 E-.33448
G1 X52.94 Y5.795 E-.19328
G1 X52.778 Y5.795 E-.06178
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y6.253 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X57.052 Y6.253 E.05957
G1 X57.052 Y5.996 E.00852
G1 X58.848 Y5.996 E.05957
G1 X58.848 Y6.193 E.00653
G1 X59.24 Y6.645 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y6.645 E.07928
G1 X56.66 Y6.057 E.01807
G1 X56.66 Y5.657 E.01229
G1 F11239.081
G1 X56.66 Y5.604 E.00163
G1 F10200
G1 X59.24 Y5.604 E.07928
G1 F11239.081
G1 X59.24 Y5.657 E.00163
G1 F12000
G1 X59.24 Y6.057 E.01229
G1 X59.24 Y6.585 E.01622
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y6.631 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/58
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
G1 X22.602 Y6.133
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y4.776 E.045
G1 X24.398 Y4.776 E.05957
G1 X24.398 Y6.133 E.045
G1 X22.662 Y6.133 E.05758
G1 X22.21 Y6.525 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y4.396 E.06544
G1 X22.21 Y4.384 E.00034
G1 X24.79 Y4.384 E.07928
G1 X24.79 Y4.396 E.00034
G1 X24.79 Y6.525 E.06543
G1 X22.27 Y6.525 E.07743
; WIPE_START
M204 S10000
G1 X22.214 Y4.526 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.957 Y5.692 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.517695
G1 F13269.443
G1 X23.957 Y5.217 E.01837
G1 X23.043 Y5.217 E.03536
G1 X23.043 Y5.692 E.01837
G1 X23.897 Y5.692 E.03304
; WIPE_START
G1 X23.043 Y5.692 E-.32454
G1 X23.043 Y5.217 E-.18041
G1 X23.714 Y5.217 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.343 Y5.453 Z2.2 F30000
G1 X53.398 Y6.133 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.133 E.05957
G1 X51.602 Y4.776 E.045
G1 X53.398 Y4.776 E.05957
G1 X53.398 Y6.073 E.04301
G1 X53.79 Y6.525 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y6.525 E.07928
G1 X51.21 Y4.396 E.06543
G1 X51.21 Y4.384 E.00034
G1 X53.79 Y4.384 E.07928
G1 X53.79 Y4.396 E.00034
G1 X53.79 Y6.465 E.06359
; WIPE_START
M204 S10000
G1 X51.791 Y6.512 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.043 Y5.692 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51769
G1 F13269.583
G1 X52.957 Y5.692 E.03536
G1 X52.957 Y5.217 E.01837
G1 X52.043 Y5.217 E.03536
G1 X52.043 Y5.632 E.01605
; WIPE_START
G1 X52.043 Y5.217 E-.15762
G1 X52.957 Y5.217 E-.34734
G1 X52.957 Y5.692 E-.18041
G1 X52.761 Y5.692 E-.07463
; WIPE_END
G1 E-.04 F1800
G1 X59.24 Y6.525 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y6.525 E.07928
G1 X56.66 Y5.563 E.02956
G1 X56.66 Y5.536 E.00083
G1 X59.24 Y5.536 E.07928
G1 X59.24 Y5.563 E.00083
G1 X59.24 Y6.465 E.02772
M204 S10000
G1 X59.044 Y6.031 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.63978
G1 F10555.239
G1 X56.856 Y6.031 E.10641
; WIPE_START
G1 X58.856 Y6.031 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.048 Y13.62 Z2.2 F30000
G1 X55.398 Y38.498 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X20.602 Y38.498 E1.15424
G1 X20.602 Y12.067 E.87676
G1 X54.618 Y12.067 E1.12835
G1 X55.018 Y12.067 E.01327
G1 F13999.876
G1 X55.418 Y12.067 E.01327
G1 F6459.938
G1 X55.818 Y12.067 E.01327
G1 F1800
G1 X56.2 Y12.067 E.01269
; FEATURE: Overhang wall
G1 F3000
M204 S5000
G1 X56.25 Y12.067 E.00166
; FEATURE: Inner wall
G1 F1800
M204 S10000
G1 X56.633 Y12.067 E.01269
G1 F6459.938
G1 X57.033 Y12.067 E.01327
G1 F13999.876
G1 X57.433 Y12.067 E.01327
G1 F15476.087
G1 X57.833 Y12.067 E.01327
G1 X58.848 Y12.067 E.03368
G1 X58.848 Y24.221 E.40318
G1 X57.052 Y24.221 E.05957
G1 X57.052 Y13.298 E.36234
G1 X57.052 Y12.898 E.01327
G1 F14442.666
G1 X57.052 Y12.498 E.01327
G1 F6761.824
G1 X56.633 Y12.498 E.01392
G1 F1800
G1 X56.25 Y12.498 E.01269
; FEATURE: Overhang wall
G1 F3000
M204 S5000
G1 X56.2 Y12.498 E.00166
; FEATURE: Inner wall
G1 F1800
M204 S10000
G1 X55.818 Y12.498 E.01269
G1 F6761.668
G1 X55.398 Y12.498 E.01392
G1 F14442.438
G1 X55.398 Y12.898 E.01327
G1 F15476.087
G1 X55.398 Y13.298 E.01327
G1 X55.398 Y38.438 E.83394
G1 X55.79 Y38.89 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.675 E.83625
G1 X55.031 Y11.675 E1.06995
G1 X55.431 Y11.675 E.01229
G1 F6459.938
G1 X55.831 Y11.675 E.01229
G1 F1800
G1 X56.2 Y11.675 E.01134
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
G1 F3000
G1 X56.25 Y11.675 E.00166
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1800
G1 X56.619 Y11.675 E.01134
G1 F6459.938
G1 X57.019 Y11.675 E.01229
G1 F12000
G1 X57.419 Y11.675 E.01229
G1 X59.24 Y11.675 E.05595
G1 X59.24 Y23.631 E.36738
G1 X59.24 Y24.031 E.01229
G1 F9811.683
G1 X59.24 Y24.431 E.01229
G1 F3734.018
G1 X59.24 Y24.613 E.0056
G1 F1920
G1 X56.66 Y24.613 E.07928
G1 F3734.018
G1 X56.66 Y24.431 E.0056
G1 F9811.683
G1 X56.66 Y24.031 E.01229
G1 F12000
G1 X56.66 Y23.631 E.01229
G1 X56.66 Y13.69 E.30546
G1 X56.66 Y13.29 E.01229
G1 F7100.311
G1 X56.66 Y12.89 E.01229
G1 F2145.173
G1 X56.619 Y12.89 E.00126
G1 F1800
G1 X56.25 Y12.89 E.01134
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
G1 F3000
G1 X56.2 Y12.89 E.00166
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1800
G1 X55.831 Y12.89 E.01134
G1 F2145.085
G1 X55.79 Y12.89 E.00126
G1 F7100.151
G1 X55.79 Y13.29 E.01229
G1 F12000
G1 X55.79 Y13.69 E.01229
G1 X55.79 Y38.83 E.77248
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.596 Y31.418 Z2.2 F30000
G1 X57.444 Y23.829 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X58.456 Y23.829 E.03109
G1 X58.456 Y12.459 E.34936
G1 X57.444 Y12.459 E.03109
G1 X57.444 Y23.769 E.34752
G1 X57.791 Y23.482 F30000
; LINE_WIDTH: 0.36025
G1 F15000
G1 X58.109 Y23.482 E.00821
G1 X58.109 Y12.806 E.27606
G1 X57.791 Y12.806 E.00821
G1 X57.791 Y23.422 E.2745
; WIPE_START
G1 X57.791 Y21.422 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.575 Y14.118 Z2.2 F30000
G1 X55.234 Y12.998 Z2.2
G1 Z1.8
G1 E.8 F1800
; LINE_WIDTH: 0.42243
G1 F15000
G1 X54.637 Y12.4 E.02614
G1 X54.1 Y12.4 E.0166
G1 X55.065 Y13.365 E.04219
G1 X55.065 Y13.902 E.0166
G1 X53.563 Y12.4 E.06567
G1 X53.027 Y12.4 E.0166
G1 X55.065 Y14.438 E.08914
G1 X55.065 Y14.975 E.0166
G1 X52.49 Y12.4 E.11261
G1 X51.953 Y12.4 E.0166
G1 X55.065 Y15.512 E.13609
G1 X55.065 Y16.048 E.0166
G1 X51.416 Y12.4 E.15956
G1 X50.88 Y12.4 E.0166
G1 X55.065 Y16.585 E.18303
G1 X55.065 Y17.122 E.0166
G1 X50.343 Y12.4 E.2065
G1 X49.806 Y12.4 E.0166
G1 X55.065 Y17.659 E.22998
G1 X55.065 Y18.195 E.0166
G1 X49.27 Y12.4 E.25345
G1 X48.733 Y12.4 E.0166
G1 X55.065 Y18.732 E.27692
G1 X55.065 Y19.269 E.0166
G1 X48.196 Y12.4 E.3004
G1 X47.66 Y12.4 E.0166
G1 X55.065 Y19.805 E.32387
G1 X55.065 Y20.342 E.0166
G1 X47.123 Y12.4 E.34734
G1 X46.586 Y12.4 E.0166
G1 X55.065 Y20.879 E.37081
G1 X55.065 Y21.416 E.0166
G1 X46.049 Y12.4 E.39429
G1 X45.513 Y12.4 E.0166
G1 X55.065 Y21.952 E.41776
G1 X55.065 Y22.489 E.0166
G1 X44.976 Y12.4 E.44123
G1 X44.439 Y12.4 E.0166
G1 X55.065 Y23.026 E.46471
G1 X55.065 Y23.562 E.0166
G1 X43.903 Y12.4 E.48818
G1 X43.366 Y12.4 E.0166
M73 P67 R5
G1 X55.065 Y24.099 E.51165
G1 X55.065 Y24.636 E.0166
G1 X42.829 Y12.4 E.53513
G1 X42.292 Y12.4 E.0166
G1 X55.065 Y25.172 E.5586
G1 X55.065 Y25.709 E.0166
G1 X41.756 Y12.4 E.58207
G1 X41.219 Y12.4 E.0166
G1 X55.065 Y26.246 E.60554
G1 X55.065 Y26.783 E.0166
G1 X40.682 Y12.4 E.62902
G1 X40.146 Y12.4 E.0166
G1 X55.065 Y27.319 E.65249
G1 X55.065 Y27.856 E.0166
G1 X39.609 Y12.4 E.67596
G1 X39.072 Y12.4 E.0166
G1 X55.065 Y28.393 E.69944
G1 X55.065 Y28.929 E.0166
G1 X38.535 Y12.4 E.72291
G1 X37.999 Y12.4 E.0166
G1 X55.065 Y29.466 E.74638
G1 X55.065 Y30.003 E.0166
G1 X37.462 Y12.4 E.76985
G1 X36.925 Y12.4 E.0166
G1 X55.065 Y30.54 E.79333
G1 X55.065 Y31.076 E.0166
G1 X36.389 Y12.4 E.8168
G1 X35.852 Y12.4 E.0166
G1 X55.065 Y31.613 E.84027
G1 X55.065 Y32.15 E.0166
G1 X35.315 Y12.4 E.86375
G1 X34.779 Y12.4 E.0166
G1 X55.065 Y32.686 E.88722
G1 X55.065 Y33.223 E.0166
G1 X34.242 Y12.4 E.91069
G1 X33.705 Y12.4 E.0166
G1 X55.065 Y33.76 E.93416
G1 X55.065 Y34.297 E.0166
G1 X33.168 Y12.4 E.95764
G1 X32.632 Y12.4 E.0166
G1 X55.065 Y34.833 E.98111
G1 X55.065 Y35.37 E.0166
G1 X32.095 Y12.4 E1.00458
G1 X31.558 Y12.4 E.0166
G1 X55.065 Y35.907 E1.02806
G1 X55.065 Y36.443 E.0166
G1 X31.022 Y12.4 E1.05153
G1 X30.485 Y12.4 E.0166
G1 X55.065 Y36.98 E1.075
G1 X55.065 Y37.517 E.0166
G1 X29.948 Y12.4 E1.09847
G1 X29.411 Y12.4 E.0166
G1 X55.065 Y38.053 E1.12195
G1 X55.065 Y38.165 E.00344
G1 X54.639 Y38.165 E.01316
G1 X28.875 Y12.4 E1.12682
G1 X28.338 Y12.4 E.0166
G1 X54.103 Y38.165 E1.12682
G1 X53.566 Y38.165 E.0166
G1 X27.801 Y12.4 E1.12682
G1 X27.265 Y12.4 E.0166
G1 X53.029 Y38.165 E1.12682
G1 X52.493 Y38.165 E.0166
G1 X26.728 Y12.4 E1.12682
G1 X26.191 Y12.4 E.0166
G1 X51.956 Y38.165 E1.12682
G1 X51.419 Y38.165 E.0166
G1 X25.654 Y12.4 E1.12682
G1 X25.118 Y12.4 E.0166
G1 X50.882 Y38.165 E1.12682
G1 X50.346 Y38.165 E.0166
G1 X24.581 Y12.4 E1.12682
G1 X24.044 Y12.4 E.0166
G1 X49.809 Y38.165 E1.12682
G1 X49.272 Y38.165 E.0166
G1 X23.508 Y12.4 E1.12682
G1 X22.971 Y12.4 E.0166
G1 X48.736 Y38.165 E1.12682
G1 X48.199 Y38.165 E.0166
G1 X22.434 Y12.4 E1.12682
G1 X21.898 Y12.4 E.0166
G1 X47.662 Y38.165 E1.12682
G1 X47.125 Y38.165 E.0166
G1 X21.361 Y12.4 E1.12682
G1 X20.935 Y12.4 E.01316
G1 X20.935 Y12.511 E.00344
G1 X46.589 Y38.165 E1.12196
G1 X46.052 Y38.165 E.0166
G1 X20.935 Y13.048 E1.09848
G1 X20.935 Y13.585 E.0166
G1 X45.515 Y38.165 E1.07501
G1 X44.979 Y38.165 E.0166
G1 X20.935 Y14.121 E1.05154
G1 X20.935 Y14.658 E.0166
G1 X44.442 Y38.165 E1.02806
G1 X43.905 Y38.165 E.0166
G1 X20.935 Y15.195 E1.00459
G1 X20.935 Y15.731 E.0166
G1 X43.369 Y38.165 E.98112
G1 X42.832 Y38.165 E.0166
G1 X20.935 Y16.268 E.95765
G1 X20.935 Y16.805 E.0166
G1 X42.295 Y38.165 E.93417
G1 X41.758 Y38.165 E.0166
G1 X20.935 Y17.342 E.9107
G1 X20.935 Y17.878 E.0166
G1 X41.222 Y38.165 E.88723
G1 X40.685 Y38.165 E.0166
G1 X20.935 Y18.415 E.86375
G1 X20.935 Y18.952 E.0166
G1 X40.148 Y38.165 E.84028
G1 X39.612 Y38.165 E.0166
G1 X20.935 Y19.488 E.81681
G1 X20.935 Y20.025 E.0166
G1 X39.075 Y38.165 E.79334
G1 X38.538 Y38.165 E.0166
G1 X20.935 Y20.562 E.76986
G1 X20.935 Y21.099 E.0166
G1 X38.001 Y38.165 E.74639
G1 X37.465 Y38.165 E.0166
G1 X20.935 Y21.635 E.72292
G1 X20.935 Y22.172 E.0166
G1 X36.928 Y38.165 E.69944
G1 X36.391 Y38.165 E.0166
G1 X20.935 Y22.709 E.67597
G1 X20.935 Y23.245 E.0166
G1 X35.855 Y38.165 E.6525
G1 X35.318 Y38.165 E.0166
G1 X20.935 Y23.782 E.62902
G1 X20.935 Y24.319 E.0166
G1 X34.781 Y38.165 E.60555
G1 X34.244 Y38.165 E.0166
G1 X20.935 Y24.856 E.58208
G1 X20.935 Y25.392 E.0166
G1 X33.708 Y38.165 E.55861
G1 X33.171 Y38.165 E.0166
G1 X20.935 Y25.929 E.53513
G1 X20.935 Y26.466 E.0166
G1 X32.634 Y38.165 E.51166
G1 X32.098 Y38.165 E.0166
G1 X20.935 Y27.002 E.48819
G1 X20.935 Y27.539 E.0166
G1 X31.561 Y38.165 E.46472
G1 X31.024 Y38.165 E.0166
G1 X20.935 Y28.076 E.44124
G1 X20.935 Y28.612 E.0166
G1 X30.488 Y38.165 E.41777
G1 X29.951 Y38.165 E.0166
G1 X20.935 Y29.149 E.3943
G1 X20.935 Y29.686 E.0166
G1 X29.414 Y38.165 E.37082
G1 X28.877 Y38.165 E.0166
G1 X20.935 Y30.223 E.34735
G1 X20.935 Y30.759 E.0166
G1 X28.341 Y38.165 E.32388
G1 X27.804 Y38.165 E.0166
G1 X20.935 Y31.296 E.3004
G1 X20.935 Y31.833 E.0166
G1 X27.267 Y38.165 E.27693
G1 X26.731 Y38.165 E.0166
G1 X20.935 Y32.369 E.25346
G1 X20.935 Y32.906 E.0166
G1 X26.194 Y38.165 E.22999
G1 X25.657 Y38.165 E.0166
G1 X20.935 Y33.443 E.20651
G1 X20.935 Y33.98 E.0166
G1 X25.12 Y38.165 E.18304
G1 X24.584 Y38.165 E.0166
G1 X20.935 Y34.516 E.15957
G1 X20.935 Y35.053 E.0166
G1 X24.047 Y38.165 E.13609
G1 X23.51 Y38.165 E.0166
G1 X20.935 Y35.59 E.11262
G1 X20.935 Y36.126 E.0166
G1 X22.974 Y38.165 E.08915
G1 X22.437 Y38.165 E.0166
G1 X20.935 Y36.663 E.06568
G1 X20.935 Y37.2 E.0166
G1 X21.9 Y38.165 E.0422
G1 X21.363 Y38.165 E.0166
G1 X20.766 Y37.567 E.02615
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.363 Y38.165 E-.32133
G1 X21.9 Y38.165 E-.20395
G1 X21.463 Y37.728 E-.23472
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/58
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
G1 X22.602 Y6.035
M73 P68 R5
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X22.602 Y4.726 E.04341
G1 X24.398 Y4.726 E.05957
G1 X24.398 Y6.035 E.04341
G1 X22.662 Y6.035 E.05758
G1 X22.21 Y6.427 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X22.21 Y4.343 E.06403
G1 X22.21 Y4.334 E.00028
G1 X24.79 Y4.334 E.07928
G1 X24.79 Y4.343 E.00028
G1 X24.79 Y6.427 E.06403
G1 X22.27 Y6.427 E.07743
; WIPE_START
M204 S10000
G1 X22.212 Y4.428 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.969 Y5.606 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49372
G1 F13975.156
G1 X23.969 Y5.155 E.01656
G1 X23.031 Y5.155 E.03446
G1 X23.031 Y5.606 E.01656
G1 X23.909 Y5.606 E.03225
; WIPE_START
G1 X23.031 Y5.606 E-.33364
G1 X23.031 Y5.155 E-.1713
G1 X23.702 Y5.155 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.331 Y5.381 Z2.4 F30000
G1 X53.398 Y6.035 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X51.602 Y6.035 E.05957
G1 X51.602 Y4.726 E.04341
G1 X53.398 Y4.726 E.05957
G1 X53.398 Y5.975 E.04142
G1 X53.79 Y6.427 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X51.21 Y6.427 E.07928
G1 X51.21 Y4.343 E.06403
G1 X51.21 Y4.334 E.00028
G1 X53.79 Y4.334 E.07928
G1 X53.79 Y4.343 E.00028
G1 X53.79 Y6.367 E.06218
; WIPE_START
M204 S10000
G1 X51.791 Y6.414 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.031 Y5.606 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49372
G1 F13975.156
G1 X52.969 Y5.606 E.03446
G1 X52.969 Y5.155 E.01656
G1 X52.031 Y5.155 E.03446
G1 X52.031 Y5.546 E.01436
; WIPE_START
G1 X52.031 Y5.155 E-.1485
G1 X52.969 Y5.155 E-.35644
G1 X52.969 Y5.606 E-.1713
G1 X52.749 Y5.606 E-.08375
; WIPE_END
G1 E-.04 F1800
G1 X59.24 Y6.427 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X56.66 Y6.427 E.07928
G1 X56.66 Y5.495 E.02864
G1 X56.66 Y5.468 E.00083
G1 X59.24 Y5.468 E.07928
G1 X59.24 Y5.495 E.00083
G1 X59.24 Y6.367 E.02679
M204 S10000
G1 X59.044 Y5.948 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.609708
G1 F11115.278
G1 X56.856 Y5.948 E.10105
; WIPE_START
G1 X58.856 Y5.948 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.958 Y11.801 Z2.4 F30000
G1 X52.922 Y13.038 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F15476.087
G1 X52.078 Y13.038 E.02801
G1 X52.078 Y12.165 E.02897
G1 X52.922 Y12.165 E.02801
G1 X52.922 Y12.978 E.02698
; WIPE_START
G1 X52.078 Y13.038 E-.3217
G1 X52.078 Y12.165 E-.33188
G1 X52.358 Y12.165 E-.10642
; WIPE_END
G1 E-.04 F1800
G1 X55.215 Y19.242 Z2.4 F30000
G1 X57.318 Y24.449 Z2.4
G1 Z2
G1 E.8 F1800
G1 F15476.087
G1 X57.318 Y12.165 E.40749
G1 X58.848 Y12.165 E.05076
G1 X58.848 Y24.449 E.40749
G1 X57.378 Y24.449 E.04876
; WIPE_START
G1 X57.368 Y22.449 E-.76
; WIPE_END
G1 E-.04 F1800
G17
G3 Z2.4 I-.49 J-1.114 P1  F30000
G1 X20.922 Y38.498 Z2.4
G1 Z2
G1 E.8 F1800
M73 P68 R4
G1 F15476.087
G1 X20.602 Y38.498 E.01062
G1 X20.602 Y12.165 E.87351
G1 X23.922 Y12.165 E.11014
G1 X23.922 Y13.038 E.02897
G1 X20.922 Y13.038 E.09952
G1 X20.922 Y38.438 E.84255
; WIPE_START
G1 X20.602 Y38.498 E-.12378
G1 X20.602 Y36.824 E-.63622
; WIPE_END
G1 E-.04 F1800
G1 X28.221 Y37.271 Z2.4 F30000
G1 X55.79 Y38.89 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F12000
M204 S5000
G1 X20.21 Y38.89 E1.09327
G1 X20.21 Y11.773 E.83323
G1 X59.24 Y11.773 E1.19928
G1 X59.24 Y23.854 E.37123
G1 X59.24 Y24.254 E.01229
G1 F8596.922
G1 X59.24 Y24.654 E.01229
G1 F3000
G1 X59.24 Y24.841 E.00575
G1 F1800
G1 X56.66 Y24.841 E.07928
G1 F3000
G1 X56.66 Y24.654 E.00575
G1 F8596.922
G1 X56.66 Y24.254 E.01229
G1 F12000
G1 X56.66 Y23.854 E.01229
G1 X56.66 Y12.89 E.3369
G1 X55.79 Y12.89 E.02673
G1 X55.79 Y38.83 E.79706
; WIPE_START
M204 S10000
G1 X53.79 Y38.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.747 Y31.456 Z2.4 F30000
G1 X57.71 Y24.057 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F15000
G1 X58.456 Y24.057 E.02292
G1 X58.456 Y12.557 E.35336
G1 X57.71 Y12.557 E.02292
G1 X57.71 Y23.997 E.35151
G1 X58.083 Y23.684 F30000
; LINE_WIDTH: 0.4118
G1 F15000
G1 X58.083 Y12.99 E.32146
; WIPE_START
G1 X58.083 Y14.99 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X56.382 Y12.094 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.29227
G1 F15000
G1 X57.122 Y12.094 E.01504
G1 X57.01 Y12.597 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38292
G1 F15000
G1 X57.01 Y12.39 E.00574
G1 X56.762 Y12.245 F30000
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F12000
M204 S2000
G1 X56.325 Y12.683 E.01903
G1 X55.791 Y12.683
G1 X56.355 Y12.119 E.02451
; WIPE_START
M204 S10000
G1 X55.791 Y12.683 E-.31083
G1 X56.325 Y12.683 E-.20782
G1 X56.762 Y12.245 E-.24135
; WIPE_END
G1 E-.04 F1800
G17
G3 Z2.4 I-1.214 J-.088 P1  F30000
G1 X54.854 Y38.683 Z2.4
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X55.583 Y37.954 E.03164
G1 X55.583 Y37.421
G1 X54.321 Y38.683 E.05482
G1 X53.788 Y38.683
G1 X55.583 Y36.888 E.07799
G1 X55.583 Y36.355
G1 X53.255 Y38.683 E.10116
G1 X52.721 Y38.683
G1 X55.583 Y35.821 E.12434
G1 X55.583 Y35.288
G1 X52.188 Y38.683 E.14751
G1 X51.655 Y38.683
G1 X55.583 Y34.755 E.17068
G1 X55.583 Y34.222
G1 X51.122 Y38.683 E.19385
G1 X50.588 Y38.683
G1 X55.583 Y33.688 E.21703
G1 X55.583 Y33.155
G1 X50.055 Y38.683 E.2402
G1 X49.522 Y38.683
G1 X55.583 Y32.622 E.26337
G1 X55.583 Y32.089
G1 X48.989 Y38.683 E.28654
G1 X48.455 Y38.683
G1 X55.583 Y31.555 E.30972
G1 X55.583 Y31.022
G1 X47.922 Y38.683 E.33289
G1 X47.389 Y38.683
G1 X55.583 Y30.489 E.35606
G1 X55.583 Y29.956
G1 X46.856 Y38.683 E.37923
G1 X46.322 Y38.683
G1 X55.583 Y29.422 E.40241
G1 X55.583 Y28.889
G1 X45.789 Y38.683 E.42558
G1 X45.256 Y38.683
G1 X55.583 Y28.356 E.44875
G1 X55.583 Y27.823
G1 X44.723 Y38.683 E.47192
G1 X44.189 Y38.683
G1 X55.583 Y27.289 E.4951
G1 X55.583 Y26.756
G1 X43.656 Y38.683 E.51827
G1 X43.123 Y38.683
G1 X55.583 Y26.223 E.54144
G1 X55.583 Y25.689
G1 X42.589 Y38.683 E.56462
G1 X42.056 Y38.683
G1 X55.583 Y25.156 E.58779
G1 X55.583 Y24.623
G1 X41.523 Y38.683 E.61096
G1 X40.99 Y38.683
G1 X55.583 Y24.09 E.63413
G1 X55.583 Y23.556
G1 X40.456 Y38.683 E.65731
G1 X39.923 Y38.683
G1 X55.583 Y23.023 E.68048
G1 X55.583 Y22.49
G1 X39.39 Y38.683 E.70365
G1 X38.857 Y38.683
G1 X55.583 Y21.957 E.72682
G1 X55.583 Y21.423
G1 X38.323 Y38.683 E.75
G1 X37.79 Y38.683
G1 X55.583 Y20.89 E.77317
G1 X55.583 Y20.357
G1 X37.257 Y38.683 E.79634
G1 X36.724 Y38.683
G1 X55.583 Y19.824 E.81951
G1 X55.583 Y19.29
G1 X36.19 Y38.683 E.84269
G1 X35.657 Y38.683
G1 X55.583 Y18.757 E.86586
G1 X55.583 Y18.224
G1 X35.124 Y38.683 E.88903
G1 X34.591 Y38.683
G1 X55.583 Y17.691 E.9122
M73 P69 R4
G1 X55.583 Y17.157
G1 X34.057 Y38.683 E.93538
G1 X33.524 Y38.683
G1 X55.583 Y16.624 E.95855
G1 X55.583 Y16.091
G1 X32.991 Y38.683 E.98172
G1 X32.458 Y38.683
G1 X55.583 Y15.558 E1.00489
G1 X55.583 Y15.024
G1 X31.924 Y38.683 E1.02807
G1 X31.391 Y38.683
G1 X55.583 Y14.491 E1.05124
G1 X55.583 Y13.958
G1 X30.858 Y38.683 E1.07441
G1 X30.325 Y38.683
G1 X55.583 Y13.425 E1.09758
G1 X55.583 Y12.891
G1 X29.791 Y38.683 E1.12076
G1 X29.258 Y38.683
G1 X55.96 Y11.98 E1.16035
G1 X55.427 Y11.98
G1 X28.725 Y38.683 E1.16035
G1 X28.192 Y38.683
G1 X54.894 Y11.98 E1.16035
G1 X54.361 Y11.98
G1 X53.145 Y13.196 E.05284
G1 X53.145 Y12.663
G1 X53.827 Y11.98 E.02966
M204 S10000
G1 X53.08 Y13.261 F30000
G1 F12000
M204 S2000
G1 X27.658 Y38.683 E1.1047
G1 X27.125 Y38.683
G1 X52.547 Y13.261 E1.1047
G1 X52.014 Y13.261
G1 X26.592 Y38.683 E1.1047
G1 X26.058 Y38.683
G1 X51.855 Y12.886 E1.121
G1 X51.855 Y12.353
G1 X25.525 Y38.683 E1.14417
G1 X24.992 Y38.683
G1 X51.694 Y11.98 E1.16035
G1 X51.161 Y11.98
G1 X24.459 Y38.683 E1.16035
G1 X23.925 Y38.683
G1 X50.628 Y11.98 E1.16035
G1 X50.095 Y11.98
G1 X23.392 Y38.683 E1.16035
G1 X22.859 Y38.683
G1 X49.561 Y11.98 E1.16035
G1 X49.028 Y11.98
G1 X22.326 Y38.683 E1.16035
G1 X21.792 Y38.683
G1 X48.495 Y11.98 E1.16035
G1 X47.962 Y11.98
G1 X21.259 Y38.683 E1.16035
G1 X21.145 Y38.264
G1 X47.428 Y11.98 E1.14215
G1 X46.895 Y11.98
G1 X21.145 Y37.731 E1.11897
G1 X21.145 Y37.197
G1 X46.362 Y11.98 E1.0958
G1 X45.828 Y11.98
G1 X21.145 Y36.664 E1.07263
G1 X21.145 Y36.131
G1 X45.295 Y11.98 E1.04946
G1 X44.762 Y11.98
G1 X21.145 Y35.598 E1.02628
G1 X21.145 Y35.064
G1 X44.229 Y11.98 E1.00311
G1 X43.695 Y11.98
G1 X21.145 Y34.531 E.97994
G1 X21.145 Y33.998
G1 X43.162 Y11.98 E.95677
G1 X42.629 Y11.98
G1 X21.145 Y33.464 E.93359
G1 X21.145 Y32.931
G1 X42.096 Y11.98 E.91042
G1 X41.562 Y11.98
G1 X21.145 Y32.398 E.88725
G1 X21.145 Y31.865
G1 X41.029 Y11.98 E.86408
G1 X40.496 Y11.98
G1 X21.145 Y31.331 E.8409
G1 X21.145 Y30.798
G1 X39.963 Y11.98 E.81773
G1 X39.429 Y11.98
G1 X21.145 Y30.265 E.79456
G1 X21.145 Y29.732
G1 X38.896 Y11.98 E.77138
G1 X38.363 Y11.98
G1 X21.145 Y29.198 E.74821
G1 X21.145 Y28.665
G1 X37.83 Y11.98 E.72504
G1 X37.296 Y11.98
G1 X21.145 Y28.132 E.70187
G1 X21.145 Y27.599
G1 X36.763 Y11.98 E.67869
G1 X36.23 Y11.98
G1 X21.145 Y27.065 E.65552
G1 X21.145 Y26.532
G1 X35.697 Y11.98 E.63235
G1 X35.163 Y11.98
G1 X21.145 Y25.999 E.60918
G1 X21.145 Y25.466
G1 X34.63 Y11.98 E.586
G1 X34.097 Y11.98
G1 X21.145 Y24.932 E.56283
G1 X21.145 Y24.399
G1 X33.564 Y11.98 E.53966
G1 X33.03 Y11.98
G1 X21.145 Y23.866 E.51649
G1 X21.145 Y23.333
G1 X32.497 Y11.98 E.49331
M73 P70 R4
G1 X31.964 Y11.98
G1 X21.145 Y22.799 E.47014
G1 X21.145 Y22.266
G1 X31.431 Y11.98 E.44697
G1 X30.897 Y11.98
G1 X21.145 Y21.733 E.4238
G1 X21.145 Y21.2
G1 X30.364 Y11.98 E.40062
G1 X29.831 Y11.98
G1 X21.145 Y20.666 E.37745
G1 X21.145 Y20.133
G1 X29.298 Y11.98 E.35428
G1 X28.764 Y11.98
G1 X21.145 Y19.6 E.33111
G1 X21.145 Y19.067
G1 X28.231 Y11.98 E.30793
G1 X27.698 Y11.98
G1 X21.145 Y18.533 E.28476
G1 X21.145 Y18
G1 X27.164 Y11.98 E.26159
G1 X26.631 Y11.98
G1 X21.145 Y17.467 E.23841
G1 X21.145 Y16.934
G1 X26.098 Y11.98 E.21524
G1 X25.565 Y11.98
G1 X21.145 Y16.4 E.19207
G1 X21.145 Y15.867
G1 X23.703 Y13.309 E.11116
G1 X23.17 Y13.309
G1 X21.145 Y15.334 E.08799
G1 X21.145 Y14.8
G1 X22.636 Y13.309 E.06481
G1 X22.103 Y13.309
G1 X21.145 Y14.267 E.04164
G1 X21.145 Y13.734
G1 X21.57 Y13.309 E.01847
; WIPE_START
M204 S10000
G1 X21.145 Y13.734 E-.22841
G1 X21.145 Y14.267 E-.20264
G1 X21.757 Y13.655 E-.32896
; WIPE_END
G1 E-.04 F1800
G1 X24.193 Y12.819 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F12000
M204 S2000
G1 X25.031 Y11.98 E.03644
G1 X24.498 Y11.98
G1 X24.145 Y12.334 E.01536
; WIPE_START
M204 S10000
G1 X24.498 Y11.98 E-.18994
G1 X25.031 Y11.98 E-.20264
G1 X24.348 Y12.664 E-.36742
; WIPE_END
G1 E-.04 F1800
G1 X31.98 Y12.643 Z2.4 F30000
G1 X55.686 Y12.577 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.122027
G1 F15000
G1 X55.477 Y12.786 E.0019
; WIPE_START
G1 X55.686 Y12.577 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.246 Y13.362 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.126936
G1 F15000
G3 X53.145 Y13.196 I.067 J-.154 E.00141
; WIPE_START
G1 X53.158 Y13.274 E-.29663
G1 X53.246 Y13.362 E-.46337
; WIPE_END
G1 E-.04 F1800
G1 X51.847 Y12.344 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.0972916
G1 F15000
M73 P71 R4
G1 X51.847 Y11.961 E.0017
; WIPE_START
G1 X51.847 Y12.344 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X44.215 Y12.414 Z2.4 F30000
G1 X23.719 Y12.602 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.50919
G1 F13511.484
G1 X20.806 Y12.602 E.11068
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F13511.484
G1 X22.806 Y12.602 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/58
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
G1 X21.398 Y38.298
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6163
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.244 E.86425
G1 X21.742 Y12.244 E.03782
G1 X24.398 Y12.244 E.0881
G1 X24.398 Y13.514 E.04212
G1 X21.398 Y13.514 E.09952
G1 X21.398 Y38.238 E.82014
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6163
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.852 E.82465
G1 X21.742 Y11.852 E.04708
G1 X24.79 Y11.852 E.09365
G1 X24.79 Y13.906 E.06311
G1 X21.79 Y13.906 E.09218
G1 X21.79 Y38.63 E.7597
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6163
G1 X21 Y13.311 E.78521
G1 X23.979 Y13.095 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.47427
G1 F6163
G1 X23.979 Y12.663 E.01516
G1 X21.786 Y12.663 E.07708
; LINE_WIDTH: 0.457317
G1 X21.569 Y12.646 E.00734
; LINE_WIDTH: 0.42341
G1 X21.352 Y12.63 E.00674
; LINE_WIDTH: 0.375726
G2 X20.97 Y12.613 I-.299 J2.431 E.01037
G1 X20.97 Y12.942 E.00894
G1 X21.419 Y12.942 E.01218
; LINE_WIDTH: 0.389504
G1 X21.481 Y12.959 E.00179
; LINE_WIDTH: 0.42341
G1 X21.542 Y12.976 E.00196
; LINE_WIDTH: 0.473833
G1 X21.603 Y12.993 E.00222
G1 X21.632 Y13.095 E.00372
G1 X23.919 Y13.095 E.08031
; WIPE_START
G1 F14620.128
G1 X21.919 Y13.095 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y5.956 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6163
G1 X22.602 Y4.686 E.04212
G1 X24.398 Y4.686 E.05957
G1 X24.398 Y5.956 E.04212
G1 X22.662 Y5.956 E.05758
G1 X22.21 Y6.348 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6163
M204 S5000
G1 X22.21 Y4.294 E.06311
G1 X24.79 Y4.294 E.07928
G1 X24.79 Y6.348 E.06311
G1 X22.27 Y6.348 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.212 Y4.349 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.979 Y5.537 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.47426
G1 F6163
G1 X23.979 Y5.105 E.01516
G1 X23.021 Y5.105 E.03365
G1 X23.021 Y5.537 E.01516
G1 X23.919 Y5.537 E.03154
; WIPE_START
G1 F14605.649
G1 X23.021 Y5.537 E-.34103
G1 X23.021 Y5.105 E-.16391
G1 X23.692 Y5.105 E-.25506
; WIPE_END
G1 E-.04 F1800
G1 X31.32 Y5.372 Z2.6 F30000
G1 X59.24 Y6.348 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6163
M204 S5000
G1 X56.66 Y6.348 E.07928
G1 X56.66 Y5.427 E.02829
G1 X56.66 Y5.419 E.00024
G1 X59.24 Y5.419 E.07928
G1 X59.24 Y5.427 E.00024
G1 X59.24 Y6.288 E.02644
M204 S10000
G1 X59.044 Y5.884 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.57932
G1 F6163
G1 X56.856 Y5.884 E.09563
; WIPE_START
G1 F11744.967
G1 X58.856 Y5.884 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.956 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6163
G1 X51.602 Y5.956 E.05957
G1 X51.602 Y4.686 E.04212
G1 X53.398 Y4.686 E.05957
G1 X53.398 Y5.896 E.04013
G1 X53.79 Y6.348 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6163
M204 S5000
G1 X51.21 Y6.348 E.07928
G1 X51.21 Y4.294 E.06311
G1 X53.79 Y4.294 E.07928
G1 X53.79 Y6.288 E.06127
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.021 Y5.537 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.47426
G1 F6163
G1 X52.979 Y5.537 E.03365
G1 X52.979 Y5.105 E.01516
G1 X52.021 Y5.105 E.03365
G1 X52.021 Y5.477 E.01305
; WIPE_START
G1 F14605.649
G1 X52.021 Y5.105 E-.14111
G1 X52.979 Y5.105 E-.36383
G1 X52.979 Y5.537 E-.16391
G1 X52.739 Y5.537 E-.09115
; WIPE_END
G1 E-.04 F1800
G1 X53.367 Y13.143 Z2.6 F30000
G1 X53.398 Y13.514 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6163
G1 X51.602 Y13.514 E.05957
G1 X51.602 Y12.244 E.04212
G1 X53.398 Y12.244 E.05957
G1 X53.398 Y13.454 E.04013
G1 X53.79 Y13.906 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6163
M204 S5000
G1 X51.21 Y13.906 E.07928
G1 X51.21 Y11.852 E.06311
G1 X53.79 Y11.852 E.07928
G1 X53.79 Y13.846 E.06127
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.893 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.021 Y13.095 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.474265
G1 F6163
G1 X52.979 Y13.095 E.03365
G1 X52.979 Y12.663 E.01516
G1 X52.021 Y12.663 E.03365
G1 X52.021 Y13.035 E.01305
; WIPE_START
G1 F14605.475
G1 X52.021 Y12.663 E-.14111
G1 X52.979 Y12.663 E-.36383
G1 X52.979 Y13.095 E-.16391
G1 X52.739 Y13.095 E-.09114
; WIPE_END
G1 E-.04 F1800
G1 X56.308 Y19.841 Z2.6 F30000
G1 X58.848 Y24.643 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6163
G1 X57.052 Y24.643 E.05957
G1 X57.052 Y12.498 E.40287
G1 X56.102 Y12.498 E.03151
G1 X56.102 Y12.244 E.00842
G1 X58.848 Y12.244 E.09109
G1 X58.848 Y24.583 E.4093
G1 X59.24 Y25.035 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2280
M204 S5000
G1 X56.66 Y25.035 E.07928
G1 F3873.169
G1 X56.66 Y24.882 E.00469
G1 F6163
G1 X56.66 Y24.482 E.01229
G1 X56.66 Y24.082 E.01229
G1 X56.66 Y12.89 E.34391
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.852 E.03189
G1 X59.24 Y11.852 E.10847
G1 X59.24 Y24.482 E.38809
G1 X59.24 Y24.882 E.01229
G1 F5700
G1 X59.24 Y24.975 E.00285
; WIPE_START
M204 S10000
G1 X57.241 Y25.021 E-.76
; WIPE_END
G1 E-.04 F1800
G17
G3 Z2.6 I1.177 J.311 P1  F30000
G1 X57.444 Y24.251 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
M73 P72 R4
G1 F6163
G1 X58.456 Y24.251 E.03109
G1 X58.456 Y12.636 E.35687
G1 X57.444 Y12.636 E.03109
G1 X57.444 Y24.191 E.35503
G1 X57.791 Y23.904 F30000
; LINE_WIDTH: 0.36025
G1 F6163
G1 X58.109 Y23.904 E.00821
G1 X58.109 Y12.983 E.28238
G1 X57.791 Y12.983 E.00821
G1 X57.791 Y23.844 E.28083
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y21.844 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/58
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
G1 X53.398 Y13.544
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6123
G1 X51.602 Y13.544 E.05957
G1 X51.602 Y12.307 E.04103
G1 X53.398 Y12.307 E.05957
G1 X53.398 Y13.484 E.03904
G1 X53.79 Y13.936 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6123
M204 S5000
G1 X51.21 Y13.936 E.07928
G1 X51.21 Y11.915 E.0621
G1 X53.79 Y11.915 E.07928
G1 X53.79 Y13.876 E.06026
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.922 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.013 Y13.133 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45783
G1 F6123
G1 X52.987 Y13.133 E.03293
G1 X52.987 Y12.718 E.01403
G1 X52.013 Y12.718 E.03293
G1 X52.013 Y13.073 E.012
; WIPE_START
G1 F15000
G1 X52.013 Y12.718 E-.13487
G1 X52.987 Y12.718 E-.37009
G1 X52.987 Y13.133 E-.15767
G1 X52.731 Y13.133 E-.09738
; WIPE_END
G1 E-.04 F1800
G1 X56.27 Y19.895 Z2.8 F30000
G1 X58.848 Y24.818 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6123
G1 X57.052 Y24.818 E.05957
G1 X57.052 Y12.307 E.41503
G1 X58.848 Y12.307 E.05957
G1 X58.848 Y24.758 E.41304
G1 X59.24 Y25.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2520
M204 S5000
G1 X56.66 Y25.21 E.07928
G1 F3962.571
G1 X56.66 Y25.076 E.00413
G1 F6123
G1 X56.66 Y24.676 E.01229
G1 X56.66 Y24.276 E.01229
G1 X56.66 Y12.89 E.34986
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.915 E.02997
G1 X59.016 Y11.915 E.10159
G1 X59.24 Y11.915 E.00688
G1 X59.24 Y24.676 E.39212
G1 X59.24 Y25.076 E.01229
G1 X59.24 Y25.15 E.00229
; WIPE_START
G1 F7500
M204 S10000
G1 X57.241 Y25.197 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.426 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6123
G1 X58.456 Y24.426 E.03109
G1 X58.456 Y12.699 E.36034
G1 X57.444 Y12.699 E.03109
G1 X57.444 Y24.366 E.3585
G1 X57.791 Y24.079 F30000
; LINE_WIDTH: 0.36025
G1 F6123
G1 X58.109 Y24.079 E.00821
G1 X58.109 Y13.046 E.28529
G1 X57.791 Y13.046 E.00821
G1 X57.791 Y24.019 E.28374
; WIPE_START
G1 F15000
G1 X57.791 Y22.019 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.491 Y14.419 Z2.8 F30000
G1 X59.24 Y6.285 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6123
M204 S5000
G1 X56.66 Y6.285 E.07928
G1 X56.66 Y5.38 E.02783
G1 X59.24 Y5.38 E.07928
G1 X59.24 Y6.225 E.02599
M204 S10000
G1 X59.044 Y5.832 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.556592
G1 F6123
G1 X56.856 Y5.832 E.09158
; WIPE_START
G1 F12264.656
G1 X58.856 Y5.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.893 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6123
G1 X51.602 Y5.893 E.05957
G1 X51.602 Y4.656 E.04103
G1 X53.398 Y4.656 E.05957
G1 X53.398 Y5.833 E.03904
G1 X53.79 Y6.285 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6123
M204 S5000
G1 X51.21 Y6.285 E.07928
G1 X51.21 Y4.264 E.0621
G1 X53.79 Y4.264 E.07928
G1 X53.79 Y6.225 E.06026
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.272 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.013 Y5.482 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.457835
G1 F6123
G1 X52.987 Y5.482 E.03293
G1 X52.987 Y5.067 E.01403
G1 X52.013 Y5.067 E.03293
G1 X52.013 Y5.422 E.012
; WIPE_START
G1 F15000
G1 X52.013 Y5.067 E-.13487
G1 X52.987 Y5.067 E-.37008
G1 X52.987 Y5.482 E-.15767
G1 X52.731 Y5.482 E-.09738
; WIPE_END
G1 E-.04 F1800
G1 X45.099 Y5.586 Z2.8 F30000
G1 X22.602 Y5.893 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6123
G1 X22.602 Y4.656 E.04103
G1 X24.398 Y4.656 E.05957
G1 X24.398 Y5.893 E.04103
G1 X22.662 Y5.893 E.05758
G1 X22.21 Y6.285 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6123
M204 S5000
G1 X22.21 Y4.264 E.0621
G1 X24.79 Y4.264 E.07928
G1 X24.79 Y6.285 E.0621
G1 X22.27 Y6.285 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.211 Y4.286 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.987 Y5.482 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45785
G1 F6123
G1 X23.987 Y5.067 E.01403
G1 X23.013 Y5.067 E.03293
G1 X23.013 Y5.482 E.01403
G1 X23.927 Y5.482 E.0309
; WIPE_START
G1 F15000
G1 X23.013 Y5.482 E-.34728
G1 X23.013 Y5.067 E-.15767
G1 X23.684 Y5.067 E-.25504
; WIPE_END
G1 E-.04 F1800
G1 X23.16 Y12.682 Z2.8 F30000
G1 X21.398 Y38.298 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6123
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.307 E.86217
G1 X21.581 Y12.307 E.03248
G1 X24.398 Y12.307 E.09344
G1 X24.398 Y13.544 E.04103
G1 X21.398 Y13.544 E.09952
G1 X21.398 Y38.238 E.81915
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6123
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.915 E.82273
G1 X21.581 Y11.915 E.04213
G1 X24.79 Y11.915 E.0986
G1 X24.79 Y13.936 E.0621
G1 X21.79 Y13.936 E.09218
G1 X21.79 Y38.63 E.75879
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6123
G1 X21 Y13.34 E.78427
G1 X23.987 Y13.133 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45783
G1 F6123
G1 X23.987 Y12.718 E.01403
G1 X21.776 Y12.718 E.07474
; LINE_WIDTH: 0.440877
G1 X21.557 Y12.701 E.00713
; LINE_WIDTH: 0.40697
G1 X21.338 Y12.684 E.00652
; LINE_WIDTH: 0.35936
G2 X20.962 Y12.667 I-.298 J2.423 E.00971
G1 X20.962 Y12.98 E.00808
G1 X21.419 Y12.98 E.01179
; LINE_WIDTH: 0.373064
G1 X21.479 Y12.997 E.00166
; LINE_WIDTH: 0.40697
G1 X21.538 Y13.014 E.00184
; LINE_WIDTH: 0.457406
G1 X21.598 Y13.031 E.00209
G1 X21.626 Y13.133 E.00356
G1 X23.927 Y13.133 E.07772
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.927 Y13.133 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/58
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
G1 X53.398 Y13.573
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6204
G1 X51.602 Y13.573 E.05957
G1 X51.602 Y12.354 E.04044
G1 X53.398 Y12.354 E.05957
G1 X53.398 Y13.513 E.03845
G1 X53.79 Y13.965 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6204
M204 S5000
G1 X51.21 Y13.965 E.07928
G1 X51.21 Y11.962 E.06156
G1 X53.79 Y11.962 E.07928
G1 X53.79 Y13.905 E.05971
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.952 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.009 Y13.167 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.448975
G1 F6204
G1 X52.991 Y13.167 E.03252
G1 X52.991 Y12.761 E.01344
G1 X52.009 Y12.761 E.03252
G1 X52.009 Y13.107 E.01145
; WIPE_START
G1 F15000
G1 X52.009 Y12.761 E-.1315
G1 X52.991 Y12.761 E-.37345
G1 X52.991 Y13.167 E-.1543
G1 X52.726 Y13.167 E-.10075
; WIPE_END
G1 E-.04 F1800
G1 X56.235 Y19.945 Z3 F30000
G1 X58.848 Y24.994 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6204
G1 X57.052 Y24.994 E.05957
G1 X57.052 Y12.354 E.41928
G1 X58.683 Y12.354 E.05409
G1 X58.848 Y12.354 E.00548
G1 X58.848 Y24.934 E.41729
G1 X59.24 Y25.386 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2520
M204 S5000
G1 X56.66 Y25.386 E.07928
G1 F3962.571
G1 X56.66 Y25.251 E.00413
G1 F6204
G1 X56.66 Y24.851 E.01229
G1 X56.66 Y24.451 E.01229
G1 X56.66 Y12.89 E.35525
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.962 E.02851
G1 X58.683 Y11.962 E.09134
G1 X59.24 Y11.962 E.01713
G1 X59.24 Y24.851 E.39605
G1 X59.24 Y25.251 E.01229
G1 X59.24 Y25.326 E.00229
; WIPE_START
G1 F7500
M204 S10000
G1 X57.241 Y25.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.602 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6204
G1 X58.456 Y24.602 E.03109
G1 X58.456 Y12.746 E.36427
G1 X57.444 Y12.746 E.03109
G1 X57.444 Y24.542 E.36243
G1 X57.791 Y24.254 F30000
; LINE_WIDTH: 0.36025
G1 F6204
G1 X58.109 Y24.254 E.00821
G1 X58.109 Y13.093 E.28861
G1 X57.791 Y13.093 E.00821
G1 X57.791 Y24.194 E.28705
; WIPE_START
G1 F15000
G1 X57.791 Y22.194 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.481 Y14.593 Z3 F30000
G1 X59.24 Y6.238 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6204
M204 S5000
G1 X56.66 Y6.238 E.07928
G1 X56.66 Y5.343 E.02751
G1 X59.24 Y5.343 E.07928
G1 X59.24 Y6.178 E.02566
M204 S10000
G1 X59.044 Y5.79 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.546046
G1 F6204
G1 X56.856 Y5.79 E.0897
; WIPE_START
G1 F12521.721
G1 X58.856 Y5.79 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.846 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6204
G1 X51.602 Y5.846 E.05957
G1 X51.602 Y4.627 E.04044
G1 X53.398 Y4.627 E.05957
G1 X53.398 Y5.786 E.03845
G1 X53.79 Y6.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6204
M204 S5000
G1 X51.21 Y6.238 E.07928
G1 X51.21 Y4.235 E.06156
G1 X53.79 Y4.235 E.07928
G1 X53.79 Y6.178 E.05971
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.224 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.009 Y5.439 Z3 F30000
G1 Z2.6
M73 P73 R4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.44897
G1 F6204
G1 X52.991 Y5.439 E.03252
G1 X52.991 Y5.033 E.01344
G1 X52.009 Y5.033 E.03252
G1 X52.009 Y5.379 E.01145
; WIPE_START
G1 F15000
G1 X52.009 Y5.033 E-.1315
G1 X52.991 Y5.033 E-.37345
G1 X52.991 Y5.439 E-.1543
G1 X52.726 Y5.439 E-.10074
; WIPE_END
G1 E-.04 F1800
G1 X45.095 Y5.542 Z3 F30000
G1 X22.602 Y5.846 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6204
G1 X22.602 Y4.627 E.04044
G1 X24.398 Y4.627 E.05957
G1 X24.398 Y5.846 E.04044
G1 X22.662 Y5.846 E.05758
G1 X22.21 Y6.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6204
M204 S5000
G1 X22.21 Y4.235 E.06156
G1 X24.79 Y4.235 E.07928
G1 X24.79 Y6.238 E.06156
G1 X22.27 Y6.238 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.239 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.991 Y5.439 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.44897
G1 F6204
G1 X23.991 Y5.033 E.01344
G1 X23.009 Y5.033 E.03252
G1 X23.009 Y5.439 E.01344
G1 X23.931 Y5.439 E.03053
; WIPE_START
G1 F15000
G1 X23.009 Y5.439 E-.35065
G1 X23.009 Y5.033 E-.1543
G1 X23.68 Y5.033 E-.25504
; WIPE_END
G1 E-.04 F1800
G1 X23.157 Y12.648 Z3 F30000
G1 X21.398 Y38.298 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6204
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.354 E.8606
G1 X24.398 Y12.354 E.12592
G1 X24.398 Y13.573 E.04044
G1 X21.398 Y13.573 E.09952
G1 X21.398 Y38.238 E.81817
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6204
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.962 E.82128
G1 X24.79 Y11.962 E.14073
G1 X24.79 Y13.965 E.06156
G1 X21.79 Y13.965 E.09218
G1 X21.79 Y38.63 E.75788
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6204
G1 X21 Y13.37 E.78333
G1 X21.11 Y12.862 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.65162
G1 F6204
G1 X21.21 Y12.862 E.00498
G1 X23.991 Y13.167 F30000
; LINE_WIDTH: 0.448985
G1 F6204
G1 X23.991 Y12.761 E.01344
G1 X21.771 Y12.761 E.07346
; LINE_WIDTH: 0.431568
G1 X21.716 Y12.753 E.00177
; LINE_WIDTH: 0.396723
G1 X21.66 Y12.745 E.00162
; LINE_WIDTH: 0.401994
G1 X21.595 Y12.764 E.00199
; LINE_WIDTH: 0.44738
G1 X21.53 Y12.784 E.00224
; LINE_WIDTH: 0.492767
G1 X21.465 Y12.803 E.00249
; LINE_WIDTH: 0.538154
G1 X21.4 Y12.823 E.00274
; LINE_WIDTH: 0.58354
G1 X21.335 Y12.842 E.00299
; LINE_WIDTH: 0.628927
G1 X21.27 Y12.862 E.00324
; LINE_WIDTH: 0.632707
G1 X21.32 Y12.881 E.00256
; LINE_WIDTH: 0.59488
G1 X21.37 Y12.9 E.00239
; LINE_WIDTH: 0.557054
G1 X21.419 Y12.919 E.00223
; LINE_WIDTH: 0.515853
G1 X21.507 Y12.992 E.00441
; LINE_WIDTH: 0.449995
G3 X21.623 Y13.166 I-.066 J.169 E.00739
G2 X23.931 Y13.167 I1.228 J-417.942 E.07657
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.931 Y13.166 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/58
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
G1 X53.398 Y13.583
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6183
G1 X51.602 Y13.583 E.05957
G1 X51.602 Y12.384 E.03979
G1 X53.398 Y12.384 E.05957
G1 X53.398 Y13.523 E.03779
G1 X53.79 Y13.975 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6183
M204 S5000
G1 X51.21 Y13.975 E.07928
G1 X51.21 Y11.992 E.06095
G1 X53.79 Y11.992 E.07928
G1 X53.79 Y13.915 E.0591
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.962 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.004 Y13.182 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.439075
G1 F6183
G1 X52.996 Y13.182 E.03204
G1 X52.996 Y12.785 E.01279
G1 X52.004 Y12.785 E.03204
G1 X52.004 Y13.122 E.01085
; WIPE_START
G1 F15000
G1 X52.004 Y12.785 E-.12774
G1 X52.996 Y12.785 E-.37721
G1 X52.996 Y13.182 E-.15054
G1 X52.721 Y13.182 E-.10451
; WIPE_END
G1 E-.04 F1800
G1 X56.203 Y19.974 Z3.2 F30000
G1 X58.848 Y25.134 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6183
G1 X57.052 Y25.134 E.05957
G1 X57.052 Y12.384 E.42293
G1 X58.848 Y12.384 E.05957
G1 X58.848 Y25.074 E.42094
G1 X59.24 Y25.526 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3000
M204 S5000
G1 X56.66 Y25.526 E.07928
G1 F4116.195
G1 X56.66 Y25.427 E.00304
G1 F6183
G1 X56.66 Y25.027 E.01229
G1 X56.66 Y24.627 E.01229
G1 X56.66 Y12.89 E.36064
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.992 E.0276
G1 X58.943 Y11.992 E.09935
G1 X59.24 Y11.992 E.00912
G1 X59.24 Y25.027 E.40053
G1 X59.24 Y25.427 E.01229
G1 X59.24 Y25.466 E.0012
; WIPE_START
G1 F10200
M204 S10000
G1 X57.241 Y25.512 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.741 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6183
G1 X58.456 Y24.741 E.03109
G1 X58.456 Y12.776 E.36766
G1 X57.444 Y12.776 E.03109
G1 X57.444 Y24.681 E.36582
G1 X57.791 Y24.394 F30000
; LINE_WIDTH: 0.36025
G1 F6183
G1 X58.109 Y24.394 E.00821
G1 X58.109 Y13.123 E.29146
G1 X57.791 Y13.123 E.00821
G1 X57.791 Y24.334 E.2899
; WIPE_START
G1 F15000
G1 X57.791 Y22.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.474 Y14.732 Z3.2 F30000
G1 X59.24 Y6.208 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6183
M204 S5000
G1 X56.66 Y6.208 E.07928
G1 X56.66 Y5.33 E.027
G1 X59.24 Y5.33 E.07928
G1 X59.24 Y6.148 E.02515
M204 S10000
G1 X59.044 Y5.769 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.529471
G1 F6183
G1 X56.856 Y5.769 E.08675
; WIPE_START
G1 F12948.28
G1 X58.856 Y5.769 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.816 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6183
G1 X51.602 Y5.816 E.05957
G1 X51.602 Y4.617 E.03978
G1 X53.398 Y4.617 E.05957
G1 X53.398 Y5.756 E.03779
G1 X53.79 Y6.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6183
M204 S5000
G1 X51.21 Y6.208 E.07928
G1 X51.21 Y4.225 E.06095
G1 X53.79 Y4.225 E.07928
G1 X53.79 Y6.148 E.0591
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.004 Y5.415 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43907
G1 F6183
G1 X52.996 Y5.415 E.03204
G1 X52.996 Y5.018 E.01279
G1 X52.004 Y5.018 E.03204
G1 X52.004 Y5.355 E.01085
; WIPE_START
G1 F15000
G1 X52.004 Y5.018 E-.12774
G1 X52.996 Y5.018 E-.37721
G1 X52.996 Y5.415 E-.15054
G1 X52.721 Y5.415 E-.1045
; WIPE_END
G1 E-.04 F1800
G1 X45.09 Y5.516 Z3.2 F30000
G1 X22.602 Y5.816 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6183
G1 X22.602 Y4.617 E.03978
G1 X24.398 Y4.617 E.05957
G1 X24.398 Y5.816 E.03978
G1 X22.662 Y5.816 E.05758
G1 X22.21 Y6.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6183
M204 S5000
G1 X22.21 Y4.225 E.06095
G1 X24.79 Y4.225 E.07928
G1 X24.79 Y6.208 E.06095
G1 X22.27 Y6.208 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.225 E-.75407
G1 X22.226 Y4.225 E-.00593
; WIPE_END
G1 E-.04 F1800
G1 X23.996 Y5.415 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43907
G1 F6183
G1 X23.996 Y5.018 E.01279
G1 X23.004 Y5.018 E.03204
G1 X23.004 Y5.415 E.01279
G1 X23.936 Y5.415 E.03011
; WIPE_START
G1 F15000
G1 X23.004 Y5.415 E-.35441
G1 X23.004 Y5.018 E-.15054
G1 X23.675 Y5.018 E-.25504
; WIPE_END
G1 E-.04 F1800
G1 X23.154 Y12.633 Z3.2 F30000
G1 X21.398 Y38.298 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6183
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.384 E.85962
G1 X24.398 Y12.384 E.12592
G1 X24.398 Y13.583 E.03979
G1 X21.398 Y13.583 E.09952
G1 X21.398 Y38.238 E.81784
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6183
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.992 E.82036
G1 X24.79 Y11.992 E.14073
G1 X24.79 Y13.975 E.06095
G1 X21.79 Y13.975 E.09218
G1 X21.79 Y38.63 E.75757
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6183
G1 X21 Y13.38 E.78302
G1 X21.1 Y12.882 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63178
G1 F6183
G1 X21.245 Y12.882 E.00698
G1 X23.996 Y13.182 F30000
; LINE_WIDTH: 0.43907
G1 F6183
G1 X23.996 Y12.785 E.01279
G1 X21.766 Y12.785 E.07201
; LINE_WIDTH: 0.457202
G1 X21.65 Y12.804 E.00394
; LINE_WIDTH: 0.493465
G1 X21.535 Y12.822 E.00429
; LINE_WIDTH: 0.529729
G1 X21.419 Y12.84 E.00463
; LINE_WIDTH: 0.56884
G1 X21.362 Y12.861 E.0026
; LINE_WIDTH: 0.596814
G1 X21.305 Y12.882 E.00274
G1 X21.419 Y12.924 E.00548
; LINE_WIDTH: 0.529729
G1 X21.477 Y12.976 E.00308
; LINE_WIDTH: 0.493465
G1 X21.535 Y13.028 E.00285
; LINE_WIDTH: 0.439634
G3 X21.623 Y13.182 I-.082 J.149 E.00602
G1 X23.936 Y13.182 E.07479
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.936 Y13.182 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/58
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
G1 X53.398 Y13.593
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6198
G1 X51.602 Y13.593 E.05957
G1 X51.602 Y12.397 E.03967
G1 X53.398 Y12.397 E.05957
G1 X53.398 Y13.533 E.03768
G1 X53.79 Y13.985 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6198
M204 S5000
G1 X51.21 Y13.985 E.07928
G1 X51.21 Y12.005 E.06084
G1 X53.79 Y12.005 E.07928
G1 X53.79 Y13.925 E.059
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.972 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.003 Y13.192 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43731
G1 F6198
G1 X52.997 Y13.192 E.03196
G1 X52.997 Y12.798 E.01268
G1 X52.003 Y12.798 E.03196
G1 X52.003 Y13.132 E.01075
; WIPE_START
G1 F15000
G1 X52.003 Y12.798 E-.12707
G1 X52.997 Y12.798 E-.37788
G1 X52.997 Y13.192 E-.14987
G1 X52.72 Y13.192 E-.10518
; WIPE_END
G1 E-.04 F1800
G1 X56.174 Y19.999 Z3.4 F30000
G1 X58.848 Y25.267 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6198
G1 X57.052 Y25.267 E.05957
G1 X57.052 Y12.397 E.42692
G1 X58.848 Y12.397 E.05957
G1 X58.848 Y25.207 E.42493
G1 X59.24 Y25.659 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3000
M204 S5000
G1 X56.66 Y25.659 E.07928
G1 F4040.103
M73 P74 R4
G1 X56.66 Y25.567 E.00285
G1 F6198
G1 X56.66 Y25.167 E.01229
G1 X56.66 Y24.767 E.01229
G1 X56.66 Y12.89 E.36494
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y12.005 E.02719
G1 X59.055 Y12.005 E.10279
G1 X59.24 Y12.005 E.00567
G1 X59.24 Y25.167 E.40442
G1 X59.24 Y25.567 E.01229
G1 X59.24 Y25.599 E.001
; WIPE_START
G1 F11100
M204 S10000
G1 X57.241 Y25.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.875 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6198
G1 X58.456 Y24.875 E.03109
G1 X58.456 Y12.789 E.37136
G1 X57.444 Y12.789 E.03109
G1 X57.444 Y24.815 E.36951
G1 X57.791 Y24.528 F30000
; LINE_WIDTH: 0.36025
G1 F6198
G1 X58.109 Y24.528 E.00821
G1 X58.109 Y13.136 E.29457
G1 X57.791 Y13.136 E.00821
G1 X57.791 Y24.468 E.29301
; WIPE_START
G1 F15000
G1 X57.791 Y22.468 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.468 Y14.866 Z3.4 F30000
G1 X59.24 Y6.195 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6198
M204 S5000
G1 X56.66 Y6.195 E.07928
G1 X56.66 Y5.317 E.02699
G1 X59.24 Y5.317 E.07928
G1 X59.24 Y6.135 E.02515
M204 S10000
G1 X59.044 Y5.756 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.529233
G1 F6198
G1 X56.856 Y5.756 E.0867
; WIPE_START
G1 F12954.641
G1 X58.856 Y5.756 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.803 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6198
G1 X51.602 Y5.803 E.05957
G1 X51.602 Y4.607 E.03967
G1 X53.398 Y4.607 E.05957
G1 X53.398 Y5.743 E.03768
G1 X53.79 Y6.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6198
M204 S5000
G1 X51.21 Y6.195 E.07928
G1 X51.21 Y4.215 E.06084
G1 X53.79 Y4.215 E.07928
G1 X53.79 Y6.135 E.059
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.181 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.003 Y5.402 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43732
G1 F6198
G1 X52.997 Y5.402 E.03196
G1 X52.997 Y5.008 E.01268
G1 X52.003 Y5.008 E.03196
G1 X52.003 Y5.342 E.01075
; WIPE_START
G1 F15000
G1 X52.003 Y5.008 E-.12707
G1 X52.997 Y5.008 E-.37788
G1 X52.997 Y5.402 E-.14987
G1 X52.72 Y5.402 E-.10518
; WIPE_END
G1 E-.04 F1800
G1 X45.089 Y5.504 Z3.4 F30000
G1 X22.602 Y5.803 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6198
G1 X22.602 Y4.607 E.03967
G1 X24.398 Y4.607 E.05957
G1 X24.398 Y5.803 E.03967
G1 X22.662 Y5.803 E.05758
G1 X22.21 Y6.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6198
M204 S5000
G1 X22.21 Y4.215 E.06084
G1 X24.79 Y4.215 E.07928
G1 X24.79 Y6.195 E.06084
G1 X22.27 Y6.195 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.215 E-.75275
G1 X22.229 Y4.215 E-.00726
; WIPE_END
G1 E-.04 F1800
G1 X23.997 Y5.402 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43732
G1 F6198
G1 X23.997 Y5.008 E.01268
G1 X23.003 Y5.008 E.03196
G1 X23.003 Y5.402 E.01268
G1 X23.937 Y5.402 E.03003
; WIPE_START
G1 F15000
G1 X23.003 Y5.402 E-.35508
G1 X23.003 Y5.008 E-.14987
G1 X23.674 Y5.008 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X23.153 Y12.622 Z3.4 F30000
G1 X21.398 Y38.298 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6198
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.397 E.85918
G1 X24.079 Y12.397 E.11534
G1 X24.398 Y12.397 E.01057
G1 X24.398 Y13.593 E.03967
G1 X21.398 Y13.593 E.09952
G1 X21.398 Y38.238 E.81752
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6198
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.005 E.81995
G1 X24.079 Y12.005 E.11889
G1 X24.79 Y12.005 E.02184
G1 X24.79 Y13.985 E.06084
G1 X21.79 Y13.985 E.09218
G1 X21.79 Y38.63 E.75727
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6198
G1 X21 Y13.39 E.78271
G1 X21.098 Y12.893 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.62828
G1 F6198
G1 X21.252 Y12.893 E.00731
G1 X23.997 Y13.192 F30000
; LINE_WIDTH: 0.437315
G1 F6198
G1 X23.997 Y12.798 E.01268
G1 X21.765 Y12.798 E.07175
; LINE_WIDTH: 0.455985
G1 X21.65 Y12.817 E.00392
; LINE_WIDTH: 0.493315
G1 X21.535 Y12.835 E.00428
; LINE_WIDTH: 0.530645
G1 X21.419 Y12.854 E.00463
; LINE_WIDTH: 0.569053
G1 X21.366 Y12.874 E.00246
; LINE_WIDTH: 0.595376
G1 X21.312 Y12.893 E.00259
G1 X21.419 Y12.933 E.00517
; LINE_WIDTH: 0.530645
G1 X21.477 Y12.985 E.0031
; LINE_WIDTH: 0.493315
G1 X21.535 Y13.038 E.00286
; LINE_WIDTH: 0.437898
G3 X21.623 Y13.192 I-.086 J.152 E.00601
G1 X23.937 Y13.192 E.07449
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.937 Y13.192 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/58
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
G1 X53.398 Y13.593
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6219
G1 X51.602 Y13.593 E.05957
G1 X51.602 Y12.397 E.03967
G1 X53.398 Y12.397 E.05957
G1 X53.398 Y13.533 E.03768
G1 X53.79 Y13.985 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6219
M204 S5000
G1 X51.21 Y13.985 E.07928
G1 X51.21 Y12.005 E.06084
G1 X53.79 Y12.005 E.07928
G1 X53.79 Y13.925 E.059
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.972 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.003 Y13.192 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4373
G1 F6219
G1 X52.997 Y13.192 E.03196
G1 X52.997 Y12.798 E.01267
G1 X52.003 Y12.798 E.03196
G1 X52.003 Y13.132 E.01075
; WIPE_START
G1 F15000
G1 X52.003 Y12.798 E-.12706
G1 X52.997 Y12.798 E-.37788
G1 X52.997 Y13.192 E-.14986
G1 X52.72 Y13.192 E-.10519
; WIPE_END
G1 E-.04 F1800
G1 X56.144 Y20.014 Z3.6 F30000
G1 X58.848 Y25.401 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6219
G1 X57.052 Y25.401 E.05957
G1 X57.052 Y12.397 E.43136
G1 X58.848 Y12.397 E.05957
G1 X58.848 Y25.341 E.42937
G1 X59.24 Y25.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3000
M204 S5000
G1 X56.66 Y25.793 E.07928
G1 F4039.983
G1 X56.66 Y25.7 E.00285
G1 F6219
G1 X56.66 Y25.3 E.01229
G1 X56.66 Y24.9 E.01229
G1 X56.66 Y12.89 E.36904
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y12.005 E.02719
G1 X59 Y12.005 E.10111
G1 X59.24 Y12.005 E.00736
G1 X59.24 Y25.3 E.40852
G1 X59.24 Y25.7 E.01229
G1 X59.24 Y25.733 E.001
; WIPE_START
G1 F11100
M204 S10000
G1 X57.241 Y25.779 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y25.009 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6219
G1 X58.456 Y25.009 E.03109
G1 X58.456 Y12.789 E.37546
G1 X57.444 Y12.789 E.03109
G1 X57.444 Y24.949 E.37362
G1 X57.791 Y24.662 F30000
; LINE_WIDTH: 0.36026
G1 F6219
G1 X58.109 Y24.662 E.00821
G1 X58.109 Y13.136 E.29803
G1 X57.791 Y13.136 E.00821
G1 X57.791 Y24.602 E.29648
; WIPE_START
G1 F15000
G1 X57.791 Y22.602 E-.76
; WIPE_END
G1 E-.04 F1800
M73 P74 R3
G1 X58.463 Y14.999 Z3.6 F30000
G1 X59.24 Y6.195 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6219
M204 S5000
G1 X56.66 Y6.195 E.07928
G1 X56.66 Y5.317 E.02699
G1 X59.24 Y5.317 E.07928
G1 X59.24 Y6.135 E.02515
M204 S10000
G1 X59.044 Y5.756 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.529256
G1 F6219
G1 X56.856 Y5.756 E.08671
; WIPE_START
G1 F12954.019
G1 X58.856 Y5.756 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.803 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6219
G1 X51.602 Y5.803 E.05957
G1 X51.602 Y4.607 E.03967
G1 X53.398 Y4.607 E.05957
G1 X53.398 Y5.743 E.03768
G1 X53.79 Y6.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6219
M204 S5000
G1 X51.21 Y6.195 E.07928
G1 X51.21 Y4.215 E.06084
G1 X53.79 Y4.215 E.07928
G1 X53.79 Y6.135 E.059
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.181 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.003 Y5.402 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43732
G1 F6219
G1 X52.997 Y5.402 E.03196
G1 X52.997 Y5.008 E.01268
G1 X52.003 Y5.008 E.03196
G1 X52.003 Y5.342 E.01075
; WIPE_START
G1 F15000
G1 X52.003 Y5.008 E-.12707
G1 X52.997 Y5.008 E-.37788
G1 X52.997 Y5.402 E-.14987
G1 X52.72 Y5.402 E-.10518
; WIPE_END
G1 E-.04 F1800
G1 X45.089 Y5.504 Z3.6 F30000
G1 X22.602 Y5.803 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6219
G1 X22.602 Y4.607 E.03967
G1 X24.398 Y4.607 E.05957
G1 X24.398 Y5.803 E.03967
G1 X22.662 Y5.803 E.05758
G1 X22.21 Y6.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6219
M204 S5000
G1 X22.21 Y4.215 E.06084
G1 X24.79 Y4.215 E.07928
G1 X24.79 Y6.195 E.06084
G1 X22.27 Y6.195 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.215 E-.75276
G1 X22.229 Y4.215 E-.00725
; WIPE_END
G1 E-.04 F1800
G1 X23.997 Y5.402 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.437335
G1 F6219
G1 X23.997 Y5.008 E.01268
M73 P75 R3
G1 X23.003 Y5.008 E.03196
G1 X23.003 Y5.402 E.01268
G1 X23.937 Y5.402 E.03003
; WIPE_START
G1 F15000
G1 X23.003 Y5.402 E-.35508
G1 X23.003 Y5.008 E-.14988
G1 X23.674 Y5.008 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X23.153 Y12.622 Z3.6 F30000
G1 X21.398 Y38.298 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6219
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.397 E.85918
G1 X24.398 Y12.397 E.12592
G1 X24.398 Y13.593 E.03967
G1 X21.398 Y13.593 E.09952
G1 X21.398 Y38.238 E.81752
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6219
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.005 E.81995
G1 X24.79 Y12.005 E.14073
G1 X24.79 Y13.985 E.06084
G1 X21.79 Y13.985 E.09218
G1 X21.79 Y38.63 E.75727
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6219
G1 X21 Y13.39 E.78271
G1 X21.098 Y12.893 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.62828
G1 F6219
G1 X21.252 Y12.893 E.00731
G1 X23.997 Y13.192 F30000
; LINE_WIDTH: 0.437315
G1 F6219
G1 X23.997 Y12.798 E.01267
G1 X21.765 Y12.798 E.07175
; LINE_WIDTH: 0.455985
G1 X21.65 Y12.817 E.00392
; LINE_WIDTH: 0.493315
G1 X21.535 Y12.835 E.00428
; LINE_WIDTH: 0.530645
G1 X21.419 Y12.854 E.00463
; LINE_WIDTH: 0.569053
G1 X21.366 Y12.874 E.00246
; LINE_WIDTH: 0.595376
G1 X21.312 Y12.893 E.00259
G1 X21.419 Y12.933 E.00517
; LINE_WIDTH: 0.530645
G1 X21.477 Y12.985 E.0031
; LINE_WIDTH: 0.493315
G1 X21.535 Y13.038 E.00286
; LINE_WIDTH: 0.437898
G3 X21.623 Y13.192 I-.086 J.152 E.00601
G1 X23.937 Y13.192 E.07449
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X21.937 Y13.192 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/58
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
G1 X21.398 Y38.298
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6407
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.384 E.85962
G1 X23.116 Y12.384 E.08338
G1 X24.398 Y12.384 E.04254
G1 X24.398 Y13.583 E.03978
G1 X21.398 Y13.583 E.09952
G1 X21.398 Y38.238 E.81784
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.992 E.82036
G1 X23.116 Y11.992 E.08928
G1 X24.79 Y11.992 E.05145
G1 X24.79 Y13.975 E.06095
G1 X21.79 Y13.975 E.09218
G1 X21.79 Y38.63 E.75757
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6407
G1 X21 Y13.38 E.78302
G1 X21.1 Y12.882 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63178
G1 F6407
G1 X21.245 Y12.882 E.00698
G1 X23.996 Y13.182 F30000
; LINE_WIDTH: 0.43907
G1 F6407
G1 X23.996 Y12.785 E.01279
G1 X21.766 Y12.785 E.07201
; LINE_WIDTH: 0.457202
G1 X21.65 Y12.804 E.00394
; LINE_WIDTH: 0.493465
G1 X21.535 Y12.822 E.00429
; LINE_WIDTH: 0.529729
G1 X21.419 Y12.84 E.00463
; LINE_WIDTH: 0.56884
G1 X21.362 Y12.861 E.0026
; LINE_WIDTH: 0.596813
G1 X21.305 Y12.882 E.00274
G1 X21.419 Y12.924 E.00548
; LINE_WIDTH: 0.529729
G1 X21.477 Y12.976 E.00308
; LINE_WIDTH: 0.493465
G1 X21.535 Y13.028 E.00285
; LINE_WIDTH: 0.439634
G3 X21.623 Y13.182 I-.082 J.149 E.00602
G1 X23.936 Y13.182 E.07479
; WIPE_START
G1 F15000
G1 X21.936 Y13.182 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y5.816 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6407
G1 X22.602 Y4.617 E.03979
G1 X24.398 Y4.617 E.05957
G1 X24.398 Y5.816 E.03979
G1 X22.662 Y5.816 E.05758
G1 X22.21 Y6.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X22.21 Y4.225 E.06095
G1 X24.79 Y4.225 E.07928
G1 X24.79 Y6.208 E.06095
G1 X22.27 Y6.208 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.225 E-.75408
G1 X22.226 Y4.225 E-.00592
; WIPE_END
G1 E-.04 F1800
G1 X23.996 Y5.415 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.43908
G1 F6407
G1 X23.996 Y5.018 E.01279
G1 X23.004 Y5.018 E.03204
G1 X23.004 Y5.415 E.01279
G1 X23.936 Y5.415 E.03011
; WIPE_START
G1 F15000
G1 X23.004 Y5.415 E-.35441
G1 X23.004 Y5.018 E-.15054
G1 X23.675 Y5.018 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.303 Y5.274 Z3.8 F30000
G1 X59.24 Y6.208 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X56.66 Y6.208 E.07928
G1 X56.66 Y5.33 E.027
G1 X59.24 Y5.33 E.07928
G1 X59.24 Y6.148 E.02515
M204 S10000
G1 X59.044 Y5.769 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.52943
G1 F6407
G1 X56.856 Y5.769 E.08674
; WIPE_START
G1 F12949.374
G1 X58.856 Y5.769 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.816 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6407
G1 X51.602 Y5.816 E.05957
G1 X51.602 Y4.617 E.03978
G1 X53.398 Y4.617 E.05957
G1 X53.398 Y5.756 E.03779
G1 X53.79 Y6.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X51.21 Y6.208 E.07928
G1 X51.21 Y4.225 E.06095
G1 X53.79 Y4.225 E.07928
G1 X53.79 Y6.148 E.0591
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.004 Y5.415 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.439075
G1 F6407
G1 X52.996 Y5.415 E.03204
G1 X52.996 Y5.018 E.01279
G1 X52.004 Y5.018 E.03204
G1 X52.004 Y5.355 E.01085
; WIPE_START
G1 F15000
G1 X52.004 Y5.018 E-.12773
G1 X52.996 Y5.018 E-.37721
G1 X52.996 Y5.415 E-.15054
G1 X52.721 Y5.415 E-.10452
; WIPE_END
G1 E-.04 F1800
G1 X53.351 Y13.021 Z3.8 F30000
G1 X53.398 Y13.583 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6407
G1 X51.602 Y13.583 E.05957
G1 X51.602 Y12.384 E.03978
G1 X53.398 Y12.384 E.05957
G1 X53.398 Y13.523 E.03779
G1 X53.79 Y13.975 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X51.21 Y13.975 E.07928
G1 X51.21 Y11.992 E.06095
G1 X53.79 Y11.992 E.07928
G1 X53.79 Y13.915 E.0591
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.962 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.004 Y13.182 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.439065
G1 F6407
G1 X52.996 Y13.182 E.03204
G1 X52.996 Y12.785 E.01279
G1 X52.004 Y12.785 E.03204
G1 X52.004 Y13.122 E.01085
; WIPE_START
G1 F15000
G1 X52.004 Y12.785 E-.12774
G1 X52.996 Y12.785 E-.37721
G1 X52.996 Y13.182 E-.15053
G1 X52.721 Y13.182 E-.10452
; WIPE_END
G1 E-.04 F1800
G1 X58.254 Y18.44 Z3.8 F30000
G1 X58.848 Y19.004 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6407
G1 X57.052 Y19.004 E.05957
G1 X57.052 Y12.384 E.21962
G1 X58.848 Y12.384 E.05957
G1 X58.848 Y18.944 E.21763
; WIPE_START
G1 F15476.087
G1 X57.052 Y19.004 E-.68281
G1 X57.052 Y18.801 E-.07719
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y25.508 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
G1 F6407
G1 X57.052 Y25.508 E.05957
G1 X57.052 Y23.196 E.07671
G1 X58.848 Y23.196 E.05957
G1 X58.848 Y25.448 E.07473
G1 X59.24 Y25.9 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6407
M204 S5000
G1 X56.66 Y25.9 E.07928
G1 X56.66 Y25.834 E.00204
G1 X56.66 Y25.434 E.01229
G1 X56.66 Y12.89 E.38544
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.992 E.0276
G1 X59.24 Y11.992 E.10847
G1 X59.24 Y25.834 E.42533
G1 X59.24 Y25.84 E.0002
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.887 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.588 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6407
G1 X57.444 Y25.116 E.04697
G1 X58.456 Y25.116 E.03109
G1 X58.456 Y23.588 E.04697
G1 X57.504 Y23.588 E.02924
G1 X57.791 Y23.935 F30000
; LINE_WIDTH: 0.36025
G1 F6407
G1 X57.791 Y24.769 E.02157
G1 X58.109 Y24.769 E.00821
G1 X58.109 Y23.935 E.02157
G1 X57.851 Y23.935 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.935 E-.09779
G1 X58.109 Y24.769 E-.31697
G1 X57.791 Y24.769 E-.12059
G1 X57.791 Y24.178 E-.22465
; WIPE_END
G1 E-.04 F1800
G1 X59.033 Y19.794 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F6407
M204 S2000
G1 X58.466 Y19.227 E.02464
G1 X57.932 Y19.227
G1 X59.033 Y20.327 E.04782
G1 X59.033 Y20.861
G1 X57.399 Y19.227 E.07099
G1 X56.867 Y19.229
G1 X59.033 Y21.394 E.09409
G1 X59.033 Y21.927
G1 X56.867 Y19.762 E.09409
G1 X56.867 Y20.295
G1 X59.033 Y22.46 E.09409
G1 X59.012 Y22.973
G1 X56.867 Y20.828 E.0932
G1 X56.867 Y21.362
G1 X58.479 Y22.973 E.07003
G1 X57.946 Y22.973
G1 X56.867 Y21.895 E.04685
G1 X56.867 Y22.428
G1 X57.412 Y22.973 E.02368
; WIPE_START
G1 F12000
M204 S10000
G1 X56.867 Y22.428 E-.29287
G1 X56.867 Y21.895 E-.20264
G1 X57.36 Y22.387 E-.26449
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.612 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6407
G1 X58.456 Y18.612 E.03109
G1 X58.456 Y12.776 E.17933
G1 X57.444 Y12.776 E.03109
G1 X57.444 Y18.552 E.17749
G1 X57.791 Y18.265 F30000
; LINE_WIDTH: 0.36025
G1 F6407
G1 X58.109 Y18.265 E.00821
G1 X58.109 Y13.123 E.13297
G1 X57.791 Y13.123 E.00821
G1 X57.791 Y18.205 E.13141
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y16.205 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/58
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
G1 X21.398 Y38.298
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.354 E.8606
G1 X22.48 Y12.354 E.06229
G1 X24.398 Y12.354 E.06362
G1 X24.398 Y13.573 E.04044
G1 X21.398 Y13.573 E.09952
G1 X21.398 Y38.238 E.81817
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.962 E.82128
G1 X22.48 Y11.962 E.06975
G1 X24.79 Y11.962 E.07098
M73 P76 R3
G1 X24.79 Y13.965 E.06156
G1 X21.79 Y13.965 E.09218
G1 X21.79 Y38.63 E.75788
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6126
G1 X21 Y13.37 E.78333
G1 X21.11 Y12.862 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.65162
G1 F6126
G1 X21.21 Y12.862 E.00498
G1 X23.991 Y13.167 F30000
; LINE_WIDTH: 0.448975
G1 F6126
G1 X23.991 Y12.761 E.01344
G1 X21.771 Y12.761 E.07346
; LINE_WIDTH: 0.43156
G1 X21.716 Y12.753 E.00177
; LINE_WIDTH: 0.39672
G1 X21.66 Y12.745 E.00162
; LINE_WIDTH: 0.401994
G1 X21.595 Y12.764 E.00199
; LINE_WIDTH: 0.44738
G1 X21.53 Y12.784 E.00224
; LINE_WIDTH: 0.492767
G1 X21.465 Y12.803 E.00249
; LINE_WIDTH: 0.538154
G1 X21.4 Y12.823 E.00274
; LINE_WIDTH: 0.58354
G1 X21.335 Y12.842 E.00299
; LINE_WIDTH: 0.628927
G1 X21.27 Y12.862 E.00324
; LINE_WIDTH: 0.632707
G1 X21.32 Y12.881 E.00256
; LINE_WIDTH: 0.59488
G1 X21.37 Y12.9 E.00239
; LINE_WIDTH: 0.557054
G1 X21.419 Y12.919 E.00223
; LINE_WIDTH: 0.51585
G1 X21.507 Y12.992 E.00441
; LINE_WIDTH: 0.449985
G3 X21.623 Y13.166 I-.067 J.169 E.00739
G2 X23.931 Y13.167 I1.23 J-418.647 E.07657
; WIPE_START
G1 F15000
G1 X21.931 Y13.166 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y5.846 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X22.602 Y4.627 E.04044
G1 X24.398 Y4.627 E.05957
G1 X24.398 Y5.846 E.04044
G1 X22.662 Y5.846 E.05758
G1 X22.21 Y6.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X22.21 Y4.235 E.06156
G1 X24.79 Y4.235 E.07928
G1 X24.79 Y6.238 E.06156
G1 X22.27 Y6.238 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X22.21 Y4.239 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.991 Y5.439 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.44899
G1 F6126
G1 X23.991 Y5.033 E.01344
G1 X23.009 Y5.033 E.03252
G1 X23.009 Y5.439 E.01344
G1 X23.931 Y5.439 E.03053
; WIPE_START
G1 F15000
G1 X23.009 Y5.439 E-.35065
G1 X23.009 Y5.033 E-.15431
G1 X23.68 Y5.033 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.308 Y5.292 Z4 F30000
G1 X59.24 Y6.238 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X56.66 Y6.238 E.07928
G1 X56.66 Y5.343 E.02751
G1 X59.24 Y5.343 E.07928
G1 X59.24 Y6.178 E.02566
M204 S10000
G1 X59.044 Y5.79 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.54601
G1 F6126
G1 X56.856 Y5.79 E.0897
; WIPE_START
G1 F12522.612
G1 X58.856 Y5.79 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.846 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X51.602 Y5.846 E.05957
G1 X51.602 Y4.627 E.04044
G1 X53.398 Y4.627 E.05957
G1 X53.398 Y5.786 E.03845
G1 X53.79 Y6.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X51.21 Y6.238 E.07928
G1 X51.21 Y4.235 E.06156
G1 X53.79 Y4.235 E.07928
G1 X53.79 Y6.178 E.05971
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y6.224 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.009 Y5.439 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.44899
G1 F6126
G1 X52.991 Y5.439 E.03252
G1 X52.991 Y5.033 E.01344
G1 X52.009 Y5.033 E.03252
G1 X52.009 Y5.379 E.01145
; WIPE_START
G1 F15000
G1 X52.009 Y5.033 E-.13151
G1 X52.991 Y5.033 E-.37345
G1 X52.991 Y5.439 E-.15431
G1 X52.726 Y5.439 E-.10074
; WIPE_END
G1 E-.04 F1800
G1 X53.354 Y13.046 Z4 F30000
G1 X53.398 Y13.573 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X51.602 Y13.573 E.05957
G1 X51.602 Y12.354 E.04044
G1 X53.398 Y12.354 E.05957
G1 X53.398 Y13.513 E.03845
G1 X53.79 Y13.965 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X51.21 Y13.965 E.07928
G1 X51.21 Y11.962 E.06156
G1 X53.79 Y11.962 E.07928
G1 X53.79 Y13.905 E.05971
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.952 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.009 Y13.167 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.44896
G1 F6126
G1 X52.991 Y13.167 E.03252
G1 X52.991 Y12.761 E.01343
G1 X52.009 Y12.761 E.03252
G1 X52.009 Y13.107 E.01145
; WIPE_START
G1 F15000
G1 X52.009 Y12.761 E-.1315
G1 X52.991 Y12.761 E-.37345
G1 X52.991 Y13.167 E-.1543
G1 X52.726 Y13.167 E-.10076
; WIPE_END
G1 E-.04 F1800
G1 X57.04 Y19.463 Z4 F30000
G1 X57.052 Y19.48 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X57.052 Y14.418 E.16792
G1 X57.528 Y14.418 E.01578
G1 X57.528 Y12.354 E.06846
G1 X58.848 Y12.354 E.04379
G1 X58.848 Y19.48 E.23638
G1 X57.112 Y19.48 E.05758
G1 X56.66 Y19.872 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X56.66 Y12.89 E.21454
G1 X55.71 Y12.89 E.02919
G1 X55.71 Y11.962 E.02851
G1 X59.24 Y11.962 E.10847
G1 X59.24 Y19.872 E.24306
G1 X56.72 Y19.872 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.703 Y17.872 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y19.088 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6126
G1 X58.456 Y19.088 E.03109
G1 X58.456 Y15.28 E.11699
; LINE_WIDTH: 0.440723
G1 X58.435 Y14.991 E.00942
; LINE_WIDTH: 0.498414
G3 X58.416 Y14.621 I1.966 J-.286 E.01374
G1 X58.416 Y12.786 E.06813
G1 X57.96 Y12.786 E.01695
G1 X57.958 Y14.661 E.0696
; LINE_WIDTH: 0.482188
G1 X57.845 Y14.736 E.00485
; LINE_WIDTH: 0.420596
G1 X57.731 Y14.81 E.00417
G1 X57.444 Y14.81 E.00884
G1 X57.444 Y19.028 E.12982
G1 X57.791 Y18.741 F30000
; LINE_WIDTH: 0.36025
G1 F6126
G1 X58.109 Y18.741 E.00821
G1 X58.109 Y14.888 E.09962
G1 X57.9 Y15.13 E.00826
G1 X57.791 Y15.147 E.00285
G1 X57.791 Y18.681 E.09137
; WIPE_START
G1 F15000
G1 X57.791 Y16.681 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X56.871 Y13.736 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F6126
M204 S2000
G1 X57.305 Y13.302 E.01888
G1 X57.305 Y12.768
G1 X56.867 Y13.206 E.01903
G1 X56.858 Y12.683
G1 X57.305 Y12.235 E.01944
G1 X56.838 Y12.169
G1 X56.325 Y12.683 E.0223
G1 X55.917 Y12.557
G1 X56.304 Y12.169 E.01682
M204 S10000
G1 X56.759 Y12.583 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.102021
G1 F6126
G1 X56.643 Y12.672 E.0007
G1 X56.665 Y12.701 E.00018
; WIPE_START
G1 F15000
G1 X56.643 Y12.672 E-.15336
G1 X56.759 Y12.583 E-.60664
; WIPE_END
G1 E-.04 F1800
G1 X57.968 Y20.119 Z4 F30000
G1 X58.848 Y25.607 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6126
G1 X57.052 Y25.607 E.05957
G1 X57.052 Y22.72 E.09577
G1 X58.848 Y22.72 E.05957
G1 X58.848 Y25.547 E.09378
G1 X59.24 Y25.999 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6126
M204 S5000
G1 X56.66 Y25.999 E.07928
G1 X56.66 Y25.941 E.00177
G1 X56.66 Y25.541 E.01229
G1 X56.66 Y22.328 E.09874
G1 X59.24 Y22.328 E.07928
G1 X59.24 Y25.939 E.11096
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.985 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.112 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6126
G1 X57.444 Y25.215 E.06461
G1 X58.456 Y25.215 E.03109
G1 X58.456 Y23.112 E.06461
G1 X57.504 Y23.112 E.02924
G1 X57.791 Y23.459 F30000
; LINE_WIDTH: 0.36025
G1 F6126
G1 X57.791 Y24.868 E.03642
G1 X58.109 Y24.868 E.00821
G1 X58.109 Y23.459 E.03642
G1 X57.851 Y23.459 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y23.459 E-.09779
G1 X58.109 Y24.868 E-.53523
G1 X57.791 Y24.868 E-.12059
G1 X57.791 Y24.851 E-.0064
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/58
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
G1 X21.398 Y38.298
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.307 E.86218
G1 X24.107 Y12.307 E.11627
G1 X24.398 Y12.307 E.00964
G1 X24.398 Y13.544 E.04103
G1 X21.398 Y13.544 E.09952
G1 X21.398 Y38.238 E.81915
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.921 E.82253
G1 X20.21 Y11.915 E.0002
G1 X24.107 Y11.915 E.11975
G1 X24.79 Y11.915 E.02098
G1 X24.79 Y11.921 E.0002
G1 X24.79 Y13.936 E.0619
G1 X21.79 Y13.936 E.09218
G1 X21.79 Y38.63 E.75879
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F5908
G1 X21 Y13.34 E.78427
G1 X23.987 Y13.133 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45784
G1 F5908
G1 X23.987 Y12.718 E.01403
G1 X21.776 Y12.718 E.07474
; LINE_WIDTH: 0.440887
G1 X21.557 Y12.701 E.00713
; LINE_WIDTH: 0.40698
G1 X21.338 Y12.684 E.00652
; LINE_WIDTH: 0.35937
G2 X20.962 Y12.667 I-.298 J2.421 E.00971
G1 X20.962 Y12.98 E.00808
G1 X21.419 Y12.98 E.01179
; LINE_WIDTH: 0.373074
G1 X21.479 Y12.997 E.00166
; LINE_WIDTH: 0.40698
G1 X21.538 Y13.014 E.00184
; LINE_WIDTH: 0.457416
G1 X21.598 Y13.031 E.00209
G1 X21.626 Y13.133 E.00356
G1 X23.927 Y13.133 E.07772
; WIPE_START
G1 F15000
G1 X21.927 Y13.133 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y5.893 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X22.602 Y4.656 E.04103
G1 X24.398 Y4.656 E.05957
G1 X24.398 Y5.893 E.04103
G1 X22.662 Y5.893 E.05758
G1 X22.21 Y6.279 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X22.21 Y4.264 E.06191
G1 X24.79 Y4.264 E.07928
G1 X24.79 Y6.279 E.06191
G1 X24.79 Y6.285 E.00019
G1 X22.264 Y6.285 E.07763
; WIPE_START
G1 F12000
M204 S10000
G1 X22.211 Y4.286 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.987 Y5.482 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45783
G1 F5908
G1 X23.987 Y5.067 E.01403
G1 X23.013 Y5.067 E.03293
G1 X23.013 Y5.482 E.01403
G1 X23.927 Y5.482 E.0309
; WIPE_START
G1 F15000
G1 X23.013 Y5.482 E-.34729
G1 X23.013 Y5.067 E-.15767
G1 X23.684 Y5.067 E-.25504
; WIPE_END
G1 E-.04 F1800
G1 X31.312 Y5.327 Z4.2 F30000
G1 X59.24 Y6.279 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X59.24 Y6.285 E.0002
G1 X56.66 Y6.285 E.07928
G1 X56.66 Y6.279 E.0002
G1 X56.66 Y5.38 E.02763
G1 X59.24 Y5.38 E.07928
G1 X59.24 Y6.219 E.02579
M204 S10000
G1 X59.044 Y5.832 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.55653
G1 F5908
G1 X56.856 Y5.832 E.09157
; WIPE_START
G1 F12266.117
G1 X58.856 Y5.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.893 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X51.602 Y5.893 E.05957
G1 X51.602 Y4.656 E.04103
G1 X53.398 Y4.656 E.05957
G1 X53.398 Y5.833 E.03904
G1 X53.79 Y6.279 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X53.79 Y6.285 E.00019
G1 X51.21 Y6.285 E.07928
G1 X51.21 Y6.279 E.00019
G1 X51.21 Y4.264 E.06191
G1 X53.79 Y4.264 E.07928
G1 X53.79 Y6.219 E.06006
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.285 E-.02521
M73 P77 R3
G1 X51.856 Y6.285 E-.73479
; WIPE_END
G1 E-.04 F1800
G1 X52.013 Y5.482 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45783
G1 F5908
G1 X52.987 Y5.482 E.03293
G1 X52.987 Y5.067 E.01403
G1 X52.013 Y5.067 E.03293
G1 X52.013 Y5.422 E.012
; WIPE_START
G1 F15000
G1 X52.013 Y5.067 E-.13487
G1 X52.987 Y5.067 E-.37009
G1 X52.987 Y5.482 E-.15767
G1 X52.731 Y5.482 E-.09738
; WIPE_END
G1 E-.04 F1800
G1 X53.36 Y13.089 Z4.2 F30000
G1 X53.398 Y13.544 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X51.602 Y13.544 E.05957
G1 X51.602 Y12.307 E.04103
G1 X53.398 Y12.307 E.05957
G1 X53.398 Y13.484 E.03904
G1 X53.79 Y13.936 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X51.21 Y13.936 E.07928
G1 X51.21 Y11.921 E.0619
G1 X51.21 Y11.915 E.0002
G1 X53.79 Y11.915 E.07928
G1 X53.79 Y11.921 E.0002
G1 X53.79 Y13.876 E.06006
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.922 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.013 Y13.133 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.45784
G1 F5908
G1 X52.987 Y13.133 E.03293
G1 X52.987 Y12.718 E.01403
G1 X52.013 Y12.718 E.03293
G1 X52.013 Y13.073 E.012
; WIPE_START
G1 F15000
G1 X52.013 Y12.718 E-.13487
G1 X52.987 Y12.718 E-.37008
G1 X52.987 Y13.133 E-.15767
G1 X52.731 Y13.133 E-.09738
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y19.09 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X57.052 Y12.307 E.225
G1 X58.848 Y12.307 E.05957
G1 X58.848 Y19.09 E.225
G1 X57.112 Y19.09 E.05758
G1 X56.66 Y19.482 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X56.66 Y11.921 E.23232
G1 X56.66 Y11.915 E.0002
G1 X59.24 Y11.915 E.07928
G1 X59.24 Y11.921 E.0002
G1 X59.24 Y19.482 E.23232
G1 X56.72 Y19.482 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.704 Y17.482 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.698 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5908
G1 X58.456 Y18.698 E.03109
G1 X58.456 Y12.699 E.18432
G1 X57.444 Y12.699 E.03109
G1 X57.444 Y18.638 E.18248
G1 X57.791 Y18.35 F30000
; LINE_WIDTH: 0.36025
G1 F5908
G1 X58.109 Y18.35 E.00821
G1 X58.109 Y13.046 E.13716
G1 X57.791 Y13.046 E.00821
G1 X57.791 Y18.29 E.13561
; WIPE_START
G1 F15000
G1 X57.791 Y16.29 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.643 Y23.875 Z4.2 F30000
G1 X58.848 Y25.705 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5908
G1 X57.052 Y25.705 E.05957
G1 X57.052 Y23.11 E.08609
G1 X58.848 Y23.11 E.05957
G1 X58.848 Y25.645 E.0841
G1 X59.24 Y26.098 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5908
M204 S5000
G1 X56.66 Y26.098 E.07928
G1 X56.66 Y26.04 E.00177
G1 X56.66 Y25.64 E.01229
G1 X56.66 Y22.718 E.08977
G1 X59.24 Y22.718 E.07928
G1 X59.24 Y26.038 E.10199
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.084 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.502 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5908
G1 X57.444 Y25.313 E.05565
G1 X58.456 Y25.313 E.03109
G1 X58.456 Y23.502 E.05565
G1 X57.504 Y23.502 E.02924
G1 X57.791 Y23.85 F30000
; LINE_WIDTH: 0.36025
G1 F5908
G1 X57.791 Y24.966 E.02887
G1 X58.109 Y24.966 E.00821
G1 X58.109 Y23.85 E.02887
G1 X57.851 Y23.85 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y23.85 E-.09779
G1 X58.109 Y24.966 E-.42433
G1 X57.791 Y24.966 E-.12059
G1 X57.791 Y24.658 E-.11729
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/58
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
G1 X21.398 Y38.298
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.244 E.86425
G1 X24.105 Y12.244 E.11621
G1 X24.398 Y12.244 E.0097
G1 X24.398 Y13.514 E.04212
G1 X21.398 Y13.514 E.09952
G1 X21.398 Y38.238 E.82014
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.874 E.82399
G1 X20.21 Y11.852 E.00066
G1 X24.105 Y11.852 E.11969
G1 X24.79 Y11.852 E.02104
G1 X24.79 Y11.874 E.00066
G1 X24.79 Y13.906 E.06245
G1 X21.79 Y13.906 E.09218
G1 X21.79 Y38.63 E.7597
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F5861
G1 X21 Y13.311 E.78521
G1 X23.979 Y13.095 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.47429
G1 F5861
G1 X23.979 Y12.663 E.01516
G1 X21.786 Y12.663 E.07709
; LINE_WIDTH: 0.457337
G1 X21.569 Y12.646 E.00734
; LINE_WIDTH: 0.42343
G1 X21.352 Y12.63 E.00674
; LINE_WIDTH: 0.375746
G2 X20.97 Y12.613 I-.299 J2.431 E.01037
G1 X20.97 Y12.942 E.00894
G1 X21.419 Y12.942 E.01218
; LINE_WIDTH: 0.389524
G1 X21.481 Y12.959 E.00179
; LINE_WIDTH: 0.42343
G1 X21.542 Y12.976 E.00196
; LINE_WIDTH: 0.473853
G1 X21.603 Y12.993 E.00222
G1 X21.632 Y13.095 E.00372
G1 X23.919 Y13.095 E.08031
; WIPE_START
G1 F14619.45
G1 X21.919 Y13.095 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y5.956 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X22.602 Y4.686 E.04212
G1 X24.398 Y4.686 E.05957
G1 X24.398 Y5.956 E.04212
G1 X22.662 Y5.956 E.05758
G1 X22.21 Y6.326 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X22.21 Y4.294 E.06245
G1 X24.79 Y4.294 E.07928
G1 X24.79 Y6.326 E.06245
G1 X24.79 Y6.348 E.00066
G1 X22.248 Y6.348 E.0781
; WIPE_START
G1 F12000
M204 S10000
G1 X22.211 Y4.348 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.979 Y5.537 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4743
G1 F5861
G1 X23.979 Y5.105 E.01516
G1 X23.021 Y5.105 E.03366
G1 X23.021 Y5.537 E.01516
G1 X23.919 Y5.537 E.03155
; WIPE_START
G1 F14604.293
G1 X23.021 Y5.537 E-.34102
G1 X23.021 Y5.105 E-.16392
G1 X23.692 Y5.105 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.32 Y5.367 Z4.4 F30000
G1 X59.24 Y6.326 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X59.24 Y6.348 E.00066
G1 X56.66 Y6.348 E.07928
G1 X56.66 Y6.326 E.00066
G1 X56.66 Y5.419 E.02787
G1 X59.24 Y5.419 E.07928
G1 X59.24 Y6.266 E.02602
M204 S10000
G1 X59.044 Y5.884 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.57932
G1 F5861
G1 X56.856 Y5.884 E.09563
; WIPE_START
G1 F11744.967
G1 X58.856 Y5.884 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y5.956 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X51.602 Y5.956 E.05957
G1 X51.602 Y4.686 E.04212
G1 X53.398 Y4.686 E.05957
G1 X53.398 Y5.896 E.04013
G1 X53.79 Y6.326 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X53.79 Y6.348 E.00066
G1 X51.21 Y6.348 E.07928
G1 X51.21 Y6.326 E.00066
G1 X51.21 Y4.294 E.06245
G1 X53.79 Y4.294 E.07928
G1 X53.79 Y6.266 E.06061
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.348 E-.031
G1 X51.872 Y6.348 E-.729
; WIPE_END
G1 E-.04 F1800
G1 X52.021 Y5.537 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4743
G1 F5861
G1 X52.979 Y5.537 E.03366
G1 X52.979 Y5.105 E.01516
G1 X52.021 Y5.105 E.03366
G1 X52.021 Y5.477 E.01305
; WIPE_START
G1 F14604.293
G1 X52.021 Y5.105 E-.14112
G1 X52.979 Y5.105 E-.36382
G1 X52.979 Y5.537 E-.16392
G1 X52.739 Y5.537 E-.09113
; WIPE_END
G1 E-.04 F1800
G1 X53.367 Y13.143 Z4.4 F30000
G1 X53.398 Y13.514 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X51.602 Y13.514 E.05957
G1 X51.602 Y12.244 E.04212
G1 X53.398 Y12.244 E.05957
G1 X53.398 Y13.454 E.04013
G1 X53.79 Y13.906 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X51.21 Y13.906 E.07928
G1 X51.21 Y11.874 E.06245
G1 X51.21 Y11.852 E.00066
G1 X53.79 Y11.852 E.07928
G1 X53.79 Y11.874 E.00066
G1 X53.79 Y13.846 E.06061
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.893 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.021 Y13.095 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.47429
G1 F5861
G1 X52.979 Y13.095 E.03366
G1 X52.979 Y12.663 E.01516
G1 X52.021 Y12.663 E.03366
G1 X52.021 Y13.035 E.01305
; WIPE_START
G1 F14604.631
G1 X52.021 Y12.663 E-.14112
G1 X52.979 Y12.663 E-.36383
G1 X52.979 Y13.095 E-.16392
G1 X52.739 Y13.095 E-.09112
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.802 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X57.052 Y12.244 E.21755
G1 X58.848 Y12.244 E.05957
G1 X58.848 Y18.802 E.21755
G1 X57.112 Y18.802 E.05758
G1 X56.66 Y19.194 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X56.66 Y11.874 E.22495
G1 X56.66 Y11.852 E.00066
G1 X59.24 Y11.852 E.07928
G1 X59.24 Y11.874 E.00066
G1 X59.24 Y19.194 E.22495
G1 X56.72 Y19.194 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.704 Y17.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.41 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5861
G1 X58.456 Y18.41 E.03109
G1 X58.456 Y12.636 E.17742
G1 X57.444 Y12.636 E.03109
G1 X57.444 Y18.35 E.17557
G1 X57.791 Y18.063 F30000
; LINE_WIDTH: 0.36025
G1 F5861
G1 X58.109 Y18.063 E.00821
G1 X58.109 Y12.983 E.13135
G1 X57.791 Y12.983 E.00821
G1 X57.791 Y18.003 E.1298
; WIPE_START
G1 F15000
G1 X57.791 Y16.003 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.61 Y23.592 Z4.4 F30000
G1 X58.848 Y25.792 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5861
G1 X57.052 Y25.792 E.05957
G1 X57.052 Y23.398 E.07942
G1 X58.848 Y23.398 E.05957
G1 X58.848 Y25.732 E.07743
G1 X59.24 Y26.184 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5861
M204 S5000
G1 X56.66 Y26.184 E.07928
G1 X56.66 Y26.139 E.00139
G1 X56.66 Y23.005 E.09627
G1 X59.24 Y23.005 E.07928
G1 X59.24 Y26.124 E.09581
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.17 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.79 Z4.4 F30000
G1 Z4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5861
G1 X57.444 Y25.4 E.04947
G1 X58.456 Y25.4 E.03109
G1 X58.456 Y23.79 E.04947
G1 X57.504 Y23.79 E.02924
G1 X57.791 Y24.137 F30000
; LINE_WIDTH: 0.36026
G1 F5861
G1 X57.791 Y25.052 E.02367
G1 X58.109 Y25.052 E.00821
G1 X58.109 Y24.137 E.02367
G1 X57.851 Y24.137 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 4.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
M73 P78 R3
G1 X58.109 Y24.137 E-.09779
G1 X58.109 Y25.052 E-.3479
G1 X57.791 Y25.052 E-.12059
G1 X57.791 Y24.543 E-.19373
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/58
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
G1 X21.398 Y38.298
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.165 E.86688
G1 X24.398 Y12.165 E.12592
G1 X24.398 Y13.474 E.04341
G1 X21.398 Y13.474 E.09952
G1 X21.398 Y38.238 E.82148
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.811 E.82591
G1 X20.21 Y11.773 E.00118
G1 X24.79 Y11.773 E.14073
G1 X24.79 Y11.811 E.00118
G1 X24.79 Y13.866 E.06313
G1 X21.79 Y13.866 E.09218
G1 X21.79 Y38.63 E.76094
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F5837
G1 X21 Y13.27 E.78649
G1 X23.969 Y13.045 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49373
G1 F5837
G1 X23.969 Y12.594 E.01656
G1 X21.796 Y12.594 E.07981
; LINE_WIDTH: 0.476777
G1 X21.582 Y12.577 E.00759
; LINE_WIDTH: 0.44287
G1 X21.369 Y12.56 E.00699
; LINE_WIDTH: 0.3951
G2 X20.98 Y12.543 I-.301 J2.441 E.01117
G1 X20.98 Y12.892 E.01002
G1 X21.419 Y12.892 E.01261
; LINE_WIDTH: 0.408964
G1 X21.482 Y12.909 E.00194
; LINE_WIDTH: 0.44287
G1 X21.545 Y12.926 E.00212
; LINE_WIDTH: 0.493279
G1 X21.608 Y12.943 E.00239
G1 X21.638 Y13.045 E.0039
G1 X23.909 Y13.045 E.08333
; WIPE_START
G1 F13988.861
G1 X21.909 Y13.045 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.035 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X22.602 Y4.726 E.04341
G1 X24.398 Y4.726 E.05957
G1 X24.398 Y6.035 E.04341
G1 X22.662 Y6.035 E.05758
G1 X22.21 Y6.389 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X22.21 Y4.334 E.06313
G1 X24.79 Y4.334 E.07928
G1 X24.79 Y6.389 E.06313
G1 X24.79 Y6.427 E.00117
G1 X22.232 Y6.427 E.07861
; WIPE_START
G1 F12000
M204 S10000
G1 X22.211 Y4.427 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.969 Y5.606 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49373
G1 F5837
G1 X23.969 Y5.155 E.01656
G1 X23.031 Y5.155 E.03446
G1 X23.031 Y5.606 E.01656
G1 X23.909 Y5.606 E.03225
; WIPE_START
G1 F13974.845
G1 X23.031 Y5.606 E-.33365
G1 X23.031 Y5.155 E-.17131
G1 X23.702 Y5.155 E-.25504
; WIPE_END
G1 E-.04 F1800
G1 X31.33 Y5.42 Z4.6 F30000
G1 X59.24 Y6.389 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X59.24 Y6.427 E.00118
G1 X56.66 Y6.427 E.07928
G1 X56.66 Y6.389 E.00118
G1 X56.66 Y5.468 E.02829
G1 X59.24 Y5.468 E.07928
G1 X59.24 Y6.329 E.02644
M204 S10000
G1 X59.044 Y5.948 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.60967
G1 F5837
G1 X56.856 Y5.948 E.10105
; WIPE_START
G1 F11116.013
G1 X58.856 Y5.948 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.035 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X51.602 Y6.035 E.05957
G1 X51.602 Y4.726 E.04341
G1 X53.398 Y4.726 E.05957
G1 X53.398 Y5.975 E.04142
G1 X53.79 Y6.389 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X53.79 Y6.427 E.00118
G1 X51.21 Y6.427 E.07928
G1 X51.21 Y6.389 E.00117
G1 X51.21 Y4.334 E.06313
G1 X53.79 Y4.334 E.07928
G1 X53.79 Y6.329 E.06129
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.427 E-.03735
G1 X51.888 Y6.427 E-.72265
; WIPE_END
G1 E-.04 F1800
G1 X52.031 Y5.606 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49374
G1 F5837
G1 X52.969 Y5.606 E.03446
G1 X52.969 Y5.155 E.01656
G1 X52.031 Y5.155 E.03446
G1 X52.031 Y5.546 E.01436
; WIPE_START
G1 F13974.534
G1 X52.031 Y5.155 E-.1485
G1 X52.969 Y5.155 E-.35644
G1 X52.969 Y5.606 E-.17131
G1 X52.749 Y5.606 E-.08375
; WIPE_END
G1 E-.04 F1800
G1 X53.376 Y13.213 Z4.6 F30000
G1 X53.398 Y13.474 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X51.602 Y13.474 E.05957
G1 X51.602 Y12.165 E.04341
G1 X53.398 Y12.165 E.05957
G1 X53.398 Y13.414 E.04142
G1 X53.79 Y13.866 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X51.21 Y13.866 E.07928
G1 X51.21 Y11.811 E.06313
G1 X51.21 Y11.773 E.00118
G1 X53.79 Y11.773 E.07928
G1 X53.79 Y11.811 E.00118
G1 X53.79 Y13.806 E.06129
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.852 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.031 Y13.045 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.49373
G1 F5837
G1 X52.969 Y13.045 E.03446
G1 X52.969 Y12.594 E.01656
G1 X52.031 Y12.594 E.03446
G1 X52.031 Y12.985 E.01436
; WIPE_START
G1 F13974.845
G1 X52.031 Y12.594 E-.14851
G1 X52.969 Y12.594 E-.35644
G1 X52.969 Y13.045 E-.17131
G1 X52.749 Y13.045 E-.08373
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.58 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X57.052 Y12.165 E.21281
G1 X58.848 Y12.165 E.05957
G1 X58.848 Y18.58 E.21281
G1 X57.112 Y18.58 E.05758
G1 X56.66 Y18.972 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X56.66 Y11.811 E.22005
G1 X56.66 Y11.773 E.00118
G1 X59.24 Y11.773 E.07928
G1 X59.24 Y11.811 E.00118
G1 X59.24 Y18.972 E.22005
G1 X56.72 Y18.972 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.703 Y16.973 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.188 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5837
G1 X58.456 Y18.188 E.03109
G1 X58.456 Y12.557 E.17303
G1 X57.444 Y12.557 E.03109
G1 X57.444 Y18.128 E.17119
G1 X57.791 Y17.841 F30000
; LINE_WIDTH: 0.36025
G1 F5837
G1 X58.109 Y17.841 E.00821
G1 X58.109 Y12.904 E.12766
G1 X57.791 Y12.904 E.00821
G1 X57.791 Y17.781 E.12611
; WIPE_START
G1 F15000
G1 X57.791 Y15.781 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.587 Y23.372 Z4.6 F30000
G1 X58.848 Y25.86 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5837
G1 X57.052 Y25.86 E.05957
G1 X57.052 Y23.62 E.0743
G1 X58.848 Y23.62 E.05957
G1 X58.848 Y25.8 E.07231
G1 X59.24 Y26.252 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5837
M204 S5000
G1 X56.66 Y26.252 E.07928
G1 X56.66 Y26.225 E.00083
G1 X56.66 Y23.228 E.09209
G1 X59.24 Y23.228 E.07928
G1 X59.24 Y26.192 E.09108
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.238 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.012 Z4.6 F30000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5837
G1 X57.444 Y25.467 E.04473
G1 X58.456 Y25.467 E.03109
G1 X58.456 Y24.012 E.04473
G1 X57.504 Y24.012 E.02924
G1 X57.791 Y24.359 F30000
; LINE_WIDTH: 0.36025
G1 F5837
G1 X57.791 Y25.12 E.01969
G1 X58.109 Y25.12 E.00821
G1 X58.109 Y24.359 E.01969
G1 X57.851 Y24.359 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 4.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.359 E-.09779
G1 X58.109 Y25.12 E-.28934
G1 X57.791 Y25.12 E-.12059
G1 X57.791 Y24.456 E-.25229
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/58
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
G1 X21.398 Y38.298
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.102 E.86897
G1 X22.602 Y12.102 E.06634
G1 X22.602 Y12.067 E.00116
G1 X24.398 Y12.067 E.05957
G1 X24.398 Y13.424 E.045
G1 X21.398 Y13.424 E.09952
G1 X21.398 Y38.238 E.82314
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.732 E.82835
G1 X20.21 Y11.71 E.00067
G1 X21.81 Y11.71 E.04916
G1 X22.21 Y11.71 E.01229
G1 X22.21 Y11.675 E.00108
G1 X24.79 Y11.675 E.07928
G1 X24.79 Y11.732 E.00175
G1 X24.79 Y12.132 E.01229
G1 X24.79 Y13.816 E.05174
G1 X21.79 Y13.816 E.09218
G1 X21.79 Y38.63 E.76248
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F5831
G1 X21 Y13.22 E.78807
G1 X23.957 Y12.983 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.510639
G1 F5831
G1 X23.957 Y12.508 E.0181
G1 X22.907 Y12.508 E.04002
G1 X22.806 Y12.534 E.00399
G1 X21.8 Y12.534 E.03833
; LINE_WIDTH: 0.483177
G1 X21.587 Y12.517 E.00766
; LINE_WIDTH: 0.44927
G1 X21.374 Y12.5 E.00707
; LINE_WIDTH: 0.401471
G2 X20.983 Y12.483 I-.302 J2.444 E.01144
G1 X20.983 Y12.839 E.01039
G1 X21.419 Y12.839 E.01274
; LINE_WIDTH: 0.415364
G1 X21.483 Y12.856 E.00199
; LINE_WIDTH: 0.44927
G1 X21.546 Y12.873 E.00217
; LINE_WIDTH: 0.499298
G1 X21.61 Y12.89 E.00244
G1 X21.64 Y12.991 E.00395
G1 X22.806 Y12.991 E.04333
; LINE_WIDTH: 0.510337
G3 X23.897 Y12.983 I1.003 J56.807 E.04157
; WIPE_START
G1 F13478.33
G1 X22.806 Y12.991 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.133 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X22.602 Y4.776 E.045
G1 X24.398 Y4.776 E.05957
G1 X24.398 Y6.133 E.045
G1 X22.662 Y6.133 E.05758
G1 X22.21 Y6.468 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X22.21 Y4.384 E.06403
G1 X24.79 Y4.384 E.07928
G1 X24.79 Y6.068 E.05174
G1 X24.79 Y6.468 E.01229
G1 X24.79 Y6.525 E.00175
G1 X22.213 Y6.525 E.07918
; WIPE_START
G1 F9300
M204 S10000
G1 X22.21 Y4.525 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.957 Y5.692 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.517685
G1 F5831
G1 X23.957 Y5.217 E.01837
G1 X23.043 Y5.217 E.03536
G1 X23.043 Y5.692 E.01837
G1 X23.897 Y5.692 E.03304
; WIPE_START
G1 F13269.723
G1 X23.043 Y5.692 E-.32454
G1 X23.043 Y5.217 E-.18041
G1 X23.714 Y5.217 E-.25506
; WIPE_END
G1 E-.04 F1800
G1 X31.342 Y5.486 Z4.8 F30000
G1 X59.24 Y6.468 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X59.24 Y6.525 E.00175
G1 X56.66 Y6.525 E.07928
G1 X56.66 Y6.468 E.00175
G1 X56.66 Y6.068 E.01229
G1 X56.66 Y5.536 E.01634
G1 X59.24 Y5.536 E.07928
G1 X59.24 Y6.408 E.02679
M204 S10000
G1 X59.044 Y6.031 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.63981
G1 F5831
G1 X56.856 Y6.031 E.10642
; WIPE_START
G1 F10554.709
G1 X58.856 Y6.031 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.133 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X51.602 Y6.133 E.05957
G1 X51.602 Y4.776 E.045
G1 X53.398 Y4.776 E.05957
G1 X53.398 Y6.073 E.04301
G1 X53.79 Y6.468 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X53.79 Y6.525 E.00175
M73 P79 R3
G1 X51.21 Y6.525 E.07928
G1 X51.21 Y6.468 E.00175
G1 X51.21 Y6.068 E.01229
G1 X51.21 Y4.384 E.05174
G1 X53.79 Y4.384 E.07928
G1 X53.79 Y6.408 E.06218
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.525 E-.04444
G1 X51.907 Y6.525 E-.71556
; WIPE_END
G1 E-.04 F1800
G1 X52.043 Y5.692 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51768
G1 F5831
G1 X52.957 Y5.692 E.03536
G1 X52.957 Y5.217 E.01837
G1 X52.043 Y5.217 E.03536
G1 X52.043 Y5.632 E.01605
; WIPE_START
G1 F13269.863
G1 X52.043 Y5.217 E-.15761
G1 X52.957 Y5.217 E-.34734
G1 X52.957 Y5.692 E-.18041
G1 X52.761 Y5.692 E-.07465
; WIPE_END
G1 E-.04 F1800
G1 X53.388 Y13.299 Z4.8 F30000
G1 X53.398 Y13.424 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X51.602 Y13.424 E.05957
G1 X51.602 Y12.067 E.045
G1 X53.398 Y12.067 E.05957
G1 X53.398 Y13.364 E.04301
G1 X53.79 Y13.816 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X51.21 Y13.816 E.07928
G1 X51.21 Y12.132 E.05174
G1 X51.21 Y11.732 E.01229
G1 X51.21 Y11.675 E.00175
G1 X53.79 Y11.675 E.07928
G1 X53.79 Y11.732 E.00175
G1 X53.79 Y12.132 E.01229
G1 X53.79 Y13.756 E.04989
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.802 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.043 Y12.983 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51769
G1 F5831
G1 X52.957 Y12.983 E.03536
G1 X52.957 Y12.508 E.01837
G1 X52.043 Y12.508 E.03536
G1 X52.043 Y12.923 E.01605
; WIPE_START
G1 F13269.583
G1 X52.043 Y12.508 E-.15762
G1 X52.957 Y12.508 E-.34734
G1 X52.957 Y12.983 E-.18042
G1 X52.761 Y12.983 E-.07463
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.401 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X57.052 Y12.067 E.21012
G1 X58.848 Y12.067 E.05957
G1 X58.848 Y18.401 E.21012
G1 X57.112 Y18.401 E.05758
G1 X56.66 Y18.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X56.66 Y12.132 E.20469
G1 X56.66 Y11.732 E.01229
G1 X56.66 Y11.675 E.00175
G1 X59.24 Y11.675 E.07928
G1 X59.24 Y11.732 E.00175
G1 X59.24 Y12.132 E.01229
G1 X59.24 Y18.793 E.20469
G1 X56.72 Y18.793 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.702 Y16.793 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.009 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5831
G1 X58.456 Y18.009 E.03109
G1 X58.456 Y12.459 E.17054
G1 X57.444 Y12.459 E.03109
G1 X57.444 Y17.949 E.16869
G1 X57.791 Y17.662 F30000
; LINE_WIDTH: 0.36025
G1 F5831
G1 X58.109 Y17.662 E.00821
G1 X58.109 Y12.806 E.12556
G1 X57.791 Y12.806 E.00821
G1 X57.791 Y17.602 E.12401
; WIPE_START
G1 F15000
G1 X57.791 Y15.602 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.568 Y23.195 Z4.8 F30000
G1 X58.848 Y25.927 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5831
G1 X57.052 Y25.927 E.05957
G1 X57.052 Y23.799 E.07061
G1 X58.848 Y23.799 E.05957
G1 X58.848 Y25.867 E.06862
G1 X59.24 Y26.32 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5831
M204 S5000
G1 X56.66 Y26.32 E.07928
G1 X56.66 Y26.293 E.00083
G1 X56.66 Y23.407 E.08868
G1 X59.24 Y23.407 E.07928
G1 X59.24 Y26.26 E.08766
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.306 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.191 Z4.8 F30000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5831
G1 X57.444 Y25.535 E.04131
G1 X58.456 Y25.535 E.03109
G1 X58.456 Y24.191 E.04131
G1 X57.504 Y24.191 E.02924
G1 X57.791 Y24.538 F30000
; LINE_WIDTH: 0.36025
G1 F5831
G1 X57.791 Y25.188 E.01681
G1 X58.109 Y25.188 E.00821
G1 X58.109 Y24.538 E.01681
G1 X57.851 Y24.538 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 4.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.538 E-.1043
G1 X58.109 Y25.188 E-.26354
G1 X57.791 Y25.188 E-.12862
G1 X57.791 Y24.538 E-.26354
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/58
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
G1 X21.398 Y38.298
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.202 E.86565
G1 X22.602 Y12.202 E.06634
G1 X22.602 Y11.947 E.00846
G1 X24.398 Y11.947 E.05957
G1 X24.398 Y13.371 E.04725
G1 X21.398 Y13.371 E.09952
G1 X21.398 Y38.238 E.82487
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.81 E.82595
G1 X21.81 Y11.81 E.04916
G1 X22.21 Y11.81 E.01229
G1 X22.21 Y11.634 E.00541
G1 X22.21 Y11.555 E.00242
G1 F5700
G1 X24.79 Y11.555 E.07928
G1 F5859
G1 X24.79 Y11.634 E.00242
G1 X24.79 Y12.034 E.01229
G1 X24.79 Y13.763 E.05314
G1 X21.79 Y13.763 E.09218
G1 X21.79 Y38.63 E.76408
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F5859
G1 X21 Y13.168 E.78973
G1 X21.085 Y12.685 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.60172
G1 F5859
G1 X21.297 Y12.685 E.00964
G1 X23.94 Y12.914 F30000
; LINE_WIDTH: 0.551536
G1 F5859
G1 X23.94 Y12.405 E.02108
G2 X23.061 Y12.406 I-.349 J123.361 E.03645
G1 X23.026 Y12.532 E.00545
; LINE_WIDTH: 0.530284
G1 X22.953 Y12.554 E.00304
; LINE_WIDTH: 0.48779
G1 X22.879 Y12.575 E.00277
; LINE_WIDTH: 0.425494
G1 X22.806 Y12.596 E.00238
G1 X21.757 Y12.596 E.0327
; LINE_WIDTH: 0.446259
G1 X21.657 Y12.618 E.00337
; LINE_WIDTH: 0.490677
G1 X21.557 Y12.641 E.00374
; LINE_WIDTH: 0.535094
G1 X21.457 Y12.663 E.00411
; LINE_WIDTH: 0.579512
G1 X21.357 Y12.685 E.00448
G1 X21.414 Y12.733 E.00328
; LINE_WIDTH: 0.535094
G1 X21.472 Y12.78 E.00301
; LINE_WIDTH: 0.490677
G1 X21.53 Y12.828 E.00273
; LINE_WIDTH: 0.42527
G3 X21.623 Y12.977 I-.075 J.15 E.00577
G1 X22.806 Y12.977 E.03685
; LINE_WIDTH: 0.445297
G1 X22.953 Y12.956 E.00487
; LINE_WIDTH: 0.48779
G1 X23.1 Y12.935 E.00538
; LINE_WIDTH: 0.547501
G1 X23.246 Y12.914 E.0061
G1 X23.88 Y12.914 E.02605
; WIPE_START
G1 F12485.612
G1 X23.246 Y12.914 E-.61573
G1 X23.1 Y12.935 E-.14427
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.253 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X22.602 Y4.829 E.04725
G1 X24.398 Y4.829 E.05957
G1 X24.398 Y6.253 E.04725
G1 X22.662 Y6.253 E.05758
G1 X22.21 Y6.566 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X22.21 Y4.437 E.06543
G1 X24.79 Y4.437 E.07928
G1 X24.79 Y6.166 E.05314
G1 X24.79 Y6.566 E.01229
G1 X24.79 Y6.645 E.00242
G1 F5700
G1 X22.21 Y6.645 E.07928
G1 F5859
G1 X22.21 Y6.626 E.00058
; WIPE_START
G1 F5973.807
M204 S10000
G1 X22.21 Y4.626 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.94 Y5.795 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55154
G1 F5859
G1 X23.94 Y5.286 E.02108
G1 X23.06 Y5.286 E.03648
G1 X23.06 Y5.795 E.02108
G1 X23.88 Y5.795 E.03399
; WIPE_START
G1 F12386.459
G1 X23.06 Y5.795 E-.31167
G1 X23.06 Y5.286 E-.19327
G1 X23.731 Y5.286 E-.25506
; WIPE_END
G1 E-.04 F1800
G1 X31.361 Y5.496 Z5 F30000
G1 X58.848 Y6.253 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X57.052 Y6.253 E.05957
G1 X57.052 Y5.996 E.00852
G1 X58.848 Y5.996 E.05957
G1 X58.848 Y6.193 E.00653
G1 X59.24 Y6.566 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X59.24 Y6.645 E.00242
G1 F5700
G1 X56.66 Y6.645 E.07928
G1 F5859
G1 X56.66 Y6.566 E.00242
G1 X56.66 Y6.166 E.01229
G1 X56.66 Y5.604 E.01727
G1 X59.24 Y5.604 E.07928
G1 X59.24 Y6.506 E.02772
; WIPE_START
G1 F12000
M204 S10000
G1 X59.24 Y6.645 E-.05277
G1 X57.379 Y6.645 E-.70723
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.253 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X51.602 Y6.253 E.05957
G1 X51.602 Y4.829 E.04725
G1 X53.398 Y4.829 E.05957
G1 X53.398 Y6.193 E.04526
G1 X53.79 Y6.566 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X53.79 Y6.645 E.00242
G1 F5700
G1 X51.21 Y6.645 E.07928
G1 F5859
G1 X51.21 Y6.566 E.00242
G1 X51.21 Y6.166 E.01229
G1 X51.21 Y4.437 E.05314
G1 X53.79 Y4.437 E.07928
G1 X53.79 Y6.506 E.06359
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.645 E-.05278
G1 X51.929 Y6.645 E-.70722
; WIPE_END
G1 E-.04 F1800
G1 X52.06 Y5.795 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.551535
G1 F5859
G1 X52.94 Y5.795 E.03648
G1 X52.94 Y5.286 E.02108
G1 X52.06 Y5.286 E.03648
G1 X52.06 Y5.735 E.01859
; WIPE_START
G1 F12386.582
G1 X52.06 Y5.286 E-.17047
G1 X52.94 Y5.286 E-.33448
G1 X52.94 Y5.795 E-.19328
G1 X52.778 Y5.795 E-.06178
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y13.371 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X51.602 Y13.371 E.05957
G1 X51.602 Y11.947 E.04725
G1 X53.398 Y11.947 E.05957
G1 X53.398 Y13.311 E.04526
G1 X53.79 Y13.763 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X51.21 Y13.763 E.07928
G1 X51.21 Y12.034 E.05314
G1 X51.21 Y11.634 E.01229
G1 X51.21 Y11.555 E.00242
G1 F5700
G1 X53.79 Y11.555 E.07928
G1 F5859
G1 X53.79 Y11.634 E.00242
G1 X53.79 Y12.034 E.01229
G1 X53.79 Y13.703 E.0513
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.75 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.06 Y12.914 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55153
G1 F5859
G1 X52.94 Y12.914 E.03648
G1 X52.94 Y12.405 E.02108
G1 X52.06 Y12.405 E.03648
G1 X52.06 Y12.854 E.01859
; WIPE_START
G1 F12386.701
G1 X52.06 Y12.405 E-.17048
G1 X52.94 Y12.405 E-.33448
G1 X52.94 Y12.914 E-.19328
G1 X52.778 Y12.914 E-.06177
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.253 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X57.052 Y11.947 E.20918
G1 X58.848 Y11.947 E.05957
G1 X58.848 Y18.253 E.20918
G1 X57.112 Y18.253 E.05758
G1 X56.66 Y18.645 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X56.66 Y12.034 E.20314
G1 X56.66 Y11.634 E.01229
G1 X56.66 Y11.555 E.00242
G1 F5700
G1 X59.24 Y11.555 E.07928
G1 F5859
G1 X59.24 Y11.634 E.00242
G1 X59.24 Y12.034 E.01229
G1 X59.24 Y18.645 E.20314
G1 X56.72 Y18.645 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.702 Y16.645 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.861 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5859
G1 X58.456 Y17.861 E.03109
G1 X58.456 Y12.339 E.16966
G1 X57.444 Y12.339 E.03109
G1 X57.444 Y17.801 E.16782
G1 X57.791 Y17.514 F30000
; LINE_WIDTH: 0.36025
G1 F5859
G1 X58.109 Y17.514 E.00821
G1 X58.109 Y12.686 E.12483
G1 X57.791 Y12.686 E.00821
G1 X57.791 Y17.454 E.12328
; WIPE_START
G1 F15000
G1 X57.791 Y15.454 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.553 Y23.048 Z5 F30000
G1 X58.848 Y25.995 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5859
G1 X57.052 Y25.995 E.05957
G1 X57.052 Y23.947 E.06795
G1 X58.848 Y23.947 E.05957
G1 X58.848 Y25.935 E.06595
G1 X59.24 Y26.387 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5859
M204 S5000
G1 X56.66 Y26.387 E.07928
G1 X56.66 Y26.361 E.00083
G1 X56.66 Y23.555 E.08621
G1 X59.24 Y23.555 E.07928
G1 X59.24 Y26.327 E.08519
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.374 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.339 Z5 F30000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F5859
G1 X57.444 Y25.603 E.03884
G1 X58.456 Y25.603 E.03109
G1 X58.456 Y24.339 E.03884
G1 X57.504 Y24.339 E.02924
G1 X57.791 Y24.686 F30000
; LINE_WIDTH: 0.36025
G1 F5859
G1 X57.791 Y25.256 E.01473
G1 X58.109 Y25.256 E.00821
G1 X58.109 Y24.686 E.01473
G1 X57.851 Y24.686 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 4.8
; LAYER_HEIGHT: 0.2
; WIPE_START
M73 P80 R3
G1 F15000
G1 X58.109 Y24.686 E-.11409
G1 X58.109 Y25.256 E-.2526
G1 X57.791 Y25.256 E-.1407
G1 X57.791 Y24.686 E-.2526
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/58
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
G1 X21.398 Y38.298
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.302 E.86233
G1 X22.602 Y12.302 E.06634
G1 X22.602 Y11.799 E.0167
G1 X24.398 Y11.799 E.05957
G1 X24.398 Y13.3 E.04979
G1 X21.398 Y13.3 E.09952
G1 X21.398 Y38.238 E.82724
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6225
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y11.91 E.82288
G1 X21.81 Y11.91 E.04916
G1 X22.21 Y11.91 E.01229
G1 X22.21 Y11.514 E.01217
G1 F4076.669
G1 X22.21 Y11.407 E.0033
G1 F2880
G1 X24.79 Y11.407 E.07928
G1 F4076.79
G1 X24.79 Y11.514 E.0033
G1 F6225
G1 X24.79 Y11.914 E.01229
G1 X24.79 Y12.314 E.01229
G1 X24.79 Y13.692 E.04234
G1 X21.79 Y13.692 E.09218
G1 X21.79 Y38.63 E.76628
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.431773
G1 F6225
G1 X21 Y13.096 E.79211
G1 X21.021 Y13.038 E.00195
; LINE_WIDTH: 0.49613
G1 X21.043 Y12.981 E.00228
; LINE_WIDTH: 0.539069
G1 X21.064 Y12.923 E.00249
; LINE_WIDTH: 0.582009
G1 X21.086 Y12.865 E.00271
; LINE_WIDTH: 0.624949
G1 X21.107 Y12.807 E.00292
; LINE_WIDTH: 0.633936
G1 X22.805 Y12.801 E.08178
G1 X24.006 Y12.908 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.414854
G1 F6225
G1 X24.006 Y12.191 E.02173
G1 X23.287 Y12.18 E.02179
G1 X23.009 Y12.141 E.00851
G1 X23.187 Y12.28 E.00683
G1 X23.198 Y12.908 E.01902
G1 X23.946 Y12.908 E.02268
G1 X23.556 Y12.549 F30000
; LINE_WIDTH: 0.38278
G1 F6225
G1 X23.587 Y12.549 E.00087
; WIPE_START
G1 F15000
G1 X23.556 Y12.549 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.401 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X22.602 Y4.9 E.04979
G1 X24.398 Y4.9 E.05957
G1 X24.398 Y6.401 E.04979
G1 X22.662 Y6.401 E.05758
G1 X22.21 Y6.686 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6225
M204 S5000
G1 X22.21 Y4.508 E.06692
G1 X24.79 Y4.508 E.07928
G1 X24.79 Y5.886 E.04234
G1 X24.79 Y6.286 E.01229
G1 X24.79 Y6.686 E.01229
G1 F4076.306
G1 X24.79 Y6.793 E.0033
G1 F2880
G1 X22.21 Y6.793 E.07928
G1 F3381.871
G1 X22.21 Y6.746 E.00145
; WIPE_START
M204 S10000
G1 X22.21 Y4.746 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.009 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6225
G1 X24.006 Y5.292 E.02203
G1 X22.994 Y5.292 E.03109
G1 X22.994 Y6.009 E.02203
G1 X23.946 Y6.009 E.02924
G1 X23.353 Y5.651 F30000
; LINE_WIDTH: 0.38276
G1 F6225
G1 X23.587 Y5.651 E.0065
; WIPE_START
G1 F15000
G1 X23.353 Y5.651 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X30.983 Y5.812 Z5.2 F30000
G1 X58.848 Y6.401 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X57.052 Y6.401 E.05957
G1 X57.052 Y6.09 E.01032
G1 X58.848 Y6.09 E.05957
G1 X58.848 Y6.341 E.00833
G1 X59.24 Y6.686 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4076.548
M204 S5000
G1 X59.24 Y6.793 E.0033
G1 F2880
G1 X56.66 Y6.793 E.07928
G1 F4076.548
G1 X56.66 Y6.686 E.0033
G1 F6225
G1 X56.66 Y6.286 E.01229
G1 X56.66 Y5.698 E.01807
G1 X59.24 Y5.698 E.07928
G1 X59.24 Y6.626 E.02852
; WIPE_START
G1 F12000
M204 S10000
G1 X59.24 Y6.793 E-.06359
G1 X57.407 Y6.793 E-.69641
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.401 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X51.602 Y6.401 E.05957
G1 X51.602 Y4.9 E.04979
G1 X53.398 Y4.9 E.05957
G1 X53.398 Y6.341 E.0478
G1 X53.79 Y6.686 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4076.306
M204 S5000
G1 X53.79 Y6.793 E.0033
G1 F2880
G1 X51.21 Y6.793 E.07928
G1 F4076.306
G1 X51.21 Y6.686 E.0033
G1 F6225
G1 X51.21 Y6.286 E.01229
G1 X51.21 Y5.886 E.01229
G1 X51.21 Y4.508 E.04234
G1 X53.79 Y4.508 E.07928
G1 X53.79 Y6.626 E.06508
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.793 E-.06358
G1 X51.957 Y6.793 E-.69642
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.009 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6225
G1 X53.006 Y6.009 E.03109
G1 X53.006 Y5.292 E.02203
G1 X51.994 Y5.292 E.03109
G1 X51.994 Y5.949 E.02018
G1 X52.353 Y5.651 F30000
; LINE_WIDTH: 0.38276
G1 F6225
G1 X52.587 Y5.651 E.0065
; WIPE_START
G1 F15000
G1 X52.353 Y5.651 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.386 Y13.213 Z5.2 F30000
G1 X53.398 Y13.3 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X51.602 Y13.3 E.05957
G1 X51.602 Y11.799 E.04979
G1 X53.398 Y11.799 E.05957
G1 X53.398 Y13.24 E.0478
G1 X53.79 Y13.692 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6225
M204 S5000
G1 X51.21 Y13.692 E.07928
G1 X51.21 Y12.314 E.04234
G1 X51.21 Y11.914 E.01229
G1 X51.21 Y11.514 E.01229
G1 F4076.548
G1 X51.21 Y11.407 E.0033
G1 F2880
G1 X53.79 Y11.407 E.07928
G1 F4076.669
G1 X53.79 Y11.514 E.0033
G1 F6225
G1 X53.79 Y11.914 E.01229
G1 X53.79 Y12.314 E.01229
G1 X53.79 Y13.632 E.04049
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.678 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.908 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6225
G1 X53.006 Y12.908 E.03109
G1 X53.006 Y12.191 E.02203
G1 X51.994 Y12.191 E.03109
G1 X51.994 Y12.848 E.02019
G1 X52.353 Y12.549 F30000
; LINE_WIDTH: 0.38278
G1 F6225
G1 X52.587 Y12.549 E.0065
; WIPE_START
G1 F15000
G1 X52.353 Y12.549 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.133 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X57.052 Y11.799 E.21012
G1 X58.848 Y11.799 E.05957
G1 X58.848 Y18.133 E.21012
G1 X57.112 Y18.133 E.05758
G1 X56.66 Y18.525 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6225
M204 S5000
G1 X56.66 Y12.314 E.19085
G1 X56.66 Y11.914 E.01229
G1 X56.66 Y11.514 E.01229
G1 F4076.79
G1 X56.66 Y11.407 E.0033
G1 F2880
G1 X59.24 Y11.407 E.07928
G1 F4076.79
G1 X59.24 Y11.514 E.0033
G1 F6225
G1 X59.24 Y11.914 E.01229
G1 X59.24 Y12.314 E.01229
G1 X59.24 Y18.525 E.19085
G1 X56.72 Y18.525 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.701 Y16.525 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.741 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6225
G1 X58.456 Y17.741 E.03109
G1 X58.456 Y12.191 E.17054
G1 X57.444 Y12.191 E.03109
G1 X57.444 Y17.681 E.16869
G1 X57.791 Y17.394 F30000
; LINE_WIDTH: 0.36025
G1 F6225
G1 X58.109 Y17.394 E.00821
G1 X58.109 Y12.538 E.12556
G1 X57.791 Y12.538 E.00821
G1 X57.791 Y17.334 E.12401
; WIPE_START
G1 F15000
G1 X57.791 Y15.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.541 Y22.929 Z5.2 F30000
G1 X58.848 Y26.039 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6225
G1 X57.052 Y26.039 E.05957
G1 X57.052 Y24.067 E.0654
G1 X58.848 Y24.067 E.05957
G1 X58.848 Y25.979 E.06341
G1 X59.24 Y26.428 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6225
M204 S5000
G1 X56.66 Y26.428 E.07928
G1 X56.66 Y23.675 E.08461
G1 X59.24 Y23.675 E.07928
G1 X59.24 Y26.368 E.08276
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.415 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.459 Z5.2 F30000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6225
G1 X57.444 Y25.647 E.03649
G1 X58.456 Y25.647 E.03109
G1 X58.456 Y24.459 E.03649
G1 X57.504 Y24.459 E.02924
G1 X57.791 Y24.806 F30000
; LINE_WIDTH: 0.36025
G1 F6225
G1 X57.791 Y25.299 E.01275
G1 X58.109 Y25.299 E.00821
G1 X58.109 Y24.806 E.01275
G1 X57.851 Y24.806 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.806 E-.1253
G1 X58.109 Y25.299 E-.24009
G1 X57.791 Y25.299 E-.15451
G1 X57.791 Y24.806 E-.24009
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/58
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
G1 X21.398 Y38.298
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.402 E.85901
G1 X22.602 Y12.402 E.06634
G1 X22.602 Y11.62 E.02596
G1 X24.398 Y11.62 E.05957
G1 X24.398 Y13.228 E.05336
G1 X21.398 Y13.228 E.09952
G1 X21.398 Y38.238 E.82962
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6398
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.01 E.8198
G1 X22.21 Y12.01 E.06145
G1 X22.21 Y11.766 E.00751
G1 X22.21 Y11.366 E.01229
G1 F4007.487
G1 X22.21 Y11.228 E.00424
G1 F2520
G1 X24.79 Y11.228 E.07928
G1 F4007.487
G1 X24.79 Y11.366 E.00424
G1 F6398
G1 X24.79 Y11.766 E.01229
G1 X24.79 Y12.166 E.01229
G1 X24.79 Y13.62 E.0447
G1 X21.79 Y13.62 E.09218
G1 X21.79 Y38.63 E.76848
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.4318
G1 F6398
G1 X21 Y13.025 E.79443
G1 X21.021 Y12.934 E.00296
; LINE_WIDTH: 0.495653
G1 X21.043 Y12.843 E.00345
; LINE_WIDTH: 0.503206
G1 X21.119 Y12.829 E.00289
; LINE_WIDTH: 0.475722
G1 X21.194 Y12.815 E.00272
; LINE_WIDTH: 0.461961
G1 X22.805 Y12.815 E.05501
G1 X24.006 Y12.836 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X24.006 Y12.012 E.02533
G1 X22.994 Y12.012 E.03109
G1 X23.009 Y12.192 E.00556
G1 X23.063 Y12.2 E.00167
G1 X23.198 Y12.416 E.00782
G1 X23.198 Y12.836 E.01292
G1 X23.946 Y12.836 E.02299
; WIPE_START
G1 F15000
G1 X23.198 Y12.836 E-.28436
G1 X23.198 Y12.416 E-.15973
G1 X23.063 Y12.2 E-.09672
G1 X23.009 Y12.192 E-.02066
G1 X22.994 Y12.012 E-.06878
G1 X23.336 Y12.012 E-.12975
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.58 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X22.602 Y4.972 E.05336
G1 X24.398 Y4.972 E.05957
G1 X24.398 Y6.58 E.05336
G1 X22.662 Y6.58 E.05758
G1 X22.21 Y6.834 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6398
M204 S5000
G1 X22.21 Y4.58 E.06928
G1 X24.79 Y4.58 E.07928
G1 X24.79 Y6.034 E.0447
G1 X24.79 Y6.434 E.01229
G1 X24.79 Y6.834 E.01229
G1 F4007.607
G1 X24.79 Y6.972 E.00424
G1 F2520
G1 X22.21 Y6.972 E.07928
G1 F3319.322
G1 X22.21 Y6.894 E.0024
; WIPE_START
M204 S10000
G1 X22.21 Y4.894 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.188 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X24.006 Y5.364 E.02533
G1 X22.994 Y5.364 E.03109
G1 X22.994 Y6.188 E.02533
G1 X23.946 Y6.188 E.02924
G1 X23.406 Y5.776 F30000
; LINE_WIDTH: 0.49035
G1 F6398
G1 X23.534 Y5.776 E.00464
; WIPE_START
G1 F14080.414
G1 X23.406 Y5.776 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X31.037 Y5.949 Z5.4 F30000
G1 X58.848 Y6.58 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X57.052 Y6.58 E.05957
G1 X57.052 Y6.189 E.01299
G1 X58.848 Y6.189 E.05957
G1 X58.848 Y6.52 E.011
G1 X59.24 Y6.834 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4007.367
M204 S5000
G1 X59.24 Y6.972 E.00424
G1 F2520
G1 X56.66 Y6.972 E.07928
G1 F4007.367
G1 X56.66 Y6.834 E.00424
G1 F6398
G1 X56.66 Y6.434 E.01229
G1 X56.66 Y6.034 E.01229
G1 X56.66 Y5.797 E.00731
M73 P81 R3
G1 X59.24 Y5.797 E.07928
G1 X59.24 Y6.774 E.03004
; WIPE_START
G1 F12000
M204 S10000
G1 X59.24 Y6.972 E-.07529
G1 X57.438 Y6.972 E-.68471
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.58 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X51.602 Y6.58 E.05957
G1 X51.602 Y4.972 E.05336
G1 X53.398 Y4.972 E.05957
G1 X53.398 Y6.52 E.05137
G1 X53.79 Y6.834 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4007.607
M204 S5000
G1 X53.79 Y6.972 E.00424
G1 F2520
G1 X51.21 Y6.972 E.07928
G1 F4007.607
G1 X51.21 Y6.834 E.00424
G1 F6398
G1 X51.21 Y6.434 E.01229
G1 X51.21 Y6.034 E.01229
G1 X51.21 Y4.58 E.0447
G1 X53.79 Y4.58 E.07928
G1 X53.79 Y6.774 E.06743
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y6.972 E-.0753
G1 X51.988 Y6.972 E-.6847
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.188 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X53.006 Y6.188 E.03109
G1 X53.006 Y5.364 E.02533
G1 X51.994 Y5.364 E.03109
G1 X51.994 Y6.128 E.02349
G1 X52.406 Y5.776 F30000
; LINE_WIDTH: 0.49035
G1 F6398
G1 X52.534 Y5.776 E.00464
; WIPE_START
G1 F14080.414
G1 X52.406 Y5.776 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y13.228 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X51.602 Y13.228 E.05957
G1 X51.602 Y11.62 E.05336
G1 X53.398 Y11.62 E.05957
M73 P81 R2
G1 X53.398 Y13.168 E.05137
G1 X53.79 Y13.62 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6398
M204 S5000
G1 X51.21 Y13.62 E.07928
G1 X51.21 Y12.166 E.0447
G1 X51.21 Y11.766 E.01229
G1 X51.21 Y11.366 E.01229
G1 F4007.607
G1 X51.21 Y11.228 E.00424
G1 F2520
G1 X53.79 Y11.228 E.07928
G1 F4007.607
G1 X53.79 Y11.366 E.00424
G1 F6398
G1 X53.79 Y11.766 E.01229
G1 X53.79 Y12.166 E.01229
G1 X53.79 Y13.56 E.04285
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.607 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.836 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X53.006 Y12.836 E.03109
G1 X53.006 Y12.012 E.02533
G1 X51.994 Y12.012 E.03109
G1 X51.994 Y12.776 E.02349
G1 X52.406 Y12.424 F30000
; LINE_WIDTH: 0.49035
G1 F6398
G1 X52.534 Y12.424 E.00464
; WIPE_START
G1 F14080.414
G1 X52.406 Y12.424 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.035 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X57.052 Y11.62 E.21281
G1 X58.848 Y11.62 E.05957
G1 X58.848 Y18.035 E.21281
G1 X57.112 Y18.035 E.05758
G1 X56.66 Y18.427 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6398
M204 S5000
G1 X56.66 Y12.166 E.1924
G1 X56.66 Y11.766 E.01229
G1 X56.66 Y11.366 E.01229
G1 F4007.367
G1 X56.66 Y11.228 E.00424
G1 F2520
G1 X59.24 Y11.228 E.07928
G1 F4007.367
G1 X59.24 Y11.366 E.00424
G1 F6398
G1 X59.24 Y11.766 E.01229
G1 X59.24 Y12.166 E.01229
G1 X59.24 Y18.427 E.1924
G1 X56.72 Y18.427 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.701 Y16.427 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.643 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X58.456 Y17.643 E.03109
G1 X58.456 Y12.012 E.17303
G1 X57.444 Y12.012 E.03109
G1 X57.444 Y17.583 E.17119
G1 X57.791 Y17.296 F30000
; LINE_WIDTH: 0.36025
G1 F6398
G1 X58.109 Y17.296 E.00821
G1 X58.109 Y12.359 E.12766
G1 X57.791 Y12.359 E.00821
G1 X57.791 Y17.236 E.12611
; WIPE_START
G1 F15000
G1 X57.791 Y15.236 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.532 Y22.832 Z5.4 F30000
G1 X58.848 Y26.078 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6398
G1 X57.052 Y26.078 E.05957
G1 X57.052 Y24.165 E.06347
G1 X58.848 Y24.165 E.05957
G1 X58.848 Y26.018 E.06148
G1 X59.24 Y26.47 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6398
M204 S5000
G1 X56.66 Y26.47 E.07928
G1 X56.66 Y23.773 E.08289
G1 X59.24 Y23.773 E.07928
G1 X59.24 Y26.41 E.08104
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.457 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.557 Z5.4 F30000
G1 Z5
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6398
G1 X57.444 Y25.686 E.0347
G1 X58.456 Y25.686 E.03109
G1 X58.456 Y24.557 E.0347
G1 X57.504 Y24.557 E.02924
G1 X57.791 Y24.904 F30000
; LINE_WIDTH: 0.36025
G1 F6398
G1 X57.791 Y25.339 E.01124
G1 X58.109 Y25.339 E.00821
G1 X58.109 Y24.904 E.01124
G1 X57.851 Y24.904 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 5.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.904 E-.1354
G1 X58.109 Y25.339 E-.22881
G1 X57.791 Y25.339 E-.16697
G1 X57.791 Y24.904 E-.22881
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/58
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
G1 X21.398 Y38.298
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.502 E.8557
G1 X22.602 Y12.502 E.06634
G1 X22.602 Y11.42 E.03588
G1 X24.398 Y11.42 E.05957
G1 X24.398 Y13.14 E.05703
G1 X21.398 Y13.14 E.09952
G1 X21.398 Y38.238 E.83256
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6697
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.11 E.81673
G1 X22.21 Y12.11 E.06145
G1 X22.21 Y11.587 E.01609
G1 X22.21 Y11.187 E.01229
G1 F3779.695
G1 X22.21 Y11.028 E.00486
G1 F2160
G1 X24.79 Y11.028 E.07928
G1 F3779.695
G1 X24.79 Y11.187 E.00486
G1 F6697
G1 X24.79 Y11.587 E.01229
G1 X24.79 Y11.987 E.01229
G1 X24.79 Y13.532 E.04748
G1 X21.79 Y13.532 E.09218
G1 X21.79 Y38.63 E.7712
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.431687
G1 F6697
G1 X21 Y12.936 E.797
G1 X21.002 Y12.902 E.0011
G1 X21.05 Y12.881 E.00166
; LINE_WIDTH: 0.37427
G1 X21.098 Y12.861 E.00141
; LINE_WIDTH: 0.333922
G1 X21.146 Y12.841 E.00124
; LINE_WIDTH: 0.293574
G1 X21.194 Y12.821 E.00107
; LINE_WIDTH: 0.273373
G1 X22.805 Y12.821 E.03025
G1 X24.006 Y12.748 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
G1 X24.006 Y11.813 E.02873
G1 X22.994 Y11.813 E.03109
G1 X23.009 Y12.292 E.01474
G1 X23.116 Y12.325 E.00344
G1 X23.198 Y12.481 E.00539
G1 X23.198 Y12.748 E.0082
G1 X23.946 Y12.748 E.02299
G1 X23.607 Y12.189 F30000
; LINE_WIDTH: 0.5226
G1 F6697
G2 X23.607 Y12.293 I-.03 J.052 E.00982
; WIPE_START
G1 F13133.756
G1 X23.548 Y12.293 E-.18992
G1 X23.518 Y12.241 E-.19003
G1 X23.548 Y12.189 E-.19003
G1 X23.607 Y12.189 E-.19002
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y6.78 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X22.602 Y5.06 E.05703
G1 X24.398 Y5.06 E.05957
G1 X24.398 Y6.78 E.05703
G1 X22.662 Y6.78 E.05758
G1 X22.21 Y7.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6697
M204 S5000
G1 X22.21 Y4.668 E.07206
G1 X24.79 Y4.668 E.07928
G1 X24.79 Y6.213 E.04748
G1 X24.79 Y6.613 E.01229
G1 X24.79 Y7.013 E.01229
G1 F3779.579
G1 X24.79 Y7.172 E.00486
G1 F2160
G1 X22.21 Y7.172 E.07928
G1 F3112.098
G1 X22.21 Y7.073 E.00302
; WIPE_START
M204 S10000
G1 X22.21 Y5.073 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.387 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
G1 X24.006 Y5.452 E.02873
G1 X22.994 Y5.452 E.03109
G1 X22.994 Y6.387 E.02873
G1 X23.946 Y6.387 E.02924
; WIPE_START
G1 F15000
G1 X22.994 Y6.387 E-.36167
G1 X22.994 Y5.452 E-.3553
G1 X23.107 Y5.452 E-.04304
; WIPE_END
G1 E-.04 F1800
G1 X30.735 Y5.736 Z5.6 F30000
G1 X58.848 Y6.78 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X57.052 Y6.78 E.05957
G1 X57.052 Y6.305 E.01575
G1 X58.848 Y6.305 E.05957
G1 X58.848 Y6.72 E.01376
G1 X59.24 Y7.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3779.579
M204 S5000
G1 X59.24 Y7.172 E.00486
G1 F2160
G1 X56.66 Y7.172 E.07928
G1 F3779.579
G1 X56.66 Y7.013 E.00486
G1 F6697
G1 X56.66 Y6.613 E.01229
G1 X56.66 Y6.213 E.01229
G1 X56.66 Y5.913 E.00924
G1 X59.24 Y5.913 E.07928
G1 X59.24 Y6.953 E.03198
M204 S10000
G1 X58.644 Y6.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.11059
G1 F6697
G1 X57.256 Y6.542 E.00766
; WIPE_START
G1 F15000
G1 X58.644 Y6.542 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.78 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X51.602 Y6.78 E.05957
G1 X51.602 Y5.06 E.05703
G1 X53.398 Y5.06 E.05957
G1 X53.398 Y6.72 E.05504
G1 X53.79 Y7.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3779.579
M204 S5000
G1 X53.79 Y7.172 E.00486
G1 F2160
G1 X51.21 Y7.172 E.07928
G1 F3779.579
G1 X51.21 Y7.013 E.00486
G1 F6697
G1 X51.21 Y6.613 E.01229
G1 X51.21 Y6.213 E.01229
G1 X51.21 Y4.668 E.04748
G1 X53.79 Y4.668 E.07928
G1 X53.79 Y6.953 E.07022
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y7.172 E-.08289
G1 X52.008 Y7.172 E-.67711
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.387 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
G1 X53.006 Y6.387 E.03109
G1 X53.006 Y5.452 E.02873
G1 X51.994 Y5.452 E.03109
G1 X51.994 Y6.327 E.02689
; WIPE_START
G1 F15000
G1 X51.994 Y5.452 E-.3325
G1 X53.006 Y5.452 E-.38447
G1 X53.006 Y5.566 E-.04304
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y13.14 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X51.602 Y13.14 E.05957
G1 X51.602 Y11.42 E.05703
G1 X53.398 Y11.42 E.05957
G1 X53.398 Y13.08 E.05504
G1 X53.79 Y13.532 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6697
M204 S5000
G1 X51.21 Y13.532 E.07928
G1 X51.21 Y11.987 E.04748
G1 X51.21 Y11.587 E.01229
G1 X51.21 Y11.187 E.01229
G1 F3779.695
G1 X51.21 Y11.028 E.00486
G1 F2160
G1 X53.79 Y11.028 E.07928
G1 F3779.695
G1 X53.79 Y11.187 E.00486
G1 F6697
G1 X53.79 Y11.587 E.01229
G1 X53.79 Y11.987 E.01229
G1 X53.79 Y13.472 E.04563
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.518 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.748 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
G1 X53.006 Y12.748 E.03109
G1 X53.006 Y11.813 E.02873
G1 X51.994 Y11.813 E.03109
G1 X51.994 Y12.688 E.02689
; WIPE_START
G1 F15000
G1 X51.994 Y11.813 E-.3325
G1 X53.006 Y11.813 E-.38447
G1 X53.006 Y11.926 E-.04304
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.956 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X57.052 Y11.42 E.21679
G1 X58.848 Y11.42 E.05957
G1 X58.848 Y17.956 E.21679
G1 X57.112 Y17.956 E.05758
G1 X56.66 Y18.348 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6697
M204 S5000
G1 X56.66 Y11.987 E.19547
G1 X56.66 Y11.587 E.01229
G1 X56.66 Y11.187 E.01229
G1 F3779.695
G1 X56.66 Y11.028 E.00486
G1 F2160
G1 X59.24 Y11.028 E.07928
G1 F3779.695
G1 X59.24 Y11.187 E.00486
G1 F6697
G1 X59.24 Y11.587 E.01229
G1 X59.24 Y11.987 E.01229
G1 X59.24 Y18.348 E.19547
G1 X56.72 Y18.348 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.701 Y16.348 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.564 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
G1 X58.456 Y17.564 E.03109
G1 X58.456 Y11.813 E.17671
G1 X57.444 Y11.813 E.03109
G1 X57.444 Y17.504 E.17487
G1 X57.791 Y17.217 F30000
; LINE_WIDTH: 0.36025
G1 F6697
G1 X58.109 Y17.217 E.00821
G1 X58.109 Y12.16 E.13076
G1 X57.791 Y12.16 E.00821
G1 X57.791 Y17.157 E.12921
; WIPE_START
G1 F15000
G1 X57.791 Y15.157 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.524 Y22.754 Z5.6 F30000
G1 X58.848 Y26.118 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6697
G1 X57.052 Y26.118 E.05957
G1 X57.052 Y24.244 E.06216
G1 X58.848 Y24.244 E.05957
G1 X58.848 Y26.058 E.06017
G1 X59.24 Y26.51 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6697
M204 S5000
G1 X56.66 Y26.51 E.07928
G1 X56.66 Y23.852 E.08167
G1 X59.24 Y23.852 E.07928
G1 X59.24 Y26.45 E.07983
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.497 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.636 Z5.6 F30000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6697
M73 P82 R2
G1 X57.444 Y25.726 E.03348
G1 X58.456 Y25.726 E.03109
G1 X58.456 Y24.636 E.03348
G1 X57.504 Y24.636 E.02924
G1 X57.791 Y24.983 F30000
; LINE_WIDTH: 0.36025
G1 F6697
G1 X57.791 Y25.379 E.01022
G1 X58.109 Y25.379 E.00821
G1 X58.109 Y24.983 E.01022
G1 X57.851 Y24.983 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 5.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.983 E-.14324
G1 X58.109 Y25.379 E-.22006
G1 X57.791 Y25.379 E-.17664
G1 X57.791 Y24.983 E-.22006
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 27/58
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
G1 X22.602 Y6.98
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X22.602 Y5.155 E.06052
G1 X24.398 Y5.155 E.05957
G1 X24.398 Y6.98 E.06052
G1 X22.662 Y6.98 E.05758
G1 X22.21 Y7.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6982
M204 S5000
G1 X22.21 Y4.763 E.07527
G1 X24.79 Y4.763 E.07928
G1 X24.79 Y6.413 E.05069
G1 X24.79 Y6.813 E.01229
G1 X24.79 Y7.213 E.01229
G1 F3789.617
G1 X24.79 Y7.372 E.00489
G1 F2160
G1 X22.21 Y7.372 E.07928
G1 F3121.207
G1 X22.21 Y7.273 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y5.273 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.587 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X24.006 Y5.547 E.03197
G1 X22.994 Y5.547 E.03109
G1 X22.994 Y6.587 E.03197
G1 X23.946 Y6.587 E.02924
G1 X23.659 Y6.24 F30000
; LINE_WIDTH: 0.36026
G1 F6982
G1 X23.659 Y5.894 E.00895
G1 X23.341 Y5.894 E.00821
G1 X23.341 Y6.24 E.00895
G1 X23.599 Y6.24 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y6.24 E-.15441
G1 X23.341 Y5.894 E-.20759
G1 X23.659 Y5.894 E-.19041
G1 X23.659 Y6.24 E-.20759
; WIPE_END
G1 E-.04 F1800
G1 X23.122 Y13.854 Z5.8 F30000
G1 X21.398 Y38.298 Z5.8
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X20.602 Y38.298 E.0264
G1 X20.602 Y12.602 E.85238
G1 X22.602 Y12.602 E.06634
G1 X22.602 Y11.22 E.04583
G1 X24.398 Y11.22 E.05957
G1 X24.398 Y13.045 E.06052
G1 X21.398 Y13.045 E.09952
G1 X21.398 Y38.238 E.8357
G1 X21.79 Y38.69 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6982
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.21 E.81366
G1 X22.21 Y12.21 E.06145
G1 X22.21 Y11.787 E.01299
G1 X22.21 Y11.387 E.01229
G1 X22.21 Y10.987 E.01229
G1 F3789.734
G1 X22.21 Y10.828 E.00489
G1 F2160
G1 X24.79 Y10.828 E.07928
G1 F3789.734
G1 X24.79 Y10.987 E.00489
G1 F6982
G1 X24.79 Y11.387 E.01229
G1 X24.79 Y11.787 E.01229
G1 X24.79 Y13.437 E.05069
G1 X21.79 Y13.437 E.09218
G1 X21.79 Y38.63 E.77411
M204 S10000
G1 X21 Y38.094 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.43172
G1 F6982
G1 X21 Y12.806 E.80121
G1 X24.006 Y12.653 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X24.006 Y11.613 E.03197
G1 X22.994 Y11.613 E.03109
G1 X22.994 Y12.653 E.03197
G1 X23.946 Y12.653 E.02924
G1 X23.659 Y12.306 F30000
; LINE_WIDTH: 0.36026
G1 F6982
G1 X23.659 Y11.96 E.00895
G1 X23.341 Y11.96 E.00821
G1 X23.341 Y12.306 E.00895
G1 X23.599 Y12.306 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y12.306 E-.1544
G1 X23.341 Y11.96 E-.2076
G1 X23.659 Y11.96 E-.1904
G1 X23.659 Y12.306 E-.2076
; WIPE_END
G1 E-.04 F1800
G1 X30.761 Y15.1 Z5.8 F30000
G1 X58.848 Y26.152 Z5.8
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X57.052 Y26.152 E.05957
G1 X57.052 Y24.307 E.06121
G1 X58.848 Y24.307 E.05957
G1 X58.848 Y26.092 E.05922
G1 X59.24 Y26.544 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6982
M204 S5000
G1 X56.66 Y26.544 E.07928
G1 X56.66 Y23.915 E.08079
G1 X57.456 Y23.915 E.02447
G1 X59.24 Y23.915 E.05481
G1 X59.24 Y26.484 E.07895
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.531 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.699 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X57.444 Y25.76 E.0326
G1 X58.456 Y25.76 E.03109
G1 X58.456 Y24.699 E.0326
G1 X57.504 Y24.699 E.02924
G1 X57.791 Y25.046 F30000
; LINE_WIDTH: 0.36025
G1 F6982
G1 X57.791 Y25.413 E.00948
G1 X58.109 Y25.413 E.00821
G1 X58.109 Y25.046 E.00948
G1 X57.851 Y25.046 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y25.046 E-.14951
G1 X58.109 Y25.413 E-.21306
G1 X57.791 Y25.413 E-.18437
G1 X57.791 Y25.046 E-.21306
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.893 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X57.052 Y11.22 E.22135
G1 X58.848 Y11.22 E.05957
G1 X58.848 Y17.893 E.22135
G1 X57.112 Y17.893 E.05758
G1 X56.66 Y18.285 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6982
M204 S5000
G1 X56.66 Y11.787 E.19966
G1 X56.66 Y11.387 E.01229
G1 X56.66 Y10.987 E.01229
G1 F3790.902
G1 X56.66 Y10.828 E.00489
G1 F2160
G1 X59.24 Y10.828 E.07928
G1 F3790.902
G1 X59.24 Y10.987 E.00489
G1 F6982
G1 X59.24 Y11.387 E.01229
G1 X59.24 Y11.787 E.01229
G1 X59.24 Y18.285 E.19966
G1 X56.72 Y18.285 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.702 Y16.285 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.501 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X58.456 Y17.501 E.03109
G1 X58.456 Y11.612 E.18094
G1 X57.444 Y11.612 E.03109
G1 X57.444 Y17.441 E.1791
G1 X57.791 Y17.154 F30000
; LINE_WIDTH: 0.36025
G1 F6982
G1 X58.109 Y17.154 E.00821
G1 X58.109 Y11.96 E.13432
G1 X57.791 Y11.96 E.00821
G1 X57.791 Y17.094 E.13277
; WIPE_START
G1 F15000
G1 X57.791 Y15.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y13.045 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X51.602 Y13.045 E.05957
G1 X51.602 Y11.22 E.06052
G1 X53.398 Y11.22 E.05957
G1 X53.398 Y12.985 E.05853
G1 X53.79 Y13.437 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F6982
M204 S5000
G1 X51.21 Y13.437 E.07928
G1 X51.21 Y11.787 E.05069
G1 X51.21 Y11.387 E.01229
G1 X51.21 Y10.987 E.01229
G1 F3789.734
G1 X51.21 Y10.828 E.00489
G1 F2160
G1 X53.79 Y10.828 E.07928
G1 F3789.734
G1 X53.79 Y10.987 E.00489
G1 F6982
G1 X53.79 Y11.387 E.01229
G1 X53.79 Y11.787 E.01229
G1 X53.79 Y13.377 E.04885
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.424 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.653 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X53.006 Y12.653 E.03109
G1 X53.006 Y11.613 E.03197
G1 X51.994 Y11.613 E.03109
G1 X51.994 Y12.593 E.03012
G1 X52.341 Y12.306 F30000
; LINE_WIDTH: 0.36025
G1 F6982
G1 X52.659 Y12.306 E.00821
G1 X52.659 Y11.96 E.00895
G1 X52.341 Y11.96 E.00821
G1 X52.341 Y12.246 E.00739
; WIPE_START
G1 F15000
G1 X52.341 Y11.96 E-.17159
G1 X52.659 Y11.96 E-.19041
G1 X52.659 Y12.306 E-.20759
G1 X52.341 Y12.306 E-.19041
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y6.98 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X51.602 Y6.98 E.05957
G1 X51.602 Y5.155 E.06052
G1 X53.398 Y5.155 E.05957
G1 X53.398 Y6.92 E.05853
G1 X53.79 Y7.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y7.372 E.00489
G1 F2160
G1 X51.21 Y7.372 E.07928
G1 F3789.617
G1 X51.21 Y7.213 E.00489
G1 F6982
G1 X51.21 Y6.813 E.01229
G1 X51.21 Y6.413 E.01229
G1 X51.21 Y4.763 E.05069
G1 X53.79 Y4.763 E.07928
G1 X53.79 Y7.153 E.07343
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y7.372 E-.08322
G1 X52.009 Y7.372 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.587 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F6982
G1 X53.006 Y6.587 E.03109
G1 X53.006 Y5.547 E.03197
G1 X51.994 Y5.547 E.03109
G1 X51.994 Y6.527 E.03012
G1 X52.341 Y6.24 F30000
; LINE_WIDTH: 0.36025
G1 F6982
G1 X52.659 Y6.24 E.00821
G1 X52.659 Y5.894 E.00895
G1 X52.341 Y5.894 E.00821
G1 X52.341 Y6.18 E.00739
; WIPE_START
G1 F15000
G1 X52.341 Y5.894 E-.17159
G1 X52.659 Y5.894 E-.19041
G1 X52.659 Y6.24 E-.20759
G1 X52.341 Y6.24 E-.19041
; WIPE_END
G1 E-.04 F1800
G1 X58.848 Y6.98 Z5.8 F30000
G1 Z5.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F6982
G1 X57.052 Y6.98 E.05957
G1 X57.052 Y6.438 E.01795
G1 X58.848 Y6.438 E.05957
G1 X58.848 Y6.92 E.01596
G1 X59.24 Y7.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y7.372 E.00489
G1 F2160
G1 X56.66 Y7.372 E.07928
G1 F3789.617
G1 X56.66 Y7.213 E.00489
G1 F6982
G1 X56.66 Y6.813 E.01229
G1 X56.66 Y6.413 E.01229
G1 X56.66 Y6.046 E.01125
G1 X59.24 Y6.046 E.07928
G1 X59.24 Y7.153 E.03399
M204 S10000
G1 X58.644 Y6.709 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.17694
G1 F6982
G1 X57.256 Y6.709 E.01517
; CHANGE_LAYER
; Z_HEIGHT: 5.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.644 Y6.709 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 28/58
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
G1 X23.318 Y12.938
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X23.318 Y12.343 E.01976
G1 X23.078 Y12.343 E.00796
G1 X23.078 Y11.02 E.04386
G1 X24.398 Y11.02 E.04379
G1 X24.398 Y12.938 E.06362
G1 X23.378 Y12.938 E.03384
; WIPE_START
G1 F15476.087
G1 X23.318 Y12.343 E-.22747
G1 X23.078 Y12.343 E-.09123
G1 X23.078 Y11.181 E-.4413
; WIPE_END
G1 E-.04 F1800
G1 X22.721 Y18.805 Z6 F30000
G1 X21.79 Y38.69 Z6
G1 Z5.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8292
M204 S5000
G1 X20.21 Y38.69 E.04855
G1 X20.21 Y12.31 E.81058
G1 X22.21 Y12.31 E.06145
G1 X22.21 Y11.587 E.0222
G1 X22.21 Y11.187 E.01229
G1 X22.21 Y10.787 E.01229
G1 F3789.734
G1 X22.21 Y10.628 E.00489
G1 F2160
G1 X24.79 Y10.628 E.07928
G1 F3789.734
G1 X24.79 Y10.787 E.00489
G1 F8292
G1 X24.79 Y11.187 E.01229
G1 X24.79 Y11.587 E.01229
G1 X24.79 Y13.33 E.05356
G1 X21.79 Y13.33 E.09218
G1 X21.79 Y38.63 E.77739
M204 S10000
G1 X20.926 Y38.483 F30000
; FEATURE: Top surface
G1 F8292
M204 S2000
G1 X21.583 Y37.826 E.02854
G1 X21.583 Y37.293
G1 X20.417 Y38.458 E.05063
G1 X20.417 Y37.925
G1 X21.583 Y36.759 E.05063
G1 X21.583 Y36.226
G1 X20.417 Y37.391 E.05063
G1 X20.417 Y36.858
G1 X21.583 Y35.693 E.05063
G1 X21.583 Y35.16
G1 X20.417 Y36.325 E.05063
G1 X20.417 Y35.792
G1 X21.583 Y34.626 E.05063
G1 X21.583 Y34.093
G1 X20.417 Y35.258 E.05063
G1 X20.417 Y34.725
G1 X21.583 Y33.56 E.05063
G1 X21.583 Y33.027
G1 X20.417 Y34.192 E.05063
G1 X20.417 Y33.659
G1 X21.583 Y32.493 E.05063
G1 X21.583 Y31.96
G1 X20.417 Y33.125 E.05063
G1 X20.417 Y32.592
G1 X21.583 Y31.427 E.05063
G1 X21.583 Y30.894
G1 X20.417 Y32.059 E.05063
G1 X20.417 Y31.526
G1 X21.583 Y30.36 E.05063
G1 X21.583 Y29.827
G1 X20.417 Y30.992 E.05063
G1 X20.417 Y30.459
G1 X21.583 Y29.294 E.05063
G1 X21.583 Y28.761
G1 X20.417 Y29.926 E.05063
G1 X20.417 Y29.393
G1 X21.583 Y28.227 E.05063
G1 X21.583 Y27.694
G1 X20.417 Y28.859 E.05063
G1 X20.417 Y28.326
G1 X21.583 Y27.161 E.05063
G1 X21.583 Y26.628
G1 X20.417 Y27.793 E.05063
G1 X20.417 Y27.259
G1 X21.583 Y26.094 E.05063
G1 X21.583 Y25.561
G1 X20.417 Y26.726 E.05063
G1 X20.417 Y26.193
G1 X21.583 Y25.028 E.05063
G1 X21.583 Y24.494
G1 X20.417 Y25.66 E.05063
G1 X20.417 Y25.126
G1 X21.583 Y23.961 E.05063
G1 X21.583 Y23.428
G1 X20.417 Y24.593 E.05063
G1 X20.417 Y24.06
G1 X21.583 Y22.895 E.05063
G1 X21.583 Y22.361
G1 X20.417 Y23.527 E.05063
G1 X20.417 Y22.993
G1 X21.583 Y21.828 E.05063
G1 X21.583 Y21.295
G1 X20.417 Y22.46 E.05063
G1 X20.417 Y21.927
G1 X21.583 Y20.762 E.05063
G1 X21.583 Y20.228
G1 X20.417 Y21.394 E.05063
G1 X20.417 Y20.86
G1 X21.583 Y19.695 E.05063
G1 X21.583 Y19.162
G1 X20.417 Y20.327 E.05063
G1 X20.417 Y19.794
G1 X21.583 Y18.629 E.05063
G1 X21.583 Y18.095
G1 X20.417 Y19.261 E.05063
G1 X20.417 Y18.727
M73 P83 R2
G1 X21.583 Y17.562 E.05063
G1 X21.583 Y17.029
G1 X20.417 Y18.194 E.05063
G1 X20.417 Y17.661
G1 X21.583 Y16.496 E.05063
G1 X21.583 Y15.962
G1 X20.417 Y17.128 E.05063
G1 X20.417 Y16.594
G1 X21.583 Y15.429 E.05063
G1 X21.583 Y14.896
G1 X20.417 Y16.061 E.05063
G1 X20.417 Y15.528
G1 X21.583 Y14.363 E.05063
G1 X21.583 Y13.829
G1 X20.417 Y14.995 E.05063
G1 X20.417 Y14.461
G1 X21.583 Y13.296 E.05063
G1 X22.289 Y13.123
G1 X22.855 Y12.557 E.02461
G1 X22.417 Y12.461
G1 X22.855 Y12.023 E.01903
G1 X22.795 Y11.551
G1 X22.417 Y11.928 E.0164
G1 X22.361 Y12.517
G1 X21.756 Y13.123 E.02631
G1 X21.828 Y12.517
G1 X20.417 Y13.928 E.0613
G1 X20.417 Y13.395
G1 X21.295 Y12.517 E.03813
G1 X20.762 Y12.517
G1 X20.417 Y12.862 E.01495
; WIPE_START
G1 F12000
M204 S10000
G1 X20.762 Y12.517 E-.18495
G1 X21.295 Y12.517 E-.20264
G1 X20.602 Y13.21 E-.37241
; WIPE_END
G1 E-.04 F1800
G1 X23.041 Y13.142 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.190887
G1 F8292
G1 X23.041 Y12.638 E.00607
G1 X23.003 Y12.546 E.0012
; WIPE_START
G1 F15000
G1 X23.041 Y12.638 E-.12515
G1 X23.041 Y13.142 E-.63485
; WIPE_END
G1 E-.04 F1800
G1 X24.026 Y12.566 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.37943
G1 F8292
G1 X24.026 Y12.139 E.01172
; LINE_WIDTH: 0.399437
G1 X24.006 Y11.986 E.00448
; LINE_WIDTH: 0.43945
G1 X23.986 Y11.833 E.00498
; LINE_WIDTH: 0.497282
G3 X23.966 Y11.452 I1.446 J-.267 E.01417
G1 X23.51 Y11.452 E.0169
G1 X23.521 Y11.911 E.01699
G1 X23.63 Y11.938 E.00413
; LINE_WIDTH: 0.479464
G1 X23.65 Y12.005 E.00249
; LINE_WIDTH: 0.43945
G1 X23.67 Y12.072 E.00226
; LINE_WIDTH: 0.381238
G1 X23.69 Y12.139 E.00193
G1 X23.69 Y12.566 E.01178
G1 X23.966 Y12.566 E.00762
; WIPE_START
G1 F15000
G1 X23.69 Y12.566 E-.2716
G1 X23.69 Y12.139 E-.41974
G1 X23.67 Y12.072 E-.06867
; WIPE_END
G1 E-.04 F1800
G1 X22.671 Y11.168 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; LINE_WIDTH: 0.50814
G1 F8292
G2 X22.669 Y11.269 I-.029 J.05 E.0091
G1 X22.882 Y10.901 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.19666
G1 F8292
G1 X22.406 Y10.901 E.00596
; WIPE_START
G1 F15000
G1 X22.882 Y10.901 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y7.18 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X22.602 Y5.262 E.06362
G1 X24.398 Y5.262 E.05957
G1 X24.398 Y7.18 E.06362
G1 X22.662 Y7.18 E.05758
G1 X22.21 Y7.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8292
M204 S5000
G1 X22.21 Y4.87 E.07814
G1 X24.79 Y4.87 E.07928
G1 X24.79 Y6.613 E.05356
G1 X24.79 Y7.013 E.01229
G1 X24.79 Y7.413 E.01229
G1 F3789.617
G1 X24.79 Y7.572 E.00489
G1 F2160
G1 X22.21 Y7.572 E.07928
G1 F3121.207
G1 X22.21 Y7.473 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y5.473 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.787 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F8292
G1 X24.006 Y5.654 E.03483
G1 X22.994 Y5.654 E.03109
G1 X22.994 Y6.787 E.03483
G1 X23.946 Y6.787 E.02924
G1 X23.659 Y6.44 F30000
; LINE_WIDTH: 0.36026
G1 F8292
G1 X23.659 Y6.001 E.01136
G1 X23.341 Y6.001 E.00821
G1 X23.341 Y6.44 E.01136
G1 X23.599 Y6.44 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y6.44 E-.13458
G1 X23.341 Y6.001 E-.22973
G1 X23.659 Y6.001 E-.16596
G1 X23.659 Y6.44 E-.22973
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y6.601 Z6 F30000
G1 X58.848 Y7.18 Z6
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X57.052 Y7.18 E.05957
G1 X57.052 Y6.586 E.0197
G1 X58.848 Y6.586 E.05957
G1 X58.848 Y7.12 E.01771
G1 X59.24 Y7.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y7.572 E.00489
G1 F2160
G1 X56.66 Y7.572 E.07928
G1 F3789.617
G1 X56.66 Y7.413 E.00489
G1 F8292
G1 X56.66 Y7.013 E.01229
G1 X56.66 Y6.613 E.01229
G1 X56.66 Y6.194 E.01288
G1 X59.24 Y6.194 E.07928
G1 X59.24 Y7.353 E.03561
M204 S10000
G1 X58.644 Y6.883 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.22972
G1 F8292
G1 X57.256 Y6.883 E.02114
; WIPE_START
G1 F15000
G1 X58.644 Y6.883 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y7.18 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X51.602 Y7.18 E.05957
G1 X51.602 Y5.262 E.06362
G1 X53.398 Y5.262 E.05957
G1 X53.398 Y7.12 E.06163
G1 X53.79 Y7.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y7.572 E.00489
G1 F2160
G1 X51.21 Y7.572 E.07928
G1 F3789.617
G1 X51.21 Y7.413 E.00489
G1 F8292
G1 X51.21 Y7.013 E.01229
G1 X51.21 Y6.613 E.01229
G1 X51.21 Y4.87 E.05356
G1 X53.79 Y4.87 E.07928
G1 X53.79 Y7.353 E.07629
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y7.572 E-.08322
G1 X52.009 Y7.572 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.787 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F8292
G1 X53.006 Y6.787 E.03109
G1 X53.006 Y5.654 E.03483
G1 X51.994 Y5.654 E.03109
G1 X51.994 Y6.727 E.03299
G1 X52.341 Y6.44 F30000
; LINE_WIDTH: 0.36025
G1 F8292
G1 X52.659 Y6.44 E.00821
G1 X52.659 Y6.001 E.01136
G1 X52.341 Y6.001 E.00821
G1 X52.341 Y6.38 E.00981
; WIPE_START
G1 F15000
G1 X52.341 Y6.001 E-.19835
G1 X52.659 Y6.001 E-.16596
G1 X52.659 Y6.44 E-.22973
G1 X52.341 Y6.44 E-.16596
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.938 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X51.602 Y12.938 E.05957
G1 X51.602 Y11.02 E.06362
G1 X53.398 Y11.02 E.05957
G1 X53.398 Y12.878 E.06163
G1 X53.79 Y13.33 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8292
M204 S5000
G1 X51.21 Y13.33 E.07928
G1 X51.21 Y11.587 E.05356
G1 X51.21 Y11.187 E.01229
G1 X51.21 Y10.787 E.01229
G1 F3789.734
G1 X51.21 Y10.628 E.00489
G1 F2160
G1 X53.79 Y10.628 E.07928
G1 F3789.734
G1 X53.79 Y10.787 E.00489
G1 F8292
G1 X53.79 Y11.187 E.01229
G1 X53.79 Y11.587 E.01229
G1 X53.79 Y13.27 E.05171
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.317 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.546 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F8292
G1 X53.006 Y12.546 E.03109
G1 X53.006 Y11.413 E.03483
G1 X51.994 Y11.413 E.03109
G1 X51.994 Y12.486 E.03299
G1 X52.341 Y12.199 F30000
; LINE_WIDTH: 0.36025
G1 F8292
G1 X52.659 Y12.199 E.00821
G1 X52.659 Y11.76 E.01136
G1 X52.341 Y11.76 E.00821
G1 X52.341 Y12.139 E.00981
; WIPE_START
G1 F15000
G1 X52.341 Y11.76 E-.19835
G1 X52.659 Y11.76 E-.16596
G1 X52.659 Y12.199 E-.22973
G1 X52.341 Y12.199 E-.16596
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.846 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X57.052 Y11.02 E.22641
G1 X58.848 Y11.02 E.05957
G1 X58.848 Y17.846 E.22641
G1 X57.112 Y17.846 E.05758
G1 X56.66 Y18.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8292
M204 S5000
G1 X56.66 Y11.587 E.20436
G1 X56.66 Y11.187 E.01229
G1 X56.66 Y10.787 E.01229
G1 F3789.267
G1 X56.66 Y10.628 E.00488
G1 F2160
G1 X59.24 Y10.628 E.07928
G1 F3789.267
G1 X59.24 Y10.787 E.00488
G1 F8292
G1 X59.24 Y11.187 E.01229
G1 X59.24 Y11.587 E.01229
G1 X59.24 Y18.238 E.20436
G1 X56.72 Y18.238 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.702 Y16.238 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.454 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F8292
G1 X58.456 Y17.454 E.03109
G1 X58.456 Y11.412 E.18563
G1 X57.444 Y11.412 E.03109
G1 X57.444 Y17.394 E.18379
G1 X57.791 Y17.107 F30000
; LINE_WIDTH: 0.36025
G1 F8292
G1 X58.109 Y17.107 E.00821
G1 X58.109 Y11.76 E.13826
G1 X57.791 Y11.76 E.00821
G1 X57.791 Y17.047 E.13671
; WIPE_START
G1 F15000
G1 X57.791 Y15.047 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.513 Y22.645 Z6 F30000
G1 X58.848 Y26.165 Z6
G1 Z5.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8292
G1 X57.052 Y26.165 E.05957
G1 X57.052 Y24.354 E.06007
G1 X58.848 Y24.354 E.05957
G1 X58.848 Y26.105 E.05808
G1 X59.24 Y26.557 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F8292
M204 S5000
G1 X56.66 Y26.557 E.07928
G1 X56.66 Y23.962 E.07974
G1 X59.24 Y23.962 E.07928
G1 X59.24 Y26.497 E.0779
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.544 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.746 Z6 F30000
G1 Z5.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F8292
G1 X57.444 Y25.773 E.03155
G1 X58.456 Y25.773 E.03109
G1 X58.456 Y24.746 E.03155
G1 X57.504 Y24.746 E.02924
G1 X57.791 Y25.093 F30000
; LINE_WIDTH: 0.36025
G1 F8292
G1 X57.791 Y25.426 E.0086
G1 X58.109 Y25.426 E.00821
G1 X58.109 Y25.093 E.0086
G1 X57.851 Y25.093 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 5.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.093 E-.15777
G1 X58.109 Y25.426 E-.20383
G1 X57.791 Y25.426 E-.19456
G1 X57.791 Y25.093 E-.20383
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 29/58
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
G1 X24.398 Y12.818
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X22.602 Y12.818 E.05957
G1 X22.602 Y10.82 E.06627
G1 X24.398 Y10.82 E.05957
G1 X24.398 Y12.758 E.06428
G1 X24.79 Y13.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4169
M204 S5000
G1 X22.21 Y13.21 E.07928
G1 X22.21 Y11.387 E.05602
G1 X22.21 Y10.987 E.01229
G1 X22.21 Y10.587 E.01229
G1 F3789.734
G1 X22.21 Y10.428 E.00489
G1 F2160
G1 X24.79 Y10.428 E.07928
G1 F3789.734
G1 X24.79 Y10.587 E.00489
G1 F4169
G1 X24.79 Y10.987 E.01229
G1 X24.79 Y11.387 E.01229
G1 X24.79 Y13.15 E.05417
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y13.197 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y12.426 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X24.006 Y11.213 E.0373
G1 X22.994 Y11.213 E.03109
G1 X22.994 Y12.426 E.0373
G1 X23.946 Y12.426 E.02924
G1 X23.659 Y12.079 F30000
; LINE_WIDTH: 0.36026
G1 F4169
G1 X23.659 Y11.56 E.01343
G1 X23.341 Y11.56 E.00821
G1 X23.341 Y12.079 E.01343
G1 X23.599 Y12.079 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y12.079 E-.12122
G1 X23.341 Y11.56 E-.24465
G1 X23.659 Y11.56 E-.14948
G1 X23.659 Y12.079 E-.24466
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y7.38 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X22.602 Y5.382 E.06627
G1 X24.398 Y5.382 E.05957
G1 X24.398 Y7.38 E.06627
G1 X22.662 Y7.38 E.05758
G1 X22.21 Y7.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4169
M204 S5000
G1 X22.21 Y4.99 E.0806
G1 X24.79 Y4.99 E.07928
G1 X24.79 Y6.813 E.05602
G1 X24.79 Y7.213 E.01229
G1 X24.79 Y7.613 E.01229
G1 F3789.617
G1 X24.79 Y7.772 E.00489
G1 F2160
G1 X22.21 Y7.772 E.07928
G1 F3121.207
G1 X22.21 Y7.673 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y5.673 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y6.987 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X24.006 Y5.774 E.0373
G1 X22.994 Y5.774 E.03109
G1 X22.994 Y6.987 E.0373
G1 X23.946 Y6.987 E.02924
G1 X23.659 Y6.64 F30000
; LINE_WIDTH: 0.36026
G1 F4169
G1 X23.659 Y6.121 E.01343
G1 X23.341 Y6.121 E.00821
G1 X23.341 Y6.64 E.01343
G1 X23.599 Y6.64 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y6.64 E-.12122
G1 X23.341 Y6.121 E-.24465
G1 X23.659 Y6.121 E-.14948
G1 X23.659 Y6.64 E-.24465
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y6.801 Z6.2 F30000
G1 X58.848 Y7.38 Z6.2
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X57.052 Y7.38 E.05957
G1 X57.052 Y6.761 E.02052
M73 P84 R2
G1 X58.848 Y6.761 E.05957
G1 X58.848 Y7.32 E.01853
G1 X59.24 Y7.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y7.772 E.00489
G1 F2160
G1 X56.66 Y7.772 E.07928
G1 F3789.617
G1 X56.66 Y7.613 E.00489
G1 F4169
G1 X56.66 Y7.213 E.01229
G1 X56.66 Y6.813 E.01229
G1 X56.66 Y6.369 E.01363
G1 X59.24 Y6.369 E.07928
G1 X59.24 Y7.553 E.03637
M204 S10000
G1 X58.644 Y7.07 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.25432
G1 F4169
G1 X57.256 Y7.07 E.02392
; WIPE_START
G1 F15000
G1 X58.644 Y7.07 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y7.38 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X51.602 Y7.38 E.05957
G1 X51.602 Y5.382 E.06627
G1 X53.398 Y5.382 E.05957
G1 X53.398 Y7.32 E.06428
G1 X53.79 Y7.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y7.772 E.00489
G1 F2160
G1 X51.21 Y7.772 E.07928
G1 F3789.617
G1 X51.21 Y7.613 E.00489
G1 F4169
G1 X51.21 Y7.213 E.01229
G1 X51.21 Y6.813 E.01229
G1 X51.21 Y4.99 E.05602
G1 X53.79 Y4.99 E.07928
G1 X53.79 Y7.553 E.07876
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y7.772 E-.08322
G1 X52.009 Y7.772 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y6.987 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X53.006 Y6.987 E.03109
G1 X53.006 Y5.774 E.0373
G1 X51.994 Y5.774 E.03109
G1 X51.994 Y6.927 E.03545
G1 X52.341 Y6.64 F30000
; LINE_WIDTH: 0.36025
G1 F4169
G1 X52.659 Y6.64 E.00821
G1 X52.659 Y6.121 E.01343
G1 X52.341 Y6.121 E.00821
G1 X52.341 Y6.58 E.01188
; WIPE_START
G1 F15000
G1 X52.341 Y6.121 E-.21639
G1 X52.659 Y6.121 E-.14948
G1 X52.659 Y6.64 E-.24465
G1 X52.341 Y6.64 E-.14948
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.818 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X51.602 Y12.818 E.05957
G1 X51.602 Y10.82 E.06627
G1 X53.398 Y10.82 E.05957
G1 X53.398 Y12.758 E.06428
G1 X53.79 Y13.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4169
M204 S5000
G1 X51.21 Y13.21 E.07928
G1 X51.21 Y11.387 E.05602
G1 X51.21 Y10.987 E.01229
G1 X51.21 Y10.587 E.01229
G1 F3789.734
G1 X51.21 Y10.428 E.00489
G1 F2160
G1 X53.79 Y10.428 E.07928
G1 F3789.734
G1 X53.79 Y10.587 E.00489
G1 F4169
G1 X53.79 Y10.987 E.01229
G1 X53.79 Y11.387 E.01229
G1 X53.79 Y13.15 E.05417
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.197 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.426 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X53.006 Y12.426 E.03109
G1 X53.006 Y11.213 E.0373
G1 X51.994 Y11.213 E.03109
G1 X51.994 Y12.366 E.03545
G1 X52.341 Y12.079 F30000
; LINE_WIDTH: 0.36025
G1 F4169
G1 X52.659 Y12.079 E.00821
G1 X52.659 Y11.56 E.01343
G1 X52.341 Y11.56 E.00821
G1 X52.341 Y12.019 E.01188
; WIPE_START
G1 F15000
G1 X52.341 Y11.56 E-.21639
G1 X52.659 Y11.56 E-.14948
G1 X52.659 Y12.079 E-.24465
G1 X52.341 Y12.079 E-.14948
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.816 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X57.052 Y10.82 E.23206
G1 X58.848 Y10.82 E.05957
G1 X58.848 Y17.816 E.23206
G1 X57.112 Y17.816 E.05758
G1 X56.66 Y18.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4169
M204 S5000
G1 X56.66 Y11.387 E.20959
G1 X56.66 Y10.987 E.01229
G1 X56.66 Y10.587 E.01229
G1 F3789.033
G1 X56.66 Y10.428 E.00488
G1 F2160
G1 X59.24 Y10.428 E.07928
G1 F3789.033
G1 X59.24 Y10.587 E.00488
G1 F4169
G1 X59.24 Y10.987 E.01229
G1 X59.24 Y11.387 E.01229
G1 X59.24 Y18.208 E.20959
G1 X56.72 Y18.208 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.702 Y16.208 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.424 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X58.456 Y17.424 E.03109
G1 X58.456 Y11.213 E.19086
G1 X57.444 Y11.213 E.03109
G1 X57.444 Y17.364 E.18902
G1 X57.791 Y17.077 F30000
; LINE_WIDTH: 0.36025
G1 F4169
G1 X58.109 Y17.077 E.00821
G1 X58.109 Y11.56 E.14267
G1 X57.791 Y11.56 E.00821
G1 X57.791 Y17.017 E.14111
; WIPE_START
G1 F15000
G1 X57.791 Y15.017 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.511 Y22.615 Z6.2 F30000
G1 X58.848 Y26.178 Z6.2
G1 Z5.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4169
G1 X57.052 Y26.178 E.05957
G1 X57.052 Y24.384 E.05953
G1 X58.848 Y24.384 E.05957
G1 X58.848 Y26.118 E.05753
G1 X59.24 Y26.57 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4169
M204 S5000
G1 X56.66 Y26.57 E.07928
G1 X56.66 Y23.992 E.07923
G1 X59.24 Y23.992 E.07928
G1 X59.24 Y26.51 E.07739
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.557 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.776 Z6.2 F30000
G1 Z5.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4169
G1 X57.444 Y25.786 E.03104
G1 X58.456 Y25.786 E.03109
G1 X58.456 Y24.776 E.03104
G1 X57.504 Y24.776 E.02924
G1 X57.791 Y25.123 F30000
; LINE_WIDTH: 0.35954
G1 F4169
G1 X57.791 Y25.439 E.00817
G1 X58.109 Y25.439 E.00821
G1 X58.109 Y25.123 E.00817
G1 X57.851 Y25.123 E.00666
; CHANGE_LAYER
; Z_HEIGHT: 6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.123 E-.16217
G1 X58.109 Y25.439 E-.19898
G1 X57.791 Y25.439 E-.19987
G1 X57.791 Y25.123 E-.19898
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 30/58
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
G1 X24.398 Y12.689
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X22.602 Y12.689 E.05957
G1 X22.602 Y10.62 E.06862
G1 X24.398 Y10.62 E.05957
G1 X24.398 Y12.629 E.06663
G1 X24.79 Y13.081 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4254
M204 S5000
G1 X22.21 Y13.081 E.07928
G1 X22.21 Y11.187 E.05819
G1 X22.21 Y10.787 E.01229
G1 X22.21 Y10.387 E.01229
G1 F3789.734
G1 X22.21 Y10.228 E.00489
G1 F2160
G1 X24.79 Y10.228 E.07928
G1 F3789.734
G1 X24.79 Y10.387 E.00489
G1 F4254
G1 X24.79 Y10.787 E.01229
G1 X24.79 Y11.187 E.01229
G1 X24.79 Y13.021 E.05634
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y13.068 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y12.297 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X24.006 Y11.013 E.03947
G1 X22.994 Y11.013 E.03109
G1 X22.994 Y12.297 E.03947
G1 X23.946 Y12.297 E.02924
G1 X23.659 Y11.95 F30000
; LINE_WIDTH: 0.36026
G1 F4254
G1 X23.659 Y11.36 E.01526
G1 X23.341 Y11.36 E.00821
G1 X23.341 Y11.95 E.01526
G1 X23.599 Y11.95 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y11.95 E-.11145
G1 X23.341 Y11.36 E-.25555
G1 X23.659 Y11.36 E-.13744
G1 X23.659 Y11.95 E-.25555
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y7.58 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X22.602 Y5.511 E.06862
G1 X24.398 Y5.511 E.05957
G1 X24.398 Y7.58 E.06862
G1 X22.662 Y7.58 E.05758
G1 X22.21 Y7.813 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4254
M204 S5000
G1 X22.21 Y5.119 E.08277
G1 X24.79 Y5.119 E.07928
G1 X24.79 Y7.013 E.05819
G1 X24.79 Y7.413 E.01229
G1 X24.79 Y7.813 E.01229
G1 F3789.617
G1 X24.79 Y7.972 E.00489
G1 F2160
G1 X22.21 Y7.972 E.07928
G1 F3121.207
G1 X22.21 Y7.873 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y5.873 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.187 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X24.006 Y5.903 E.03947
G1 X22.994 Y5.903 E.03109
G1 X22.994 Y7.187 E.03947
G1 X23.946 Y7.187 E.02924
G1 X23.659 Y6.84 F30000
; LINE_WIDTH: 0.36026
G1 F4254
G1 X23.659 Y6.25 E.01526
G1 X23.341 Y6.25 E.00821
G1 X23.341 Y6.84 E.01526
G1 X23.599 Y6.84 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y6.84 E-.11145
G1 X23.341 Y6.25 E-.25555
G1 X23.659 Y6.25 E-.13744
G1 X23.659 Y6.84 E-.25555
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y7.001 Z6.4 F30000
G1 X58.848 Y7.58 Z6.4
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X57.052 Y7.58 E.05957
G1 X57.052 Y6.955 E.02071
G1 X58.848 Y6.955 E.05957
G1 X58.848 Y7.52 E.01872
G1 X59.24 Y7.813 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y7.972 E.00489
G1 F2160
G1 X56.66 Y7.972 E.07928
G1 F3789.617
G1 X56.66 Y7.813 E.00489
G1 F4254
G1 X56.66 Y7.413 E.01229
G1 X56.66 Y7.013 E.01229
G1 X56.66 Y6.563 E.01381
G1 X59.24 Y6.563 E.07928
G1 X59.24 Y7.753 E.03655
M204 S10000
G1 X58.644 Y7.267 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.26008
G1 F4254
G1 X57.256 Y7.267 E.02458
; WIPE_START
G1 F15000
G1 X58.644 Y7.267 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y7.58 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X51.602 Y7.58 E.05957
G1 X51.602 Y5.511 E.06862
G1 X53.398 Y5.511 E.05957
G1 X53.398 Y7.52 E.06663
G1 X53.79 Y7.813 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y7.972 E.00489
G1 F2160
G1 X51.21 Y7.972 E.07928
G1 F3789.617
G1 X51.21 Y7.813 E.00489
G1 F4254
G1 X51.21 Y7.413 E.01229
G1 X51.21 Y7.013 E.01229
G1 X51.21 Y5.119 E.05819
G1 X53.79 Y5.119 E.07928
G1 X53.79 Y7.753 E.08093
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y7.972 E-.08322
G1 X52.009 Y7.972 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.187 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X53.006 Y7.187 E.03109
G1 X53.006 Y5.903 E.03947
G1 X51.994 Y5.903 E.03109
G1 X51.994 Y7.127 E.03762
G1 X52.341 Y6.84 F30000
; LINE_WIDTH: 0.36025
G1 F4254
G1 X52.659 Y6.84 E.00821
G1 X52.659 Y6.25 E.01526
G1 X52.341 Y6.25 E.00821
G1 X52.341 Y6.78 E.01371
; WIPE_START
G1 F15000
G1 X52.341 Y6.25 E-.22956
G1 X52.659 Y6.25 E-.13744
G1 X52.659 Y6.84 E-.25555
G1 X52.341 Y6.84 E-.13744
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.689 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X51.602 Y12.689 E.05957
G1 X51.602 Y10.62 E.06862
G1 X53.398 Y10.62 E.05957
G1 X53.398 Y12.629 E.06663
G1 X53.79 Y13.081 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4254
M204 S5000
G1 X51.21 Y13.081 E.07928
G1 X51.21 Y11.187 E.05819
G1 X51.21 Y10.787 E.01229
G1 X51.21 Y10.387 E.01229
G1 F3789.734
G1 X51.21 Y10.228 E.00489
G1 F2160
G1 X53.79 Y10.228 E.07928
G1 F3789.734
G1 X53.79 Y10.387 E.00489
G1 F4254
G1 X53.79 Y10.787 E.01229
G1 X53.79 Y11.187 E.01229
G1 X53.79 Y13.021 E.05634
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y13.068 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.297 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X53.006 Y12.297 E.03109
G1 X53.006 Y11.013 E.03947
G1 X51.994 Y11.013 E.03109
G1 X51.994 Y12.237 E.03762
G1 X52.341 Y11.95 F30000
; LINE_WIDTH: 0.36025
G1 F4254
G1 X52.659 Y11.95 E.00821
G1 X52.659 Y11.36 E.01526
G1 X52.341 Y11.36 E.00821
G1 X52.341 Y11.89 E.01371
; WIPE_START
G1 F15000
G1 X52.341 Y11.36 E-.22956
G1 X52.659 Y11.36 E-.13744
G1 X52.659 Y11.95 E-.25555
G1 X52.341 Y11.95 E-.13744
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.803 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X57.052 Y10.62 E.23825
G1 X58.848 Y10.62 E.05957
G1 X58.848 Y17.803 E.23825
G1 X57.112 Y17.803 E.05758
G1 X56.66 Y18.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4254
M204 S5000
G1 X56.66 Y11.187 E.21532
G1 X56.66 Y10.787 E.01229
G1 X56.66 Y10.387 E.01229
G1 F3789.734
G1 X56.66 Y10.228 E.00489
G1 F2160
G1 X59.24 Y10.228 E.07928
G1 F3789.734
G1 X59.24 Y10.387 E.00489
G1 F4254
G1 X59.24 Y10.787 E.01229
G1 X59.24 Y11.187 E.01229
G1 X59.24 Y18.195 E.21532
G1 X56.72 Y18.195 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.703 Y16.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.411 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X58.456 Y17.411 E.03109
G1 X58.456 Y11.013 E.19659
G1 X57.444 Y11.013 E.03109
G1 X57.444 Y17.351 E.19475
G1 X57.791 Y17.064 F30000
; LINE_WIDTH: 0.36025
G1 F4254
G1 X58.109 Y17.064 E.00821
G1 X58.109 Y11.36 E.14749
G1 X57.791 Y11.36 E.00821
G1 X57.791 Y17.004 E.14594
; WIPE_START
G1 F15000
G1 X57.791 Y15.004 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.509 Y22.602 Z6.4 F30000
G1 X58.848 Y26.191 Z6.4
G1 Z6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4254
G1 X57.052 Y26.191 E.05957
G1 X57.052 Y24.397 E.05952
G1 X58.848 Y24.397 E.05957
G1 X58.848 Y26.131 E.05753
G1 X59.24 Y26.583 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4254
M204 S5000
G1 X56.66 Y26.583 E.07928
G1 X56.66 Y24.005 E.07923
G1 X59.24 Y24.005 E.07928
G1 X59.24 Y26.523 E.07738
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.57 E-.76
; WIPE_END
M73 P85 R2
G1 E-.04 F1800
G1 X57.444 Y24.789 Z6.4 F30000
G1 Z6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4254
G1 X57.444 Y25.799 E.03104
G1 X58.456 Y25.799 E.03109
G1 X58.456 Y24.789 E.03104
G1 X57.504 Y24.789 E.02924
G1 X57.791 Y25.136 F30000
; LINE_WIDTH: 0.35944
G1 F4254
G1 X57.791 Y25.453 E.00816
G1 X58.109 Y25.453 E.00821
G1 X58.109 Y25.136 E.00816
G1 X57.851 Y25.136 E.00666
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.136 E-.16224
G1 X58.109 Y25.453 E-.19891
G1 X57.791 Y25.453 E-.19994
G1 X57.791 Y25.136 E-.19891
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 31/58
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
G1 X24.398 Y12.541
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X22.602 Y12.541 E.05957
G1 X22.602 Y10.42 E.07033
G1 X24.398 Y10.42 E.05957
G1 X24.398 Y12.481 E.06834
G1 X24.79 Y12.933 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4324
M204 S5000
G1 X22.21 Y12.933 E.07928
G1 X22.21 Y10.987 E.05978
G1 X22.21 Y10.587 E.01229
G1 X22.21 Y10.187 E.01229
G1 F3789.734
G1 X22.21 Y10.028 E.00489
G1 F2160
G1 X24.79 Y10.028 E.07928
G1 F3789.734
G1 X24.79 Y10.187 E.00489
G1 F4324
G1 X24.79 Y10.587 E.01229
G1 X24.79 Y10.987 E.01229
G1 X24.79 Y12.873 E.05793
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y12.919 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y12.149 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X24.006 Y10.813 E.04105
G1 X22.994 Y10.813 E.03109
G1 X22.994 Y12.149 E.04105
G1 X23.946 Y12.149 E.02924
G1 X23.659 Y11.801 F30000
; LINE_WIDTH: 0.36025
G1 F4324
G1 X23.659 Y11.16 E.01659
G1 X23.341 Y11.16 E.00821
G1 X23.341 Y11.801 E.01659
G1 X23.599 Y11.801 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y11.801 E-.10525
G1 X23.341 Y11.16 E-.26248
G1 X23.659 Y11.16 E-.12979
G1 X23.659 Y11.801 E-.26248
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y7.78 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X22.602 Y5.659 E.07033
G1 X24.398 Y5.659 E.05957
G1 X24.398 Y7.78 E.07033
G1 X22.662 Y7.78 E.05758
G1 X22.21 Y8.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4324
M204 S5000
G1 X22.21 Y5.267 E.08436
G1 X24.79 Y5.267 E.07928
G1 X24.79 Y7.213 E.05978
G1 X24.79 Y7.613 E.01229
G1 X24.79 Y8.013 E.01229
G1 F3789.617
G1 X24.79 Y8.172 E.00489
G1 F2160
G1 X22.21 Y8.172 E.07928
G1 F3121.207
G1 X22.21 Y8.073 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y6.073 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.387 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X24.006 Y6.051 E.04106
G1 X22.994 Y6.051 E.03109
G1 X22.994 Y7.387 E.04106
G1 X23.946 Y7.387 E.02924
G1 X23.659 Y7.04 F30000
; LINE_WIDTH: 0.36026
G1 F4324
G1 X23.659 Y6.399 E.01659
G1 X23.341 Y6.399 E.00821
G1 X23.341 Y7.04 E.01659
G1 X23.599 Y7.04 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y7.04 E-.10525
G1 X23.341 Y6.399 E-.26248
G1 X23.659 Y6.399 E-.12979
G1 X23.659 Y7.04 E-.26248
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y7.201 Z6.6 F30000
G1 X58.848 Y7.78 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X57.052 Y7.78 E.05957
G1 X57.052 Y7.183 E.01978
G1 X58.848 Y7.183 E.05957
G1 X58.848 Y7.72 E.01779
G1 X59.24 Y8.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y8.172 E.00489
G1 F2160
G1 X56.66 Y8.172 E.07928
G1 F3789.617
G1 X56.66 Y8.013 E.00489
G1 F4324
G1 X56.66 Y7.613 E.01229
G1 X56.66 Y7.213 E.01229
G1 X56.66 Y6.791 E.01295
G1 X59.24 Y6.791 E.07928
G1 X59.24 Y7.953 E.03568
M204 S10000
G1 X58.644 Y7.481 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.23202
G1 F4324
G1 X57.256 Y7.481 E.0214
; WIPE_START
G1 F15000
G1 X58.644 Y7.481 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y7.78 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X51.602 Y7.78 E.05957
G1 X51.602 Y5.659 E.07033
G1 X53.398 Y5.659 E.05957
G1 X53.398 Y7.72 E.06834
G1 X53.79 Y8.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y8.172 E.00489
G1 F2160
G1 X51.21 Y8.172 E.07928
G1 F3789.617
G1 X51.21 Y8.013 E.00489
G1 F4324
G1 X51.21 Y7.613 E.01229
G1 X51.21 Y7.213 E.01229
G1 X51.21 Y5.267 E.05978
G1 X53.79 Y5.267 E.07928
G1 X53.79 Y7.953 E.08252
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y8.172 E-.08322
G1 X52.009 Y8.172 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.387 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X53.006 Y7.387 E.03109
G1 X53.006 Y6.051 E.04105
G1 X51.994 Y6.051 E.03109
G1 X51.994 Y7.327 E.03921
G1 X52.341 Y7.04 F30000
; LINE_WIDTH: 0.36025
G1 F4324
G1 X52.659 Y7.04 E.00821
G1 X52.659 Y6.399 E.01659
G1 X52.341 Y6.399 E.00821
G1 X52.341 Y6.98 E.01504
; WIPE_START
G1 F15000
G1 X52.341 Y6.399 E-.23794
G1 X52.659 Y6.399 E-.12979
G1 X52.659 Y7.04 E-.26248
G1 X52.341 Y7.04 E-.12979
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.541 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X51.602 Y12.541 E.05957
G1 X51.602 Y10.42 E.07033
G1 X53.398 Y10.42 E.05957
G1 X53.398 Y12.481 E.06834
G1 X53.79 Y12.933 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4324
M204 S5000
G1 X51.21 Y12.933 E.07928
G1 X51.21 Y10.987 E.05978
G1 X51.21 Y10.587 E.01229
G1 X51.21 Y10.187 E.01229
G1 F3789.734
G1 X51.21 Y10.028 E.00489
G1 F2160
G1 X53.79 Y10.028 E.07928
G1 F3789.734
G1 X53.79 Y10.187 E.00489
G1 F4324
G1 X53.79 Y10.587 E.01229
G1 X53.79 Y10.987 E.01229
G1 X53.79 Y12.873 E.05793
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y12.919 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y12.149 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X53.006 Y12.149 E.03109
G1 X53.006 Y10.813 E.04106
G1 X51.994 Y10.813 E.03109
G1 X51.994 Y12.089 E.03921
G1 X52.341 Y11.801 F30000
; LINE_WIDTH: 0.36026
G1 F4324
G1 X52.659 Y11.801 E.00821
G1 X52.659 Y11.16 E.01659
G1 X52.341 Y11.16 E.00821
G1 X52.341 Y11.741 E.01504
; WIPE_START
G1 F15000
G1 X52.341 Y11.16 E-.23794
G1 X52.659 Y11.16 E-.12979
G1 X52.659 Y11.801 E-.26248
G1 X52.341 Y11.801 E-.12979
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.803 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X57.052 Y10.42 E.24489
G1 X58.848 Y10.42 E.05957
G1 X58.848 Y17.803 E.24489
G1 X57.112 Y17.803 E.05758
G1 X56.66 Y18.195 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4324
M204 S5000
G1 X56.66 Y10.987 E.22147
G1 X56.66 Y10.587 E.01229
G1 X56.66 Y10.187 E.01229
G1 F3789.734
G1 X56.66 Y10.028 E.00489
G1 F2160
G1 X59.24 Y10.028 E.07928
G1 F3789.734
G1 X59.24 Y10.187 E.00489
G1 F4324
G1 X59.24 Y10.587 E.01229
G1 X59.24 Y10.987 E.01229
G1 X59.24 Y18.195 E.22147
G1 X56.72 Y18.195 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.703 Y16.195 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.411 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X58.456 Y17.411 E.03109
G1 X58.456 Y10.813 E.20274
G1 X57.444 Y10.813 E.03109
G1 X57.444 Y17.351 E.2009
G1 X57.791 Y17.064 F30000
; LINE_WIDTH: 0.36025
G1 F4324
G1 X58.109 Y17.064 E.00821
G1 X58.109 Y11.16 E.15266
G1 X57.791 Y11.16 E.00821
G1 X57.791 Y17.004 E.15111
; WIPE_START
G1 F15000
G1 X57.791 Y15.004 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.509 Y22.602 Z6.6 F30000
G1 X58.848 Y26.191 Z6.6
G1 Z6.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4324
G1 X57.052 Y26.191 E.05957
G1 X57.052 Y24.397 E.05952
G1 X58.848 Y24.397 E.05957
G1 X58.848 Y26.131 E.05753
G1 X59.24 Y26.583 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4324
M204 S5000
G1 X56.66 Y26.583 E.07928
G1 X56.66 Y24.005 E.07923
G1 X59.24 Y24.005 E.07928
G1 X59.24 Y26.523 E.07738
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.57 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.789 Z6.6 F30000
G1 Z6.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4324
G1 X57.444 Y25.799 E.03104
G1 X58.456 Y25.799 E.03109
G1 X58.456 Y24.789 E.03104
G1 X57.504 Y24.789 E.02924
G1 X57.791 Y25.136 F30000
; LINE_WIDTH: 0.35943
G1 F4324
G1 X57.791 Y25.453 E.00816
G1 X58.109 Y25.453 E.00821
G1 X58.109 Y25.136 E.00816
G1 X57.851 Y25.136 E.00666
; CHANGE_LAYER
; Z_HEIGHT: 6.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.136 E-.16224
G1 X58.109 Y25.453 E-.19891
G1 X57.791 Y25.453 E-.19994
G1 X57.791 Y25.136 E-.19891
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 32/58
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
G1 X24.398 Y12.382
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X22.602 Y12.382 E.05957
G1 X22.602 Y10.22 E.07169
G1 X24.398 Y10.22 E.05957
G1 X24.398 Y12.322 E.0697
G1 X24.79 Y12.774 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4385
M204 S5000
G1 X22.21 Y12.774 E.07928
G1 X22.21 Y10.787 E.06104
G1 X22.21 Y10.387 E.01229
G1 X22.21 Y9.987 E.01229
G1 F3789.734
G1 X22.21 Y9.828 E.00489
G1 F2160
G1 X24.79 Y9.828 E.07928
G1 F3789.734
G1 X24.79 Y9.987 E.00489
G1 F4385
G1 X24.79 Y10.387 E.01229
G1 X24.79 Y10.787 E.01229
G1 X24.79 Y12.714 E.05919
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y12.76 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y11.99 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X24.006 Y10.613 E.04232
G1 X22.994 Y10.613 E.03109
G1 X22.994 Y11.99 E.04232
G1 X23.946 Y11.99 E.02924
G1 X23.659 Y11.642 F30000
; LINE_WIDTH: 0.36026
G1 F4385
G1 X23.659 Y10.96 E.01766
G1 X23.341 Y10.96 E.00821
G1 X23.341 Y11.642 E.01766
G1 X23.599 Y11.642 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y11.642 E-.1008
G1 X23.341 Y10.96 E-.26745
G1 X23.659 Y10.96 E-.1243
G1 X23.659 Y11.642 E-.26745
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y7.98 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X22.602 Y5.818 E.07169
G1 X24.398 Y5.818 E.05957
G1 X24.398 Y7.98 E.07169
G1 X22.662 Y7.98 E.05758
G1 X22.21 Y8.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4385
M204 S5000
G1 X22.21 Y5.426 E.08562
G1 X24.79 Y5.426 E.07928
G1 X24.79 Y7.413 E.06104
G1 X24.79 Y7.813 E.01229
G1 X24.79 Y8.213 E.01229
G1 F3789.617
G1 X24.79 Y8.372 E.00489
G1 F2160
G1 X22.21 Y8.372 E.07928
G1 F3121.207
G1 X22.21 Y8.273 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y6.273 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.587 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X24.006 Y6.21 E.04232
G1 X22.994 Y6.21 E.03109
G1 X22.994 Y7.587 E.04232
G1 X23.946 Y7.587 E.02924
G1 X23.659 Y7.24 F30000
; LINE_WIDTH: 0.36026
G1 F4385
G1 X23.659 Y6.557 E.01766
G1 X23.341 Y6.557 E.00821
G1 X23.341 Y7.24 E.01766
G1 X23.599 Y7.24 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y7.24 E-.1008
G1 X23.341 Y6.557 E-.26745
G1 X23.659 Y6.557 E-.1243
G1 X23.659 Y7.24 E-.26745
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y7.401 Z6.8 F30000
G1 X58.848 Y7.98 Z6.8
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X57.052 Y7.98 E.05957
G1 X57.052 Y7.456 E.01735
G1 X58.848 Y7.456 E.05957
G1 X58.848 Y7.92 E.01536
G1 X59.24 Y8.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y8.372 E.00489
G1 F2160
G1 X56.66 Y8.372 E.07928
G1 F3789.617
G1 X56.66 Y8.213 E.00489
G1 F4385
G1 X56.66 Y7.813 E.01229
G1 X56.66 Y7.413 E.01229
G1 X56.66 Y7.064 E.0107
G1 X59.24 Y7.064 E.07928
G1 X59.24 Y8.153 E.03344
M204 S10000
G1 X58.644 Y7.718 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.15888
G1 F4385
G1 X57.256 Y7.718 E.01312
; WIPE_START
G1 F15000
G1 X58.644 Y7.718 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y7.98 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X51.602 Y7.98 E.05957
G1 X51.602 Y5.818 E.07169
G1 X53.398 Y5.818 E.05957
G1 X53.398 Y7.92 E.0697
G1 X53.79 Y8.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P86 R2
G1 F3789.617
M204 S5000
G1 X53.79 Y8.372 E.00489
G1 F2160
G1 X51.21 Y8.372 E.07928
G1 F3789.617
G1 X51.21 Y8.213 E.00489
G1 F4385
G1 X51.21 Y7.813 E.01229
G1 X51.21 Y7.413 E.01229
G1 X51.21 Y5.426 E.06104
G1 X53.79 Y5.426 E.07928
G1 X53.79 Y8.153 E.08378
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y8.372 E-.08322
G1 X52.009 Y8.372 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.587 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X53.006 Y7.587 E.03109
G1 X53.006 Y6.21 E.04232
G1 X51.994 Y6.21 E.03109
G1 X51.994 Y7.527 E.04047
G1 X52.341 Y7.24 F30000
; LINE_WIDTH: 0.36025
G1 F4385
G1 X52.659 Y7.24 E.00821
G1 X52.659 Y6.557 E.01766
G1 X52.341 Y6.557 E.00821
G1 X52.341 Y7.18 E.0161
; WIPE_START
G1 F15000
G1 X52.341 Y6.557 E-.24394
G1 X52.659 Y6.557 E-.12431
G1 X52.659 Y7.24 E-.26745
G1 X52.341 Y7.24 E-.12431
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.382 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X51.602 Y12.382 E.05957
G1 X51.602 Y10.22 E.07169
G1 X53.398 Y10.22 E.05957
G1 X53.398 Y12.322 E.0697
G1 X53.79 Y12.774 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4385
M204 S5000
G1 X51.21 Y12.774 E.07928
G1 X51.21 Y10.787 E.06104
G1 X51.21 Y10.387 E.01229
G1 X51.21 Y9.987 E.01229
G1 F3789.734
G1 X51.21 Y9.828 E.00489
G1 F2160
G1 X53.79 Y9.828 E.07928
G1 F3789.734
G1 X53.79 Y9.987 E.00489
G1 F4385
G1 X53.79 Y10.387 E.01229
G1 X53.79 Y10.787 E.01229
G1 X53.79 Y12.714 E.05919
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y12.76 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y11.99 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X53.006 Y11.99 E.03109
G1 X53.006 Y10.613 E.04232
G1 X51.994 Y10.613 E.03109
G1 X51.994 Y11.93 E.04047
G1 X52.341 Y11.642 F30000
; LINE_WIDTH: 0.36025
G1 F4385
G1 X52.659 Y11.642 E.00821
G1 X52.659 Y10.96 E.01766
G1 X52.341 Y10.96 E.00821
G1 X52.341 Y11.582 E.0161
; WIPE_START
G1 F15000
G1 X52.341 Y10.96 E-.24394
G1 X52.659 Y10.96 E-.1243
G1 X52.659 Y11.642 E-.26745
G1 X52.341 Y11.642 E-.1243
; WIPE_END
G1 E-.04 F1800
G1 X56.971 Y17.71 Z6.8 F30000
G1 X57.052 Y17.816 Z6.8
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X57.052 Y10.22 E.25197
G1 X58.848 Y10.22 E.05957
G1 X58.848 Y17.816 E.25197
G1 X57.112 Y17.816 E.05758
G1 X56.66 Y18.208 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4385
M204 S5000
G1 X56.66 Y10.787 E.22802
G1 X56.66 Y10.387 E.01229
G1 X56.66 Y9.987 E.01229
G1 F3790.551
G1 X56.66 Y9.828 E.00489
G1 F2160
G1 X59.24 Y9.828 E.07928
G1 F3790.551
G1 X59.24 Y9.987 E.00489
G1 F4385
G1 X59.24 Y10.387 E.01229
G1 X59.24 Y10.787 E.01229
G1 X59.24 Y18.208 E.22802
G1 X56.72 Y18.208 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.704 Y16.208 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.424 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X58.456 Y17.424 E.03109
G1 X58.456 Y10.612 E.2093
G1 X57.444 Y10.612 E.03109
G1 X57.444 Y17.364 E.20745
G1 X57.791 Y17.077 F30000
; LINE_WIDTH: 0.36025
G1 F4385
G1 X58.109 Y17.077 E.00821
G1 X58.109 Y10.96 E.15818
G1 X57.791 Y10.96 E.00821
G1 X57.791 Y17.017 E.15663
; WIPE_START
G1 F15000
G1 X57.791 Y15.017 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.511 Y22.615 Z6.8 F30000
G1 X58.848 Y26.178 Z6.8
G1 Z6.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4385
G1 X57.052 Y26.178 E.05957
G1 X57.052 Y24.384 E.05953
G1 X58.848 Y24.384 E.05957
G1 X58.848 Y26.118 E.05754
G1 X59.24 Y26.57 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4385
M204 S5000
G1 X56.66 Y26.57 E.07928
G1 X56.66 Y23.992 E.07923
G1 X59.24 Y23.992 E.07928
G1 X59.24 Y26.51 E.07739
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.557 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.776 Z6.8 F30000
G1 Z6.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4385
G1 X57.444 Y25.786 E.03104
G1 X58.456 Y25.786 E.03109
G1 X58.456 Y24.776 E.03104
G1 X57.504 Y24.776 E.02924
G1 X57.791 Y25.123 F30000
; LINE_WIDTH: 0.35956
G1 F4385
G1 X57.791 Y25.439 E.00817
G1 X58.109 Y25.439 E.00821
G1 X58.109 Y25.123 E.00817
G1 X57.851 Y25.123 E.00666
; CHANGE_LAYER
; Z_HEIGHT: 6.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.123 E-.16216
G1 X58.109 Y25.439 E-.19899
G1 X57.791 Y25.439 E-.19986
G1 X57.791 Y25.123 E-.19899
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 33/58
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
G1 X24.398 Y12.2
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X22.602 Y12.2 E.05957
G1 X22.602 Y10.02 E.07231
G1 X24.398 Y10.02 E.05957
G1 X24.398 Y12.14 E.07032
G1 X24.79 Y12.592 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4400
M204 S5000
G1 X22.21 Y12.592 E.07928
G1 X22.21 Y10.587 E.06161
G1 X22.21 Y10.187 E.01229
G1 X22.21 Y9.787 E.01229
G1 F3789.734
G1 X22.21 Y9.628 E.00489
G1 F2160
G1 X24.79 Y9.628 E.07928
G1 F3789.734
G1 X24.79 Y9.787 E.00489
G1 F4400
G1 X24.79 Y10.187 E.01229
G1 X24.79 Y10.587 E.01229
G1 X24.79 Y12.532 E.05977
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y12.579 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y11.808 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X24.006 Y10.413 E.04289
G1 X22.994 Y10.413 E.03109
G1 X22.994 Y11.808 E.04289
G1 X23.946 Y11.808 E.02924
G1 X23.659 Y11.461 F30000
; LINE_WIDTH: 0.36025
G1 F4400
G1 X23.659 Y10.76 E.01814
G1 X23.341 Y10.76 E.00821
G1 X23.341 Y11.461 E.01814
G1 X23.599 Y11.461 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y11.461 E-.0989
G1 X23.341 Y10.76 E-.26957
G1 X23.659 Y10.76 E-.12196
G1 X23.659 Y11.461 E-.26957
; WIPE_END
G1 E-.04 F1800
G1 X22.602 Y8.18 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X22.602 Y6 E.07231
G1 X24.398 Y6 E.05957
G1 X24.398 Y8.18 E.07231
G1 X22.662 Y8.18 E.05758
G1 X22.21 Y8.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4400
M204 S5000
G1 X22.21 Y5.607 E.08619
G1 X24.79 Y5.607 E.07928
G1 X24.79 Y7.613 E.06161
G1 X24.79 Y8.013 E.01229
G1 X24.79 Y8.413 E.01229
G1 F3789.617
G1 X24.79 Y8.572 E.00489
G1 F2160
G1 X22.21 Y8.572 E.07928
G1 F3121.207
G1 X22.21 Y8.473 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y6.473 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.787 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X24.006 Y6.392 E.04289
G1 X22.994 Y6.392 E.03109
G1 X22.994 Y7.787 E.04289
G1 X23.946 Y7.787 E.02924
G1 X23.659 Y7.44 F30000
; LINE_WIDTH: 0.36025
G1 F4400
G1 X23.659 Y6.739 E.01814
G1 X23.341 Y6.739 E.00821
G1 X23.341 Y7.44 E.01814
G1 X23.599 Y7.44 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y7.44 E-.0989
G1 X23.341 Y6.739 E-.26957
G1 X23.659 Y6.739 E-.12196
G1 X23.659 Y7.44 E-.26957
; WIPE_END
G1 E-.04 F1800
G1 X31.289 Y7.601 Z7 F30000
G1 X58.848 Y8.18 Z7
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X57.052 Y8.18 E.05957
G1 X57.052 Y7.775 E.01342
G1 X58.848 Y7.775 E.05957
G1 X58.848 Y8.12 E.01143
G1 X59.24 Y8.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y8.572 E.00489
G1 F2160
G1 X56.66 Y8.572 E.07928
G1 F3789.617
G1 X56.66 Y8.413 E.00489
G1 F4400
G1 X56.66 Y8.013 E.01229
G1 X56.66 Y7.613 E.01229
G1 X56.66 Y7.383 E.00706
G1 X59.24 Y7.383 E.07928
G1 X59.24 Y8.353 E.0298
; WIPE_START
G1 F12000
M204 S10000
G1 X59.24 Y8.572 E-.08322
G1 X57.459 Y8.572 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y8.18 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X51.602 Y8.18 E.05957
G1 X51.602 Y6 E.07231
G1 X53.398 Y6 E.05957
G1 X53.398 Y8.12 E.07032
G1 X53.79 Y8.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y8.572 E.00489
G1 F2160
G1 X51.21 Y8.572 E.07928
G1 F3789.617
G1 X51.21 Y8.413 E.00489
G1 F4400
G1 X51.21 Y8.013 E.01229
G1 X51.21 Y7.613 E.01229
G1 X51.21 Y5.607 E.06161
G1 X53.79 Y5.607 E.07928
G1 X53.79 Y8.353 E.08435
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y8.572 E-.08322
G1 X52.009 Y8.572 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.787 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X53.006 Y7.787 E.03109
G1 X53.006 Y6.392 E.04289
G1 X51.994 Y6.392 E.03109
G1 X51.994 Y7.727 E.04105
G1 X52.341 Y7.44 F30000
; LINE_WIDTH: 0.36026
G1 F4400
G1 X52.659 Y7.44 E.00821
G1 X52.659 Y6.739 E.01814
G1 X52.341 Y6.739 E.00821
G1 X52.341 Y7.38 E.01659
; WIPE_START
G1 F15000
G1 X52.341 Y6.739 E-.24651
G1 X52.659 Y6.739 E-.12196
G1 X52.659 Y7.44 E-.26957
G1 X52.341 Y7.44 E-.12196
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.2 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X51.602 Y12.2 E.05957
G1 X51.602 Y10.02 E.07231
G1 X53.398 Y10.02 E.05957
G1 X53.398 Y12.14 E.07032
G1 X53.79 Y12.592 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4400
M204 S5000
G1 X51.21 Y12.592 E.07928
G1 X51.21 Y10.587 E.06161
G1 X51.21 Y10.187 E.01229
G1 X51.21 Y9.787 E.01229
G1 F3789.734
G1 X51.21 Y9.628 E.00489
G1 F2160
G1 X53.79 Y9.628 E.07928
G1 F3789.734
G1 X53.79 Y9.787 E.00489
G1 F4400
G1 X53.79 Y10.187 E.01229
G1 X53.79 Y10.587 E.01229
G1 X53.79 Y12.532 E.05977
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y12.579 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y11.808 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X53.006 Y11.808 E.03109
G1 X53.006 Y10.413 E.04289
G1 X51.994 Y10.413 E.03109
G1 X51.994 Y11.748 E.04105
G1 X52.341 Y11.461 F30000
; LINE_WIDTH: 0.36026
G1 F4400
G1 X52.659 Y11.461 E.00821
G1 X52.659 Y10.76 E.01814
G1 X52.341 Y10.76 E.00821
G1 X52.341 Y11.401 E.01659
; WIPE_START
G1 F15000
G1 X52.341 Y10.76 E-.24651
G1 X52.659 Y10.76 E-.12196
G1 X52.659 Y11.461 E-.26957
G1 X52.341 Y11.461 E-.12196
; WIPE_END
G1 E-.04 F1800
G1 X56.873 Y17.603 Z7 F30000
G1 X57.052 Y17.846 Z7
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X57.052 Y10.02 E.25958
G1 X58.848 Y10.02 E.05957
G1 X58.848 Y17.846 E.25958
G1 X57.112 Y17.846 E.05758
G1 X56.66 Y18.238 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4400
M204 S5000
G1 X56.66 Y10.587 E.23508
G1 X56.66 Y10.187 E.01229
G1 X56.66 Y9.787 E.01229
G1 F3789.383
G1 X56.66 Y9.628 E.00489
G1 F2160
G1 X59.24 Y9.628 E.07928
G1 F3789.383
G1 X59.24 Y9.787 E.00489
G1 F4400
G1 X59.24 Y10.187 E.01229
G1 X59.24 Y10.587 E.01229
G1 X59.24 Y18.238 E.23508
G1 X56.72 Y18.238 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.704 Y16.238 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.454 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X58.456 Y17.454 E.03109
G1 X58.456 Y10.412 E.21635
G1 X57.444 Y10.412 E.03109
G1 X57.444 Y17.394 E.21451
G1 X57.791 Y17.107 F30000
; LINE_WIDTH: 0.36025
G1 F4400
G1 X58.109 Y17.107 E.00821
G1 X58.109 Y10.76 E.16412
G1 X57.791 Y10.76 E.00821
G1 X57.791 Y17.047 E.16257
; WIPE_START
G1 F15000
G1 X57.791 Y15.047 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.513 Y22.645 Z7 F30000
G1 X58.848 Y26.165 Z7
G1 Z6.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4400
G1 X57.052 Y26.165 E.05957
G1 X57.052 Y24.354 E.06007
G1 X58.848 Y24.354 E.05957
G1 X58.848 Y26.105 E.05808
G1 X59.24 Y26.557 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4400
M204 S5000
G1 X56.66 Y26.557 E.07928
G1 X56.66 Y23.962 E.07974
G1 X59.24 Y23.962 E.07928
G1 X59.24 Y26.497 E.0779
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.544 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.746 Z7 F30000
G1 Z6.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4400
G1 X57.444 Y25.773 E.03155
G1 X58.456 Y25.773 E.03109
G1 X58.456 Y24.746 E.03155
G1 X57.504 Y24.746 E.02924
G1 X57.791 Y25.093 F30000
; LINE_WIDTH: 0.36025
G1 F4400
G1 X57.791 Y25.426 E.0086
G1 X58.109 Y25.426 E.00821
G1 X58.109 Y25.093 E.0086
G1 X57.851 Y25.093 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 6.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y25.093 E-.15777
G1 X58.109 Y25.426 E-.20383
G1 X57.791 Y25.426 E-.19456
G1 X57.791 Y25.093 E-.20383
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 34/58
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
G1 X22.602 Y8.38
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X22.602 Y6.199 E.07232
G1 X24.398 Y6.199 E.05957
G1 X24.398 Y8.38 E.07232
G1 X22.662 Y8.38 E.05758
G1 X22.21 Y8.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4398
M204 S5000
G1 X22.21 Y5.807 E.0862
G1 X24.79 Y5.807 E.07928
G1 X24.79 Y7.813 E.06162
G1 X24.79 Y8.213 E.01229
G1 X24.79 Y8.613 E.01229
G1 F3789.617
G1 X24.79 Y8.772 E.00489
G1 F2160
G1 X22.21 Y8.772 E.07928
M73 P87 R2
G1 F3121.207
G1 X22.21 Y8.673 E.00304
; WIPE_START
M204 S10000
G1 X22.21 Y6.673 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y7.987 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X24.006 Y6.591 E.0429
G1 X22.994 Y6.591 E.03109
G1 X22.994 Y7.987 E.0429
G1 X23.946 Y7.987 E.02924
G1 X23.659 Y7.64 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X23.659 Y6.939 E.01814
G1 X23.341 Y6.939 E.00821
G1 X23.341 Y7.64 E.01814
G1 X23.599 Y7.64 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y7.64 E-.09887
G1 X23.341 Y6.939 E-.2696
G1 X23.659 Y6.939 E-.12193
G1 X23.659 Y7.64 E-.2696
; WIPE_END
G1 E-.04 F1800
G1 X24.398 Y12.001 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X22.602 Y12.001 E.05957
G1 X22.602 Y9.82 E.07232
G1 X24.398 Y9.82 E.05957
G1 X24.398 Y11.941 E.07033
G1 X24.79 Y12.393 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4398
M204 S5000
G1 X22.21 Y12.393 E.07928
G1 X22.21 Y10.387 E.06162
G1 X22.21 Y9.987 E.01229
G1 X22.21 Y9.587 E.01229
G1 F3789.734
G1 X22.21 Y9.428 E.00489
G1 F2160
G1 X24.79 Y9.428 E.07928
G1 F3789.734
G1 X24.79 Y9.587 E.00489
G1 F4398
G1 X24.79 Y9.987 E.01229
G1 X24.79 Y10.387 E.01229
G1 X24.79 Y12.333 E.05978
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y12.379 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y11.609 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X24.006 Y10.213 E.0429
G1 X22.994 Y10.213 E.03109
G1 X22.994 Y11.609 E.0429
G1 X23.946 Y11.609 E.02924
G1 X23.659 Y11.261 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X23.659 Y10.56 E.01814
G1 X23.341 Y10.56 E.00821
G1 X23.341 Y11.261 E.01814
G1 X23.599 Y11.261 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y11.261 E-.09887
G1 X23.341 Y10.56 E-.2696
G1 X23.659 Y10.56 E-.12193
G1 X23.659 Y11.261 E-.2696
; WIPE_END
G1 E-.04 F1800
G1 X30.688 Y14.236 Z7.2 F30000
G1 X58.848 Y26.152 Z7.2
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X57.052 Y26.152 E.05957
G1 X57.052 Y24.307 E.06121
G1 X57.428 Y24.307 E.01246
G1 X58.848 Y24.307 E.04711
G1 X58.848 Y26.092 E.05922
G1 X59.24 Y26.544 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4398
M204 S5000
G1 X56.66 Y26.544 E.07928
G1 X56.66 Y23.921 E.0806
G1 X56.66 Y23.915 E.0002
G1 X57.428 Y23.915 E.02359
G1 X59.24 Y23.915 E.05569
G1 X59.24 Y23.921 E.0002
G1 X59.24 Y26.484 E.07876
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.531 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.699 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X57.444 Y25.76 E.0326
G1 X58.456 Y25.76 E.03109
G1 X58.456 Y24.699 E.0326
G1 X57.504 Y24.699 E.02924
G1 X57.791 Y25.046 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X57.791 Y25.413 E.00948
G1 X58.109 Y25.413 E.00821
G1 X58.109 Y25.046 E.00948
G1 X57.851 Y25.046 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y25.046 E-.14951
G1 X58.109 Y25.413 E-.21306
G1 X57.791 Y25.413 E-.18437
G1 X57.791 Y25.046 E-.21306
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y17.893 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X57.052 Y9.82 E.26779
G1 X58.848 Y9.82 E.05957
G1 X58.848 Y17.893 E.26779
G1 X57.112 Y17.893 E.05758
G1 X56.66 Y18.285 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4398
M204 S5000
G1 X56.66 Y18.279 E.00019
G1 X56.66 Y10.387 E.24249
G1 X56.66 Y9.987 E.01229
G1 X56.66 Y9.587 E.01229
G1 F3789.383
G1 X56.66 Y9.428 E.00489
G1 F2160
G1 X59.24 Y9.428 E.07928
G1 F3789.383
G1 X59.24 Y9.587 E.00489
G1 F4398
G1 X59.24 Y9.987 E.01229
G1 X59.24 Y10.387 E.01229
G1 X59.24 Y18.279 E.24249
G1 X59.24 Y18.285 E.0002
G1 X56.72 Y18.285 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.66 Y18.279 E-.02292
G1 X56.66 Y16.339 E-.73708
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.501 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X58.456 Y17.501 E.03109
G1 X58.456 Y10.213 E.22395
G1 X57.444 Y10.213 E.03109
G1 X57.444 Y17.441 E.22211
G1 X57.791 Y17.154 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X58.109 Y17.154 E.00821
G1 X58.109 Y10.56 E.17052
G1 X57.791 Y10.56 E.00821
G1 X57.791 Y17.094 E.16896
; WIPE_START
G1 F15000
G1 X57.791 Y15.094 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y12.001 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X51.602 Y12.001 E.05957
G1 X51.602 Y9.82 E.07232
G1 X53.398 Y9.82 E.05957
G1 X53.398 Y11.941 E.07033
G1 X53.79 Y12.393 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4398
M204 S5000
G1 X51.21 Y12.393 E.07928
G1 X51.21 Y10.387 E.06162
G1 X51.21 Y9.987 E.01229
G1 X51.21 Y9.587 E.01229
G1 F3789.734
G1 X51.21 Y9.428 E.00489
G1 F2160
G1 X53.79 Y9.428 E.07928
G1 F3789.734
G1 X53.79 Y9.587 E.00489
G1 F4398
G1 X53.79 Y9.987 E.01229
M73 P87 R1
G1 X53.79 Y10.387 E.01229
G1 X53.79 Y12.333 E.05978
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y12.379 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y11.609 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X53.006 Y11.609 E.03109
G1 X53.006 Y10.213 E.0429
G1 X51.994 Y10.213 E.03109
G1 X51.994 Y11.549 E.04105
G1 X52.341 Y11.261 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X52.659 Y11.261 E.00821
G1 X52.659 Y10.56 E.01814
G1 X52.341 Y10.56 E.00821
G1 X52.341 Y11.201 E.01659
; WIPE_START
G1 F15000
G1 X52.341 Y10.56 E-.24655
G1 X52.659 Y10.56 E-.12193
G1 X52.659 Y11.261 E-.2696
G1 X52.341 Y11.261 E-.12193
; WIPE_END
G1 E-.04 F1800
G1 X53.398 Y8.38 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4398
G1 X51.602 Y8.38 E.05957
G1 X51.602 Y6.199 E.07232
G1 X53.398 Y6.199 E.05957
G1 X53.398 Y8.32 E.07033
G1 X53.79 Y8.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X53.79 Y8.772 E.00489
G1 F2160
G1 X51.21 Y8.772 E.07928
G1 F3789.617
G1 X51.21 Y8.613 E.00489
G1 F4398
G1 X51.21 Y8.213 E.01229
G1 X51.21 Y7.813 E.01229
G1 X51.21 Y5.807 E.06162
G1 X53.79 Y5.807 E.07928
G1 X53.79 Y8.553 E.08436
; WIPE_START
G1 F12000
M204 S10000
G1 X53.79 Y8.772 E-.08322
G1 X52.009 Y8.772 E-.67678
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y7.987 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4398
G1 X53.006 Y7.987 E.03109
G1 X53.006 Y6.591 E.0429
G1 X51.994 Y6.591 E.03109
G1 X51.994 Y7.927 E.04105
G1 X52.341 Y7.64 F30000
; LINE_WIDTH: 0.36025
G1 F4398
G1 X52.659 Y7.64 E.00821
G1 X52.659 Y6.939 E.01814
G1 X52.341 Y6.939 E.00821
G1 X52.341 Y7.58 E.01659
; WIPE_START
G1 F15000
G1 X52.341 Y6.939 E-.24655
G1 X52.659 Y6.939 E-.12193
G1 X52.659 Y7.64 E-.2696
G1 X52.341 Y7.64 E-.12193
; WIPE_END
G1 E-.04 F1800
G1 X59.24 Y8.613 Z7.2 F30000
G1 Z6.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3789.617
M204 S5000
G1 X59.24 Y8.772 E.00489
G1 F2160
G1 X56.66 Y8.772 E.07928
G1 F3789.617
G1 X56.66 Y8.613 E.00489
G1 F4398
G1 X56.66 Y8.213 E.01229
G1 X56.66 Y7.79 E.01297
G1 X59.24 Y7.79 E.07928
G1 X59.24 Y8.553 E.02342
M204 S10000
G1 X59.044 Y8.281 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.63199
G1 F4398
G1 X56.856 Y8.281 E.10502
; CHANGE_LAYER
; Z_HEIGHT: 7
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10694.825
G1 X58.856 Y8.281 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 35/58
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
G1 X24.398 Y11.78
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4974
G1 X22.602 Y11.78 E.05957
G1 X22.602 Y10.601 E.03912
G1 X22.602 Y10.201 E.01327
G1 X22.602 Y9.801 E.01327
G1 F3899.032
G1 X22.602 Y9.401 E.01327
G1 F600
G1 X22.602 Y8.799 E.01996
G1 F3899.032
G1 X22.602 Y8.399 E.01327
G1 F4974
G1 X22.602 Y7.999 E.01327
G1 X22.602 Y7.599 E.01327
G1 X22.602 Y6.42 E.03912
G1 X24.398 Y6.42 E.05957
G1 X24.398 Y7.599 E.03912
G1 X24.398 Y7.999 E.01327
G1 X24.398 Y8.399 E.01327
G1 F3899.032
G1 X24.398 Y8.799 E.01327
G1 F600
G1 X24.398 Y9.401 E.01996
G1 F3899.032
G1 X24.398 Y9.801 E.01327
G1 F4974
G1 X24.398 Y10.201 E.01327
G1 X24.398 Y10.601 E.01327
G1 X24.398 Y11.72 E.03713
G1 X24.79 Y12.172 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4974
M204 S5000
G1 X22.21 Y12.172 E.07928
G1 X22.21 Y10.587 E.0487
G1 X22.21 Y10.187 E.01229
G1 X22.21 Y9.787 E.01229
G1 F3899.032
G1 X22.21 Y9.387 E.01229
G1 F600
G1 X22.21 Y8.813 E.01766
G1 F3899.032
G1 X22.21 Y8.413 E.01229
G1 F4974
G1 X22.21 Y8.013 E.01229
G1 X22.21 Y7.613 E.01229
G1 X22.21 Y6.028 E.0487
G1 X24.79 Y6.028 E.07928
G1 X24.79 Y7.613 E.0487
G1 X24.79 Y8.013 E.01229
G1 X24.79 Y8.413 E.01229
G1 F3899.032
G1 X24.79 Y8.813 E.01229
G1 F600
G1 X24.79 Y9.387 E.01766
G1 F3899.032
G1 X24.79 Y9.787 E.01229
G1 F4974
G1 X24.79 Y10.187 E.01229
G1 X24.79 Y10.587 E.01229
G1 X24.79 Y12.112 E.04685
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y12.159 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X23.956 Y11.338 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.5191
G1 F4974
G1 X23.956 Y10.862 E.01848
G1 X23.044 Y10.862 E.03541
G1 X23.044 Y11.338 E.01848
G1 X23.896 Y11.338 E.03308
G1 X23.878 Y10.605 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.4954
G1 F3000
G1 X23.878 Y7.764 E.10476
G1 X23.425 Y7.764 E.01668
G1 X23.425 Y10.436 E.0985
G1 X22.973 Y10.436 E.01668
G1 X22.973 Y7.595 E.10476
G1 X23.956 Y7.338 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51911
G1 F4974
G1 X23.956 Y6.862 E.01848
G1 X23.044 Y6.862 E.03541
G1 X23.044 Y7.338 E.01848
G1 X23.896 Y7.338 E.03308
; WIPE_START
G1 F13230.012
G1 X23.044 Y7.338 E-.324
G1 X23.044 Y6.862 E-.18095
G1 X23.715 Y6.862 E-.25505
; WIPE_END
G1 E-.04 F1800
G1 X31.245 Y8.109 Z7.4 F30000
G1 X53.398 Y11.78 Z7.4
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4974
G1 X51.602 Y11.78 E.05957
G1 X51.602 Y10.601 E.03912
G1 X51.602 Y10.201 E.01327
G1 X51.602 Y9.801 E.01327
G1 F3899.032
G1 X51.602 Y9.401 E.01327
G1 F600
G1 X51.602 Y8.799 E.01996
G1 F3899.032
G1 X51.602 Y8.399 E.01327
G1 F4974
G1 X51.602 Y7.999 E.01327
G1 X51.602 Y7.599 E.01327
G1 X51.602 Y6.42 E.03912
G1 X53.398 Y6.42 E.05957
G1 X53.398 Y7.599 E.03912
G1 X53.398 Y7.999 E.01327
G1 X53.398 Y8.399 E.01327
G1 F3899.032
G1 X53.398 Y8.799 E.01327
G1 F600
G1 X53.398 Y9.401 E.01996
G1 F3899.032
G1 X53.398 Y9.801 E.01327
G1 F4974
G1 X53.398 Y10.201 E.01327
G1 X53.398 Y10.601 E.01327
G1 X53.398 Y11.72 E.03713
G1 X53.79 Y12.172 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4974
M204 S5000
G1 X51.21 Y12.172 E.07928
G1 X51.21 Y10.587 E.0487
G1 X51.21 Y10.187 E.01229
G1 X51.21 Y9.787 E.01229
G1 F3899.032
G1 X51.21 Y9.387 E.01229
G1 F600
G1 X51.21 Y8.813 E.01766
G1 F3899.032
G1 X51.21 Y8.413 E.01229
G1 F4974
G1 X51.21 Y8.013 E.01229
G1 X51.21 Y7.613 E.01229
G1 X51.21 Y6.028 E.0487
G1 X53.79 Y6.028 E.07928
G1 X53.79 Y7.613 E.0487
G1 X53.79 Y8.013 E.01229
G1 X53.79 Y8.413 E.01229
G1 F3899.032
G1 X53.79 Y8.813 E.01229
G1 F600
G1 X53.79 Y9.387 E.01766
G1 F3899.032
G1 X53.79 Y9.787 E.01229
G1 F4974
G1 X53.79 Y10.187 E.01229
G1 X53.79 Y10.587 E.01229
G1 X53.79 Y12.112 E.04685
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y12.159 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X52.878 Y10.605 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.4954
G1 F3000
G1 X52.878 Y7.764 E.10476
G1 X52.425 Y7.764 E.01668
G1 X52.425 Y10.436 E.0985
G1 X51.973 Y10.436 E.01668
G1 X51.973 Y7.595 E.10476
G1 X52.044 Y7.338 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.51911
G1 F4974
G1 X52.956 Y7.338 E.03541
G1 X52.956 Y6.862 E.01848
G1 X52.044 Y6.862 E.03541
G1 X52.044 Y7.278 E.01615
; WIPE_START
G1 F13230.012
G1 X52.044 Y6.862 E-.15815
G1 X52.956 Y6.862 E-.3468
G1 X52.956 Y7.338 E-.18095
G1 X52.761 Y7.338 E-.0741
; WIPE_END
G1 E-.04 F1800
G1 X52.044 Y11.338 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; LINE_WIDTH: 0.5191
G1 F4974
G1 X52.956 Y11.338 E.03541
G1 X52.956 Y10.862 E.01848
G1 X52.044 Y10.862 E.03541
M73 P88 R1
G1 X52.044 Y11.278 E.01615
; WIPE_START
G1 F13230.291
G1 X52.044 Y10.862 E-.15815
G1 X52.956 Y10.862 E-.3468
G1 X52.956 Y11.338 E-.18095
G1 X52.761 Y11.338 E-.0741
; WIPE_END
G1 E-.04 F1800
G1 X56.914 Y17.742 Z7.4 F30000
G1 X57.052 Y17.956 Z7.4
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4974
G1 X57.052 Y10.601 E.24398
G1 X57.052 Y10.201 E.01327
G1 X57.052 Y9.801 E.01327
G1 F3899.032
G1 X57.052 Y9.401 E.01327
G1 F600
G1 X57.052 Y8.799 E.01996
G1 F1286.901
G1 X57.052 Y8.679 E.00398
G1 F4974
G1 X57.452 Y8.679 E.01327
G1 X57.852 Y8.679 E.01327
G1 X58.252 Y8.679 E.01327
G1 X58.848 Y8.679 E.01977
G1 F1286.901
G1 X58.848 Y8.799 E.00398
G1 F600
G1 X58.848 Y9.401 E.01996
G1 F3899.032
G1 X58.848 Y9.801 E.01327
G1 F4974
G1 X58.848 Y10.201 E.01327
G1 X58.848 Y10.601 E.01327
G1 X58.848 Y17.956 E.24398
G1 X57.112 Y17.956 E.05758
G1 X56.66 Y18.348 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4974
M204 S5000
G1 X56.66 Y18.326 E.00066
G1 X56.66 Y10.587 E.23779
G1 X56.66 Y10.187 E.01229
G1 X56.66 Y9.787 E.01229
G1 F3899.032
G1 X56.66 Y9.387 E.01229
G1 F600
G1 X56.66 Y8.813 E.01766
G1 F4974
G1 X56.66 Y8.287 E.01615
G1 X57.06 Y8.287 E.01229
G1 X58.84 Y8.287 E.05469
G1 X59.24 Y8.287 E.01229
G1 X59.24 Y8.813 E.01615
G1 F600
G1 X59.24 Y9.387 E.01766
G1 F3899.032
G1 X59.24 Y9.787 E.01229
G1 F4974
G1 X59.24 Y10.187 E.01229
G1 X59.24 Y10.587 E.01229
G1 X59.24 Y18.326 E.2378
G1 X59.24 Y18.348 E.00066
G1 X56.72 Y18.348 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.66 Y18.326 E-.02424
G1 X56.66 Y16.39 E-.73576
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.564 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4974
G1 X58.456 Y17.564 E.03109
G1 X58.456 Y10.813 E.20744
G1 X57.444 Y10.813 E.03109
G1 X57.444 Y17.504 E.20559
G1 X57.791 Y17.217 F30000
; LINE_WIDTH: 0.36025
G1 F4974
G1 X58.109 Y17.217 E.00821
G1 X58.109 Y11.16 E.15661
G1 X57.791 Y11.16 E.00821
G1 X57.791 Y17.157 E.15506
G1 X58.684 Y10.419 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.45354
G1 F3000
G1 X57.385 Y10.419 E.04347
G1 X57.385 Y10.008 E.01374
G1 X58.515 Y10.008 E.03779
G1 X58.515 Y9.598 E.01374
G1 X57.385 Y9.598 E.03779
G1 X57.385 Y9.187 E.01374
G1 X58.684 Y9.187 E.04347
; WIPE_START
G1 X57.385 Y9.187 E-.49363
G1 X57.385 Y9.598 E-.15604
G1 X57.676 Y9.598 E-.11033
; WIPE_END
G1 E-.04 F1800
G1 X58.216 Y17.211 Z7.4 F30000
G1 X58.848 Y26.118 Z7.4
G1 Z7
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4974
G1 X57.052 Y26.118 E.05957
G1 X57.052 Y24.244 E.06216
G1 X58.848 Y24.244 E.05957
G1 X58.848 Y26.058 E.06017
G1 X59.24 Y26.51 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4974
M204 S5000
G1 X56.66 Y26.51 E.07928
G1 X56.66 Y23.874 E.08101
G1 X56.66 Y23.852 E.00066
G1 X59.24 Y23.852 E.07928
G1 X59.24 Y23.874 E.00066
G1 X59.24 Y26.45 E.07917
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.497 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.636 Z7.4 F30000
G1 Z7
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F4974
G1 X57.444 Y25.726 E.03349
G1 X58.456 Y25.726 E.03109
G1 X58.456 Y24.636 E.03349
G1 X57.504 Y24.636 E.02924
G1 X57.791 Y24.983 F30000
; LINE_WIDTH: 0.36025
G1 F4974
G1 X57.791 Y25.379 E.01022
G1 X58.109 Y25.379 E.00821
G1 X58.109 Y24.983 E.01022
G1 X57.851 Y24.983 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 7.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.983 E-.14323
G1 X58.109 Y25.379 E-.22007
G1 X57.791 Y25.379 E-.17663
G1 X57.791 Y24.983 E-.22007
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 36/58
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
G1 X24.398 Y11.521
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3511
G1 X22.602 Y11.521 E.05957
G1 X22.602 Y6.679 E.16061
G1 X24.398 Y6.679 E.05957
G1 X24.398 Y11.461 E.15861
G1 X24.79 Y11.913 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3511
M204 S5000
G1 X22.21 Y11.913 E.07928
G1 X22.21 Y6.287 E.17286
G1 X24.79 Y6.287 E.07928
G1 X24.79 Y11.853 E.17102
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y11.899 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y11.129 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3511
G1 X24.006 Y7.071 E.12467
G1 X22.994 Y7.071 E.03109
G1 X22.994 Y11.129 E.12467
G1 X23.946 Y11.129 E.02924
G1 X23.659 Y10.782 F30000
; LINE_WIDTH: 0.36026
G1 F3511
G1 X23.659 Y7.418 E.08697
G1 X23.341 Y7.418 E.00821
G1 X23.341 Y10.782 E.08697
G1 X23.599 Y10.782 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y10.782 E-.09779
G1 X23.341 Y9.039 E-.66221
; WIPE_END
G1 E-.04 F1800
G1 X30.948 Y9.667 Z7.6 F30000
G1 X53.398 Y11.521 Z7.6
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3511
G1 X51.602 Y11.521 E.05957
G1 X51.602 Y6.679 E.16061
G1 X53.398 Y6.679 E.05957
G1 X53.398 Y11.461 E.15861
G1 X53.79 Y11.913 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3511
M204 S5000
G1 X51.21 Y11.913 E.07928
G1 X51.21 Y6.287 E.17286
G1 X53.79 Y6.287 E.07928
G1 X53.79 Y11.853 E.17102
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y11.899 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y11.129 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3511
G1 X53.006 Y11.129 E.03109
G1 X53.006 Y7.071 E.12467
G1 X51.994 Y7.071 E.03109
G1 X51.994 Y11.069 E.12283
G1 X52.341 Y10.782 F30000
; LINE_WIDTH: 0.36025
G1 F3511
G1 X52.659 Y10.782 E.00821
G1 X52.659 Y7.418 E.08696
G1 X52.341 Y7.418 E.00821
G1 X52.341 Y10.722 E.08541
; WIPE_START
G1 F15000
G1 X52.341 Y8.722 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.786 Y15.532 Z7.6 F30000
G1 X57.052 Y18.035 Z7.6
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3511
G1 X57.052 Y9.176 E.29388
G1 X58.848 Y9.176 E.05957
G1 X58.848 Y18.035 E.29388
G1 X57.112 Y18.035 E.05758
G1 X56.66 Y18.427 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3511
M204 S5000
G1 X56.66 Y18.389 E.00117
G1 X56.66 Y8.784 E.29514
G1 X59.24 Y8.784 E.07928
G1 X59.24 Y18.389 E.29514
G1 X59.24 Y18.427 E.00117
G1 X56.72 Y18.427 E.07743
; WIPE_START
G1 F12000
M204 S10000
G1 X56.66 Y18.389 E-.02703
G1 X56.66 Y16.46 E-.73297
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.643 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3511
G1 X58.456 Y17.643 E.03109
G1 X58.456 Y9.568 E.24812
G1 X57.444 Y9.568 E.03109
G1 X57.444 Y17.583 E.24628
G1 X57.791 Y17.296 F30000
; LINE_WIDTH: 0.36025
G1 F3511
G1 X58.109 Y17.296 E.00821
G1 X58.109 Y9.915 E.19085
G1 X57.791 Y9.915 E.00821
G1 X57.791 Y17.236 E.1893
; WIPE_START
G1 F15000
G1 X57.791 Y15.236 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.532 Y22.832 Z7.6 F30000
G1 X58.848 Y26.078 Z7.6
G1 Z7.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3511
G1 X57.052 Y26.078 E.05957
G1 X57.052 Y24.165 E.06347
G1 X58.848 Y24.165 E.05957
G1 X58.848 Y26.018 E.06148
G1 X59.24 Y26.47 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3511
M204 S5000
G1 X56.66 Y26.47 E.07928
G1 X56.66 Y23.811 E.08171
G1 X56.66 Y23.773 E.00117
G1 X59.24 Y23.773 E.07928
G1 X59.24 Y23.811 E.00117
G1 X59.24 Y26.41 E.07987
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.457 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.557 Z7.6 F30000
G1 Z7.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3511
G1 X57.444 Y25.686 E.0347
G1 X58.456 Y25.686 E.03109
G1 X58.456 Y24.557 E.0347
G1 X57.504 Y24.557 E.02924
G1 X57.791 Y24.904 F30000
; LINE_WIDTH: 0.36025
G1 F3511
G1 X57.791 Y25.339 E.01124
G1 X58.109 Y25.339 E.00821
G1 X58.109 Y24.904 E.01124
G1 X57.851 Y24.904 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.904 E-.13541
G1 X58.109 Y25.339 E-.22881
G1 X57.791 Y25.339 E-.16698
G1 X57.791 Y24.904 E-.22881
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 37/58
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
G1 X24.398 Y11.232
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3307
G1 X22.602 Y11.232 E.05957
G1 X22.602 Y6.968 E.14145
G1 X24.398 Y6.968 E.05957
G1 X24.398 Y11.172 E.13946
G1 X24.79 Y11.624 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3307
M204 S5000
G1 X22.21 Y11.624 E.07928
G1 X22.21 Y6.576 E.15512
G1 X24.79 Y6.576 E.07928
G1 X24.79 Y11.564 E.15328
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y11.611 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y10.84 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3307
G1 X24.006 Y7.36 E.10693
G1 X22.994 Y7.36 E.03109
G1 X22.994 Y10.84 E.10693
G1 X23.946 Y10.84 E.02924
G1 X23.659 Y10.493 F30000
; LINE_WIDTH: 0.36026
G1 F3307
G1 X23.659 Y7.707 E.07203
G1 X23.341 Y7.707 E.00821
G1 X23.341 Y10.493 E.07203
G1 X23.599 Y10.493 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y10.493 E-.09779
G1 X23.341 Y8.75 E-.66221
; WIPE_END
G1 E-.04 F1800
G1 X30.948 Y9.378 Z7.8 F30000
G1 X53.398 Y11.232 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3307
G1 X51.602 Y11.232 E.05957
G1 X51.602 Y6.968 E.14145
G1 X53.398 Y6.968 E.05957
G1 X53.398 Y11.172 E.13946
G1 X53.79 Y11.624 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3307
M204 S5000
G1 X51.21 Y11.624 E.07928
G1 X51.21 Y6.576 E.15512
G1 X53.79 Y6.576 E.07928
G1 X53.79 Y11.564 E.15328
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y11.611 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y10.84 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3307
G1 X53.006 Y10.84 E.03109
G1 X53.006 Y7.36 E.10693
G1 X51.994 Y7.36 E.03109
G1 X51.994 Y10.78 E.10508
G1 X52.341 Y10.493 F30000
; LINE_WIDTH: 0.36025
G1 F3307
G1 X52.659 Y10.493 E.00821
G1 X52.659 Y7.707 E.07203
G1 X52.341 Y7.707 E.00821
G1 X52.341 Y10.433 E.07048
; WIPE_START
G1 F15000
G1 X52.341 Y8.433 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.676 Y15.298 Z7.8 F30000
G1 X57.052 Y18.133 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3307
G1 X57.052 Y9.672 E.28065
G1 X58.848 Y9.672 E.05957
G1 X58.848 Y18.133 E.28065
G1 X57.112 Y18.133 E.05758
G1 X56.66 Y18.525 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3307
M204 S5000
G1 X56.66 Y18.468 E.00175
G1 X56.66 Y9.28 E.28231
G1 X59.24 Y9.28 E.07928
G1 X59.24 Y18.068 E.27002
G1 X59.24 Y18.468 E.01229
G1 X59.24 Y18.525 E.00175
G1 X56.72 Y18.525 E.07743
; WIPE_START
G1 F9300
M204 S10000
G1 X56.66 Y18.468 E-.03145
G1 X56.66 Y16.551 E-.72855
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.741 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3307
G1 X58.456 Y17.741 E.03109
G1 X58.456 Y10.064 E.23587
M73 P89 R1
G1 X57.444 Y10.064 E.03109
G1 X57.444 Y17.681 E.23403
G1 X57.791 Y17.394 F30000
; LINE_WIDTH: 0.36025
G1 F3307
G1 X58.109 Y17.394 E.00821
G1 X58.109 Y10.412 E.18055
G1 X57.791 Y10.412 E.00821
G1 X57.791 Y17.334 E.17899
; WIPE_START
G1 F15000
G1 X57.791 Y15.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.541 Y22.929 Z7.8 F30000
G1 X58.848 Y26.039 Z7.8
G1 Z7.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3307
G1 X57.052 Y26.039 E.05957
G1 X57.052 Y24.067 E.0654
G1 X58.848 Y24.067 E.05957
G1 X58.848 Y25.979 E.06341
G1 X59.24 Y26.431 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3307
M204 S5000
G1 X56.66 Y26.431 E.07928
G1 X56.66 Y24.132 E.07063
G1 X56.66 Y23.732 E.01229
G1 X56.66 Y23.675 E.00175
G1 X59.24 Y23.675 E.07928
G1 X59.24 Y23.732 E.00175
G1 X59.24 Y24.132 E.01229
G1 X59.24 Y26.371 E.06879
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.417 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.459 Z7.8 F30000
G1 Z7.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3307
G1 X57.444 Y25.647 E.03649
G1 X58.456 Y25.647 E.03109
G1 X58.456 Y24.459 E.03649
G1 X57.504 Y24.459 E.02924
G1 X57.791 Y24.806 F30000
; LINE_WIDTH: 0.36025
G1 F3307
G1 X57.791 Y25.299 E.01275
G1 X58.109 Y25.299 E.00821
G1 X58.109 Y24.806 E.01275
G1 X57.851 Y24.806 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 7.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.806 E-.1253
G1 X58.109 Y25.299 E-.24009
G1 X57.791 Y25.299 E-.15452
G1 X57.791 Y24.806 E-.24009
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 38/58
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
G1 X24.398 Y10.897
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3089
G1 X22.602 Y10.897 E.05957
G1 X22.602 Y7.303 E.11925
G1 X24.398 Y7.303 E.05957
G1 X24.398 Y10.837 E.11725
G1 X24.79 Y11.289 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3089
M204 S5000
G1 X22.21 Y11.289 E.07928
G1 X22.21 Y6.911 E.13455
G1 X24.79 Y6.911 E.07928
G1 X24.79 Y11.229 E.13271
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y11.276 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y10.505 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3089
G1 X24.006 Y7.695 E.08636
G1 X22.994 Y7.695 E.03109
G1 X22.994 Y10.505 E.08636
G1 X23.946 Y10.505 E.02924
G1 X23.659 Y10.158 F30000
; LINE_WIDTH: 0.36026
G1 F3089
G1 X23.659 Y8.042 E.05472
G1 X23.341 Y8.042 E.00821
G1 X23.341 Y10.158 E.05472
G1 X23.599 Y10.158 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y10.158 E-.09779
G1 X23.341 Y8.415 E-.66221
; WIPE_END
G1 E-.04 F1800
G1 X30.948 Y9.044 Z8 F30000
G1 X53.398 Y10.897 Z8
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3089
G1 X51.602 Y10.897 E.05957
G1 X51.602 Y7.303 E.11925
G1 X53.398 Y7.303 E.05957
G1 X53.398 Y10.837 E.11725
G1 X53.79 Y11.289 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3089
M204 S5000
G1 X51.21 Y11.289 E.07928
G1 X51.21 Y6.911 E.13455
G1 X53.79 Y6.911 E.07928
G1 X53.79 Y11.229 E.13271
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y11.276 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y10.505 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3089
G1 X53.006 Y10.505 E.03109
G1 X53.006 Y7.695 E.08636
G1 X51.994 Y7.695 E.03109
G1 X51.994 Y10.445 E.08452
G1 X52.341 Y10.158 F30000
; LINE_WIDTH: 0.36025
G1 F3089
G1 X52.659 Y10.158 E.00821
G1 X52.659 Y8.042 E.05472
G1 X52.341 Y8.042 E.00821
G1 X52.341 Y10.098 E.05317
; WIPE_START
G1 F15000
G1 X52.341 Y8.098 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X55.553 Y15.022 Z8 F30000
G1 X57.052 Y18.253 Z8
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3089
G1 X57.052 Y10.169 E.26816
G1 X58.848 Y10.169 E.05957
G1 X58.848 Y18.253 E.26816
G1 X57.112 Y18.253 E.05758
G1 X56.66 Y18.645 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3089
M204 S5000
G1 X56.66 Y18.566 E.00242
G1 X56.66 Y9.777 E.27007
G1 X59.24 Y9.777 E.07928
G1 X59.24 Y18.166 E.25777
G1 X59.24 Y18.566 E.01229
G1 X59.24 Y18.645 E.00242
G1 X56.72 Y18.645 E.07743
; WIPE_START
G1 F5700
M204 S10000
G1 X56.66 Y18.566 E-.03767
G1 X56.66 Y16.665 E-.72233
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y17.861 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3089
G1 X58.456 Y17.861 E.03109
G1 X58.456 Y10.561 E.2243
G1 X57.444 Y10.561 E.03109
G1 X57.444 Y17.801 E.22245
G1 X57.791 Y17.514 F30000
; LINE_WIDTH: 0.36025
G1 F3089
G1 X58.109 Y17.514 E.00821
G1 X58.109 Y10.908 E.1708
G1 X57.791 Y10.908 E.00821
G1 X57.791 Y17.454 E.16925
; WIPE_START
G1 F15000
G1 X57.791 Y15.454 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.553 Y23.048 Z8 F30000
G1 X58.848 Y25.995 Z8
G1 Z7.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3089
G1 X57.052 Y25.995 E.05957
G1 X57.052 Y23.947 E.06795
G1 X58.848 Y23.947 E.05957
G1 X58.848 Y25.935 E.06595
G1 X59.24 Y26.387 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3089
M204 S5000
G1 X56.66 Y26.387 E.07928
G1 X56.66 Y24.034 E.07232
G1 X56.66 Y23.634 E.01229
G1 X56.66 Y23.555 E.00242
G1 X59.24 Y23.555 E.07928
G1 X59.24 Y23.634 E.00242
G1 X59.24 Y24.034 E.01229
G1 X59.24 Y26.327 E.07047
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.374 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.339 Z8 F30000
G1 Z7.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F3089
G1 X57.444 Y25.603 E.03884
G1 X58.456 Y25.603 E.03109
G1 X58.456 Y24.339 E.03884
G1 X57.504 Y24.339 E.02924
G1 X57.791 Y24.686 F30000
; LINE_WIDTH: 0.36025
G1 F3089
G1 X57.791 Y25.256 E.01473
G1 X58.109 Y25.256 E.00821
G1 X58.109 Y24.686 E.01473
G1 X57.851 Y24.686 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 7.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.686 E-.11409
G1 X58.109 Y25.256 E-.2526
G1 X57.791 Y25.256 E-.1407
G1 X57.791 Y24.686 E-.2526
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 39/58
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
G1 X24.398 Y10.475
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2833
G1 X22.602 Y10.475 E.05957
G1 X22.602 Y7.725 E.0912
G1 X24.398 Y7.725 E.05957
G1 X24.398 Y10.415 E.0892
G1 X24.79 Y10.867 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2833
M204 S5000
G1 X22.21 Y10.867 E.07928
G1 X22.21 Y7.333 E.10857
G1 X24.79 Y7.333 E.07928
G1 X24.79 Y10.807 E.10673
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y10.853 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.006 Y10.083 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2833
G1 X24.006 Y8.117 E.06038
G1 X22.994 Y8.117 E.03109
G1 X22.994 Y10.083 E.06038
G1 X23.946 Y10.083 E.02924
G1 X23.659 Y9.735 F30000
; LINE_WIDTH: 0.36026
G1 F2833
G1 X23.659 Y8.465 E.03286
G1 X23.341 Y8.465 E.00821
G1 X23.341 Y9.735 E.03286
G1 X23.599 Y9.735 E.00665
; WIPE_START
G1 F15000
G1 X23.341 Y9.735 E-.09779
G1 X23.341 Y8.465 E-.48284
G1 X23.659 Y8.465 E-.12059
G1 X23.659 Y8.619 E-.05879
; WIPE_END
G1 E-.04 F1800
G1 X31.276 Y9.095 Z8.2 F30000
G1 X53.398 Y10.475 Z8.2
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2833
G1 X51.602 Y10.475 E.05957
G1 X51.602 Y7.725 E.0912
G1 X53.398 Y7.725 E.05957
G1 X53.398 Y10.415 E.0892
G1 X53.79 Y10.867 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2833
M204 S5000
G1 X51.21 Y10.867 E.07928
G1 X51.21 Y7.333 E.10857
G1 X53.79 Y7.333 E.07928
G1 X53.79 Y10.807 E.10673
; WIPE_START
G1 F12000
M204 S10000
G1 X51.791 Y10.853 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X51.994 Y10.083 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2833
G1 X53.006 Y10.083 E.03109
G1 X53.006 Y8.117 E.06038
M73 P90 R1
G1 X51.994 Y8.117 E.03109
G1 X51.994 Y10.023 E.05854
G1 X52.341 Y9.735 F30000
; LINE_WIDTH: 0.36025
G1 F2833
G1 X52.659 Y9.735 E.00821
G1 X52.659 Y8.465 E.03286
G1 X52.341 Y8.465 E.00821
G1 X52.341 Y9.675 E.03131
; WIPE_START
G1 F15000
G1 X52.341 Y8.465 E-.46004
G1 X52.659 Y8.465 E-.12059
G1 X52.659 Y8.937 E-.17937
; WIPE_END
G1 E-.04 F1800
G1 X55.872 Y15.86 Z8.2 F30000
G1 X57.052 Y18.401 Z8.2
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2833
G1 X57.052 Y10.666 E.2566
G1 X58.848 Y10.666 E.05957
G1 X58.848 Y18.401 E.2566
G1 X57.112 Y18.401 E.05758
G1 X56.66 Y18.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2833
M204 S5000
G1 X56.66 Y18.686 E.0033
G1 X56.66 Y18.286 E.01229
G1 X56.66 Y10.274 E.2462
G1 X59.24 Y10.274 E.07928
G1 X59.24 Y17.886 E.23391
G1 X59.24 Y18.286 E.01229
G1 X59.24 Y18.686 E.01229
G1 X59.24 Y18.793 E.0033
G1 X56.72 Y18.793 E.07743
; WIPE_START
G1 F2880
M204 S10000
G1 X56.66 Y18.686 E-.04672
G1 X56.66 Y18.286 E-.152
G1 X56.66 Y16.809 E-.56128
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.009 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2833
G1 X58.456 Y18.009 E.03109
G1 X58.456 Y11.058 E.21359
G1 X57.444 Y11.058 E.03109
G1 X57.444 Y17.949 E.21175
G1 X57.791 Y17.662 F30000
; LINE_WIDTH: 0.36025
G1 F2833
G1 X58.109 Y17.662 E.00821
G1 X58.109 Y11.405 E.1618
G1 X57.791 Y11.405 E.00821
G1 X57.791 Y17.602 E.16025
; WIPE_START
G1 F15000
G1 X57.791 Y15.602 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.568 Y23.195 Z8.2 F30000
G1 X58.848 Y25.927 Z8.2
G1 Z7.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2833
G1 X57.052 Y25.927 E.05957
G1 X57.052 Y23.799 E.07061
G1 X58.848 Y23.799 E.05957
G1 X58.848 Y25.867 E.06862
G1 X59.24 Y26.32 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2833
M204 S5000
G1 X56.66 Y26.32 E.07928
G1 X56.66 Y24.314 E.06162
G1 X56.66 Y23.914 E.01229
G1 X56.66 Y23.514 E.01229
G1 X56.66 Y23.407 E.0033
G1 X59.24 Y23.407 E.07928
G1 X59.24 Y23.514 E.0033
G1 X59.24 Y23.914 E.01229
G1 X59.24 Y24.314 E.01229
G1 X59.24 Y26.26 E.05978
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.306 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.191 Z8.2 F30000
G1 Z7.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2833
G1 X57.444 Y25.535 E.04131
G1 X58.456 Y25.535 E.03109
G1 X58.456 Y24.191 E.04131
G1 X57.504 Y24.191 E.02924
G1 X57.791 Y24.538 F30000
; LINE_WIDTH: 0.36026
G1 F2833
G1 X57.791 Y25.188 E.01681
G1 X58.109 Y25.188 E.00821
G1 X58.109 Y24.538 E.01681
G1 X57.851 Y24.538 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.538 E-.1043
G1 X58.109 Y25.188 E-.26354
G1 X57.791 Y25.188 E-.12862
G1 X57.791 Y24.538 E-.26354
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 40/58
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
G1 X24.79 Y10.292
G1 Z8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2562
M204 S5000
G1 X22.21 Y10.292 E.07928
G1 X22.21 Y7.908 E.07327
G1 X24.79 Y7.908 E.07928
G1 X24.79 Y10.232 E.07143
; WIPE_START
G1 F12000
M204 S10000
G1 X22.791 Y10.279 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.583 Y9.23 Z8.4 F30000
G1 Z8
G1 E.8 F1800
; FEATURE: Top surface
G1 F2562
M204 S2000
G1 X23.727 Y10.085 E.03717
G1 X23.194 Y10.085
G1 X24.583 Y8.696 E.06034
G1 X24.583 Y8.163
G1 X22.661 Y10.085 E.08351
G1 X22.417 Y9.795
G1 X24.097 Y8.115 E.073
G1 X23.564 Y8.115
G1 X22.417 Y9.262 E.04983
G1 X22.417 Y8.728
G1 X23.031 Y8.115 E.02665
; WIPE_START
G1 F12000
M204 S10000
G1 X22.417 Y8.728 E-.32963
G1 X22.417 Y9.262 E-.20264
G1 X22.841 Y8.838 E-.22773
; WIPE_END
G1 E-.04 F1800
G1 X30.465 Y9.196 Z8.4 F30000
G1 X53.79 Y10.292 Z8.4
G1 Z8
G1 E.8 F1800
; FEATURE: Outer wall
G1 F2562
M204 S5000
G1 X51.21 Y10.292 E.07928
G1 X51.21 Y7.908 E.07327
G1 X53.79 Y7.908 E.07928
G1 X53.79 Y10.232 E.07143
M204 S10000
G1 X53.056 Y10.085 F30000
; FEATURE: Top surface
G1 F2562
M204 S2000
G1 X53.583 Y9.559 E.02286
G1 X53.583 Y9.025
G1 X52.523 Y10.085 E.04604
G1 X51.99 Y10.085
G1 X53.583 Y8.492 E.06921
G1 X53.426 Y8.115
G1 X51.457 Y10.085 E.08559
G1 X51.417 Y9.591
G1 X52.893 Y8.115 E.06413
G1 X52.36 Y8.115
G1 X51.417 Y9.058 E.04096
G1 X51.417 Y8.524
G1 X51.827 Y8.115 E.01778
; WIPE_START
G1 F12000
M204 S10000
G1 X51.417 Y8.524 E-.21995
G1 X51.417 Y9.058 E-.20264
G1 X52.045 Y8.43 E-.33742
; WIPE_END
G1 E-.04 F1800
G1 X55.422 Y15.275 Z8.4 F30000
G1 X57.052 Y18.58 Z8.4
G1 Z8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2562
G1 X57.052 Y11.162 E.24607
G1 X58.848 Y11.162 E.05957
G1 X58.848 Y18.58 E.24607
G1 X57.112 Y18.58 E.05758
G1 X56.66 Y18.972 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2562
M204 S5000
G1 X56.66 Y18.834 E.00424
G1 X56.66 Y18.434 E.01229
G1 X56.66 Y10.77 E.2355
G1 X59.24 Y10.77 E.07928
G1 X59.24 Y18.034 E.22321
G1 X59.24 Y18.434 E.01229
G1 X59.24 Y18.834 E.01229
G1 X59.24 Y18.972 E.00424
G1 F2520
G1 X56.72 Y18.972 E.07743
; WIPE_START
M204 S10000
G1 X56.66 Y18.834 E-.05723
G1 X56.66 Y18.434 E-.152
G1 X56.66 Y16.985 E-.55077
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.188 Z8.4 F30000
G1 Z8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2562
G1 X58.456 Y18.188 E.03109
G1 X58.456 Y11.554 E.20384
G1 X57.444 Y11.554 E.03109
G1 X57.444 Y18.128 E.202
G1 X57.791 Y17.841 F30000
; LINE_WIDTH: 0.36025
G1 F2562
G1 X58.109 Y17.841 E.00821
G1 X58.109 Y11.902 E.15359
G1 X57.791 Y11.902 E.00821
G1 X57.791 Y17.781 E.15204
; WIPE_START
G1 F15000
G1 X57.791 Y15.781 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.587 Y23.372 Z8.4 F30000
G1 X58.848 Y25.86 Z8.4
G1 Z8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2562
G1 X57.052 Y25.86 E.05957
G1 X57.052 Y23.62 E.0743
G1 X58.848 Y23.62 E.05957
G1 X58.848 Y25.8 E.07231
G1 X59.24 Y26.252 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2562
M204 S5000
G1 X56.66 Y26.252 E.07928
G1 X56.66 Y24.166 E.0641
G1 X56.66 Y23.766 E.01229
G1 X56.66 Y23.366 E.01229
G1 X56.66 Y23.228 E.00424
G1 F2520
G1 X59.24 Y23.228 E.07928
G1 F2562
G1 X59.24 Y23.366 E.00424
G1 X59.24 Y23.766 E.01229
G1 X59.24 Y24.166 E.01229
G1 X59.24 Y26.192 E.06225
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.238 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.012 Z8.4 F30000
G1 Z8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2562
G1 X57.444 Y25.467 E.04473
G1 X58.456 Y25.467 E.03109
G1 X58.456 Y24.012 E.04473
G1 X57.504 Y24.012 E.02924
G1 X57.791 Y24.359 F30000
; LINE_WIDTH: 0.36025
G1 F2562
G1 X57.791 Y25.12 E.01969
G1 X58.109 Y25.12 E.00821
G1 X58.109 Y24.359 E.01969
G1 X57.851 Y24.359 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 8.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X58.109 Y24.359 E-.09779
G1 X58.109 Y25.12 E-.28934
G1 X57.791 Y25.12 E-.12059
G1 X57.791 Y24.456 E-.25228
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 41/58
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
G17
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
G1 X58.848 Y25.792
G1 Z8.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1537
G1 X57.052 Y25.792 E.05957
G1 X57.052 Y23.42 E.07866
G1 X58.848 Y23.42 E.05957
G1 X58.848 Y25.732 E.07667
G1 X59.24 Y26.184 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1537
M204 S5000
G1 X56.66 Y26.184 E.07928
G1 X56.66 Y23.987 E.06751
G1 X56.66 Y23.587 E.01229
G1 X56.66 Y23.187 E.01229
G1 X56.66 Y23.028 E.00486
G1 X59.24 Y23.028 E.07928
G1 X59.24 Y23.187 E.00486
G1 X59.24 Y23.587 E.01229
G1 X59.24 Y23.987 E.01229
G1 X59.24 Y26.124 E.06567
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.17 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.813 Z8.6 F30000
G1 Z8.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1537
G1 X57.444 Y25.4 E.04876
G1 X58.456 Y25.4 E.03109
G1 X58.456 Y23.813 E.04876
G1 X57.504 Y23.813 E.02924
G1 X57.791 Y24.16 F30000
; LINE_WIDTH: 0.36025
G1 F1537
G1 X57.791 Y25.052 E.02308
G1 X58.109 Y25.052 E.00821
G1 X58.109 Y24.16 E.02308
G1 X57.851 Y24.16 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y24.16 E-.09779
G1 X58.109 Y25.052 E-.3392
G1 X57.791 Y25.052 E-.12059
M73 P91 R1
G1 X57.791 Y24.52 E-.20242
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.78 Z8.6 F30000
G1 Z8.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1537
G1 X57.052 Y11.659 E.2362
G1 X58.848 Y11.659 E.05957
G1 X58.848 Y18.78 E.2362
G1 X57.112 Y18.78 E.05758
G1 X56.66 Y19.172 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1537
M204 S5000
G1 X56.66 Y19.013 E.00486
G1 X56.66 Y18.613 E.01229
G1 X56.66 Y11.267 E.22574
G1 X59.24 Y11.267 E.07928
G1 X59.24 Y18.213 E.21345
G1 X59.24 Y18.613 E.01229
G1 X59.24 Y19.013 E.01229
G1 X59.24 Y19.172 E.00486
G1 X56.72 Y19.172 E.07743
; WIPE_START
G1 F2160
M204 S10000
G1 X56.66 Y19.013 E-.06427
G1 X56.66 Y18.613 E-.152
G1 X56.66 Y17.183 E-.54373
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.387 Z8.6 F30000
G1 Z8.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1537
G1 X58.456 Y18.387 E.03109
G1 X58.456 Y12.051 E.1947
G1 X57.444 Y12.051 E.03109
G1 X57.444 Y18.327 E.19285
G1 X57.791 Y18.04 F30000
; LINE_WIDTH: 0.36025
G1 F1537
G1 X58.109 Y18.04 E.00821
G1 X58.109 Y12.398 E.1459
G1 X57.791 Y12.398 E.00821
G1 X57.791 Y17.98 E.14434
; CHANGE_LAYER
; Z_HEIGHT: 8.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y15.98 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 42/58
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
G1 X58.848 Y25.705
G1 Z8.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1513
G1 X57.052 Y25.705 E.05957
G1 X57.052 Y23.22 E.08243
G1 X58.848 Y23.22 E.05957
G1 X58.848 Y25.645 E.08044
G1 X59.24 Y26.098 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1513
M204 S5000
G1 X56.66 Y26.098 E.07928
G1 X56.66 Y23.787 E.07099
G1 X56.66 Y23.387 E.01229
G1 X56.66 Y22.987 E.01229
G1 X56.66 Y22.828 E.00489
G1 X59.24 Y22.828 E.07928
G1 X59.24 Y22.987 E.00489
G1 X59.24 Y23.387 E.01229
G1 X59.24 Y23.787 E.01229
G1 X59.24 Y26.038 E.06914
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y26.084 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.613 Z8.8 F30000
G1 Z8.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1513
G1 X57.444 Y25.313 E.05226
G1 X58.456 Y25.313 E.03109
G1 X58.456 Y23.613 E.05226
G1 X57.504 Y23.613 E.02924
G1 X57.791 Y23.96 F30000
; LINE_WIDTH: 0.36025
G1 F1513
G1 X57.791 Y24.966 E.02603
G1 X58.109 Y24.966 E.00821
G1 X58.109 Y23.96 E.02603
G1 X57.851 Y23.96 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.96 E-.09779
G1 X58.109 Y24.966 E-.38247
G1 X57.791 Y24.966 E-.12059
G1 X57.791 Y24.547 E-.15915
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y18.98 Z8.8 F30000
G1 Z8.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1513
G1 X57.052 Y12.156 E.22636
G1 X58.848 Y12.156 E.05957
G1 X58.848 Y18.98 E.22636
G1 X57.112 Y18.98 E.05758
G1 X56.66 Y19.213 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1513
M204 S5000
G1 X56.66 Y11.763 E.22889
G1 X59.24 Y11.763 E.07928
G1 X59.24 Y18.413 E.20431
G1 X59.24 Y18.813 E.01229
G1 X59.24 Y19.213 E.01229
G1 X59.24 Y19.372 E.00489
G1 X56.66 Y19.372 E.07928
G1 X56.66 Y19.273 E.00304
; WIPE_START
G1 F3121.419
M204 S10000
G1 X56.66 Y17.273 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.587 Z8.8 F30000
G1 Z8.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1513
G1 X58.456 Y18.587 E.03109
G1 X58.456 Y12.548 E.18558
G1 X57.444 Y12.548 E.03109
G1 X57.444 Y18.527 E.18374
G1 X57.791 Y18.24 F30000
; LINE_WIDTH: 0.36025
G1 F1513
G1 X58.109 Y18.24 E.00821
G1 X58.109 Y12.895 E.13823
G1 X57.791 Y12.895 E.00821
G1 X57.791 Y18.18 E.13667
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X57.791 Y16.18 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 43/58
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
G1 X58.848 Y25.607
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1488
G1 X57.052 Y25.607 E.05957
G1 X57.052 Y23.02 E.0858
G1 X58.848 Y23.02 E.05957
G1 X58.848 Y25.547 E.0838
G1 X59.24 Y25.999 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1488
M204 S5000
G1 X56.66 Y25.999 E.07928
G1 X56.66 Y23.587 E.0741
G1 X56.66 Y23.187 E.01229
G1 X56.66 Y22.787 E.01229
G1 X56.66 Y22.628 E.00489
G1 X59.24 Y22.628 E.07928
G1 X59.24 Y22.787 E.00489
G1 X59.24 Y23.187 E.01229
G1 X59.24 Y23.587 E.01229
G1 X59.24 Y25.939 E.07226
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.985 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.413 Z9 F30000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1488
G1 X57.444 Y25.215 E.05538
G1 X58.456 Y25.215 E.03109
G1 X58.456 Y23.413 E.05538
G1 X57.504 Y23.413 E.02924
G1 X57.791 Y23.76 F30000
; LINE_WIDTH: 0.36025
G1 F1488
G1 X57.791 Y24.868 E.02865
G1 X58.109 Y24.868 E.00821
G1 X58.109 Y23.76 E.02865
G1 X57.851 Y23.76 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.76 E-.09779
G1 X58.109 Y24.868 E-.42099
G1 X57.791 Y24.868 E-.12059
G1 X57.791 Y24.55 E-.12063
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y19.18 Z9 F30000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1488
G1 X57.052 Y12.652 E.21653
G1 X58.848 Y12.652 E.05957
G1 X58.848 Y19.18 E.21653
G1 X57.112 Y19.18 E.05758
G1 X56.66 Y19.413 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1488
M204 S5000
G1 X56.66 Y12.26 E.21978
G1 X59.24 Y12.26 E.07928
G1 X59.24 Y18.613 E.1952
G1 X59.24 Y19.013 E.01229
G1 X59.24 Y19.413 E.01229
G1 X59.24 Y19.572 E.00489
G1 X56.66 Y19.572 E.07928
G1 X56.66 Y19.473 E.00304
; WIPE_START
G1 F3121.419
M204 S10000
G1 X56.66 Y17.473 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.787 Z9 F30000
G1 Z8.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1488
G1 X58.456 Y18.787 E.03109
G1 X58.456 Y13.044 E.17647
G1 X57.444 Y13.044 E.03109
G1 X57.444 Y18.727 E.17463
G1 X57.791 Y18.44 F30000
; LINE_WIDTH: 0.36025
G1 F1488
G1 X58.109 Y18.44 E.00821
G1 X58.109 Y13.391 E.13056
G1 X57.791 Y13.391 E.00821
G1 X57.791 Y18.38 E.129
; CHANGE_LAYER
; Z_HEIGHT: 8.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y16.38 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 44/58
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
G1 X58.848 Y25.508
G1 Z8.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1463
G1 X57.052 Y25.508 E.05957
M73 P92 R1
G1 X57.052 Y22.82 E.08916
G1 X58.848 Y22.82 E.05957
G1 X58.848 Y25.448 E.08717
G1 X59.24 Y25.9 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1463
M204 S5000
G1 X56.66 Y25.9 E.07928
G1 X56.66 Y23.387 E.07721
G1 X56.66 Y22.987 E.01229
G1 X56.66 Y22.587 E.01229
G1 X56.66 Y22.428 E.00489
G1 X59.24 Y22.428 E.07928
G1 X59.24 Y22.587 E.00489
G1 X59.24 Y22.987 E.01229
G1 X59.24 Y23.387 E.01229
G1 X59.24 Y25.84 E.07537
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.887 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.213 Z9.2 F30000
G1 Z8.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1463
G1 X57.444 Y25.116 E.05849
G1 X58.456 Y25.116 E.03109
G1 X58.456 Y23.213 E.05849
G1 X57.504 Y23.213 E.02924
G1 X57.791 Y23.56 F30000
; LINE_WIDTH: 0.36026
G1 F1463
G1 X57.791 Y24.769 E.03127
G1 X58.109 Y24.769 E.00821
G1 X58.109 Y23.56 E.03127
G1 X57.851 Y23.56 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.56 E-.09779
G1 X58.109 Y24.769 E-.4595
G1 X57.791 Y24.769 E-.12059
G1 X57.791 Y24.553 E-.08213
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y19.38 Z9.2 F30000
G1 Z8.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1463
G1 X57.052 Y13.149 E.20669
G1 X58.848 Y13.149 E.05957
G1 X58.848 Y19.38 E.20669
G1 X57.112 Y19.38 E.05758
G1 X56.66 Y19.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1463
M204 S5000
G1 X56.66 Y12.757 E.21066
G1 X59.24 Y12.757 E.07928
G1 X59.24 Y18.813 E.18608
G1 X59.24 Y19.213 E.01229
G1 X59.24 Y19.613 E.01229
G1 X59.24 Y19.772 E.00489
G1 X56.66 Y19.772 E.07928
G1 X56.66 Y19.673 E.00304
; WIPE_START
G1 F3121.525
M204 S10000
G1 X56.66 Y17.673 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y18.988 Z9.2 F30000
G1 Z8.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1463
G1 X58.456 Y18.988 E.03109
G1 X58.456 Y13.541 E.16736
G1 X57.444 Y13.541 E.03109
G1 X57.444 Y18.928 E.16551
G1 X57.791 Y18.64 F30000
; LINE_WIDTH: 0.36025
G1 F1463
G1 X58.109 Y18.64 E.00821
G1 X58.109 Y13.888 E.12289
G1 X57.791 Y13.888 E.00821
G1 X57.791 Y18.58 E.12133
; CHANGE_LAYER
; Z_HEIGHT: 9
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y16.58 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 45/58
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
G1 X58.848 Y25.401
G1 Z9
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1436
G1 X57.052 Y25.401 E.05957
G1 X57.052 Y22.62 E.09223
G1 X58.848 Y22.62 E.05957
G1 X58.848 Y25.341 E.09024
G1 X59.24 Y25.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1436
M204 S5000
G1 X56.66 Y25.793 E.07928
G1 X56.66 Y23.187 E.08006
G1 X56.66 Y22.787 E.01229
G1 X56.66 Y22.387 E.01229
G1 X56.66 Y22.228 E.00489
G1 X59.24 Y22.228 E.07928
G1 X59.24 Y22.387 E.00489
G1 X59.24 Y22.787 E.01229
G1 X59.24 Y23.187 E.01229
G1 X59.24 Y25.733 E.07822
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.779 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.013 Z9.4 F30000
G1 Z9
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1436
G1 X57.444 Y25.009 E.06134
G1 X58.456 Y25.009 E.03109
G1 X58.456 Y23.013 E.06134
G1 X57.504 Y23.013 E.02924
G1 X57.791 Y23.36 F30000
; LINE_WIDTH: 0.36025
G1 F1436
G1 X57.791 Y24.662 E.03366
G1 X58.109 Y24.662 E.00821
G1 X58.109 Y23.36 E.03366
G1 X57.851 Y23.36 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.36 E-.09779
G1 X58.109 Y24.662 E-.4947
G1 X57.791 Y24.662 E-.12059
G1 X57.791 Y24.538 E-.04693
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y19.58 Z9.4 F30000
G1 Z9
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1436
G1 X57.052 Y13.645 E.19685
G1 X58.848 Y13.645 E.05957
G1 X58.848 Y19.58 E.19685
G1 X57.112 Y19.58 E.05758
G1 X56.66 Y19.813 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1436
M204 S5000
G1 X56.66 Y13.253 E.20155
G1 X59.24 Y13.253 E.07928
G1 X59.24 Y19.013 E.17697
G1 X59.24 Y19.413 E.01229
G1 X59.24 Y19.813 E.01229
G1 X59.24 Y19.972 E.00489
G1 X56.66 Y19.972 E.07928
G1 X56.66 Y19.873 E.00304
; WIPE_START
G1 F3121.419
M204 S10000
G1 X56.66 Y17.873 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y19.188 Z9.4 F30000
G1 Z9
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1436
G1 X58.456 Y19.188 E.03109
G1 X58.456 Y14.037 E.15824
G1 X57.444 Y14.037 E.03109
G1 X57.444 Y19.128 E.1564
G1 X57.791 Y18.84 F30000
; LINE_WIDTH: 0.36025
G1 F1436
G1 X58.109 Y18.84 E.00821
G1 X58.109 Y14.385 E.11522
G1 X57.791 Y14.385 E.00821
G1 X57.791 Y18.78 E.11366
; CHANGE_LAYER
; Z_HEIGHT: 9.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y16.78 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 46/58
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
G1 X58.848 Y25.267
G1 Z9.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1406
G1 X57.052 Y25.267 E.05957
G1 X57.052 Y22.42 E.09443
G1 X58.848 Y22.42 E.05957
G1 X58.848 Y25.207 E.09244
G1 X59.24 Y25.659 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1406
M204 S5000
G1 X56.66 Y25.659 E.07928
G1 X56.66 Y22.987 E.0821
G1 X56.66 Y22.587 E.01229
G1 X56.66 Y22.187 E.01229
G1 X56.66 Y22.028 E.00489
G1 X59.24 Y22.028 E.07928
M73 P93 R1
G1 X59.24 Y22.187 E.00489
G1 X59.24 Y22.587 E.01229
G1 X59.24 Y22.987 E.01229
G1 X59.24 Y25.599 E.08026
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y22.813 Z9.6 F30000
G1 Z9.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1406
G1 X57.444 Y24.875 E.06338
G1 X58.456 Y24.875 E.03109
G1 X58.456 Y22.813 E.06338
G1 X57.504 Y22.813 E.02924
G1 X57.791 Y23.16 F30000
; LINE_WIDTH: 0.36026
G1 F1406
G1 X57.791 Y24.528 E.03538
G1 X58.109 Y24.528 E.00821
G1 X58.109 Y23.16 E.03538
G1 X57.851 Y23.16 E.00665
; WIPE_START
G1 F15000
G1 X58.109 Y23.16 E-.09779
G1 X58.109 Y24.528 E-.51991
G1 X57.791 Y24.528 E-.12059
G1 X57.791 Y24.471 E-.02172
; WIPE_END
G1 E-.04 F1800
G1 X57.052 Y19.78 Z9.6 F30000
G1 Z9.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1406
G1 X57.052 Y14.142 E.18701
G1 X58.848 Y14.142 E.05957
G1 X58.848 Y19.78 E.18701
G1 X57.112 Y19.78 E.05758
G1 X56.66 Y20.013 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1406
M204 S5000
G1 X56.66 Y13.75 E.19244
G1 X59.24 Y13.75 E.07928
G1 X59.24 Y19.213 E.16785
G1 X59.24 Y19.613 E.01229
G1 X59.24 Y20.013 E.01229
G1 X59.24 Y20.172 E.00488
G1 X56.66 Y20.172 E.07928
G1 X56.66 Y20.073 E.00304
; WIPE_START
G1 F3120.359
M204 S10000
G1 X56.66 Y18.073 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y19.387 Z9.6 F30000
G1 Z9.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1406
G1 X58.456 Y19.387 E.03109
G1 X58.456 Y14.534 E.14913
G1 X57.444 Y14.534 E.03109
G1 X57.444 Y19.327 E.14728
G1 X57.791 Y19.04 F30000
; LINE_WIDTH: 0.36025
G1 F1406
G1 X58.109 Y19.04 E.00821
G1 X58.109 Y14.881 E.10754
G1 X57.791 Y14.881 E.00821
G1 X57.791 Y18.98 E.10599
; CHANGE_LAYER
; Z_HEIGHT: 9.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y16.98 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 47/58
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
G1 X58.848 Y25.134
G1 Z9.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1273
G1 X57.052 Y25.134 E.05957
G1 X57.052 Y23.201 E.06411
G1 X57.052 Y22.801 E.01327
G1 X57.052 Y22.401 E.01327
G1 X57.052 Y22.001 E.01327
G1 X57.052 Y21.618 E.01269
; FEATURE: Overhang wall
G1 F3000
M204 S5000
G1 X57.052 Y20.582 E.03439
; FEATURE: Inner wall
G1 F1273
M204 S10000
G1 X57.052 Y20.199 E.01269
G1 X57.052 Y19.799 E.01327
G1 X57.052 Y19.399 E.01327
G1 X57.052 Y18.999 E.01327
G1 X57.052 Y14.639 E.14464
G1 X58.848 Y14.639 E.05957
G1 X58.848 Y18.999 E.14464
G1 X58.848 Y19.399 E.01327
G1 X58.848 Y19.799 E.01327
G1 X58.848 Y20.199 E.01327
G1 X58.848 Y20.582 E.01269
; FEATURE: Overhang wall
G1 F3000
M204 S5000
G1 X58.848 Y21.618 E.03439
; FEATURE: Inner wall
G1 F1273
M204 S10000
G1 X58.848 Y22.001 E.01269
G1 X58.848 Y22.401 E.01327
G1 X58.848 Y22.801 E.01327
G1 X58.848 Y23.201 E.01327
G1 X58.848 Y25.074 E.06212
G1 X59.24 Y25.526 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1273
M204 S5000
G1 X56.66 Y25.526 E.07928
G1 X56.66 Y22.787 E.08414
G1 X56.66 Y22.387 E.01229
G1 X56.66 Y21.987 E.01229
G1 X56.66 Y21.618 E.01134
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
G1 F3000
G1 X56.66 Y20.582 E.03439
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1273
G1 X56.66 Y20.213 E.01134
G1 X56.66 Y19.813 E.01229
G1 X56.66 Y19.413 E.01229
G1 X56.66 Y14.247 E.15874
G1 X59.24 Y14.247 E.07928
G1 X59.24 Y19.413 E.15874
G1 X59.24 Y19.813 E.01229
G1 X59.24 Y20.213 E.01229
G1 X59.24 Y20.582 E.01134
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
G1 F3000
G1 X59.24 Y21.618 E.03439
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1273
G1 X59.24 Y21.987 E.01134
G1 X59.24 Y22.387 E.01229
G1 X59.24 Y22.787 E.01229
G1 X59.24 Y25.466 E.08229
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.512 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X58.328 Y23.205 Z9.8 F30000
G1 Z9.4
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.4954
G1 F3000
G1 X58.328 Y19.164 E.149
G1 X57.876 Y19.164 E.01668
G1 X57.876 Y23.036 E.14274
G1 X57.423 Y23.036 E.01668
G1 X57.423 Y18.995 E.149
G1 X57.444 Y18.787 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
M73 P93 R0
G1 F1273
G1 X58.456 Y18.787 E.03109
G1 X58.456 Y15.031 E.11543
G1 X57.444 Y15.031 E.03109
G1 X57.444 Y18.727 E.11358
G1 X57.791 Y18.44 F30000
; LINE_WIDTH: 0.36026
G1 F1273
G1 X58.109 Y18.44 E.00821
G1 X58.109 Y15.378 E.07918
G1 X57.791 Y15.378 E.00821
G1 X57.791 Y18.38 E.07763
; WIPE_START
G1 F15000
G1 X57.791 Y16.38 E-.76
; WIPE_END
G1 E-.04 F1800
G17
G3 Z9.8 I-1.215 J-.06 P1  F30000
G1 X57.444 Y23.413 Z9.8
G1 Z9.4
G1 E.8 F1800
; LINE_WIDTH: 0.41999
G1 F1273
G1 X57.444 Y24.741 E.04083
G1 X58.456 Y24.741 E.03109
G1 X58.456 Y23.413 E.04083
G1 X57.504 Y23.413 E.02924
G1 X57.791 Y23.76 F30000
; LINE_WIDTH: 0.36025
G1 F1273
G1 X57.791 Y24.394 E.0164
G1 X58.109 Y24.394 E.00821
G1 X58.109 Y23.76 E.0164
G1 X57.851 Y23.76 E.00665
; CHANGE_LAYER
; Z_HEIGHT: 9.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X58.109 Y23.76 E-.1061
G1 X58.109 Y24.394 E-.26153
G1 X57.791 Y24.394 E-.13083
G1 X57.791 Y23.76 E-.26153
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 48/58
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
G1 X58.848 Y24.994
G1 Z9.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1372
G1 X57.052 Y24.994 E.05957
G1 X57.052 Y15.135 E.32702
G1 X58.848 Y15.135 E.05957
G1 X58.848 Y24.934 E.32503
G1 X59.24 Y25.386 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1372
M204 S5000
M73 P94 R0
G1 X56.66 Y25.386 E.07928
G1 X56.66 Y14.743 E.32701
G1 X59.24 Y14.743 E.07928
G1 X59.24 Y25.326 E.32517
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.602 Z10 F30000
G1 Z9.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1372
G1 X58.456 Y24.602 E.03109
G1 X58.456 Y15.527 E.27882
G1 X57.444 Y15.527 E.03109
G1 X57.444 Y24.542 E.27697
G1 X57.791 Y24.254 F30000
; LINE_WIDTH: 0.36025
G1 F1372
G1 X58.109 Y24.254 E.00821
G1 X58.109 Y15.875 E.21669
G1 X57.791 Y15.875 E.00821
G1 X57.791 Y24.194 E.21514
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y22.194 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 49/58
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
G1 X58.848 Y24.818
G1 Z9.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1290
G1 X57.052 Y24.818 E.05957
G1 X57.052 Y15.632 E.30473
G1 X58.848 Y15.632 E.05957
G1 X58.848 Y24.758 E.30274
G1 X59.24 Y25.21 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1290
M204 S5000
G1 X56.66 Y25.21 E.07928
G1 X56.66 Y15.24 E.30636
G1 X59.24 Y15.24 E.07928
G1 X59.24 Y25.15 E.30452
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.197 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.426 Z10.2 F30000
G1 Z9.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1290
G1 X58.456 Y24.426 E.03109
G1 X58.456 Y16.024 E.25817
G1 X57.444 Y16.024 E.03109
G1 X57.444 Y24.366 E.25633
G1 X57.791 Y24.079 F30000
; LINE_WIDTH: 0.36025
G1 F1290
G1 X58.109 Y24.079 E.00821
G1 X58.109 Y16.371 E.19931
G1 X57.791 Y16.371 E.00821
G1 X57.791 Y24.019 E.19776
; CHANGE_LAYER
; Z_HEIGHT: 10
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y22.019 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 50/58
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
G1 X58.848 Y24.643
G1 Z10
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1206
G1 X57.052 Y24.643 E.05957
G1 X57.052 Y16.129 E.28244
G1 X58.848 Y16.129 E.05957
G1 X58.848 Y24.583 E.28045
G1 X59.24 Y25.035 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1206
M204 S5000
G1 X56.66 Y25.035 E.07928
G1 X56.66 Y15.736 E.28572
G1 X59.24 Y15.736 E.07928
G1 X59.24 Y24.975 E.28387
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y25.021 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.251 Z10.4 F30000
G1 Z10
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1206
G1 X58.456 Y24.251 E.03109
G1 X58.456 Y16.521 E.23752
G1 X57.444 Y16.521 E.03109
G1 X57.444 Y24.191 E.23568
G1 X57.791 Y23.904 F30000
; LINE_WIDTH: 0.36025
G1 F1206
G1 X58.109 Y23.904 E.00821
G1 X58.109 Y16.868 E.18193
G1 X57.791 Y16.868 E.00821
G1 X57.791 Y23.844 E.18038
; CHANGE_LAYER
; Z_HEIGHT: 10.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y21.844 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 51/58
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
G1 X58.848 Y24.449
G1 Z10.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y24.449 E.05957
G1 X57.052 Y16.625 E.25954
G1 X58.848 Y16.625 E.05957
G1 X58.848 Y24.389 E.25755
G1 X59.24 Y24.841 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y24.841 E.07928
G1 X56.66 Y16.233 E.2645
G1 X59.24 Y16.233 E.07928
G1 X59.24 Y24.781 E.26266
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y24.828 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y24.057 Z10.6 F30000
G1 Z10.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y24.057 E.03109
G1 X58.456 Y17.017 E.21631
G1 X57.444 Y17.017 E.03109
G1 X57.444 Y23.997 E.21447
G1 X57.791 Y23.71 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y23.71 E.00821
G1 X58.109 Y17.364 E.16408
G1 X57.791 Y17.364 E.00821
G1 X57.791 Y23.65 E.16253
; CHANGE_LAYER
; Z_HEIGHT: 10.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y21.65 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 52/58
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
G1 X58.848 Y24.221
G1 Z10.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y24.221 E.05957
G1 X57.052 Y17.122 E.2355
M73 P95 R0
G1 X58.848 Y17.122 E.05957
G1 X58.848 Y24.161 E.23351
G1 X59.24 Y24.613 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y24.613 E.07928
G1 X56.66 Y16.73 E.24224
G1 X59.24 Y16.73 E.07928
G1 X59.24 Y24.553 E.24039
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y24.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.829 Z10.8 F30000
G1 Z10.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y23.829 E.03109
G1 X58.456 Y17.514 E.19404
G1 X57.444 Y17.514 E.03109
G1 X57.444 Y23.769 E.1922
G1 X57.791 Y23.482 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y23.482 E.00821
G1 X58.109 Y17.861 E.14534
G1 X57.791 Y17.861 E.00821
G1 X57.791 Y23.422 E.14379
; CHANGE_LAYER
; Z_HEIGHT: 10.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X57.791 Y21.422 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 53/58
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
G1 X58.848 Y23.993
G1 Z10.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y23.993 E.05957
G1 X57.052 Y17.618 E.21146
G1 X58.848 Y17.618 E.05957
G1 X58.848 Y23.933 E.20947
G1 X59.24 Y24.385 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y24.385 E.07928
G1 X56.66 Y17.226 E.21997
G1 X59.24 Y17.226 E.07928
G1 X59.24 Y24.325 E.21812
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y24.372 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.601 Z11 F30000
G1 Z10.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y23.601 E.03109
G1 X58.456 Y18.01 E.17178
G1 X57.444 Y18.01 E.03109
G1 X57.444 Y23.541 E.16993
G1 X57.791 Y23.254 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y23.254 E.00821
G1 X58.109 Y18.358 E.1266
G1 X57.791 Y18.358 E.00821
G1 X57.791 Y23.194 E.12505
; CHANGE_LAYER
; Z_HEIGHT: 10.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y21.194 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 54/58
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
G1 X58.848 Y23.702
G1 Z10.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y23.702 E.05957
G1 X57.052 Y18.115 E.18532
G1 X58.848 Y18.115 E.05957
G1 X58.848 Y23.642 E.18333
G1 X59.24 Y24.094 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y24.094 E.07928
G1 X56.66 Y17.723 E.19575
G1 X59.24 Y17.723 E.07928
G1 X59.24 Y24.034 E.19391
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y24.08 E-.76
; WIPE_END
G1 E-.04 F1800
M73 P96 R0
G1 X57.444 Y23.31 Z11.2 F30000
G1 Z10.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y23.31 E.03109
G1 X58.456 Y18.507 E.14756
G1 X57.444 Y18.507 E.03109
G1 X57.444 Y23.25 E.14572
G1 X57.791 Y22.962 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y22.962 E.00821
G1 X58.109 Y18.854 E.10623
G1 X57.791 Y18.854 E.00821
G1 X57.791 Y22.902 E.10467
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y20.902 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 55/58
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
G1 X58.848 Y23.402
G1 Z11
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y23.402 E.05957
G1 X57.052 Y18.612 E.15891
G1 X58.848 Y18.612 E.05957
G1 X58.848 Y23.342 E.15692
G1 X59.24 Y23.794 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y23.794 E.07928
G1 X56.66 Y18.22 E.1713
G1 X59.24 Y18.22 E.07928
G1 X59.24 Y23.734 E.16945
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y23.781 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y23.01 Z11.4 F30000
G1 Z11
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y23.01 E.03109
G1 X58.456 Y19.004 E.1231
G1 X57.444 Y19.004 E.03109
G1 X57.444 Y22.95 E.12126
G1 X57.791 Y22.663 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y22.663 E.00821
G1 X58.109 Y19.351 E.08564
G1 X57.791 Y19.351 E.00821
G1 X57.791 Y22.603 E.08409
; CHANGE_LAYER
; Z_HEIGHT: 11.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y20.603 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 56/58
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
G1 X58.848 Y23.016
G1 Z11.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y23.016 E.05957
G1 X57.052 Y19.108 E.12963
G1 X58.848 Y19.108 E.05957
G1 X58.848 Y22.956 E.12764
G1 X59.24 Y23.408 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y23.408 E.07928
G1 X56.66 Y18.716 E.14417
G1 X59.24 Y18.716 E.07928
G1 X59.24 Y23.348 E.14232
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y23.395 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y22.624 Z11.6 F30000
G1 Z11.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y22.624 E.03109
G1 X58.456 Y19.5 E.09598
G1 X57.444 Y19.5 E.03109
G1 X57.444 Y22.564 E.09413
G1 X57.791 Y22.277 F30000
; LINE_WIDTH: 0.36025
G1 F1200
G1 X58.109 Y22.277 E.00821
G1 X58.109 Y19.848 E.06281
G1 X57.791 Y19.848 E.00821
G1 X57.791 Y22.217 E.06126
; CHANGE_LAYER
; Z_HEIGHT: 11.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X57.791 Y20.217 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 57/58
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
G1 X58.848 Y22.579
G1 Z11.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X57.052 Y22.579 E.05957
G1 X57.052 Y19.621 E.09815
G1 X58.848 Y19.621 E.05957
G1 X58.848 Y22.519 E.09616
M73 P97 R0
G1 X59.24 Y22.971 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y22.971 E.07928
G1 X56.66 Y19.229 E.11501
G1 X59.24 Y19.229 E.07928
G1 X59.24 Y22.911 E.11317
; WIPE_START
G1 F12000
M204 S10000
G1 X57.241 Y22.958 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X57.444 Y22.187 Z11.8 F30000
G1 Z11.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F1200
G1 X58.456 Y22.187 E.03109
G1 X58.456 Y20.013 E.06682
G1 X57.444 Y20.013 E.03109
G1 X57.444 Y22.127 E.06498
G1 X57.791 Y21.84 F30000
; LINE_WIDTH: 0.36026
G1 F1200
G1 X58.109 Y21.84 E.00821
G1 X58.109 Y20.36 E.03828
G1 X57.791 Y20.36 E.00821
G1 X57.791 Y21.78 E.03673
; CHANGE_LAYER
; Z_HEIGHT: 11.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X57.791 Y20.36 E-.53969
G1 X58.109 Y20.36 E-.12059
G1 X58.109 Y20.622 E-.09972
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 58/58
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
G1 X59.24 Y22.382
G1 Z11.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X56.66 Y22.382 E.07928
G1 X56.66 Y19.818 E.07881
G1 X59.24 Y19.818 E.07928
G1 X59.24 Y22.322 E.07696
M204 S10000
G1 X58.564 Y22.175 F30000
; FEATURE: Top surface
G1 F1200
M204 S2000
G1 X59.033 Y21.706 E.02037
G1 X59.033 Y21.173
G1 X58.031 Y22.175 E.04354
G1 X57.497 Y22.175
G1 X59.033 Y20.64 E.06672
G1 X59.033 Y20.106
G1 X56.964 Y22.175 E.08989
G1 X56.867 Y21.738
G1 X58.581 Y20.025 E.07446
G1 X58.048 Y20.025
G1 X56.867 Y21.205 E.05128
G1 X56.867 Y20.672
G1 X57.514 Y20.025 E.02811
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F12000
M204 S10000
G1 X56.867 Y20.672 E-.34766
G1 X56.867 Y21.205 E-.20264
G1 X57.258 Y20.815 E-.2097
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
G1 Z12.1 F900 ; lower z a little
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

    G1 Z111.6 F600
    G1 Z109.6

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

