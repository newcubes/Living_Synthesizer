import json
import subprocess
import time
import signal
import os

class WS2000Monitor:
    def __init__(self):
        # Initialize any necessary variables or settings
        self.device = 'hw:1,0,0'  # Adjust this to your actual device
        self.process = None

    def check_rtl_433(self):
        """Check if rtl_433 is available and working"""
        print("Checking rtl_433 availability...")
        try:
            result = subprocess.run(['./rtl_433', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"rtl_433 version: {result.stdout.strip()}")
            return True
        except subprocess.TimeoutExpired:
            print("rtl_433 version check timed out")
            return False
        except FileNotFoundError:
            print("rtl_433 executable not found")
            return False
        except Exception as e:
            print(f"Error checking rtl_433: {e}")
            return False

    def get_latest_reading(self):
        """Fetch the latest wind reading from the WS2000."""
        print("Starting get_latest_reading...")
        
        # First check if rtl_433 is available
        if not self.check_rtl_433():
            print("rtl_433 not available, returning default values")
            return {'wind_speed': 0.0, 'wind_direction': 0.0}
        
        try:
            # Command to run rtl_433 with detailed output
            cmd = [
                './rtl_433',
                '-f', '915M',
                '-M', 'level',
                '-M', 'report_meta',
                '-Y', 'autolevel',
                '-F', 'json:-'  # Output JSON to stdout
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            print("Starting subprocess...")
            
            # Start rtl_433 process with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            print(f"Process started with PID: {process.pid}")
            print("Waiting for output...")
            
            # Try to read one line with a timeout
            try:
                # Set a timeout of 15 seconds (longer for first detection)
                import select
                print("Setting up select with 15 second timeout...")
                ready, _, _ = select.select([process.stdout], [], [], 15.0)
                
                if ready:
                    print("Data available, reading line...")
                    line = process.stdout.readline()
                    print(f"Got line: {line.strip()}")
                    if line:
                        try:
                            data = json.loads(line)
                            print(f"Parsed JSON: {data}")
                            # Check if the model is Fineoffset-WH24
                            if data.get('model') == "Fineoffset-WH24":
                                # Extract wind data - convert m/s to MPH
                                wind_speed = data.get('wind_speed', 0) * 2.23694  # Convert m/s to MPH
                                wind_direction = data.get('wind_dir_deg', 0)  # Wind direction in degrees
                                temperature = data.get('temperature_C', 0)  # Temperature in Celsius
                                humidity = data.get('humidity', 0)  # Humidity percentage
                                
                                print(f"Wind Speed: {wind_speed:.2f} MPH, Wind Direction: {wind_direction}°")
                                print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                                
                                return {
                                    'wind_speed': wind_speed, 
                                    'wind_direction': wind_direction,
                                    'temperature': temperature,
                                    'humidity': humidity
                                }
                            else:
                                print(f"Received data from model: {data.get('model', 'unknown')}")
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            pass  # Ignore lines that cannot be parsed
                else:
                    print("Timeout waiting for output")
                    # Check if process is still running
                    if process.poll() is None:
                        print("Process is still running but no output received")
                        # Check stderr for any error messages
                        stderr_output = process.stderr.read()
                        if stderr_output:
                            print(f"stderr output: {stderr_output}")
                    else:
                        print(f"Process exited with code: {process.returncode}")
                        # Get stderr output
                        stderr_output = process.stderr.read()
                        if stderr_output:
                            print(f"stderr output: {stderr_output}")
                
                # If no valid data found, return default values
                return {'wind_speed': 0.0, 'wind_direction': 0.0}
                
            finally:
                # Always terminate the process
                print("Terminating process...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print("Process terminated successfully")
                except subprocess.TimeoutExpired:
                    print("Process didn't terminate, killing...")
                    process.kill()
                    process.wait()
                    print("Process killed")

        except Exception as e:
            print(f"Error fetching wind data: {e}")
            import traceback
            traceback.print_exc()
            return {'wind_speed': 0.0, 'wind_direction': 0.0}  # Return default values on error

    def start_monitoring(self):
        """Start continuous monitoring of the WS2000."""
        try:
            # Command to run rtl_433 with detailed output
            cmd = [
                './rtl_433',
                '-f', '915M',
                '-M', 'level',
                '-M', 'report_meta',
                '-Y', 'autolevel',
                '-F', 'json:-'  # Output JSON to stdout
            ]
            
            # Start rtl_433 process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            print("Monitoring WS-2000 weather station...")
            print("Press Ctrl+C to stop")
            
            while True:
                line = self.process.stdout.readline()
                if line:
                    try:
                        data = json.loads(line)
                        # Check if the model is Fineoffset-WH24
                        if data.get('model') == "Fineoffset-WH24":
                            wind_speed = data.get('wind_speed', 0) * 2.23694  # Convert to MPH
                            wind_direction = data.get('wind_dir_deg', 0)  # Default to 0 if not found
                            temperature = data.get('temperature_C', 0)
                            humidity = data.get('humidity', 0)
                            print(f"Wind Speed: {wind_speed:.2f} MPH, Wind Direction: {wind_direction}°")
                            print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                    except json.JSONDecodeError:
                        continue  # Ignore lines that cannot be parsed

        except Exception as e:
            print(f"Error in monitoring: {e}")

    def cleanup(self):
        """Clean up any resources if necessary."""
        if self.process:
            self.process.terminate()
            self.process.wait()

# Example usage
if __name__ == "__main__":
    monitor = WS2000Monitor()
    # For testing, get a single reading
    reading = monitor.get_latest_reading()
    print(f"Single reading: {reading}")
    
    # For continuous monitoring, uncomment the line below:
    # monitor.start_monitoring()
