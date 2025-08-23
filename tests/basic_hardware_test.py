#!/usr/bin/env python3
import subprocess
import time

print("=== Basic Hardware Debug Test ===")

# Test 1: Check if rtl_433 exists and has permissions
print("1. Checking rtl_433 file:")
try:
    result = subprocess.run(['ls', '-la', './rtl_433'], capture_output=True, text=True, timeout=5)
    print(f"File info: {result.stdout}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try to run rtl_433 version with timeout
print("\n2. Testing rtl_433 version (5 second timeout):")
try:
    result = subprocess.run(['./rtl_433', '--version'], capture_output=True, text=True, timeout=5)
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    print(f"return code: {result.returncode}")
except subprocess.TimeoutExpired:
    print("rtl_433 version check timed out - it's hanging!")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Check if RTL-SDR device is still available
print("\n3. Checking RTL-SDR device:")
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
    lines = result.stdout.split('\n')
    for line in lines:
        if 'realtek' in line.lower() or 'rtl' in line.lower():
            print(f"Found: {line}")
    if 'realtek' not in result.stdout.lower():
        print("No RTL devices found in lsusb")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Try rtl_test again
print("\n4. Testing rtl_test:")
try:
    result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=10)
    print(f"rtl_test output: {result.stdout}")
    print(f"rtl_test stderr: {result.stderr}")
    print(f"rtl_test return code: {result.returncode}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Try a simple rtl_433 command with timeout
print("\n5. Testing simple rtl_433 command (10 second timeout):")
try:
    cmd = ['./rtl_433', '-f', '915M', '-M', 'level', '-Y', 'autolevel']
    print(f"Running: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    print(f"Process started with PID: {process.pid}")
    
    # Wait for 10 seconds
    time.sleep(10)
    
    # Check if process is still running
    if process.poll() is None:
        print("Process is still running after 10 seconds - it's hanging!")
        process.terminate()
        process.wait()
        print("Process terminated")
    else:
        print(f"Process exited with code: {process.returncode}")
        stdout, stderr = process.communicate()
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== Basic Hardware Test Complete ===")
