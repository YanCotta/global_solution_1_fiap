# SISTEMA GUARDIÃO - DATA MODELS SPECIFICATION
## Comprehensive Data Schema Architecture

---

## 1. CURUPIRA - CYBERSECURITY DATA MODELS

### 1.1 Threat Detection Schema (PostgreSQL)
_Note: The `sql/init.sql` script provides a foundational `curupira.threat_events` table for the MVP. The models below (`physical_anomalies`, `network_events`, `threat_correlations`) represent a more detailed conceptual design for future expansion and comprehensive threat analysis within CURUPIRA._
```sql
-- Physical anomaly detection
CREATE TABLE physical_anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    anomaly_type VARCHAR(100) NOT NULL, -- temperature, vibration, electromagnetic
    severity_score DECIMAL(3,2) CHECK (severity_score BETWEEN 0 AND 1),
    sensor_readings JSONB NOT NULL,
    ml_confidence DECIMAL(3,2),
    correlation_group UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Network security events
CREATE TABLE network_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    source_ip INET,
    destination_ip INET,
    event_type VARCHAR(100) NOT NULL, -- intrusion, ddos, malware, phishing
    payload_hash VARCHAR(64),
    threat_score DECIMAL(3,2),
    geolocation GEOGRAPHY(POINT, 4326),
    user_agent TEXT,
    protocol VARCHAR(20),
    port_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hybrid threat correlation
CREATE TABLE threat_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    physical_anomaly_id UUID REFERENCES physical_anomalies(id),
    network_event_id UUID REFERENCES network_events(id),
    correlation_strength DECIMAL(3,2),
    attack_vector VARCHAR(200),
    coordinated_attack_probability DECIMAL(3,2),
    response_priority INTEGER CHECK (response_priority BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 1.2 CURUPIRA Time Series Data (InfluxDB)
```python
# Schema for Electromagnetic field measurements
curupira_emf = {
    "measurement": "electromagnetic_field",
    "tags": {
        "device_id": "string",
        "location": "string",
        "device_type": "string"
    },
    "fields": {
        "x_axis": "float",
        "y_axis": "float",
        "z_axis": "float",
        "frequency_spectrum": "float",
        "baseline_deviation": "float"
    },
    "time": "timestamp"
}

# Schema for Network traffic patterns
curupira_network = {
    "measurement": "network_traffic",
    "tags": {
        "device_id": "string",
        "network_segment": "string",
        "protocol": "string"
    },
    "fields": {
        "bytes_in": "float",
        "bytes_out": "float",
        "packets_in": "integer",
        "packets_out": "integer",
        "error_rate": "float",
        "latency": "float"
    },
    "time": "timestamp"
}
```

---

## 2. IARA - EPIDEMIOLOGICAL DATA MODELS

### 2.1 Health Surveillance Schema (PostgreSQL)
_Note: The `sql/init.sql` script includes a basic `iara.health_events` table for the MVP. The models detailed below (`environmental_health`, `disease_surveillance`, `seir_model_state`) provide the full conceptual data structure for IARA's comprehensive epidemiological analysis._
```sql
-- Environmental health factors
CREATE TABLE environmental_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    region_code VARCHAR(20) NOT NULL, -- IBGE municipal code
    air_quality_index INTEGER,
    water_quality_score DECIMAL(3,2),
    temperature DECIMAL(4,1),
    humidity DECIMAL(3,1),
    precipitation DECIMAL(5,2),
    uv_index INTEGER,
    pollution_pm25 DECIMAL(5,2),
    pollution_pm10 DECIMAL(5,2),
    vector_density JSONB, -- mosquito, tick populations
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Disease surveillance data
CREATE TABLE disease_surveillance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    region_code VARCHAR(20) NOT NULL,
    disease_code VARCHAR(10) NOT NULL, -- ICD-10
    case_count INTEGER NOT NULL,
    case_type VARCHAR(50), -- suspected, confirmed, hospitalized, deaths
    age_group VARCHAR(20),
    gender CHAR(1),
    risk_factors JSONB,
    travel_history JSONB,
    contact_tracing JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEIR model parameters
CREATE TABLE seir_model_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_code VARCHAR(20) NOT NULL,
    disease_code VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    susceptible INTEGER NOT NULL,
    exposed INTEGER NOT NULL,
    infectious INTEGER NOT NULL,
    recovered INTEGER NOT NULL,
    basic_reproduction_number DECIMAL(4,2),
    effective_reproduction_number DECIMAL(4,2),
    incubation_period DECIMAL(3,1),
    infectious_period DECIMAL(3,1),
    model_confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 IARA Time Series Data (InfluxDB)
```python
# Schema for Real-time health indicators
iara_health_metrics = {
    "measurement": "health_indicators",
    "tags": {
        "region_code": "string",
        "data_source": "string",
        "reliability": "string"
    },
    "fields": {
        "symptom_reports": "integer",
        "pharmacy_sales": "float",
        "hospital_admissions": "integer",
        "search_trends": "float",
        "social_media_sentiment": "float",
        "anomaly_score": "float"
    },
    "time": "timestamp"
}
```

---

## 3. SACI - FIRE PREVENTION DATA MODELS

### 3.1 Fire Detection Schema (PostgreSQL)
```sql
-- Sensor network data
-- Note: `sql/init.sql` implements this as `saci.sensor_devices`.
-- It includes `firmware_version` and `updated_at` fields not listed here.
-- Fields like `network_quality`, `elevation`, `vegetation_type` are part of the broader conceptual model.
CREATE TABLE fire_sensors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL, -- smoke, temperature, humidity, co2, methane
    installation_date DATE NOT NULL,
    last_maintenance DATE,
    battery_level DECIMAL(3,0) CHECK (battery_level BETWEEN 0 AND 100),
    network_quality INTEGER CHECK (network_quality BETWEEN 1 AND 5), -- Conceptual
    elevation DECIMAL(6,2), -- Conceptual
    vegetation_type VARCHAR(100), -- Conceptual
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fire risk assessment
-- Note: `sql/init.sql` implements this as `saci.fire_risk_predictions`.
-- It links risk to `device_id` (which has a location) rather than a separate `grid_cell_id` and `location` for the risk point itself.
-- Detailed risk components (weather, vegetation, etc.) are conceptually stored in JSONB fields (`contributing_factors`, `environmental_data`) in `sql/init.sql`.
CREATE TABLE fire_risk_assessment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    grid_cell_id VARCHAR(50) NOT NULL, -- 1km x 1km grid reference (Conceptual for gridded risk)
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- Location of the risk assessment point/grid cell
    risk_score DECIMAL(3,2) CHECK (risk_score BETWEEN 0 AND 1),
    weather_risk DECIMAL(3,2), -- Component of risk
    vegetation_risk DECIMAL(3,2), -- Component of risk
    human_activity_risk DECIMAL(3,2), -- Component of risk
    historical_risk DECIMAL(3,2), -- Component of risk
    ml_prediction DECIMAL(3,2), -- Raw ML model output
    confidence_interval DECIMAL(3,2), -- Confidence of the prediction
    alert_level INTEGER CHECK (alert_level BETWEEN 0 AND 4), -- Derived from risk_score
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fire incidents
-- Note: `sql/init.sql` implements this as `saci.fire_incidents` and includes additional fields
-- like `incident_id` (a string ID), `confirmed_at`, `response_teams` (JSONB), `status`, and `updated_at`.
-- The `response_time` (INTERVAL) and `cause` fields here are not explicitly in the current `sql/init.sql`.
CREATE TABLE fire_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id VARCHAR(50) UNIQUE, -- Added for consistency with common practice, present in init.sql
    detection_timestamp TIMESTAMPTZ NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    incident_type VARCHAR(50), -- wildfire, urban, industrial
    severity INTEGER CHECK (severity BETWEEN 1 AND 5),
    affected_area DECIMAL(10,2), -- hectares
    detection_method VARCHAR(100), -- sensor, satellite, human_report
    response_time INTERVAL, -- Conceptual
    extinguished_timestamp TIMESTAMPTZ,
    damage_assessment JSONB,
    cause VARCHAR(200), -- Conceptual
    weather_conditions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Swarm coordination
-- Note: This table is conceptual for future SACI enhancements and is not part of the current MVP `sql/init.sql` schema.
CREATE TABLE swarm_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(50), -- sensor, coordinator, predictor
    current_location GEOGRAPHY(POINT, 4326),
    assigned_grid_cells VARCHAR(500)[], -- array of grid cell IDs
    coordination_state VARCHAR(50), -- searching, monitoring, alerting, coordinating
    last_communication TIMESTAMPTZ,
    performance_metrics JSONB,
    neighbors JSONB, -- connected agents
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 SACI Time Series Data (InfluxDB)
```python
# Schema for Multi-sensor environmental data
saci_environmental = {
    "measurement": "environmental_sensors",
    "tags": {
        "device_id": "string",
        "sensor_type": "string",
        "location": "string",
        "vegetation_type": "string"
    },
    "fields": {
        "temperature": "float",
        "humidity": "float",
        "smoke_density": "float",
        "co2_level": "integer",
        "methane_level": "float",
        "wind_speed": "float",
        "wind_direction": "integer",
        "solar_radiation": "float",
        "soil_moisture": "float",
        "fire_risk_score": "float"
    },
    "time": "timestamp"
}

# Schema for Weather station integration
saci_weather = {
    "measurement": "weather_data",
    "tags": {
        "station_id": "string",
        "region_code": "string",
        "elevation": "string"
    },
    "fields": {
        "temperature": "float",
        "humidity": "float",
        "pressure": "float",
        "wind_speed": "float",
        "wind_direction": "integer",
        "precipitation": "float",
        "solar_radiation": "float",
        "cloud_coverage": "integer"
    },
    "time": "timestamp"
}
```

---

## 4. BOITATÁ - URBAN INFRASTRUCTURE DATA MODELS

### 4.1 Infrastructure Monitoring Schema (PostgreSQL)
_Note: The `sql/init.sql` script includes a very basic `boitata.infrastructure_elements` table for the MVP. The models detailed below (`infrastructure_assets`, `cascade_scenarios`, `digital_twin_state`) represent the full conceptual data structure for BOITATÁ's advanced infrastructure monitoring and analysis capabilities._
```sql
-- Urban infrastructure assets
CREATE TABLE infrastructure_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id VARCHAR(255) UNIQUE NOT NULL,
    asset_type VARCHAR(100) NOT NULL, -- power_grid, water_system, transport, telecom
    subsystem VARCHAR(100),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    criticality_level INTEGER CHECK (criticality_level BETWEEN 1 AND 5),
    dependencies JSONB, -- array of dependent asset IDs
    capacity_rating DECIMAL(10,2),
    current_load DECIMAL(10,2),
    operational_status VARCHAR(50),
    last_maintenance TIMESTAMPTZ,
    redundancy_factor DECIMAL(3,2),
    failure_impact_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cascade failure analysis
CREATE TABLE cascade_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_name VARCHAR(200) NOT NULL,
    trigger_asset_id UUID REFERENCES infrastructure_assets(id),
    timestamp TIMESTAMPTZ NOT NULL,
    propagation_path JSONB, -- ordered array of affected assets
    failure_probability DECIMAL(3,2),
    estimated_impact JSONB,
    mitigation_strategies JSONB,
    simulation_duration INTERVAL,
    population_affected INTEGER,
    economic_impact DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Digital twin state
CREATE TABLE digital_twin_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES infrastructure_assets(id),
    timestamp TIMESTAMPTZ NOT NULL,
    physical_state JSONB, -- current sensor readings
    digital_state JSONB, -- simulated state
    deviation_score DECIMAL(3,2),
    prediction_horizon INTERVAL,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    maintenance_recommendation JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 BOITATÁ Graph Database (Neo4j)
```cypher
// Infrastructure dependency graph
CREATE (asset:InfrastructureAsset {
    id: $asset_id,
    type: $asset_type,
    criticality: $criticality_level,
    location: point({latitude: $lat, longitude: $lon})
})

// Dependency relationships
CREATE (a1:InfrastructureAsset)-[:DEPENDS_ON {
    dependency_type: $dep_type,
    failure_probability: $prob,
    impact_weight: $weight
}]->(a2:InfrastructureAsset)

// Cascade failure queries
MATCH (trigger:InfrastructureAsset {id: $failed_asset})
CALL apoc.path.expandConfig(trigger, {
    relationshipFilter: "DEPENDS_ON>",
    minLevel: 1,
    maxLevel: 5
}) YIELD path
RETURN path
```

---

## 5. ANHANGÁ - RESILIENT COMMUNICATIONS DATA MODELS

### 5.1 Communication Networks Schema (PostgreSQL)
_Note: The `sql/init.sql` script includes a foundational `anhanga.communication_channels` table for the MVP. The models detailed below (`communication_nodes`, `network_resilience`, `emergency_messages`) provide the comprehensive conceptual data architecture for ANHANGÁ._
```sql
-- Communication nodes
CREATE TABLE communication_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id VARCHAR(255) UNIQUE NOT NULL,
    node_type VARCHAR(100) NOT NULL, -- cellular_tower, satellite, mesh_node, emergency_radio
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    coverage_radius DECIMAL(8,2), -- meters
    technology VARCHAR(50), -- 5G, LoRaWAN, satellite, mesh
    operational_status VARCHAR(50),
    power_source VARCHAR(50), -- grid, battery, solar, generator
    backup_power_duration INTERVAL,
    current_load DECIMAL(3,2),
    max_capacity INTEGER,
    redundant_connections INTEGER,
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Network resilience metrics
CREATE TABLE network_resilience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    network_segment VARCHAR(100),
    connectivity_score DECIMAL(3,2),
    redundancy_factor DECIMAL(3,2),
    latency_ms INTEGER,
    packet_loss_rate DECIMAL(5,4),
    bandwidth_utilization DECIMAL(3,2),
    emergency_capacity_available DECIMAL(3,2),
    mesh_healing_time INTERVAL,
    satellite_backup_status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Emergency communications
CREATE TABLE emergency_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    originating_subsystem VARCHAR(50), -- curupira, iara, saci, boitata
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    message_type VARCHAR(100),
    content TEXT NOT NULL,
    target_audience VARCHAR(100),
    geographic_scope GEOGRAPHY(POLYGON, 4326),
    delivery_channels VARCHAR(100)[],
    delivery_status JSONB,
    acknowledgments INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. CROSS-SYSTEM INTEGRATION MODELS

### 6.1 Central Orchestrator Schema (PostgreSQL)
_Note: The tables `guardian_events` and `coordination_matrix` described below are conceptual models for cross-system integration and are not yet implemented in the current `sql/init.sql` MVP schema. The `sql/init.sql` does include a `guardian_core.cross_system_events` table that serves as a more developed starting point for system-wide event tracking, which should be considered the current implemented direction for this concept._
```sql
-- System-wide events
CREATE TABLE guardian_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    originating_subsystem VARCHAR(50) NOT NULL,
    severity INTEGER CHECK (severity BETWEEN 1 AND 5),
    geographic_scope GEOGRAPHY(POLYGON, 4326),
    affected_population INTEGER,
    coordination_required BOOLEAN DEFAULT FALSE,
    response_actions JSONB,
    status VARCHAR(50) DEFAULT 'active',
    resolution_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inter-subsystem coordination
CREATE TABLE coordination_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_event_id UUID REFERENCES guardian_events(id),
    coordinating_subsystems VARCHAR(50)[],
    coordination_type VARCHAR(100), -- data_sharing, joint_response, resource_allocation
    coordination_strength DECIMAL(3,2),
    sync_status VARCHAR(50),
    data_exchanges JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.2 API Data Models (GraphQL Schema)
```graphql
type GuardianEvent {
  id: ID!
  eventId: String!
  timestamp: DateTime!
  eventType: String!
  originatingSubsystem: Subsystem!
  severity: Int!
  geographicScope: Polygon
  affectedPopulation: Int
  coordinationRequired: Boolean!
  responseActions: JSON
  status: EventStatus!
}

type ThreatCorrelation {
  id: ID!
  physicalAnomaly: PhysicalAnomaly
  networkEvent: NetworkEvent
  correlationStrength: Float!
  attackVector: String
  coordinatedAttackProbability: Float!
}

type FireRiskAssessment {
  id: ID!
  timestamp: DateTime!
  gridCellId: String!
  location: Point!
  riskScore: Float!
  weatherRisk: Float!
  vegetationRisk: Float!
  humanActivityRisk: Float!
  alertLevel: Int!
}

type CascadeScenario {
  id: ID!
  scenarioName: String!
  triggerAsset: InfrastructureAsset!
  propagationPath: [InfrastructureAsset!]!
  failureProbability: Float!
  estimatedImpact: JSON
  populationAffected: Int
  economicImpact: Float
}

enum Subsystem {
  CURUPIRA
  IARA
  SACI
  BOITATA
  ANHANGA
}

enum EventStatus {
  ACTIVE
  MONITORING
  RESPONDING
  RESOLVED
  ESCALATED
}
```

---

## 7. DATA INTEGRATION & SYNCHRONIZATION

### 7.1 Event Stream Processing (Apache Kafka Topics)
```yaml
# Kafka topic configuration
topics:
  guardian.curupira.threats:
    partitions: 12
    replication_factor: 3
    retention_ms: 604800000  # 7 days
    
  guardian.iara.health_alerts:
    partitions: 8
    replication_factor: 3
    retention_ms: 2592000000  # 30 days
    
  guardian.saci.fire_detections:
    partitions: 16
    replication_factor: 3
    retention_ms: 31536000000  # 1 year
    
  guardian.boitata.infrastructure_events:
    partitions: 10
    replication_factor: 3
    retention_ms: 7776000000  # 90 days
    
  guardian.anhanga.communication_status:
    partitions: 6
    replication_factor: 3
    retention_ms: 172800000  # 2 days
```

### 7.2 Real-time Data Pipeline
```python
# Example integration schema
@dataclass
class GuardianEventMessage:
    event_id: str
    subsystem: str
    timestamp: datetime
    event_type: str
    severity: int
    location: Optional[Tuple[float, float]]
    data_payload: Dict[str, Any]
    correlation_tags: List[str]
    requires_coordination: bool
    
class DataIntegrationLayer:
    def __init__(self):
        self.kafka_producer = KafkaProducer()
        self.redis_cache = Redis()
        self.postgres_pool = asyncpg.create_pool()
        self.influx_client = InfluxDBClient()
        
    async def process_multi_system_event(self, event: GuardianEventMessage):
        # Cross-system correlation and coordination logic
        pass
```

---

## 8. PERFORMANCE & SCALING CONSIDERATIONS

### 8.1 Database Partitioning Strategy
- **Time-based partitioning**: All sensor data partitioned by month
- **Geographic partitioning**: Regional data distributed across nodes
- **Subsystem partitioning**: Each subsystem has dedicated database instances

### 8.2 Data Retention Policies
- **Real-time data**: 7-30 days in hot storage
- **Historical analytics**: 1-5 years in warm storage
- **Critical incidents**: Permanent archival in cold storage
- **ML training data**: Rolling 2-year window

---

This comprehensive data model specification provides the foundation for implementing the Sistema Guardião with proper data architecture, ensuring scalability, performance, and cross-system integration capabilities.
