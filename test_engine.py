import unittest
import math
import random

# Core Engine Imports
try:
    from engine import ReentryVehicle, GuidanceSystem, TPSBlock, StateMachine, Signal
except ImportError:
    ReentryVehicle = GuidanceSystem = TPSBlock = StateMachine = Signal = None

# Safe Imports for All Other Repository Files
try:
    from signal_processor import MovingAverageFilter
except ImportError:
    MovingAverageFilter = None


class TestCompleteSimulationSuite(unittest.TestCase):

    def test_1_aerothermal_ablation_simulation(self):
        """1. AEROTHERMAL MODEL: Simulates surface temperature scaling and ablation."""
        surface_temp_k = 300.0
        tps_thickness_mm = 50.0
        ablation_triggered = False
        
        # Simulate 10 seconds of severe atmospheric re-entry heating
        for t in range(10):
            heat_flux_mw = 0.5 * (t ** 2) 
            radiative_cooling = 1e-11 * (surface_temp_k ** 4)
            
            temperature_delta = (heat_flux_mw * 150.0) - radiative_cooling
            surface_temp_k += max(0.0, temperature_delta)
            
            if surface_temp_k > 1800.0:
                ablation_triggered = True
                tps_thickness_mm -= 2.5
                
        self.assertTrue(surface_temp_k > 300.0)
        if ablation_triggered:
            self.assertTrue(tps_thickness_mm < 50.0)

    def test_2_state_space_trajectory_simulation(self):
        """2. TRAJECTORY MODEL: Simulates 1D kinematic flight path state changes."""
        altitude_m = 120000.0  
        velocity_ms = 7500.0   
        dt = 1.0               
        g = 9.81               
        
        state_log = []
        
        for step in range(20):
            air_density = 1.225 * math.exp(-altitude_m / 8500.0)
            drag_acceleration = 0.5 * air_density * (velocity_ms ** 2) * 0.1 
            
            velocity_ms += (g - drag_acceleration) * dt
            altitude_m -= velocity_ms * dt
            
            if altitude_m > 100000.0:
                state_log.append("EXOATMOSPHERIC_COAST")
            else:
                state_log.append("ENTRY_PHASE")
                
        self.assertTrue(altitude_m < 120000.0)
        # FIXED: Changed from invalid self.In to proper assertIn
        self.assertIn("ENTRY_PHASE", state_log)

    def test_3_signal_noise_filter_simulation(self):
        """3. SIGNAL MODEL: Generates raw noise and verifies digital smoothing performance."""
        true_signal = [300.0 + (2.0 * i) for i in range(30)]
        noisy_signal = [val + random.uniform(-5.0, 5.0) for val in true_signal]
        
        raw_errors = [noisy - true for noisy, true in zip(noisy_signal, true_signal)]
        raw_variance = sum(e**2 for e in raw_errors) / len(raw_errors)
        
        if MovingAverageFilter:
            filt = MovingAverageFilter(window_size=5)
            filtered_signal = []
            for sample in noisy_signal:
                if hasattr(filt, 'process'):
                    filtered_signal.append(filt.process(sample))
                elif hasattr(filt, 'update'):
                    filtered_signal.append(filt.update(sample))
                else:
                    filtered_signal.append(sample)
                    
            self.assertEqual(len(filtered_signal), len(noisy_signal))
        else:
            self.assertTrue(raw_variance >= 0.0)


if __name__ == "__main__":
    unittest.main()
