#!/usr/bin/env python3
"""
Weather to Digitone Integration

Connects weather station data to Digitone LFO control for weather-driven synthesis.
"""

import sys
import os
import time

# Add src and midi to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'midi'))

from src.monitor import WS2000Monitor
from midi.digitone_control import DigitoneControl

class WeatherToDigitone:
    """
    Main integration class that connects weather monitoring to Digitone control.
    """
    
    def __init__(self, smoothing_profile='balanced', midi_port='hw:1,0,0'):
        # Initialize weather monitor
        self.monitor = WS2000Monitor(smoothing_profile=smoothing_profile)
        
        # Initialize Digitone controller
        self.digitone = DigitoneControl(midi_port=midi_port, debug=True)
        
        # LFO configuration
        self.lfo_config = {
            'lfo1': {
                'enabled': True,
                'destination': 74,  # Filter Cutoff (typical)
                'multiplier': 0,    # No tempo sync
                'depth_override': None  # Use temperature mapping
            },
            'lfo2': {
                'enabled': True,
                'destination': 71,  # Resonance (typical)
                'multiplier': 0,    # No tempo sync
                'depth_override': None  # Use temperature mapping
            }
        }
        
        print("Weather to Digitone Integration initialized!")
        print(f"  Smoothing profile: {smoothing_profile}")
        print(f"  MIDI port: {midi_port}")
        print(f"  LFO1 enabled: {self.lfo_config['lfo1']['enabled']}")
        print(f"  LFO2 enabled: {self.lfo_config['lfo2']['enabled']}")
    
    def setup_lfo_destinations(self):
        """Configure LFO destinations and settings"""
        print("\nSetting up LFO destinations...")
        
        if self.lfo_config['lfo1']['enabled']:
            self.digitone.set_lfo_destination(1, self.lfo_config['lfo1']['destination'])
            self.digitone.set_lfo_multiplier(1, self.lfo_config['lfo1']['multiplier'])
            print(f"  LFO1 → Filter Cutoff (CC {self.lfo_config['lfo1']['destination']})")
        
        if self.lfo_config['lfo2']['enabled']:
            self.digitone.set_lfo_destination(2, self.lfo_config['lfo2']['destination'])
            self.digitone.set_lfo_multiplier(2, self.lfo_config['lfo2']['multiplier'])
            print(f"  LFO2 → Resonance (CC {self.lfo_config['lfo2']['destination']})")
    
    def process_weather_data(self, reading):
        """Process weather data and send to Digitone"""
        wind_speed = reading.get('wind_speed', 0)
        wind_direction = reading.get('wind_direction', 0)
        temperature = reading.get('temperature', 20)  # Default 20°C
        humidity = reading.get('humidity', 50)        # Default 50%
        
        print(f"\n🌪️ Weather Data:")
        print(f"  Wind: {wind_speed:.1f} MPH, {wind_direction}°")
        print(f"  Temp: {temperature}°C, Humidity: {humidity}%")
        
        # Control LFO1 (wind speed → rate, direction → waveform, temp → depth)
        if self.lfo_config['lfo1']['enabled']:
            self.digitone.control_lfo(
                lfo_number=1,
                wind_speed_mph=wind_speed,
                wind_direction_deg=wind_direction,
                temperature_c=temperature,
                depth_override=self.lfo_config['lfo1']['depth_override']
            )
        
        # Control LFO2 (different mapping for variety)
        if self.lfo_config['lfo2']['enabled']:
            # Use smoothed wind speed for LFO2 rate
            smooth_speed = reading.get('smooth_speed', 0) * 25  # Convert 0-1 to 0-25 MPH
            self.digitone.control_lfo(
                lfo_number=2,
                wind_speed_mph=smooth_speed,
                wind_direction_deg=(wind_direction + 180) % 360,  # Opposite direction
                temperature_c=temperature,
                depth_override=self.lfo_config['lfo2']['depth_override']
            )
    
    def run(self):
        """Main run loop - continuously monitor weather and control Digitone"""
        print("\n🎵 Starting Weather-Driven Digitone Control...")
        print("Press Ctrl+C to stop")
        
        # Setup LFO destinations
        self.setup_lfo_destinations()
        
        try:
            # Start weather monitoring
            for reading in self.monitor.start_monitoring():
                if reading:
                    self.process_weather_data(reading)
                else:
                    print("No weather data received...")
                
                # Small delay to prevent overwhelming MIDI
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping Weather to Digitone control...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.monitor.cleanup()
            print("✅ Cleanup complete")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Weather to Digitone Integration')
    parser.add_argument('--smoothing', default='balanced', 
                       choices=['responsive', 'balanced', 'smooth', 'ambient'],
                       help='Smoothing profile for wind data')
    parser.add_argument('--midi-port', default='hw:1,0,0',
                       help='MIDI port for Digitone')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no MIDI output)')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Test mode - no MIDI output will be sent")
        # Create test instance without MIDI
        integration = WeatherToDigitone(args.smoothing, 'test')
    else:
        integration = WeatherToDigitone(args.smoothing, args.midi_port)
    
    integration.run()

if __name__ == "__main__":
    main()
