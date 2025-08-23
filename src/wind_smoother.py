import numpy as np
from collections import deque
import time

class WindSmoother:
    """
    Configurable wind data smoother with adjustable parameters.
    
    Parameters:
    - buffer_size: Number of readings to average (more = smoother but slower)
    - max_wind_mph: Maximum expected wind speed for normalization
    - interpolation_steps: Steps between readings (more = smoother transitions)
    - smoothing_type: 'linear', 'exponential', or 'gaussian'
    - response_speed: How quickly to respond to changes (0.1 = slow, 1.0 = fast)
    """
    
    def __init__(self, buffer_size=10, max_wind_mph=20.0, interpolation_steps=150, 
                 smoothing_type='linear', response_speed=0.5):
        self.buffer_size = buffer_size
        self.max_wind_mph = max_wind_mph
        self.interpolation_steps = interpolation_steps
        self.smoothing_type = smoothing_type
        self.response_speed = max(0.1, min(1.0, response_speed))  # Clamp between 0.1 and 1.0
        
        self.wind_buffer = deque(maxlen=buffer_size)
        self.last_value = 0
        self.target_value = 0
        self.current_step = 0
        
        # Predefined smoothing profiles
        self.smoothing_profiles = {
            'responsive': {
                'buffer_size': 3,
                'interpolation_steps': 50,
                'response_speed': 0.8
            },
            'balanced': {
                'buffer_size': 8,
                'interpolation_steps': 100,
                'response_speed': 0.5
            },
            'smooth': {
                'buffer_size': 15,
                'interpolation_steps': 200,
                'response_speed': 0.3
            },
            'ambient': {
                'buffer_size': 20,
                'interpolation_steps': 300,
                'response_speed': 0.2
            }
        }
        
    def set_smoothing_profile(self, profile_name):
        """Set smoothing parameters using predefined profiles"""
        if profile_name in self.smoothing_profiles:
            profile = self.smoothing_profiles[profile_name]
            self.buffer_size = profile['buffer_size']
            self.interpolation_steps = profile['interpolation_steps']
            self.response_speed = profile['response_speed']
            
            # Adjust buffer size
            while len(self.wind_buffer) > self.buffer_size:
                self.wind_buffer.popleft()
            
            print(f"Set smoothing profile: {profile_name}")
            print(f"  Buffer size: {self.buffer_size}")
            print(f"  Interpolation steps: {self.interpolation_steps}")
            print(f"  Response speed: {self.response_speed}")
        else:
            print(f"Unknown profile: {profile_name}")
            print(f"Available profiles: {list(self.smoothing_profiles.keys())}")
    
    def set_custom_parameters(self, buffer_size=None, interpolation_steps=None, 
                            response_speed=None, smoothing_type=None):
        """Set custom smoothing parameters"""
        if buffer_size is not None:
            self.buffer_size = buffer_size
        if interpolation_steps is not None:
            self.interpolation_steps = interpolation_steps
        if response_speed is not None:
            self.response_speed = max(0.1, min(1.0, response_speed))
        if smoothing_type is not None:
            self.smoothing_type = smoothing_type
            
        print(f"Custom parameters set:")
        print(f"  Buffer size: {self.buffer_size}")
        print(f"  Interpolation steps: {self.interpolation_steps}")
        print(f"  Response speed: {self.response_speed}")
        print(f"  Smoothing type: {self.smoothing_type}")
        
    def add_wind_reading(self, wind_mph):
        """Add new wind reading and set as interpolation target"""
        self.wind_buffer.append(min(wind_mph, self.max_wind_mph))
        
        # Calculate target based on smoothing type
        if self.smoothing_type == 'gaussian':
            # Gaussian-weighted average
            weights = np.exp(-0.5 * ((np.arange(len(self.wind_buffer)) - len(self.wind_buffer)/2) / (len(self.wind_buffer)/4))**2)
            weights = weights / np.sum(weights)
            self.target_value = np.average(list(self.wind_buffer), weights=weights)
        elif self.smoothing_type == 'exponential':
            # Exponential moving average
            alpha = 2.0 / (len(self.wind_buffer) + 1)
            self.target_value = alpha * wind_mph + (1 - alpha) * self.target_value
        else:  # linear
            # Simple moving average
            self.target_value = np.mean(self.wind_buffer)
        
        self.last_value = self.get_smoothed_value()
        self.current_step = 0
        
    def get_smoothed_value(self):
        """Get interpolated value between last and target"""
        if self.current_step >= self.interpolation_steps:
            return self.target_value
            
        # Apply response speed to interpolation
        adjusted_steps = int(self.interpolation_steps / self.response_speed)
        progress = self.current_step / adjusted_steps
        
        # Different interpolation curves
        if self.smoothing_type == 'exponential':
            # Exponential ease-out
            progress = 1 - (1 - progress) ** 2
        elif self.smoothing_type == 'gaussian':
            # Gaussian curve
            progress = 1 - np.exp(-4 * progress)
        else:  # linear
            pass  # Linear interpolation
        
        # Clamp progress
        progress = max(0, min(1, progress))
        
        # Interpolate
        smoothed = self.last_value + (self.target_value - self.last_value) * progress
        
        # Increment step
        self.current_step = min(self.current_step + 1, self.interpolation_steps)
        
        return smoothed
        
    def get_normalized_value(self):
        """Get smoothed value normalized to 0-1 range"""
        return self.get_smoothed_value() / self.max_wind_mph
    
    def get_smoothing_info(self):
        """Get current smoothing parameters and statistics"""
        return {
            'buffer_size': self.buffer_size,
            'interpolation_steps': self.interpolation_steps,
            'response_speed': self.response_speed,
            'smoothing_type': self.smoothing_type,
            'buffer_fill': len(self.wind_buffer),
            'current_step': self.current_step,
            'last_value': self.last_value,
            'target_value': self.target_value
        }
