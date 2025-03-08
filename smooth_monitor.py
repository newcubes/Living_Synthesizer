#!/usr/bin/env python3
import json
import subprocess
import datetime
import signal
import sys
import time
import rtmidi
from threading import Thread, Event

class SmoothValue:
    def __init__(self, initial_value=0):
        self.current = initial_value
        self.target = initial_value
        # Interpolate over 1 second (adjust this value to change smoothing time)
        self.steps_per_second = 60  # 60fps update rate
        self.step_size = 0
        
    def set_target(self, new_target):
        """Set new target and calculate step size"""
        self.target = new_target
        # Calculate step size to reach target in 1 second
        self.step_size = (new_target - self.current) / self.steps_per_second
        
    def update(self):
        """Move one step closer to target"""
        if self.current != self.target:
            self.current += self.step_size
            # Snap to target if we're very close
            if abs(self.current - self.target) < abs(self.step_size):
                self.current = self.target
        return self.current

class WeatherToMidi:
    def __init__(self):
        # MIDI setup
        self.midi_out = rtmidi.MidiOut()
        
        # Print available MIDI ports
        ports = self.midi_out.get_ports()
        print("Available MIDI ports:")
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
            
        # Try to find Digitone
        digitone_port = None
        for i, port in enumerate(ports):
            if 'digitone' in port.lower():
                digitone_port = i
                break
        
        if digitone_port is not None:
            self.midi_out.open_port(digitone_port)
            print(f"Connected to Digitone on port {digitone_port}")
        else:
            print("Digitone not found. Please select a MIDI port number:")
            port_num = int(input())
            self.midi_out.open_port(port_num)
        
        # MIDI CC numbers for Digitone LFO parameters
        self.CC_LFO1_SPEED = 102  # Example - adjust for Digitone
        self.CC_LFO1_DEPTH = 103  # Example - adjust for Digitone
        
        # Smooth value handlers
        self.wind_speed = SmoothValue()
        self.wind_dir = SmoothValue()
        
        # Control flags
        self.running = True
        
        # Start interpolation thread
        self.interpolation_thread = Thread(target=self.interpolation_loop)
        self.interpolation_thread.daemon = True
        self.interpolation_thread.start()
    
    def map_value(self, value, in_min, in_max, out_min, out_max):
        """Map value from one range to another"""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def send_midi_cc(self, cc_num, value):
        """Send MIDI CC message"""
        # Ensure value is within MIDI range (0-127)
        value = max(0, min(127, int(value)))
        midi_message = [0xB0, cc_num, value]
        self.midi_out.send_message(midi_message)
    
    def interpolation_loop(self):
        """Continuous interpolation thread"""
        while self.running:
            # Update smooth values
            speed_value = self.wind_speed.update()
            dir_value = self.wind_dir.update()
            
            # Map to MIDI range and send
            lfo_speed = int(self.map_value(speed_value, 0, 50, 0, 127))
            lfo_depth = int(self.map_value(dir_value, 0, 360, 0, 127))
            
            self.send_midi_cc(self.CC_LFO1_SPEED, lfo_speed)
            self.send_midi_cc(self.CC_LFO1_DEPTH, lfo_depth)
            
            # Update at 60fps
            time.sleep(1/60)
    
    def process_weather_data(self, data):
        """Process weather data and update smooth value targets"""
        try:
            # Extract wind data
            wind_speed = data.get('wind_speed_kph', 0)
            wind_dir = data.get('wind_dir_deg', 0)
            
            # Update smooth value targets immediately
            self.wind_speed.set_target(wind_speed)
            self.wind_dir.set_target(wind_dir)
            
            # Print status
            print(f"\nNew Weather Data:")
            print(f"Wind Speed: {wind_speed:.1f} kph")
            print(f"Wind Direction: {wind_dir:.1f}°")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error processing data: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.interpolation_thread.join()
        self.midi_out.close_port()

def monitor_weather_and_midi():
    # Initialize MIDI converter
    midi_converter = WeatherToMidi()
    
    # Command to run rtl_433 with maximum update frequency
    cmd = [
        './rtl_433',
        '-f', '915M',
        '-F', 'json:-',
        '-M', 'level',  # Show signal levels
        '-Y', 'autolevel'  # Auto signal level adjustment
    ]
    
    # Start rtl_433 process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    print("Monitoring weather station and converting to MIDI...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            output = process.stdout.readline()
            if output:
                try:
                    data = json.loads(output)
                    midi_converter.process_weather_data(data)
                except json.JSONDecodeError:
                    continue
                    
    except KeyboardInterrupt:
        print("\nStopping...")
        midi_converter.cleanup()
        process.terminate()

if __name__ == "__main__":
    monitor_weather_and_midi()
