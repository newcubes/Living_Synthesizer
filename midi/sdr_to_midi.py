import rtlsdr
import alsaseq
import alsamidi
import numpy as np
import time
from src.monitor import WS2000Monitor
from src.wind_smoother import WindSmoother

class SDRModulator:
    def __init__(self):
        # Initialize ALSA MIDI
        alsaseq.client('SDRModulator', 1, 1, False)
        self.find_digitone()

        # Initialize SDR
        self.sdr = rtlsdr.RtlSdr()
        self.configure_sdr()

        # Initialize wind smoother
        self.wind_smoother = WindSmoother(buffer_size=10, max_wind_mph=10.0)

        # MIDI CC numbers for Digitone LFO parameters
        self.CC_LFO_SPEED = 102  # Example CC number, adjust based on Digitone manual
        self.CC_LFO_DEPTH = 103  # Example CC number, adjust based on Digitone manual
    
    def configure_sdr(self):
        self.sdr.sample_rate = 2.048e6
        self.sdr.center_freq = 100e6  # Adjust based on desired frequency
        self.sdr.gain = 'auto'
    
    def find_digitone(self):
        # TODO: Implement ALSA port discovery for Digitone
        # For now, assuming port 0
        self.port = 0

    def process_samples(self, samples):
        # Get signal magnitude
        magnitude = np.abs(samples)

        # Calculate different characteristics of the signal
        avg_magnitude = np.mean(magnitude)
        peak_magnitude = np.max(magnitude)

        # Map these to MIDI CC values (0-127)
        speed_cc = int(np.clip(avg_magnitude * 127, 0, 127))
        depth_cc = int(np.clip(peak_magnitude * 127, 0, 127))

        return speed_cc, depth_cc

    def send_midi_cc(self, cc_number, value):
        event = alsamidi.controller_change(0, cc_number, value)
        alsaseq.output(event)

    def run(self):
        print("Starting SDR to MIDI conversion...")
        ws2000 = WS2000Monitor()  # Initialize WS2000 monitor
        try:
            while True:
                # Get wind reading from WS2000 monitor
                wind_data = ws2000.get_latest_reading()
                if wind_data and 'wind_speed' in wind_data:
                    # Process wind speed through smoother
                    self.wind_smoother.add_wind_reading(wind_data['wind_speed'])
                    smooth_value = self.wind_smoother.get_normalized_value()

                    # Send MIDI CC messages
                    self.send_midi_cc(self.CC_LFO_SPEED, smooth_value)
                    # Optionally send depth or other parameters
                    # self.send_midi_cc(self.CC_LFO_DEPTH, depth_value)

                # Small delay to prevent flooding
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.sdr.close()

if __name__ == "__main__":
    modulator = SDRModulator()
    modulator.run()







