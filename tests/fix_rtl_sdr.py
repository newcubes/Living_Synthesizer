#!/usr/bin/env python3
import subprocess

print("=== RTL-SDR Fix Script ===")

# Check for DVB devices
print("1. Checking for DVB devices:")
try:
    result = subprocess.run(['ls', '-la', '/dev/dvb/'], capture_output=True, text=True, timeout=5)
    print(f"DVB devices: {result.stdout}")
except Exception as e:
    print(f"Error: {e}")

# Check loaded modules
print("\n2. Checking loaded kernel modules:")
try:
    result = subprocess.run(['lsmod'], capture_output=True, text=True, timeout=5)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'rtl' in line.lower() or 'dvb' in line.lower():
            print(f"  {line}")
except Exception as e:
    print(f"Error: {e}")

# Try to load RTL-SDR modules
print("\n3. Loading RTL-SDR modules:")
modules_to_load = [
    'dvb_usb_rtl28xxu',
    'rtl2832',
    'rtl2830'
]

for module in modules_to_load:
    try:
        print(f"  Loading {module}...")
        result = subprocess.run(['sudo', 'modprobe', module], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"    {module} loaded successfully")
        else:
            print(f"    {module} failed to load: {result.stderr}")
    except Exception as e:
        print(f"    Error loading {module}: {e}")

# Check if device appears after loading modules
print("\n4. Checking for RTL devices after loading modules:")
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'realtek' in line.lower() or 'rtl' in line.lower():
            print(f"  Found: {line}")
except Exception as e:
    print(f"Error: {e}")

# Try rtl_test again
print("\n5. Testing RTL-SDR after module load:")
try:
    result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=10)
    print(f"rtl_test output: {result.stdout}")
    print(f"rtl_test stderr: {result.stderr}")
    print(f"rtl_test return code: {result.returncode}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Fix Complete ===")
