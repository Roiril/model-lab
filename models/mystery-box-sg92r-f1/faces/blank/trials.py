"""Real geometry copies and cut-downs for mount clearance trials."""
import bpy

from .geometry import boolean, primitive


def build(parts, interface, common_params):
    result = {}
    for key, bounds in (("key_l", None), ("panel", {"type": "box", "size_mm": [40,30,12], "center_mm": [-27,-17,4]})):
        source = parts[key]["object"] if isinstance(parts[key], dict) else parts[key]
        obj = source.copy()
        obj.data = source.data.copy()
        bpy.context.collection.objects.link(obj)
        obj.name = f"mount_trial_{key}"
        if bounds is not None:
            boolean(obj, primitive(bounds, "trial_bounds"), "INTERSECT")
        result[f"mount_{key}"] = obj
    return result
