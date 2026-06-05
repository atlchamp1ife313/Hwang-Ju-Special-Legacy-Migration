import unittest
from engine import ReentryVehicle, GuidanceSystem, TPSBlock, StateMachine, Signal

class TestDigitalEngineeringFramework(unittest.TestCase):

    def setUp(self):
        """Set up fresh system configurations before every individual test."""
        self.rv = ReentryVehicle()
        self.gnc = GuidanceSystem()
        self.tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)
        self.rv_state_machine = StateMachine(block_context=self.rv, tps_context=self.tps)
        self.init_signal = Signal("Initialize Guidance")
        
        # Attach formal engineering specifications
        self.rv.attach_requirement("REQ-001", "GN&C system must initialize autonomously upon atmospheric entry.")
        self.tps.attach_requirement("REQ-002", "TPS structural bondline temperature must remain stable.")

    def test_initial_system_state(self):
        """Verify subsystems initialize to safe, nominal default states."""
        self.assertEqual(self.rv_state_machine.current_state, "EXOATMOSPHERIC_COAST")
        self.assertEqual(self.gnc.status, "DORMANT")
        self.assertEqual(self.tps.value_properties["surface_temp_k"], 300.0)

    def test_properties_and_requirements(self):
        """Verify property assignment and baseline requirements structure."""
        self.rv.set_property("aerodynamic_drag", 60000.0)
        self.tps.set_property("peak_heat_flux_mw", 2.0)
        
        self.assertEqual(self.rv.value_properties["aerodynamic_drag"], 60000.0)
        self.assertEqual(self.tps.value_properties["peak_heat_flux_mw"], 2.0)
        self.assertTrue(len(self.rv.requirements) > 0)

if __name__ == "__main__":
    unittest.main()
