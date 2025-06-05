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

# Standard library imports
import argparse
import json
import re
import sys
import time
from datetime import datetime
from typing import Dict, Optional, IO

# Third-party imports
import serial # PySerial library for serial communication


# --- Constants ---
DEFAULT_BAUD_RATE: int = 115200
DEFAULT_TIMEOUT: float = 2.0
# Regular expression to parse the sensor data line from the ESP32.
# It expects a format like: "Temp: 25.5 C, Hum: 45.0 %, Smoke: 150, Risk: LOW"
# or "Temp: ERROR C, Hum: ERROR %, Smoke: ERROR, Risk: UNKNOWN"
# Risk level is optional in the regex to handle lines without it.
SENSOR_DATA_PATTERN = re.compile(
    r"Temp:\s*([\d\.\-]+|ERROR)\s*C,\s*"
    r"Hum:\s*([\d\.\-]+|ERROR)\s*%,\s*"
    r"Smoke:\s*(\d+|ERROR)"
    r"(?:,\s*Risk:\s*(\w+))?"  # Non-capturing group for optional Risk
)


class SACISerialReader:
    """
    Handles serial communication with an ESP32 device that sends sensor data
    in a specific string format (e.g., "Temp: 25.5 C, Hum: 45.0 %, Smoke: 150, Risk: LOW").
    This class is responsible for connecting to the serial port, reading lines of data,
    parsing these lines into structured dictionaries, and optionally logging them
    to a file or printing them to the console.

    The expected sensor data includes temperature, humidity, and a smoke ADC value.
    It can also include an optional "Risk" level. The parser is designed to be
    resilient to "ERROR" values reported by the sensors.
    """

    def __init__(self,
                 port: str,
                 baud_rate: int = DEFAULT_BAUD_RATE,
                 timeout: float = DEFAULT_TIMEOUT):
        """
        Initializes the SACISerialReader.

        Args:
            port: The serial port to connect to (e.g., /dev/ttyUSB0, COM3).
            baud_rate: The baud rate for the serial communication.
            timeout: Read timeout in seconds for serial operations.
        """
        self.port: str = port
        self.baud_rate: int = baud_rate
        self.timeout: float = timeout
        self.serial_conn: Optional[serial.Serial] = None
        # Using the globally defined pattern for consistency
        self.data_pattern: re.Pattern = SENSOR_DATA_PATTERN

    def connect(self) -> bool:
        """
        Establishes the serial connection to the specified port.

        Returns:
            True if the connection was successful, False otherwise.

        Raises:
            Prints error messages to stdout for serial.SerialException or
            other unexpected exceptions during connection.
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,    # 8 data bits
                parity=serial.PARITY_NONE,   # No parity
                stopbits=serial.STOPBITS_ONE # 1 stop bit
            )
            # A short delay can be helpful for some serial devices to initialize properly after connection.
            time.sleep(2)
            print(f"[INFO] Successfully connected to {self.port} at {self.baud_rate} baud.")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Failed to connect to {self.port}: {e}")
            return False
        except Exception as e: # Catch any other unexpected errors
            print(f"[ERROR] Unexpected error connecting to serial port {self.port}: {e}")
            return False

    def disconnect(self) -> None:
        """
        Closes the serial connection if it is open.
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                print("[INFO] Serial connection closed.")
            except Exception as e: # Should not typically fail, but good to catch
                print(f"[ERROR] Error while closing serial connection: {e}")
        else:
            print("[INFO] Serial connection was not open or already closed.")

    def _parse_single_value(self, value_str: str, target_type: type):
        """Helper to parse individual sensor values, handling 'ERROR'."""
        if value_str == "ERROR":
            return None
        try:
            return target_type(value_str)
        except (ValueError, TypeError):
            return None

    def parse_sensor_data(self, line: str) -> Optional[Dict[str, any]]:
        """
        Parses a single line of sensor data received from the ESP32.

        The expected format is:
        "Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL"
        "ERROR" can replace any sensor value. The "Risk: LEVEL" part is optional.

        Args:
            line: The raw string read from the serial port.

        Returns:
            A dictionary containing the parsed sensor data if successful, otherwise None.
            The dictionary includes the following keys:
            - 'timestamp': ISO 8601 format string of when the data was parsed.
            - 'temperature_celsius': Float, temperature in Celsius, or None if "ERROR".
            - 'humidity_percent': Float, humidity percentage, or None if "ERROR".
            - 'smoke_adc': Integer, smoke sensor ADC reading, or None if "ERROR".
            - 'risk_level': String, risk level (e.g., "LOW", "HIGH"), or "N/A" if not provided.
            - 'raw_line': String, the original stripped line read from serial.
            Returns None if parsing fails (e.g., line does not match expected format).
        """
        line_stripped = line.strip()
        match = self.data_pattern.search(line_stripped)

        if not match:
            # Line does not match the expected sensor data format.
            return None

        try:
            temp_str, hum_str, smoke_str, risk_str = match.groups()

            temperature = self._parse_single_value(temp_str, float)
            humidity = self._parse_single_value(hum_str, float)
            smoke_level = self._parse_single_value(smoke_str, int)
            
            # Risk level is optional and may not be present in all lines
            risk_level = risk_str if risk_str else "N/A" # Default to N/A if not present

            return {
                'timestamp': datetime.now().isoformat(),  # ISO 8601 format timestamp
                'temperature_celsius': temperature,      # Parsed temperature
                'humidity_percent': humidity,            # Parsed humidity
                'smoke_adc': smoke_level,                # Parsed smoke ADC value
                'risk_level': risk_level,                # Parsed risk level
                'raw_line': line_stripped                # Original data line
            }
        except Exception as e:
            # This catches errors if, for example, group access fails (though pattern matching should prevent this)
            # or if datetime.now() fails (highly unlikely).
            print(f"[ERROR] Unexpected error processing matched groups from line '{line_stripped}': {e}")
            return None

    def read_continuous(self,
                        output_file_path: Optional[str] = None,
                        verbose: bool = True) -> None:
        """
        Continuously reads data from the serial port. For each line read,
        it attempts to parse it as sensor data. If successful, the parsed
        data is printed (if verbose) and logged to a file (if specified).
        If parsing fails, the raw line is printed (if verbose and it is not
        one of this script own log messages).

        The loop handles serial communication errors, unicode decoding errors,
        and file I/O errors gracefully. It terminates on KeyboardInterrupt (Ctrl+C)
        or a fatal serial error.

        Args:
            output_file_path: Optional path to a file for logging sensor data
                              in JSON Lines format.
            verbose: If True, parsed data and other relevant messages from
                     the ESP32 are printed to the console.
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("[ERROR] Serial connection not established. Cannot read data.")
            return

        file_handle: Optional[IO[str]] = None
        if output_file_path:
            try:
                # Open file in append mode ('a') with UTF-8 encoding.
                # Buffering is handled by Python's default.
                file_handle = open(output_file_path, 'a', encoding='utf-8')
                print(f"[INFO] Logging sensor data to: {output_file_path}")
            except IOError as e:
                print(f"[ERROR] Failed to open output file '{output_file_path}': {e}. "
                      "Data will not be logged to file.")
                file_handle = None # Ensure it's None so no write attempts are made
        
        print("[INFO] Starting continuous data reading. Press Ctrl+C to stop.")
        print("-" * 70) # Visual separator for console output
        
        # Store raw_line to avoid decoding multiple times if needed for logging errors
        raw_line_bytes: Optional[bytes] = None

        try:
            while True:
                line_stripped: Optional[str] = None
                try:
                    if self.serial_conn.in_waiting > 0:
                        raw_line_bytes = self.serial_conn.readline()
                        line = raw_line_bytes.decode('utf-8', errors='ignore')
                        line_stripped = line.strip()

                        if not line_stripped: # Skip empty lines
                            continue

                        parsed_data = self.parse_sensor_data(line_stripped)
                        
                        if parsed_data:
                            if verbose:
                                self.print_formatted_data(parsed_data)
                            
                            if file_handle:
                                try:
                                    file_handle.write(json.dumps(parsed_data) + '\n')
                                    file_handle.flush()
                                except IOError as e:
                                    print(f"[ERROR] Could not write to log file '{output_file_path}': {e}")
                        elif verbose and line_stripped: # If not parsed and verbose, print raw
                            # Avoid re-printing this script's own log messages if they get echoed by chance
                            is_internal_log_msg = any(
                                line_stripped.startswith(prefix) for prefix in
                                ("[INFO]", "[ERROR]", "[WARN]", "[DEBUG]", "[FATAL]", "ESP32 Raw:")
                            )
                            if not is_internal_log_msg:
                                print(f"ESP32 Raw: {line_stripped}")

                except serial.SerialException as e:
                    print(f"[ERROR] Serial communication error: {e}. Halting data reading.")
                    break
                except UnicodeDecodeError as e:
                    error_msg = f"[WARN] Unicode decode error for a line: {e}."
                    if raw_line_bytes:
                        error_msg += f" Raw bytes: {raw_line_bytes!r}"
                    print(error_msg)
                    continue
                except IOError as e:
                    print(f"[ERROR] IO error during serial read: {e}. Halting data reading.")
                    break

                time.sleep(0.05)
                    
        except KeyboardInterrupt:
            print("\n[INFO] Data collection stopped by user (Ctrl+C).")
        finally:
            if file_handle:
                try:
                    file_handle.close()
                    print(f"[INFO] Log file '{output_file_path}' closed.")
                except IOError as e:
                    print(f"[ERROR] Error closing log file '{output_file_path}': {e}")

    def print_formatted_data(self, data: Dict[str, any]) -> None:
        """
        Prints parsed sensor data to the console in a structured, human-readable format.

        Args:
            data: A dictionary containing the parsed sensor data, which must include
                  'timestamp', 'temperature_celsius', 'humidity_percent',
                  'smoke_adc', and 'risk_level' keys.
        """
        # Safely get values using .get() with default values if keys might be missing
        ts = data.get('timestamp', 'N/A')
        temp_val = data.get('temperature_celsius')
        hum_val = data.get('humidity_percent')
        smoke_val = data.get('smoke_adc')
        risk_val = data.get('risk_level', "N/A") # Default to "N/A"

        # Format values for printing, handling None (ERROR from sensor)
        temp_str = f"{temp_val:.1f}°C" if temp_val is not None else "ERROR"
        hum_str = f"{hum_val:.1f}%" if hum_val is not None else "ERROR"
        smoke_str = str(smoke_val) if smoke_val is not None else "ERROR"
        
        # Consistent formatting for console output. Max timestamp length (ISO 8601) is usually 26.
        # Example: [2023-10-27T10:30:00.123456] T:  25.5°C | H:  45.0% | Smoke:   150 | Risk: LOW
        print(f"[{ts:<26}] T: {temp_str:>7s} | H: {hum_str:>7s} | "
              f"Smoke: {smoke_str:>5s} | Risk: {risk_val}")

    def test_connection(self) -> bool:
        """
        Tests the serial connection by attempting to read a few lines of data
        and parse them as sensor readings.

        This method helps verify that the correct port is selected, the device
        is responsive, and the data format is as expected. It runs for a
        fixed duration (10 seconds).

        Returns:
            True if valid sensor data was successfully received and parsed
            within the test duration; False otherwise.
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("[ERROR] Serial connection not established. Cannot perform test.")
            return False
        
        print(f"[INFO] Testing connection to {self.port} for up to 10 seconds...")
        print("[INFO] Attempting to read and parse incoming sensor data...")
        start_time = time.time()
        lines_received_count = 0
        parsed_successfully = False
        
        try:
            while time.time() - start_time < 10:  # Test for a 10-second duration
                if self.serial_conn.in_waiting > 0:
                    # Read raw bytes and decode, stripping whitespace
                    line_bytes = self.serial_conn.readline()
                    line_str = ""
                    try:
                        line_str = line_bytes.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        print(f"  [TEST] Warning: Received line with undecodable characters: {line_bytes!r}")
                        line_str = line_bytes.decode('utf-8', errors='ignore').strip() # Try with ignore

                    if line_str: # If line is not empty after stripping
                        lines_received_count += 1
                        print(f"  [TEST] Raw line received: \"{line_str}\"")
                        parsed_data = self.parse_sensor_data(line_str)
                        if parsed_data:
                            # Optional: print formatted data for more detail during test
                            # self.print_formatted_data(parsed_data)
                            print(f"  [TEST] Successfully parsed data: {parsed_data['temperature_celsius']}°C, "
                                  f"{parsed_data['humidity_percent']}%, {parsed_data['smoke_adc']} (Smoke), "
                                  f"Risk: {parsed_data['risk_level']}")
                            parsed_successfully = True
                            break # Exit test loop on first successful parse
                time.sleep(0.1) # Brief pause to yield execution
        
        except serial.SerialException as e:
            print(f"[ERROR] A serial error occurred during the connection test: {e}")
            return False # Test fails on serial error
        except Exception as e: # Catch any other unexpected error during test
            print(f"[ERROR] An unexpected error occurred during the connection test: {e}")
            return False # Test fails on other errors

        # After the loop (timer up or break)
        if parsed_successfully:
            print("[INFO] Connection test PASSED: Valid sensor data received and parsed.")
            return True
        else:
            print("[WARN] Connection test FINISHED.")
            if lines_received_count == 0:
                print("[WARN] No data was received from the serial port during the 10s test period.")
                print("        Possible issues to check:")
                print("          - Device power and connection.")
                print("          - Correct serial port selected (`{self.port}`).")
                print(f"          - Baud rate match (currently {self.baud_rate}).")
                print("          - ESP32 firmware is running and sending data.")
            else:
                print(f"[WARN] Received {lines_received_count} lines, but none matched the expected sensor data format.")
                print("        Possible issues to check:")
                print("          - ESP32 firmware output format (should match SENSOR_DATA_PATTERN).")
                print("          - Serial encoding issues (though UTF-8 with ignore is used).")
            return False

# --- Main Execution ---
def main() -> None:
    """
    Main execution function for the SACI Serial Reader script.

    This function orchestrates the script's operations:
    1. Parses command-line arguments for serial port, baud rate, output file, etc.
    2. Initializes the `SACISerialReader` with the provided settings.
    3. Establishes a connection to the serial port.
    4. If the `--test` flag is used, it performs a connection test and exits.
    5. Otherwise, it starts continuously reading and processing sensor data.
    6. Handles `KeyboardInterrupt` (Ctrl+C) for graceful shutdown.
    7. Ensures the serial connection is closed upon termination (normally or due to error).
    8. Exits with appropriate status codes (0 for success, 1 for errors).
    """
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(
        description="SACI MVP Serial Data Reader: Connects to an ESP32 sensor node, "
                    "reads sensor data via serial, parses it, and optionally logs to a file.",
        formatter_class=argparse.RawDescriptionHelpFormatter, # Preserves formatting in epilog
        epilog=(
            "Examples of use:\n"
            "  # Read from /dev/ttyUSB0 and print to console\n"
            "  python %(prog)s /dev/ttyUSB0\n\n"
            "  # Read from COM3 at 9600 baud and save to data.jsonl\n"
            "  python %(prog)s COM3 --baud 9600 --output data.jsonl\n\n"
            "  # Test connection to /dev/ttyACM0, then exit\n"
            "  python %(prog)s /dev/ttyACM0 --test\n\n"
            "  # Read from /dev/ttyUSB1, log to file, no verbose data output\n"
            "  python %(prog)s /dev/ttyUSB1 -o sensor.log --quiet"
        )
    )
    
    # Define command-line arguments
    parser.add_argument(
        'port',
        metavar='SERIAL_PORT',
        help="The serial port connected to the ESP32 (e.g., "
             "/dev/ttyUSB0 on Linux, COM3 on Windows)."
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=DEFAULT_BAUD_RATE,
        help="Baud rate for the serial connection "
             f"(default: {DEFAULT_BAUD_RATE})."
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Serial read timeout in seconds "
             f"(default: {DEFAULT_TIMEOUT})."
    )
    parser.add_argument(
        '--output', '-o',
        metavar='FILE_PATH',
        help="Optional file path to log sensor data in JSON Lines format. "
             "Data is appended if the file already exists."
    )
    parser.add_argument(
        '--test',
        action='store_true', # Makes it a flag, value is True if present
        help="Perform a connection test: attempts to read data for a short "
             "period, parse it, print results, and then exit. Useful for "
             "verifying the connection and data format."
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true', # Makes it a flag
        help="Suppress printing of successfully parsed sensor data lines "
             "to the console. Error messages and raw output from ESP32 "
             "(if not parsable as sensor data) are still displayed. "
             "Useful when primarily logging data to a file."
    )
    
    args = parser.parse_args() # Parse the arguments provided from the command line
    
    # Instantiate the serial reader with configuration derived from command-line arguments
    reader = SACISerialReader(
        port=args.port,
        baud_rate=args.baud,
        timeout=args.timeout
    )
    
    exit_code = 0 # Default exit code assumes success
    try:
        # Attempt to connect to the serial port
        if not reader.connect():
            # connect() method prints specific error messages
            sys.exit(1) # Exit with an error code if connection fails
        
        if args.test:
            # If --test flag is used, perform the connection test
            print("[INFO] Test mode activated.")
            if not reader.test_connection():
                exit_code = 1 # Test failed, set error exit code
            # test_connection() prints its own success/failure messages
            # Program will then proceed to finally block and exit
        else:
            # Normal operation: continuous reading mode
            # Verbosity is controlled by the --quiet flag
            reader.read_continuous(output_file_path=args.output, verbose=not args.quiet)
    
    except KeyboardInterrupt:
        # Handle user interruption (Ctrl+C) gracefully
        print("\n[INFO] Program terminated by user (KeyboardInterrupt).")
        # Typically, a user-initiated Ctrl+C might be considered a normal exit (code 0)
        # or a specific code like 130. For simplicity, we'll use 0 here.
        exit_code = 0
    except Exception as e:
        # Catch any other unexpected exceptions not handled at lower levels
        print(f"[FATAL] An unexpected critical error occurred in main: {e}", file=sys.stderr)
        # For debugging, one might want to include the full traceback:
        # import traceback
        # traceback.print_exc()
        exit_code = 1 # Set error exit code for unexpected errors
    finally:
        # This block is always executed, ensuring resources are cleaned up
        print("[INFO] Shutting down application...")
        if reader: # Check if reader object was successfully instantiated
            reader.disconnect() # Close the serial connection if open
        print(f"[INFO] Application finished with exit code {exit_code}.")
        sys.exit(exit_code) # Exit the program with the determined exit code

if __name__ == "__main__":
    # This standard Python construct ensures that main() is called only when
    # the script is executed directly (e.g., `python saci_serial_reader.py ...`),
    # and not when it's imported as a module into another script.
    main()
