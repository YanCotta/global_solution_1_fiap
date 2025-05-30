#!/usr/bin/env python3
"""
SACI MVP - Serial Data Reader
Sistema Guardião - Fire Prevention and Detection
Author: Yan Cotta
Date: May 30, 2025

Reads sensor data from ESP32 via serial connection and parses the values.
Usage: python saci_serial_reader.py [PORT] [--baud BAUD_RATE]
Example: python saci_serial_reader.py /dev/ttyUSB0 --baud 115200
"""

import serial
import argparse
import re
import json
import time
import sys
from datetime import datetime
from typing import Dict, Optional

class SACISerialReader:
    """Serial data reader for SACI MVP sensor data"""
    
    def __init__(self, port: str, baud_rate: int = 115200, timeout: float = 2.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_conn = None
        self.data_pattern = re.compile(
            r"Temp:\s*([\d\.\-]+|ERROR)\s*C,\s*Hum:\s*([\d\.\-]+|ERROR)\s*%,\s*Smoke:\s*(\d+|ERROR)(?:,\s*Risk:\s*(\w+))?"
        )
        
    def connect(self) -> bool:
        """
        Establish serial connection
        Returns: True if successful, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"Connected to {self.port} at {self.baud_rate} baud")
            time.sleep(2)  # Allow ESP32 to stabilize
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to serial port: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Serial connection closed")
    
    def parse_sensor_data(self, line: str) -> Optional[Dict]:
        """
        Parse sensor data from ESP32 output line
        
        Args:
            line: String from ESP32 in format "Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL"
        
        Returns:
            Dictionary with parsed values or None if parsing fails
        """
        try:
            match = self.data_pattern.search(line.strip())
            if not match:
                return None
            
            temp_str, hum_str, smoke_str, risk_str = match.groups()
            
            # Parse temperature
            try:
                temperature = float(temp_str) if temp_str != "ERROR" else None
            except (ValueError, TypeError):
                temperature = None
            
            # Parse humidity
            try:
                humidity = float(hum_str) if hum_str != "ERROR" else None
            except (ValueError, TypeError):
                humidity = None
            
            # Parse smoke level
            try:
                smoke_level = int(smoke_str) if smoke_str != "ERROR" else None
            except (ValueError, TypeError):
                smoke_level = None
            
            # Parse risk level (optional)
            risk_level = risk_str if risk_str else None
            
            return {
                'timestamp': datetime.now().isoformat(),
                'temperature': temperature,
                'humidity': humidity,
                'smoke': smoke_level,
                'risk_level': risk_level,
                'raw_line': line.strip()
            }
            
        except Exception as e:
            print(f"Error parsing line '{line.strip()}': {e}")
            return None
    
    def read_continuous(self, output_file: Optional[str] = None, verbose: bool = True):
        """
        Continuously read and parse data from ESP32
        
        Args:
            output_file: Optional file path to save data as JSON lines
            verbose: Whether to print parsed data to console
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Serial connection not established")
            return
        
        file_handle = None
        if output_file:
            try:
                file_handle = open(output_file, 'a', encoding='utf-8')
                print(f"Logging data to {output_file}")
            except Exception as e:
                print(f"Failed to open output file {output_file}: {e}")
        
        print("Reading sensor data... Press Ctrl+C to stop")
        print("-" * 60)
        
        try:
            while True:
                try:
                    # Read line from serial
                    if self.serial_conn.in_waiting > 0:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                        
                        if line.strip():
                            # Parse sensor data
                            parsed_data = self.parse_sensor_data(line)
                            
                            if parsed_data:
                                if verbose:
                                    self.print_formatted_data(parsed_data)
                                
                                # Save to file if specified
                                if file_handle:
                                    file_handle.write(json.dumps(parsed_data) + '\n')
                                    file_handle.flush()
                            else:
                                # Print non-sensor lines (info, errors, etc.)
                                if verbose and not line.strip().startswith('['):
                                    print(f"ESP32: {line.strip()}")
                    
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                    
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")
                    break
                except UnicodeDecodeError as e:
                    print(f"Unicode decode error: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("\nStopping data collection...")
        finally:
            if file_handle:
                file_handle.close()
                print(f"Data saved to {output_file}")
    
    def print_formatted_data(self, data: Dict):
        """Print parsed data in a formatted way"""
        timestamp = data['timestamp']
        temp = f"{data['temperature']:.1f}°C" if data['temperature'] is not None else "ERROR"
        hum = f"{data['humidity']:.1f}%" if data['humidity'] is not None else "ERROR"
        smoke = f"{data['smoke']}" if data['smoke'] is not None else "ERROR"
        risk = data['risk_level'] if data['risk_level'] else "N/A"
        
        print(f"[{timestamp}] T: {temp:>8} | H: {hum:>8} | Smoke: {smoke:>6} | Risk: {risk}")
    
    def test_connection(self):
        """Test serial connection by reading a few lines"""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Serial connection not established")
            return False
        
        print("Testing connection... (10 seconds)")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    if line.strip():
                        print(f"Received: {line.strip()}")
                        parsed = self.parse_sensor_data(line)
                        if parsed:
                            print(f"Parsed: {parsed}")
                            return True
                time.sleep(0.1)
            except Exception as e:
                print(f"Test error: {e}")
                return False
        
        print("No valid sensor data received during test")
        return False

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Read and parse sensor data from SACI MVP ESP32",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python saci_serial_reader.py /dev/ttyUSB0
  python saci_serial_reader.py COM3 --baud 115200
  python saci_serial_reader.py /dev/ttyUSB0 --output sensor_data.jsonl
  python saci_serial_reader.py COM3 --test
        """
    )
    
    parser.add_argument('port', help='Serial port (e.g., /dev/ttyUSB0 or COM3)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--timeout', type=float, default=2.0, help='Read timeout in seconds (default: 2.0)')
    parser.add_argument('--output', '-o', help='Output file to save data as JSON lines')
    parser.add_argument('--test', action='store_true', help='Test connection and exit')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress console output')
    
    args = parser.parse_args()
    
    # Create reader instance
    reader = SACISerialReader(args.port, args.baud, args.timeout)
    
    try:
        # Connect to serial port
        if not reader.connect():
            sys.exit(1)
        
        if args.test:
            # Test mode
            success = reader.test_connection()
            sys.exit(0 if success else 1)
        else:
            # Continuous reading mode
            reader.read_continuous(args.output, not args.quiet)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        reader.disconnect()

if __name__ == "__main__":
    main()
