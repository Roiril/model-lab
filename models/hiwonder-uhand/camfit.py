"""写真の目印点とモデル上の同じ点を対応させて、写真を撮ったカメラの位置・向き・焦点距離を逆算する。

py -3.11 models/hiwonder-uhand/camfit.py <view>

- 目印は points/<view>.json: {"size": [w, h], "mirror": bool, "points": [[name, [x,y,z] mm, [u,v] px], ...]}
  画素は左右反転した後の写真の座標（mirror=true のとき）
- 焦点距離を総当たりし、各焦点で solvePnP を解いて再投影誤差が最小のものを採る
- "ippe": 0 / 1 で、平面の目印から出る 2 つの姿勢のどちらかを選ぶ（板だけでは決まらない）
- 結果は points/<view>_cam.json（render_views.py がこれを読んで同じ画角で描く）
- 点ごとの残差を出す。残差が大きい点は、モデルのその部品の位置が写真と違う
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def solve(obj, img, w, h, f, alt=None):
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]], float)
    if alt is not None:
        # 目印が 1 平面に乗るとき、板の傾きを鏡に映した 2 つ目の姿勢がほぼ同じ誤差で解ける（IPPE の 2 解）。
        # alt で解の番号を選ぶ。どちらが正しいかは、平面の外にある部品（指・親指）を重ねて決める
        n, rvs, tvs, _ = cv2.solvePnPGeneric(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
        rv, tv = rvs[alt], tvs[alt]
        proj, _ = cv2.projectPoints(obj, rv, tv, K, None)
        res = np.linalg.norm(proj.reshape(-1, 2) - img, axis=1)
        return float(np.sqrt((res ** 2).mean())), rv, tv, K, res
    ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:
        return None
    ok, rv, tv = cv2.solvePnP(obj, img, K, None, rv, tv, True, cv2.SOLVEPNP_ITERATIVE)
    proj, _ = cv2.projectPoints(obj, rv, tv, K, None)
    res = np.linalg.norm(proj.reshape(-1, 2) - img, axis=1)
    return float(np.sqrt((res ** 2).mean())), rv, tv, K, res


def main():
    view = sys.argv[1]
    d = json.load(open(os.path.join(HERE, "points", f"{view}.json"), encoding="utf-8"))
    w, h = d["size"]
    names = [p[0] for p in d["points"]]
    obj = np.array([p[1] for p in d["points"]], float)
    img = np.array([p[2] for p in d["points"]], float)
    best = None
    fs = [d["f"]] if "f" in d else np.geomspace(300, 20000, 200)   # 目印が 1 平面に乗るときは焦点を固定する
    for f in fs:
        r = solve(obj, img, w, h, f, d.get("ippe"))
        if r and (best is None or r[0] < best[0][0]):
            best = (r, f)
    (rms, rv, tv, K, res), f = best
    R, _ = cv2.Rodrigues(rv)
    cam_pos = (-R.T @ tv).ravel()            # mm, ワールド座標
    # OpenCV のカメラ軸（x 右, y 下, z 前）をワールドへ
    right, down, fwd = R.T[:, 0], R.T[:, 1], R.T[:, 2]
    out = dict(view=view, size=[w, h], f_px=f, rms_px=rms, pos=cam_pos.tolist(),
               right=right.tolist(), down=down.tolist(), fwd=fwd.tolist(), mirror=d.get("mirror", False))
    json.dump(out, open(os.path.join(HERE, "points", f"{view}_cam.json"), "w", encoding="utf-8"), indent=1)
    print(f"{view}: f={f:.0f}px  rms={rms:.1f}px  cam=({cam_pos[0]:.0f},{cam_pos[1]:.0f},{cam_pos[2]:.0f})mm "
          f"dist={np.linalg.norm(cam_pos):.0f}")
    for n, r_ in sorted(zip(names, res), key=lambda t: -t[1]):
        print(f"  {n:24s} {r_:6.1f}px")


main()
