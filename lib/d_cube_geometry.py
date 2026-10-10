"""D1/D2 共通の80mm角箱と隠れ蝶番。

既存C2の内部機構を設定差し替えで使い、外殻・天面・蝶番だけをD形状へ置き換える。
形状はmmで作り、書き出し時だけmへ戻す。
"""
import json
import importlib.util
import math
import os
import sys
import types


def install_linkage(ns, p):
    """Blenderに依存しない4節リンク関数をlinkage.pyへ展開する。"""
    mm = 1000.0
    h = (p.HINGE_Y * mm, p.HINGE_Z * mm)
    o = (p.SHAFT_Y * mm, p.SHAFT_Z * mm)
    a_len = p.CRANK_A * mm
    b_rel = (p.B_REL_Y * mm, p.B_REL_Z * mm)
    alpha0 = p.CRANK_ALPHA_CLOSED_DEG
    theta_open = p.LID_OPEN_DEG

    def rot(v, deg):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

    def add(a, b):
        return (a[0] + b[0], a[1] + b[1])

    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1])

    def norm(v):
        return math.hypot(v[0], v[1])

    def pin_a(alpha):
        r = math.radians(alpha)
        return (o[0] + a_len * math.cos(r), o[1] + a_len * math.sin(r))

    def pin_b(theta):
        return add(h, rot(b_rel, theta))

    b0 = pin_b(0.0)
    l_link = norm(sub(b0, pin_a(alpha0)))

    def crank_angle(theta, prev=alpha0):
        b = pin_b(theta)
        d = norm(sub(b, o))
        if d > a_len + l_link or d < abs(l_link - a_len):
            return None
        base = math.degrees(math.atan2(b[1] - o[1], b[0] - o[0]))
        x = math.degrees(math.acos(max(-1.0, min(1.0, (a_len ** 2 + d * d - l_link ** 2) / (2 * a_len * d)))))
        return min((base + x, base - x), key=lambda c: abs((c - prev + 180.0) % 360.0 - 180.0))

    def unwrap(alpha, prev):
        return prev + ((alpha - prev + 180.0) % 360.0 - 180.0)

    def sweep(theta_max=theta_open, n=96, theta_min=0.0):
        out = []
        prev = alpha0
        if theta_min != 0.0:
            for k in range(1, 41):
                a = crank_angle(theta_min * k / 40, prev)
                if a is None:
                    return None
                prev = unwrap(a, prev)
        for i in range(n + 1):
            theta = theta_min + (theta_max - theta_min) * i / n
            alpha = crank_angle(theta, prev)
            if alpha is None:
                return None
            prev = unwrap(alpha, prev)
            out.append((theta, prev))
        return out

    def link_angle(theta, alpha):
        a, b = pin_a(alpha), pin_b(theta)
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    def relative_link_crank(theta, alpha):
        return (link_angle(theta, alpha) - alpha + 180.0) % 360.0 - 180.0

    def pressure_angle(theta, alpha):
        a, b = pin_a(alpha), pin_b(theta)
        link = sub(b, a)
        velocity = rot(sub(b, h), 90.0)
        cosine = abs(link[0] * velocity[0] + link[1] * velocity[1]) / (norm(link) * norm(velocity))
        return math.degrees(math.acos(min(1.0, cosine)))

    def ratio(theta, step=0.05):
        a1 = crank_angle(theta - step, crank_angle(theta))
        a2 = crank_angle(theta + step, crank_angle(theta))
        return (2 * step) / (unwrap(a2, a1) - a1)

    ns.update(MM=mm, H=h, O=o, A_LEN=a_len, B_REL=b_rel, ALPHA0=alpha0,
              THETA_OPEN=theta_open, B0=b0, L_LINK=l_link, rot=rot, add=add,
              sub=sub, norm=norm, pin_a=pin_a, pin_b=pin_b, crank_angle=crank_angle,
              unwrap=unwrap, sweep=sweep, link_angle=link_angle,
              relative_link_crank=relative_link_crank, pressure_angle=pressure_angle,
              ratio=ratio)


def _load_c2_template(model_file):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.dirname(os.path.abspath(model_file))
    source_path = os.path.join(repo, "models", "mystery-box-sg92r-c2", "model.py")
    with open(source_path, "r", encoding="utf-8") as fh:
        source = fh.read()
    marker = "\nmain()"
    if marker not in source:
        raise RuntimeError("C2 model template has no final main() call")
    source = source.rsplit(marker, 1)[0] + "\n"
    module = types.ModuleType(f"_d_cube_{os.path.basename(os.path.dirname(model_file))}")
    module.__file__ = os.path.abspath(model_file)
    params_spec = importlib.util.spec_from_file_location(f"{module.__name__}_params", os.path.join(model_dir, "params.py"))
    params_module = importlib.util.module_from_spec(params_spec)
    params_spec.loader.exec_module(params_module)
    old_params = sys.modules.get("params")
    old_linkage = sys.modules.get("linkage")
    try:
        sys.modules["params"] = params_module
        linkage_spec = importlib.util.spec_from_file_location(f"{module.__name__}_linkage", os.path.join(model_dir, "linkage.py"))
        linkage_module = importlib.util.module_from_spec(linkage_spec)
        linkage_spec.loader.exec_module(linkage_module)
        sys.modules["linkage"] = linkage_module
        exec(compile(source, source_path, "exec"), module.__dict__)
    finally:
        if old_params is None:
            sys.modules.pop("params", None)
        else:
            sys.modules["params"] = old_params
        if old_linkage is None:
            sys.modules.pop("linkage", None)
        else:
            sys.modules["linkage"] = old_linkage
    return module


def _patch_geometry(m):
    p = m.P
    m.R = m.mm(p.HINGE_EAR_R)

    raw_union = m.union
    raw_cut = m.cut

    def discard(ob):
        if ob and ob.name in m.bpy.data.objects:
            m.bpy.data.objects.remove(ob, do_unlink=True)

    def union_keep_internal(target, addition):
        if addition.name.startswith(("knuckle_in", "hinge_gusset")):
            discard(addition)
            return target
        return raw_union(target, addition)

    def cut_without_external_openings(target, cutter):
        if cutter.name.startswith(("sweep", "back_lip", "hole_r", "hole_l", "mouth_r", "mouth_l", "wire_exit")):
            discard(cutter)
            return target
        return raw_cut(target, cutter)

    m.union = union_keep_internal
    m.cut = cut_without_external_openings

    def outer_solid(_bed_side, name):
        return m.box(-m.HALF, m.HALF, -m.HALF, m.HALF, 0.0, m.L, name)

    def knuckle_bite_poly():
        return [(-m.HALF - 5, m.SPLIT), (m.HALF + 5, m.SPLIT),
                (m.HALF + 5, m.L + 10), (-m.HALF - 5, m.L + 10)]

    m.outer_solid = outer_solid
    m.knuckle_bite_poly = knuckle_bite_poly

    def seam_boundary(radius):
        points = []
        for i in range(17):
            z = m.SPLIT + (m.L - m.SPLIT) * i / 16
            dz = z - m.HZ
            y = m.HY + math.sqrt(max(0.0, radius * radius - dz * dz))
            points.append((y, z))
        return points

    def top_poly(radius, front):
        arc = seam_boundary(radius)
        if front:
            return m.ccw([arc[0], (m.HALF, m.SPLIT), (m.HALF, m.L), arc[-1], *reversed(arc[1:-1])])
        return m.ccw([(-m.HALF, m.SPLIT), arc[0], *arc[1:], (-m.HALF, m.L)])

    def path_points():
        return [(m.HY, m.HZ - 3.5), (m.HY + 6.0, m.HZ - 12.0),
                (m.HY + 10.0, m.HZ - 18.0), m.K.B0,
                (m.HY + 20.0, m.SPLIT + 0.2)]

    def make_path(x0, x1, radius, name):
        points = path_points()
        result = None
        for index, (a, b) in enumerate(zip(points, points[1:])):
            poly = m.hull(m.circle(a, radius, 24) + m.circle(b, radius, 24))
            segment = m.prism(poly, "x", x0, x1, f"{name}_{index}")
            if result is None:
                result = segment
            else:
                m.union(result, segment)
        return result

    def add_path(target, x0, x1, radius, name):
        m.union(target, make_path(x0, x1, radius, name))

    def build_lid():
        lid = m.prism(top_poly(m.mm(p.LID_SEAM_R), True), "x", -m.HALF, m.HALF, "lid")
        knuckle_r = m.mm(p.HINGE_EAR_R)
        lx = m.mm(p.LID_KNUCKLE_HALF_X)
        m.union(lid, m.cyl_x((m.HY, m.HZ), knuckle_r, -lx, lx, 96, "lid_knuckle"))
        support_w = m.mm(p.LID_SUPPORT_X_W)
        for x0, x1 in ((-lx, -lx + support_w), (lx - support_w, lx)):
            add_path(lid, x0, x1, m.mm(p.LID_ARM_HALF_W), "lid_support")
        fin = make_path(m.FIN_X0, m.FIN_X1, m.mm(p.LID_ARM_HALF_W), "lid_fin")
        m.union(fin, m.cyl_x(m.K.B0, m.mm(p.FIN_B_BOSS_R), m.FIN_X0, m.FIN_X1, 64, "fin_boss"))
        m.cut_b_joint(fin)
        m.clean(fin)
        m.union(lid, fin)
        m.cut(lid, m.cyl_x((m.HY, m.HZ), m.mm(p.HINGE_HOLE_LID_D) / 2,
                           -lx - 0.5, lx + 0.5, 64, "lid_hinge_hole"))
        m.clean(lid)
        lid.name = "lid"
        return lid

    def roof_support_poly():
        top = (m.HY, m.SPLIT + 0.4)
        return m.hull(m.circle((m.HY, m.HZ), m.mm(p.HINGE_EAR_R), 48) + m.circle(top, 2.2, 24))

    def build_roof():
        roof = m.prism(top_poly(m.mm(p.ROOF_SEAM_R), False), "x", -m.HALF, m.HALF, "roof")
        ear_r = m.mm(p.HINGE_EAR_R)
        hole_r = m.mm(p.HINGE_HOLE_LID_D) / 2
        lx = m.mm(p.LID_KNUCKLE_HALF_X)
        m.cut(roof, m.cyl_x((m.HY, m.HZ), m.mm(p.ROOF_KNUCKLE_CLEAR_R),
                            -lx - 0.2, lx + 0.2, 96, "roof_knuckle_pocket"))
        for x0, x1 in ((-m.mm(p.ROOF_EAR_X1), -m.mm(p.ROOF_EAR_X0)),
                       (m.mm(p.ROOF_EAR_X0), m.mm(p.ROOF_EAR_X1))):
            m.union(roof, m.prism(roof_support_poly(), "x", x0, x1, "roof_ear_support"))
            m.cut(roof, m.cyl_x((m.HY, m.HZ), hole_r, x0 - 0.5, x1 + 0.5, 64, "roof_hole"))

        z0, z1 = m.mm(p.ROOF_LEG_BOTTOM), m.SPLIT + 0.2
        t, x, hook = m.mm(p.ROOF_LEG_T), m.mm(p.ROOF_LEG_X), m.mm(p.ROOF_HOOK)
        for side in (-1, 1):
            rx, rt = m.mm(p.ROOF_RELEASE_X), m.mm(p.ROOF_RELEASE_T)
            rz0, rz1 = m.mm(p.ROOF_RELEASE_BOTTOM), m.mm(p.ROOF_RELEASE_FOOT_Z)
            rz_top = m.mm(p.ROOF_RELEASE_TOP_Z)
            poly = [(rx, rz0), (rx + rt, rz0), (rx + rt, rz1), (x, rz1),
                    (x, z0), (x + hook, z0),
                    (x + hook, z0 + m.mm(p.ROOF_HOOK_H) - hook),
                    (x, z0 + m.mm(p.ROOF_HOOK_H)), (x, z1), (x - t, z1),
                    (x - t, rz_top), (rx, rz1)]
            if side < 0:
                poly = [(-px, pz) for px, pz in reversed(poly)]
            m.union(roof, m.prism(poly, "y", m.mm(p.ROOF_LEG_Y0), m.mm(p.ROOF_LEG_Y1), "roof_leg"))
        roof.name = "roof"
        return roof

    def build_pin():
        body_r = m.mm(p.HINGE_PIN_D) / 2
        tip_ry = m.mm(p.HINGE_TIP_D) / 2
        tip_rz = body_r
        x0, x1 = -m.mm(p.PIN_END_X), m.mm(p.PIN_HEAD_X0)
        pin = m.cyl_x((0, 0), body_r, x0 + m.mm(p.HINGE_TIP_L) - 0.2, x1 + 0.2, 64, "pin")
        tip_poly = [(tip_ry * math.cos(2 * math.pi * i / 64),
                     tip_rz * math.sin(2 * math.pi * i / 64)) for i in range(64)]
        m.union(pin, m.prism(tip_poly, "x", x0, x0 + m.mm(p.HINGE_TIP_L), "pin_tip"))
        head_ry = m.mm(p.PIN_HEAD_R)
        head_rz = body_r + 0.05
        head_poly = [(head_ry * math.cos(2 * math.pi * i / 64),
                      head_rz * math.sin(2 * math.pi * i / 64)) for i in range(64)]
        m.union(pin, m.prism(head_poly, "x", x1, m.mm(p.PIN_END_X), "pin_head"))
        m.cut(pin, m.box(x0 - 0.2, x0 + m.mm(p.HINGE_SPLIT_L),
                         -m.mm(p.HINGE_SPLIT_W) / 2, m.mm(p.HINGE_SPLIT_W) / 2,
                         -10, 10, "pin_split"))
        m.cut(pin, m.box(x0 - 1, m.mm(p.PIN_END_X) + 1, -10, 10,
                         -10, -body_r + m.mm(p.HINGE_PIN_FLAT), "pin_flat"))
        m.clean(pin)
        pin.name = "pin"
        return pin

    m.build_lid = build_lid
    m.build_roof = build_roof
    m.build_pin = build_pin


def _install_main(m):
    def main():
        m.clear_scene()
        os.makedirs(m.BUILD, exist_ok=True)
        a0 = m.K.ALPHA0
        parts = {
            "box": m.build_box(),
            "lid": m.build_lid(),
            "roof": m.build_roof(),
            "crank": m.build_crank(a0),
            "link": m.build_link(a0, 0.0),
            "clip": m.build_clip(),
            "speaker_clip": m.build_speaker_clip(),
        }
        pin_print = m.build_pin()
        pin = m.copy_obj(pin_print, "pin_asm")
        m.transform(pin, m.Matrix.Translation((0, m.HY, m.HZ)))
        parts["pin"] = pin
        refs = {key: m.import_ref(key) for key in ("body", "horn", "wire")}
        refs["speaker"] = m.build_speaker_ref()
        m.place_horn(refs["horn"], a0)

        joint_b_test = m.build_joint_b_test()
        joint_b_test_print = m.copy_obj(joint_b_test, "joint_b_test_print")
        m.to_print(joint_b_test_print, m.FLIP_X)
        assert m.nonmanifold(joint_b_test_print) == 0, joint_b_test_print.name
        assert m.component_count(joint_b_test_print) == 1, joint_b_test_print.name
        m.save_stl([joint_b_test_print], os.path.join(m.BUILD, "print_joint_b_test.stl"))

        speaker_test = m.copy_obj(parts["box"], "speaker_test")
        m.intersect(speaker_test, m.box(15.0, m.HALF + 1, -1.0, m.HALF + 1,
                                        -1.0, 40.0, "speaker_test_trim"))
        m.to_print(speaker_test, m.Matrix.Identity(4))
        assert m.nonmanifold(speaker_test) == 0, speaker_test.name
        assert m.component_count(speaker_test) == 1, speaker_test.name
        m.save_stl([speaker_test], os.path.join(m.BUILD, "print_speaker_test.stl"))

        report = {"units": "mm", "parts": {},
                  "servo_dimension_profile": m.P.SERVO_DIMENSION_PROFILE}
        for key, ob in parts.items():
            report["parts"][key] = {
                "nonmanifold": m.nonmanifold(ob),
                "nm_at": m.nonmanifold_where(ob),
                "components": m.component_count(ob),
                "volume_mm3": round(m.volume(ob), 1),
                "bbox": m.bbox(ob),
            }
            assert report["parts"][key]["nonmanifold"] == 0, (key, report["parts"][key])
            assert report["parts"][key]["components"] == 1, (key, report["parts"][key])
        report["linkage"] = {
            "H": m.K.H, "O": m.K.O, "a": m.K.A_LEN, "l": m.K.L_LINK,
            "B0": m.K.B0, "alpha0": a0,
            "layers": {"crank": [m.CRANK_X0, m.CRANK_X1],
                       "link": [m.LINK_X0, m.LINK_X1], "fin": [m.FIN_X0, m.FIN_X1]},
        }
        report["tests"] = {
            "joint_b_test": {"nonmanifold": m.nonmanifold(joint_b_test_print),
                             "components": m.component_count(joint_b_test_print),
                             "bbox": m.bbox(joint_b_test_print)},
            "speaker_test": {"nonmanifold": m.nonmanifold(speaker_test),
                             "components": m.component_count(speaker_test),
                             "bbox": m.bbox(speaker_test)},
        }

        opened = {}
        pose = m.pose_matrices(m.K.THETA_OPEN)
        for key in ("lid", "crank", "link"):
            opened[key] = m.copy_obj(parts[key], f"{key}_open")
            m.transform(opened[key], pose[key])
        horn_open = m.copy_obj(refs["horn"], "horn_open")
        m.transform(horn_open, m.rot_x_about(pose["alpha"] - a0, m.OY, m.OZ))

        for key, ob in list(parts.items()) + [(f"ref_{key}", ob) for key, ob in refs.items()]:
            m.save_stl([ob], os.path.join(m.BUILD, f"{key}.stl"))

        printed = {}
        print_mats = (("box", m.Matrix.Identity(4)), ("lid", m.FLIP_X),
                      ("roof", m.FLIP_X), ("crank", m.ROT_Y_UP),
                      ("link", m.ROT_Y_UP),
                      ("clip", m.Matrix.Rotation(math.radians(90), 4, "Y")),
                      ("speaker_clip", m.ROT_Y_UP))
        for key, mat in print_mats:
            printed[key] = m.copy_obj(parts[key], f"{key}_print")
            m.to_print(printed[key], mat)
        printed["pin"] = pin_print
        m.to_print(pin_print, m.Matrix.Identity(4))
        for key, ob in printed.items():
            report["parts"][key]["print_bbox"] = m.bbox(ob)
            m.save_stl([ob], os.path.join(m.BUILD, f"print_{key}.stl"))

        assembly = list(parts.values()) + list(refs.values())
        open_objects = [parts["box"], parts["roof"], parts["pin"], parts["clip"],
                        parts["speaker_clip"], refs["body"], refs["wire"], refs["speaker"],
                        opened["lid"], opened["crank"], opened["link"], horn_open]
        all_objects = set(assembly) | set(open_objects) | set(printed.values()) | {
            joint_b_test, joint_b_test_print, speaker_test,
        }
        m.scale_to_m(all_objects)
        m.export_stl(f"{m.NAME}-asm", only=assembly)
        m.export_stl(f"{m.NAME}-open", only=open_objects)
        for key, ob in printed.items():
            m.export_stl(f"{m.NAME}-{key}", only=[ob])
        with open(os.path.join(m.BUILD, "model_report.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print(json.dumps(report, ensure_ascii=False))

    m.main = main


def create_model(model_file):
    module = _load_c2_template(model_file)
    _patch_geometry(module)
    _install_main(module)
    return module
