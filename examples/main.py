import time
from src.monitor import WS2000Monitor
from src.wind_smoother import WindSmoother
from midi.sdr_to_midi import SDRModulator

class Coordinator:
    def __init__(self):
        print("Initializing WS2000Monitor...")
        self.monitor = WS2000Monitor()
        print("Initializing WindSmoother...")
        self.smoother = WindSmoother(buffer_size=10, max_wind_mph=10.0)
        print("Initializing SDRModulator...")
        self.midi_modulator = SDRModulator()

    def run(self):
        print("Starting the monitoring and MIDI conversion process...")
        try:
            while True:
                reading = self.monitor.get_latest_reading()
                print(f"Reading: {reading}")  # Debug output
                if reading:
                    wind_speed = reading.get('wind_speed', 0)
                    wind_direction = reading.get('wind_direction', 0)

                    # Smooth the wind speed
                    smoothed_speed = self.smoother.add_wind_reading(wind_speed)

                    # Send MIDI message
                    midi_output = self.midi_modulator.send_midi_cc(smoothed_speed)  # Assuming send_midi_cc is the method to send MIDI
                    print(f"Wind Speed: {wind_speed:.2f} MPH, Wind Direction: {wind_direction}°")
                    print(f"MIDI Output: {midi_output}")  # Debug output

                time.sleep(1)  # Adjust the sleep time as necessary

        except KeyboardInterrupt:
            print("Stopping the coordinator...")
            self.monitor.cleanup()  # Call cleanup if necessary

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.run()
