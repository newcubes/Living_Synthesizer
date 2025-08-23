import json
import subprocess
import time
import os
from wind_smoother import WindSmoother

class WS2000Monitor:
    def __init__(self):
        self.process = None
        # Initialize wind smoother for smooth transitions
        self.wind_smoother = WindSmoother(buffer_size=10, max_wind_mph=20.0)

    def get_latest_reading(self):
        """Fetch the latest wind reading from the WS2000."""
        try:
            # Use a different approach - run rtl_433 with a timeout and capture output
            cmd = [
                'timeout', '10',  # 10 second timeout
                './rtl_433',
                '-f', '915M',
                '-M', 'level',
                '-M', 'report_meta',
                '-Y', 'autolevel',
                '-F', 'json:-'
            ]
            
            # Run with timeout and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15  # Additional Python timeout
            )
            
            # Parse the output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            
                            # Check if the model is Fineoffset-WH24
                            if data.get('model') == "Fineoffset-WH24":
                                # Extract wind data - convert m/s to MPH
                                wind_speed = data.get('wind_avg_m_s', 0) * 2.23694  # Convert m/s to MPH
                                wind_direction = data.get('wind_dir_deg', 0)  # Wind direction in degrees
                                temperature = data.get('temperature_C', 0)  # Temperature in Celsius
                                humidity = data.get('humidity', 0)  # Humidity percentage
                                
                                return {
                                    'wind_speed': wind_speed, 
                                    'wind_direction': wind_direction,
                                    'temperature': temperature,
                                    'humidity': humidity
                                }
                        except json.JSONDecodeError:
                            continue
            
            return None

        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            print(f"Error fetching wind data: {e}")
            return None

    def start_monitoring(self):
        """Start continuous monitoring of the WS2000."""
        print("Starting continuous weather monitoring for MIDI control...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                reading = self.get_latest_reading()
                
                if reading:
                    wind_speed = reading.get('wind_speed', 0)
                    wind_direction = reading.get('wind_direction', 0)
                    temperature = reading.get('temperature', 0)
                    humidity = reading.get('humidity', 0)
                    
                    # Add to smoother for smooth transitions
                    self.wind_smoother.add_wind_reading(wind_speed)
                    smooth_speed = self.wind_smoother.get_normalized_value()
                    
                    print(f"Wind: {wind_speed:.1f} mph | Smooth: {smooth_speed:.3f} | Dir: {wind_direction}° | Temp: {temperature}°C | Humidity: {humidity}%")
                    
                    # Return the smoothed value for MIDI control
                    yield {
                        'wind_speed': wind_speed,
                        'smooth_speed': smooth_speed,
                        'wind_direction': wind_direction,
                        'temperature': temperature,
                        'humidity': humidity
                    }
                else:
                    print("No weather data received, using last known values...")
                    # Return last known smoothed value
                    smooth_speed = self.wind_smoother.get_normalized_value()
                    yield {
                        'wind_speed': 0.0,
                        'smooth_speed': smooth_speed,
                        'wind_direction': 0,
                        'temperature': 0,
                        'humidity': 0
                    }
                
                time.sleep(2)  # Wait 2 seconds between readings
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

    def cleanup(self):
        """Clean up any resources if necessary."""
        if self.process:
            self.process.terminate()
            self.process.wait()

# Example usage
if __name__ == "__main__":
    monitor = WS2000Monitor()
    
    # For continuous monitoring and MIDI control
    for reading in monitor.start_monitoring():
        # This is where you would send MIDI data
        # reading['smooth_speed'] contains the smoothed wind speed (0-1 range)
        # reading['wind_direction'] contains wind direction (0-360 degrees)
        pass
