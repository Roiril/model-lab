"""D1/D2 の組立経路、弾性爪、蝶番ピン、B 継手を実形状で検証する。"""
import math

from mathutils import Matrix, Vector

from printmech.mesh import Mesh


MM = 1000.0
TOL = 0.0001


def _cube(lo, hi, name):
    vertices = [Vector((x, y, z)) for z in (lo[2], hi[2])
                for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    triangles = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6),
                 (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3),
                 (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return Mesh(vertices, triangles, name)


def _calibrate(intersection):
    unit = _cube((0, 0, 0), (2, 2, 2), 'assembly_calibration')
    overlap = intersection(unit, _cube((1, 1, 1), (3, 3, 3), 'known_overlap'))
    contained = intersection(unit, _cube((.5, .5, .5), (1.5, 1.5, 1.5), 'known_contained'))
    separated = intersection(unit, _cube((4, 4, 4), (6, 6, 6), 'known_separated'))
    ok = abs(overlap - 1.0) < 1e-5 and abs(contained - 1.0) < 1e-5 and separated <= TOL
    return dict(ok=ok, checked=3, passed=3 if ok else sum((abs(overlap - 1.0) < 1e-5,
                                                          abs(contained - 1.0) < 1e-5,
                                                          separated <= TOL)),
                overlap_mm3=overlap, contained_mm3=contained, separated_mm3=separated,
                note='既知の1mm³交差、1mm³内包、非交差でEXACT交差計器を校正。')


def _rot_x(degrees, center):
    return (Matrix.Translation((0, center[0], center[1]))
            @ Matrix.Rotation(math.radians(degrees), 4, 'X')
            @ Matrix.Translation((0, -center[0], -center[1])))


def _path(moving, static, samples, intersection):
    worst = {}
    tests = 0
    for value, matrix in samples:
        for moving_name, mesh in moving.items():
            moved = mesh.moved(matrix)
            for static_name, obstacle in static.items():
                volume = intersection(moved, obstacle)
                tests += 1
                key = moving_name + '-' + static_name
                if key not in worst or volume > worst[key]['volume_mm3']:
                    worst[key] = dict(at=round(value, 4), volume_mm3=volume)
    failures = [dict(pair=key, **row) for key, row in worst.items() if row['volume_mm3'] > TOL]
    return dict(ok=not failures, samples=len(samples), intersection_tests=tests,
                tolerance_mm3=TOL, worst=worst, failures=failures)


def _roof_pressed(mesh, P):
    root_z = P.CUBE * MM - P.LID_T * MM
    rigid_top = max((P.ROOF_LEG_BOTTOM + P.ROOF_HOOK_H) * MM,
                    P.ROOF_RELEASE_TOP_Z * MM)
    flex_length = root_z - rigid_top
    hook_lever = rigid_top - (P.ROOF_LEG_BOTTOM + P.ROOF_HOOK_H - P.ROOF_HOOK) * MM
    requested = P.ROOF_PRESS_DELTA * MM
    base_delta = requested / (1 + 1.5 * hook_lever / flex_length)
    vertices = []
    for vertex in mesh.v:
        point = vertex.copy()
        in_leg = (P.ROOF_LEG_Y0 * MM - .01 <= vertex.y <= P.ROOF_LEG_Y1 * MM + .01)
        if vertex.z < root_z and in_leg:
            distance = root_z - vertex.z
            q = min(1.0, max(0.0, distance / flex_length))
            beyond = max(0.0, distance - flex_length)
            offset = base_delta * (q * q * (3 - q) / 2 + beyond * 1.5 / flex_length)
            point.x -= math.copysign(offset, vertex.x)
        vertices.append(point)
    strain = 100 * 1.5 * P.ROOF_LEG_T * MM * requested / flex_length ** 2
    return Mesh(vertices, mesh.t, 'roof_pressed'), dict(
        deflection_mm=round(requested, 4), free_span_mm=round(flex_length, 4),
        estimated_strain_pct=round(strain, 4), estimate_limit_pct=2.0,
        estimate_ok=strain <= 2.0)


def _pin_pressed(mesh, P):
    center_y = P.HINGE_Y * MM
    tip_start = -P.PIN_END_X * MM
    tip_end = tip_start + P.HINGE_TIP_L * MM
    split_half = P.HINGE_SPLIT_W * MM / 2
    tip_radius = P.HINGE_TIP_D * MM / 2
    hole_radius = P.HINGE_HOLE_LID_D * MM / 2
    target_radius = hole_radius - .05
    scale = (target_radius - split_half) / (tip_radius - split_half)
    vertices = []
    for vertex in mesh.v:
        point = vertex.copy()
        if tip_start - .01 <= vertex.x <= tip_end + .01:
            dy = vertex.y - center_y
            if abs(dy) > split_half:
                point.y = center_y + math.copysign(split_half + (abs(dy) - split_half) * scale, dy)
        vertices.append(point)
    delta = max(0.0, tip_radius - target_radius)
    flexible_thickness = (P.HINGE_TIP_D - P.HINGE_SPLIT_W) * MM / 2
    length = P.HINGE_SPLIT_L * MM
    strain = 100 * 1.5 * flexible_thickness * delta / length ** 2
    return Mesh(vertices, mesh.t, 'pin_pressed'), dict(
        radial_deflection_mm=round(delta, 4), insertion_clearance_mm=.05,
        flexible_length_mm=round(length, 4),
        estimated_strain_pct=round(strain, 4), estimate_limit_pct=2.0,
        estimate_ok=strain <= 2.0)


def _unit_and_roof(parts, P, pose, intersection):
    setup_theta = P.LID_OPEN_DEG
    setup = pose(parts, setup_theta)
    pressed, deformation = _roof_pressed(parts['roof'], P)
    unit_names = ('lid', 'roof', 'pin', 'crank', 'link', 'ref_body', 'ref_horn', 'ref_wire')
    unit = {name: (pressed if name == 'roof' else setup[name]) for name in unit_names}
    static = {name: parts[name] for name in ('box', 'speaker_clip', 'ref_speaker') if name in parts}
    lifts = list(range(80, -1, -2)) + [1.0, .5, .25, 0.0]
    lifts = sorted(set(lifts), reverse=True)
    insertion = _path(unit, static,
                      [(lift, Matrix.Translation((0, 0, lift))) for lift in lifts], intersection)
    pressed_final = intersection(pressed, parts['box'])
    restored_final = intersection(parts['roof'], parts['box'])
    release = _path({'roof': pressed}, {'box': parts['box']},
                    [(lift, Matrix.Translation((0, 0, lift)))
                     for lift in [i * .25 for i in range(25)] + [8, 12, 20, 30, 45]], intersection)
    pull_limit = max(8.0, P.ROOF_HOOK_H * MM * 2)
    pull_lifts = [i * .25 for i in range(math.ceil(pull_limit / .25) + 1)]
    restored_pull = [dict(lift_mm=lift,
                          volume_mm3=intersection(parts['roof'].moved(
                              Matrix.Translation((0, 0, lift))), parts['box']))
                     for lift in pull_lifts]
    first_block = next((row for row in restored_pull if row['volume_mm3'] > TOL), None)
    retained = (pressed_final <= TOL and first_block is not None
                and first_block['lift_mm'] <= P.ROOF_HOOK_H * MM)
    assertions = (insertion['ok'], release['ok'], retained, deformation['estimate_ok'])
    checked = len(assertions)
    passed = sum(assertions)
    ok = insertion['ok'] and release['ok'] and retained and deformation['estimate_ok']
    failures = []
    if not insertion['ok']:
        failures.append(dict(check='unit_insert', collisions=insertion['failures']))
    if not release['ok']:
        failures.append(dict(check='roof_release', collisions=release['failures']))
    if not retained:
        failures.append(dict(check='roof_restore_retention', pressed_mm3=pressed_final,
                             restored_mm3=restored_final, first_block=first_block))
    if not deformation['estimate_ok']:
        failures.append(dict(check='roof_strain_estimate', value_pct=deformation['estimated_strain_pct']))
    return dict(ok=ok, checked=checked, passed=max(0, passed), failures=failures,
                setup_lid_deg=setup_theta, insertion=insertion,
                roof_snap=dict(ok=retained and release['ok'] and deformation['estimate_ok'],
                               pressed_intersection_mm3=pressed_final,
                               restored_intersection_mm3=restored_final,
                               first_block=first_block, restored_pull=restored_pull,
                               release=release, deformation=deformation),
                note='箱外で結合したroof/lid/pinとB/A、SGホーン、サーボ一式を上から下降。roof爪だけを幾何学変形。')


def _hinge_pin(parts, P, pose, intersection):
    setup_theta = P.ASSEMBLY_LID_BACK_DEG
    setup = pose(parts, setup_theta)
    pressed, deformation = _pin_pressed(parts['pin'], P)
    lower, _ = parts['pin'].bounds()
    travel = P.CUBE * MM / 2 - lower[0] + 2.0
    positions = [travel - i * .5 for i in range(math.ceil(travel / .5))] + [0.25, 0.0]
    positions = sorted(set(max(0.0, value) for value in positions), reverse=True)
    insertion = _path({'pin': pressed}, {'roof': parts['roof'], 'lid': setup['lid']},
                      [(x, Matrix.Translation((x, 0, 0))) for x in positions], intersection)
    pressed_final = sum(intersection(pressed, other) for other in (parts['roof'], setup['lid']))
    restored = {name: intersection(parts['pin'], mesh)
                for name, mesh in (('roof', parts['roof']), ('lid', setup['lid']))}
    restored_total = sum(restored.values())
    pull_max = max(3.0, P.HINGE_TIP_L * MM + 2.0)
    pulls = [i * .25 for i in range(math.ceil(pull_max / .25) + 1)]
    restored_pull = []
    for pull in pulls:
        moved = parts['pin'].moved(Matrix.Translation((pull, 0, 0)))
        volumes = {name: intersection(moved, mesh)
                   for name, mesh in (('roof', parts['roof']), ('lid', setup['lid']))}
        restored_pull.append(dict(pull_mm=pull, volume_mm3=sum(volumes.values()), by_part=volumes))
    first_block = next((row for row in restored_pull if row['volume_mm3'] > TOL), None)
    retained = first_block is not None and first_block['pull_mm'] < P.HINGE_SPLIT_L * MM
    seated_clear = restored_total <= TOL
    ok = (insertion['ok'] and pressed_final <= TOL and seated_clear and retained
          and deformation['estimate_ok'])
    failures = []
    if not insertion['ok']:
        failures.append(dict(check='pin_insert', collisions=insertion['failures']))
    if pressed_final > TOL:
        failures.append(dict(check='pin_compressed_seating', intersection_mm3=pressed_final))
    if not seated_clear:
        failures.append(dict(check='pin_restored_seating', intersection_mm3=restored_total))
    if not retained:
        failures.append(dict(check='pin_restore_retention', first_block=first_block))
    if not deformation['estimate_ok']:
        failures.append(dict(check='pin_strain_estimate', value_pct=deformation['estimated_strain_pct']))
    assertions = (insertion['ok'], pressed_final <= TOL, seated_clear, retained,
                  deformation['estimate_ok'])
    checked = len(assertions)
    return dict(ok=ok, checked=checked, passed=sum(assertions), failures=failures,
                setup_lid_deg=setup_theta, travel_mm=round(travel, 4), insertion=insertion,
                pressed_intersection_mm3=pressed_final,
                restored_intersection_mm3=restored,
                first_block=first_block, restored_pull=restored_pull,
                deformation=deformation,
                note='割り先端を穴径より0.05mm小さく幾何学圧縮して挿入。静止位置で復元し、引抜き経路のEXACT交差を保持として測定。')


def _b_joint(parts, P, K, pose, intersection):
    setup_theta = P.ASSEMBLY_LID_BACK_DEG
    setup = pose(parts, setup_theta)
    alpha_setup = K.sweep(setup_theta, max(2, math.ceil(setup_theta * 2)))[-1][1]
    point_b = K.pin_b(setup_theta)
    link_setup_deg = K.link_angle(setup_theta, alpha_setup)
    key_deg = setup_theta + P.B_KEY_DEG - 180.0
    link_at_key = setup['link'].moved(_rot_x(key_deg - link_setup_deg, point_b))
    insert_values = [-8.0 + i * .25 for i in range(33)]
    insertion = _path({'link': link_at_key}, {'lid': setup['lid']},
                      [(x, Matrix.Translation((x, 0, 0))) for x in insert_values], intersection)

    forward = (link_setup_deg - key_deg) % 360.0
    candidates = []
    for delta in (forward, forward - 360.0):
        count = max(1, math.ceil(abs(delta) / 2.5))
        values = [delta * i / count for i in range(count + 1)]
        path = _path({'link': link_at_key}, {'lid': setup['lid']},
                     [(value, _rot_x(value, point_b)) for value in values], intersection)
        mean_a_z = sum(point_b[1] - K.L_LINK * math.sin(math.radians(key_deg + value))
                       for value in values) / len(values)
        candidates.append(dict(delta_deg=round(delta, 4), mean_a_z_mm=round(mean_a_z, 4), **path))
    clear_candidates = [row for row in candidates if row['ok']]
    chosen = min(clear_candidates, key=lambda row: row['mean_a_z_mm']) if clear_candidates else min(
        candidates, key=lambda row: max((item['volume_mm3'] for item in row['worst'].values()), default=0))

    pin_exit = (P.FIN_T + P.AX_GAP + P.B_TAB_T) * MM
    pull_max = pin_exit + 2.0
    pulls = [i * .25 for i in range(math.ceil(pull_max / .25) + 1)]
    operating = []
    retained = True
    tests = 0
    for theta in (0.0, K.THETA_OPEN / 4, K.THETA_OPEN / 2, 3 * K.THETA_OPEN / 4, K.THETA_OPEN):
        state = pose(parts, theta)
        path = []
        for pull in pulls:
            volume = intersection(state['link'].moved(Matrix.Translation((-pull, 0, 0))), state['lid'])
            tests += 1
            path.append(dict(pull_mm=pull, volume_mm3=volume))
        first = next((row for row in path if row['volume_mm3'] > TOL), None)
        pose_ok = first is not None and first['pull_mm'] < pin_exit
        retained &= pose_ok
        operating.append(dict(theta_deg=round(theta, 4), ok=pose_ok,
                              first_contact_mm=None if first is None else first['pull_mm'],
                              max_intersection_mm3=max(row['volume_mm3'] for row in path)))
    key_withdrawal = []
    for pull in pulls:
        volume = intersection(link_at_key.moved(Matrix.Translation((-pull, 0, 0))), setup['lid'])
        tests += 1
        key_withdrawal.append(dict(pull_mm=pull, volume_mm3=volume))
    key_clear = all(row['volume_mm3'] <= TOL for row in key_withdrawal)
    lock_ok = retained and key_clear
    ok = insertion['ok'] and chosen['ok'] and lock_ok
    failures = []
    if not insertion['ok']:
        failures.append(dict(check='b_insert', collisions=insertion['failures']))
    if not chosen['ok']:
        failures.append(dict(check='b_turn', collisions=chosen['failures']))
    if not lock_ok:
        failures.append(dict(check='b_retention', operating=operating, key_clear=key_clear))
    assertions = [insertion['ok'], chosen['ok'], key_clear]
    assertions.extend(row['ok'] for row in operating)
    checked = len(assertions)
    return dict(ok=ok, checked=checked, passed=sum(assertions), failures=failures,
                key_link_deg=round(key_deg, 4), insertion=insertion,
                turn=dict(ok=chosen['ok'], chosen_delta_deg=chosen['delta_deg'], candidates=candidates),
                retention=dict(ok=lock_ok, pin_exit_mm=round(pin_exit, 4),
                               operating=operating, key_withdrawal_clear=key_clear,
                               key_withdrawal=key_withdrawal),
                note='B鍵角で挿入して組立角へ回転。通常開角5姿勢で、ピンが抜ける前の保持交差を測定。')


def _a_joint(parts, P, K, pose, intersection):
    setup_theta = P.ASSEMBLY_LID_BACK_DEG
    setup = pose(parts, setup_theta)
    alpha_setup = K.sweep(setup_theta, max(2, math.ceil(setup_theta * 2)))[-1][1]
    point_a = K.pin_a(alpha_setup)
    link_setup_deg = K.link_angle(setup_theta, alpha_setup)
    alpha_key = link_setup_deg - P.BAYONET_KEY_DEG
    crank_at_key = setup['crank'].moved(_rot_x(alpha_key - alpha_setup, point_a))
    insert_values = [-8.0 + i * .25 for i in range(33)]
    insertion = _path({'crank': crank_at_key}, {'link': setup['link'], 'lid': setup['lid']},
                      [(x, Matrix.Translation((x, 0, 0))) for x in insert_values], intersection)
    count = max(1, math.ceil(abs(alpha_setup - alpha_key) / 2.5))
    angles = [alpha_key + (alpha_setup - alpha_key) * i / count for i in range(count + 1)]
    turn = _path({'crank': crank_at_key}, {'link': setup['link'], 'lid': setup['lid']},
                 [(angle, _rot_x(angle - alpha_key, point_a)) for angle in angles], intersection)

    pin_exit = (P.LINK_T + P.AX_GAP + P.TAB_T) * MM
    pulls = [i * .25 for i in range(math.ceil((pin_exit + 2) / .25) + 1)]
    operating = []
    relative_angles = []
    count = math.ceil(K.THETA_OPEN / 2.5)
    for index in range(count + 1):
        theta = K.THETA_OPEN * index / count
        state = pose(parts, theta)
        alpha = K.sweep(theta, max(2, math.ceil(theta * 2)))[-1][1]
        relative = K.relative_link_crank(theta, alpha)
        key_distance = abs((relative - P.BAYONET_KEY_DEG + 180.0) % 360.0 - 180.0)
        relative_angles.append(dict(theta_deg=round(theta, 4), relative_deg=round(relative, 4),
                                    key_distance_deg=round(key_distance, 4)))
        path = []
        for pull in pulls:
            moved = state['link'].moved(Matrix.Translation((pull, 0, 0)))
            forward = intersection(moved, state['crank'])
            reverse = intersection(state['crank'], moved)
            path.append(dict(pull_mm=pull, volume_mm3=max(forward, reverse),
                             forward_mm3=forward, reverse_mm3=reverse))
            if abs(forward - reverse) > .001 or (forward > TOL and reverse > TOL):
                break
        first = next((row for row in path
                      if row['forward_mm3'] > TOL and row['reverse_mm3'] > TOL), None)
        consistent = all(abs(row['forward_mm3'] - row['reverse_mm3']) <= .001 for row in path)
        row_ok = consistent and first is not None and first['pull_mm'] < pin_exit
        remaining_engagement = None if first is None else pin_exit - first['pull_mm']
        operating.append(dict(theta_deg=round(theta, 4), relative_deg=round(relative, 4), ok=row_ok,
                              first_contact_mm=None if first is None else first['pull_mm'],
                              remaining_pin_engagement_mm=(None if remaining_engagement is None
                                                           else round(remaining_engagement, 4)),
                              max_intersection_mm3=max(row['volume_mm3'] for row in path),
                              intersection_order_consistent=consistent,
                              direction_mismatch_max_mm3=max(abs(row['forward_mm3'] - row['reverse_mm3'])
                                                             for row in path)))
    closed = pose(parts, 0.0)
    alpha0 = K.ALPHA0
    point_a0 = K.pin_a(alpha0)
    relative0 = K.relative_link_crank(0.0, alpha0)
    link_at_key = closed['link'].moved(_rot_x(P.BAYONET_KEY_DEG - relative0, point_a0))
    key_path = []
    for pull in pulls:
        moved = link_at_key.moved(Matrix.Translation((pull, 0, 0)))
        forward = intersection(moved, closed['crank'])
        reverse = intersection(closed['crank'], moved)
        key_path.append(dict(pull_mm=pull, volume_mm3=max(forward, reverse),
                             forward_mm3=forward, reverse_mm3=reverse))
    key_order_consistent = all(abs(row['forward_mm3'] - row['reverse_mm3']) <= .001
                               for row in key_path)
    key_clear = (key_order_consistent
                 and all(row['forward_mm3'] <= TOL and row['reverse_mm3'] <= TOL for row in key_path))
    closest_key = min(relative_angles, key=lambda row: row['key_distance_deg'])
    assertions = [insertion['ok'], turn['ok'], key_clear]
    assertions.extend(row['ok'] for row in operating)
    failures = []
    if not insertion['ok']:
        failures.append(dict(check='a_insert', collisions=insertion['failures']))
    if not turn['ok']:
        failures.append(dict(check='a_turn', collisions=turn['failures']))
    if not all(row['ok'] for row in operating) or not key_clear:
        failures.append(dict(check='a_retention', operating=operating, key_clear=key_clear))
    return dict(ok=all(assertions), checked=len(assertions), passed=sum(assertions), failures=failures,
                key_relative_deg=P.BAYONET_KEY_DEG, insertion=insertion, turn=turn,
                retention=dict(ok=all(row['ok'] for row in operating) and key_clear,
                               pin_exit_mm=pin_exit, operating=operating,
                               pin_exit_basis='LINK_T + AX_GAP + TAB_T。円柱芯はtab先端まで連続し、link近側面が先端を越えると完全離脱。',
                               samples=len(operating), step_deg=K.THETA_OPEN / count,
                               minimum_remaining_pin_engagement_mm=min((
                                   row['remaining_pin_engagement_mm'] for row in operating
                                   if row['remaining_pin_engagement_mm'] is not None), default=None),
                               relative_range_deg=[min(row['relative_deg'] for row in relative_angles),
                                                   max(row['relative_deg'] for row in relative_angles)],
                               key_distance_min_deg=closest_key['key_distance_deg'],
                               key_closest_theta_deg=closest_key['theta_deg'],
                               key_withdrawal_clear=key_clear,
                               key_intersection_order_consistent=key_order_consistent,
                               key_withdrawal=key_path),
                note='Bを保持したlid/linkへA鍵角でcrankを挿入。通常開角を2.5°以下刻みで保持測定し、片側1個の鍵角との360°距離も記録。')


def _clip_pressed(mesh, P, K):
    center = (P.PED_Y0 + P.PED_Y1) * MM / 2
    root_z = K.O[1] + P.SG.BODY_W * MM / 2 + P.CLIP_TOP_GAP * MM
    free_z = (P.HOOK_Z + P.HOOK_H) * MM
    length = root_z - free_z
    delta = max(0.0, P.HOOK_D * MM - .3)
    y0, y1 = P.PED_Y0 * MM, P.PED_Y1 * MM
    band = P.CLIP_SIDE_GAP * MM + P.CLIP_LEG_T * MM + delta + .02
    vertices = []
    for vertex in mesh.v:
        point = vertex.copy()
        is_leg = abs(vertex.y - y0) <= band or abs(vertex.y - y1) <= band
        if is_leg and vertex.z < root_z:
            q = min(1.0, max(0.0, (root_z - vertex.z) / length))
            point.y += math.copysign(delta * q * q * (3 - q) / 2, vertex.y - center)
        vertices.append(point)
    strain = 100 * 1.5 * P.CLIP_LEG_T * MM * delta / length ** 2
    return Mesh(vertices, mesh.t, 'clip_pressed'), dict(
        deflection_mm=round(delta, 4), free_span_mm=round(length, 4),
        estimated_strain_pct=round(strain, 4), estimate_limit_pct=2.0,
        estimate_ok=strain <= 2.0)


def _servo_clip(parts, P, K, pose, intersection):
    state = pose(parts, P.LID_OPEN_DEG)
    pressed, deformation = _clip_pressed(parts['clip'], P, K)
    static = {'box': parts['box'], 'wire': parts['ref_wire'], 'crank': state['crank'],
              'horn': state['ref_horn'], 'link': state['link'], 'lid': state['lid']}
    lifts = [25 - i * .25 for i in range(101)]
    insertion = _path({'clip': pressed}, static,
                      [(lift, Matrix.Translation((0, 0, lift))) for lift in lifts], intersection)
    pressed_final = intersection(pressed, parts['box'])
    restored_final = intersection(parts['clip'], parts['box'])
    pulls = [i * .25 for i in range(17)]
    pull_path = [dict(lift_mm=lift,
                      volume_mm3=intersection(parts['clip'].moved(
                          Matrix.Translation((0, 0, lift))), parts['box'])) for lift in pulls]
    first_block = next((row for row in pull_path if row['volume_mm3'] > TOL), None)
    retained = first_block is not None and first_block['lift_mm'] < P.HOOK_H * MM
    preload = intersection(parts['clip'], parts['ref_body'])
    assertions = (insertion['ok'], pressed_final <= TOL, restored_final <= TOL,
                  retained, deformation['estimate_ok'])
    failures = []
    if not insertion['ok']:
        failures.append(dict(check='clip_insert', collisions=insertion['failures']))
    if pressed_final > TOL or restored_final > TOL:
        failures.append(dict(check='clip_seating', pressed_mm3=pressed_final,
                             restored_mm3=restored_final))
    if not retained:
        failures.append(dict(check='clip_retention', first_block=first_block))
    if not deformation['estimate_ok']:
        failures.append(dict(check='clip_strain_estimate', value_pct=deformation['estimated_strain_pct']))
    return dict(ok=all(assertions), checked=len(assertions), passed=sum(assertions), failures=failures,
                setup_lid_deg=P.LID_OPEN_DEG, insertion=insertion,
                pressed_intersection_mm3=pressed_final, restored_intersection_mm3=restored_final,
                first_block=first_block, restored_pull=pull_path, deformation=deformation,
                servo_preload_intersection_mm3=preload,
                note='lidを開いてclip脚を幾何学変形し上から挿入。サーボ本体への板ばね予圧は意図接触として別記録。')


def run(parts, P, K, intersection, pose):
    """組立検証を実行し、JSONへ直接保存できる辞書を返す。"""
    calibration = _calibrate(intersection)
    unit = _unit_and_roof(parts, P, pose, intersection)
    pin = _hinge_pin(parts, P, pose, intersection)
    joint_b = _b_joint(parts, P, K, pose, intersection)
    joint_a = _a_joint(parts, P, K, pose, intersection)
    clip = _servo_clip(parts, P, K, pose, intersection)
    sections = (unit, pin, joint_b, joint_a, clip)
    failures = []
    for name, section in zip(('unit_and_roof', 'hinge_pin', 'b_joint', 'a_joint', 'servo_clip'), sections):
        if not section['ok']:
            failures.append(dict(check=name, details=section['failures']))
    if not calibration['ok']:
        failures.insert(0, dict(check='calibration', details=calibration))
    ok = calibration['ok'] and all(section['ok'] for section in sections)
    checked = calibration['checked'] + sum(section['checked'] for section in sections)
    passed = calibration['passed'] + sum(section['passed'] for section in sections)
    return dict(ok=ok, status='verified' if ok else 'failed', checked=checked, passed=passed,
                failures=failures, physical_tested=False, calibration=calibration,
                unit_and_roof=unit, hinge_pin=pin, b_joint=joint_b,
                a_joint=joint_a, servo_clip=clip,
                method='実STLのEXACT交差と幾何学変形で経路を測定。変形時のひずみは片持ち梁の推定値。実物の反復保持力、手と配線の収まりは未確認。',
                assembly_order=['箱の外でlidとBを組む', 'AとSGホーンを組む',
                                'roof/pinを65°で組む', '天面とサーボ一式を上から下ろす', 'lidを開けてclipを付ける',
                                'roofを復元してsnap保持する'])
