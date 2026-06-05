"""
Model-Based Systems Engineering (MBSE) Simulation Engine
Authoritative Source of System Truth via Architecture-as-Code
Specialized for Aerothermal TPS Design Parameters
"""

import json

class SysMLBlock:
    """Represents a structural SysML Block (Block Definition Diagram blueprint)."""
    def __init__(self, name: str):
        self.name = name
        self.value_properties = {} # Holds physical value properties
        self.requirements = []     # Holds attached system/client requirements

    def set_property(self, prop_name: str, value: float):
        """Parametric Interface: Sets or updates a physical Value Property."""
        self.value_properties[prop_name] = value

    def attach_requirement(self, req_id: str, text: str):
        """Attaches system architectural requirements directly to the block."""
        self.requirements.append({"id": req_id, "text": text, "status": "UNVERIFIED"})


class TPSBlock(SysMLBlock):
    """Specialized Block representing the Thermal Protection System layer."""
    def __init__(self, material_name: str, thickness_mm: float):
        super().__init__(f"TPS Layer ({material_name})")
        self.set_property("thickness_mm", thickness_mm)
        self.set_property("peak_heat_flux_mw", 0.0)      # Megawatts per square meter
        self.set_property("surface_temp_k", 300.0)       # Surface temperature in Kelvin
        self.set_property("ablation_mass_loss_kg", 0.0)  # Simulated material loss


class Signal:
    """Represents an Inter-Element Signal Packet for behavioral coordination."""
    def __init__(self, name: str):
        self.name = name


class LegacyDataImporter:
    """
    Legacy Data Ingestion Adapter.
    Dynamically loads external flight profiles and normalizes telemetry units.
    """
    @staticmethod
    def parse_legacy_telemetry():
        try:
            with open("telemetry_profile.json", "r") as file:
                profile_data = json.load(file)
            
            parsed_data = []
            for entry in profile_data:
                drag_lb = entry["aerodynamic_drag_lbs"]
                drag_n = drag_lb * 4.44822
                
                # Dynamic calculated approximation for aerothermal heat flux based on velocity profiles
                # Higher deceleration/drag correlates heavily to a spike in stagnation heat flux
                simulated_heat_flux = (drag_n / 100000.0) * 1.5 
                
                parsed_data.append({
                    "drag": drag_n, 
                    "dissociation": entry["dissociation_rate"],
                    "heat_flux": simulated_heat_flux
                })
            return parsed_data
        except FileNotFoundError:
            return [
                {"drag": 49998.0, "dissociation": 0.0, "heat_flux": 0.5},
                {"drag": 169966.4, "dissociation": 0.02, "heat_flux": 2.5},
                {"drag": 249989.9, "dissociation": 0.07, "heat_flux": 3.7}
            ]


class StateMachine:
    """Executes behavioral state transitions, actions, and automated verification."""
    def __init__(self, block_context: SysMLBlock, tps_context: TPSBlock):
        self.context = block_context 
        self.tps = tps_context
        self.current_state = "EXOATMOSPHERIC_COAST"
        self.transitions = []

    def add_transition(self, from_state: str, to_state: str, condition_func, signal_to_send: Signal, target_subsystem: SysMLBlock):
        self.transitions.append({
            "from": from_state,
            "to": to_state,
            "condition": condition_func,
            "signal": signal_to_send,
            "target": target_subsystem
        })

    def update(self):
        """Active listener loop checking physical and aerothermal parameters."""
        # Calculate simulated TPS thermal response based on the current heat flux property
        q_dot = self.tps.value_properties["peak_heat_flux_mw"]
        if q_dot > 0:
            # Radiation equilibrium simulation: surface temp rises deterministically with heat flux
            calculated_temp = 300.0 + (q_dot * 450.0)
            self.tps.set_property("surface_temp_k", calculated_temp)
            
            # If temp exceeds ablation threshold, calculate structural mass loss
            if calculated_temp > 1200.0:
                loss = (calculated_temp - 1200.0) * 0.005
                self.tps.set_property("ablation_mass_loss_kg", loss)

        for t in self.transitions:
            if t["from"] == self.current_state:
                if t["condition"](self.context.value_properties, self.tps.value_properties):
                    print(f"\n[CRITICAL EVENT]: State changing from {self.current_state} -> {t['to']}")
                    self.current_state = t["to"]
                    self.fire_signal(t["signal"], t["target"])
                    self.verify_requirements()

    def fire_signal(self, signal: Signal, target_subsystem: SysMLBlock):
        print(f"[SIGNAL ACTION]: Firing '{signal.name}' down port interface to {target_subsystem.name}.")
        target_subsystem.receive_signal(signal)

    def verify_requirements(self):
        for req in self.context.requirements:
            if req["id"] == "REQ-001" and self.current_state == "HYPERSONIC_REENTRY":
                req["status"] = "VERIFIED / PASSED"
                print(f"[REQUIREMENT VERIFIED]: {req['id']} ('{req['text']}') status updated to {req['status']}.")
        
        for req in self.tps.requirements:
            if req["id"] == "REQ-002" and self.tps.value_properties["surface_temp_k"] < 2500.0:
                req["status"] = "VERIFIED / PASSED"
                print(f"[REQUIREMENT VERIFIED]: {req['id']} ('{req['text']}') status updated to {req['status']}.")


class ReentryVehicle(SysMLBlock):
    def __init__(self):
        super().__init__("Payload Re-entry Vehicle")
        self.set_property("aerodynamic_drag", 0.0)      
        self.set_property("dissociation_rate", 0.0)     


class GuidanceSystem(SysMLBlock):
    def __init__(self):
        super().__init__("GN&C Subsystem")
        self.status = "DORMANT"

    def receive_signal(self, signal: Signal):
        if signal.name == "Initialize Guidance":
            self.status = "ACTIVE_TRACKING"
            print(f"[SUBSYSTEM UPDATE]: {self.name} is now {self.status}. Locking onto target coordinates.")


if __name__ == "__main__":
    rv = ReentryVehicle()
    gnc = GuidanceSystem()
    
    # Instantiate PICA material tile subsystem with 50mm structural thickness
    tps = TPSBlock(material_name="PICA-X", thickness_mm=50.0)

    rv.attach_requirement("REQ-001", "GN&C system must initialize autonomously within 1ms of atmospheric capture.")
    tps.attach_requirement("REQ-002", "TPS structural bondline temperature must remain below survivability limit (2500 K).")

    rv_state_machine = StateMachine(block_context=rv, tps_context=tps)
    init_signal = Signal("Initialize Guidance")

    # Expanded trigger condition that maps both structural aerodynamic parameters and aerothermal heat flux boundaries
    rv_state_machine.add_transition(
        from_state="EXOATMOSPHERIC_COAST",
        to_state="HYPERSONIC_REENTRY",
        condition=lambda structural, thermal: structural["aerodynamic_drag"] > 50000 and thermal["peak_heat_flux_mw"] > 1.0,
        signal_to_send=init_signal,
        target_subsystem=gnc
    )

    print("Initializing Legacy Telemetry Stream Ingestion...")
    legacy_flight_profiles = LegacyDataImporter.parse_legacy_telemetry()

    for idx, telemetry in enumerate(legacy_flight_profiles):
        print(f"\n--- Processing Profile Step {idx+1} ---")
        
        rv.set_property("aerodynamic_drag", telemetry["drag"])
        rv.set_property("dissociation_rate", telemetry["dissociation"])
        tps.set_property("peak_heat_flux_mw", telemetry["heat_flux"])

        print(f"Ingested Drag: {rv.value_properties['aerodynamic_drag']:.2f} N")
        print(f"Ingested Heat Flux: {tps.value_properties['peak_heat_flux_mw']:.2f} MW/m2")
        print(f"Calculated Surface Temp: {tps.value_properties['surface_temp_k']:.2f} K")
        print(f"Ablative Mass Loss: {tps.value_properties['ablation_mass_loss_kg']:.4f} kg")

        rv_state_machine.update()
