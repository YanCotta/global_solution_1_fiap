"""
SACI MVP Integration Application
---------------------------------

This script serves as the main application for the Sistema Guardião SACI MVP.
It integrates components for:
1. Reading live sensor data (Temperature, Humidity, Smoke ADC) transmitted
   from an ESP32 device via a serial connection using SACISerialReader.
2. Loading a pre-trained machine learning model (e.g., Logistic Regression)
   for fire risk prediction using functions from saci_fire_predictor.
3. Processing the live sensor data through the ML model to predict fire risk
   (e.g., "No Fire Detected" or "Fire Detected") and associated probability.
4. Displaying the live data, predictions, and status messages in a
   human-readable format on the console.

The application is designed to be robust, with error handling for model loading,
serial communication, data parsing, and prediction processes. It can be
configured via command-line arguments for the serial port, baud rate, and the
path to the ML model file.

Usage:
    python src/applications/saci_mvp_integration_app.py [OPTIONS]

Options:
    --port SERIAL_PORT       Serial port for connecting to the ESP32 sensor node
                             (default: /dev/ttyUSB0 on Linux, COM3 on Windows).
    --baud BAUD_RATE         Baud rate for serial communication (default: 115200).
    --model_path MODEL_FILE  Path to the trained .joblib model file
                             (default: saci_logistic_regression_model.joblib,
                             expected in the script's directory or a reachable path).

Example:
    python src/applications/saci_mvp_integration_app.py --port /dev/ttyS0 --baud 9600 --model_path models/my_saci_model.joblib

Dependencies:
    - Python 3.x
    - pyserial: For serial communication.
    - joblib: For loading the ML model.
    - scikit-learn: Typically required by the loaded ML model.
    - SACISerialReader: Custom module for ESP32 data handling.
    - saci_fire_predictor: Custom module for ML model loading and prediction.

Note:
    Ensure the ESP32 device is connected and transmitting data in the expected format:
    "SACI MVP Raw Data: Temp=XX.X,Hum=YY.Y,Smoke=ZZZ"
    or "SACI MVP Error: Sensor Error Message"
"""
import time
from datetime import datetime
import argparse # For command-line arguments

# Assuming the script is run from the root of the project or PYTHONPATH is set up
# If running from root, 'python -m src.applications.saci_mvp_integration_app' might be needed
# or ensure src directory is in PYTHONPATH.
from src.data_collection.saci_serial_reader import SACISerialReader
from src.ml_models.saci_fire_predictor import load_model, predict_saci_fire_risk

# --- Configuration Constants ---
DEFAULT_SERIAL_PORT = '/dev/ttyUSB0'  # Adjust for your OS (e.g., 'COM3' on Windows)
DEFAULT_BAUD_RATE = 115200
DEFAULT_MODEL_PATH = 'saci_logistic_regression_model.joblib' # Ensure this path is correct relative to execution location or use an absolute path.

def parse_arguments():
    """
    Parses command-line arguments for serial port, baud rate, and model path.
    Provides default values and help messages for each argument.
    """
    parser = argparse.ArgumentParser(
        description="SACI MVP Integration Application: Reads sensor data from ESP32, predicts fire risk using an ML model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help message.
    )
    parser.add_argument(
        "--port",
        type=str,
        default=DEFAULT_SERIAL_PORT,
        help="Serial port for connecting to the ESP32 sensor node."
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=DEFAULT_BAUD_RATE,
        help="Baud rate for serial communication."
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="Path to the trained ML model file (.joblib)."
    )
    return parser.parse_args()

def main():
    """
    Main function to run the SACI MVP Integration Application.
    Handles argument parsing, model loading, serial connection, data processing,
    and prediction loop.
    """
    args = parse_arguments() # Parse command-line arguments

    # --- 1. Load the ML Model ---
    # Attempts to load the specified machine learning model.
    # Exits if the model cannot be found or loaded.
    model = None
    try:
        model = load_model(args.model_path)
        logger.info(f"Successfully loaded ML model from: {args.model_path}")
    except FileNotFoundError:
        logger.error(f"Model file not found at '{args.model_path}'. Please check the path and ensure the file exists.")
        return  # Exit application if model cannot be loaded
    except Exception as e: # Catch other potential errors during model loading
        logger.error(f"Could not load ML model from '{args.model_path}': {e}")
        return  # Exit application if model loading fails

    # --- 2. Initialize SACISerialReader ---
    # Creates an instance of the SACISerialReader to handle serial communication.
    reader = SACISerialReader(port=args.port, baud_rate=args.baud)

    # --- 3. Connect to Serial Port ---
    # Attempts to establish a connection to the specified serial port.
    # Exits if the connection fails.
    if not reader.connect(): # reader.connect() returns True on success, False on failure
        print(f"ERROR: Failed to connect to serial port {args.port}. Please check the connection, port settings, and permissions.")
        return  # Exit application if serial connection fails

    print(f"INFO: Connected to ESP32 on {args.port} at {args.baud} baud.")
    print("INFO: Starting real-time fire risk prediction...")
    print("INFO: Press Ctrl+C to stop the application.")
    print("-" * 70) # Print a separator line for clarity

    try:
        # --- 4. Main Processing Loop ---
        # Continuously reads data from the serial port, parses it,
        # makes predictions, and prints the results.
        while True:
            try:
                # Check if there's data available in the serial buffer
                if reader.serial_conn and reader.serial_conn.in_waiting > 0:
                    # Read a line from serial, decode, and strip whitespace
                    line = reader.serial_conn.readline().decode('utf-8', errors='ignore').strip()

                    if not line: # If the line is empty after stripping
                        time.sleep(0.05) # Small delay to prevent busy-waiting if lines are sparse
                        continue

                    # Parse the raw sensor data string using the reader's method
                    parsed_data = reader.parse_sensor_data(line)

                    if parsed_data: # If parsing was successful and returned data
                        temp = parsed_data.get('temperature')
                        hum = parsed_data.get('humidity')
                        smoke_adc = parsed_data.get('smoke') # ESP32 sends 'Smoke', parser maps to 'smoke'

                        # Ensure all necessary sensor values are present for prediction
                        if temp is not None and hum is not None and smoke_adc is not None:
                            # Perform fire risk prediction using the loaded model
                            try:
                                predicted_label, probability_scores = predict_saci_fire_risk(model, temp, hum, smoke_adc)

                                # Assuming class 1 is 'Fire' and class 0 is 'No Fire'.
                                # probability_scores is often an array like [P(class_0), P(class_1)]
                                prob_fire = probability_scores[1] if len(probability_scores) > 1 else probability_scores[0]
                                risk_status = "Fire Detected" if predicted_label == 1 else "No Fire Detected"

                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                # Format and print the output string
                                output_str = (
                                    f"Timestamp: {current_time} | "
                                    f"Live Data: Temp={temp}°C, Hum={hum}%, Smoke ADC={smoke_adc} -> "
                                    f"Predicted Risk: {risk_status}, P(Fire): {prob_fire:.2f}"
                                )
                                print(output_str)

                            except Exception as pred_e: # Handle errors during the prediction step
                                print(f"ERROR: Prediction failed: {pred_e}. Input data: {parsed_data}")
                        else:
                            # Log if essential data (temp, hum, smoke) is missing after successful parsing
                            # This can happen if the ESP32 sends "ERROR" for a sensor, which parse_sensor_data might handle by omitting the key.
                            print(f"INFO: Incomplete sensor data received, skipping prediction. Raw: '{line}', Parsed: {parsed_data}")
                    else:
                        # Log lines that are not successfully parsed as sensor data
                        # These could be ESP32 status messages, boot messages, or noise.
                        # Filter out common, expected non-data messages from ESP32 if necessary.
                        if line and not line.startswith("SACI MVP") and not line.startswith("ESP32:") and not line.startswith("[INFO]"):
                             print(f"RAW ESP32 Output: {line}")


                # Main loop delay: controls how frequently the loop checks for serial data.
                # Adjust based on data transmission rate and desired responsiveness.
                time.sleep(0.1)

            except UnicodeDecodeError as ude: # Handle potential errors decoding serial data
                # This can happen if baud rates don't match or due to line noise.
                print(f"WARNING: Unicode decode error for line: '{line if 'line' in locals() else '<unavailable>'}'. Error: {ude}")
            except Exception as loop_e: # Catch-all for other unexpected errors within the loop
                print(f"ERROR: An unexpected error occurred in the processing loop: {loop_e}")
                time.sleep(1) # Pause briefly before continuing to avoid rapid error messages

    except KeyboardInterrupt: # Handle graceful shutdown on Ctrl+C
        print("\nINFO: KeyboardInterrupt received. Shutting down application...")
    finally:
        # --- 5. Cleanup ---
        # This block executes regardless of how the try block exits (success or exception).
        # Ensures resources like the serial connection are properly released.
        if reader and reader.serial_conn and reader.serial_conn.is_open:
            print("INFO: Disconnecting serial reader and closing port.")
            reader.disconnect()
        print("INFO: SACI MVP Integration Application stopped.")

if __name__ == '__main__':
    # This standard Python construct ensures that main() is called only when the script
    # is executed directly (not when imported as a module into another script).
    main()
