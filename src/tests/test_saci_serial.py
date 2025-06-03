#!/usr/bin/env python3
"""
Test script for SACI Serial Reader
Sistema Guardião - Fire Prevention and Detection
Author: Yan Cotta
Date: May 30, 2025

Test the parsing functionality of `SACISerialReader.parse_sensor_data`
without requiring actual ESP32 hardware connected. This script focuses on
unit testing the data parsing logic with various input string formats.
"""

# Standard library imports
import sys
import os
from datetime import datetime # For printing test execution date

# Add the project root to the Python path to allow importing from `src`
# This assumes the test script is in `src/tests/` and modules are in `src/data_collection/` etc.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Now import the module to be tested
from src.data_collection.saci_serial_reader import SACISerialReader

def test_data_parsing() -> bool:
    """
    Tests the data parsing functionality of SACISerialReader.parse_sensor_data.
    
    It iterates through a predefined list of test cases, each containing an
    input string (simulating a line from the serial port) and an expected
    dictionary output (or None if the line should not be parsed).
    
    The function prints detailed PASS/FAIL results for each test case and
    an overall summary. The keys in the 'expected' dictionary must match
    the keys returned by the current implementation of `parse_sensor_data()`.

    Returns:
        bool: True if all test cases pass, False otherwise.
    """

    # Create a SACISerialReader instance. The port is irrelevant for this test
    # as we are only testing the parse_sensor_data method directly.
    reader = SACISerialReader(port="/dev/null_test") # Dummy port for testing

    # Test cases:
    # Each case includes an 'input' string and 'expected' dictionary or None.
    # Expected keys must match SACISerialReader.parse_sensor_data output:
    # 'temperature_celsius', 'humidity_percent', 'smoke_adc', 'risk_level'.
    # 'timestamp' and 'raw_line' are also returned but not checked here for simplicity,
    # as 'timestamp' is dynamic and 'raw_line' is the input itself.
    test_cases = [
        {
            "input": "Temp: 25.5 C, Hum: 60.0 %, Smoke: 450, Risk: LOW",
            "expected": {
                "temperature_celsius": 25.5,
                "humidity_percent": 60.0,
                "smoke_adc": 450,
                "risk_level": "LOW"
            },
            "description": "Valid data line with all fields including risk."
        },
        {
            "input": "Temp: 35.2 C, Hum: 25.0 %, Smoke: 600, Risk: HIGH",
            "expected": {
                "temperature_celsius": 35.2,
                "humidity_percent": 25.0,
                "smoke_adc": 600,
                "risk_level": "HIGH"
            },
            "description": "Another valid data line with different values."
        },
        {
            "input": "Temp: ERROR C, Hum: 45.0 %, Smoke: 300", # Risk not present
            "expected": {
                "temperature_celsius": None,
                "humidity_percent": 45.0,
                "smoke_adc": 300,
                "risk_level": "N/A" # SACISerialReader defaults to "N/A" if risk is missing
            },
            "description": "Data line with 'ERROR' for temperature and no risk level."
        },
        {
            "input": "Temp: 22.1 C, Hum: ERROR %, Smoke: ERROR, Risk: MEDIUM",
            "expected": {
                "temperature_celsius": 22.1,
                "humidity_percent": None,
                "smoke_adc": None,
                "risk_level": "MEDIUM" # Risk level is present
            },
            "description": "Data line with 'ERROR' for humidity and smoke."
        },
        {
            "input": "Temp: -5.0 C, Hum: 10.5 %, Smoke: 100, Risk: MINIMAL",
            "expected": {
                "temperature_celsius": -5.0,
                "humidity_percent": 10.5,
                "smoke_adc": 100,
                "risk_level": "MINIMAL"
            },
            "description": "Valid data with negative temperature."
        },
        {
            "input": "SACI MVP starting sensor monitoring...", # Informational line
            "expected": None,
            "description": "Non-sensor informational line."
        },
        {
            "input": "[INFO] Memory cleanup - Free: 50000 bytes", # Log-style line
            "expected": None,
            "description": "Log-style informational line."
        },
        {
            "input": "This is a malformed line.", # Completely different format
            "expected": None,
            "description": "Malformed line, not matching sensor data pattern."
        },
        {
            "input": "Temp: C, Hum: %, Smoke: , Risk:", # Empty values
            "expected": None, # Should fail parsing due to regex not matching empty values for numbers
            "description": "Line with empty values for sensors."
        }
    ]
    
    print("--- Testing SACISerialReader.parse_sensor_data() ---")
    print("=" * 70)
    
    all_tests_passed = True # Flag to track overall test success
    
    # Iterate through each test case
    for i, test_case in enumerate(test_cases, 1):
        input_line = test_case["input"]
        expected_output = test_case["expected"]
        description = test_case["description"]
        
        print(f"\nTest Case {i}: {description}")
        print(f"  Input Line: \"{input_line}\"")
        
        # Call the parsing function from SACISerialReader
        parsed_result = reader.parse_sensor_data(input_line)
        
        # Validate the result
        if expected_output is None:
            # Case: Expected not to parse (e.g., informational lines, malformed data)
            if parsed_result is None:
                print(f"  Result: Correctly returned None.")
                print("  ✓ PASS")
            else:
                print(f"  Result: Incorrectly parsed data. Expected None, but got: {parsed_result}")
                print("  ✗ FAIL")
                all_tests_passed = False
        else:
            # Case: Expected to parse successfully
            if parsed_result is None:
                print(f"  Result: Failed to parse. Expected data dictionary, but got None.")
                print(f"  Expected: {expected_output}")
                print("  ✗ FAIL")
                all_tests_passed = False
            else:
                # Compare each field in the parsed result against the expected dictionary
                current_case_passed = True
                # Check all keys present in 'expected_output'
                for key, expected_value in expected_output.items():
                    actual_value = parsed_result.get(key) # Use .get() for safer access
                    if actual_value != expected_value:
                        # Detailed message for mismatched field
                        print(f"    Field '{key}': Mismatch. Expected: '{expected_value}' "
                              f"(type {type(expected_value).__name__}), "
                              f"Got: '{actual_value}' (type {type(actual_value).__name__})")
                        current_case_passed = False
                
                # Optionally, check if parsed_result contains unexpected keys (not in MVP scope)
                # for key in parsed_result:
                #    if key not in expected_output and key not in ['timestamp', 'raw_line']:
                #        print(f"    Field '{key}': Unexpected key in result.")
                #        current_case_passed = False

                if current_case_passed:
                    print(f"  Result: All checked fields matched expected values.")
                    # Optionally print full parsed result for verification, excluding dynamic timestamp for brevity
                    # relevant_parsed_info = {k: v for k, v in parsed_result.items() if k != 'timestamp'}
                    # print(f"  Parsed Data (excluding timestamp): {relevant_parsed_info}")
                    print("  ✓ PASS")
                else:
                    all_tests_passed = False # Mark overall failure
                    print(f"  Result: One or more fields did not match. Full parsed data: {parsed_result}")
                    print("  ✗ FAIL (details above)")

    print("\n" + "=" * 70)
    if all_tests_passed:
        print("✓ ALL DATA PARSING TESTS PASSED SUCCESSFULLY!")
    else:
        print("✗ SOME DATA PARSING TESTS FAILED. Please review the output above.")
    print("=" * 70)
    return all_tests_passed

def simulate_esp32_output() -> None:
    """
    Simulates a stream of diverse ESP32 output lines for manual observation
    of how `SACISerialReader.parse_sensor_data` handles them.

    This function is primarily for demonstration and visual checking during development,
    rather than being an automated test with assertions. It prints the raw lines
    and then shows how SACISerialReader would parse and format them if they
    were sensor data lines.
    """
    # Sample lines that might come from an ESP32 device, including valid data,
    # informational messages, and potential error outputs.
    sample_esp32_lines = [
        "SISTEMA GUARDIÃO - SACI MVP - Initializing...", # Boot message
        "ESP32 Board ID: XYZ-123-PROG",                 # Device info
        "DHT22 Sensor: Initialized OK.",                 # Sensor status
        "MQ-135 Sensor: Initialized OK.",                # Sensor status
        "[INFO] Sensor calibration values loaded from NVM.", # Firmware log
        "SACI MVP - Sensors initialized successfully",      # Confirmation
        "SACI MVP starting sensor monitoring...",           # Status update
        "Format: Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL", # Info line
        "-" * 60,                                           # Separator line
        "Temp: 24.5 C, Hum: 55.0 %, Smoke: 320, Risk: LOW", # Valid data
        "Temp: 25.1 C, Hum: 54.5 %, Smoke: 325, Risk: LOW", # Valid data
        "Temp: ERROR C, Hum: 52.0 %, Smoke: 340, Risk: UNKNOWN", # Data with error, risk specified
        "Temp: 28.5 C, Hum: 48.0 %, Smoke: 380",           # Valid data, risk not specified
        "Some debug message from ESP32 firmware.",          # Non-data, firmware debug
        "Temp: 32.0 C, Hum: 35.0 %, Smoke: 520, Risk: HIGH", # Valid data
        "[WARN] Low battery detected on sensor node! Voltage: 3.1V", # Warning from ESP32
        "Temp: 29.0 C, Hum: ERROR %, Smoke: ERROR", # Multiple errors, no risk
        "DHT22 read error: Checksum mismatch",             # Specific sensor error message
    ]
    
    print("\n--- Simulating ESP32 Output Stream & Parsing ---")
    print("=" * 70)
    
    # Create a reader instance (port is not used for this simulation)
    reader = SACISerialReader(port="/dev/null_simulation")
    
    for line in sample_esp32_lines:
        print(f"\nESP32 Sent -> \"{line}\"") # Print the raw line as if from ESP32
        
        # Attempt to parse the line using the reader's method
        parsed_data_dict = reader.parse_sensor_data(line)
        
        if parsed_data_dict:
            # If data is parsed, print it using the reader's formatted output method.
            # Note: print_formatted_data is part of SACISerialReader and expects
            # the dictionary keys as returned by parse_sensor_data.
            print("  Reader Parsed & Formatted -> ", end="")
            reader.print_formatted_data(parsed_data_dict)
        else:
            # If not parsed, indicate that (e.g., it's an info line or malformed)
            print("  Reader Result -> (Line was not parsed as standard sensor data)")

    print("\n" + "=" * 70)
    print("--- ESP32 Output Simulation Finished ---")


def main() -> None:
    """
    Main function to orchestrate the execution of tests for `SACISerialReader`.

    Currently, it performs the following:
    1. Runs automated data parsing tests (`test_data_parsing`).
    2. Shows a simulation of ESP32 output and how it's processed, for
       manual/visual verification (`simulate_esp32_output`).
    3. Prints a summary of the automated test results and reminders for
       testing with actual hardware.
    """
    print("===== SACI MVP - Serial Reader Test Suite =====")
    print(f"Test Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70) # Use a consistent separator length
    
    # Execute the automated data parsing tests
    parsing_tests_successful = test_data_parsing()
    
    print("\n" + "=" * 70)
    
    # Run the ESP32 output simulation for visual inspection.
    # This is not an automated test but helps in understanding behavior with diverse inputs.
    simulate_esp32_output()
    
    # Final summary of automated test results
    print("\n" + "=" * 70)
    print("===== Test Suite Summary =====")
    if parsing_tests_successful:
        print("  ✓ Data Parsing Tests: ALL PASSED")
    else:
        print("  ✗ Data Parsing Tests: SOME FAILED (see details above for specifics)")

    print("\n--- End of Test Suite ---")
    print("\nReminder for testing with actual hardware:")
    print("  1. Ensure `saci_sensor_node.py` (MicroPython script) is running on your ESP32.")
    print("  2. Connect the ESP32 to this machine via a USB serial connection.")
    print("  3. Execute the main serial reader application, for example:")
    print("     python src/data_collection/saci_serial_reader.py YOUR_SERIAL_PORT_HERE")
    print("     (Replace YOUR_SERIAL_PORT_HERE with the actual port, e.g., /dev/ttyUSB0 or COM3)")

if __name__ == "__main__":
    # This block ensures that main() is called only when the script is run directly.
    main()
