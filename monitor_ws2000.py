import json
import subprocess
import time

class WS2000Monitor:
    def __init__(self):
        # Initialize any necessary variables or settings
        self.device = 'hw:1,0,0'  # Adjust this to your actual device

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
            
            print("Monitoring WS-2000 weather station...")
            print("Press Ctrl+C to stop")
            
            while True:
                line = process.stdout.readline()
                if line:
                    try:
                        data = json.loads(line)
                        # Check if the model is Fineoffset-WH24
                        if data.get('model') == "Fineoffset-WH24":
                            wind_speed_mps = data.get('wind_avg_m_s', 0)  # Wind speed in m/s
                            wind_speed_mph = wind_speed_mps * 2.23694  # Convert to MPH
                            wind_direction = data.get('wind_dir_deg', 0)  # Default to 0 if not found
                            print(f"Wind Speed: {wind_speed_mph:.2f} MPH, Wind Direction: {wind_direction}°")
                    except json.JSONDecodeError:
                        continue  # Ignore lines that cannot be parsed

        except Exception as e:
            print(f"Error fetching wind data: {e}")
            return {'wind_speed': 0.0, 'wind_direction': 0.0}  # Return default values on error

    def cleanup(self):
        """Clean up any resources if necessary."""
        pass  # Implement cleanup if needed 

# Example usage
if __name__ == "__main__":
    monitor = WS2000Monitor()
    monitor.get_latest_reading()

