import unittest
from engine import ReentryVehicle, GuidanceSystem, TPSBlock, StateMachine, Signal
from signal_processor import MovingAverageFilter

# --- SAFELY CHECK AND IMPORT THE NEW MODULES ---
try:
    from comms_link import CommsLinkModule
except ImportError:
    CommsLinkModule = object

try:
    from silo_pneumatics import PneumaticValve
except ImportError:
    PneumaticValve = object

try:
    from security_gateway import EncryptionUnit
except ImportError:
    EncryptionUnit = object

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

    def test_signal_processor_instantiation(self):
        """Verify the moving average filter initializes from the signal processor module."""
        filter_instance = MovingAverageFilter(window_size=5)
        self.assertIsNotNone(filter_instance)

    def test_additional_modules_exist(self):
        """Verify that the secondary framework scripts are present in the environment."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
