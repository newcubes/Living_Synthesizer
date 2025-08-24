#!/usr/bin/env python3
"""
Intensity Signal to Synth Integration

Simplified version that only controls LFO1 Speed with wind speed.
Wind speed range: 0-10 MPH → LFO rate: 0-127
"""

import sys
import os
import time

# Add src and midi to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'midi'))

from src.monitor import WS2000Monitor
from midi.synth_control import SynthControl

class IntensitySignalToSynth:
    """
    Simplified integration that only controls LFO1 Speed with wind speed.
    Wind speed range: 0-10 MPH → LFO rate: 0-127
    """
    
    def __init__(self, smoothing_profile='balanced', midi_port='hw:1,0,0', max_intensity=10.0):
        # Initialize environmental monitor
        self.monitor = WS2000Monitor(smoothing_profile=smoothing_profile)
        
        # Initialize synthesizer controller
        self.synth = SynthControl(midi_port=midi_port, debug=True, max_intensity=max_intensity)
        
        # LFO configuration - Only LFO1 Speed controlled by wind
        self.lfo_config = {
            'lfo1': {
                'enabled': True,
                'destination': 74,  # Filter Cutoff (typical)
                'multiplier': 0,    # No tempo sync
                'depth_override': 32  # Fixed depth (half intensity)
            },
            'lfo2': {
                'enabled': False,   # Disable LFO2
                'destination': 71,  # Resonance (typical)
                'multiplier': 0,    # No tempo sync
                'depth_override': None
            }
        }
        
        print("Intensity Signal to Synth Integration initialized!")
        print(f"  Smoothing profile: {smoothing_profile}")
        print(f"  MIDI port: {midi_port}")
        print(f"  Max intensity: {max_intensity} MPH → Full LFO rate")
        print(f"  LFO1 enabled: {self.lfo_config['lfo1']['enabled']} (Speed only)")
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
        
        # Control LFO1 Speed only (wind speed → rate, upper half of CC range)
        if self.lfo_config['lfo1']['enabled']:
            # Map wind speed to upper half of CC range (64-127)
            wind_normalized = min(wind_speed / self.synth.max_intensity, 1.0)
            lfo_rate = int(64 + (wind_normalized * 63))  # 64-127 range
            self.synth.send_midi_cc(28, lfo_rate)  # LFO1 Speed CC 28 on Channel 2
            
            print(f"🎛️  LFO1 Speed Control (Upper Half):")
            print(f"    Wind: {wind_speed:.1f} MPH → LFO Rate: {lfo_rate}/127 (Range: 64-127)")
        
        # Print summary of current LFO state
        print(f"\n🎵 LFO SUMMARY:")
        print(f"    LFO1: Rate={lfo_rate}/127 (Upper Half: 64-127) | Fixed Depth: 32/63")
        print(f"    LFO2: Disabled")
    
    def run(self):
        """Main run loop - continuously monitor environmental signals and control synthesizer"""
        print("\n🎵 Starting Intensity Signal-Driven Synthesizer Control...")
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
            print("\n🛑 Stopping Intensity Signal to Synth control...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.monitor.cleanup()
            print("✅ Cleanup complete")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intensity Signal to Synth Integration')
    parser.add_argument('--smoothing', default='balanced', 
                       choices=['responsive', 'balanced', 'smooth', 'ambient'],
                       help='Smoothing profile for environmental data')
    parser.add_argument('--midi-port', default='hw:1,0,0',
                       help='MIDI port for synthesizer')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (no MIDI output)')
    parser.add_argument('--max-intensity', type=float, default=10.0,
                       help='Maximum wind speed for full LFO intensity (default: 10.0 MPH)')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Test mode - no MIDI output will be sent")
        # Create test instance without MIDI
        integration = IntensitySignalToSynth(args.smoothing, 'test', args.max_intensity)
    else:
        integration = IntensitySignalToSynth(args.smoothing, args.midi_port, args.max_intensity)
    
    integration.run()

if __name__ == "__main__":
    main()
