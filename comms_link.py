"""
LGM-35A Sentinel Program - RF Communications Link Budget Subsystem
Models signal attenuation and telemetry link margins during flight.
"""

class CommsLinkTracker:
    """Tracks RF transmission strength and link viability."""
    def __init__(self):
        self.transmitter_power_dbm = 43.0  # ~20 Watts RF output
        self.link_margin_db = 15.0         # Baseline signal safety buffer
        self.plasma_blackout_active = False

    def evaluate_link_stability(self, altitude_ft: float, speed_mach: float) -> str:
        """Calculates dynamic attenuation based on vehicle environmental state."""
        # Simulate extreme atmospheric friction ionization (Plasma Blackout)
        if altitude_ft < 150000 and speed_mach > 12.0:
            self.plasma_blackout_active = True
            self.link_margin_db = -25.0  # Signal completely dropped
            return "CRITICAL FAULT: Plasma ionization blackout. Telemetry stream severed."
        
        # Standard atmospheric free-space path loss attenuation approximation
        if altitude_ft > 50000:
            self.link_margin_db = 15.0 - (altitude_ft / 20000.0)
        
        if self.link_margin_db > 0.0:
            return f"NOMINAL: RF Telemetry link stable. Margin: {self.link_margin_db:.1f} dB"
        else:
            return "WARN: Signal attenuation exceeds receiver threshold. Packet degradation occurring."


if __name__ == "__main__":
    print("Initializing RF Communications Link Subsystem...")
    comms = CommsLinkTracker()
    
    print(comms.evaluate_link_stability(60000, 3.5))
    print(comms.evaluate_link_stability(120000, 15.0)) # Trigger blackout parameters
