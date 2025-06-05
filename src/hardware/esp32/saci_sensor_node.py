"""
SACI MVP - ESP32 Sensor Node (MicroPython)
------------------------------------------

This MicroPython script is designed for an ESP32 microcontroller to function as a
sensor node for the Sistema Guardião - Fire Prevention and Detection project.

Key functionalities:
- Reads temperature and humidity from a DHT22 sensor.
- Reads smoke/gas levels from an MQ-135 analog sensor.
- Calculates a simplified fire risk level based on these sensor inputs.
- Formats the sensor data and risk level into a string.
- Prints the formatted string to the serial console at regular intervals.
- Includes basic error handling for sensor readings.
- Manages memory with periodic garbage collection.

The script is intended for continuous operation, providing real-time (or near
real-time) environmental data that can be read by a connected host system
(e.g., a Raspberry Pi or PC running the SACI MVP Integration Application).

Pin Configuration:
- DHT22 Sensor: Connected to GPIO2 (configurable via DHT22_PIN_NUM).
- MQ-135 Sensor: Connected to GPIO36 (ADC1_CH0, configurable via MQ135_PIN_NUM).

Output Format (Serial Print):
  "Temp:XX.XC, Hum:XX.X%, Smoke:XXXX, Risk:LEVEL"
  (e.g., "Temp:25.5C, Hum:45.0%, Smoke:150, Risk:LOW")
  "ERROR" is used for values if a sensor reading fails.

This script forms the hardware data collection part of the SACI MVP.
"""
# Author: Yan Cotta
# Date: May 30, 2025

import time
import dht
from machine import Pin, ADC # Consolidated machine imports
import gc

# --- Pin Configuration ---
# Define Pin objects directly for clarity and MicroPython best practice.
DHT22_PIN_NUM = 2  # ESP32 GPIO2 (often D4 on dev boards)
MQ135_PIN_NUM = 36 # ESP32 GPIO36 (ADC1_CH0, often marked VP)

# --- Sensor Initialization ---
# Attempt to initialize sensors at startup. Errors are critical.
try:
    # Initialize DHT22 Temperature and Humidity Sensor
    dht_sensor = dht.DHT22(Pin(DHT22_PIN_NUM))

    # Initialize MQ-135 Gas/Smoke Sensor
    mq135_adc = ADC(Pin(MQ135_PIN_NUM))
    # Set ADC attenuation for full 0-3.3V range.
    # This is important for MQ-135 which can output varying voltage levels.
    mq135_adc.atten(ADC.ATTN_11DB)
    print("[INFO] SACI MVP: Sensors initialized successfully.")
except Exception as e:
    # Use a more descriptive error message.
    # Consider if the program should halt or try to run with partial functionality.
    # For MVP, critical sensor failure at init might warrant a halt or specific error state.
    print(f"[FATAL] Sensor initialization error: {e}. Check connections/pins.")
    # Optionally, re-raise the exception if a full stop is desired:
    # raise e

# --- Constants for Sensor Logic and Operation ---
READING_INTERVAL = 2  # Seconds between sensor readings.
# Threshold for MQ-135 raw ADC value. This value is empirical and may need calibration.
# Higher values indicate more particles/gases (e.g., smoke).
SMOKE_THRESHOLD = 400
# Temperature in Celsius above which is considered a high-risk factor.
TEMP_THRESHOLD = 35   # Degrees Celsius

# --- Sensor Reading Functions ---
def read_dht22():
    """
    Reads temperature and humidity from the connected DHT22 sensor.

    It triggers a measurement, then fetches temperature and humidity.
    Includes basic validation for data types.

    Returns:
        tuple (float, float): (temperature, humidity) in Celsius and RH(%).
                              Returns (None, None) if a read error occurs or
                              data is invalid.
    """
    try:
        dht_sensor.measure()  # Trigger a new sensor reading
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Basic validation: Ensure readings are sensible numbers.
        # DHT library should handle this, but an extra check can be useful.
        if isinstance(temperature, (int, float)) and isinstance(humidity, (int, float)):
            # Example valid range check (optional, depends on expected environment)
            # if not (-40 < temperature < 85 and 0 <= humidity <= 100):
            #     print(f"DHT22 read warning: Data out of typical range T:{temperature}, H:{humidity}")
            #     # Decide if out-of-range is an error or just a warning.
            #     # For now, we accept it if it's a number.
            return temperature, humidity
        else:
            print(f"DHT22 read error: Invalid data types received (T: {type(temperature)}, H: {type(humidity)}).")
            return None, None
    except OSError as e:
        # OSError is common for DHT sensors (e.g., timeout, checksum error).
        print(f"DHT22 read error (OSError): {e}")
        return None, None
    except Exception as e:
        # Catch any other unexpected errors.
        print(f"DHT22 unexpected error: {e}")
        return None, None

def read_mq135():
    """
    Reads the analog value from the MQ-135 gas/smoke sensor.

    The raw ADC value (typically 0-4095 for a 12-bit ADC on ESP32) is returned.
    Higher values generally indicate a higher concentration of detectable gases/smoke.
    No complex conversion to PPM is done in this MVP.

    Returns:
        int: Raw ADC value (0-4095), or None if an ADC read error occurs.
    """
    try:
        # Read raw ADC value from the pre-configured ADC pin.
        raw_value = mq135_adc.read()
        return raw_value
    except Exception as e:
        # Catch any errors during ADC read.
        print(f"MQ-135 ADC read error: {e}")
        return None

# --- Core Logic ---
# --- Core Logic ---
def calculate_fire_risk(temperature, humidity, smoke_level):
    """
    Calculates a basic fire risk level based on sensor readings.
    This is a simplified model for MVP (Minimum Viable Product) purposes.

    Args:
        temperature (float): Current temperature in Celsius. Can be None.
        humidity (float): Current relative humidity in percent. Can be None.
        smoke_level (int): Raw ADC reading from MQ-135 sensor. Can be None.

    Returns:
        str: Risk level ("MINIMAL", "LOW", "MEDIUM", "HIGH", "UNKNOWN").
             "UNKNOWN" is returned if temperature or smoke_level is None,
             as these are considered primary indicators for this basic model.
    """
    # Critical sensor readings: if temperature or smoke data is missing, risk is "UNKNOWN".
    # Humidity is treated as a secondary factor and can be None without defaulting to "UNKNOWN".
    if temperature is None or smoke_level is None:
        return "UNKNOWN"
    
    # The risk_score is an empirical value derived from sensor readings.
    # Thresholds and score contributions are based on general observations and may
    # require calibration and tuning for specific environments and accuracy needs.
    risk_score = 0 # Initialize risk score
    
    # Temperature Factor:
    # Higher temperatures contribute more to the risk score.
    # TEMP_THRESHOLD is the primary threshold for high temperature.
    if temperature > TEMP_THRESHOLD:  # e.g., > 35°C
        risk_score += 2 # Significant risk increase
    elif temperature > (TEMP_THRESHOLD - 5): # e.g., > 30°C (moderately high)
        risk_score += 1 # Minor risk increase
    
    # Humidity Factor (only if humidity data is available):
    # Lower humidity can increase the likelihood and spread of fire.
    if humidity is not None:
        if humidity < 20:  # Very dry conditions
            risk_score += 2 # Significant risk increase due to dryness
        elif humidity < 40: # Moderately dry conditions
            risk_score += 1 # Minor risk increase
    
    # Smoke Level Factor:
    # Higher smoke ADC values are strong indicators of combustion.
    # SMOKE_THRESHOLD is the primary threshold for significant smoke detection.
    if smoke_level > SMOKE_THRESHOLD:  # e.g., > 400 raw ADC
        risk_score += 3  # Major risk increase, strong fire indicator
    elif smoke_level > (SMOKE_THRESHOLD / 2): # e.g., > 200 raw ADC (moderate smoke)
        risk_score += 1  # Minor risk increase
    
    # Determine Risk Level based on the cumulative risk_score:
    # These score thresholds are empirical and may need adjustment based on testing.
    if risk_score >= 5: # High cumulative score
        return "HIGH"
    elif risk_score >= 3: # Medium cumulative score
        return "MEDIUM"
    elif risk_score >= 1: # Low cumulative score
        return "LOW"
    else: # No significant factors detected
        return "MINIMAL"

def format_sensor_data(temperature, humidity, smoke_level):
    """
    Formats sensor data and the calculated fire risk for serial output.

    Args:
        temperature (float): Current temperature in Celsius. Can be None.
        humidity (float): Current relative humidity in percent. Can be None.
        smoke_level (int): Raw ADC reading from MQ-135 sensor. Can be None.

    Returns:
        str: A formatted string containing all sensor data and the risk level.
             Indicates "ERROR" for sensor values if they are None.
    """
    # Calculate risk level based on current sensor readings
    risk_level = calculate_fire_risk(temperature, humidity, smoke_level)
    
    # Format each sensor value for display, substituting "ERROR" if data is None.
    temp_str = f"{temperature:.1f}" if temperature is not None else "ERROR"
    hum_str = f"{humidity:.1f}" if humidity is not None else "ERROR"
    smoke_str = str(smoke_level) if smoke_level is not None else "ERROR" # smoke_level is int
    
    # Construct the output string. Keep it concise for typical serial monitors.
    # Example: "Temp:25.5C, Hum:45.0%, Smoke:150, Risk:LOW"
    return f"Temp:{temp_str}C, Hum:{hum_str}%, Smoke:{smoke_str}, Risk:{risk_level}"

# --- Main Loop ---
def main_loop():
    """
    Main sensor reading and data processing loop.
    Continuously reads from DHT22 and MQ-135 sensors, calculates fire risk,
    prints the formatted data to the serial console, and manages memory
    by periodically invoking the garbage collector.
    Handles KeyboardInterrupt for graceful shutdown and other exceptions
    to attempt continuous operation.
    """
    print("[INFO] SACI MVP: Starting sensor monitoring loop...")
    print("[INFO] Output Format: Temp:XX.XC, Hum:XX.X%, Smoke:XXXX, Risk:LEVEL")
    print("-" * 60) # Print a separator line for readability
    
    reading_count = 0 # Counter for readings, used for periodic tasks
    
    while True:
        try:
            # Step 1: Read sensor values
            temperature, humidity = read_dht22()
            smoke_level = read_mq135()
            
            # Step 2: Process data and print to serial console
            sensor_data_output = format_sensor_data(temperature, humidity, smoke_level)
            print(sensor_data_output)
            
            # Step 3: Placeholder for alert functionality (not called directly in loop for MVP)
            # For future use, one might check the risk level here and call send_alert:
            # current_risk = calculate_fire_risk(temperature, humidity, smoke_level)
            # if current_risk == "HIGH": # Or other conditions
            #     send_alert(current_risk, temperature, humidity, smoke_level)

            # Step 4: Memory management
            reading_count += 1
            # Periodically run garbage collector to free up memory.
            # Important for long-running applications on memory-constrained devices.
            if reading_count % 25 == 0:  # Run GC approx. every 50s (25 * 2s interval)
                gc.collect()
                # The following line can be uncommented for memory debugging:
                # print(f"[DEBUG] Memory cleanup - Free: {gc.mem_free()} bytes, Allocated: {gc.mem_alloc()} bytes")
            
            # Step 5: Wait for the next reading interval
            time.sleep(READING_INTERVAL) # READING_INTERVAL is in seconds
            
        except KeyboardInterrupt:
            # Gracefully exit the loop if Ctrl+C is pressed.
            print("\n[INFO] SACI MVP: Monitoring stopped by user (KeyboardInterrupt).")
            break
        except Exception as e:
            # Catch any other unexpected errors during the loop.
            # Log the error and continue the loop to maintain uptime if possible.
            print(f"[ERROR] Main loop unexpected error: {e}")
            # Wait for a slightly longer interval before retrying to prevent rapid error messages
            # in case of a persistent problem.
            time.sleep(READING_INTERVAL * 2)

# --- Placeholder Functions for Future Expansion ---
# These functions define intended future capabilities but are currently not implemented
# or called in the main MVP loop. They serve as placeholders for future development.

def send_alert(risk_level, temperature, humidity, smoke_level):
    """
    (NOT IMPLEMENTED IN MVP - PLACEHOLDER)
    Future function to send alerts (e.g., via WiFi, LoRa, SMS).
    For MVP, it could print a more prominent message to the console if high risk.

    Args:
        risk_level (str): The calculated fire risk level (e.g., "HIGH", "MEDIUM").
        temperature (float): Current temperature at the time of the alert.
        humidity (float): Current humidity at the time of the alert.
        smoke_level (int): Current smoke sensor reading at the time of the alert.
    """
    # This function is a placeholder.
    # In a full system, this would format a message and send it over a network
    # or trigger another form of alert.
    if risk_level == "HIGH":
        print(f"--- ALERT! FIRE RISK: {risk_level} ---")
        print(f"    Data: Temp={temperature:.1f}C, Hum={humidity:.1f}%, Smoke={smoke_level}")
    elif risk_level == "MEDIUM": # Example of handling medium risk differently
        print(f"--- WARNING! Fire Risk: {risk_level} ---")
        print(f"    Data: Temp={temperature:.1f}C, Hum={humidity:.1f}%, Smoke={smoke_level}")

def calibrate_sensors():
    """
    (NOT IMPLEMENTED IN MVP - PLACEHOLDER)
    Future function for sensor calibration routines.
    For example, MQ-135 sensors might require setting a baseline R0 value
    in clean air for accurate gas concentration measurements. DHT22 sensors
    are typically factory calibrated.
    """
    # This function is a placeholder.
    # Actual calibration would involve specific procedures for each sensor type.
    print("[INFO] Sensor calibration (calibrate_sensors) is a placeholder for future development.")
    pass # No operation in MVP

def setup_wifi():
    """
    (NOT IMPLEMENTED IN MVP - PLACEHOLDER)
    Future function to establish a WiFi connection.
    This would be used for transmitting data to a remote server/cloud,
    enabling Over-The-Air (OTA) updates, or other network functionalities.
    """
    # This function is a placeholder.
    # Actual WiFi setup involves using the 'network' module in MicroPython.
    # The commented-out code below is an example and should not be enabled for the MVP.
    # --- Example WiFi Connection (DO NOT UNCOMMENT FOR MVP) ---
    # import network
    # STA_SSID = "YourWifiSSID"
    # STA_PASSWORD = "YourWifiPassword"
    # wlan = network.WLAN(network.STA_IF)
    # wlan.active(True)
    # if not wlan.isconnected():
    #     print(f"Attempting to connect to WiFi SSID: {STA_SSID}...")
    #     wlan.connect(STA_SSID, STA_PASSWORD)
    #     timeout_ms = 10000 # 10-second timeout for connection
    #     start_ms = time.ticks_ms()
    #     while not wlan.isconnected():
    #         if time.ticks_diff(time.ticks_ms(), start_ms) > timeout_ms:
    #             print("[ERROR] WiFi connection timed out.")
    #             break
    #         time.sleep_ms(100) # Check status every 100ms
    # if wlan.isconnected():
    #     print(f"[INFO] WiFi connected. Network configuration: {wlan.ifconfig()}")
    # else:
    #     print("[WARN] WiFi connection failed or not configured.")
    # --- End Example ---
    print("[INFO] WiFi setup (setup_wifi) is a placeholder for future development.")
    pass # No operation in MVP

# --- Main Execution Block ---
if __name__ == "__main__":
    # Display a startup banner with information about the system.
    print("=" * 60)
    print("    SISTEMA GUARDIÃO - SACI Sensor Node MVP (MicroPython)")
    print("    Fire Prevention & Detection Proof of Concept")
    print("    Sensors: DHT22 (Temperature/Humidity), MQ-135 (Smoke/Gas)")
    print("    Target: ESP32 Microcontroller")
    print("=" * 60)
    
    # In a more complete system, you might call setup functions here:
    # print("[INFO] Initializing system...")
    # setup_wifi()        # Attempt to connect to WiFi
    # calibrate_sensors() # Perform sensor calibration if needed

    # Start the main sensor monitoring loop.
    # This function will run indefinitely until a KeyboardInterrupt or critical error.
    main_loop()
