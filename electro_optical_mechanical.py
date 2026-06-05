"""
LGM-35A Sentinel Program - Electro-Optical Mechanical (EOM) Tracking Subsystem
Models the stabilization loop of an optical sensor via mechanical gimbals.
"""

class ElectroOpticalMechanicalSystem:
    """Represents a stabilized EO/IR optical tracking sensor array."""
    def __init__(self):
        # Electrical Domain Parameters
        self.voltage_in = 28.0                 # Standard defense bus voltage
        self.current_draw_amps = 2.0           # Nominal idle current

        # Mechanical Domain Parameters
        self.gimbal_azimuth_deg = 0.0          # Current pan angle
        self.gimbal_elevation_deg = 0.0        # Current tilt angle
        self.motor_temperature_c = 25.0        # Thermal state of servo motors

        # Optical/Software Domain Parameters
        self.focal_length_mm = 150.0           # Lens specification
        self.target_locked = False
        self.tracking_error_arcsec = 0.0       # Precision metric

    def track_target(self, target_az: float, target_el: float):
        """Simulates mechanical gimbals slewing to track an optical target."""
        print(f"[EOM UPDATE]: Optical target spotted at Az: {target_az}°, El: {target_el}°")
        
        # Calculate mechanical movement needed
        az_delta = target_az - self.gimbal_azimuth_deg
        el_delta = target_el - self.gimbal_elevation_deg

        # Mechanical actuation causes an electrical draw spike and thermal heating
        if abs(az_delta) > 0.1 or abs(el_delta) > 0.1:
            self.current_draw_amps = 12.5       # Electrical spike during motor acceleration
            self.motor_temperature_c += 1.8     # Mechanical friction/resistance heat dissipation
            
            # Slew the physical hardware
            self.gimbal_azimuth_deg = target_az
            self.gimbal_elevation_deg = target_el
            self.tracking_error_arcsec = 1.2    # Stabilization jitter residual error
            self.target_locked = True
        else:
            self.current_draw_amps = 2.0        # Return to electrical baseline
            self.tracking_error_arcsec = 0.4    # Static lock accuracy optimized

    def check_system_health(self) -> str:
        """Evaluates multidisciplinary compliance boundaries for the EOM system."""
        if self.voltage_in < 22.0:
            return "CRITICAL FAULT: Under-voltage line sag on EO power bus"
        if self.motor_temperature_c > 85.0:
            return "CRITICAL FAULT: Mechanical servo actuators overheating"
        if self.tracking_error_arcsec > 5.0:
            return "WARN: Optical jitter exceeds line-of-sight tracking thresholds"
        
        return "PASSED: Electro-Optical Mechanical payload operational"


if __name__ == "__main__":
    print("Initializing Electro-Optical Mechanical Tracking System...")
    eom_payload = ElectroOpticalMechanicalSystem()
    
    print(f"Initial Health: {eom_payload.check_system_health()}")
    
    # Simulate intercept track command step
    print("\nExecuting line-of-sight acquisition sweep...")
    eom_payload.track_target(45.2, 12.8)
    
    print(f"Post-Slew Current Draw: {eom_payload.current_draw_amps} Amps")
    print(f"Post-Slew Motor Temp:   {eom_payload.motor_temperature_c:.1f}°C")
    print(f"Target Lock Status:     {eom_payload.target_locked}")
    print(f"Payload Health:         {eom_payload.check_system_health()}")
