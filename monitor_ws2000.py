import json
import subprocess
import time

class WS2000Monitor:
    def __init__(self):
        # Initialize any necessary variables or settings
        self.device = 'hw:1,0,0'  # Adjust this to your actual device
        self.process = None

    def get_latest_reading(self):
        """Fetch the latest wind reading from the WS2000."""
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
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
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
