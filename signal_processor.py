"""
LGM-35A Sentinel Program - Telemetry Signal Processing Module
Implements Real-Time Low-Pass Window Filtering for Noisy Aerothermal Sensors.
"""

class MovingAverageFilter:
    """Smoothes raw, noisy telemetry sensor streams using an N-sample window."""
    def __init__(self, window_size: int = 3):
        self.window_size = window_size
        self.history = {}

    def filter_signal(self, sensor_id: str, raw_value: float) -> float:
        """Applies a moving average calculation to eliminate transient noise spikes."""
        if sensor_id not in self.history:
            self.history[sensor_id] = []
        
        # Append latest raw hardware reading
        self.history[sensor_id].append(raw_value)
        
        # Keep window bounded to specified sizing constraint
        if len(self.history[sensor_id]) > self.window_size:
            self.history[sensor_id].pop(0)
            
        # Compute the deterministic moving mean
        return sum(self.history[sensor_id]) / len(self.history[sensor_id])


if __name__ == "__main__":
    print("Initializing Flight Instrumentation Signal Processor...")
    processor = MovingAverageFilter(window_size=3)
    
    # Simulated noisy sensor data stream for aerodynamic drag (transient spikes)
    noisy_drag_stream = [48000.0, 56000.0, 52000.0, 120000.0, 54000.0]
    
    print("\n--- Processing Telemetry Stream Window Filters ---")
    for raw_reading in noisy_drag_stream:
        clean_reading = processor.filter_signal("STAGNATION_DRAG_01", raw_reading)
        print(f"Raw Input: {raw_reading:9.2f} N | Filtered Output: {clean_reading:9.2f} N")
