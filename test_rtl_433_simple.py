#!/usr/bin/env python3
import subprocess
import time

print("=== RTL_433 Simple Test ===")

# Test 1: Check rtl_433 version (should work)
print("1. Testing rtl_433 version:")
try:
    result = subprocess.run(['./rtl_433', '--version'], capture_output=True, text=True, timeout=5)
    print(f"Version: {result.stdout.strip()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try rtl_433 with a very short timeout
print("\n2. Testing rtl_433 with 5 second timeout:")
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
    
    # Wait for 5 seconds maximum
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        print("Process is still running after 5 seconds - terminating...")
        process.terminate()
        try:
            process.wait(timeout=3)
            print("Process terminated successfully")
        except subprocess.TimeoutExpired:
            print("Process didn't terminate, killing...")
            process.kill()
            process.wait()
    else:
        print(f"Process exited with code: {process.returncode}")
        stdout, stderr = process.communicate()
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try rtl_433 with different frequency
print("\n3. Testing rtl_433 with 100MHz (different frequency):")
try:
    cmd = ['./rtl_433', '-f', '100M', '-M', 'level', '-Y', 'autolevel']
    print(f"Running: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    print(f"Process started with PID: {process.pid}")
    
    # Wait for 5 seconds maximum
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        print("Process is still running after 5 seconds - terminating...")
        process.terminate()
        try:
            process.wait(timeout=3)
            print("Process terminated successfully")
        except subprocess.TimeoutExpired:
            print("Process didn't terminate, killing...")
            process.kill()
            process.wait()
    else:
        print(f"Process exited with code: {process.returncode}")
        stdout, stderr = process.communicate()
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test Complete ===")
