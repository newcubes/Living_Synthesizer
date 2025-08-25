import json
import subprocess
import time
import os
from .wind_smoother import WindSmoother

class WS2000Monitor:
    def __init__(self, smoothing_profile='balanced'):
        self.process = None
        # Initialize wind smoother with configurable profile
        self.wind_smoother = WindSmoother()
        self.wind_smoother.set_smoothing_profile(smoothing_profile)
        self.last_reading = None

    def check_device(self):
        """Check if RTL-SDR device is available."""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            return 'realtek' in result.stdout.lower()
        except:
            return False

    def start_monitoring(self):
        """Start continuous monitoring of the WS2000."""
        print("Starting continuous weather monitoring for MIDI control...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Check if device is available
                if not self.check_device():
                    print("RTL-SDR device not found. Waiting for device...")
                    time.sleep(5)
                    continue
                
                print("RTL-SDR device found. Starting rtl_433...")
                
                # Start rtl_433 process continuously
                # Find rtl_433 relative to the project root
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                rtl_433_path = os.path.join(project_root, 'rtl_433')
                
                cmd = [
                    rtl_433_path,
                    '-f', '915M',
                    '-F', 'json:-'
                ]
                
                print(f"Starting rtl_433: {' '.join(cmd)}")
                
                # Start the process
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                print(f"rtl_433 started with PID: {self.process.pid}")
                print("Listening for weather station transmissions...")
                
                # Read output continuously
                while True:
                    # Check if process is still running
                    if self.process.poll() is not None:
                        print("rtl_433 process exited unexpectedly. Restarting...")
                        break
                    
                    # Check if device is still available
                    if not self.check_device():
                        print("RTL-SDR device lost. Restarting...")
                        break
                    
                    # Read output with timeout
                    try:
                        line = self.process.stdout.readline()
                        if line:
                            try:
                                data = json.loads(line.strip())
                                
                                # Check if the model is Fineoffset-WH24
                                if data.get('model') == "Fineoffset-WH24":
                                    # Extract wind data - convert m/s to MPH
                                    wind_speed = data.get('wind_avg_m_s', 0) * 2.23694  # Convert m/s to MPH
                                    wind_direction = data.get('wind_dir_deg', 0)  # Wind direction in degrees
                                    temperature = data.get('temperature_C', 0)  # Temperature in Celsius
                                    humidity = data.get('humidity', 0)  # Humidity percentage
                                    
                                    # Add to smoother for smooth transitions
                                    self.wind_smoother.add_wind_reading(wind_speed)
                                    smooth_speed = self.wind_smoother.get_normalized_value()
                                    
                                    print(f"Wind: {wind_speed:.1f} mph | Smooth: {smooth_speed:.3f} | Dir: {wind_direction}° | Temp: {temperature}°C | Humidity: {humidity}%")
                                    
                                    # Yield the data for MIDI control
                                    yield {
                                        'wind_speed': wind_speed,
                                        'smooth_speed': smooth_speed,
                                        'wind_direction': wind_direction,
                                        'temperature': temperature,
                                        'humidity': humidity
                                    }
                                    
                                    # Store the reading
                                    self.last_reading = {
                                        'wind_speed': wind_speed,
                                        'wind_direction': wind_direction,
                                        'temperature': temperature,
                                        'humidity': humidity
                                    }
                                    
                            except json.JSONDecodeError:
                                # Skip non-JSON lines
                                continue
                        else:
                            # No output, check if process is still alive
                            time.sleep(0.1)
                            
                    except Exception as e:
                        print(f"Error reading output: {e}")
                        break
                        
            except KeyboardInterrupt:
                print("\nStopping monitoring...")
                break
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(5)  # Wait before retrying
            finally:
                if self.process:
                    self.process.terminate()
                    self.process.wait()
                    print("rtl_433 process terminated")

    def get_latest_reading(self):
        """Get the last known reading (for compatibility)."""
        if self.last_reading:
            wind_speed = self.last_reading.get('wind_speed', 0)
            self.wind_smoother.add_wind_reading(wind_speed)
            smooth_speed = self.wind_smoother.get_normalized_value()
            
            return {
                'wind_speed': wind_speed,
                'smooth_speed': smooth_speed,
                'wind_direction': self.last_reading.get('wind_direction', 0),
                'temperature': self.last_reading.get('temperature', 0),
                'humidity': self.last_reading.get('humidity', 0)
            }
        return None

    def set_smoothing_profile(self, profile_name):
        """Change smoothing profile on the fly"""
        self.wind_smoother.set_smoothing_profile(profile_name)
    
    def set_custom_smoothing(self, **kwargs):
        """Set custom smoothing parameters"""
        self.wind_smoother.set_custom_parameters(**kwargs)
    
    def get_smoothing_info(self):
        """Get current smoothing parameters"""
        return self.wind_smoother.get_smoothing_info()
    
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
