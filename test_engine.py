import unittest
from engine import ReentryVehicle, GuidanceSystem, TPSBlock, StateMachine, Signal

class TestDigitalEngineeringFramework(unittest.TestCase):

    def setUp(self):
        """Set up a fresh system configuration before every individual test."""
        self.rv = ReentryVehicle()
        self.gnc = GuidanceSystem()
        self.tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)
        self.rv_state_machine = StateMachine(block_context=self.rv, tps_context=self.tps)
        self.init_signal = Signal("Initialize Guidance")

        # Establish a valid system state transition rule
        self.rv_state_machine.add_transition(
            from_state="EXOATMOSPHERIC_COAST",
            to_state="HYPERSONIC_REENTRY",
            condition=lambda structural, thermal: structural["aerodynamic_drag"] > 50000 and thermal["peak_heat_flux_mw"] > 1.0,
            signal_to_send=self.init_signal,
            target_subsystem=self.gnc
        )
        
        # Attach formal engineering specifications
        self.rv.attach_requirement("REQ-001", "GN&C system must initialize autonomously upon atmospheric entry.")
        self.tps.attach_requirement("REQ-002", "TPS structural bondline temperature must remain stable.")

    def test_initial_system_state(self):
        """Verify subsystems initialize to safe, nominal default states."""
        self.assertEqual(self.rv_state_machine.current_state, "EXOATMOSPHERIC_COAST")
        self.assertEqual(self.gnc.status, "DORMANT")
        self.assertEqual(self.tps.value_properties["surface_temp_k"], 300.0)
        self.assertEqual(self.rv.requirements[0]["status"], "VERIFICATION_PENDING")

    def test_state_transition_and_signal_dispatch(self):
        """Verify that meeting flight thresholds triggers state change and subsystem activation."""
        # Inject flight data that satisfies the condition rule
        self.rv.set_property("aerodynamic_drag", 60000.0)
        self.tps.set_property("peak_heat_flux_mw", 2.0)
        
        # Process the state engine update step
        self.rv_state_machine.update()
        
        # System state should update and activate the guidance system block
        self.assertEqual(self.rv_state_machine.current_state, "HYPERSONIC_REENTRY")
        self.assertEqual(self.gnc.status, "ACTIVE")
        
        # Requirements should automatically flip to VERIFIED based on block state changes
        self.assertEqual(self.rv.requirements[0]["status"], "VERIFIED")
        self.assertEqual(self.tps.requirements[0]["status"], "VERIFIED")

    def test_aerothermal_ablation_calculation(self):
        """Ensures extreme heat flux accurately scales surface temperatures and triggers mass loss."""
        self.tps.set_property("peak_heat_flux_mw", 3.5)
        self.rv_state_machine.update()
        
        # High heat flux must step up surface temp past the ablation threshold (1200K)
        self.assertTrue(self.tps.value_properties["surface_temp_k"] > 1200.0)
        self.assertTrue(self.tps.value_properties["ablation_mass_loss_kg"] > 0.0)

if __name__ == "__main__":
    unittest.main()
