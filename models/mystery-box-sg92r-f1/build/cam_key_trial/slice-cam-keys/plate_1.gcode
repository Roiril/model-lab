; HEADER_BLOCK_START
; BambuStudio 02.03.01.51
; model printing time: 2m 4s; total estimated time: 9m 19s
; total layer number: 20
; total filament length [mm] : 206.30
; total filament volume [cm^3] : 496.20
; total filament weight [g] : 0.63
; model label id: 8,12
; filament_density: 1.26
; filament_diameter: 1.75
; max_z_height: 4.00
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
M73 P0 R9
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
M73 P1 R9
    G1 Y265
    M400
M621 S0A
M620.1 E F523.843 T240

M412 S1 ; ===turn on filament runout detection===

M109 S250 ;set nozzle to common flush temp
M106 P1 S0
G92 E0
M73 P6 R8
G1 E50 F200
M400
M104 S220
G92 E0
M73 P52 R4
G1 E50 F200
M400
M106 P1 S255
G92 E0
M73 P53 R4
G1 E5 F300
M109 S200 ; drop nozzle temp, make filament shink a bit
G92 E0
M73 P55 R4
G1 E-0.5 F300

M73 P58 R3
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
M73 P59 R3
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
M73 P60 R3
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
    G29 A X20 Y6 I30.9 J5
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

M73 P61 R3
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
M73 P62 R3
    G1 X65.000 E1.24726 F1508.32
    G1 X70.000 E0.31181 F1508.32
    G1 X75.000 E0.31181 F6033.27
    G1 X80.000 E0.31181 F1508.32
    G1 X85.000 E0.31181 F6033.27
    G1 X90.000 E0.31181 F1508.32
M73 P63 R3
    G1 X95.000 E0.31181 F6033.27
    G1 X100.000 E0.31181 F1508.32
    G1 X105.000 E0.31181 F6033.27
    G1 X110.000 E0.31181 F1508.32
    G1 X115.000 E0.31181 F6033.27
    G1 X120.000 E0.31181 F1508.32
    G1 X125.000 E0.31181 F6033.27
    G1 X130.000 E0.31181 F1508.32
    G1 X135.000 E0.31181 F6033.27
M73 P64 R3
    G1 X140.000 E0.31181 F1508.32
    G1 X145.000 E0.31181 F6033.27
    G1 X150.000 E0.31181 F1508.32
    G1 X155.000 E0.31181 F6033.27
M73 P65 R3
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
M73 P66 R3
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
M73 P67 R3
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
M73 P68 R2
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
M73 P69 R2
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
; layer num/total_layer_count: 1/20
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
M204 S6000
G1 Z.4 F30000
; object ids of layer 1 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer1 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X39.793 Y8.143
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F2205
M204 S500
M73 P70 R2
G1 X39.307 Y8.143 E.0181
G1 X39.307 Y4.857 E.12239
G1 X39.793 Y4.857 E.0181
G1 X39.793 Y5.858 E.03727
G1 X42.126 Y5.855 E.08692
G2 X42.126 Y7.145 I13.867 J.645 E.04803
G1 X39.793 Y7.142 E.08692
G1 X39.793 Y8.083 E.03504
M204 S6000
G1 X40.25 Y8.6 F30000
; FEATURE: Outer wall
G1 F2205
M204 S500
G1 X38.85 Y8.6 E.05215
G1 X38.85 Y4.4 E.15643
G1 X40.25 Y4.4 E.05215
G1 X40.25 Y5.4 E.03726
G3 X49.662 Y5.371 I7.789 J1007.961 E.35055
G1 X49.675 Y5.048 E.01206
G2 X50.1 Y5.049 I.252 J-12.083 E.01584
G1 X50.1 Y5.4 E.01306
G1 X50.5 Y5.4 E.0149
G1 X50.5 Y5.801 E.01494
G3 X42.584 Y5.829 I-5.342 J-400.159 E.29484
G2 X42.584 Y7.171 I14.452 J.671 E.05004
G3 X49.404 Y7.174 I3.164 J681.83 E.25402
G2 X50.5 Y7.199 I1.282 J-32.277 E.04082
G1 X50.5 Y7.6 E.01494
G1 X50.1 Y7.6 E.0149
G1 X50.1 Y7.951 E.01306
G2 X49.675 Y7.952 I-.173 J12.084 E.01584
G1 X49.662 Y7.629 E.01206
G1 X43.058 Y7.629 E.24596
G2 X40.25 Y7.6 I-1.898 J48.219 E.1046
G1 X40.25 Y8.54 E.03502
; WIPE_START
M73 P71 R2
G1 F3000
G1 X38.85 Y8.6 E-.53249
G1 X38.85 Y8.001 E-.22751
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X40.948 Y6.039 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.53251
G1 F2205
M204 S500
M73 P72 R2
G1 X41.664 Y6.756 E.0404
G1 X40.971 Y6.755 E.02765
G1 X40.462 Y6.246 E.02873
G1 X39.77 Y6.246 E.0276
G1 X40.484 Y6.96 E.04027
; OBJECT_ID: 8
; WIPE_START
M73 P76 R2
G1 F6300
G1 X39.77 Y6.246 E-.3836
G1 X40.462 Y6.246 E-.26285
G1 X40.673 Y6.457 E-.11355
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
M204 S6000
G1 X33.069 Y7.12 Z.6 F30000
G1 X21.343 Y8.143 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F2205
M204 S500
G1 X20.857 Y8.143 E.0181
G1 X20.857 Y4.857 E.12239
G1 X21.343 Y4.857 E.0181
G1 X21.343 Y5.858 E.03727
G1 X23.676 Y5.855 E.08692
G2 X23.676 Y7.145 I13.867 J.645 E.04803
G1 X21.343 Y7.142 E.08692
G1 X21.343 Y8.083 E.03504
M204 S6000
G1 X21.8 Y8.6 F30000
; FEATURE: Outer wall
G1 F2205
M204 S500
G1 X20.4 Y8.6 E.05215
G1 X20.4 Y4.4 E.15643
G1 X21.8 Y4.4 E.05215
G1 X21.8 Y5.4 E.03726
G3 X31.212 Y5.371 I7.789 J1007.961 E.35055
G1 X31.225 Y5.048 E.01206
G2 X31.65 Y5.049 I.252 J-12.083 E.01584
G1 X31.65 Y5.4 E.01306
G1 X32.05 Y5.4 E.0149
G1 X32.05 Y5.801 E.01494
G3 X24.134 Y5.829 I-5.342 J-400.159 E.29484
G2 X24.134 Y7.171 I14.452 J.671 E.05004
G3 X30.954 Y7.174 I3.164 J681.83 E.25402
G2 X32.05 Y7.199 I1.282 J-32.277 E.04082
G1 X32.05 Y7.6 E.01494
M73 P77 R2
G1 X31.65 Y7.6 E.0149
G1 X31.65 Y7.951 E.01306
G2 X31.225 Y7.952 I-.173 J12.084 E.01584
G1 X31.212 Y7.629 E.01206
G1 X24.608 Y7.629 E.24596
G2 X21.8 Y7.6 I-1.898 J48.219 E.1046
G1 X21.8 Y8.54 E.03502
; WIPE_START
G1 F3000
G1 X20.4 Y8.6 E-.53249
G1 X20.4 Y8.001 E-.22751
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X22.498 Y6.039 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.53251
G1 F2205
M204 S500
G1 X23.214 Y6.756 E.0404
G1 X22.521 Y6.755 E.02765
G1 X22.012 Y6.246 E.02873
G1 X21.32 Y6.246 E.0276
G1 X22.034 Y6.96 E.04027
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6300
G1 X21.32 Y6.246 E-.3836
G1 X22.012 Y6.246 E-.26285
G1 X22.223 Y6.457 E-.11355
; WIPE_END
G1 E-.03999 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 2/20
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
; object ids of layer 2 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer2 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z.4
M73 P78 R2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3454
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3454
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3454
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3454
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F3454
M73 P78 R1
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3454
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3454
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3454
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
M73 P79 R1
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3454
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3454
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z.8 F30000
G1 X21.598 Y8.398 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3454
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3454
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3454
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3454
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F3454
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3454
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3454
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3454
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3454
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3454
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 3/20
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
G17
G3 Z.8 I1.217 J0 P1  F30000
; object ids of layer 3 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer3 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
M73 P80 R1
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z1 F30000
G1 X21.598 Y8.398 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 4/20
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
G17
G3 Z1 I1.217 J0 P1  F30000
; object ids of layer 4 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer4 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
M73 P81 R1
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z1.2 F30000
G1 X21.598 Y8.398 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 5/20
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
G17
G3 Z1.2 I1.217 J0 P1  F30000
; object ids of layer 5 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer5 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
M73 P82 R1
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z1.4 F30000
G1 X21.598 Y8.398 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 6/20
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
G17
G3 Z1.4 I1.217 J0 P1  F30000
; object ids of layer 6 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer6 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
M73 P83 R1
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z1.6 F30000
G1 X21.598 Y8.398 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 7/20
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
G17
G3 Z1.6 I1.217 J0 P1  F30000
; object ids of layer 7 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer7 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
M73 P84 R1
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z1.8 F30000
G1 X21.598 Y8.398 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 8/20
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
G17
G3 Z1.8 I1.217 J0 P1  F30000
; object ids of layer 8 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer8 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z2 F30000
G1 Z1.6
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
M73 P85 R1
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z2 F30000
G1 X21.598 Y8.398 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z2 F30000
G1 Z1.6
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 9/20
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
G17
G3 Z2 I1.217 J0 P1  F30000
; object ids of layer 9 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer9 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
M73 P86 R1
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z2.2 F30000
G1 X21.598 Y8.398 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 10/20
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
G17
G3 Z2.2 I1.217 J0 P1  F30000
; object ids of layer 10 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer10 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
M73 P87 R1
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z2.4 F30000
G1 X21.598 Y8.398 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 11/20
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
G17
G3 Z2.4 I1.217 J0 P1  F30000
; object ids of layer 11 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer11 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
M73 P88 R1
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z2.6 F30000
G1 X21.598 Y8.398 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z2.6 F30000
G1 Z2.2
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 12/20
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
G17
G3 Z2.6 I1.217 J0 P1  F30000
; object ids of layer 12 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer12 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
M73 P89 R1
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z2.8 F30000
G1 X21.598 Y8.398 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
M73 P89 R0
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z2.8 F30000
G1 Z2.4
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 13/20
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
G17
G3 Z2.8 I1.217 J0 P1  F30000
; object ids of layer 13 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer13 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z3 F30000
G1 Z2.6
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
M73 P90 R0
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z3 F30000
G1 X21.598 Y8.398 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z3 F30000
G1 Z2.6
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z3 F30000
G1 Z2.6
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 14/20
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
G17
G3 Z3 I1.217 J0 P1  F30000
; object ids of layer 14 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer14 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y5.602 E.03317
G1 X42.348 Y5.602 E.0763
G1 X42.348 Y7.398 E.05957
G1 X40.048 Y7.398 E.0763
G1 X40.048 Y8.338 E.03118
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X42.544 Y7.4 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X49.706 Y7.4 E.2266
G1 X49.803 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X49.9 Y7.448 E.00375
G1 X49.9 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X49.9 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X49.9 Y7.448 E.00529
G1 X49.997 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X50.094 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X50.494 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X50.094 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X50.494 Y5.6 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
G1 F3388
G1 X50.094 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X49.997 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X49.9 Y5.552 E.00364
G1 X49.9 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X49.9 Y5.056 E.01106
G1 X49.9 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X49.803 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X49.706 Y5.6 E.00316
G1 X42.544 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X44.544 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y5.1 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y5.797 E.03344
G1 X41.956 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X41.956 Y5.994 E.01554
G1 X39.844 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X39.786 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X39.728 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X39.669 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X39.611 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X39.552 Y5.857 E.00301
G1 X39.531 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X39.509 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X39.487 Y6.179 E.00434
; LINE_WIDTH: 0.484853
M73 P91 R0
G1 X39.466 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X39.444 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X39.465 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X39.486 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X39.508 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X39.529 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X39.55 Y7.194 E.00553
G1 X39.609 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X39.668 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X39.727 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X39.786 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X39.844 Y7.006 E.00215
G1 X41.956 Y7.006 E.06497
G1 X41.956 Y6.56 E.01372
G1 X41.609 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X41.609 Y6.341 E.0041
G1 X39.844 Y6.341 E.04562
G1 X39.791 Y6.297 E.00179
G1 X39.791 Y6.712 E.01073
G1 X39.844 Y6.659 E.00194
G1 X41.609 Y6.659 E.04562
G1 X41.609 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X41.609 Y6.659 E-.03749
G1 X39.844 Y6.659 E-.67042
G1 X39.791 Y6.712 E-.02852
G1 X39.791 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y7.9 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X39.55 Y7.254 E.03098
; OBJECT_ID: 8
; WIPE_START
G1 F10699.365
G1 X39.55 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.92 Y8.112 Z3.2 F30000
G1 X21.598 Y8.398 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3388
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y5.602 E.03317
G1 X23.898 Y5.602 E.0763
G1 X23.898 Y7.398 E.05957
G1 X21.598 Y7.398 E.0763
G1 X21.598 Y8.338 E.03118
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3388
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X24.094 Y7.4 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.431194
G1 F3388
G1 X31.256 Y7.4 E.2266
G1 X31.353 Y7.424 E.00316
; LINE_WIDTH: 0.503601
G1 X31.45 Y7.448 E.00375
G1 X31.45 Y7.944 F30000
; LINE_WIDTH: 0.43086
G1 F3388
G1 X31.45 Y7.594 E.01106
; LINE_WIDTH: 0.489227
G1 X31.45 Y7.448 E.00529
G1 X31.547 Y7.424 E.00364
; LINE_WIDTH: 0.455105
G1 X31.644 Y7.4 E.00336
; LINE_WIDTH: 0.43086
G1 X32.044 Y7.4 E.01264
; WIPE_START
G1 F15000
G1 X31.644 Y7.4 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X32.044 Y5.6 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
G1 F3388
G1 X31.644 Y5.6 E.01264
; LINE_WIDTH: 0.455107
G1 X31.547 Y5.576 E.00336
; LINE_WIDTH: 0.48923
G1 X31.45 Y5.552 E.00364
G1 X31.45 Y5.406 E.00529
; LINE_WIDTH: 0.43086
G1 X31.45 Y5.056 E.01106
G1 X31.45 Y5.552 F30000
; LINE_WIDTH: 0.503595
G1 F3388
G1 X31.353 Y5.576 E.00375
; LINE_WIDTH: 0.431194
G1 X31.256 Y5.6 E.00316
G1 X24.094 Y5.6 E.2266
; WIPE_START
G1 F15000
G1 X26.094 Y5.6 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y5.1 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y5.797 E.03344
G1 X23.506 Y6.5 F30000
; LINE_WIDTH: 0.41999
G1 F3388
G1 X23.506 Y5.994 E.01554
G1 X21.394 Y5.994 E.06488
; LINE_WIDTH: 0.441611
G1 X21.336 Y5.967 E.0021
; LINE_WIDTH: 0.484853
G1 X21.278 Y5.939 E.00233
; LINE_WIDTH: 0.528095
G1 X21.219 Y5.912 E.00255
; LINE_WIDTH: 0.571337
G1 X21.161 Y5.884 E.00278
; LINE_WIDTH: 0.614579
G1 X21.102 Y5.857 E.00301
G1 X21.081 Y5.964 E.00511
; LINE_WIDTH: 0.571337
G1 X21.059 Y6.072 E.00472
; LINE_WIDTH: 0.528095
G1 X21.037 Y6.179 E.00434
; LINE_WIDTH: 0.484853
G1 X21.016 Y6.287 E.00395
; LINE_WIDTH: 0.42738
G2 X20.994 Y6.606 I.782 J.213 E.01007
; LINE_WIDTH: 0.441165
G1 X21.015 Y6.723 E.00388
; LINE_WIDTH: 0.483515
G1 X21.036 Y6.841 E.0043
; LINE_WIDTH: 0.525865
G1 X21.058 Y6.959 E.00471
; LINE_WIDTH: 0.568215
G1 X21.079 Y7.077 E.00512
; LINE_WIDTH: 0.610565
G1 X21.1 Y7.194 E.00553
G1 X21.159 Y7.157 E.00323
; LINE_WIDTH: 0.568215
G1 X21.218 Y7.119 E.00299
; LINE_WIDTH: 0.525865
G1 X21.277 Y7.081 E.00275
; LINE_WIDTH: 0.483515
G1 X21.336 Y7.044 E.00251
; LINE_WIDTH: 0.420554
G1 X21.394 Y7.006 E.00215
G1 X23.506 Y7.006 E.06497
G1 X23.506 Y6.56 E.01372
G1 X23.159 Y6.5 F30000
; LINE_WIDTH: 0.36026
G1 F3388
G1 X23.159 Y6.341 E.0041
G1 X21.394 Y6.341 E.04562
G1 X21.341 Y6.297 E.00179
G1 X21.341 Y6.712 E.01073
G1 X21.394 Y6.659 E.00194
G1 X23.159 Y6.659 E.04562
G1 X23.159 Y6.56 E.00255
; WIPE_START
G1 F15000
G1 X23.159 Y6.659 E-.03749
G1 X21.394 Y6.659 E-.67042
G1 X21.341 Y6.712 E-.02852
G1 X21.341 Y6.65 E-.02357
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y7.9 Z3.2 F30000
G1 Z2.8
G1 E.8 F1800
; LINE_WIDTH: 0.63174
G1 F3388
G1 X21.1 Y7.254 E.03098
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.365
G1 X21.1 Y7.9 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 15/20
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
G17
G3 Z3.2 I1.217 J0 P1  F30000
; object ids of layer 15 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer15 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X39.572 Y8.398
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4737
G1 X39.052 Y8.398 E.01725
G1 X39.052 Y4.602 E.12592
G1 X39.572 Y4.602 E.01725
G1 X39.572 Y8.338 E.12393
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4737
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y5.21 E.03073
G1 X49.51 Y5.21 E.2787
G1 X49.51 Y4.86 E.01075
G1 X50.29 Y4.86 E.02397
G1 X50.29 Y5.21 E.01075
G1 X50.69 Y5.21 E.01229
G1 X50.69 Y5.99 E.02397
G1 X42.74 Y5.99 E.24428
G1 X42.74 Y7.01 E.03134
G1 X50.69 Y7.01 E.24428
G1 X50.69 Y7.79 E.02397
G1 X50.29 Y7.79 E.01229
G1 X50.29 Y8.14 E.01075
G1 X49.51 Y8.14 E.02397
G1 X49.51 Y7.79 E.01075
G1 X40.44 Y7.79 E.2787
G1 X40.44 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X39.312 Y8.194 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.15602
G1 F4737
G1 X39.312 Y4.806 E.03123
; WIPE_START
G1 F15000
G1 X39.312 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X46.91 Y6.084 Z3.4 F30000
G1 X50.09 Y5.783 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F4737
M204 S2000
G1 X49.717 Y5.41 E.01619
G1 X49.192 Y5.417
G1 X49.557 Y5.783 E.01587
G1 X49.023 Y5.783
G1 X48.658 Y5.417 E.01587
G1 X48.125 Y5.417
G1 X48.49 Y5.783 E.01587
G1 X47.957 Y5.783
G1 X47.592 Y5.417 E.01587
G1 X47.058 Y5.417
G1 X47.424 Y5.783 E.01587
G1 X46.89 Y5.783
G1 X46.525 Y5.417 E.01587
G1 X45.992 Y5.417
G1 X46.357 Y5.783 E.01587
G1 X45.824 Y5.783
G1 X45.459 Y5.417 E.01587
G1 X44.925 Y5.417
G1 X45.291 Y5.783 E.01587
G1 X44.757 Y5.783
G1 X44.392 Y5.417 E.01587
G1 X43.859 Y5.417
G1 X44.224 Y5.783 E.01587
G1 X43.691 Y5.783
G1 X43.326 Y5.417 E.01587
G1 X42.792 Y5.417
G1 X43.158 Y5.783 E.01587
G1 X42.624 Y5.783
G1 X42.259 Y5.417 E.01587
G1 X41.726 Y5.417
G1 X42.533 Y6.224 E.03505
G1 X42.533 Y6.757
G1 X41.193 Y5.417 E.05823
G1 X40.233 Y4.991
G1 X39.795 Y4.553 E.01903
; WIPE_START
G1 F12000
M204 S10000
G1 X40.233 Y4.991 E-.23532
G1 X41.193 Y5.417 E-.39924
G1 X41.426 Y5.651 E-.12544
; WIPE_END
G1 E-.04 F1800
G1 X48.932 Y7.034 Z3.4 F30000
G1 X49.925 Y7.217 Z3.4
M73 P92 R0
G1 Z3
G1 E.8 F1800
G1 F4737
M204 S2000
G1 X50.29 Y7.583 E.01587
G1 X50.083 Y7.908
G1 X49.392 Y7.217 E.03002
G1 X48.859 Y7.217
G1 X49.224 Y7.583 E.01587
G1 X48.69 Y7.583
G1 X48.325 Y7.217 E.01587
G1 X47.792 Y7.217
G1 X48.157 Y7.583 E.01587
G1 X47.624 Y7.583
G1 X47.259 Y7.217 E.01587
G1 X46.725 Y7.217
G1 X47.091 Y7.583 E.01587
G1 X46.557 Y7.583
G1 X46.192 Y7.217 E.01587
G1 X45.659 Y7.217
G1 X46.024 Y7.583 E.01587
G1 X45.491 Y7.583
G1 X45.126 Y7.217 E.01587
G1 X44.592 Y7.217
G1 X44.958 Y7.583 E.01587
G1 X44.424 Y7.583
G1 X44.059 Y7.217 E.01587
G1 X43.526 Y7.217
G1 X43.891 Y7.583 E.01587
G1 X43.358 Y7.583
G1 X42.993 Y7.217 E.01587
G1 X42.825 Y7.583
G1 X40.659 Y5.417 E.09409
G1 X39.795 Y5.086
G1 X42.291 Y7.583 E.10849
G1 X41.758 Y7.583
G1 X39.795 Y5.619 E.08532
G1 X39.795 Y6.152
G1 X41.225 Y7.583 E.06215
G1 X40.692 Y7.583
G1 X39.795 Y6.686 E.03897
G1 X39.795 Y7.219
G1 X40.233 Y7.657 E.01903
G1 X40.233 Y8.19
G1 X39.795 Y7.752 E.01903
; WIPE_START
G1 F12000
M204 S10000
G1 X40.233 Y8.19 E-.23532
G1 X40.233 Y7.657 E-.20264
G1 X39.795 Y7.219 E-.23532
G1 X39.795 Y6.991 E-.08673
; WIPE_END
G1 E-.04 F1800
G1 X47.38 Y6.144 Z3.4 F30000
G1 X50.451 Y5.801 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.149587
G1 F4737
G1 X49.699 Y5.049 E.00925
G1 X49.948 Y5.374 F30000
; LINE_WIDTH: 0.343632
G1 F4737
G1 X50.346 Y5.554 E.0107
G1 X50.362 Y5.662 E.00268
; LINE_WIDTH: 0.30488
G1 X50.292 Y5.709 E.0018
; LINE_WIDTH: 0.271441
G1 X50.222 Y5.755 E.00157
; LINE_WIDTH: 0.238001
G1 X50.152 Y5.801 E.00134
; WIPE_START
G1 F15000
G1 X50.222 Y5.755 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X42.618 Y5.095 Z3.4 F30000
G1 X39.828 Y4.853 Z3.4
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.108334
G1 F4737
G1 X39.794 Y5.035 E.00099
; WIPE_START
G1 F15000
G1 X39.828 Y4.853 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X47.217 Y6.764 Z3.4 F30000
G1 X50.456 Y7.601 Z3.4
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.134115
G1 F4737
G1 X50.456 Y7.199 E.00299
; OBJECT_ID: 8
; WIPE_START
G1 F15000
G1 X50.456 Y7.601 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X42.826 Y7.809 Z3.4 F30000
G1 X21.122 Y8.398 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4737
G1 X20.602 Y8.398 E.01725
G1 X20.602 Y4.602 E.12592
G1 X21.122 Y4.602 E.01725
G1 X21.122 Y8.338 E.12393
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4737
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y5.21 E.03073
G1 X31.06 Y5.21 E.2787
G1 X31.06 Y4.86 E.01075
G1 X31.84 Y4.86 E.02397
G1 X31.84 Y5.21 E.01075
G1 X32.24 Y5.21 E.01229
G1 X32.24 Y5.99 E.02397
G1 X24.29 Y5.99 E.24428
G1 X24.29 Y7.01 E.03134
G1 X32.24 Y7.01 E.24428
G1 X32.24 Y7.79 E.02397
G1 X31.84 Y7.79 E.01229
G1 X31.84 Y8.14 E.01075
G1 X31.06 Y8.14 E.02397
G1 X31.06 Y7.79 E.01075
G1 X21.99 Y7.79 E.2787
G1 X21.99 Y8.73 E.02888
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X20.862 Y8.194 Z3.4 F30000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.15602
G1 F4737
G1 X20.862 Y4.806 E.03123
; WIPE_START
G1 F15000
G1 X20.862 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.46 Y6.084 Z3.4 F30000
G1 X31.64 Y5.783 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F4737
M204 S2000
G1 X31.267 Y5.41 E.01619
G1 X30.742 Y5.417
G1 X31.107 Y5.783 E.01587
G1 X30.573 Y5.783
G1 X30.208 Y5.417 E.01587
G1 X29.675 Y5.417
G1 X30.04 Y5.783 E.01587
G1 X29.507 Y5.783
G1 X29.142 Y5.417 E.01587
G1 X28.608 Y5.417
G1 X28.974 Y5.783 E.01587
G1 X28.44 Y5.783
G1 X28.075 Y5.417 E.01587
G1 X27.542 Y5.417
G1 X27.907 Y5.783 E.01587
G1 X27.374 Y5.783
G1 X27.009 Y5.417 E.01587
G1 X26.475 Y5.417
G1 X26.841 Y5.783 E.01587
G1 X26.307 Y5.783
G1 X25.942 Y5.417 E.01587
G1 X25.409 Y5.417
G1 X25.774 Y5.783 E.01587
G1 X25.241 Y5.783
G1 X24.876 Y5.417 E.01587
G1 X24.342 Y5.417
G1 X24.708 Y5.783 E.01587
G1 X24.174 Y5.783
G1 X23.809 Y5.417 E.01587
G1 X23.276 Y5.417
G1 X24.083 Y6.224 E.03505
G1 X24.083 Y6.757
G1 X22.743 Y5.417 E.05823
G1 X21.783 Y4.991
G1 X21.345 Y4.553 E.01903
; WIPE_START
G1 F12000
M204 S10000
G1 X21.783 Y4.991 E-.23532
G1 X22.743 Y5.417 E-.39924
G1 X22.976 Y5.651 E-.12544
; WIPE_END
G1 E-.04 F1800
G1 X30.482 Y7.034 Z3.4 F30000
G1 X31.475 Y7.217 Z3.4
G1 Z3
G1 E.8 F1800
G1 F4737
M204 S2000
G1 X31.84 Y7.583 E.01587
G1 X31.633 Y7.908
G1 X30.942 Y7.217 E.03002
G1 X30.409 Y7.217
G1 X30.774 Y7.583 E.01587
G1 X30.24 Y7.583
G1 X29.875 Y7.217 E.01587
G1 X29.342 Y7.217
G1 X29.707 Y7.583 E.01587
G1 X29.174 Y7.583
G1 X28.809 Y7.217 E.01587
G1 X28.275 Y7.217
G1 X28.641 Y7.583 E.01587
G1 X28.107 Y7.583
G1 X27.742 Y7.217 E.01587
G1 X27.209 Y7.217
G1 X27.574 Y7.583 E.01587
G1 X27.041 Y7.583
G1 X26.676 Y7.217 E.01587
G1 X26.142 Y7.217
G1 X26.508 Y7.583 E.01587
G1 X25.974 Y7.583
G1 X25.609 Y7.217 E.01587
G1 X25.076 Y7.217
G1 X25.441 Y7.583 E.01587
G1 X24.908 Y7.583
G1 X24.543 Y7.217 E.01587
G1 X24.375 Y7.583
G1 X22.209 Y5.417 E.09409
G1 X21.345 Y5.086
G1 X23.841 Y7.583 E.10849
G1 X23.308 Y7.583
G1 X21.345 Y5.619 E.08532
G1 X21.345 Y6.152
M73 P93 R0
G1 X22.775 Y7.583 E.06215
G1 X22.242 Y7.583
G1 X21.345 Y6.686 E.03897
G1 X21.345 Y7.219
G1 X21.783 Y7.657 E.01903
G1 X21.783 Y8.19
G1 X21.345 Y7.752 E.01903
; WIPE_START
G1 F12000
M204 S10000
G1 X21.783 Y8.19 E-.23532
G1 X21.783 Y7.657 E-.20264
G1 X21.345 Y7.219 E-.23532
G1 X21.345 Y6.991 E-.08673
; WIPE_END
G1 E-.04 F1800
G1 X28.93 Y6.144 Z3.4 F30000
G1 X32.001 Y5.801 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.149587
G1 F4737
G1 X31.249 Y5.049 E.00925
G1 X31.498 Y5.374 F30000
; LINE_WIDTH: 0.343632
G1 F4737
G1 X31.896 Y5.554 E.0107
G1 X31.912 Y5.662 E.00268
; LINE_WIDTH: 0.30488
G1 X31.842 Y5.709 E.0018
; LINE_WIDTH: 0.271441
G1 X31.772 Y5.755 E.00157
; LINE_WIDTH: 0.238001
G1 X31.702 Y5.801 E.00134
; WIPE_START
G1 F15000
G1 X31.772 Y5.755 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X24.168 Y5.095 Z3.4 F30000
G1 X21.378 Y4.853 Z3.4
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.108334
G1 F4737
G1 X21.344 Y5.035 E.00099
; WIPE_START
G1 F15000
G1 X21.378 Y4.853 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X28.767 Y6.764 Z3.4 F30000
G1 X32.006 Y7.601 Z3.4
G1 Z3
G1 E.8 F1800
; LINE_WIDTH: 0.134115
G1 F4737
G1 X32.006 Y7.199 E.00299
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X32.006 Y7.601 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 16/20
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
G17
G3 Z3.4 I1.217 J0 P1  F30000
; object ids of layer 16 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer16 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y8.338 E.12393
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y8.194 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X39.55 Y4.806 E.16259
; OBJECT_ID: 8
; WIPE_START
G1 F10699.728
G1 X39.55 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.947 Y7.48 Z3.6 F30000
G1 X21.598 Y8.398 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y8.338 E.12393
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y8.194 Z3.6 F30000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X21.1 Y4.806 E.16259
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.728
G1 X21.1 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 17/20
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
G17
G3 Z3.6 I1.217 J0 P1  F30000
; object ids of layer 17 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer17 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y8.338 E.12393
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y8.194 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X39.55 Y4.806 E.16259
; OBJECT_ID: 8
; WIPE_START
G1 F10699.728
G1 X39.55 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.947 Y7.48 Z3.8 F30000
G1 X21.598 Y8.398 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y8.338 E.12393
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y8.194 Z3.8 F30000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X21.1 Y4.806 E.16259
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.728
G1 X21.1 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 18/20
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
G17
G3 Z3.8 I1.217 J0 P1  F30000
; object ids of layer 18 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer18 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y8.338 E.12393
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y8.194 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X39.55 Y4.806 E.16259
; OBJECT_ID: 8
; WIPE_START
G1 F10699.728
G1 X39.55 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.947 Y7.48 Z4 F30000
M73 P94 R0
G1 X21.598 Y8.398 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y8.338 E.12393
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y8.194 Z4 F30000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X21.1 Y4.806 E.16259
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.728
G1 X21.1 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 19/20
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
G17
G3 Z4 I1.217 J0 P1  F30000
; object ids of layer 19 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer19 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.048 Y8.398
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X39.052 Y8.398 E.03303
G1 X39.052 Y4.602 E.12592
G1 X40.048 Y4.602 E.03303
G1 X40.048 Y8.338 E.12393
G1 X40.44 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y8.73 E.13889
; WIPE_START
M73 P95 R0
G1 F12000
M204 S10000
G1 X38.66 Y8.79 E-.67679
G1 X38.66 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X39.55 Y8.194 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X39.55 Y4.806 E.16259
; OBJECT_ID: 8
; WIPE_START
G1 F10699.728
G1 X39.55 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.947 Y7.48 Z4.2 F30000
G1 X21.598 Y8.398 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X20.602 Y8.398 E.03303
G1 X20.602 Y4.602 E.12592
G1 X21.598 Y4.602 E.03303
G1 X21.598 Y8.338 E.12393
G1 X21.99 Y8.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y8.73 E.13889
; WIPE_START
G1 F12000
M204 S10000
G1 X20.21 Y8.79 E-.67679
G1 X20.21 Y8.571 E-.08321
; WIPE_END
G1 E-.04 F1800
G1 X21.1 Y8.194 Z4.2 F30000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.63172
G1 F1200
G1 X21.1 Y4.806 E.16259
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10699.728
G1 X21.1 Y6.806 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
M625
; layer num/total_layer_count: 20/20
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
G17
G3 Z4.2 I1.217 J0 P1  F30000
; object ids of layer 20 start: 8,12
M624 AwAAAAAAAAA=
;========Date 20250206========
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0
M1004 S5 P1  ; external shutter

M623
; SKIPPABLE_END

; object ids of this layer20 end: 8,12
M625
; OBJECT_ID: 12
; start printing object, unique label id: 12
M624 AgAAAAAAAAA=
G1 X40.44 Y8.79
G1 Z4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X38.66 Y8.79 E.05469
G1 X38.66 Y4.21 E.14073
G1 X40.44 Y4.21 E.05469
G1 X40.44 Y8.73 E.13889
M204 S10000
G1 X39.659 Y8.583 F30000
; FEATURE: Top surface
G1 F1200
M204 S2000
G1 X40.233 Y8.009 E.02491
G1 X40.233 Y7.476
G1 X39.126 Y8.583 E.04808
G1 X38.867 Y8.308
G1 X40.233 Y6.943 E.05933
G1 X40.233 Y6.41
G1 X38.867 Y7.775 E.05933
G1 X38.867 Y7.242
G1 X40.233 Y5.876 E.05933
G1 X40.233 Y5.343
G1 X38.867 Y6.708 E.05933
G1 X38.867 Y6.175
G1 X40.233 Y4.81 E.05933
G1 X40.092 Y4.417
G1 X38.867 Y5.642 E.05321
G1 X38.867 Y5.109
G1 X39.559 Y4.417 E.03004
; OBJECT_ID: 8
; WIPE_START
G1 F12000
M204 S10000
G1 X38.867 Y5.109 E-.37146
G1 X38.867 Y5.642 E-.20264
G1 X39.213 Y5.296 E-.1859
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 12
M625
; start printing object, unique label id: 8
M624 AQAAAAAAAAA=
G1 X31.733 Y6.813 Z4.4 F30000
G1 X21.99 Y8.79 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Outer wall
G1 F1200
M204 S5000
G1 X20.21 Y8.79 E.05469
G1 X20.21 Y4.21 E.14073
G1 X21.99 Y4.21 E.05469
G1 X21.99 Y8.73 E.13889
M204 S10000
G1 X21.209 Y8.583 F30000
; FEATURE: Top surface
G1 F1200
M204 S2000
G1 X21.783 Y8.009 E.02491
G1 X21.783 Y7.476
G1 X20.676 Y8.583 E.04808
G1 X20.417 Y8.308
G1 X21.783 Y6.943 E.05933
G1 X21.783 Y6.41
G1 X20.417 Y7.775 E.05933
G1 X20.417 Y7.242
M73 P96 R0
G1 X21.783 Y5.876 E.05933
G1 X21.783 Y5.343
G1 X20.417 Y6.708 E.05933
G1 X20.417 Y6.175
G1 X21.783 Y4.81 E.05933
G1 X21.642 Y4.417
G1 X20.417 Y5.642 E.05321
G1 X20.417 Y5.109
G1 X21.109 Y4.417 E.03004
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F12000
M204 S10000
G1 X20.417 Y5.109 E-.37146
G1 X20.417 Y5.642 E-.20264
G1 X20.763 Y5.296 E-.18591
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 8
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
G1 Z4.5 F900 ; lower z a little
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

    G1 Z104 F600
    G1 Z102

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

