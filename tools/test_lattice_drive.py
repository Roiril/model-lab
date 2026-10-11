"""Deterministic geometry-meter tests for lattice_drive.py."""
from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lattice_drive as drive


def involute_gear(teeth=30, module=1.0, pressure_deg=20.0, phase=0.0):
    """Return an extruded, zero-backlash involute gear as STL triangles in mm."""
    pitch = module * teeth / 2
    base = pitch * math.cos(math.radians(pressure_deg))
    root, tip = pitch - 1.25 * module, pitch + module
    pressure = math.radians(pressure_deg)
    pitch_involute = math.tan(pressure) - pressure

    def involute(r):
        alpha = math.acos(base / r)
        return math.tan(alpha) - alpha

    flank_radii = np.linspace(base, tip, 9)
    half = lambda r: math.pi / (2 * teeth) + pitch_involute - involute(r)
    half_base, half_tip = half(base), half(tip)
    points = []
    tooth_pitch = 2 * math.pi / teeth
    for index in range(teeth):
        center = phase + index * tooth_pitch
        points.extend((root * math.cos(a), root * math.sin(a)) for a in np.linspace(
            center - tooth_pitch / 2, center - half_base, 3, endpoint=False))
        points.append((root * math.cos(center - half_base), root * math.sin(center - half_base)))
        points.extend((r * math.cos(center - half(r)), r * math.sin(center - half(r)))
                      for r in flank_radii)
        points.extend((tip * math.cos(a), tip * math.sin(a))
                      for a in np.linspace(center - half_tip, center + half_tip, 4)[1:])
        points.extend((r * math.cos(center + half(r)), r * math.sin(center + half(r)))
                      for r in flank_radii[-2::-1])
        points.append((root * math.cos(center + half_base), root * math.sin(center + half_base)))
        points.extend((root * math.cos(a), root * math.sin(a)) for a in np.linspace(
            center + half_base, center + tooth_pitch / 2, 3)[1:])

    polygon = np.asarray(points)
    triangles = []
    for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
        a0, b0 = np.array((0.0, *a)), np.array((0.0, *b))
        a1, b1 = np.array((4.0, *a)), np.array((4.0, *b))
        triangles.extend(((a0, b0, b1), (a0, b1, a1)))
    return np.asarray(triangles)


class SliceAndContactTest(unittest.TestCase):
    def test_surface_meter_accepts_retriangulation_and_skinny_faces_rejects_missing_and_shifted(self):
        calibration = drive.canonical_surface_calibration()
        self.assertTrue(calibration['pass'], calibration)
        detail = calibration['detail']
        self.assertLess(detail['sameSurfaceRetriangulatedDistanceMm'], 1e-10)
        self.assertGreater(detail['missingFaceDistanceMm'], .2)
        self.assertAlmostEqual(detail['shiftedSurfaceDistanceMm'], .5)
        self.assertLess(detail['skinnyIdenticalDistanceMm'], 1e-10)
        self.assertAlmostEqual(detail['skinnyShiftedDistanceMm'], .02)

    def test_rear_surface_contact_separation_penetration_and_missing_support(self):
        cube = drive.cube_triangles()
        for shift, expected in [(1, 0), (1.01, .01), (.99, -.01)]:
            measured = drive.rear_surface_measure(cube + np.array([shift, 0, 0]), cube)
            self.assertTrue(measured['complete'])
            self.assertAlmostEqual(measured['minimumGapMm'], expected)
        self.assertFalse(drive.rear_surface_measure(cube + np.array([1, 2, 0]), cube)['complete'])

    def test_blind_floor_rejects_thin_connected_material(self):
        witnesses = np.array([[.25, .25], [.5, .5], [.75, .75]])
        cube = drive.cube_triangles()
        positive = drive.blind_floor_measure(cube * np.array([1.25, 1, 1]), witnesses, 0, 1.25)
        negative = drive.blind_floor_measure(cube * np.array([.15, 1, 1]), witnesses, 0, 1.25)
        self.assertTrue(positive['pass'])
        self.assertEqual(positive['minimumAxialThicknessMm'], 1.25)
        self.assertFalse(negative['pass'])

    def test_common_rotation_preserves_axial_relative_pose(self):
        keys = {drive.relative_pose_key(angle, (0, 53.7), (.13, 0, 0), angle, (0, 53.7))
                for angle in np.linspace(0, 160, 65)}
        self.assertEqual(len(keys), 1)
        self.assertNotEqual(drive.relative_pose_key(0, (0, 53.7), (.13, 0, 0), 0, (0, 53.7)),
                            drive.relative_pose_key(10, (0, 53.7), (.13, 0, 0), 0, (0, 53.7)))

    def test_missing_face_is_detected_when_vertices_remain(self):
        cube = drive.cube_triangles()
        missing = cube[1:]
        self.assertTrue(np.array_equal(np.unique(cube.reshape(-1, 3), axis=0),
                                      np.unique(missing.reshape(-1, 3), axis=0)))
        self.assertAlmostEqual(drive.unique_surface_area(cube), 6.0)
        self.assertAlmostEqual(drive.unique_surface_area(missing), 5.5)
        self.assertAlmostEqual(drive.unique_surface_area(np.concatenate((cube, cube))), 6.0)

    def test_axial_ray_records_material_faces_and_clear_miss(self):
        self.assertEqual(drive.ray_x_surfaces(drive.cube_triangles(), (.5, .5)), [0.0, 1.0])
        self.assertEqual(drive.ray_x_surfaces(drive.cube_triangles(), (2, .5)), [])

    def setUp(self):
        self.square = drive.polygon_edges([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        inner = drive.polygon_edges([(-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)])
        outer = drive.polygon_edges([(-3, -3), (3, -3), (3, 3), (-3, 3)])
        self.socket = np.concatenate((inner, outer))
        circle = drive.polygon_edges([(1.5 * math.cos(i * 2 * math.pi / 360),
                                       1.5 * math.sin(i * 2 * math.pi / 360)) for i in range(360)])
        self.round_socket = np.concatenate((circle, outer))

    def test_cube_slice_at_half_has_complete_boundary(self):
        section = drive.slice_x(drive.cube_triangles(), 0.5)
        self.assertEqual(len(section), 8)
        self.assertTrue(np.allclose(section.reshape(-1, 2).min(axis=0), (0, 0)))
        self.assertTrue(np.allclose(section.reshape(-1, 2).max(axis=0), (1, 1)))

    def test_annular_socket_inside_and_contact_angle(self):
        self.assertFalse(drive.intersects(self.square, self.socket))
        self.assertEqual(drive.inside(np.array([[0, 0], [2, 0]]), self.socket).tolist(), [False, True])
        angle = drive.contact_angle(self.square, self.socket, (0, 0), 1, 30)
        self.assertAlmostEqual(angle, 13.0519405687, places=4)

    def test_round_and_missing_shapes_do_not_claim_contact(self):
        self.assertIsNone(drive.contact_angle(self.square, self.round_socket, (0, 0), 1, 180))
        missing = np.empty((0, 2, 2))
        self.assertIsNone(drive.contact_angle(missing, self.socket, (0, 0), 1, 30))
        report = drive.interface_rotation(np.empty((0, 3, 3)), drive.cube_triangles(),
                                          0.5, (0, 0), 'missing', 'missing')
        self.assertEqual(report['status'], 'fail')


class InvoluteGearMeterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = SimpleNamespace(
            GEAR_X=.002, DRIVE_GEAR_X0=0.0, GEAR_MODULE=.001, GEAR_TEETH=30,
            GEAR_PRESSURE_DEG=20.0, GEAR_THICK=.004, SERVO_AXIS_Z=0.0,
            CAM_AXIS_Z=.030, SERVO_HOME_DEG=0.0, SERVO_END_DEG=0.0)
        pitch = 2 * math.pi / cls.params.GEAR_TEETH
        cls.driver = involute_gear(phase=math.pi / 2)
        cls.follower = involute_gear(phase=-math.pi / 2 + pitch / 2) + np.array((0, 0, 30))

    def report(self, driver=None, follower=None):
        return drive.gear_report({'drive_gear': self.driver if driver is None else driver,
                                  'cam_gear': self.follower if follower is None else follower}, self.params)

    def test_nominal_involute_pair_has_two_sided_contact(self):
        report = self.report()
        self.assertEqual(report['status'], 'pass', report)
        self.assertEqual(report['actualTeeth'], [30, 30])
        self.assertTrue(all(value is not None for value in report['samples'][0]['contactAnglesDeg']))

    def test_missing_overlap_and_phase_faults_fail(self):
        center = (0, 30)
        faults = {
            'missing': np.empty((0, 3, 3)),
            'axialshift': self.driver + np.array((6, 0, 0)),
        }
        for name, altered in faults.items():
            with self.subTest(name=name):
                self.assertEqual(self.report(driver=altered)['status'], 'fail')
        self.assertEqual(self.report(follower=self.follower + np.array((0, 0, 10)))['status'], 'fail')
        half_phase = drive.transform_triangles(self.follower, 180 / 30, center)
        self.assertEqual(self.report(follower=half_phase)['status'], 'fail')


if __name__ == '__main__':
    unittest.main(verbosity=2)
