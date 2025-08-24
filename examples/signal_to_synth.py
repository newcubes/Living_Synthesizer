#!/usr/bin/env python3
"""
Signal to Synth Integration

Connects environmental sensor data to synthesizer LFO control for signal-driven synthesis.
"""

import sys
import os
import time

# Add src and midi to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'midi'))

from src.monitor import WS2000Monitor
from midi.synth_control import SynthControl

class SignalToSynth:
    """
    Main integration class that connects environmental monitoring to synthesizer control.
    """
    
    def __init__(self, smoothing_profile='balanced', midi_port='hw:1,0,0', max_intensity=25.0):
        # Initialize environmental monitor
        self.monitor = WS2000Monitor(smoothing_profile=smoothing_profile)
        
        # Initialize synthesizer controller
        self.synth = SynthControl(midi_port=midi_port, debug=True, max_intensity=max_intensity)
        
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
        
        print("Signal to Synth Integration initialized!")
        print(f"  Smoothing profile: {smoothing_profile}")
        print(f"  MIDI port: {midi_port}")
        print(f"  Max intensity: {max_intensity} MPH → Full LFO rate")
        print(f"  LFO1 enabled: {self.lfo_config['lfo1']['enabled']}")
        print(f"  LFO2 enabled: {self.lfo_config['lfo2']['enabled']}")
    
    def setup_lfo_destinations(self):
        """Configure LFO destinations and settings"""
        print("\nSetting up LFO destinations...")
        
        if self.lfo_config['lfo1']['enabled']:
            self.synth.set_lfo_destination(1, self.lfo_config['lfo1']['destination'])
            self.synth.set_lfo_multiplier(1, self.lfo_config['lfo1']['multiplier'])
            print(f"  LFO1 → Filter Cutoff (CC {self.lfo_config['lfo1']['destination']})")
        
        if self.lfo_config['lfo2']['enabled']:
            self.synth.set_lfo_destination(2, self.lfo_config['lfo2']['destination'])
            self.synth.set_lfo_multiplier(2, self.lfo_config['lfo2']['multiplier'])
            print(f"  LFO2 → Resonance (CC {self.lfo_config['lfo2']['destination']})")
    
    def process_signal_data(self, reading):
        """Process environmental signal data and send to synthesizer"""
        wind_speed = reading.get('wind_speed', 0)
        wind_direction = reading.get('wind_direction', 0)
        temperature = reading.get('temperature', 20)  # Default 20°C
        humidity = reading.get('humidity', 50)        # Default 50%
        smooth_speed = reading.get('smooth_speed', 0)
        
        print(f"\n{'='*60}")
        print(f"🌪️  ENVIRONMENTAL SIGNAL DATA:")
        print(f"    Raw Wind: {wind_speed:.1f} MPH | Direction: {wind_direction}°")
        print(f"    Smooth Wind: {smooth_speed:.3f} (0-1) | Temperature: {temperature}°C")
        print(f"    Humidity: {humidity}%")
        print(f"{'='*60}")
        
        # Control LFO1 (wind speed → rate, direction → waveform, temp → depth)
        if self.lfo_config['lfo1']['enabled']:
            self.synth.control_lfo(
                lfo_number=1,
                wind_speed_mph=wind_speed,
                wind_direction_deg=wind_direction,
                temperature_c=temperature,
                depth_override=self.lfo_config['lfo1']['depth_override']
            )
        
        # Control LFO2 (different mapping for variety)
        if self.lfo_config['lfo2']['enabled']:
            # Use smoothed wind speed for LFO2 rate
            smooth_speed_mph = smooth_speed * self.synth.max_intensity  # Convert 0-1 to 0-max_intensity MPH
            self.synth.control_lfo(
                lfo_number=2,
                wind_speed_mph=smooth_speed_mph,
                wind_direction_deg=(wind_direction + 180) % 360,  # Opposite direction
                temperature_c=temperature,
                depth_override=self.lfo_config['lfo2']['depth_override']
            )
        
        # Print summary of current LFO state
        print(f"\n🎵 LFO SUMMARY:")
        print(f"    LFO1: Rate={self.synth.map_wind_speed_to_lfo_rate(wind_speed)}/127 | "
              f"Waveform={self.synth.map_wind_direction_to_waveform(wind_direction)} | "
              f"Depth={self.synth.map_temperature_to_depth(temperature)}/63")
        print(f"    LFO2: Rate={self.synth.map_wind_speed_to_lfo_rate(smooth_speed_mph)}/127 | "
              f"Waveform={self.synth.map_wind_direction_to_waveform((wind_direction + 180) % 360)} | "
              f"Depth={self.synth.map_temperature_to_depth(temperature)}/63")
    
    def run(self):
        """Main run loop - continuously monitor environmental signals and control synthesizer"""
        print("\n🎵 Starting Signal-Driven Synthesizer Control...")
        print("Press Ctrl+C to stop")
        
        # Setup LFO destinations
        self.setup_lfo_destinations()
        
        try:
            # Start environmental monitoring
            for reading in self.monitor.start_monitoring():
                if reading:
                    self.process_signal_data(reading)
                else:
                    print("No environmental signal data received...")
                
                # Small delay to prevent overwhelming MIDI
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping Signal to Synth control...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.monitor.cleanup()
            print("✅ Cleanup complete")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Signal to Synth Integration')
    parser.add_argument('--smoothing', default='balanced', 
                       choices=['responsive', 'balanced', 'smooth', 'ambient'],
                       help='Smoothing profile for environmental data')
    parser.add_argument('--midi-port', default='hw:1,0,0',
                       help='MIDI port for synthesizer')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no MIDI output)')
    parser.add_argument('--max-intensity', type=float, default=25.0,
                       help='Maximum wind speed for full LFO intensity (default: 25.0 MPH)')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Test mode - no MIDI output will be sent")
        # Create test instance without MIDI
        integration = SignalToSynth(args.smoothing, 'test', args.max_intensity)
    else:
        integration = SignalToSynth(args.smoothing, args.midi_port, args.max_intensity)
    
    integration.run()

if __name__ == "__main__":
    main()
