"""
LGM-35A Sentinel Program - Ground Silo Environmental Pneumatics Subsystem
Validates nitrogen pressure accumulator loops and launch facility environment bounds.
"""

class SiloPneumaticsController:
    """Manages environmental gas pressure and mechanical valve validation."""
    def __init__(self):
        self.accumulator_pressure_psi = 2200.0  # Target charging pressure
        self.exhaust_valve_open = False
        self.facility_status = "STABLE"

    def adjust_pressure(self, command: str) -> float:
        """Simulates mechanical valve actuation affecting fluid loop pressures."""
        if command == "CHARGE_ACCUMULATOR":
            self.accumulator_pressure_psi += 400.0
        elif command == "VENT_SAFETY":
            self.exhaust_valve_open = True
            self.accumulator_pressure_psi = 14.7 # Drop back to atmospheric pressure
            
        return self.accumulator_pressure_psi

    def verify_launch_readiness(self) -> bool:
        """Confirms system pressures settle perfectly inside safety thresholds."""
        # Operational limits: Must be between 2000 and 3000 PSI to support launch umbilical separation
        if 2000.0 <= self.accumulator_pressure_psi <= 3000.0 and not self.exhaust_valve_open:
            self.facility_status = "READY"
            return True
        else:
            self.facility_status = "HOLD_REQUIRED"
            return False


if __name__ == "__main__":
    print("Initializing Ground Segment Pneumatic Control Loop...")
    pneumatics = SiloPneumaticsController()
    
    print(f"Initial Status: {pneumatics.verify_launch_readiness()} (Pressure: {pneumatics.accumulator_pressure_psi} PSI)")
    pneumatics.adjust_pressure("CHARGE_ACCUMULATOR")
    print(f"Post-Charge Status: {pneumatics.verify_launch_readiness()} (Pressure: {pneumatics.accumulator_pressure_psi} PSI)")
