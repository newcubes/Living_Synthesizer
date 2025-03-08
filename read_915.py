from rtlsdr import RtlSdr
import numpy as np
from matplotlib import pyplot as plt

# Initialize device
sdr = RtlSdr()

# Configure device
sdr.sample_rate = 2.4e6    # Hz
sdr.center_freq = 915e6    # Hz
sdr.freq_correction = 60   # PPM
sdr.gain = 'auto'

# Read samples
samples = sdr.read_samples(256*1024)

# Clean up
sdr.close()

# Convert samples to dB
psd = 10 * np.log10(np.abs(np.fft.fft(samples))**2)
f = np.fft.fftfreq(len(samples), 1/sdr.sample_rate)

# Plot
plt.figure(figsize=(12,6))
plt.plot(f/1e6, psd)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (dB)')
plt.grid(True)
plt.savefig('spectrum.png')
