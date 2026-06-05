"""
LGM-35A Sentinel Program - Advanced Multidisciplinary Systems Engineering (MSE) Framework
Implements Dynamic Interface Control Document (ICD) Cascading Dependencies.
"""

class SystemInterfaceBus:
    """Centralized System Bus representing physical and logical interfaces between domains (ICD)."""
    def __init__(self):
        self.registry = {}

    def register_domain(self, name: str, block):
        self.registry[name] = block

    def propagate_change(self, source_domain: str, parameter: str, value: float):
        """Dynamic Change Propagation Matrix mapping cross-discipline physics coupling."""
        # 1. Software to Mechanical Coupling
        if source_domain == "Software" and parameter == "commanded_tvc_gimbal_deg":
            mechanical = self.registry.get("Mechanical")
            if mechanical:
                # Moving mechanical parts increases hydraulic demand
                new_pressure = 3000.0 - (abs(value) * 25.0)
                mechanical.update_parameter("hydraulic_pressure_psi", new_pressure)
                
                # 2. Mechanical to Electrical Coupling (Cascade)
                electrical = self.registry.get("Electrical")
                if electrical:
                    # Hydraulic valves demanding more power spikes the avionics bus current draw
                    new_current = 15.0 + (abs(value) * 4.5)
                    electrical.update_parameter("current_draw_amps", new_current)

        # 3. Structural to Mechanical Coupling
        if source_domain == "Structural" and parameter == "current_aerodynamic_load_n":
            mechanical = self.registry.get("Mechanical")
            if mechanical and value > 200000.0:
                # Extreme structural wind sheer forcing active adjustments degrades hydraulic pressure reserves
                current_press = mechanical.attributes.get("hydraulic_pressure_psi", 3000.0)
                mechanical.update_parameter("hydraulic_pressure_psi", current_press - 150.0)


class EngineeringDomainBlock:
    """Base class representing a specialized engineering discipline domain."""
    def __init__(self, domain_name: str, bus: SystemInterfaceBus):
        self.domain_name = domain_name
        self.bus = bus
        self.attributes = {}
        self.verification_status = "UNVERIFIED"
        self.bus.register_domain(domain_name, self)

    def update_parameter(self, key: str, value: float, broadcast=False):
        self.attributes[key] = value
        if broadcast:
            self.bus.propagate_change(self.domain_name, key, value)


# --- INDIVIDUAL SUB-DOMAINS ---

class StructuralBlock(EngineeringDomainBlock):
    def __init__(self, bus):
        super().__init__("Structural", bus)
        self.update_parameter("skin_thickness_mm", 12.5)
        self.update_parameter("current_aerodynamic_load_n", 0.0)

    def verify(self):
        if self.attributes["current_aerodynamic_load_n"] < 300000.0:
            self.verification_status = "PASSED (Structural Load Margin Tolerable)"
        else:
            self.verification_status = "FAILED (Structural Stress Deflection Exceeded)"


class ElectricalBlock(EngineeringDomainBlock):
    def __init__(self, bus):
        super().__init__("Electrical", bus)
        self.update_parameter("bus_voltage_v", 28.0)
        self.update_parameter("current_draw_amps", 15.0)

    def verify(self):
        # High current draw drops bus voltage line (Ohm's Law dependency)
        if self.attributes["current_draw_amps"] > 40.0:
            self.update_parameter("bus_voltage_v", 22.5) # Voltage sag
        
        if 24.0 <= self.attributes["bus_voltage_v"] <= 32.0 and self.attributes["current_draw_amps"] < 50.0:
            self.verification_status = "PASSED (Avionics Bus Healthy)"
        else:
            self.verification_status = "FAILED (Avionics Voltage Sag / Under-voltage fault)"


class MechanicalBlock(EngineeringDomainBlock):
    def __init__(self, bus):
        super().__init__("Mechanical", bus)
        self.update_parameter("hydraulic_pressure_psi", 3000.0)

    def verify(self):
        if 2800.0 <= self.attributes["hydraulic_pressure_psi"] <= 3200.0:
            self.verification_status = "PASSED (Hydraulic Pressure Bounds Nominal)"
        else:
            self.verification_status = "FAILED (Hydraulic Pressure Dropped Below Actuation Margin)"


class SoftwareBlock(EngineeringDomainBlock):
    def __init__(self, bus):
        super().__init__("Software", bus)
        self.update_parameter("cpu_utilization_pct", 34.5)
        self.update_parameter("commanded_tvc_gimbal_deg", 0.0)

    def verify(self):
        if self.attributes["cpu_utilization_pct"] < 80.0:
            self.verification_status = "PASSED (Real-Time Executive Window Satisfied)"
        else:
            self.verification_status = "FAILED (CPU Deadline Missed)"


# --- EXECUTION ENGINE PIPELINE ---
if __name__ == "__main__":
    print("Initializing Multi-Disciplinary Interface Control System...")
    
    # Instantiate the communication bus
    icd_bus = SystemInterfaceBus()

    # Instantiate the system segments linked via the bus
    structural = StructuralBlock(icd_bus)
    electrical = ElectricalBlock(icd_bus)
    mechanical = MechanicalBlock(icd_bus)
    software = SoftwareBlock(icd_bus)

    print("\nInitial State Verification:")
    for b in [structural, electrical, mechanical, software]:
        b.verify()
        print(f" -> [{b.domain_name}]: {b.verification_status}")

    print("\n========================================================")
    print("SCENARIO: Flight Software executes emergency vector adjustment")
    print("========================================================")
    
    # Software updates an internal parameter and broadcasts via the ICD matrix
    print("[SOFTWARE ACTION]: Commanding extreme Thrust Vector Control adjustment (+6.5 Degrees)...")
    software.update_parameter("commanded_tvc_gimbal_deg", 6.5, broadcast=True)
    
    # Structural load experiences unexpected high atmospheric shear forces simultaneously
    print("[STRUCTURAL EVENT]: Ingesting severe aerodynamic atmospheric wavefront stress load...")
    structural.update_parameter("current_aerodynamic_load_n", 220000.0, broadcast=True)

    print("\nPost-Cascading Dependency Verification Results:")
    for b in [structural, electrical, mechanical, software]:
        b.verify()
        print(f" -> [{b.domain_name}]: {b.verification_status}")
