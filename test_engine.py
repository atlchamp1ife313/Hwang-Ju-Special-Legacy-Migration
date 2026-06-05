import unittest
from engine import ReentryVehicle, GuidanceSystem, TPSBlock

class TestBaselineSentinel(unittest.TestCase):

    def test_vehicle_instantiation(self):
        """Verify core aerospace blocks initialize without syntax or type errors."""
        rv = ReentryVehicle()
        gnc = GuidanceSystem()
        tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)
        
        self.assertIsNotNone(rv)
        self.assertEqual(gnc.status, "DORMANT")
        self.assertEqual(tps.value_properties["surface_temp_k"], 300.0)

if __name__ == "__main__":
    unittest.main()
