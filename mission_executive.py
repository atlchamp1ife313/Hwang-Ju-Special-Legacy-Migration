"""
LGM-35A Sentinel Program - Integrated Mission Assurance Executive
Orchestrates and executes cross-functional multi-domain simulation timelines.
"""

from security_gateway import SecurityGateway
from comms_link import CommsLinkTracker
from silo_pneumatics import SiloPneumaticsController
from electro_optical_mechanical import ElectroOpticalMechanicalSystem
from signal_processor import MovingAverageFilter
from engine import ReentryVehicle, StateMachine, TPSBlock, Signal, GuidanceSystem

class MissionExecutive:
    """Centralized flight computer orchestrating all hardware/software domain nodes."""
    def __init__(self):
        print("[EXECUTIVE]: Initializing Master System-of-Systems Domain Cluster...")
        self.security = SecurityGateway()
        self.comms = CommsLinkTracker()
        self.pneumatics = SiloPneumaticsController()
        self.eo_payload = ElectroOpticalMechanicalSystem()
        self.filter = MovingAverageFilter(window_size=2)
        
        # Core Flight Vehicle Units
        self.rv = ReentryVehicle()
        self.gnc = GuidanceSystem()
        self.tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)
        self.state_machine = StateMachine(block_context=self.rv, tps_context=self.tps)
        
        # Attach initial state conditions
        self.state_machine.add_transition(
            from_state="EXOATMOSPHERIC_COAST",
            to_state="HYPERSONIC_REENTRY",
            condition=lambda structural, thermal: structural["aerodynamic_drag"] > 50000 and thermal["peak_heat_flux_mw"] > 1.0,
            signal_to_send=Signal("Initialize Guidance"),
            target_subsystem=self.gnc
        )

    def run_pre_launch_sequence(self) -> bool:
        """Phase 1: Ground Segment & Cybersecurity Readiness Verification."""
        print("\n=== PHASE 1: PRE-LAUNCH COMPLIANCE CHECK ===")
        
        # 1. Check ground facility pneumatics
        if not self.pneumatics.verify_launch_readiness():
            print("[EXECUTIVE FAULT]: Silo pneumatic loop unstable. Aborting.")
            return False
        print("[EXECUTIVE INFO]: Ground segment pneumatic pressure within safety boundaries.")

        # 2. Authenticate secure command datalink
        secure_token = "SENTINEL_ALPHA_2026_SECURE"
        if not self.security.execute_handshake(secure_token):
            print("[EXECUTIVE FAULT]: Cyber authentication matrix failed. Aborting.")
            return False
            
        print("[EXECUTIVE SUCCESS]: Pre-launch checks passed. Silo umbilical separation cleared.")
        return True

    def run_flight_simulation(self):
        """Phase 2: Dynamic atmospheric flight handling signal processing, telemetry, and tracking."""
        print("\n=== PHASE 2: ACTIVE FLIGHT METRICS STREAM ===")
        
        # Mock telemetry steps representing raw noisy sensors during atmospheric capture
        flight_steps = [
            {"raw_drag": 45000.0, "alt": 140000.0, "mach": 4.0,  "t_az": 0.0,  "t_el": 0.0},
            {"raw_drag": 120000.0, "alt": 95000.0,  "mach": 14.5, "t_az": 12.5, "t_el": 4.2}, # Blackout & High Heat Step
            {"raw_drag": 55000.0,  "alt": 45000.0,  "mach": 3.2,  "t_az": 45.2, "t_el": 12.8}
        ]
        
        for step_idx, data in enumerate(flight_steps):
            print(f"\n--- Simulation Step {step_idx + 1} (Alt: {data['alt']} ft) ---")
            
            # Filter sensory noise using our digital moving window filter
            smooth_drag = self.filter.filter_signal("DRAG_SENSE", data["raw_drag"])
            print(f"[DATA FILTER]: Raw Drag Sensor: {data['raw_drag']} N -> Processed: {smooth_drag:.1f} N")
            
            # Map structural/aerothermal inputs dynamically
            self.rv.set_property("aerodynamic_drag", smooth_drag)
            sim_heat_flux = (smooth_drag / 100000.0) * 1.5
            self.tps.set_property("peak_heat_flux_mw", sim_heat_flux)
            
            # Check RF Comms link margin stability
            comms_status = self.comms.evaluate_link_stability(data["alt"], data["mach"])
            print(f"[COMMS LAYER]: {comms_status}")
            
            # Process terminal target tracking commands via electro-optical gimbals
            if data["t_az"] > 0.0:
                self.eo_payload.track_target(data["t_az"], data["t_el"])
                print(f"[PAYLOAD HEALTH]: {self.eo_payload.check_system_health()}")
                
            # Update core state machine tracking
            self.state_machine.update()


if __name__ == "__main__":
    executive = MissionExecutive()
    if executive.run_pre_launch_sequence():
        executive.run_flight_simulation()
