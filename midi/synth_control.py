#!/usr/bin/env python3
"""
Synthesizer MIDI Control Module

Controls synthesizer LFO parameters via MIDI CC messages.
Maps environmental signals to LFO rate for signal-driven synthesis.
"""

import subprocess
import time
import math

class SynthControl:
    """
    Controls synthesizer LFO parameters via MIDI CC messages.
    
    Maps environmental data to LFO controls:
    - Wind speed → LFO rate (CC 28/30)
    - Wind direction → LFO waveform (CC 111/117) 
    - Temperature → LFO depth (CC 29/31)
    """
    
    def __init__(self, midi_port='hw:1,0,0', debug=True, max_intensity=25.0):
        self.midi_port = midi_port
        self.debug = debug
        self.max_intensity = max_intensity  # Maximum wind speed for full LFO intensity
        
        # Synthesizer LFO CC mappings
        self.LFO_CC_MAPPINGS = {
            'lfo1': {
                'speed': 28,      # LFO1 Speed MSB
                'speed_lsb': 60,  # LFO1 Speed LSB
                'depth': 29,      # LFO1 Depth MSB
                'depth_lsb': 61,  # LFO1 Depth LSB
                'waveform': 111,  # LFO1 Waveform
                'destination': 110, # LFO1 Destination
                'multiplier': 108,  # LFO1 Multiplier
                'fade': 109,        # LFO1 Fade
                'start_phase': 112, # LFO1 Start Phase
                'trig_mode': 113    # LFO1 Trig Mode
            },
            'lfo2': {
                'speed': 30,      # LFO2 Speed MSB
                'speed_lsb': 62,  # LFO2 Speed LSB
                'depth': 31,      # LFO2 Depth MSB
                'depth_lsb': 63,  # LFO2 Depth LSB
                'waveform': 117,  # LFO2 Waveform
                'destination': 116, # LFO2 Destination
                'multiplier': 114,  # LFO2 Multiplier
                'fade': 115,        # LFO2 Fade
                'start_phase': 118, # LFO2 Start Phase
                'trig_mode': 119    # LFO2 Trig Mode
            }
        }
        
        # LFO Waveform mappings (based on wind direction)
        self.WAVEFORM_MAPPINGS = {
            'north': 0,      # Triangle (0-22.5°)
            'northeast': 1,  # Sine (22.5-67.5°)
            'east': 2,       # Square (67.5-112.5°)
            'southeast': 3,  # Sawtooth (112.5-157.5°)
            'south': 4,      # Exponential (157.5-202.5°)
            'southwest': 5,  # Ramp (202.5-247.5°)
            'west': 6,       # Random (247.5-292.5°)
            'northwest': 0   # Triangle (292.5-337.5°)
        }
        
        # Wind speed to LFO rate mapping
        self.wind_speed_range = (0, self.max_intensity)  # MPH
        self.lfo_rate_range = (0, 127)   # MIDI CC values
        
        print(f"DigitoneControl initialized on port: {midi_port}")
        print(f"Max intensity: {self.max_intensity} MPH → Full LFO rate (127)")
        print(f"Wind speed range: 0-{self.max_intensity} MPH → LFO rate: 0-127")
        
    def send_midi_cc(self, cc_number, value):
        """Send MIDI CC message to Digitone"""
        # Clamp value to 0-127 range
        midi_value = max(0, min(127, int(value)))
        
        # Format MIDI message (B0 = CC, followed by CC number and value)
        midi_message = f"B0 {cc_number:02x} {midi_value:02x}"
        
        if self.debug:
            print(f"📤 MIDI CC: {cc_number} = {midi_value}/127 ({midi_message})")
        
        try:
            subprocess.run(['amidi', '-p', self.midi_port, '-S', midi_message], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to send MIDI CC {cc_number}: {e}")
        except FileNotFoundError:
            print("❌ Error: 'amidi' command not found. Install alsa-utils package.")
    
    def map_wind_speed_to_lfo_rate(self, wind_speed_mph):
        """Map wind speed (MPH) to LFO rate (0-127)"""
        # Clamp wind speed to range
        clamped_wind = max(self.wind_speed_range[0], 
                          min(self.wind_speed_range[1], wind_speed_mph))
        
        # Linear mapping from wind speed to LFO rate
        normalized = (clamped_wind - self.wind_speed_range[0]) / (self.wind_speed_range[1] - self.wind_speed_range[0])
        lfo_rate = int(normalized * self.lfo_rate_range[1])
        
        if self.debug:
            print(f"🌪️  Wind: {wind_speed_mph:.1f} MPH → LFO Rate: {lfo_rate}/127")
            print(f"    Clamped: {clamped_wind:.1f} MPH | Normalized: {normalized:.3f} | Range: 0-{self.max_intensity} MPH")
        
        return lfo_rate
    
    def map_wind_direction_to_waveform(self, wind_direction_deg):
        """Map wind direction (degrees) to LFO waveform"""
        # Normalize direction to 0-360
        direction = wind_direction_deg % 360
        
        # Map to 8 directions
        if direction < 22.5 or direction >= 337.5:
            direction_name = 'north'
        elif direction < 67.5:
            direction_name = 'northeast'
        elif direction < 112.5:
            direction_name = 'east'
        elif direction < 157.5:
            direction_name = 'southeast'
        elif direction < 202.5:
            direction_name = 'south'
        elif direction < 247.5:
            direction_name = 'southwest'
        elif direction < 292.5:
            direction_name = 'west'
        else:
            direction_name = 'northwest'
        
        waveform = self.WAVEFORM_MAPPINGS[direction_name]
        
        if self.debug:
            print(f"🧭 Wind Direction: {wind_direction_deg}° ({direction_name}) → Waveform: {waveform}")
            print(f"    Waveforms: 0=Triangle, 1=Sine, 2=Square, 3=Saw, 4=Exp, 5=Ramp, 6=Random")
        
        return waveform
    
    def map_temperature_to_depth(self, temperature_c):
        """Map temperature (Celsius) to LFO depth"""
        # Map temperature range (0-40°C) to depth range (0-63)
        temp_range = (0, 40)
        depth_range = (0, 63)
        
        clamped_temp = max(temp_range[0], min(temp_range[1], temperature_c))
        normalized = (clamped_temp - temp_range[0]) / (temp_range[1] - temp_range[0])
        depth = int(normalized * depth_range[1])
        
        if self.debug:
            print(f"🌡️  Temperature: {temperature_c}°C → LFO Depth: {depth}/63")
            print(f"    Range: 0-40°C → 0-63 depth | Normalized: {normalized:.3f}")
        
        return depth
    
    def control_lfo(self, lfo_number, wind_speed_mph, wind_direction_deg=None, 
                   temperature_c=None, depth_override=None):
        """Control LFO parameters based on weather data"""
        if lfo_number not in [1, 2]:
            raise ValueError("LFO number must be 1 or 2")
        
        lfo_key = f'lfo{lfo_number}'
        cc_mappings = self.LFO_CC_MAPPINGS[lfo_key]
        
        print(f"\n🎛️  LFO{lfo_number} Control:")
        print(f"    CC Speed: {cc_mappings['speed']} | CC Waveform: {cc_mappings['waveform']} | CC Depth: {cc_mappings['depth']}")
        
        # Map wind speed to LFO rate
        lfo_rate = self.map_wind_speed_to_lfo_rate(wind_speed_mph)
        self.send_midi_cc(cc_mappings['speed'], lfo_rate)
        
        # Map wind direction to waveform (if provided)
        if wind_direction_deg is not None:
            waveform = self.map_wind_direction_to_waveform(wind_direction_deg)
            self.send_midi_cc(cc_mappings['waveform'], waveform)
        
        # Map temperature to depth (if provided)
        if temperature_c is not None:
            depth = self.map_temperature_to_depth(temperature_c)
            self.send_midi_cc(cc_mappings['depth'], depth)
        elif depth_override is not None:
            self.send_midi_cc(cc_mappings['depth'], depth_override)
    
    def set_lfo_destination(self, lfo_number, destination_cc):
        """Set LFO destination (filter cutoff, pitch, amp, etc.)"""
        if lfo_number not in [1, 2]:
            raise ValueError("LFO number must be 1 or 2")
        
        lfo_key = f'lfo{lfo_number}'
        cc_mappings = self.LFO_CC_MAPPINGS[lfo_key]
        
        self.send_midi_cc(cc_mappings['destination'], destination_cc)
        
        if self.debug:
            print(f"LFO{lfo_number} Destination set to CC: {destination_cc}")
    
    def set_lfo_multiplier(self, lfo_number, multiplier):
        """Set LFO tempo multiplier"""
        if lfo_number not in [1, 2]:
            raise ValueError("LFO number must be 1 or 2")
        
        lfo_key = f'lfo{lfo_number}'
        cc_mappings = self.LFO_CC_MAPPINGS[lfo_key]
        
        self.send_midi_cc(cc_mappings['multiplier'], multiplier)
        
        if self.debug:
            print(f"LFO{lfo_number} Multiplier set to: {multiplier}")
    
    def get_weather_mapping_info(self, wind_speed_mph, wind_direction_deg, temperature_c):
        """Get mapping information for debugging"""
        return {
            'wind_speed_mph': wind_speed_mph,
            'lfo_rate': self.map_wind_speed_to_lfo_rate(wind_speed_mph),
            'wind_direction_deg': wind_direction_deg,
            'waveform': self.map_wind_direction_to_waveform(wind_direction_deg),
            'temperature_c': temperature_c,
            'depth': self.map_temperature_to_depth(temperature_c)
        }

# Example usage
if __name__ == "__main__":
    # Create synthesizer controller
    synth = SynthControl(debug=True)
    
    # Test wind speed mapping
    print("Testing wind speed to LFO rate mapping:")
    for wind_speed in [0, 5, 10, 15, 20, 25]:
        rate = synth.map_wind_speed_to_lfo_rate(wind_speed)
        print(f"  {wind_speed} MPH → LFO Rate: {rate}")
    
    # Test wind direction mapping
    print("\nTesting wind direction to waveform mapping:")
    for direction in [0, 45, 90, 135, 180, 225, 270, 315]:
        waveform = synth.map_wind_direction_to_waveform(direction)
        print(f"  {direction}° → Waveform: {waveform}")
    
    # Test full LFO control
    print("\nTesting full LFO control:")
    synth.control_lfo(1, wind_speed_mph=12.5, wind_direction_deg=90, temperature_c=25)
