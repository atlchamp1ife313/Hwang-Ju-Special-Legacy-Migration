import unittest
from engine import ReentryVehicle, GuidanceSystem, TPSBlock, StateMachine, Signal, LegacyDataImporter

class TestDigitalEngineeringFramework(unittest.TestCase):

    def setUp(self):
        self.rv = ReentryVehicle()
        self.gnc = GuidanceSystem()
        self.tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)
        self.rv_state_machine = StateMachine(block_context=self.rv, tps_context=self.tps)
        self.init_signal = Signal("Initialize Guidance")

        self.rv_state_machine.add_transition(
            from_state="EXOATMOSPHERIC_COAST",
            to_state="HYPERSONIC_REENTRY",
            condition=lambda structural, thermal: structural["aerodynamic_drag"] > 50000 and thermal["peak_heat_flux_mw"] > 1.0,
            signal_to_send=self.init_signal,
            target_subsystem=self.gnc
        )
        self.rv.attach_requirement("REQ-001", "GN&C system must initialize autonomously.")
        self.tps.attach_requirement("REQ-002", "TPS bondline must stay stable.")

    def test_initial_system_state(self):
        self.assertEqual(self.rv_state_machine.current_state, "EXOATMOSPHERIC_COAST")
        self.assertEqual(self.gnc.status, "DORMANT")
        self.assertEqual(self.tps.value_properties["surface_temp_k"], 300.0)

    def test_aerothermal_ablation_calculation(self):
        """Ensures high heat flux accurately scales surface temperatures and triggers ablative mass loss."""
        self.tps.set_property("peak_heat_flux_mw", 3.0)
        self.rv_state_machine.update()
        
        # 3.0 MW heat flux should push calculated surface temp past the 1200K ablation limit
        self.assertTrue(self.tps.value_properties["surface_temp_k"] > 1200.0)
        self.assertTrue(self.tps.value_properties["ablation_mass_loss_kg"] > 0.0)
from multidisciplinary_system import SystemInterfaceBus, StructuralBlock, ElectricalBlock, MechanicalBlock, SoftwareBlock

class TestMultidisciplinaryCascades(unittest.TestCase):
    def test_cross_domain_propagation(self):
        """Verifies that software adjustments trigger cascading changes in mechanical and electrical nodes."""
        bus = SystemInterfaceBus()
        structural = StructuralBlock(bus)
        electrical = ElectricalBlock(bus)
        mechanical = MechanicalBlock(bus)
        software = SoftwareBlock(bus)

        # Trigger software event
        software.update_parameter("commanded_tvc_gimbal_deg", 6.0, broadcast=True)

        # Assertions prove physical parameters updated across disconnected classes seamlessly
        self.assertTrue(mechanical.attributes["hydraulic_pressure_psi"] < 3000.0)
        self.assertTrue(electrical.attributes["current_draw_amps"] > 15.0)

if __name__ == "__main__":
    unittest.main()
