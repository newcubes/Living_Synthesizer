import numpy as np
from collections import deque
import time

class WindSmoother:
    def __init__(self, buffer_size=10, max_wind_mph=10.0):
        self.buffer_size = buffer_size
        self.max_wind_mph = max_wind_mph
        self.wind_buffer = deque(maxlen=buffer_size)
        self.last_value = 0
        self.target_value = 0
        self.interpolation_steps = 150  # Steps between wind readings
        self.current_step = 0
        
    def add_wind_reading(self, wind_mph):
        """Add new wind reading and set as interpolation target"""
        self.wind_buffer.append(min(wind_mph, self.max_wind_mph))
        self.last_value = self.target_value
        self.target_value = np.mean(self.wind_buffer)
        self.current_step = 0
        
    def get_smoothed_value(self):
        """Get interpolated value between last and target"""
        # Linear interpolation
        progress = self.current_step / self.interpolation_steps
        smoothed = self.last_value + (self.target_value - self.last_value) * progress
        
        # Increment step
        self.current_step = min(self.current_step + 1, self.interpolation_steps)
        
        return smoothed
        
    def get_normalized_value(self):
        """Get smoothed value normalized to 0-1 range"""
        return self.get_smoothed_value() / self.max_wind_mph
