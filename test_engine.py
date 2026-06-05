"""
Automated Unit Testing & Verification Suite
Validates the Architectural Pipeline, Logic Gates, and State Constraints
"""

import unittest
from engine import ReentryVehicle, GuidanceSystem, StateMachine, Signal, LegacyDataImporter

class TestDigitalEngineeringFramework(unittest.TestCase):

    def setUp(self):
        """Initializes system architecture baseline before each test execution."""
        self.rv = ReentryVehicle()
        self.gnc = GuidanceSystem()
        self.rv_state_machine = StateMachine(block_context=self.rv)
        self.init_signal = Signal("Initialize Guidance")

        # Bind the standard physical threshold logic gate
        self.rv_state_machine.add_transition(
            from_state="EXOATMOSPHERIC_COAST",
            to_state="HYPERSONIC_REENTRY",
            condition=lambda props: props["aerodynamic_drag"] > 50000 and props["dissociation_rate"] > 0.05,
            signal_to_send=self.init_signal,
            target_subsystem=self.gnc
        )
        self.rv.attach_requirement("REQ-001", "GN&C system must initialize autonomously.")

    def test_initial_system_state(self):
        """Validates that system blocks initialize in their nominal, unexcited states."""
        self.assertEqual(self.rv_state_machine.current_state, "EXOATMOSPHERIC_COAST")
        self.assertEqual(self.gnc.status, "DORMANT")
        self.assertEqual(self.rv.requirements[0]["status"], "UNVERIFIED")

    def test_sub_threshold_handling(self):
        """Ensures state machine ignores telemetry that fails to breach physical thresholds."""
        # High drag, but zero molecular dissociation (e.g., dense cold atmosphere simulation)
        self.rv.set_property("aerodynamic_drag", 60000.0)
        self.rv.set_property("dissociation_rate", 0.01)
        
        self.rv_state_machine.update()
        
        # System should remain dormant
        self.assertEqual(self.rv_state_machine.current_state, "EXOATMOSPHERIC_COAST")
        self.assertEqual(self.gnc.status, "DORMANT")

    def test_deterministic_boundary_breach(self):
        """Validates immediate state transition and cascading subsystem wake-up upon threshold breach."""
        # Explicitly force properties past the tripwire gates
        self.rv.set_property("aerodynamic_drag", 55000.0)
        self.rv.set_property("dissociation_rate", 0.06)
        
        self.rv_state_machine.update()
        
        # Verify that state machine flipped, signal was sent, and requirement passed automatically
        self.assertEqual(self.rv_state_machine.current_state, "HYPERSONIC_REENTRY")
        self.assertEqual(self.gnc.status, "ACTIVE_TRACKING")
        self.assertEqual(self.rv.requirements[0]["status"], "VERIFIED / PASSED")

    def test_legacy_data_normalization(self):
        """Validates that the legacy ingestion adapter parses and converts units accurately."""
        parsed_steps = LegacyDataImporter.parse_legacy_telemetry()
        
        # Ensure the parser caught all 3 steps from the mock telemetry file
        self.assertEqual(len(parsed_steps), 3)
        
        # Validate unit conversion math for Step 1: 11240 lbs * 4.44822 = 50001.99 N
        self.assertAlmostEqual(parsed_steps[0]["drag"], 50001.99, places=1)


if __name__ == "__main__":
    print("Executing Automated Architectural Verification Suite...\n")
    unittest.main()
