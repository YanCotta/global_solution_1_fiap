#!/usr/bin/env python3
"""
Test script for SACI Serial Reader
Sistema Guardião - Fire Prevention and Detection
Author: Yan Cotta
Date: May 30, 2025

Test the parsing functionality without requiring actual ESP32 hardware.
"""

import sys
import os

# Add the parent directory to the path to import the serial reader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.saci_serial_reader import SACISerialReader

def test_data_parsing():
    """Test the data parsing functionality with sample data"""
    
    # Create reader instance (port doesn't matter for parsing tests)
    reader = SACISerialReader("/dev/null")
    
    # Test cases with expected sensor data formats
    test_cases = [
        {
            "input": "Temp: 25.5 C, Hum: 60.0 %, Smoke: 450, Risk: LOW",
            "expected": {
                "temperature": 25.5,
                "humidity": 60.0,
                "smoke": 450,
                "risk_level": "LOW"
            }
        },
        {
            "input": "Temp: 35.2 C, Hum: 25.0 %, Smoke: 600, Risk: HIGH",
            "expected": {
                "temperature": 35.2,
                "humidity": 25.0,
                "smoke": 600,
                "risk_level": "HIGH"
            }
        },
        {
            "input": "Temp: ERROR C, Hum: 45.0 %, Smoke: 300",
            "expected": {
                "temperature": None,
                "humidity": 45.0,
                "smoke": 300,
                "risk_level": None
            }
        },
        {
            "input": "Temp: 22.1 C, Hum: ERROR %, Smoke: ERROR",
            "expected": {
                "temperature": 22.1,
                "humidity": None,
                "smoke": None,
                "risk_level": None
            }
        },
        {
            "input": "SACI MVP starting sensor monitoring...",
            "expected": None  # Should not parse
        },
        {
            "input": "[INFO] Memory cleanup - Free: 50000 bytes",
            "expected": None  # Should not parse
        }
    ]
    
    print("Testing SACI Serial Reader Data Parsing")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        input_line = test_case["input"]
        expected = test_case["expected"]
        
        print(f"\nTest {i}: {input_line}")
        
        result = reader.parse_sensor_data(input_line)
        
        if expected is None:
            if result is None:
                print("✓ PASS: Correctly ignored non-sensor data")
            else:
                print(f"✗ FAIL: Expected None, got {result}")
                all_passed = False
        else:
            if result is None:
                print("✗ FAIL: Expected data, got None")
                all_passed = False
            else:
                # Check each expected field
                passed = True
                for key, expected_value in expected.items():
                    if result.get(key) != expected_value:
                        print(f"✗ FAIL: {key} - Expected {expected_value}, got {result.get(key)}")
                        passed = False
                        all_passed = False
                
                if passed:
                    print("✓ PASS: All fields matched")
                    print(f"  Parsed: {result}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        return False

def simulate_esp32_output():
    """Simulate ESP32 output for manual testing"""
    
    sample_outputs = [
        "SISTEMA GUARDIÃO - SACI MVP",
        "Fire Prevention & Detection Sensor Node",
        "ESP32 + DHT22 + MQ-135",
        "SACI MVP - Sensors initialized successfully",
        "SACI MVP starting sensor monitoring...",
        "Format: Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL",
        "-" * 60,
        "Temp: 24.5 C, Hum: 55.0 %, Smoke: 320, Risk: LOW",
        "Temp: 25.1 C, Hum: 54.5 %, Smoke: 325, Risk: LOW",
        "Temp: 26.0 C, Hum: 52.0 %, Smoke: 340, Risk: LOW",
        "Temp: 28.5 C, Hum: 48.0 %, Smoke: 380, Risk: MEDIUM",
        "Temp: 32.0 C, Hum: 35.0 %, Smoke: 520, Risk: HIGH",
        "*** ALERT: HIGH FIRE RISK DETECTED ***",
        "T: 32.0°C, H: 35.0%, S: 520",
        "Temp: ERROR C, Hum: 33.0 %, Smoke: 450, Risk: MEDIUM",
        "DHT22 read error: [Errno 116] ETIMEDOUT",
        "Temp: 29.0 C, Hum: 40.0 %, Smoke: 410, Risk: MEDIUM",
        "[INFO] Memory cleanup - Free: 45000 bytes"
    ]
    
    print("Simulated ESP32 Output:")
    print("=" * 50)
    
    reader = SACISerialReader("/dev/null")
    
    for line in sample_outputs:
        print(f"ESP32: {line}")
        
        # Try to parse each line
        parsed = reader.parse_sensor_data(line)
        if parsed:
            reader.print_formatted_data(parsed)
        
        print()

def main():
    """Main test function"""
    print("SACI MVP - Serial Reader Test Suite")
    print("Date: May 30, 2025")
    print()
    
    # Run parsing tests
    parsing_success = test_data_parsing()
    
    print("\n" + "=" * 70)
    
    # Show simulated output
    simulate_esp32_output()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print(f"Data Parsing Tests: {'PASSED' if parsing_success else 'FAILED'}")
    print("\nTo test with real ESP32:")
    print("1. Upload saci_sensor_node.py to your ESP32")
    print("2. Connect ESP32 via USB")
    print("3. Run: python saci_serial_reader.py /dev/ttyUSB0")
    print("   (or COM3 on Windows)")

if __name__ == "__main__":
    main()
