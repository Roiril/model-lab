"""回転遊びの位相包絡計器を校正する。"""
from __future__ import annotations

import math
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lattice_simulation as simulation


def interface(identifier, reverse, forward):
    return {
        "id": identifier,
        "status": "pass",
        "contactAnglesDeg": [reverse, forward],
    }


class PhaseEnvelopeCalibrationTest(unittest.TestCase):
    def test_periodic_extrema_include_internal_peak(self):
        sine = simulation.periodic_trig_range("sin", 80.0, 100.0)
        cosine = simulation.periodic_trig_range("cos", -10.0, 10.0)
        self.assertAlmostEqual(sine[1], 1.0)
        self.assertAlmostEqual(sine[0], math.sin(math.radians(80.0)))
        self.assertAlmostEqual(cosine[1], 1.0)
        self.assertAlmostEqual(cosine[0], math.cos(math.radians(10.0)))

    def test_c4_measured_chain_reaches_90_degree_peak(self):
        params = SimpleNamespace(
            SERVO_MIN_DEG=10.0,
            SERVO_MAX_DEG=170.0,
            CAM_THETA_MIN_DEG=-80.0,
            CAM_E=(0.003, 0.002, 0.001),
        )
        low = math.sin(math.radians(params.CAM_THETA_MIN_DEG))
        motion = SimpleNamespace(
            cam_theta_deg=lambda servo: servo - 90.0,
            lift_m=lambda group, servo: params.CAM_E[group]
            * (math.sin(math.radians(servo - 90.0)) - low),
        )
        report = {"interfaces": [
            interface("horn-receiver", 0.487359, 0.487329),
            interface("coupler-shaft", 9.750476, 9.750476),
            interface("shaft-cam_center", 6.083568, 6.083568),
            interface("shaft-cam_inner", 6.083558, 6.083549),
            interface("shaft-cam_outer", 6.083568, 6.083547),
        ]}
        envelope = simulation.clearance_envelope(
            "mystery-box-sg92r-c4", params, motion, report)
        center = envelope["summary"]["groups"][0]
        self.assertAlmostEqual(center["maximumPhaseDifferenceDeg"], 16.321403)
        self.assertEqual(len(envelope["groups"][0]["samples"]), 65)
        self.assertLessEqual(max(
            b["servoDeg"] - a["servoDeg"]
            for a, b in zip(envelope["groups"][0]["samples"],
                            envelope["groups"][0]["samples"][1:])), 2.5)
        self.assertAlmostEqual(center["end"]["nominalHeightMm"], 5.90884651807)
        self.assertAlmostEqual(center["end"]["heightRangeMm"][1], 5.95442325904)
        self.assertEqual(center["start"]["heightRangeMm"][0], 0.0)

    def test_c3_uses_largest_gear_pose_and_each_cam_contact(self):
        params = SimpleNamespace(
            SERVO_HOME_DEG=15.0,
            SERVO_END_DEG=165.0,
            CAM_HOME_DEG=-5.0,
            CAM_PHASE_DEG=(145.0, 105.0),
            CAM_E=0.005,
            GRID_N=2,
        )
        cam_theta = lambda servo: params.CAM_HOME_DEG + servo - params.SERVO_HOME_DEG

        def carrier_height(group, servo):
            angle = math.radians(cam_theta(servo) - params.CAM_PHASE_DEG[group])
            return max(0.0, params.CAM_E * (math.cos(angle) - 0.4))

        motion = SimpleNamespace(cam_theta_deg=cam_theta, carrier_height=carrier_height)
        gear = {"id": "gear-mesh", "status": "pass", "samples": [
            {"servoDeg": 15.0, "contactAnglesDeg": [1.0, 1.1]},
            {"servoDeg": 17.5, "contactAnglesDeg": [1.2, 0.9]},
        ]}
        report = {"interfaces": [
            interface("horn-receiver", 0.5, 0.4),
            gear,
            interface("shaft-cam_gear", 2.0, 1.9),
            interface("shaft-cam_0", 3.0, 2.8),
            interface("shaft-cam_1", 4.0, 3.8),
        ]}
        envelope = simulation.clearance_envelope(
            "mystery-box-sg92r-c3", params, motion, report)
        self.assertEqual(
            [group["maximumPhaseDifferenceDeg"] for group in envelope["groups"]],
            [6.7, 7.7],
        )
        self.assertEqual(len(envelope["groups"][0]["samples"]), 61)
        self.assertEqual(
            [source["id"] for source in envelope["groups"][0]["sources"]],
            ["horn-receiver", "gear-mesh", "shaft-cam_gear", "shaft-cam_0"],
        )

    def test_missing_contact_measurement_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "contact angles are missing"):
            simulation.maximum_contact_angle({
                "id": "horn-receiver", "status": "pass", "contactAnglesDeg": [None, None],
            })


if __name__ == "__main__":
    unittest.main(verbosity=2)
