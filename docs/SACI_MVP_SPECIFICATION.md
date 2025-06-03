# SACI MVP - SISTEMA DE PREVENÇÃO DE INCÊNDIOS
## Especificação Técnica Detalhada do Produto Mínimo Viável

---

## 1. VISÃO GERAL DO MVP

### 1.1 Objetivo do MVP
Desenvolver um sistema funcional de detecção precoce de incêndios utilizando:
- **Hardware**: Rede de sensores ESP32 com múltiplos sensores ambientais
- **Software**: Modelo de machine learning para predição de risco de incêndio
- **Comunicação**: Sistema de alertas em tempo real via LoRaWAN/WiFi

### 1.2 Escopo Limitado (MVP)
- **Área de cobertura**: 1 km² (grid de teste)
- **Número de sensores**: 10-15 nós ESP32
- **Período de teste**: 30 dias
- **Capacidades**: Detecção, predição, alerta básico

---

## 2. ESPECIFICAÇÕES DE HARDWARE

### 2.1 ESP32 Sensor Node Specification
```yaml
Core_Components:
  microcontroller: "ESP32-WROOM-32"
  flash_memory: "4MB"
  ram: "520KB"
  wifi: "802.11 b/g/n"
  bluetooth: "v4.2 BR/EDR and BLE"
  
Power_Management:
  battery: "LiPo 3.7V 5000mAh"
  solar_panel: "6V 2W monocrystalline"
  charging_controller: "TP4056"
  low_power_mode: "Deep sleep <10µA"
  
Sensor_Array:
  # NOTE: The currently implemented MVP firmware (src/hardware/esp32/saci_sensor_node.py)
  # primarily utilizes the DHT22 for temperature/humidity and an analog gas sensor
  # (like MQ-2 or MQ-135, referred to as MQ-2 in this section's original list) for air quality/smoke.
  # The sensors listed below represent the full planned specification for the SACI node
  # or future MVP iterations. The initial MVP focuses on core fire detection capabilities.
  temperature_humidity: "DHT22"
  smoke_detection: "MQ-2 gas sensor" 
  co2_measurement: "MH-Z19B NDIR"
  light_intensity: "BH1750"
  soil_moisture: "YL-69 resistive"
  wind_direction: "Hall effect encoder"
  wind_speed: "Anemometer with pulse output"
  atmospheric_pressure: "BMP280"

Communication:
  primary: "LoRaWAN (RFM95W 915MHz)"
  backup: "WiFi mesh networking"
  emergency: "ESP-NOW protocol"
  
Enclosure:
  material: "IP65 weatherproof ABS"
  mounting: "Pole mount with adjustable angles"
  antenna: "External 915MHz +3dBi"
```

### 2.2 Sensor Data Points Collected
```python
@dataclass
class SACIDataPoint:
    # Device identification
    device_id: str
    timestamp: datetime
    location: Tuple[float, float]  # lat, lon
    battery_level: float  # 0-100%
    
    # Environmental sensors
    temperature: float        # °C (-40 to +80)
    humidity: float          # % (0-100)
    smoke_density: int       # PPM (0-1000)
    co2_level: int          # PPM (400-5000)
    light_intensity: float   # Lux (0-65535)
    soil_moisture: float     # % (0-100)
    atmospheric_pressure: float  # hPa (300-1100)
    
    # Weather sensors
    wind_speed: float        # m/s (0-50)
    wind_direction: int      # degrees (0-359)
    
    # Calculated metrics
    heat_index: float        # °C
    fire_weather_index: float # 0-100 scale
    vegetation_stress: float  # 0-1 scale
    
    # Data quality
    sensor_health: Dict[str, bool]
    transmission_quality: int  # 1-5 scale
```

### 2.3 Network Architecture
```mermaid
graph TD
    A[ESP32 Sensor Node 1] -->|LoRaWAN| D[LoRaWAN Gateway]
    B[ESP32 Sensor Node 2] -->|LoRaWAN| D
    C[ESP32 Sensor Node ...N] -->|LoRaWAN| D
    
    D -->|4G/Ethernet| E[Cloud Processing]
    E --> F[ML Prediction Engine]
    E --> G[Alert System]
    E --> H[Dashboard/Monitoring]
    
    A -.->|WiFi Mesh Backup| B
    B -.->|WiFi Mesh Backup| C
```

---

## 3. SOFTWARE ARCHITECTURE

### 3.1 ESP32 Firmware Specification
```python
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

if __name__ == "__main__":
    print("=" * 60)
    print("SISTEMA GUARDIÃO - SACI MVP")
    print("Fire Prevention & Detection Sensor Node")
    print("ESP32 + DHT22 + MQ-135")
    print("=" * 60)
    
    # Run main monitoring loop
    main_loop()
```

### 3.2 Cloud Processing Architecture
```python
# saci_cloud_processor.py
from typing import List, Dict, Optional
import asyncio
import asyncpg
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta

class SACICloudProcessor:
    def __init__(self):
        self.postgres_pool = None
        self.influx_client = InfluxDBClient(
            url="http://localhost:8086",
            token="your-token",
            org="saci-org"
        )
        self.ml_model = self.load_ml_model()
        self.alert_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }
    
    async def initialize(self):
        """Initialize database connections"""
        self.postgres_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/saci_db"
        )
    
    async def process_sensor_data(self, sensor_data: Dict) -> Dict:
        """Main processing pipeline for incoming sensor data"""
        try:
            # 1. Validate and clean data
            cleaned_data = self.validate_sensor_data(sensor_data)
            
            # 2. Store in databases
            await self.store_sensor_data(cleaned_data)
            
            # 3. Calculate fire risk prediction
            risk_prediction = await self.predict_fire_risk(cleaned_data)
            
            # 4. Check for alerts
            alert_status = self.check_alert_conditions(risk_prediction)
            
            # 5. Update swarm coordination if needed
            if alert_status['level'] >= 2:  # Medium or higher
                await self.coordinate_swarm_response(cleaned_data, alert_status)
            
            return {
                'status': 'success',
                'device_id': cleaned_data['device_id'],
                'risk_prediction': risk_prediction,
                'alert_status': alert_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error processing sensor data: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def validate_sensor_data(self, data: Dict) -> Dict:
        """Validate and clean incoming sensor data"""
        cleaned = {}
        
        # Required fields
        required_fields = ['device_id', 'timestamp', 'location', 'sensors']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            cleaned[field] = data[field]
        
        # Sensor value validation
        sensors = data['sensors']
        cleaned['sensors'] = {
            'temperature': self._clamp(sensors.get('temperature', 0), -50, 80),
            'humidity': self._clamp(sensors.get('humidity', 0), 0, 100),
            'smoke': self._clamp(sensors.get('smoke', 0), 0, 1000),
            'co2': self._clamp(sensors.get('co2', 400), 400, 5000),
            'light': self._clamp(sensors.get('light', 0), 0, 65535),
            'moisture': self._clamp(sensors.get('moisture', 0), 0, 100),
            'wind_speed': self._clamp(sensors.get('wind_speed', 0), 0, 50),
            'wind_dir': self._clamp(sensors.get('wind_dir', 0), 0, 359),
            'pressure': self._clamp(sensors.get('pressure', 1013), 300, 1100)
        }
        
        return cleaned
    
    async def store_sensor_data(self, data: Dict):
        """Store data in PostgreSQL and InfluxDB"""
        # Store in PostgreSQL for relational queries
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO fire_sensor_data 
                (device_id, timestamp, location, temperature, humidity, smoke_level, 
                 co2_level, light_intensity, soil_moisture, wind_speed, wind_direction, pressure)
                VALUES ($1, $2, ST_SetSRID(ST_Point($3, $4), 4326), $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, 
                data['device_id'],
                datetime.fromisoformat(data['timestamp']),
                data['location']['lon'], data['location']['lat'],
                data['sensors']['temperature'],
                data['sensors']['humidity'],
                data['sensors']['smoke'],
                data['sensors']['co2'],
                data['sensors']['light'],
                data['sensors']['moisture'],
                data['sensors']['wind_speed'],
                data['sensors']['wind_dir'],
                data['sensors']['pressure']
            )
        
        # Store in InfluxDB for time series analysis
        write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
        point = Point("saci_sensors") \
            .tag("device_id", data['device_id']) \
            .tag("location", f"{data['location']['lat']},{data['location']['lon']}") \
            .field("temperature", data['sensors']['temperature']) \
            .field("humidity", data['sensors']['humidity']) \
            .field("smoke", data['sensors']['smoke']) \
            .field("co2", data['sensors']['co2']) \
            .field("light", data['sensors']['light']) \
            .field("moisture", data['sensors']['moisture']) \
            .field("wind_speed", data['sensors']['wind_speed']) \
            .field("wind_direction", data['sensors']['wind_dir']) \
            .field("pressure", data['sensors']['pressure']) \
            .time(datetime.fromisoformat(data['timestamp']))
        
        write_api.write(bucket="saci-bucket", record=point)
    
    async def predict_fire_risk(self, data: Dict) -> Dict:
        """Use ML model to predict fire risk"""
        # Prepare features for ML model
        features = np.array([[
            data['sensors']['temperature'],
            data['sensors']['humidity'],
            data['sensors']['smoke'],
            data['sensors']['co2'],
            data['sensors']['light'],
            data['sensors']['moisture'],
            data['sensors']['wind_speed'],
            data['sensors']['pressure']
        ]])
        
        # Get prediction from trained model
        risk_score = self.ml_model.predict(features)[0]
        confidence = self.ml_model.predict_proba(features).max()
        
        # Get historical context
        historical_risk = await self.get_historical_risk_context(
            data['location'], data['device_id']
        )
        
        # Combine current prediction with historical patterns
        adjusted_risk = self._adjust_risk_with_context(risk_score, historical_risk)
        
        return {
            'risk_score': float(adjusted_risk),
            'confidence': float(confidence),
            'factors': self._analyze_risk_factors(data['sensors']),
            'historical_context': historical_risk,
            'prediction_timestamp': datetime.utcnow().isoformat()
        }
    
    def check_alert_conditions(self, risk_prediction: Dict) -> Dict:
        """Determine if alerts should be triggered"""
        risk_score = risk_prediction['risk_score']
        confidence = risk_prediction['confidence']
        
        alert_level = 0
        alert_message = "Normal conditions"
        
        if risk_score >= self.alert_thresholds['critical'] and confidence > 0.8:
            alert_level = 4
            alert_message = "CRITICAL: Immediate fire risk detected"
        elif risk_score >= self.alert_thresholds['high'] and confidence > 0.7:
            alert_level = 3
            alert_message = "HIGH: Elevated fire risk"
        elif risk_score >= self.alert_thresholds['medium'] and confidence > 0.6:
            alert_level = 2
            alert_message = "MEDIUM: Increased fire risk"
        elif risk_score >= self.alert_thresholds['low']:
            alert_level = 1
            alert_message = "LOW: Watch conditions"
        
        return {
            'level': alert_level,
            'message': alert_message,
            'risk_score': risk_score,
            'confidence': confidence,
            'requires_action': alert_level >= 2
        }
    
    async def coordinate_swarm_response(self, sensor_data: Dict, alert_status: Dict):
        """Coordinate response among nearby sensors in the swarm"""
        # Find nearby sensors within 500m radius
        nearby_sensors = await self.find_nearby_sensors(
            sensor_data['location'], radius_meters=500
        )
        
        # Increase monitoring frequency for nearby sensors
        coordination_message = {
            'type': 'increase_monitoring',
            'trigger_device': sensor_data['device_id'],
            'alert_level': alert_status['level'],
            'new_interval': 60 if alert_status['level'] >= 3 else 180,  # seconds
            'duration': 3600  # 1 hour
        }
        
        # Send coordination commands to nearby sensors
        for sensor_id in nearby_sensors:
            await self.send_swarm_command(sensor_id, coordination_message)
    
    def load_ml_model(self):
        """Load pre-trained fire risk prediction model"""
        try:
            return joblib.load('models/saci_fire_risk_model.pkl')
        except FileNotFoundError:
            # Return a simple baseline model if trained model not available
            print("Warning: Using baseline model. Train proper model for production.")
            return self._create_baseline_model()
    
    def _create_baseline_model(self):
        """Create a simple baseline model for testing"""
        # This is a placeholder - replace with proper trained model
        from sklearn.dummy import DummyRegressor
        model = DummyRegressor(strategy='constant', constant=0.2)
        # Fit with dummy data
        X_dummy = np.random.random((100, 8))
        y_dummy = np.random.random(100)
        model.fit(X_dummy, y_dummy)
        return model
    
    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(value, max_val))
    
    def _analyze_risk_factors(self, sensors: Dict) -> Dict:
        """Analyze which factors contribute most to fire risk"""
        factors = {}
        
        # Temperature factor
        if sensors['temperature'] > 35:
            factors['high_temperature'] = {
                'contribution': 0.3,
                'description': f"High temperature: {sensors['temperature']}°C"
            }
        
        # Low humidity
        if sensors['humidity'] < 20:
            factors['low_humidity'] = {
                'contribution': 0.25,
                'description': f"Low humidity: {sensors['humidity']}%"
            }
        
        # Smoke detection
        if sensors['smoke'] > 300:
            factors['smoke_detected'] = {
                'contribution': 0.4,
                'description': f"Smoke detected: {sensors['smoke']} PPM"
            }
        
        # Dry soil
        if sensors['moisture'] < 15:
            factors['dry_soil'] = {
                'contribution': 0.2,
                'description': f"Dry soil: {sensors['moisture']}% moisture"
            }
        
        # High wind speed
        if sensors['wind_speed'] > 10:
            factors['high_wind'] = {
                'contribution': 0.15,
                'description': f"High wind speed: {sensors['wind_speed']} m/s"
            }
        
        return factors
```

---

## 4. MACHINE LEARNING MODEL

### 4.1 Fire Risk Prediction Model
```python
# saci_ml_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib

class SACIFireRiskModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'temperature', 'humidity', 'smoke_level', 'co2_level',
            'light_intensity', 'soil_moisture', 'wind_speed', 
            'atmospheric_pressure', 'heat_index', 'day_of_year',
            'hour_of_day', 'days_since_rain'
        ]
    
    def prepare_training_data(self) -> tuple:
        """Prepare training data from historical fire incidents and sensor data"""
        # This would load from your database/files
        # For MVP, we'll create synthetic training data
        
        # Generate synthetic data based on fire behavior knowledge
        np.random.seed(42)
        n_samples = 10000
        
        # Environmental conditions
        temperature = np.random.normal(25, 10, n_samples)
        humidity = np.random.normal(50, 20, n_samples)
        smoke_level = np.random.exponential(50, n_samples)
        co2_level = np.random.normal(400, 50, n_samples)
        light_intensity = np.random.normal(20000, 10000, n_samples)
        soil_moisture = np.random.normal(40, 15, n_samples)
        wind_speed = np.random.exponential(5, n_samples)
        pressure = np.random.normal(1013, 20, n_samples)
        
        # Derived features
        heat_index = temperature + 0.5 * (humidity - 50) / 100
        day_of_year = np.random.randint(1, 366, n_samples)
        hour_of_day = np.random.randint(0, 24, n_samples)
        days_since_rain = np.random.exponential(3, n_samples)
        
        # Create feature matrix
        X = np.column_stack([
            temperature, humidity, smoke_level, co2_level,
            light_intensity, soil_moisture, wind_speed, pressure,
            heat_index, day_of_year, hour_of_day, days_since_rain
        ])
        
        # Create target variable (fire risk score 0-1)
        # High risk conditions: high temp, low humidity, smoke, dry soil, wind
        fire_risk = (
            (temperature > 30) * 0.2 +
            (humidity < 30) * 0.2 +
            (smoke_level > 100) * 0.3 +
            (soil_moisture < 20) * 0.2 +
            (wind_speed > 8) * 0.1 +
            np.random.normal(0, 0.1, n_samples)  # noise
        )
        
        # Clip to 0-1 range
        fire_risk = np.clip(fire_risk, 0, 1)
        
        return X, fire_risk
    
    def train_model(self):
        """Train the fire risk prediction model"""
        print("Preparing training data...")
        X, y = self.prepare_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        print("Training Random Forest model...")
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        print("Training Gradient Boosting model...")
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Fit models
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_score = rf_model.score(X_test_scaled, y_test)
        gb_score = gb_model.score(X_test_scaled, y_test)
        
        print(f"Random Forest R² Score: {rf_score:.4f}")
        print(f"Gradient Boosting R² Score: {gb_score:.4f}")
        
        # Use the better performing model
        if rf_score > gb_score:
            self.model = rf_model
            print("Selected Random Forest as final model")
        else:
            self.model = gb_model
            print("Selected Gradient Boosting as final model")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Average CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nFeature Importance:")
            print(importance_df)
        
        return self.model
    
    def predict_fire_risk(self, sensor_data: dict) -> dict:
        """Predict fire risk for given sensor data"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Prepare features
        features = self._prepare_features(sensor_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Make prediction
        risk_score = self.model.predict(features_scaled)[0]
        
        # Get prediction confidence (for tree-based models)
        if hasattr(self.model, 'predict_proba'):
            # For classification models
            confidence = self.model.predict_proba(features_scaled).max()
        else:
            # For regression models, use prediction variance
            confidence = min(1.0, 1.0 - abs(risk_score - 0.5) * 2)
        
        return {
            'risk_score': float(np.clip(risk_score, 0, 1)),
            'confidence': float(confidence),
            'risk_category': self._categorize_risk(risk_score)
        }
    
    def _prepare_features(self, sensor_data: dict) -> np.ndarray:
        """Convert sensor data to feature vector"""
        from datetime import datetime
        
        # Extract sensor values
        temp = sensor_data.get('temperature', 25.0)
        humidity = sensor_data.get('humidity', 50.0)
        smoke = sensor_data.get('smoke_level', 0)
        co2 = sensor_data.get('co2_level', 400)
        light = sensor_data.get('light_intensity', 20000)
        moisture = sensor_data.get('soil_moisture', 40.0)
        wind_speed = sensor_data.get('wind_speed', 0.0)
        pressure = sensor_data.get('atmospheric_pressure', 1013.0)
        
        # Calculate derived features
        heat_index = temp + 0.5 * (humidity - 50) / 100
        
        # Time features
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        hour_of_day = now.hour
        
        # This would come from weather API or stored data
        days_since_rain = sensor_data.get('days_since_rain', 1.0)
        
        return np.array([
            temp, humidity, smoke, co2, light, moisture,
            wind_speed, pressure, heat_index, day_of_year,
            hour_of_day, days_since_rain
        ])
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into text labels"""
        if risk_score < 0.2:
            return "Very Low"
        elif risk_score < 0.4:
            return "Low"
        elif risk_score < 0.6:
            return "Moderate"
        elif risk_score < 0.8:
            return "High"
        else:
            return "Very High"
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        print(f"Model loaded from {filepath}")

# Training script
if __name__ == "__main__":
    # Train and save the model
    fire_model = SACIFireRiskModel()
    fire_model.train_model()
    fire_model.save_model('models/saci_fire_risk_model.pkl')
    
    # Test prediction
    test_data = {
        'temperature': 35.0,
        'humidity': 15.0,
        'smoke_level': 250,
        'co2_level': 420,
        'light_intensity': 45000,
        'soil_moisture': 8.0,
        'wind_speed': 12.0,
        'atmospheric_pressure': 1015.0,
        'days_since_rain': 7
    }
    
    result = fire_model.predict_fire_risk(test_data)
    print(f"\nTest prediction: {result}")
```

---

## 5. DEPLOYMENT ARCHITECTURE

### 5.1 MVP Deployment Specification
```yaml
# docker-compose.yml
version: '3.8'

services:
  saci-postgres:
    image: postgis/postgis:13-3.1
    environment:
      POSTGRES_DB: saci_db
      POSTGRES_USER: saci_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
  
  saci-influxdb:
    image: influxdb:2.0
    environment:
      INFLUXDB_DB: saci_timeseries
      INFLUXDB_ADMIN_USER: admin
      INFLUXDB_ADMIN_PASSWORD: secure_password
    volumes:
      - influx_data:/var/lib/influxdb2
    ports:
      - "8086:8086"
  
  saci-redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
  
  saci-api:
    build: ./api
    environment:
      - DATABASE_URL=postgresql://saci_user:secure_password@saci-postgres:5432/saci_db
      - INFLUXDB_URL=http://saci-influxdb:8086
      - REDIS_URL=redis://saci-redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - saci-postgres
      - saci-influxdb
      - saci-redis
    volumes:
      - ./models:/app/models
  
  saci-dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    depends_on:
      - saci-api
    environment:
      - API_URL=http://saci-api:8000
  
  lorawan-gateway:
    image: semtech/udp-packet-forwarder
    ports:
      - "1700:1700/udp"
    environment:
      - GATEWAY_EUI=AA555A0000000000
      - SERVER_ADDRESS=router.us.thethings.network
    privileged: true

volumes:
  postgres_data:
  influx_data:
  redis_data:
```

### 5.2 Testing Strategy
```python
# tests/test_saci_mvp.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from saci_cloud_processor import SACICloudProcessor

class TestSACIMVP:
    @pytest.fixture
    async def processor(self):
        processor = SACICloudProcessor()
        await processor.initialize()
        return processor
    
    @pytest.mark.asyncio
    async def test_sensor_data_validation(self, processor):
        """Test sensor data validation"""
        valid_data = {
            'device_id': 'SACI_001',
            'timestamp': '2024-01-15T10:30:00Z',
            'location': {'lat': -19.9167, 'lon': -43.9345},
            'sensors': {
                'temperature': 28.5,
                'humidity': 45.0,
                'smoke': 150,
                'co2': 420,
                'light': 25000,
                'moisture': 30.0,
                'wind_speed': 5.2,
                'wind_dir': 180,
                'pressure': 1013.2
            }
        }
        
        cleaned = processor.validate_sensor_data(valid_data)
        assert cleaned['device_id'] == 'SACI_001'
        assert cleaned['sensors']['temperature'] == 28.5
    
    @pytest.mark.asyncio
    async def test_fire_risk_prediction(self, processor):
        """Test fire risk prediction logic"""
        high_risk_data = {
            'device_id': 'SACI_001',
            'timestamp': '2024-01-15T10:30:00Z',
            'location': {'lat': -19.9167, 'lon': -43.9345},
            'sensors': {
                'temperature': 40.0,  # High temp
                'humidity': 15.0,     # Low humidity
                'smoke': 500,         # Smoke detected
                'co2': 450,
                'light': 50000,
                'moisture': 5.0,      # Very dry
                'wind_speed': 15.0,   # High wind
                'wind_dir': 180,
                'pressure': 1010.0
            }
        }
        
        risk_prediction = await processor.predict_fire_risk(high_risk_data)
        
        assert risk_prediction['risk_score'] > 0.6  # Should be high risk
        assert risk_prediction['confidence'] > 0.5
        assert 'factors' in risk_prediction
    
    @pytest.mark.asyncio
    async def test_alert_system(self, processor):
        """Test alert generation"""
        risk_prediction = {
            'risk_score': 0.85,
            'confidence': 0.9
        }
        
        alert_status = processor.check_alert_conditions(risk_prediction)
        
        assert alert_status['level'] >= 3  # Should be high alert
        assert alert_status['requires_action'] == True
        assert 'CRITICAL' in alert_status['message'] or 'HIGH' in alert_status['message']
    
    def test_sensor_hardware_simulation(self):
        """Test ESP32 sensor reading simulation"""
        # Simulate ESP32 sensor readings
        sensor_reading = {
            'temperature': 32.5,
            'humidity': 25.0,
            'smoke_level': 300,
            'co2_level': 430,
            'light_intensity': 35000,
            'soil_moisture': 15.0,
            'wind_speed': 8.5,
            'wind_direction': 225,
            'pressure': 1012.5,
            'battery_voltage': 3.7
        }
        
        # Test fire risk calculation (local ESP32 logic)
        fire_risk = self.calculate_local_fire_risk(sensor_reading)
        assert 0.0 <= fire_risk <= 1.0
        assert fire_risk > 0.3  # Should indicate some risk
    
    def calculate_local_fire_risk(self, reading):
        """Simulate ESP32 local fire risk calculation"""
        risk = 0.0
        
        if reading['temperature'] > 30.0:
            risk += (reading['temperature'] - 30.0) * 0.02
        
        if reading['humidity'] < 30.0:
            risk += (30.0 - reading['humidity']) * 0.01
        
        if reading['smoke_level'] > 200:
            risk += 0.4
        
        risk += reading['wind_speed'] * 0.01
        
        if reading['soil_moisture'] < 20.0:
            risk += (20.0 - reading['soil_moisture']) * 0.02
        
        return min(risk, 1.0)

# Performance tests
class TestSACIPerformance:
    @pytest.mark.asyncio
    async def test_data_processing_throughput(self):
        """Test system can handle expected data throughput"""
        processor = SACICloudProcessor()
        await processor.initialize()
        
        # Simulate 15 sensors sending data every 5 minutes
        # That's 180 messages per hour
        start_time = asyncio.get_event_loop().time()
        
        for i in range(100):  # Test with 100 messages
            sensor_data = self.generate_test_sensor_data(f"SACI_{i:03d}")
            await processor.process_sensor_data(sensor_data)
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Should process 100 messages in under 10 seconds
        assert processing_time < 10.0
        print(f"Processed 100 messages in {processing_time:.2f} seconds")
    
    def generate_test_sensor_data(self, device_id):
        """Generate realistic test sensor data"""
        import random
        return {
            'device_id': device_id,
            'timestamp': '2024-01-15T10:30:00Z',
            'location': {
                'lat': -19.9167 + random.uniform(-0.01, 0.01),
                'lon': -43.9345 + random.uniform(-0.01, 0.01)
            },
            'sensors': {
                'temperature': random.uniform(15, 45),
                'humidity': random.uniform(10, 90),
                'smoke': random.randint(0, 800),
                'co2': random.randint(400, 600),
                'light': random.randint(1000, 60000),
                'moisture': random.uniform(0, 80),
                'wind_speed': random.uniform(0, 20),
                'wind_dir': random.randint(0, 359),
                'pressure': random.uniform(990, 1030)
            }
        }
```

---

## 6. SUCCESS METRICS & KPIs

### 6.1 Technical Performance Metrics
```yaml
Performance_Targets:
  sensor_network:
    uptime: ">95%"
    data_transmission_success: ">98%"
    battery_life: ">30 days"
    sensor_accuracy: "±5% of calibrated values"
    
  cloud_processing:
    api_response_time: "<200ms"
    data_processing_latency: "<30 seconds"
    model_prediction_accuracy: ">85%"
    system_availability: ">99.5%"
    
  ml_model:
    false_positive_rate: "<10%"
    false_negative_rate: "<5%"
    prediction_confidence: ">80% for high-risk events"
    model_drift_detection: "weekly retraining"

Operational_Metrics:
  alert_system:
    time_to_alert: "<60 seconds from detection"
    alert_acknowledgment_rate: ">95%"
    escalation_accuracy: ">90%"
    
  maintenance:
    sensor_replacement_interval: ">6 months"
    system_self_healing: ">80% of minor issues"
    manual_intervention_required: "<5% of incidents"
```

### 6.2 Success Criteria for MVP
- **Hardware**: 15 sensor nodes deployed and operational for 30 days
- **Data Collection**: >10,000 sensor readings collected successfully
- **ML Performance**: Fire risk predictions with >80% accuracy
- **Alert System**: <2 minute response time for high-risk detections
- **Integration**: Seamless data flow from sensors to cloud to alerts
- **Documentation**: Complete technical documentation and user guides

---

This comprehensive SACI MVP specification provides the foundation for implementing a functional fire prevention system that can demonstrate the core capabilities of the Sistema Guardião platform.

---

## SACI MVP: Current Limitations and Future Enhancements

This section outlines the known limitations of the current Minimum Viable Product (MVP) for the SACI system and discusses potential enhancements for future development iterations. The MVP is designed to deliver core functionality and validate the system's concept, with the understanding that further improvements will be built upon this foundation.

### Current Limitations

1.  **Simplified Sensor Array:**
    *   The current MVP implementation, as detailed in `src/hardware/esp32/saci_sensor_node.py`, primarily utilizes a DHT22 sensor for temperature and humidity, and an analog gas sensor (like the MQ-135) for basic air quality and smoke detection. This is a simplified set compared to the full hardware specification which includes specialized sensors like the MH-Z19B (CO2), BH1750 (light intensity), soil moisture sensors, and anemometers.

2.  **Basic Machine Learning Model:**
    *   Fire risk prediction is currently handled by a Logistic Regression model, as implemented in `src/ml_models/saci_fire_predictor.py`. While functional for demonstrating the prediction pipeline, this is a relatively basic model and may not capture complex environmental interactions as effectively as more advanced algorithms.

3.  **Console-Only Application Interface:**
    *   The main integration application (`src/applications/saci_mvp_integration_app.py`) provides output and status updates exclusively through the console. It lacks a graphical user interface (GUI) or a web-based dashboard, which would offer more intuitive visualization and interaction for end-users.

4.  **Serial-Based Data Transmission:**
    *   Data transmission from the ESP32 sensor node to the host machine in the MVP primarily relies on a direct serial (USB) connection. This setup is suitable for development and testing but is not designed for field deployment over wider areas, which would typically require wireless protocols like LoRaWAN or MQTT.

5.  **No Implemented Swarm Intelligence:**
    *   The current MVP codebase does not include the advanced swarm intelligence features envisioned for the full SACI system. Features such as dynamic sensor coordination based on detected events, distributed data analysis, or optimized alert routing among nodes are not yet implemented.

### Future Enhancements

1.  **Full Sensor Integration:**
    *   Integrate the complete array of sensors as specified in the hardware design document. This includes incorporating the MH-Z19B for CO2 measurements, BH1750 for light intensity, soil moisture sensors, wind speed and direction sensors, and others. This will provide a richer dataset for more accurate environmental assessment and fire risk prediction.

2.  **Advanced Machine Learning Models:**
    *   Develop and deploy more sophisticated Machine Learning (e.g., Random Forests, Gradient Boosting Machines, Support Vector Machines) or Deep Learning models (e.g., LSTMs, CNNs for spatio-temporal analysis). This will aim to improve prediction accuracy, reduce false positives/negatives, and provide more nuanced risk assessments.

3.  **Graphical User Interface (GUI) / Web Dashboard:**
    *   Create a user-friendly GUI (desktop application) or a web-based dashboard. This interface will allow users to visualize real-time sensor data from multiple nodes, view current and historical fire risk levels on a map, receive and manage alerts, and configure system settings.

4.  **Robust Wireless Communication:**
    *   Implement field-deployable wireless communication protocols such as LoRaWAN (for long-range, low-power communication) or MQTT (for lightweight publish/subscribe messaging over IP networks like Wi-Fi or cellular). This is crucial for deploying sensor nodes across large geographical areas.

5.  **Swarm Intelligence Features:**
    *   Begin the phased introduction of swarm intelligence capabilities. This could start with features like:
        *   **Adaptive Sensing:** Allowing sensor nodes to dynamically adjust their sensing frequency or data transmission rates based on detected events or instructions from a central system or other nodes.
        *   **Collaborative Data Analysis:** Enabling nodes to share data or partial analyses with nearby nodes to improve local decision-making or validate alerts.
        *   **Optimized Alert Dissemination:** Developing strategies for alerts to propagate efficiently through the network to relevant stakeholders or actuator systems.
