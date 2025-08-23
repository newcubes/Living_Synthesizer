#!/usr/bin/env python3
import subprocess

print("=== USB Device Detection Test ===")

# Check all USB devices
print("1. All USB devices:")
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}")

# Check USB device details
print("\n2. USB device details:")
try:
    result = subprocess.run(['lsusb', '-v'], capture_output=True, text=True, timeout=10)
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if 'Realtek' in line or 'RTL' in line or '2838' in line:
            print(f"Found RTL device: {line}")
            # Print next few lines for more details
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip():
                    print(f"  {lines[j]}")
                else:
                    break
except Exception as e:
    print(f"Error: {e}")

# Check system logs for USB events
print("\n3. Recent USB system messages:")
try:
    result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
    lines = result.stdout.split('\n')
    recent_lines = lines[-50:]  # Last 50 lines
    for line in recent_lines:
        if 'usb' in line.lower() or 'rtl' in line.lower():
            print(f"  {line}")
except Exception as e:
    print(f"Error: {e}")

# Check if device is in /dev
print("\n4. Checking /dev for RTL devices:")
try:
    result = subprocess.run(['ls', '-la', '/dev/'], capture_output=True, text=True, timeout=5)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'rtl' in line.lower() or 'sdr' in line.lower():
            print(f"  {line}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test Complete ===")
