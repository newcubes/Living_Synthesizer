#!/usr/bin/env python3
"""
Demo script showing different smoothing profiles for wind data.

This script demonstrates how different smoothing parameters affect
the responsiveness and smoothness of wind data for MIDI control.
"""

import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitor import WS2000Monitor

def demo_smoothing_profiles():
    """Demonstrate different smoothing profiles"""
    
    print("=== Wind Smoothing Profile Demo ===")
    print("This demo shows how different smoothing profiles affect LFO control.")
    print()
    
    # Create monitor with responsive profile
    print("1. Testing 'responsive' profile (fast response, less smooth):")
    monitor = WS2000Monitor(smoothing_profile='responsive')
    print(f"   Profile info: {monitor.get_smoothing_info()}")
    print()
    
    # Simulate some wind readings
    test_readings = [2.0, 5.0, 8.0, 3.0, 7.0, 4.0, 9.0, 6.0]
    
    for i, reading in enumerate(test_readings):
        print(f"   Reading {i+1}: {reading} mph")
        monitor.wind_smoother.add_wind_reading(reading)
        
        # Show smoothed values over time
        for step in range(10):
            smoothed = monitor.wind_smoother.get_smoothed_value()
            normalized = monitor.wind_smoother.get_normalized_value()
            print(f"     Step {step}: {smoothed:.2f} mph -> {normalized:.3f} (MIDI)")
            time.sleep(0.1)
        print()
    
    print("2. Testing 'ambient' profile (slow response, very smooth):")
    monitor.set_smoothing_profile('ambient')
    print(f"   Profile info: {monitor.get_smoothing_info()}")
    print()
    
    for i, reading in enumerate(test_readings):
        print(f"   Reading {i+1}: {reading} mph")
        monitor.wind_smoother.add_wind_reading(reading)
        
        # Show smoothed values over time
        for step in range(10):
            smoothed = monitor.wind_smoother.get_smoothed_value()
            normalized = monitor.wind_smoother.get_normalized_value()
            print(f"     Step {step}: {smoothed:.2f} mph -> {normalized:.3f} (MIDI)")
            time.sleep(0.1)
        print()
    
    print("3. Custom parameters (balanced for LFO):")
    monitor.set_custom_smoothing(
        buffer_size=5,
        interpolation_steps=80,
        response_speed=0.6,
        smoothing_type='exponential'
    )
    print(f"   Custom info: {monitor.get_smoothing_info()}")
    print()
    
    print("=== Profile Comparison ===")
    print("Available profiles:")
    print("  'responsive': Fast response, good for rhythmic LFOs")
    print("  'balanced':   Default, good for most applications")
    print("  'smooth':     Slower response, very smooth transitions")
    print("  'ambient':    Very slow response, perfect for ambient music")
    print()
    print("Usage in your code:")
    print("  monitor = WS2000Monitor(smoothing_profile='responsive')")
    print("  monitor.set_smoothing_profile('ambient')  # Change on the fly")

if __name__ == "__main__":
    demo_smoothing_profiles()
