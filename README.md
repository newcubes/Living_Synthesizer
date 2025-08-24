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

# Create monitor with different smoothing profiles
monitor = WS2000Monitor(smoothing_profile='responsive')  # Fast response
monitor = WS2000Monitor(smoothing_profile='ambient')     # Very smooth
monitor = WS2000Monitor(smoothing_profile='balanced')    # Default

# Get continuous weather data
for reading in monitor.start_monitoring():
    wind_speed = reading['wind_speed']      # Raw wind speed (MPH)
    smooth_speed = reading['smooth_speed']  # Smoothed (0-1 range)
    wind_direction = reading['wind_direction']  # Degrees
    temperature = reading['temperature']    # Celsius
    humidity = reading['humidity']          # Percentage

# Change smoothing on the fly
monitor.set_smoothing_profile('ambient')
monitor.set_custom_smoothing(buffer_size=5, response_speed=0.8)
```

### MIDI Control

```python
from midi import SDRModulator, SignalConverter, SynthControl

# Create signal converter
converter = SignalConverter()

# Convert and send environmental data to synthesizer
converter.run()

# Or use dedicated synthesizer control
synth = SynthControl(midi_port='hw:1,0,0')
synth.control_lfo(1, wind_speed_mph=12.5, wind_direction_deg=90, temperature_c=25)
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

## Smoothing Profiles

The system includes configurable smoothing profiles for different musical applications:

### **Responsive Profile** (`smoothing_profile='responsive'`)
- **Buffer**: 3 readings
- **Response**: Fast (0.8)
- **Use case**: Rhythmic LFOs, percussive sounds
- **Latency**: ~1-2 seconds

### **Balanced Profile** (`smoothing_profile='balanced'`) - Default
- **Buffer**: 8 readings  
- **Response**: Medium (0.5)
- **Use case**: General purpose, most applications
- **Latency**: ~2-3 seconds

### **Smooth Profile** (`smoothing_profile='smooth'`)
- **Buffer**: 15 readings
- **Response**: Slow (0.3)
- **Use case**: Pad sounds, evolving textures
- **Latency**: ~3-4 seconds

### **Ambient Profile** (`smoothing_profile='ambient'`)
- **Buffer**: 20 readings
- **Response**: Very slow (0.2)
- **Use case**: Ambient music, atmospheric sounds
- **Latency**: ~4-5 seconds

### **Custom Parameters**
```python
monitor.set_custom_smoothing(
    buffer_size=5,           # Number of readings to average
    interpolation_steps=80,  # Smoothness of transitions
    response_speed=0.6,      # How quickly to respond (0.1-1.0)
    smoothing_type='exponential'  # 'linear', 'exponential', 'gaussian'
)
```

## Synthesizer Integration

The system includes dedicated synthesizer MIDI control for signal-driven synthesis:

### **Wind Speed → LFO Rate Mapping**
- **0 MPH wind** → **Slowest LFO rate** (CC 28/30 = 0)
- **12.5 MPH wind** → **Medium LFO rate** (CC 28/30 = 64)
- **25+ MPH wind** → **Fastest LFO rate** (CC 28/30 = 127)

### **Wind Direction → LFO Waveform**
- **North (0°)** → **Triangle wave**
- **East (90°)** → **Square wave**
- **South (180°)** → **Exponential wave**
- **West (270°)** → **Random wave**

### **Temperature → LFO Depth**
- **0°C** → **No modulation** (CC 29/31 = 0)
- **20°C** → **Medium modulation** (CC 29/31 = 32)
- **40°C** → **Maximum modulation** (CC 29/31 = 63)

### **Usage**
```bash
# Run complete signal-to-synth integration
python3 examples/signal_to_synth.py

# Test without MIDI output
python3 examples/signal_to_synth.py --test

# Use different smoothing profile
python3 examples/signal_to_synth.py --smoothing ambient
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
