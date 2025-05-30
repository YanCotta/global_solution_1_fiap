# SACI MVP - ESP32 Sensor Node (MicroPython)
# Sistema Guardião - Fire Prevention and Detection
# Author: Yan Cotta
# Date: May 30, 2025

import machine
import time
import dht
from machine import Pin, ADC
import gc

# Pin Configuration
DHT22_PIN = 2  # GPIO2 (D4)
MQ135_PIN = 36  # GPIO36 (VP - ADC1_CH0)

# Sensor initialization
try:
    dht_sensor = dht.DHT22(Pin(DHT22_PIN))
    mq135_adc = ADC(Pin(MQ135_PIN))
    mq135_adc.atten(ADC.ATTN_11DB)  # For 3.3V range
    print("SACI MVP - Sensors initialized successfully")
except Exception as e:
    print(f"Sensor initialization error: {e}")

# Constants
READING_INTERVAL = 2  # seconds
SMOKE_THRESHOLD = 400  # Basic threshold for smoke detection
TEMP_THRESHOLD = 35   # Temperature threshold in Celsius

def read_dht22():
    """
    Read temperature and humidity from DHT22 sensor
    Returns: tuple (temperature, humidity) or (None, None) if error
    """
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except OSError as e:
        print(f"DHT22 read error: {e}")
        return None, None

def read_mq135():
    """
    Read analog value from MQ-135 gas sensor
    Returns: int (0-4095) or None if error
    """
    try:
        # Read raw ADC value (0-4095 for 12-bit ADC)
        raw_value = mq135_adc.read()
        return raw_value
    except Exception as e:
        print(f"MQ-135 read error: {e}")
        return None

def calculate_fire_risk(temperature, humidity, smoke_level):
    """
    Calculate basic fire risk based on sensor readings
    Returns: string risk level
    """
    if temperature is None or humidity is None or smoke_level is None:
        return "UNKNOWN"
    
    risk_score = 0
    
    # Temperature factor
    if temperature > TEMP_THRESHOLD:
        risk_score += 2
    elif temperature > 30:
        risk_score += 1
    
    # Humidity factor (lower humidity = higher risk)
    if humidity < 30:
        risk_score += 2
    elif humidity < 50:
        risk_score += 1
    
    # Smoke level factor
    if smoke_level > SMOKE_THRESHOLD:
        risk_score += 3
    elif smoke_level > 300:
        risk_score += 1
    
    # Determine risk level
    if risk_score >= 5:
        return "HIGH"
    elif risk_score >= 3:
        return "MEDIUM"
    elif risk_score >= 1:
        return "LOW"
    else:
        return "MINIMAL"

def format_sensor_data(temperature, humidity, smoke_level):
    """
    Format sensor data for serial output
    """
    risk_level = calculate_fire_risk(temperature, humidity, smoke_level)
    
    # Handle None values
    temp_str = f"{temperature:.1f}" if temperature is not None else "ERROR"
    hum_str = f"{humidity:.1f}" if humidity is not None else "ERROR"
    smoke_str = f"{smoke_level}" if smoke_level is not None else "ERROR"
    
    return f"Temp: {temp_str} C, Hum: {hum_str} %, Smoke: {smoke_str}, Risk: {risk_level}"

def main_loop():
    """
    Main sensor reading loop
    """
    print("SACI MVP starting sensor monitoring...")
    print("Format: Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL")
    print("-" * 60)
    
    reading_count = 0
    
    while True:
        try:
            # Read sensors
            temperature, humidity = read_dht22()
            smoke_level = read_mq135()
            
            # Format and print data
            sensor_data = format_sensor_data(temperature, humidity, smoke_level)
            print(sensor_data)
            
            # Memory management
            reading_count += 1
            if reading_count % 50 == 0:  # Every 100 seconds
                gc.collect()
                print(f"[INFO] Memory cleanup - Free: {gc.mem_free()} bytes")
            
            # Wait for next reading
            time.sleep(READING_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nSACI MVP monitoring stopped by user")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(READING_INTERVAL)

# Additional functions for future expansion
def send_alert(risk_level, temperature, humidity, smoke_level):
    """
    Future function to send alerts via WiFi/LoRa
    Currently just prints alert
    """
    if risk_level in ["HIGH", "MEDIUM"]:
        print(f"*** ALERT: {risk_level} FIRE RISK DETECTED ***")
        print(f"T: {temperature}°C, H: {humidity}%, S: {smoke_level}")

def calibrate_sensors():
    """
    Future function for sensor calibration
    """
    print("Sensor calibration not implemented in MVP")
    pass

# WiFi configuration for future use
def setup_wifi():
    """
    Future WiFi setup for data transmission
    """
    # import network
    # wlan = network.WLAN(network.STA_IF)
    # wlan.active(True)
    # wlan.connect('SSID', 'PASSWORD')
    print("WiFi setup not implemented in MVP")
    pass

if __name__ == "__main__":
    print("=" * 60)
    print("SISTEMA GUARDIÃO - SACI MVP")
    print("Fire Prevention & Detection Sensor Node")
    print("ESP32 + DHT22 + MQ-135")
    print("=" * 60)
    
    # Run main monitoring loop
    main_loop()
