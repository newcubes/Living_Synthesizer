import json
import subprocess
import time
import os

class WS2000Monitor:
    def __init__(self):
<<<<<<< HEAD
=======
        # Initialize any necessary variables or settings
        self.device = 'hw:1,0,0'  # Adjust this to your actual device
>>>>>>> c5e4e3ddeb26f12cffb6ad335db7d810cb7f7f10
        self.process = None

    def get_latest_reading(self):
        """Fetch the latest wind reading from the WS2000."""
        print("Starting get_latest_reading...")
        
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
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Run with timeout and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15  # Additional Python timeout
            )
            
<<<<<<< HEAD
            print(f"Process completed with return code: {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            
            # Parse the output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
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
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            continue
            
            print("No valid weather data found")
            return {'wind_speed': 0.0, 'wind_direction': 0.0}
=======
            # Try to read one line with a timeout
            try:
                line = process.stdout.readline()
                if line:
                    try:
                        data = json.loads(line)
                        # Check if the model is Fineoffset-WH24
                        if data.get('model') == "Fineoffset-WH24":
                            wind_speed = data.get('wind_avg_m_s', 0) * 2.23694  # Convert to MPH
                            wind_direction = data.get('wind_dir_deg', 0)  # Default to 0 if not found
                            print(f"Wind Speed: {wind_speed:.2f} MPH, Wind Direction: {wind_direction}°")
                            return {'wind_speed': wind_speed, 'wind_direction': wind_direction}
                    except json.JSONDecodeError:
                        pass  # Ignore lines that cannot be parsed
                
                # If no valid data found, return default values
                return {'wind_speed': 0.0, 'wind_direction': 0.0}
                
            finally:
                # Always terminate the process
                process.terminate()
                process.wait()

        except Exception as e:
            print(f"Error fetching wind data: {e}")
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
                            wind_speed = data.get('wind_avg_m_s', 0) * 2.23694  # Convert to MPH
                            wind_direction = data.get('wind_dir_deg', 0)  # Default to 0 if not found
                            print(f"Wind Speed: {wind_speed:.2f} MPH, Wind Direction: {wind_direction}°")
                    except json.JSONDecodeError:
                        continue  # Ignore lines that cannot be parsed
>>>>>>> c5e4e3ddeb26f12cffb6ad335db7d810cb7f7f10

        except subprocess.TimeoutExpired:
            print("Command timed out")
            return {'wind_speed': 0.0, 'wind_direction': 0.0}
        except Exception as e:
<<<<<<< HEAD
            print(f"Error fetching wind data: {e}")
            return {'wind_speed': 0.0, 'wind_direction': 0.0}

    def start_monitoring(self):
        """Start continuous monitoring of the WS2000."""
        print("Starting continuous monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                reading = self.get_latest_reading()
                print(f"Reading: {reading}")
                time.sleep(5)  # Wait 5 seconds between readings
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
=======
            print(f"Error in monitoring: {e}")
>>>>>>> c5e4e3ddeb26f12cffb6ad335db7d810cb7f7f10

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
