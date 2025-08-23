#!/usr/bin/env python3
import subprocess
import time

print("=== RTL_433 Simple Test ===")

# Test 1: Check if rtl_433 exists
print("1. Checking if rtl_433 exists...")
try:
    result = subprocess.run(['ls', '-la', './rtl_433'], capture_output=True, text=True, timeout=5)
    print(f"Result: {result.stdout}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check rtl_433 version
print("\n2. Checking rtl_433 version...")
try:
    result = subprocess.run(['./rtl_433', '--version'], capture_output=True, text=True, timeout=10)
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    print(f"return code: {result.returncode}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try a simple rtl_433 command
print("\n3. Trying simple rtl_433 command...")
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
    
    # Wait for 5 seconds
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        print("Process is still running after 5 seconds")
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

print("\n=== Test Complete ===")
