import json
import os
import struct
import sys
import tempfile
import unittest
import zipfile
from unittest import mock


sys.path.insert(0, os.path.dirname(__file__))
import studio_plate  # noqa: E402


def write_fixture(path, parts, unit="millimeter", components=False, external=False,
                  duplicate_build=False):
    objects = []
    build = []
    config = []
    for object_id, label, vertices, triangles, transform in parts:
        if components:
            body = f'<components><component objectid="{object_id}"/></components>'
        else:
            vertex_xml = "".join(
                f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in vertices)
            triangle_xml = "".join(
                f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in triangles)
            body = f'<mesh><vertices>{vertex_xml}</vertices><triangles>{triangle_xml}</triangles></mesh>'
        objects.append(f'<object id="{object_id}" type="model">{body}</object>')
        transform_attr = f' transform="{transform}"' if transform is not None else ""
        build.append(f'<item objectid="{object_id}"{transform_attr}/>')
        if duplicate_build:
            build.append(f'<item objectid="{object_id}"{transform_attr}/>')
        config.append(
            f'<object id="{object_id}"><metadata key="name" value="{label}"/>'
            f'<part id="{object_id}" subtype="normal_part">'
            f'<metadata key="name" value="{label}"/></part></object>')
    model = (f'<?xml version="1.0"?><model xmlns="{studio_plate.CORE_NS}" unit="{unit}">'
             f'<resources>{"".join(objects)}</resources><build>{"".join(build)}</build></model>')
    rel = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           '<Relationship Target="https://example.invalid/model.model" TargetMode="External" '
           'Id="r1" Type="model"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("3D/3dmodel.model", model)
        archive.writestr("Metadata/model_settings.config", f'<config>{"".join(config)}</config>')
        if external:
            archive.writestr("_rels/.rels", rel)


def stl_points(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    count = struct.unpack("<I", raw[80:84])[0]
    points = []
    for index in range(count):
        offset = 84 + index * 50 + 12
        coords = struct.unpack("<9f", raw[offset:offset + 36])
        points.extend([coords[0:3], coords[3:6], coords[6:9]])
    return points


def point_bbox(points):
    return ([min(point[axis] for point in points) for axis in range(3)],
            [max(point[axis] for point in points) for axis in range(3)])


class StudioPlateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_exports = studio_plate.EXPORTS
        self.old_plates = studio_plate.PLATES
        studio_plate.EXPORTS = os.path.join(self.temp.name, "exports")
        studio_plate.PLATES = os.path.join(self.temp.name, "plates")
        os.makedirs(studio_plate.EXPORTS)
        os.makedirs(studio_plate.PLATES)

    def tearDown(self):
        studio_plate.EXPORTS = self.old_exports
        studio_plate.PLATES = self.old_plates
        self.temp.cleanup()

    def source(self, label, vertices, triangles):
        path = os.path.join(studio_plate.EXPORTS, label + ".stl")
        data, _points = studio_plate._binary_stl(vertices, triangles)
        with open(path, "wb") as fh:
            fh.write(data)

    def test_applies_asymmetric_rotation_and_translation(self):
        label = "demo-wedge"
        vertices = [(1, 2, 3), (4, 2, 3), (1, 5, 3)]
        triangles = [(0, 1, 2)]
        self.source(label, vertices, triangles)
        path = os.path.join(studio_plate.EXPORTS, "layout.3mf")
        transform = "0 1 0 -1 0 0 0 0 1 10 20 30"
        write_fixture(path, [("7", label, vertices, triangles, transform)])
        manifest = studio_plate.export_studio_plate("demo", path)
        points = stl_points(os.path.join(studio_plate.EXPORTS, manifest["parts"][0]["file"]))
        self.assertEqual(points, [(8.0, 21.0, 33.0), (8.0, 24.0, 33.0), (5.0, 21.0, 33.0)])
        self.assertEqual(manifest["parts"][0]["objectId"], "7")
        self.assertEqual(manifest["parts"][0]["buildTransform"], [float(x) for x in transform.split()])

    def test_exports_multiple_parts(self):
        path = os.path.join(studio_plate.EXPORTS, "layout.3mf")
        triangle = ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)])
        self.source("demo-a", *triangle)
        rotated_vertices = [(-y, x, z) for x, y, z in triangle[0]]
        self.source("demo-b", rotated_vertices, triangle[1])
        write_fixture(path, [
            ("2", "demo-a", *triangle, None),
            ("9", "demo-b", *triangle, "1 0 0 0 1 0 0 0 1 4 5 6"),
        ])
        manifest = studio_plate.export_studio_plate("demo", path, bed=(300, 320))
        self.assertEqual([part["objectId"] for part in manifest["parts"]], ["2", "9"])
        self.assertEqual(manifest["bed"], {"width": 300, "depth": 320})
        self.assertTrue(all(os.path.isfile(os.path.join(studio_plate.EXPORTS, part["file"]))
                            for part in manifest["parts"]))

    def test_rejects_unsupported_features(self):
        triangle = ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)])
        cases = [
            ("unit", {"unit": "inch"}, "unit"),
            ("components", {"components": True}, "components"),
            ("external", {"external": True}, "external"),
            ("duplicate", {"duplicate_build": True}, "multiple build"),
        ]
        for name, options, message in cases:
            with self.subTest(name=name):
                path = os.path.join(studio_plate.EXPORTS, name + ".3mf")
                write_fixture(path, [("1", "demo-a", *triangle, None)], **options)
                with self.assertRaisesRegex(ValueError, message):
                    studio_plate.export_studio_plate("demo", path)

    def test_failure_keeps_old_manifest(self):
        manifest_path = os.path.join(studio_plate.PLATES, "demo.json")
        with open(manifest_path, "wb") as fh:
            fh.write(b"old manifest\n")
        path = os.path.join(studio_plate.EXPORTS, "layout.3mf")
        mesh = ([(0, 0, 0), (2, 0, 0), (0, 2, 0), (1, 1, 0)],
                [(0, 1, 3), (0, 3, 2)])
        source = ([(0, 0, 0), (2, 0, 0), (0, 2, 0), (1.2, 0.8, 0)],
                  [(0, 1, 3), (0, 3, 2)])
        self.source("demo-stale", *source)
        write_fixture(path, [("1", "demo-stale", *mesh, None)])
        with self.assertRaisesRegex(ValueError, "geometry does not match"):
            studio_plate.export_studio_plate("demo", path)
        with open(manifest_path, "rb") as fh:
            self.assertEqual(fh.read(), b"old manifest\n")
        self.assertFalse(any(name.endswith(".tmp") for name in os.listdir(studio_plate.PLATES)))

    def test_identical_reexport_does_not_replace_files(self):
        label = "demo-static"
        triangle = ([(0, 0, 0), (2, 0, 0), (0, 3, 0)], [(0, 1, 2)])
        self.source(label, *triangle)
        path = os.path.join(studio_plate.EXPORTS, "layout.3mf")
        write_fixture(path, [("4", label, *triangle, None)])
        first = studio_plate.export_studio_plate("demo", path)
        output_path = os.path.join(studio_plate.EXPORTS, first["parts"][0]["file"])
        manifest_path = os.path.join(studio_plate.PLATES, "demo.json")
        mtimes = (os.stat(output_path).st_mtime_ns, os.stat(manifest_path).st_mtime_ns)

        with mock.patch.object(studio_plate.os, "replace",
                               side_effect=AssertionError("同一ファイルを置換した")):
            second = studio_plate.export_studio_plate("demo", path)

        self.assertEqual(second, first)
        self.assertEqual((os.stat(output_path).st_mtime_ns, os.stat(manifest_path).st_mtime_ns),
                         mtimes)


class ActualPlateTest(unittest.TestCase):
    def test_c1_and_c2_parts_and_bboxes(self):
        expected = {"mystery-box-sg92r-c1": 7, "mystery-box-sg92r-c2": 8}
        for model, count in expected.items():
            with self.subTest(model=model):
                source = os.path.join(studio_plate.ROOT, "exports", model + "-plate.3mf")
                manifest = studio_plate.export_studio_plate(model, source)
                self.assertEqual(len(manifest["parts"]), count)
                _raw, _labels, objects, items = studio_plate._parse_3mf(source)
                transforms = dict(items)
                for part in manifest["parts"]:
                    transformed = [studio_plate._transform_vertex(vertex, transforms[part["objectId"]])
                                   for vertex in objects[part["objectId"]][0]]
                    expected_bbox = point_bbox(transformed)
                    actual_bbox = point_bbox(stl_points(os.path.join(studio_plate.EXPORTS,
                                                                      part["file"])))
                    for actual_axis, expected_axis in zip(actual_bbox, expected_bbox):
                        for actual_value, expected_value in zip(actual_axis, expected_axis):
                            self.assertAlmostEqual(actual_value, expected_value, places=4)
                    self.assertEqual(actual_bbox, (part["bbox"]["min"], part["bbox"]["max"]))


if __name__ == "__main__":
    unittest.main()
