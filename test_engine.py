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


from signal_processor import MovingAverageFilter

class TestSignalProcessingFilters(unittest.TestCase):
    def test_moving_average_smoothing(self):
        """Validates that transient physical noise spikes are effectively dampened by the filter window."""
        processor = MovingAverageFilter(window_size=3)
        
        # Step 1 & 2 establish a steady state baseline
        processor.filter_signal("DRAG", 100.0)
        processor.filter_signal("DRAG", 100.0)
        
        # Step 3 introduces an extreme momentary noise anomaly (e.g., sensor static)
        filtered_val = processor.filter_signal("DRAG", 400.0)
        
        # The mean of [100, 100, 400] is 200. The spike is effectively cut in half!
        self.assertEqual(filtered_val, 200.0)


from electro_optical_mechanical import ElectroOpticalMechanicalSystem

class TestElectroOpticalMechanicalSystem(unittest.TestCase):
    def test_eom_actuation_dynamics(self):
        """Validates that optical tracking adjustments trigger mechanical thermal changes and electrical power draw shifts."""
        eom = ElectroOpticalMechanicalSystem()
        
        # Slew the tracking sensor system
        eom.track_target(15.0, -5.0)
        
        # Verify multidisciplinary dependencies triggered successfully
        self.assertTrue(eom.target_locked)
        self.assertEqual(eom.current_draw_amps, 12.5)       # Electrical parameter change
        self.assertTrue(eom.motor_temperature_c > 25.0)     # Mechanical parameter change
        self.assertEqual(eom.check_system_health(), "PASSED: Electro-Optical Mechanical payload operational")


from security_gateway import SecurityGateway
from comms_link import CommsLinkTracker
from silo_pneumatics import SiloPneumaticsController

class TestExpandedSentinelSubsystems(unittest.TestCase):
    def test_cybersecurity_handshake_gating(self):
        gateway = SecurityGateway()
        # Should fail initially
        self.assertIn("REJECTED", gateway.authorize_command("LAUNCH"))
        # Should pass with valid token
        self.assertTrue(gateway.execute_handshake("SENTINEL_ALPHA_2026_SECURE"))
        self.assertIn("EXECUTED", gateway.authorize_command("LAUNCH"))

    def test_rf_comms_attenuation_and_blackout(self):
        comms = CommsLinkTracker()
        # Normal high alt flight
        self.assertIn("NOMINAL", comms.evaluate_link_stability(60000, 4.0))
        # Hypersonic plasma blackout criteria
        self.assertIn("CRITICAL FAULT", comms.evaluate_link_stability(120000, 15.0))
        self.assertTrue(comms.plasma_blackout_active)

    def test_silo_pneumatics_boundaries(self):
        pneumatics = SiloPneumaticsController()
        # Baseline launch ready check
        self.assertTrue(pneumatics.verify_launch_readiness())
        # Venting system should trigger a launch hold condition
        pneumatics.adjust_pressure("VENT_SAFETY")
        self.assertFalse(pneumatics.verify_launch_readiness())
        self.assertEqual(pneumatics.facility_status, "HOLD_REQUIRED")


from mission_executive import MissionExecutive

class TestIntegratedMissionExecutive(unittest.TestCase):
    def test_end_to_end_executive_execution(self):
        """Verifies that the Mission Executive smoothly transitions from ground checks to flight metrics processing."""
        exec_system = MissionExecutive()
        
        # Test Phase 1 verification loops run and pass flawlessly
        pre_launch_success = exec_system.run_pre_launch_sequence()
        self.assertTrue(pre_launch_success)
        self.assertTrue(exec_system.security.authenticated_session)
        
        # Trigger flight simulation step to confirm filter and comms integration
        exec_system.run_flight_simulation()
        
        # Assert that parameters across distinct modules updated during the integrated timeline run
        self.assertTrue(exec_system.filter.history["DRAG_SENSE"])
        self.assertTrue(exec_system.tps.value_properties["surface_temp_k"] > 300.0)

# --- THIS BLOCK INVOCATION IS REQUIRED TO RUN ALL CLASSES ABOVE ---
if __name__ == "__main__":
    unittest.main()
