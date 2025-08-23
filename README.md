# Living Synthesizer

A weather-controlled synthesizer system that uses real-time wind data to modulate MIDI parameters.

## Overview

This project connects a WS2000 weather station to a synthesizer (Digitone) using an RTL-SDR device. Wind speed and direction data are used to control LFO parameters in real-time, creating a "living" synthesizer that responds to environmental conditions.

## Components

- **Weather Station**: Fineoffset-WH24 transmitting on 915MHz
- **RTL-SDR**: Nooelec NESDR SMArt v5 for receiving weather data
- **Raspberry Pi**: Processes weather data and sends MIDI commands
- **Synthesizer**: Elektron Digitone (or other MIDI-compatible device)

## Files

### Core Monitoring
- `monitor.py` - Main weather station monitoring script with continuous operation
- `wind_smoother.py` - Smooths wind data for gradual MIDI transitions
- `sdr_to_midi.py` - Converts SDR data to MIDI control signals

### MIDI Control
- `wind_control.py` - Wind-based MIDI control system
- `smooth_monitor.py` - Smooth weather monitoring with MIDI output

### Coordination
- `main.py` - Main coordinator script that runs the entire system

## Setup

1. **Hardware Setup**
   - Connect RTL-SDR to Raspberry Pi
   - Ensure weather station is transmitting on 915MHz
   - Connect MIDI device

2. **Software Setup**
   - Install RTL-SDR tools: `sudo apt install rtl-sdr librtlsdr-dev`
   - Blacklist DVB driver: `echo 'blacklist dvb_usb_rtl28xxu' | sudo tee -a /etc/modprobe.d/blacklist-rtl.conf`
   - Reboot: `sudo reboot`

3. **Testing**
   - Run hardware tests: `python3 tests/test_hardware.py`
   - Test monitoring: `python3 monitor.py`

## Usage

### Basic Monitoring
```bash
python3 monitor.py
```

### Full System
```bash
python3 main.py
```

### Testing
```bash
# Test hardware
python3 tests/test_hardware.py

# Test RTL-SDR
python3 tests/test_rtl_simple.py

# Fix issues
python3 tests/fix_rtl_sdr.py
```

## Troubleshooting

See `tests/README.md` for detailed troubleshooting guides.

Common issues:
- RTL-SDR not detected: Check USB connection and DVB driver blacklist
- No weather data: Verify weather station is transmitting on 915MHz
- MIDI not working: Check MIDI device connections and permissions

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
