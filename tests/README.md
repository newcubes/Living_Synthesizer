# Test Scripts

This directory contains test and debugging scripts for the Living Synthesizer weather station monitoring system.

## Hardware Tests

### `test_hardware.py`
Comprehensive hardware test that checks:
- RTL-SDR device detection
- USB device permissions
- User group membership
- rtl_test functionality
- rtl_433 device detection

### `basic_hardware_test.py`
Basic hardware connectivity test with detailed output.

### `check_usb.py`
USB device detection and system log analysis.

## RTL-SDR Tests

### `test_rtl_simple.py`
Simple RTL-SDR functionality test with timeout handling.

### `test_rtl_433_simple.py`
Tests rtl_433 command execution and timeout behavior.

## Fix Scripts

### `fix_rtl_sdr.py`
Attempts to fix RTL-SDR detection issues by:
- Loading required kernel modules
- Checking DVB device conflicts
- Testing device detection after fixes

## Monitor Tests

### `test_monitor.py`
Tests the WS2000Monitor class functionality.

## Usage

Run tests from the project root directory:

```bash
# Test hardware connectivity
python3 tests/test_hardware.py

# Test RTL-SDR functionality
python3 tests/test_rtl_simple.py

# Fix RTL-SDR issues
python3 tests/fix_rtl_sdr.py

# Test monitor functionality
python3 tests/test_monitor.py
```

## Troubleshooting

If you encounter RTL-SDR issues:

1. Run `test_hardware.py` to identify the problem
2. Use `fix_rtl_sdr.py` to attempt automatic fixes
3. Check USB connections and device permissions
4. Ensure the DVB driver is blacklisted
5. Verify the weather station is transmitting on 915MHz
