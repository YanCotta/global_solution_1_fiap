-- Sistema Guardião - Database Initialization
-- PostgreSQL Schema Creation for SACI MVP

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create database schema
CREATE SCHEMA IF NOT EXISTS saci;
CREATE SCHEMA IF NOT EXISTS curupira;
CREATE SCHEMA IF NOT EXISTS iara;
CREATE SCHEMA IF NOT EXISTS boitata;
CREATE SCHEMA IF NOT EXISTS anhanga;

-- SACI Fire Prevention Tables
CREATE TABLE saci.sensor_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) UNIQUE NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    device_type VARCHAR(30) NOT NULL,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_maintenance TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    battery_level DECIMAL(5,2),
    firmware_version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE saci.fire_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(50) UNIQUE NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    extinguished_at TIMESTAMP WITH TIME ZONE,
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    affected_area DECIMAL(10,2), -- hectares
    detection_method VARCHAR(50),
    weather_conditions JSONB,
    response_teams JSONB,
    damage_assessment JSONB,
    status VARCHAR(30) DEFAULT 'detected',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE saci.fire_risk_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) REFERENCES saci.sensor_devices(device_id),
    prediction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    risk_score DECIMAL(5,4) CHECK (risk_score BETWEEN 0 AND 1),
    risk_level VARCHAR(20) NOT NULL, -- low, medium, high, critical
    contributing_factors JSONB,
    ml_model_version VARCHAR(20),
    confidence_score DECIMAL(5,4),
    environmental_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert fire_risk_predictions to hypertable for time series
SELECT create_hypertable('saci.fire_risk_predictions', 'prediction_timestamp');

-- CURUPIRA Cybersecurity Tables (Basic structure)
CREATE TABLE curupira.threat_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    threat_type VARCHAR(50) NOT NULL,
    severity_score DECIMAL(3,2) CHECK (severity_score BETWEEN 0 AND 1),
    source_ip INET,
    target_system VARCHAR(100),
    event_details JSONB,
    mitigated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- IARA Health Surveillance Tables (Basic structure)
CREATE TABLE iara.health_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    population_affected INTEGER,
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    event_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BOITATÁ Infrastructure Tables (Basic structure)
CREATE TABLE boitata.infrastructure_elements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    element_type VARCHAR(50) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    capacity DECIMAL(15,2),
    current_load DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'operational',
    dependencies JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ANHANGÁ Communications Tables (Basic structure)
CREATE TABLE anhanga.communication_channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_type VARCHAR(50) NOT NULL,
    coverage_area GEOGRAPHY(POLYGON, 4326),
    capacity INTEGER,
    current_usage DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'active',
    backup_channels JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_sensor_devices_location ON saci.sensor_devices USING GIST (location);
CREATE INDEX idx_fire_incidents_location ON saci.fire_incidents USING GIST (location);
CREATE INDEX idx_fire_incidents_detected_at ON saci.fire_incidents (detected_at);
CREATE INDEX idx_fire_risk_predictions_device_timestamp ON saci.fire_risk_predictions (device_id, prediction_timestamp);
CREATE INDEX idx_fire_risk_predictions_risk_level ON saci.fire_risk_predictions (risk_level);

-- Insert sample data for SACI MVP
INSERT INTO saci.sensor_devices (device_id, location, device_type, battery_level, firmware_version) VALUES
('ESP32_001', ST_GeogFromText('POINT(-43.9345 -19.9167)'), 'Multi-Sensor', 85.5, 'v1.2.0'),
('ESP32_002', ST_GeogFromText('POINT(-43.8345 -19.8167)'), 'Multi-Sensor', 72.3, 'v1.2.0'),
('ESP32_003', ST_GeogFromText('POINT(-43.7345 -19.7167)'), 'Multi-Sensor', 91.8, 'v1.2.0'),
('ESP32_004', ST_GeogFromText('POINT(-43.6345 -19.6167)'), 'Multi-Sensor', 68.9, 'v1.2.0'),
('ESP32_005', ST_GeogFromText('POINT(-43.5345 -19.5167)'), 'Multi-Sensor', 88.2, 'v1.2.0');

-- Sample fire risk predictions
INSERT INTO saci.fire_risk_predictions (device_id, prediction_timestamp, risk_score, risk_level, contributing_factors, ml_model_version, confidence_score) VALUES
('ESP32_001', NOW() - INTERVAL '1 hour', 0.15, 'low', '{"temperature": 22.5, "humidity": 65.2, "wind_speed": 2.3}', 'v1.0.0', 0.87),
('ESP32_002', NOW() - INTERVAL '30 minutes', 0.78, 'high', '{"temperature": 33.2, "humidity": 38.9, "wind_speed": 12.1}', 'v1.0.0', 0.92),
('ESP32_003', NOW() - INTERVAL '15 minutes', 0.35, 'medium', '{"temperature": 28.8, "humidity": 55.3, "wind_speed": 4.2}', 'v1.0.0', 0.84),
('ESP32_004', NOW() - INTERVAL '5 minutes', 0.89, 'critical', '{"temperature": 37.2, "humidity": 29.4, "wind_speed": 18.7}', 'v1.0.0', 0.95),
('ESP32_005', NOW(), 0.22, 'low', '{"temperature": 26.4, "humidity": 58.7, "wind_speed": 3.8}', 'v1.0.0', 0.81);

-- Create views for easy data access
CREATE OR REPLACE VIEW saci.current_risk_status AS
SELECT 
    sd.device_id,
    sd.location,
    frp.risk_score,
    frp.risk_level,
    frp.prediction_timestamp,
    frp.confidence_score,
    sd.battery_level,
    sd.status as device_status
FROM saci.sensor_devices sd
JOIN saci.fire_risk_predictions frp ON sd.device_id = frp.device_id
WHERE frp.prediction_timestamp = (
    SELECT MAX(prediction_timestamp) 
    FROM saci.fire_risk_predictions frp2 
    WHERE frp2.device_id = sd.device_id
);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA saci TO guardiao;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA curupira TO guardiao;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA iara TO guardiao;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA boitata TO guardiao;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA anhanga TO guardiao;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA saci TO guardiao;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA curupira TO guardiao;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA iara TO guardiao;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA boitata TO guardiao;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA anhanga TO guardiao;
