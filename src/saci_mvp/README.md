# SACI MVP - Sistema de Prevenção de Incêndios
## Sistema Inteligente de Detecção Precoce de Incêndios

[![CI/CD Pipeline](https://github.com/usuario/sistema-guardiao/workflows/CI/badge.svg)](https://github.com/usuario/sistema-guardiao/actions)
[![Coverage](https://codecov.io/gh/usuario/sistema-guardiao/branch/main/graph/badge.svg)](https://codecov.io/gh/usuario/sistema-guardiao)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🔥 VISÃO GERAL

O **SACI MVP** é um sistema de detecção precoce de incêndios que combina sensores IoT distribuídos, inteligência artificial e algoritmos de enxame para prevenir e responder rapidamente a riscos de incêndio. Este é o Produto Mínimo Viável (MVP) do subsistema SACI do Sistema Guardião.

### ✨ Características Principais

- 🌡️ **Sensoriamento Multi-dimensional**: Temperatura, umidade, fumaça, CO₂, vento, umidade do solo
- 🤖 **Inteligência Artificial**: Modelos de ML para predição de risco de incêndio
- 🐝 **Inteligência de Enxame**: Coordenação distribuída entre sensores
- ⚡ **Alertas em Tempo Real**: Detecção e notificação em segundos
- 📱 **Dashboard Intuitivo**: Monitoramento visual em tempo real
- 🔋 **Eficiência Energética**: Operação prolongada com energia solar

---

## 🚀 INSTALAÇÃO RÁPIDA

### Pré-requisitos
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+
- InfluxDB 2.0+

### Instalação com Docker (Recomendado)
```bash
# Clone o repositório
git clone https://github.com/usuario/sistema-guardiao.git
cd sistema-guardiao

# Inicie os serviços
docker-compose up -d

# Aguarde todos os serviços ficarem saudáveis
docker-compose ps

# Acesse o dashboard
open http://localhost:3000
```

### Instalação Manual
```bash
# Clone e configure o ambiente
git clone https://github.com/usuario/sistema-guardiao.git
cd sistema-guardiao

# Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
export DATABASE_URL="postgresql://user:password@localhost:5432/saci_db"
alembic upgrade head

# Execute o servidor
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔧 CONFIGURAÇÃO

### Variáveis de Ambiente
```bash
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/saci_db
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influx-token
REDIS_URL=redis://localhost:6379

# Machine Learning
ML_MODEL_PATH=./models/saci_fire_risk_model.pkl
PREDICTION_THRESHOLD=0.7

# Comunicação IoT
MQTT_BROKER=localhost
MQTT_PORT=1883
LORAWAN_GATEWAY_EUI=AA555A0000000000

# Alertas
ALERT_EMAIL_SMTP=smtp.gmail.com
ALERT_EMAIL_PORT=587
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook

# Monitoramento
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### Configuração dos Sensores ESP32
```cpp
// Configuração no firmware ESP32
#define DEVICE_ID "SACI_001"
#define LATITUDE -19.9167
#define LONGITUDE -43.9345
#define TRANSMISSION_INTERVAL 300  // 5 minutos
#define LORA_FREQUENCY 915E6       // 915 MHz Brasil

// Configuração LoRaWAN
#define APPEUI "0000000000000000"
#define DEVEUI "AA555A0000000001"
#define APPKEY "2B7E151628AED2A6ABF7158809CF4F3C"
```

---

## 📡 HARDWARE - ESP32 SENSOR NODE

### Componentes Necessários
| Componente | Modelo | Função | Preço Estimado |
|------------|--------|--------|----------------|
| Microcontrolador | ESP32-WROOM-32 | Processamento principal | R$ 35 |
| Sensor Temp/Umidade | DHT22 | Temperatura e umidade | R$ 25 |
| Sensor de Fumaça | MQ-2 | Detecção de gases combustíveis | R$ 15 |
| Sensor CO₂ | MH-Z19B | Concentração de CO₂ | R$ 85 |
| Sensor de Luz | BH1750 | Intensidade luminosa | R$ 12 |
| Sensor Umidade Solo | YL-69 | Umidade do solo | R$ 8 |
| Sensor Pressão | BMP280 | Pressão atmosférica | R$ 18 |
| Módulo LoRa | RFM95W | Comunicação longa distância | R$ 45 |
| Painel Solar | 6V 2W | Alimentação sustentável | R$ 35 |
| Bateria | LiPo 3.7V 5000mAh | Armazenamento energia | R$ 55 |
| Gabinete | IP65 ABS | Proteção intempéries | R$ 25 |
| **Total por nó** | | | **R$ 358** |

### Esquema de Ligação
```
ESP32 GPIO Connections:
├── DHT22 → GPIO 4 (Temperatura/Umidade)
├── MQ-2 → GPIO A0 (Fumaça)
├── MH-Z19B → GPIO 16,17 (CO₂ UART)
├── BH1750 → GPIO 21,22 (I2C)
├── YL-69 → GPIO A1 (Umidade Solo)
├── BMP280 → GPIO 21,22 (I2C)
├── RFM95W → GPIO 18,19,23,5 (SPI)
└── Battery Monitor → GPIO A3
```

### Firmware ESP32
```cpp
#include "SACIFireSensor.h"

SACIFireSensor sensor;

void setup() {
    Serial.begin(115200);
    sensor.initialize();
    Serial.println("SACI Fire Sensor v1.0 - Online");
}

void loop() {
    SensorReading reading = sensor.collectData();
    float fireRisk = sensor.calculateRisk(reading);
    
    if (sensor.transmitData(reading, fireRisk)) {
        Serial.println("Data transmitted successfully");
    }
    
    sensor.enterSleepMode(300); // 5 minutes
}
```

---

## 🧠 MACHINE LEARNING

### Modelo de Predição de Risco
O sistema utiliza um modelo ensemble combinando Random Forest e Gradient Boosting para predizer o risco de incêndio baseado em múltiplas variáveis ambientais.

#### Características do Modelo
- **Entrada**: 12 features ambientais e temporais
- **Saída**: Score de risco (0-1) + confiança
- **Acurácia**: >85% em dados de teste
- **Latência**: <100ms por predição

#### Features Utilizadas
```python
features = [
    'temperature',      # Temperatura (°C)
    'humidity',         # Umidade relativa (%)
    'smoke_level',      # Densidade de fumaça (PPM)
    'co2_level',        # Concentração CO₂ (PPM)
    'light_intensity',  # Intensidade luz (Lux)
    'soil_moisture',    # Umidade solo (%)
    'wind_speed',       # Velocidade vento (m/s)
    'pressure',         # Pressão atmosférica (hPa)
    'heat_index',       # Índice de calor calculado
    'day_of_year',      # Dia do ano (sazonalidade)
    'hour_of_day',      # Hora do dia
    'days_since_rain'   # Dias desde última chuva
]
```

#### Treinamento do Modelo
```bash
# Treinar novo modelo
python src/ml/train_model.py

# Avaliar performance
python src/ml/evaluate_model.py

# Deploy do modelo
python src/ml/deploy_model.py
```

---

## 📊 API ENDPOINTS

### Sensor Data API
```http
POST /api/v1/sensors/data
Content-Type: application/json

{
    "device_id": "SACI_001",
    "timestamp": "2024-01-15T10:30:00Z",
    "location": {"lat": -19.9167, "lon": -43.9345},
    "sensors": {
        "temperature": 28.5,
        "humidity": 45.0,
        "smoke": 150,
        "co2": 420,
        "light": 25000,
        "moisture": 30.0,
        "wind_speed": 5.2,
        "wind_direction": 180,
        "pressure": 1013.2
    },
    "battery_level": 85.5
}
```

### Fire Risk Prediction API
```http
GET /api/v1/predictions/fire-risk?device_id=SACI_001

Response:
{
    "device_id": "SACI_001",
    "risk_score": 0.73,
    "risk_category": "High",
    "confidence": 0.89,
    "factors": {
        "high_temperature": {"contribution": 0.3},
        "low_humidity": {"contribution": 0.25},
        "smoke_detected": {"contribution": 0.4}
    },
    "alert_level": 3,
    "timestamp": "2024-01-15T10:31:00Z"
}
```

### Real-time Alerts API
```http
GET /api/v1/alerts/stream
Content-Type: text/event-stream

data: {"type": "fire_risk", "level": 3, "device_id": "SACI_001", "message": "High fire risk detected"}

data: {"type": "sensor_offline", "device_id": "SACI_003", "message": "Sensor offline for 10 minutes"}
```

---

## 🎯 MONITORAMENTO E DASHBOARD

### Métricas Principais
- **Cobertura da Rede**: % de área monitorada
- **Health dos Sensores**: Status operacional em tempo real
- **Predições de Risco**: Mapa de calor de risco de incêndio
- **Alertas Ativos**: Lista de alertas não resolvidos
- **Performance do Sistema**: Latência, throughput, disponibilidade

### Dashboard URLs
- **Principal**: http://localhost:3000
- **Administração**: http://localhost:3000/admin
- **Métricas**: http://localhost:3000/metrics
- **API Docs**: http://localhost:8000/docs

### Grafana Dashboards
```bash
# Importar dashboards pré-configurados
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/saci-overview.json

curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/sensor-health.json
```

---

## 🧪 TESTES

### Executar Testes
```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_sensor_data.py -v
pytest tests/test_ml_model.py -v
pytest tests/test_api.py -v

# Testes com cobertura
pytest tests/ --cov=src/ --cov-report=html

# Testes de performance
pytest tests/test_performance.py --benchmark-only
```

### Teste de Hardware
```bash
# Simular dados de sensor
python scripts/simulate_sensor_data.py --devices 10 --duration 3600

# Teste de conectividade LoRaWAN
python scripts/test_lorawan.py --gateway-ip 192.168.1.100

# Validação do modelo ML
python scripts/validate_ml_model.py --test-data datasets/test_fire_incidents.csv
```

---

## 🚀 DEPLOYMENT

### Produção com Kubernetes
```bash
# Deploy no cluster Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verificar status
kubectl get pods -n sistema-guardiao
kubectl logs -f deployment/saci-api -n sistema-guardiao
```

### CI/CD Pipeline
O sistema utiliza GitHub Actions para automação:
- ✅ Testes automatizados
- 🔍 Análise de código
- 🐳 Build de containers
- 🚀 Deploy automático
- 📊 Relatórios de cobertura

---

## 📈 PERFORMANCE E ESCALABILIDADE

### Benchmarks MVP
- **Throughput**: 1,000 mensagens de sensor/minuto
- **Latência API**: <200ms (95th percentile)
- **Predição ML**: <100ms por inferência
- **Uptime**: >99.5% disponibilidade
- **Capacidade**: Suporte a 50 sensores simultâneos

### Escalabilidade
- **Horizontal**: Auto-scaling baseado em métricas
- **Vertical**: Ajuste automático de recursos
- **Geográfica**: Preparado para múltiplas regiões
- **Temporal**: Particionamento de dados por período

---

## 🤝 CONTRIBUINDO

### Como Contribuir
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Padrões de Código
- **Python**: Seguir PEP 8 + Black formatter
- **C++**: Seguir Google C++ Style Guide
- **Commit**: Conventional Commits
- **Documentação**: Markdown + docstrings

### Testes Obrigatórios
- Cobertura mínima: 80%
- Testes unitários para toda lógica de negócio
- Testes de integração para APIs
- Testes de hardware para ESP32

---

## 📋 ROADMAP

### Versão 1.0 (MVP) - ✅ Concluído
- [x] Sensores ESP32 funcionais
- [x] Modelo ML básico
- [x] API REST completa
- [x] Dashboard web
- [x] Sistema de alertas

### Versão 1.1 - 🔄 Em Progresso
- [ ] Otimização do modelo ML
- [ ] Interface mobile
- [ ] Integração com serviços de emergência
- [ ] Análise preditiva avançada

### Versão 2.0 - 📅 Planejado
- [ ] Inteligência de enxame completa
- [ ] Detecção por satélite
- [ ] Integração com drones
- [ ] Sistema de prevenção ativo

---

## 📞 SUPORTE

### Documentação
- 📖 [Documentação Completa](docs/README.md)
- 🏗️ [Guia de Arquitetura](docs/ARCHITECTURE.md)
- 🔧 [Manual de Hardware](docs/HARDWARE.md)
- 🤖 [Guia de ML](docs/ML_GUIDE.md)

### Comunidade
- 💬 [Discussions](https://github.com/usuario/sistema-guardiao/discussions)
- 🐛 [Issues](https://github.com/usuario/sistema-guardiao/issues)
- 📧 Email: saci-support@sistema-guardiao.com
- 📱 Slack: [#sistema-guardiao](https://workspace.slack.com/channels/sistema-guardiao)

### Status do Sistema
- 📊 [Status Page](https://status.sistema-guardiao.com)
- 🔍 [Metrics Dashboard](https://metrics.sistema-guardiao.com)
- 📈 [Performance Monitor](https://performance.sistema-guardiao.com)

---

## 📄 LICENÇA

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏆 RECONHECIMENTOS

- **FIAP**: Pela oportunidade de desenvolvimento
- **ESP32 Community**: Pela excelente documentação
- **scikit-learn**: Pela robusta biblioteca de ML
- **LoRaWAN Alliance**: Pelos protocolos de comunicação
- **Open Source Community**: Por todas as ferramentas utilizadas

---

## 📊 ESTATÍSTICAS DO PROJETO

![GitHub repo size](https://img.shields.io/github/repo-size/usuario/sistema-guardiao)
![GitHub contributors](https://img.shields.io/github/contributors/usuario/sistema-guardiao)
![GitHub stars](https://img.shields.io/github/stars/usuario/sistema-guardiao?style=social)
![GitHub forks](https://img.shields.io/github/forks/usuario/sistema-guardiao?style=social)

---

**Sistema Guardião - Protegendo o futuro com inteligência artificial** 🛡️🔥
