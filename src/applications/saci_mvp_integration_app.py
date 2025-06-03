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
                             (default: models/saci_logistic_regression_model.joblib,
                             expected in the 'models' directory relative to the project root).

Example:
    python src/applications/saci_mvp_integration_app.py --port /dev/ttyS0 --baud 9600 \
--model_path models/my_saci_model.joblib

Dependencies:
    - Python 3.x
    - pyserial: For serial communication.
    - joblib: For loading the ML model.
    - scikit-learn & numpy: Typically required by the loaded ML model and its operations.
    - SACISerialReader: Custom module from this project for ESP32 data handling.
    - saci_fire_predictor: Custom module from this project for ML model loading and prediction.

Note:
    Ensure the ESP32 device is connected and transmitting data in a format compatible
    with SACISerialReader's parsing logic (e.g., "Temp: XX.X C, Hum: YY.Y %, Smoke: ZZZ, Risk: LEVEL").
    The script assumes it is run from the project's root directory or that the `src`
    directory is appropriately added to PYTHONPATH for module resolution.
"""
# Standard library imports
import sys
import os
import time
from datetime import datetime
import argparse  # For command-line arguments
import logging   # For application logging

# --- Project-Specific Imports ---
# Add the project root to Python path to allow direct imports of modules from `src`.
# This is a common pattern for scripts within a project structure.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Now, import custom modules after sys.path modification.
from src.data_collection.saci_serial_reader import SACISerialReader
from src.ml_models.saci_fire_predictor import load_model, predict_saci_fire_risk

# --- Global Logger Configuration ---
# It's good practice to get a logger instance for the current module.
logger = logging.getLogger(__name__) # Logger for this application module.

# --- Configuration Constants ---
# Default values for command-line arguments.
# These make the script easier to run without specifying every option.
DEFAULT_SERIAL_PORT = '/dev/ttyUSB0' if os.name != 'nt' else 'COM3' # OS-dependent default
DEFAULT_BAUD_RATE = 115200
# Default model path assumes the script is run from the project root.
DEFAULT_MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'saci_fire_risk_model.joblib')


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for serial port, baud rate, and model path.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments
                            as attributes (e.g., args.port, args.baud).
    """
    parser = argparse.ArgumentParser(
        description="SACI MVP Integration Application: Reads live sensor data from an ESP32, "
                    "predicts fire risk using a pre-trained ML model, and displays results.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
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
        help="Baud rate for serial communication with the ESP32."
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="Path to the trained machine learning model file (.joblib)."
    )
    return parser.parse_args()

def process_sensor_reading(line: str, reader: SACISerialReader, model: any) -> None:
    """
    Processes a single line of sensor data: parses, predicts, and logs the result.

    Args:
        line: The raw data line read from the serial port.
        reader: Instance of SACISerialReader used for parsing.
        model: The pre-trained machine learning model for prediction.
    """
    parsed_data = reader.parse_sensor_data(line) #SACISerialReader.parse_sensor_data now returns dict with specific keys

    if parsed_data:
        # Ensure to use the correct keys as returned by the updated SACISerialReader.parse_sensor_data
        # These should be 'temperature_celsius', 'humidity_percent', 'smoke_adc'.
        temp = parsed_data.get('temperature_celsius')
        hum = parsed_data.get('humidity_percent')
        smoke_adc = parsed_data.get('smoke_adc') # This key was 'smoke_adc' in serial_reader

        if temp is not None and hum is not None and smoke_adc is not None:
            try:
                predicted_label, probability_scores = predict_saci_fire_risk(
                    model, temp, hum, smoke_adc # predict_saci_fire_risk expects temp, hum, smoke_adc
                )

                # Validate the structure of probability_scores before indexing
                if probability_scores is not None and len(probability_scores) == 2:
                    prob_fire = probability_scores[1]  # Assuming P(Fire) is at index 1
                    risk_status = "Fire Detected" if predicted_label == 1 else "No Fire Detected"
                    # Using milliseconds for more precise timing if needed
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                    output_str = (
                        f"Timestamp: {current_time} | "
                        f"Data: Temp={temp:.1f}°C, Hum={hum:.1f}%, Smoke={smoke_adc} -> "
                        f"Risk: {risk_status} (Label: {predicted_label}), P(Fire): {prob_fire:.3f}"
                    )
                    logger.info(output_str)
                else:
                    logger.warning(f"Received invalid probability scores array: {probability_scores}. "
                                   f"Cannot determine P(Fire). Parsed data: {parsed_data}")

            except Exception as pred_e: # Catch errors from predict_saci_fire_risk
                logger.error(f"Prediction failed for parsed data '{parsed_data}': {pred_e}", exc_info=True)
        else:
            # This case handles if parsing was successful but some expected keys were still None.
            logger.info(f"Incomplete sensor data after parsing (some values are None), "
                        f"skipping prediction. Raw line: '{line}', Parsed: {parsed_data}")
    elif line: # If parsing failed (parsed_data is None) and the line was not empty
        # Log non-empty lines that couldn't be parsed by SACISerialReader.parse_sensor_data.
        # This helps identify unexpected output from the ESP32 (e.g., debug messages, errors).
        # Avoid re-logging messages that this script itself might be generating if serial echo is on.
        is_internal_log_message = any(
            line.startswith(prefix) for prefix in
            ("[INFO]", "[ERROR]", "[WARN]", "[DEBUG]", "RAW ESP32 Output")
        )
        if not is_internal_log_message:
            logger.info(f"RAW ESP32 Output (Unparsed by SACISerialReader): \"{line}\"")


def main() -> None:
    """
    Main function to run the SACI MVP Integration Application.

    This function orchestrates the entire process:
    1. Parses command-line arguments.
    2. Loads the pre-trained machine learning model.
    3. Initializes and connects the `SACISerialReader` to the ESP32.
    4. Enters a continuous loop to read data, process it, predict fire risk,
       and log the information.
    5. Handles interruptions (like Ctrl+C) and ensures cleanup on exit.
    """
    args = parse_arguments()

    logger.info("--- SACI MVP Integration Application Starting ---")
    logger.info(f"Attempting to load ML model from: {args.model_path}")
    model = None
    try:
        model = load_model(args.model_path)
        logger.info(f"Successfully loaded ML model: {type(model).__name__}")
    except FileNotFoundError:
        logger.error(f"FATAL: Model file not found at '{args.model_path}'. "
                     "Please provide a valid path using --model_path.")
        sys.exit(1) # Use sys.exit for cleaner termination from main
    except Exception as e:
        logger.error(f"FATAL: Could not load ML model from '{args.model_path}': {e}")
        sys.exit(1)

    logger.info(f"Initializing serial reader for port {args.port} at {args.baud} baud.")
    reader = SACISerialReader(port=args.port, baud_rate=args.baud)

    if not reader.connect():
        logger.error(f"FATAL: Failed to connect to serial port {args.port}. "
                     "Check connection, permissions, and settings (e.g., if device is busy).")
        sys.exit(1)

    logger.info(f"Successfully connected to ESP32 on {args.port} at {args.baud} baud.")
    logger.info("Starting real-time fire risk prediction loop...")
    logger.info("Press Ctrl+C to stop the application gracefully.")
    logger.info("-" * 80)

    try:
        while True:
            raw_line_for_log = "<unavailable>" # For logging in case of decode error
            try:
                if reader.serial_conn and reader.serial_conn.in_waiting > 0:
                    line_bytes = reader.serial_conn.readline()
                    raw_line_for_log = str(line_bytes[:100]) # Log first 100 bytes if decode fails
                    line_str = line_bytes.decode('utf-8', errors='ignore').strip()

                    if line_str:
                        process_sensor_reading(line_str, reader, model)

                # Adjust sleep time: lower for faster data, higher for less CPU.
                # 0.1s is a reasonable starting point for many serial applications.
                time.sleep(0.1)

            except UnicodeDecodeError as ude:
                logger.warning(f"Unicode decode error for line: {raw_line_for_log}. Error: {ude}. "
                               "Check ESP32 encoding or for serial line noise.")
            except serial.SerialException as se: # More specific serial error
                logger.error(f"Serial communication error encountered: {se}. Attempting to continue or reconnect if applicable.")
                # For a robust app, add reconnection logic here or exit. For MVP, we might just log.
                time.sleep(2) # Wait before trying again or exiting
            except Exception as loop_e:
                logger.error(f"An unexpected error occurred in the processing loop: {loop_e}", exc_info=True)
                time.sleep(1) # Brief pause before continuing

    except KeyboardInterrupt:
        logger.info("\nKeyboardInterrupt received. Initiating graceful shutdown...")
    finally:
        logger.info("--- SACI MVP Integration Application Shutting Down ---")
        if reader and reader.serial_conn and reader.serial_conn.is_open:
            logger.info("Disconnecting serial reader and closing port.")
            reader.disconnect()
        logger.info("Application stopped.")
        logging.shutdown() # Ensure all logging handlers are closed

if __name__ == '__main__':
    # Configure basic logging settings for the application.
    # This will show messages from this script's logger and potentially other loggers
    # if they are not configured separately.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # This standard Python construct ensures that main() is called only when the script
    # is executed directly (not when imported as a module into another script).
    main()
