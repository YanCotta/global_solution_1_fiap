# SISTEMA GUARDIÃO - ARCHITECTURE OVERVIEW
## Complete System Architecture Specification

---

## 1. SYSTEM CONTEXT (C4 Level 1)

```mermaid
graph TB
    subgraph "External Systems"
        WEATHER[Weather APIs]
        SATELLITE[Satellite Data]
        EMERGENCY[Emergency Services]
        CITIZENS[Citizens & Mobile Apps]
    end
    
    subgraph "Sistema Guardião"
        GUARDIAN[Guardian Central Orchestrator]
        CURUPIRA[CURUPIRA - Cybersecurity]
        IARA[IARA - Health Surveillance]
        SACI[SACI - Fire Prevention]
        BOITATA[BOITATÁ - Infrastructure]
        ANHANGA[ANHANGÁ - Communications]
    end
    
    subgraph "Infrastructure"
        SENSORS[IoT Sensor Network]
        CLOUD[Cloud Platform]
        NETWORKS[Communication Networks]
    end
    
    WEATHER --> GUARDIAN
    SATELLITE --> GUARDIAN
    GUARDIAN --> EMERGENCY
    GUARDIAN --> CITIZENS
    
    GUARDIAN <--> CURUPIRA
    GUARDIAN <--> IARA
    GUARDIAN <--> SACI
    GUARDIAN <--> BOITATA
    GUARDIAN <--> ANHANGA
    
    SENSORS --> CLOUD
    CLOUD --> NETWORKS
```

---

## 2. CONTAINER ARCHITECTURE (C4 Level 2)

### 2.1 Core Platform Containers
```mermaid
graph TB
    subgraph "Web Layer"
        WEB[Web Dashboard]
        MOBILE[Mobile App]
        API_GW[API Gateway]
    end
    
    subgraph "Application Layer"
        ORCHESTRATOR[Central Orchestrator]
        SACI_API[SACI API Service]
        CURUPIRA_API[CURUPIRA API Service]
        IARA_API[IARA API Service]
        BOITATA_API[BOITATÁ API Service]
        ANHANGA_API[ANHANGÁ API Service]
    end
    
    subgraph "Processing Layer"
        ML_ENGINE[ML Processing Engine]
        STREAM_PROC[Stream Processor]
        ALERT_SVC[Alert Service]
        COORD_SVC[Coordination Service]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        INFLUXDB[(InfluxDB)]
        REDIS[(Redis Cache)]
        NEO4J[(Neo4j Graph)]
    end
    
    subgraph "Infrastructure"
        MQTT[MQTT Broker]
        KAFKA[Kafka Streams]
        MONITORING[Monitoring Stack]
    end
    
    WEB --> API_GW
    MOBILE --> API_GW
    API_GW --> ORCHESTRATOR
    
    ORCHESTRATOR --> SACI_API
    ORCHESTRATOR --> CURUPIRA_API
    ORCHESTRATOR --> IARA_API
    ORCHESTRATOR --> BOITATA_API
    ORCHESTRATOR --> ANHANGA_API
    
    SACI_API --> ML_ENGINE
    SACI_API --> STREAM_PROC
    STREAM_PROC --> ALERT_SVC
    ORCHESTRATOR --> COORD_SVC
    
    ML_ENGINE --> POSTGRES
    ML_ENGINE --> INFLUXDB
    STREAM_PROC --> KAFKA
    ALERT_SVC --> REDIS
    COORD_SVC --> NEO4J
    
    MQTT --> KAFKA
    KAFKA --> STREAM_PROC
```

### 2.2 Technology Stack
```yaml
Frontend:
  web_dashboard: "React.js + TypeScript"
  mobile_app: "React Native"
  visualization: "D3.js + Mapbox GL"
  
API_Gateway:
  implementation: "Kong or AWS API Gateway"
  authentication: "JWT + OAuth2"
  rate_limiting: "Redis-based"
  
Backend_Services:
  api_framework: "FastAPI (Python)"
  async_processing: "Celery + Redis"
  websockets: "WebSocket support"
  
Databases:
  relational: "PostgreSQL with PostGIS"
  time_series: "InfluxDB 2.0"
  graph: "Neo4j Community"
  cache: "Redis Cluster"
  
Message_Queuing:
  streaming: "Apache Kafka"
  mqtt: "Eclipse Mosquitto"
  pub_sub: "Redis Pub/Sub"
  
ML_Platform:
  training: "scikit-learn + XGBoost"
  serving: "MLflow + FastAPI"
  pipelines: "Apache Airflow"
  
Monitoring:
  metrics: "Prometheus + Grafana"
  logging: "ELK Stack"
  tracing: "Jaeger"
  errors: "Sentry"
  
Deployment:
  containerization: "Docker + Docker Compose"
  orchestration: "Kubernetes"
  ci_cd: "GitHub Actions"
  infrastructure: "Terraform"
```

---

## 3. COMPONENT ARCHITECTURE (C4 Level 3)

### 3.1 SACI Fire Prevention Components
```mermaid
graph TB
    subgraph "SACI Fire Prevention System"
        subgraph "Data Ingestion"
            SENSOR_MGR[Sensor Manager]
            DATA_VAL[Data Validator]
            WEATHER_INT[Weather Integrator]
        end
        
        subgraph "Processing Engine"
            RISK_CALC[Risk Calculator]
            ML_PRED[ML Predictor]
            PATTERN_DET[Pattern Detector]
        end
        
        subgraph "Swarm Intelligence"
            SWARM_COORD[Swarm Coordinator]
            AGENT_MGR[Agent Manager]
            CONSENSUS[Consensus Engine]
        end
        
        subgraph "Alert System"
            ALERT_GEN[Alert Generator]
            NOTIF_SVC[Notification Service]
            ESCAL_MGR[Escalation Manager]
        end
        
        subgraph "Data Storage"
            SENSOR_DB[(Sensor Data)]
            RISK_DB[(Risk Assessments)]
            INCIDENT_DB[(Fire Incidents)]
        end
    end
    
    SENSOR_MGR --> DATA_VAL
    DATA_VAL --> RISK_CALC
    WEATHER_INT --> RISK_CALC
    
    RISK_CALC --> ML_PRED
    ML_PRED --> PATTERN_DET
    PATTERN_DET --> ALERT_GEN
    
    SWARM_COORD --> AGENT_MGR
    AGENT_MGR --> CONSENSUS
    CONSENSUS --> ALERT_GEN
    
    ALERT_GEN --> NOTIF_SVC
    NOTIF_SVC --> ESCAL_MGR
    
    DATA_VAL --> SENSOR_DB
    RISK_CALC --> RISK_DB
    ALERT_GEN --> INCIDENT_DB
```

### 3.2 CURUPIRA Cybersecurity Components
```mermaid
graph TB
    subgraph "CURUPIRA Cybersecurity System"
        subgraph "Threat Detection"
            PHYSICAL_MON[Physical Monitor]
            NETWORK_MON[Network Monitor]
            HYBRID_DETECT[Hybrid Detector]
        end
        
        subgraph "Analysis Engine"
            ANOMALY_DET[Anomaly Detector]
            CORRELATION[Correlation Engine]
            THREAT_INTEL[Threat Intelligence]
        end
        
        subgraph "Response System"
            AUTO_RESP[Auto Response]
            ISOLATION[Network Isolation]
            FORENSICS[Digital Forensics]
        end
        
        subgraph "Data Storage"
            THREAT_DB[(Threat Database)]
            LOG_STORE[(Security Logs)]
            INTEL_DB[(Threat Intelligence)]
        end
    end
    
    PHYSICAL_MON --> HYBRID_DETECT
    NETWORK_MON --> HYBRID_DETECT
    HYBRID_DETECT --> ANOMALY_DET
    
    ANOMALY_DET --> CORRELATION
    CORRELATION --> THREAT_INTEL
    THREAT_INTEL --> AUTO_RESP
    
    AUTO_RESP --> ISOLATION
    ISOLATION --> FORENSICS
    
    HYBRID_DETECT --> THREAT_DB
    ANOMALY_DET --> LOG_STORE
    THREAT_INTEL --> INTEL_DB
```

### 3.3 IARA Health Surveillance Components
```mermaid
graph TB
    subgraph "IARA Health Surveillance System"
        subgraph "Data Collection"
            HEALTH_MON[Health Monitor]
            ENV_SENSOR[Environmental Sensors]
            SOCIAL_LISTEN[Social Listening]
        end
        
        subgraph "Epidemiological Engine"
            SEIR_MODEL[SEIR Model]
            OUTBREAK_PRED[Outbreak Predictor]
            RISK_ASSESS[Risk Assessor]
        end
        
        subgraph "Alert System"
            HEALTH_ALERT[Health Alerts]
            CONTACT_TRACE[Contact Tracing]
            RESOURCE_PLAN[Resource Planning]
        end
        
        subgraph "Data Storage"
            HEALTH_DB[(Health Data)]
            DISEASE_DB[(Disease Surveillance)]
            ENVIRON_DB[(Environmental Data)]
        end
    end
    
    HEALTH_MON --> SEIR_MODEL
    ENV_SENSOR --> SEIR_MODEL
    SOCIAL_LISTEN --> OUTBREAK_PRED
    
    SEIR_MODEL --> OUTBREAK_PRED
    OUTBREAK_PRED --> RISK_ASSESS
    RISK_ASSESS --> HEALTH_ALERT
    
    HEALTH_ALERT --> CONTACT_TRACE
    CONTACT_TRACE --> RESOURCE_PLAN
    
    HEALTH_MON --> HEALTH_DB
    OUTBREAK_PRED --> DISEASE_DB
    ENV_SENSOR --> ENVIRON_DB
```

---

## 4. DATA FLOW ARCHITECTURE

### 4.1 Real-time Data Pipeline
```mermaid
graph LR
    subgraph "Sensor Layer"
        ESP32[ESP32 Sensors]
        WEATHER[Weather Stations]
        SATELLITE[Satellite Feeds]
    end
    
    subgraph "Edge Processing"
        GATEWAY[LoRaWAN Gateway]
        EDGE_AI[Edge AI Processing]
        LOCAL_CACHE[Local Cache]
    end
    
    subgraph "Stream Processing"
        KAFKA[Kafka Streams]
        PROCESSOR[Stream Processor]
        ENRICHER[Data Enricher]
    end
    
    subgraph "ML Pipeline"
        FEATURE_ENG[Feature Engineering]
        MODEL_INFER[Model Inference]
        PREDICTION[Predictions]
    end
    
    subgraph "Storage & Alerts"
        TIMESERIES[(Time Series DB)]
        ALERTS[Alert System]
        DASHBOARD[Real-time Dashboard]
    end
    
    ESP32 --> GATEWAY
    WEATHER --> GATEWAY
    SATELLITE --> EDGE_AI
    
    GATEWAY --> LOCAL_CACHE
    EDGE_AI --> LOCAL_CACHE
    LOCAL_CACHE --> KAFKA
    
    KAFKA --> PROCESSOR
    PROCESSOR --> ENRICHER
    ENRICHER --> FEATURE_ENG
    
    FEATURE_ENG --> MODEL_INFER
    MODEL_INFER --> PREDICTION
    PREDICTION --> ALERTS
    
    ENRICHER --> TIMESERIES
    ALERTS --> DASHBOARD
```

### 4.2 Batch Processing Pipeline
```mermaid
graph TB
    subgraph "Data Sources"
        HISTORICAL[Historical Data]
        EXTERNAL[External APIs]
        LOGS[System Logs]
    end
    
    subgraph "ETL Pipeline"
        EXTRACT[Data Extraction]
        TRANSFORM[Data Transformation]
        VALIDATE[Data Validation]
        LOAD[Data Loading]
    end
    
    subgraph "Analytics"
        ML_TRAINING[ML Model Training]
        PATTERN_ANALYSIS[Pattern Analysis]
        REPORTING[Report Generation]
    end
    
    subgraph "Storage"
        DATA_LAKE[(Data Lake)]
        DW[(Data Warehouse)]
        ML_MODELS[(Model Registry)]
    end
    
    HISTORICAL --> EXTRACT
    EXTERNAL --> EXTRACT
    LOGS --> EXTRACT
    
    EXTRACT --> TRANSFORM
    TRANSFORM --> VALIDATE
    VALIDATE --> LOAD
    
    LOAD --> DATA_LAKE
    DATA_LAKE --> ML_TRAINING
    ML_TRAINING --> ML_MODELS
    
    DATA_LAKE --> PATTERN_ANALYSIS
    PATTERN_ANALYSIS --> DW
    DW --> REPORTING
```

---

## 5. SECURITY ARCHITECTURE

### 5.1 Zero-Trust Security Model
```mermaid
graph TB
    subgraph "External Threats"
        CYBER_ATTACKS[Cyber Attacks]
        PHYSICAL_THREATS[Physical Threats]
        INSIDER_THREATS[Insider Threats]
    end
    
    subgraph "Defense Layers"
        subgraph "Network Security"
            FIREWALL[Next-Gen Firewall]
            IDS_IPS[IDS/IPS]
            VPN[Zero-Trust VPN]
        end
        
        subgraph "Application Security"
            WAF[Web Application Firewall]
            API_SEC[API Security Gateway]
            CONTAINER_SEC[Container Security]
        end
        
        subgraph "Data Security"
            ENCRYPTION[End-to-End Encryption]
            KEY_MGMT[Key Management]
            DATA_MASK[Data Masking]
        end
        
        subgraph "Identity & Access"
            IDENTITY[Identity Provider]
            MFA[Multi-Factor Auth]
            PAM[Privileged Access Mgmt]
        end
    end
    
    subgraph "Monitoring & Response"
        SIEM[Security Information & Event Management]
        SOAR[Security Orchestration & Response]
        THREAT_HUNT[Threat Hunting]
    end
    
    CYBER_ATTACKS --> FIREWALL
    PHYSICAL_THREATS --> IDS_IPS
    INSIDER_THREATS --> PAM
    
    FIREWALL --> WAF
    WAF --> API_SEC
    API_SEC --> ENCRYPTION
    
    IDENTITY --> MFA
    MFA --> PAM
    ENCRYPTION --> KEY_MGMT
    
    IDS_IPS --> SIEM
    CONTAINER_SEC --> SIEM
    SIEM --> SOAR
    SOAR --> THREAT_HUNT
```

### 5.2 Quantum-Resistant Security
```mermaid
graph LR
    subgraph "Classical Cryptography"
        RSA[RSA 4096]
        AES[AES-256]
        ECDSA[ECDSA P-384]
    end
    
    subgraph "Post-Quantum Cryptography"
        CRYSTALS[CRYSTALS-Kyber]
        FALCON[FALCON Signatures]
        SPHINCS[SPHINCS+ Hash]
    end
    
    subgraph "Hybrid Implementation"
        HYBRID_KEM[Hybrid Key Exchange]
        HYBRID_SIG[Hybrid Signatures]
        QUANTUM_SAFE[Quantum-Safe Protocols]
    end
    
    RSA --> HYBRID_KEM
    CRYSTALS --> HYBRID_KEM
    
    ECDSA --> HYBRID_SIG
    FALCON --> HYBRID_SIG
    
    AES --> QUANTUM_SAFE
    SPHINCS --> QUANTUM_SAFE
```

---

## 6. DEPLOYMENT ARCHITECTURE

### 6.1 Multi-Cloud Deployment
```yaml
Primary_Cloud: "AWS"
  regions:
    - "us-east-1" (N. Virginia)
    - "sa-east-1" (São Paulo)
  services:
    compute: "EKS (Kubernetes)"
    database: "RDS PostgreSQL + DocumentDB"
    storage: "S3 + EFS"
    networking: "VPC + CloudFront"
    monitoring: "CloudWatch + X-Ray"

Secondary_Cloud: "Azure"
  regions:
    - "Brazil South"
    - "East US 2"
  services:
    compute: "AKS (Kubernetes)"
    database: "Azure Database for PostgreSQL"
    storage: "Blob Storage + Azure Files"
    networking: "Virtual Network + Front Door"
    ai_ml: "Azure Machine Learning"

Edge_Computing:
  provider: "AWS IoT Greengrass"
  locations: "Regional data centers"
  capabilities:
    - "Local data processing"
    - "Offline operation"
    - "Edge AI inference"
    - "Data synchronization"

Disaster_Recovery:
  rto: "< 4 hours"
  rpo: "< 1 hour"
  strategy: "Active-Passive with automated failover"
  backup_frequency: "Continuous replication"
```

### 6.2 Kubernetes Architecture
```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sistema-guardiao
  labels:
    istio-injection: enabled
---
# kubernetes/saci-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: saci-api
  namespace: sistema-guardiao
spec:
  replicas: 3
  selector:
    matchLabels:
      app: saci-api
  template:
    metadata:
      labels:
        app: saci-api
        version: v1
    spec:
      containers:
      - name: saci-api
        image: sistema-guardiao/saci-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 7. PERFORMANCE & SCALING

### 7.1 Performance Requirements
```yaml
Response_Times:
  api_endpoints: "< 200ms (95th percentile)"
  dashboard_load: "< 2 seconds"
  alert_generation: "< 30 seconds"
  ml_inference: "< 100ms"

Throughput:
  sensor_data_ingestion: "100,000 messages/minute"
  concurrent_users: "10,000 simultaneous"
  api_requests: "50,000 requests/minute"
  database_queries: "100,000 IOPS"

Availability:
  system_uptime: "99.9% (8.76 hours downtime/year)"
  planned_maintenance: "< 2 hours/month"
  disaster_recovery: "< 4 hours RTO"
  data_backup: "< 1 hour RPO"

Scalability:
  horizontal_scaling: "Auto-scaling based on metrics"
  geographic_expansion: "Multi-region deployment"
  sensor_network: "Support 1M+ sensor nodes"
  data_retention: "5 years hot, 10 years cold"
```

### 7.2 Auto-Scaling Configuration
```mermaid
graph TB
    subgraph "Monitoring"
        PROMETHEUS[Prometheus Metrics]
        GRAFANA[Grafana Alerts]
        CUSTOM_METRICS[Custom App Metrics]
    end
    
    subgraph "Auto-Scaling Decision"
        HPA[Horizontal Pod Autoscaler]
        VPA[Vertical Pod Autoscaler]
        CLUSTER_AUTO[Cluster Autoscaler]
    end
    
    subgraph "Scaling Actions"
        POD_SCALE[Pod Scaling]
        NODE_SCALE[Node Scaling]
        STORAGE_SCALE[Storage Scaling]
    end
    
    PROMETHEUS --> HPA
    GRAFANA --> CLUSTER_AUTO
    CUSTOM_METRICS --> VPA
    
    HPA --> POD_SCALE
    VPA --> POD_SCALE
    CLUSTER_AUTO --> NODE_SCALE
    
    POD_SCALE --> STORAGE_SCALE
```

---

This comprehensive architecture specification provides the complete technical foundation for implementing the Sistema Guardião, ensuring scalability, security, and maintainability while supporting all five subsystems in an integrated manner.
