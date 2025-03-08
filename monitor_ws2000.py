#!/usr/bin/env python3
import json
import subprocess
import datetime
import signal
import sys
from pprint import pprint

def signal_handler(sig, frame):
    print('\nStopping monitor...')
    sys.exit(0)

def monitor_weather():
    # Command to run rtl_433 with detailed output
    cmd = [
        './rtl_433',
        '-f', '915M',
        '-M', 'level',
        '-M', 'report_meta',
        '-Y', 'autolevel',
        '-F', 'json:-'  # Output JSON to stdout
    ]
    
    # Start rtl_433 process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    print("Monitoring WS-2000 weather station...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            output = process.stdout.readline()
            if output:
                try:
                    data = json.loads(output)
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    # Print raw data for debugging
                    print(f"\n[{timestamp}] Raw Data:")
                    pprint(data)
                    
                    # Print formatted data
                    print("\nFormatted Data:")
                    
                    # Temperature
                    if 'temperature_C' in data:
                        print(f"Temperature: {data['temperature_C']}°C")
                    
                    # Humidity
                    if 'humidity' in data:
                        print(f"Humidity: {data['humidity']}%")
                    
                    # Wind measurements
                    if 'wind_speed_kph' in data:
                        print(f"Wind Speed: {data['wind_speed_kph']} kph")
                    if 'wind_avg_km_h' in data:
                        print(f"Average Wind Speed: {data['wind_avg_km_h']} km/h")
                    if 'wind_max_km_h' in data:
                        print(f"Max Wind Speed: {data['wind_max_km_h']} km/h")
                    if 'wind_dir_deg' in data:
                        print(f"Wind Direction: {data['wind_dir_deg']}°")
                    if 'wind_intensity' in data:
                        print(f"Wind Intensity: {data['wind_intensity']}")
                    
                    # Rain measurements
                    if 'rain_mm' in data:
                        print(f"Rain: {data['rain_mm']} mm")
                    if 'rain_rate_mm_h' in data:
                        print(f"Rain Rate: {data['rain_rate_mm_h']} mm/h")
                    
                    # Signal information
                    if 'signal_strength' in data:
                        print(f"Signal Strength: {data['signal_strength']} dB")
                    if 'signal_quality' in data:
                        print(f"Signal Quality: {data['signal_quality']}")
                    
                    # Battery status
                    if 'battery_ok' in data:
                        print(f"Battery OK: {data['battery_ok']}")
                    
                    print("-" * 50)  # Separator line
                    
                except json.JSONDecodeError:
                    continue
                except KeyError as e:
                    print(f"Missing data field: {e}")
                    continue
                
    except KeyboardInterrupt:
        process.terminate()
        print("\nMonitoring stopped")

if __name__ == "__main__":
    # Setup signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    monitor_weather()
