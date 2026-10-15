import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = Path(__file__).resolve().parent
BUILD_DIR = MODEL_DIR / "build"
DEFAULT_OUTPUT = ROOT / "prints" / "flag-box" / "preview.html"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_mesh(path):
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError(f"STL is too short: {path}")
    count = struct.unpack_from("<I", raw, 80)[0]
    expected = 84 + 50 * count
    if len(raw) != expected:
        raise ValueError(f"STL size mismatch: {path} ({len(raw)} != {expected})")

    vertices = []
    triangles = []
    indices = {}
    for index in range(count):
        xyz = struct.unpack_from("<9f", raw, 96 + index * 50)
        face = []
        for vertex_index in range(3):
            start = vertex_index * 3
            point = tuple(round(value, 5) for value in xyz[start:start + 3])
            if point not in indices:
                indices[point] = len(vertices) // 3
                vertices.extend(point)
            face.append(indices[point])
        triangles.extend(face)
    return {"vertices": vertices, "triangles": triangles}


def manual_checks(report):
    items = []
    for requirement in report.get("requirements", []):
        for text in requirement.get("manual", []):
            if text not in items:
                items.append(text)
    return items


def build_data(output):
    manifest = load_json(BUILD_DIR / "manifest.json")
    motion = load_json(BUILD_DIR / "motion.json")
    assembly = load_json(BUILD_DIR / "assembly.json")
    gate = load_json(BUILD_DIR / "gate_report.json")

    parts = []
    for part in manifest["parts"]:
        mesh_path = MODEL_DIR / part["assembly"]
        parts.append({
            "id": part["id"],
            "label": part["label"],
            "color": part["color"],
            "exterior": part["id"] in manifest["meta"].get("exterior_parts", []),
            "mesh": read_mesh(mesh_path),
        })

    gcode = output.parent / "flag-box-PLA.gcode.3mf"
    return {
        "meta": manifest["meta"],
        "parts": parts,
        "motion": motion,
        "assembly": assembly,
        "gate": {
            "generatedAt": gate.get("generatedAt"),
            "checks": gate.get("checks", []),
            "manual": manual_checks(gate),
        },
        "gcode": {
            "name": gcode.name,
            "exists": gcode.is_file(),
            "bytes": gcode.stat().st_size if gcode.is_file() else None,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="flag-box の単一ファイル確認ページを作る")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()

    template_path = MODEL_DIR / "preview_template.html"
    template = template_path.read_text(encoding="utf-8")
    if template.count("__DATA__") != 1:
        raise ValueError("preview_template.html must contain exactly one __DATA__ marker")

    data = json.dumps(build_data(output), ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</script", "<\\/script")
    html = template.replace("__DATA__", data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {output}")
    print(f"size {output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
