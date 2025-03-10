import numpy as np
import time
import subprocess
from monitor_ws2000 import WS2000Monitor
from wind_smoother import WindSmoother

class WindControl:
    def __init__(self):
        # Initialize WS2000 SDR monitor
        self.ws2000 = WS2000Monitor()  # This handles the SDR reception
        
        # Initialize smoother for wind data
        self.wind_smoother = WindSmoother(
            buffer_size=10,  # Store last 10 wind readings
            max_wind_mph=10.0  # Maximum expected wind speed
        )
        
        # Digitone MIDI settings
        self.midi_port = 'hw:1,0,0'
        self.CC_LFO_SPEED = 102  # CC1 is set to 102
        
        # Add debug mode
        self.debug = True
        
    def process_wind_reading(self, wind_speed):
        """Process new wind reading from WS2000"""
        # Add to smoother
        self.wind_smoother.add_wind_reading(wind_speed)
        
        # Get smoothed value (0-1 range)
        return self.wind_smoother.get_normalized_value()
    
    def send_midi_cc(self, cc_number, value):
        """Send MIDI CC to Digitone"""
        midi_value = int(value * 127)
        midi_message = f"B0 {cc_number:02x} {midi_value:02x}"
        
        if self.debug:
            print(f"Sending MIDI: {midi_message}")
            
        try:
            subprocess.run(['amidi', '-p', self.midi_port, '-S', midi_message], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to send MIDI message: {midi_message}")
    
    def run(self):
        print("Starting Wind-Controlled LFO...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Get wind reading from WS2000 monitor
                wind_data = self.ws2000.get_latest_reading()
                if wind_data and 'wind_speed' in wind_data:
                    # Process wind speed through smoother
                    smooth_value = self.process_wind_reading(wind_data['wind_speed'])
                    
                    # Send to Digitone LFO
                    self.send_midi_cc(self.CC_LFO_SPEED, smooth_value)
                    
                    # Debug output
                    print(f"\rWind: {wind_data['wind_speed']:.1f} mph | LFO: {smooth_value:.2f}", end='')
                
                # Get interpolated value between readings
                smooth_value = self.wind_smoother.get_normalized_value()
                self.send_midi_cc(self.CC_LFO_SPEED, smooth_value)
                
                # Small delay
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.ws2000.cleanup()

if __name__ == "__main__":
    controller = WindControl()
    controller.run()
