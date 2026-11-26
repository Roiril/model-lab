# -*- coding: utf-8 -*-
"""uHand と駒の場面を組む（Blender 内で import して使う）。カメラは持たない。

手の向き: 模型の +Z（指）を世界の +X、-Y（手のひら）を -Z、+X（親指側）を +Y に置き、
  そこへ pitch（指先を下げる向きが正、度）と roll（親指側を上げる向きが正、度）を掛ける。
床: 手の最下点の CLEAR 下を z = 0 にする。
駒: 中心 (cx, cy) を、親指の先と人差し指の先の両方に接するように解く（place_ghost）。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ML, "models", "hiwonder-uhand"))

import bpy
import numpy as np
from mathutils import Matrix

import anim_build as AB
import kin

# 絵のためだけに、4 本の指を開いた姿勢（量 0）より先、甲の側へ反らせられるようにする（-0.4 まで連結が解ける）。
# 実物のサーボがここまで反らせるかは確かめていない。模型の定義（kin.py）は変えず、この道具の中だけで広げる
FINGER_LO = -0.3
for _f in kin.FINGERS:
    _lo, _hi, _rest = kin.DOFS[_f]
    kin.DOFS[_f] = (FINGER_LO, _hi, _rest)

# 親指の基節と末節を別々の角度で曲げられるようにする（実物は 1 つのサーボで両方が連動する）。
# dofs に thumb_prox_deg / thumb_tip_deg を入れると、量 thumb の代わりにその角度 [deg] を使う。
# 基節を小さくすると親指が手のひらから離れて後ろへ反り、末節を大きくすると先が内へ曲がる
_THUMB = {"prox": None, "tip": None}
_thumb_pose_orig = kin.thumb_pose


def _thumb_pose(u):
    if _THUMB["prox"] is None:
        return _thumb_pose_orig(u)
    e1, e2, n, o = kin.thumb_frame()
    q = kin.thumb_points()
    Wp = kin.rot_axis(n, math.radians(_THUMB["prox"]), q["pivot"])
    Wt = kin.mul(Wp, kin.rot_axis(n, math.radians(_THUMB["tip"]), q["joint"]))
    strut = kin.apply(Wp, q["strut"])
    L = kin.vlen(kin.vsub(q["strut"], q["horn_tip"]))
    gamma = kin.horn_angle(q["shaft"], q["horn_tip"], strut, L, "thumb: 押し棒（角度指定） ")
    Wh = kin.rot_axis((0, 1, 0), gamma, q["shaft"])
    tip = kin.apply(Wh, q["horn_tip"])
    Wrod = kin.aim(q["horn_tip"], tip, kin.vsub(q["strut"], q["horn_tip"]), kin.vsub(strut, tip))
    ct = kin.apply(Wp, q["crank_t"])
    d0, d1 = kin.vsub(q["crank_t"], q["crank_f"]), kin.vsub(ct, q["crank_f"])
    Wc = kin.aim(q["crank_f"], q["crank_f"], d0, d1, kin.vlen(d1) / kin.vlen(d0))
    return {"thumb_prox": Wp, "thumb_tip": Wt, "thumb_horn": Wh, "thumb_pushrod": Wrod, "thumb_crank": Wc}, \
        dict(horn=gamma, crank_stretch=kin.vlen(d1) / kin.vlen(d0))


kin.thumb_pose = _thumb_pose

GHOST = os.path.join(ML, "exports", "geister-ghost", "ghost_blue.glb")
CLEAR = 0.001
R0 = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=float)


def rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
            "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]


def hand_rot(pitch, roll):
    return rot("y", pitch) @ rot("x", -roll) @ R0


def fingers(index, curl_step, little=None):
    """人差し指の量から、中指・薬指・小指を少しずつ浅くする（参照の扇）。

    little を渡すと、人差し指から小指までを直線で補間する（小指は負にして甲の側へ反らせてよい）。"""
    if little is not None:
        return {nm: index + (little - index) * k / 3 for k, nm in enumerate(("index", "middle", "ring", "little"))}
    return {"index": index, "middle": max(0.0, index - curl_step), "ring": max(0.0, index - 2 * curl_step),
            "little": max(0.0, index - 3 * curl_step)}


class Scene:
    def __init__(self):
        self.arm, self.rest = AB.rig()
        self.uh = [o for o in bpy.data.objects if o.name.startswith("uh_")]
        self.local = {o.name: np.array([v.co[:] for v in o.data.vertices]) for o in self.uh}
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=GHOST)
        new = [o for o in bpy.data.objects if o not in before]
        self.ghost = bpy.data.objects.new("ghost", None)
        bpy.context.scene.collection.objects.link(self.ghost)
        for r in [o for o in new if o.parent is None]:
            r.parent = self.ghost
        self.gm = [o for o in new if o.type == "MESH"]
        bpy.context.view_layer.update()
        gv = np.array([(o.matrix_world @ v.co)[:] for o in self.gm for v in o.data.vertices])
        gmin, gmax = gv.min(axis=0), gv.max(axis=0)
        gc = (gmin + gmax) / 2
        self.ghost_base = Matrix.Translation((-gc[0], -gc[1], -gmin[2]))
        self.ghost_h = float(gmax[2] - gmin[2])
        # 高さごとの半径（1mm 刻み。軸からの最大距離）
        rel = gv - np.array([gc[0], gc[1], gmin[2]])
        rr = np.hypot(rel[:, 0], rel[:, 1])
        nb = int(math.ceil(self.ghost_h * 1000)) + 1
        self.prof = np.zeros(nb)
        idx = np.clip((rel[:, 2] * 1000).astype(int), 0, nb - 1)
        np.maximum.at(self.prof, idx, rr)
        self.prof = self._smooth(self.prof)
        self.cx = self.cy = 0.0

    @staticmethod
    def _smooth(p):
        q = p.copy()
        for i in range(len(p)):
            q[i] = p[max(0, i - 1):i + 2].max()
        return q

    def r_at(self, z):
        """高さ z [m] での駒の半径 [m]。駒の高さの外は 0。"""
        i = np.clip((np.asarray(z) * 1000).astype(int), 0, len(self.prof) - 1)
        r = self.prof[i]
        return np.where((np.asarray(z) < 0) | (np.asarray(z) > self.ghost_h), 0.0, r)

    def set_hand(self, dofs, pitch, roll):
        self.dofs, self.pitch, self.roll = dict(dofs), pitch, roll
        self.arm.matrix_world = Matrix.Identity(4)
        _THUMB["prox"], _THUMB["tip"] = dofs.get("thumb_prox_deg"), dofs.get("thumb_tip_deg")
        if (_THUMB["prox"] is None) != (_THUMB["tip"] is None):
            raise ValueError("thumb_prox_deg と thumb_tip_deg は両方そろえて渡す")
        AB.apply_pose(self.arm, self.rest, dofs)
        bpy.context.view_layer.update()
        R = Matrix(hand_rot(pitch, roll).tolist()).to_4x4()
        self.verts = {}
        zmin = 1e9
        for o in self.uh:
            M = np.array(R @ o.matrix_world)
            v = self.local[o.name] @ M[:3, :3].T + M[:3, 3]
            self.verts[o.name] = v
            zmin = min(zmin, float(v[:, 2].min()))
        shift = -zmin + CLEAR
        for v in self.verts.values():
            v[:, 2] += shift
        self.arm.matrix_world = Matrix.Translation((0, 0, shift)) @ R
        bpy.context.view_layer.update()
        self.lowest = min(self.verts, key=lambda k: self.verts[k][:, 2].min())

    def clearances(self, c, near=None):
        """駒の中心 c (x, y) に対する、部品ごとの最小の隙間 [m]（負は食い込み）と、その点の高さ。

        near を渡すと、その部分集合（_near で作る）だけを見る。"""
        out = {}
        for k, (vv, rz) in (near or self._near(c, 1.0)).items():
            d = np.hypot(vv[:, 0] - c[0], vv[:, 1] - c[1]) - rz
            i = int(np.argmin(d))
            out[k] = (float(d[i]), float(vv[i, 2]))
        return out

    def _near(self, c, reach):
        """駒の高さ以下で、c から reach [m] 以内の点。部品ごとに (点, その高さの駒の半径)。"""
        out = {}
        for k, v in self.verts.items():
            m = (v[:, 2] <= self.ghost_h) & (np.hypot(v[:, 0] - c[0], v[:, 1] - c[1]) <= reach)
            if m.any():
                out[k] = (v[m], self.r_at(v[m][:, 2]))
        return out

    def place_ghost(self, touch=("uh_thumb_tip", "uh_index_tip")):
        """touch の部品すべてに接し、ほかに食い込まない中心を探す。(中心, 隙間の辞書, 目的値)。"""
        tips = [self.verts[k] for k in touch]
        c0 = np.mean([t[np.argmin(t[:, 2])][:2] for t in tips], axis=0)
        near = self._near(c0, 0.06)
        if any(k not in near for k in touch):
            return c0, {}, 1e18

        def f(c):
            cl = self.clearances(c, near)
            pen = sum(min(0.0, v[0]) ** 2 for v in cl.values()) * 1e7
            return sum((cl[k][0] * 1000) ** 2 for k in touch) + pen

        best = (None, 1e18)
        for ang in range(0, 360, 45):
            c = c0 + 0.012 * np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
            c, v = nm2(f, c, 0.004, 60)
            if v < best[1]:
                best = (c, v)
        c, v = nm2(f, best[0], 0.001, 80)
        self.cx, self.cy = float(c[0]), float(c[1])
        return c, self.clearances(c), v

    def put_ghost(self, cam_pos=None, yaw=None):
        """駒を (cx, cy) に立てる。目のある面（取り込んだ姿勢で +Y）を cam_pos の水平の向きへ。"""
        if yaw is None:
            yaw = 0.0 if cam_pos is None else math.atan2(-(cam_pos[0] - self.cx), cam_pos[1] - self.cy)
        self.ghost.matrix_world = Matrix.Translation((self.cx, self.cy, 0)) @ Matrix.Rotation(yaw, 4, "Z") @ self.ghost_base
        bpy.context.view_layer.update()

    def visibility(self, dirs, n_pts=300):
        """駒の中心 (cx, cy) に立てた駒が、各向き dirs（駒からカメラへの単位ベクトル、平行光で近似）から
        どれだけ見えるか。カメラ側を向く駒の表面の点から光線を飛ばし、手に当たらない割合。"""
        from mathutils import Vector
        from mathutils.bvhtree import BVHTree
        vs, faces, off = [], [], 0
        for k, v in self.verts.items():
            me = bpy.data.objects[k].data
            vs.extend(map(tuple, v))
            faces.extend(tuple(i + off for i in p.vertices) for p in me.polygons)
            off += len(v)
        tree = BVHTree.FromPolygons(vs, faces)
        if not hasattr(self, "_gpts"):
            pts, nrm = [], []
            for o in self.gm:
                me = o.data
                for p in me.polygons:
                    pts.append(p.center[:])
                    nrm.append(p.normal[:])
            pts, nrm = np.array(pts), np.array(nrm)
            sel = np.random.default_rng(0).choice(len(pts), min(n_pts, len(pts)), replace=False)
            self._gpts, self._gnrm = pts[sel], nrm[sel]
        # 取り込んだ駒の点（世界の原点付近）を、立てた位置へ。向きは軸まわりなので見えの判定には効かない
        bm = np.array(self.ghost_base)
        p = self._gpts @ bm[:3, :3].T + bm[:3, 3] + np.array([self.cx, self.cy, 0])
        n = self._gnrm @ bm[:3, :3].T
        out = []
        for d in dirs:
            d = np.asarray(d, float)
            front = (n @ d) > 0.15
            if not front.any():
                out.append(0.0)
                continue
            seen = 0
            for q in p[front]:
                hit = tree.ray_cast(Vector(q + d * 0.0005), Vector(d), 2.0)
                seen += hit[0] is None
            out.append(seen / int(front.sum()))
        return out

    def tip(self, name):
        v = self.verts[name]
        return v[np.argmin(v[:, 2])]


def nm2(f, x0, step, iters):
    sim = [np.array(x0, float), np.array(x0, float) + [step, 0], np.array(x0, float) + [0, step]]
    val = [f(s) for s in sim]
    for _ in range(iters):
        o = np.argsort(val)
        sim, val = [sim[i] for i in o], [val[i] for i in o]
        c = (sim[0] + sim[1]) / 2
        xr = c + (c - sim[2])
        fr = f(xr)
        if fr < val[0]:
            xe = c + 2 * (c - sim[2])
            fe = f(xe)
            sim[2], val[2] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < val[1]:
            sim[2], val[2] = xr, fr
        else:
            xc = c + 0.5 * (sim[2] - c)
            fc = f(xc)
            if fc < val[2]:
                sim[2], val[2] = xc, fc
            else:
                sim = [sim[0], sim[0] + 0.5 * (sim[1] - sim[0]), sim[0] + 0.5 * (sim[2] - sim[0])]
                val = [val[0], f(sim[1]), f(sim[2])]
    i = int(np.argmin(val))
    return sim[i], val[i]
