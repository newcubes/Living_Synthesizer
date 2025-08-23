#!/usr/bin/env python3
import subprocess
import os

print("=== RTL-SDR Hardware Test ===")

# Test 1: Check if RTL-SDR device exists
print("1. Checking for RTL-SDR devices...")
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
    print("USB devices:")
    for line in result.stdout.split('\n'):
        if 'rtl' in line.lower() or 'sdr' in line.lower() or 'dvb' in line.lower():
            print(f"  -> {line}")
    if 'rtl' not in result.stdout.lower():
        print("  No RTL-SDR devices found in USB list")
except Exception as e:
    print(f"Error running lsusb: {e}")

# Test 2: Check device permissions
print("\n2. Checking device permissions...")
try:
    result = subprocess.run(['ls', '-la', '/dev/bus/usb/'], capture_output=True, text=True, timeout=5)
    print("USB device permissions:")
    for line in result.stdout.split('\n'):
        if '001' in line or '002' in line:  # Common USB bus numbers
            print(f"  {line}")
except Exception as e:
    print(f"Error checking device permissions: {e}")

# Test 3: Check if user is in the right groups
print("\n3. Checking user groups...")
try:
    result = subprocess.run(['groups'], capture_output=True, text=True, timeout=5)
    print(f"User groups: {result.stdout.strip()}")
    if 'dialout' in result.stdout or 'usb' in result.stdout:
        print("  User is in dialout or usb group")
    else:
        print("  User might need to be added to dialout group")
except Exception as e:
    print(f"Error checking groups: {e}")

# Test 4: Try rtl_test command
print("\n4. Testing rtl_test...")
try:
    result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=10)
    print(f"rtl_test output: {result.stdout}")
    print(f"rtl_test stderr: {result.stderr}")
    print(f"rtl_test return code: {result.returncode}")
except FileNotFoundError:
    print("rtl_test not found - RTL-SDR tools might not be installed")
except Exception as e:
    print(f"Error running rtl_test: {e}")

# Test 5: Check if rtl_433 can see devices
print("\n5. Testing rtl_433 device detection...")
try:
    result = subprocess.run(['./rtl_433', '-l', 'list'], capture_output=True, text=True, timeout=10)
    print(f"rtl_433 device list: {result.stdout}")
    print(f"rtl_433 stderr: {result.stderr}")
except Exception as e:
    print(f"Error running rtl_433 device list: {e}")

print("\n=== Hardware Test Complete ===")
