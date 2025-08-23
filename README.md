# Living Synthesizer

A weather-controlled synthesizer system that uses real-time wind data to modulate MIDI parameters.

## Overview

This project connects a WS2000 weather station to a synthesizer (Digitone) using an RTL-SDR device. Wind speed and direction data are used to control LFO parameters in real-time, creating a "living" synthesizer that responds to environmental conditions.

## Project Structure

```
Living_Synthesizer/
├── src/                    # Core monitoring modules
│   ├── monitor.py         # Weather station monitoring
│   └── wind_smoother.py   # Wind data smoothing
├── midi/                   # MIDI control modules
│   ├── sdr_to_midi.py     # SDR to MIDI conversion
│   ├── signal_conversion.py # Environmental to MIDI conversion
│   └── smooth_monitor.py  # Smooth monitoring with MIDI
├── examples/               # Example usage scripts
│   └── main.py            # Main coordinator example
├── tests/                  # Test and debugging scripts
│   ├── test_hardware.py   # Hardware connectivity tests
│   ├── fix_rtl_sdr.py     # RTL-SDR troubleshooting
│   └── README.md          # Test documentation
├── setup.py               # Package installation
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Components

- **Weather Station**: Fineoffset-WH24 transmitting on 915MHz
- **RTL-SDR**: Nooelec NESDR SMArt v5 for receiving weather data
- **Raspberry Pi**: Processes weather data and sends MIDI commands
- **Synthesizer**: Elektron Digitone (or other MIDI-compatible device)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/newcubes/Living_Synthesizer.git
cd Living_Synthesizer

# Install Python dependencies
pip install -r requirements.txt

# Install RTL-SDR tools (on Raspberry Pi)
sudo apt update
sudo apt install rtl-sdr librtlsdr-dev

# Blacklist DVB driver
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee -a /etc/modprobe.d/blacklist-rtl.conf
sudo reboot
```

### Basic Usage

```bash
# Test hardware setup
python3 tests/test_hardware.py

# Start weather monitoring
python3 src/monitor.py

# Run full system example
python3 examples/main.py
```

### Development

```bash
# Install in development mode
pip install -e .

# Run tests
python3 tests/test_hardware.py
python3 tests/fix_rtl_sdr.py
```

## API Reference

### Core Monitoring

```python
from src import WS2000Monitor, WindSmoother

# Create monitor
monitor = WS2000Monitor()

# Get continuous weather data
for reading in monitor.start_monitoring():
    wind_speed = reading['wind_speed']      # Raw wind speed (MPH)
    smooth_speed = reading['smooth_speed']  # Smoothed (0-1 range)
    wind_direction = reading['wind_direction']  # Degrees
    temperature = reading['temperature']    # Celsius
    humidity = reading['humidity']          # Percentage
```

### MIDI Control

```python
from midi import SDRModulator, SignalConverter

# Create signal converter
converter = SignalConverter()

# Convert and send environmental data to synthesizer
converter.run()
```

## Troubleshooting

See `tests/README.md` for detailed troubleshooting guides.

Common issues:
- **RTL-SDR not detected**: Check USB connection and DVB driver blacklist
- **No weather data**: Verify weather station is transmitting on 915MHz
- **MIDI not working**: Check MIDI device connections and permissions

## Data Flow

1. Weather station transmits data every ~16 seconds
2. RTL-SDR receives and demodulates the signal
3. `rtl_433` decodes the weather data
4. `monitor.py` processes and smooths the data
5. MIDI control signals are sent to the synthesizer
6. Synthesizer parameters are modulated in real-time

## Weather Data

The system captures:
- **Wind Speed**: 0-20+ MPH (smoothed for gradual changes)
- **Wind Direction**: 0-360 degrees
- **Temperature**: Celsius
- **Humidity**: Percentage

Wind speed is normalized to 0-1 range for MIDI control.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
