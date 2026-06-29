# -*- coding: utf-8 -*-
"""
海底探検コンポーネントの GLB ビルダー（Blender 5.1 / bpy）。
gen_textures.py が出力した outlines.json と tex/*.png を読み、
UV 付きの薄板メッシュ（宝物/裏トークン/空気/ボード）・ソリッドのミープル・
ラウンドキューブのサイコロを生成し、

  - 各ピース単体 GLB   exports/deep-sea/glb/<name>.glb   （Unity 取り込み用）
  - 全部入りシーン GLB  exports/deep-sea/deep-sea-adventure.glb （俯瞰／ギャラリー用）

を書き出す。テクスチャは GLB に埋め込む。
"""
import bpy, bmesh, json, os, math, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "deep-sea"))
TEX  = os.path.join(OUT, "tex")
GLB  = os.path.join(OUT, "glb")
os.makedirs(GLB, exist_ok=True)

with open(os.path.join(OUT, "outlines.json"), encoding="utf-8") as f:
    MAN = json.load(f)

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for d in list(blk):
            blk.remove(d)

def srgb_to_lin(c):
    c = c/255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def solid_mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    r,g,b = [srgb_to_lin(x) for x in rgba[:3]]
    bsdf.inputs["Base Color"].default_value = (r,g,b,1.0)
    bsdf.inputs["Roughness"].default_value = 0.62
    bsdf.inputs["Metallic"].default_value = 0.0
    return m

def tex_mat(name, png):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Metallic"].default_value = 0.0
    tx = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(os.path.join(TEX, png))
    tx.image = img
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    return m

def make_tile(name, info):
    """outline を押し出した薄板。textured ならトップ面にテクスチャ、側面/裏はソリッド。"""
    outline = info["outline"]
    size = info["size_mm"] * 0.001
    th   = info["thick_mm"] * 0.001
    v2d = [(x*size, y*size) for x,y in outline]

    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)

    bm = bmesh.new()
    top = [bm.verts.new((x,y, th)) for x,y in v2d]
    bot = [bm.verts.new((x,y, 0.0)) for x,y in v2d]
    bm.verts.ensure_lookup_table()
    f_top = bm.faces.new(top)
    f_bot = bm.faces.new(list(reversed(bot)))
    n = len(v2d)
    sides = []
    for i in range(n):
        j = (i+1) % n
        sides.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    has_back = info["textured"] and info.get("back_tex")
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        flip = (f is f_bot and has_back)   # 裏面は U 反転（裏から見て正像）
        for loop in f.loops:
            co = loop.vert.co
            # Blender UV は下原点。テクスチャは PIL で上原点に描いているので
            # model+y(=画像上) を v=1 に対応させる（= 0.5 + y）。
            u = (0.5 - co.x/size) if flip else (co.x/size + 0.5)
            loop[uvl].uv = (u, 0.5 + co.y/size)

    # マテリアル割り当て: トップ=0, 側面=1, 裏=2(あれば)
    if info["textured"]:
        ob.data.materials.append(tex_mat(name+"_top", info["tex"]))
        ob.data.materials.append(solid_mat(name+"_side", info["side_color"]))
        f_top.material_index = 0
        for s in sides: s.material_index = 1
        if has_back:
            ob.data.materials.append(tex_mat(name+"_back", info["back_tex"]))
            f_bot.material_index = 2
        else:
            f_bot.material_index = 1
    else:
        ob.data.materials.append(solid_mat(name+"_mat", info["color"]))

    bm.to_mesh(me)
    bm.free()
    # スムーズシェード（側面の丸み表現）+ Auto Smooth
    for p in me.polygons: p.use_smooth = True
    return ob

def make_die(info):
    size = info["size_mm"] * 0.001
    bpy.ops.mesh.primitive_cube_add(size=size)
    ob = bpy.context.active_object
    ob.name = "die"
    # 角を丸める
    bev = ob.modifiers.new("bevel", "BEVEL")
    bev.width = size*0.08; bev.segments = 4
    bpy.ops.object.modifier_apply(modifier="bevel")
    me = ob.data
    # 面ごとに材質（1..6）。法線方向で振り分け。
    faces_map = {  # 法線軸 -> 目
        ( 1,0,0):1, (-1,0,0):6, (0,1,0):2, (0,-1,0):5, (0,0,1):3, (0,0,-1):4,
    }
    mats = {}
    for n in range(1,7):
        mats[n] = tex_mat(f"die_{n}", f"die_{n}.png")
        me.materials.append(mats[n])
    matidx = {n:i for i,n in enumerate(range(1,7))}
    # UV 展開（各面を 0..1 に）
    me.uv_layers.new(name="UVMap")
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nx,ny,nz = f.normal
        key = (round(nx),round(ny),round(nz))
        pip = faces_map.get(key)
        if pip is None:   # ベベル面: 木材色（目1の材質を流用しても良いが木目のみ）
            f.material_index = matidx[1]
            continue
        f.material_index = matidx[pip]
        # 面ローカル軸で平面 UV
        if abs(nz) > 0.5:
            for loop in f.loops:
                co = loop.vert.co
                loop[uvl].uv = (co.x/size+0.5, co.y/size+0.5)
        elif abs(nx) > 0.5:
            for loop in f.loops:
                co = loop.vert.co
                loop[uvl].uv = (co.y/size+0.5, co.z/size+0.5)
        else:
            for loop in f.loops:
                co = loop.vert.co
                loop[uvl].uv = (co.x/size+0.5, co.z/size+0.5)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob.location = (0,0,size/2)
    return ob

def export_single(ob, name):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    # 原点をオブジェクト中心へ寄せて単体は原点配置
    loc = ob.location.copy()
    ob.location = (0,0,0)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(GLB, name+".glb"),
        export_format="GLB", use_selection=True,
        export_apply=True, export_yup=True,
    )
    ob.location = loc

# ----------------------------------------------------------------- ビルド
clear()
objs = {}
for name, info in MAN.items():
    t = info["type"]
    if t == "die":
        objs[name] = make_die(info)
    else:
        objs[name] = make_tile(name, info)

# 単体 GLB（位置リセットして書き出し）
for name, ob in objs.items():
    export_single(ob, name)

# ----------------------------------------------------------------- 俯瞰レイアウト
def place(name, x, y, rot_z=0.0):
    ob = objs[name]
    ob.location = (x, y, 0.0)
    ob.rotation_euler = (0,0,rot_z)

# 実物写真の配置に合わせつつ、全体を中央寄りにコンパクト化
G  = 0.046          # チップ間隔
RX = 0.205          # 右グループの開始x（左グループとの間を詰める）
# 行A: ボード（左・大）/ 空気マーカー / 裏トークン5
place("submarine_board", 0.01, 0.205)
place("air_marker", 0.145, 0.235)
for col,n in enumerate(["back_circle","back_tri","back_square","back_pentagon","back_hexagon"]):
    place(n, RX + col*G, 0.215)
# 行B: 五角 8-11 / 六角 12-15
for col,v in enumerate(range(8,12)):  place(f"pen_{v}", 0.0 + col*G, 0.085)
for col,v in enumerate(range(12,16)): place(f"hex_{v}", RX + col*G, 0.085)
# 行C: 三角 0 / 三角 1-3 / 四角 4-7
place("tri_0", 0.0, -0.04)
for col,v in enumerate(range(1,4)):   place(f"tri_{v}", 0.062 + col*G, -0.04)
for col,v in enumerate(range(4,8)):   place(f"sq_{v}",  RX + col*G, -0.04)
# 行D: ミープル2 / サイコロ
place("meeple_purple", 0.03, -0.15)
place("meeple_red",    0.085, -0.15)
objs["die"].location = (0.145, -0.15, info["size_mm"]*0.0005)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "deep-sea-adventure.glb"),
    export_format="GLB", use_selection=True,
    export_apply=True, export_yup=True,
)

print("DONE: pieces=%d  glb_dir=%s" % (len(objs), GLB))
