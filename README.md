# Sistema Guardião: Plataforma Nacional Integrada de Prevenção e Resposta a Eventos Extremos

**Status:** Em Desenvolvimento (Global Solution FIAP 2025.1 - Sprint de 10 Dias)  
**Repositório:** [https://github.com/YanCotta/global_solution_1_fiap](https://github.com/YanCotta/global_solution_1_fiap)  
**Equipe:** Yan Cotta  

---

## 📋 Documentação Principal

**🎯 Para acessar a documentação completa e consolidada, consulte:**

### **[MASTER_DOCUMENTATION.md](./MASTER_DOCUMENTATION.md)**

Este documento contém:

- ✅ Arquitetura técnica completa
- ✅ Modelo de dados unificado
- ✅ Especificações de todos os 5 subsistemas
- ✅ Framework de IA Agêntica
- ✅ Modelo de negócio e viabilidade
- ✅ Roadmap de implementação

**🏗️ Para visualizar os diagramas C4 interativos:**

### **[C4 Architecture Diagrams](./sistema_guardiao_c4_diagrams.html)**

**📄 Especificações Detalhadas na pasta `/docs`:**

- **[Modelo de Dados](./docs/DATA_MODELS.md)**: Esquemas de banco de dados detalhados.
- **[Especificação da Arquitetura](./docs/ARCHITECTURE_SPECIFICATION.md)**: Detalhes da arquitetura técnica.
- **[Especificação do MVP SACI](./docs/SACI_MVP_SPECIFICATION.md)**: Especificação detalhada do MVP do SACI.
- **[Fluxos de Dados](./docs/DATA_FLOWS.md)**: Detalhamento dos fluxos de dados entre subsistemas.
- **[Matriz de Dependências Tecnológicas](./docs/TECH_DEPENDENCIES.md)**: Matriz explícita das tecnologias e suas interdependências.
- **[Especificação da API](./docs/API_SPECIFICATION.md)**: Detalhamento dos endpoints e estrutura da API.
- **[Protocolos de Comunicação IoT](./docs/IOT_PROTOCOLS.md)**: Especificação dos protocolos IoT utilizados.

---

## 🛡️ Visão Geral Rápida

O **Sistema Guardião** é uma arquitetura nacional brasileira que combina 5 subsistemas especializados para criar uma rede de proteção abrangente contra eventos extremos. Utilizando princípios de **inteligência artificial agêntica** e inspiração no folclore brasileiro.

### Os Cinco Guardiões Digitais

1.  **🦶 CURUPIRA** - Proteção Cibernética de Infraestruturas Críticas
2.  **🏥 IARA** - Vigilância Epidemiológica Inteligente
3.  **🔥 SACI** - Prevenção de Incêndios com Inteligência de Enxame
4.  **⚡ BOITATÁ** - Resiliência de Sistemas Urbanos Interdependentes
5.  **📡 ANHANGÁ** - Comunicações de Emergência Resilientes

### Arquitetura Multi-Camadas

```mermaid
┌─────────────────────────────────────────────────────────┐
│           COORDENAÇÃO AGÊNTICA CENTRAL                  │
│        (GuardianCentralOrchestrator + CrewAI)           │
├─────────────────────────────────────────────────────────┤
│              SUBSISTEMAS ESPECIALIZADOS                 │
│     CURUPIRA │ IARA │ SACI │ BOITATÁ │ ANHANGÁ        │
├─────────────────────────────────────────────────────────┤
│            CONECTIVIDADE AVANÇADA                       │
│    (5G/6G, LoRaWAN, Mesh Networks, Satélite)          │
├─────────────────────────────────────────────────────────┤
│           SENSORIAMENTO DISTRIBUÍDO                     │
│         (IoT Edge + AI Distribuída)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 MVP Focus: SACI Fire Prevention

**Objetivo do MVP:** Demonstrar capacidades completas do subsistema SACI com hardware ESP32 + sensores + modelo ML para predição de risco de incêndio.

**Componentes do MVP:**

- ESP32 com sensores de temperatura, umidade e fumaça
- Modelo de Machine Learning para predição de risco
- Dashboard em tempo real
- Coordenação com outros subsistemas (simulado)

---

## 📊 Tech Stack Principal

**Backend & IA:**

- Python 3.11+ (FastAPI, PyTorch, CrewAI)
- PostgreSQL + Neo4j + InfluxDB
- Apache Kafka + Redis

**Edge Computing:**

- ESP32-S3 (MicroPython/C++)
- LoRa E32 (Comunicação longo alcance)

**Frontend:**

- React + TypeScript
- D3.js (Visualizações especializadas)

---

## 📈 Roadmap 10 Dias (Resumido)

### ✅ Dias 1-2: Fundação Arquitetural

- [x] Documentação técnica consolidada
- [x] Diagramas C4 completos
- [x] Modelo de dados unificado

### 🔄 Dias 3-4: Protótipos Core

- [ ] Detectores híbridos funcionais
- [ ] Firmware ESP32 multi-sensor
- [ ] Modelos ML básicos

### 🔄 Dias 5-6: Integração

- [ ] Dashboard unificado
- [ ] API Gateway central
- [ ] Testes de comunicação

### 🔄 Dias 7-8: IA e Analytics

- [ ] Pipeline ML end-to-end
- [ ] Sistema de alertas inteligentes
- [ ] Métricas de performance

### 🔄 Dias 9-10: Finalização

- [ ] Vídeo demonstrativo
- [ ] Documentação final
- [ ] Preparação para entrega

---

## 🏛️ Estado Piloto: Minas Gerais

**Justificativa:**

- Diversidade geográfica (cerrado, mata atlântica, urbano)
- Histórico de eventos extremos (Brumadinho, secas, incêndios)
- Hub tecnológico (Belo Horizonte)
- Parcerias acadêmicas (UFMG, PUC Minas)

---

## 🎯 Valores Únicos de Proposta

- **Inteligência Preventiva:** Alerta 72h antes de 85% dos eventos críticos
- **Coordenação Emergente:** IA agêntica sem ponto único de falha
- **Integração Cultural:** Folclore brasileiro para confiança pública
- **Escalabilidade Nacional:** Arquitetura para 200M+ cidadãos

---

## 📚 Estrutura do Repositório

```text
📁 global_solution_1_fiap/
├── 📄 README.md (este arquivo)
├── 📄 MASTER_DOCUMENTATION.md (documentação principal)
├── 📄 sistema_guardiao_c4_diagrams.html (diagramas C4)
├── 📁 src/ (código do MVP)
├── 📁 docs/ (documentação adicional)
├── 📁 hardware/ (firmware ESP32)
└── 📁 assets/ (imagens, diagramas, vídeos)
```

---

> "Assim como as lendas brasileiras protegiam nossas terras, o Sistema Guardião protegerá nosso futuro."

---

## 🤝 Como Contribuir

1.  **Clone o repositório**
2.  **Revise a [documentação principal](./MASTER_DOCUMENTATION.md)**
3.  **Explore os [diagramas C4](./sistema_guardiao_c4_diagrams.html)**
4.  **Acompanhe o progresso via Issues e Projects**

### **Global Solution FIAP 2025.1 - Desenvolvido por Yan Cotta**

- **IA/ML:** PyTorch, Scikit-learn, HuggingFace Transformers, TensorFlow Lite, Pandas, NumPy.
- **Bancos de Dados:** PostgreSQL + TimescaleDB (relacional e séries temporais), Neo4j (grafos), InfluxDB (métricas IoT), Redis (cache).
- **Infraestrutura & Mensageria:** Kubernetes, Docker, Apache Kafka, RabbitMQ.
- **IoT & Edge:** ESP32 (com MicroPython/C++), Raspberry Pi, LoRaWAN, MQTT.
- **Frontend (Conceitual):** React, D3.js.
- **API:** FastAPI.

---

## 📁 Estrutura Técnica Detalhada

```text
📁 global_solution_1_fiap/
├── 📄 README.md                           # Documentação principal (este arquivo)
├── 📄 MASTER_DOCUMENTATION.md             # Especificações técnicas completas
├── 📄 sistema_guardiao_c4_diagrams.html   # Diagramas C4 interativos
├── 📄 10_day_implementation_plan.md       # Roadmap detalhado
├── 📁 src/
│   └── 📁 saci_mvp/                      # MVP do SACI (código implementado)
│       ├── 📄 README.md                  # Documentação específica do MVP
│       ├── 📁 esp32_firmware/            # Firmware para sensores
│       ├── 📁 ml_model/                  # Modelos de Machine Learning
│       ├── 📁 api/                       # API FastAPI
│       └── 📁 dashboard/                 # Interface React
├── 📁 docs/                              # Documentação adicional
│   ├── 📄 DATA_MODELS.md                # Esquemas de banco de dados
│   ├── 📄 SACI_MVP_SPECIFICATION.md     # Especificação detalhada do MVP
│   ├── 📄 ARCHITECTURE_SPECIFICATION.md # Arquitetura técnica
│   ├── 📄 DATA_FLOWS.md                # Fluxos de dados entre subsistemas
│   ├── 📄 TECH_DEPENDENCIES.md         # Matriz de dependências tecnológicas
│   ├── 📄 API_SPECIFICATION.md          # Especificação da API
│   └── 📄 IOT_PROTOCOLS.md             # Protocolos de comunicação IoT
├── 📁 hardware/                          # Configurações de hardware
├── 📁 .github/workflows/                 # CI/CD Pipeline
├── 📄 requirements.txt                   # Dependências Python
├── 📄 docker-compose.yml                 # Orquestração de containers
└── 📄 LICENSE                           # Licença MIT
```

---

## 💫 Inspiração Cultural

> "Assim como as lendas brasileiras protegiam nossas terras, o Sistema Guardião protegerá nosso futuro."
