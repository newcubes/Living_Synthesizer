#!/usr/bin/env python3
"""
Test LFO Mapping Ranges

Demonstrates the complete flow of weather data to LFO values
with configurable intensity ranges.
"""

import sys
import os

# Add src and midi to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'midi'))

from midi.synth_control import SynthControl

def test_wind_speed_mapping(max_intensity=25.0):
    """Test wind speed to LFO rate mapping"""
    print(f"\n{'='*60}")
    print(f"🌪️  WIND SPEED → LFO RATE MAPPING")
    print(f"Max Intensity: {max_intensity} MPH → Full LFO Rate (127)")
    print(f"{'='*60}")
    
    synth = SynthControl(debug=False, max_intensity=max_intensity)
    
    # Test various wind speeds
    wind_speeds = [0, 2, 5, 8, 10, 12, 15, 18, 20, 22, 25, 30]
    
    for wind_speed in wind_speeds:
        lfo_rate = synth.map_wind_speed_to_lfo_rate(wind_speed)
        percentage = (lfo_rate / 127) * 100
        
        # Visual indicator
        bar_length = 20
        filled_length = int((lfo_rate / 127) * bar_length)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"Wind: {wind_speed:2.0f} MPH → LFO Rate: {lfo_rate:3d}/127 ({percentage:5.1f}%) {bar}")

def test_wind_direction_mapping():
    """Test wind direction to LFO waveform mapping"""
    print(f"\n{'='*60}")
    print(f"🧭 WIND DIRECTION → LFO WAVEFORM MAPPING")
    print(f"{'='*60}")
    
    synth = SynthControl(debug=False)
    
    # Test compass directions
    directions = [
        (0, "North"), (45, "Northeast"), (90, "East"), (135, "Southeast"),
        (180, "South"), (225, "Southwest"), (270, "West"), (315, "Northwest")
    ]
    
    for degrees, name in directions:
        waveform = synth.map_wind_direction_to_waveform(degrees)
        waveform_names = ["Triangle", "Sine", "Square", "Sawtooth", "Exponential", "Ramp", "Random"]
        waveform_name = waveform_names[waveform] if waveform < len(waveform_names) else f"Unknown({waveform})"
        
        print(f"Direction: {degrees:3d}° ({name:10s}) → Waveform: {waveform} ({waveform_name})")

def test_temperature_mapping():
    """Test temperature to LFO depth mapping"""
    print(f"\n{'='*60}")
    print(f"🌡️  TEMPERATURE → LFO DEPTH MAPPING")
    print(f"{'='*60}")
    
    synth = SynthControl(debug=False)
    
    # Test various temperatures
    temperatures = [-5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    
    for temp in temperatures:
        depth = synth.map_temperature_to_depth(temp)
        percentage = (depth / 63) * 100
        
        # Visual indicator
        bar_length = 20
        filled_length = int((depth / 63) * bar_length)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"Temp: {temp:2.0f}°C → LFO Depth: {depth:2d}/63 ({percentage:5.1f}%) {bar}")

def test_complete_mapping():
    """Test complete weather to LFO mapping"""
    print(f"\n{'='*60}")
    print(f"🎵 COMPLETE WEATHER → LFO MAPPING")
    print(f"{'='*60}")
    
    synth = SynthControl(debug=True, max_intensity=20.0)
    
    # Simulate environmental conditions
    environmental_conditions = [
        {"wind_speed": 5, "direction": 0, "temp": 15, "desc": "Calm North"},
        {"wind_speed": 12, "direction": 90, "temp": 25, "desc": "Moderate East"},
        {"wind_speed": 18, "direction": 180, "temp": 35, "desc": "Strong South"},
        {"wind_speed": 25, "direction": 270, "temp": 40, "desc": "Stormy West"},
    ]
    
    for condition in environmental_conditions:
        print(f"\n🌪️  {condition['desc']}:")
        print(f"    Wind: {condition['wind_speed']} MPH, {condition['direction']}°, {condition['temp']}°C")
        
        # Control both LFOs
        synth.control_lfo(
            lfo_number=1,
            wind_speed_mph=condition['wind_speed'],
            wind_direction_deg=condition['direction'],
            temperature_c=condition['temp']
        )
        
        synth.control_lfo(
            lfo_number=2,
            wind_speed_mph=condition['wind_speed'] * 0.8,  # Slightly different
            wind_direction_deg=(condition['direction'] + 180) % 360,
            temperature_c=condition['temp']
        )

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test LFO Mapping Ranges')
    parser.add_argument('--max-intensity', type=float, default=25.0,
                       help='Maximum wind speed for full LFO intensity')
    parser.add_argument('--test', choices=['wind', 'direction', 'temp', 'complete', 'all'],
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    print("🎛️  LFO MAPPING TEST SUITE")
    print(f"Max Intensity: {args.max_intensity} MPH")
    
    if args.test == 'wind' or args.test == 'all':
        test_wind_speed_mapping(args.max_intensity)
    
    if args.test == 'direction' or args.test == 'all':
        test_wind_direction_mapping()
    
    if args.test == 'temp' or args.test == 'all':
        test_temperature_mapping()
    
    if args.test == 'complete' or args.test == 'all':
        test_complete_mapping()
    
    print(f"\n{'='*60}")
    print("✅ LFO Mapping Test Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
