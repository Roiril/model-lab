"""決定論的な数値校正と、古い組立証拠を合格表示しないことの回帰検査。"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import lattice_export as e


class PhysicsTests(unittest.TestCase):
    def test_known_solid_and_rotating_body(self):
        self.assertTrue(all(row["pass"] for row in e.calculation_calibration()))

    def test_translation_has_mass_but_no_rotational_energy(self):
        mass = e.physics.signed_tetra_properties(e.physics.box_triangles(), 1240)
        q = np.linspace(0, 1, 101)
        matrices = np.repeat(np.eye(4)[None], len(q), axis=0)
        matrices[:, 2, 3] = q * 12  # 12mm/rad
        result = e.rigid_properties(matrices, q, mass)
        np.testing.assert_allclose(result["inertia"], mass["massKg"] * .012**2, rtol=1e-10)
        np.testing.assert_allclose(result["gravity"], mass["massKg"] * e.limits.GRAVITY * .012, rtol=1e-10)

    def test_zero_motor_cannot_follow_known_gravity_load(self):
        tables = e.physics.synthetic_tables(gravity_nm=.01)
        result = e.physics.TableSim(tables).run(from_deg=0, to_deg=60, stall_scale=0)
        self.assertGreater(abs(result["final"]["servoDeg"] - 60), 1)

    def test_non_positive_inertia_rejected(self):
        mass = {"comM": [0, 0, 0], "massKg": 1, "inertiaComKgm2": [-1, 1, 1, 0, 0, 0]}
        with self.assertRaises(ValueError):
            e.rigid_properties(np.repeat(np.eye(4)[None], 3, axis=0), np.array([0, 1, 2]), mass)


class AssemblyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=e.BUILD, prefix="lattice-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.here = self.root / "models" / e.MODEL
        self.build = self.here / "build"
        self.case = self.here / "checks/front/build/assembly.json"
        self.step = {"id": "one", "title": "one", "instruction": "one", "moving": ["p"],
                     "checkText": "", "frames": [{"progress": 1, "transforms": {"p": np.eye(4).flatten(order="F").tolist()}}]}
        assembly = {"steps": [self.step], "pass": False, "calibration": {"pass": False}}
        e.write(self.case, assembly)
        e.write(self.build / "assembly.json", assembly)
        e.write(self.build / "cases.json", {"representative": "front"})
        self.evidence = {"fresh": True, "checks": {
            "assembly.path": {"pass": True, "detail": {"steps": [{"id": "one", "checkedPoses": 7, "pass": True}]}},
            "instrument.calibration": {"pass": True}}}

    def prepare(self, fresh=True):
        evidence = copy.deepcopy(self.evidence)
        evidence["fresh"] = fresh
        with patch.multiple(e, ROOT=self.root, HERE=self.here, BUILD=self.build), \
                patch.object(e, "dependency_status", return_value=(True, [])), \
                patch.object(e, "gate_evidence", return_value=evidence):
            changed = e.prepare_assembly()
        return changed, e.read(self.build / "assembly.json")

    def test_measured_counts_and_idempotence(self):
        changed, doc = self.prepare()
        self.assertTrue(changed)
        self.assertTrue(doc["pass"])
        self.assertEqual(doc["steps"][0]["report"]["samples"], 7)
        self.assertFalse(self.prepare()[0])

    def test_stale_gate_clears_pass_and_counts(self):
        self.prepare()
        _, doc = self.prepare(fresh=False)
        self.assertFalse(doc["pass"])
        self.assertFalse(doc["calibration"]["pass"])
        self.assertEqual(doc["steps"][0]["report"]["samples"], 0)

    def test_successful_different_path_cannot_be_reused(self):
        doc = e.read(self.case)
        doc["steps"][0]["frames"][0]["transforms"]["p"][12] = 10
        e.write(self.case, doc)
        _, output = self.prepare()
        self.assertFalse(output["pass"])


if __name__ == "__main__":
    unittest.main()
