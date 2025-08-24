#!/usr/bin/env python3
"""
Intensity Signal to Synth Integration

Simplified version that only controls LFO1 Speed with wind speed.
Wind speed range: 0-15 MPH → LFO rate: 0-127
"""

import sys
import os
import time

# Add src and midi to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'midi'))

from src.monitor import WS2000Monitor
from midi.synth_control import SynthControl
import threading
import time

class SmoothRampController:
    """
    Smooth ramping controller that transitions between values over 8 seconds.
    Prevents audible jumps when new wind values are received.
    """
    
    def __init__(self, ramp_duration=8.0, update_rate=0.1):
        self.ramp_duration = ramp_duration  # seconds
        self.update_rate = update_rate      # seconds between updates
        self.current_value = 0.0
        self.target_value = 0.0
        self.start_value = 0.0
        self.ramp_start_time = None
        self.is_ramping = False
        self.lock = threading.Lock()
        
        # Start the ramping thread
        self.running = True
        self.ramp_thread = threading.Thread(target=self._ramp_loop, daemon=True)
        self.ramp_thread.start()
    
    def set_target(self, new_target):
        """Set a new target value and start ramping"""
        with self.lock:
            if abs(new_target - self.target_value) > 0.1:  # Only ramp if change is significant
                self.start_value = self.current_value
                self.target_value = new_target
                self.ramp_start_time = time.time()
                self.is_ramping = True
                print(f"🎯 New target: {new_target:.1f} MPH (ramping from {self.start_value:.1f})")
    
    def get_current_value(self):
        """Get the current smoothed value"""
        with self.lock:
            return self.current_value
    
    def _ramp_loop(self):
        """Main ramping loop that runs in background thread"""
        while self.running:
            with self.lock:
                if self.is_ramping and self.ramp_start_time:
                    elapsed = time.time() - self.ramp_start_time
                    progress = min(elapsed / self.ramp_duration, 1.0)
                    
                    # Smooth easing function (ease-in-out)
                    if progress < 0.5:
                        ease_progress = 2 * progress * progress
                    else:
                        ease_progress = 1 - 2 * (1 - progress) * (1 - progress)
                    
                    # Interpolate between start and target
                    self.current_value = self.start_value + (self.target_value - self.start_value) * ease_progress
                    
                    # Check if ramp is complete
                    if progress >= 1.0:
                        self.current_value = self.target_value
                        self.is_ramping = False
                        print(f"✅ Ramp complete: {self.current_value:.1f} MPH")
            
            time.sleep(self.update_rate)
    
    def stop(self):
        """Stop the ramping thread"""
        self.running = False
        if self.ramp_thread.is_alive():
            self.ramp_thread.join(timeout=1.0)

class IntensitySignalToSynth:
    """
    Simplified integration that only controls LFO1 Speed with wind speed.
    Wind speed range: 0-15 MPH → LFO rate: 0-127
    Includes 8-second smooth ramping between values.
    """
    
    def __init__(self, smoothing_profile='balanced', midi_port='hw:1,0,0', max_intensity=15.0):
        # Initialize environmental monitor
        self.monitor = WS2000Monitor(smoothing_profile=smoothing_profile)
        
        # Initialize synthesizer controller
        self.synth = SynthControl(midi_port=midi_port, debug=True, max_intensity=max_intensity)
        
        # Initialize smooth ramping controller
        self.ramp_controller = SmoothRampController(ramp_duration=8.0, update_rate=0.1)
        
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
        print(f"  Smooth ramping: 8-second transitions between wind values")
    
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
        
        # Set new target for smooth ramping
        self.ramp_controller.set_target(wind_speed)
        
        # Get current smoothed value
        smoothed_wind = self.ramp_controller.get_current_value()
        
        # Control LFO1 Speed only (smoothed wind speed → rate, upper half of CC range)
        if self.lfo_config['lfo1']['enabled']:
            # Map smoothed wind speed to upper half of CC range (64-127)
            wind_normalized = min(smoothed_wind / self.synth.max_intensity, 1.0)
            lfo_rate = int(64 + (wind_normalized * 63))  # 64-127 range
            self.synth.send_midi_cc(28, lfo_rate)  # LFO1 Speed CC 28 on Channel 2
            
            print(f"🎛️  LFO1 Speed Control (Smoothed):")
            print(f"    Raw Wind: {wind_speed:.1f} MPH → Smoothed: {smoothed_wind:.1f} MPH")
            print(f"    LFO Rate: {lfo_rate}/127 (Range: 64-127)")
        
        # Print summary of current LFO state
        print(f"\n🎵 LFO SUMMARY:")
        print(f"    LFO1: Rate={lfo_rate}/127 (Smoothed: {smoothed_wind:.1f} MPH) | Fixed Depth: 32/63")
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
            self.ramp_controller.stop()
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
    parser.add_argument('--max-intensity', type=float, default=15.0,
                       help='Maximum wind speed for full LFO intensity (default: 15.0 MPH)')
    
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
