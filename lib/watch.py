"""
Run inside Blender (Scripting tab → open this file → Run Script).

Watches the built STL in exports/ and reloads it when it changes.
The actual build is done externally (Claude runs ./run.sh).

Edit MODEL below to switch which model to watch.
"""
import bpy
import os

# --- edit this to switch models ---
MODEL = "chessboard"
# ----------------------------------

_BASE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.normpath(os.path.join(_BASE, "..", "exports", MODEL + ".stl"))

POLL_SEC = 0.5
_state = {"mtime": 0.0}


def _clear():
    # Delete all objects in the current scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    # Purge orphan meshes so they don't accumulate
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)


def _reload():
    print(f"[watch] reloading {STL}")
    try:
        _clear()
        bpy.ops.wm.stl_import(filepath=STL)
        print("[watch] ok")
    except Exception:
        import traceback
        print("[watch] FAILED:")
        traceback.print_exc()


def _tick():
    if not os.path.exists(STL):
        return POLL_SEC
    m = os.path.getmtime(STL)
    if m != _state["mtime"]:
        _state["mtime"] = m
        _reload()
    return POLL_SEC


if os.path.exists(STL):
    _state["mtime"] = os.path.getmtime(STL)
    _reload()
bpy.app.timers.register(_tick, persistent=True)
print(f"[watch] watching {STL}")
