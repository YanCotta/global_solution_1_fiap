# Matriz de Dependências Tecnológicas - Sistema Guardião

Este documento descreve as principais tecnologias utilizadas no Sistema Guardião e suas dependências entre os componentes e subsistemas.

## Legenda de Subsistemas

- **OAC:** Orquestrador Agêntico Central
- **CUR:** CURUPIRA (Segurança Ciberfísica)
- **IAR:** IARA (Vigilância Epidemiológica)
- **SAC:** SACI (Prevenção de Incêndios)
- **BOI:** BOITATÁ (Resiliência Urbana)
- **ANH:** ANHANGÁ (Comunicações de Emergência)
- **IoT:** Componentes de Internet das Coisas (ex: Sensores ESP32 do SACI)
- **FE:** Frontend (Dashboard Unificado, Aplicações Móveis)
- **API:** API Gateway Central

## Matriz de Dependências

| Tecnologia Principal        | OAC | CUR | IAR | SAC | BOI | ANH | IoT | FE  | API | Notas                                                                 |
|-----------------------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----------------------------------------------------------------------|
| **Linguagens de Programação** |     |     |     |     |     |     |     |     |     |                                                                       |
| Python 3.11+                | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     |     | ✅  | Linguagem principal para backend, IA/ML, scripts.                     |
| MicroPython/C++ (ESP32)     |     |     |     | ✅  |     |     | ✅  |     |     | Firmware para dispositivos IoT (SACI MVP).                            |
| Go                            |     |     |     |     | ✅  |     |     |     |     | Potencial para BOITATÁ (alto desempenho em redes).                    |
| Java (Spring Boot)          |     |     |     |     |     |     |     |     |     | Considerado para MULA (Logística), pode ser usado em outros módulos.  |
| TypeScript                  |     |     |     |     |     |     |     | ✅  |     | Para desenvolvimento Frontend com React.                              |
| **Frameworks Backend & IA**   |     |     |     |     |     |     |     |     |     |                                                                       |
| FastAPI                     | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     |     | ✅  | Framework principal para APIs Python.                                 |
| CrewAI                      | ✅  |     |     |     |     |     |     |     |     | Para orquestração de agentes de IA no OAC.                          |
| LangGraph                   | ✅  |     |     |     |     |     |     |     |     | Para construir aplicações LLM stateful e com agentes no OAC.        |
| PyTorch                     | ✅  | ✅  | ✅  | ✅  | ✅  |     |     |     |     | Framework de Deep Learning para modelos nos subsistemas e OAC.        |
| TensorFlow (Lite)           |     | ✅  |     | ✅  |     |     | ✅  |     |     | Para modelos ML em CURUPIRA e no Edge (ESP32 - TFLite).             |
| Scikit-learn                | ✅  | ✅  | ✅  | ✅  | ✅  |     |     |     |     | Para modelos de Machine Learning clássicos.                           |
| Pandas, NumPy               | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     |     |     | Manipulação e análise de dados.                                     |
| **Bancos de Dados**           |     |     |     |     |     |     |     |     |     |                                                                       |
| PostgreSQL (TimescaleDB)    | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     |     | ✅  | BD Relacional principal, com TimescaleDB para séries temporais.       |
| Neo4j                       | ✅  |     |     |     | ✅  |     |     |     |     | BD de Grafos para BOITATÁ (dependências urbanas) e OAC (relações). |
| InfluxDB                    |     | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     |     | BD Time Series para métricas IoT e dados de sensores.                 |
| Redis                       | ✅  |     |     |     |     |     |     | ✅  | ✅  | Cache de alta performance, message broker auxiliar.                   |
| Pinecone/VectorDB           | ✅  |     |     |     |     |     |     |     |     | Para RAG e busca semântica no OAC.                                  |
| **Mensageria & Streaming**  |     |     |     |     |     |     |     |     |     |                                                                       |
| Apache Kafka                | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     | ✅  | Plataforma de streaming de eventos principal.                         |
| MQTT                        |     |     |     | ✅  |     |     | ✅  |     |     | Protocolo para comunicação IoT (sensores para Kafka).                 |
| RabbitMQ                    |     |     |     |     |     |     |     |     |     | Alternativa/Complemento a Kafka para cenários específicos.            |
| **Frontend**                |     |     |     |     |     |     |     |     |     |                                                                       |
| React                       |     |     |     |     |     |     |     | ✅  |     | Biblioteca para UI do Dashboard.                                      |
| D3.js                       |     |     |     |     |     |     |     | ✅  |     | Para visualizações de dados complexas.                                |
| **Infraestrutura & DevOps** |     |     |     |     |     |     |     |     |     |                                                                       |
| Docker                      | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     | ✅  | ✅  | Conteinerização de todas as aplicações e serviços.                  |
| Docker Compose              | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     | ✅  | ✅  | Orquestração local e para MVP.                                      |
| Kubernetes                  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |     | ✅  | ✅  | Orquestração em produção (conceitual para o MVP).                   |
| GitHub Actions              | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | CI/CD Pipeline.                                                       |
| **Comunicação IoT**         |     |     |     |     |     |     |     |     |     |                                                                       |
| LoRaWAN/LoRa E32            |     |     |     | ✅  |     | ✅  | ✅  |     |     | Comunicação de longo alcance e baixo consumo para IoT e ANHANGÁ.    |
| WiFi/Ethernet (ESP32)       |     |     |     | ✅  |     |     | ✅  |     |     | Conectividade local para ESP32.                                     |
| Mesh Networks (genérica)    |     |     |     |     |     | ✅  |     |     |     | Conceito para ANHANGÁ.                                                |
| **Segurança**               |     |     |     |     |     |     |     |     |     |                                                                       |
| OAuth2/OIDC                 | ✅  |     |     |     |     |     |     | ✅  | ✅  | Autenticação e Autorização.                                         |
| TLS/SSL                     | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | Criptografia em trânsito.                                           |
| Quantum-Resistant Crypto    | ✅  | ✅  |     |     |     | ✅  |     |     |     | Consideração para segurança de longo prazo (C4).                    |

## Notas Adicionais

- A coluna **IoT** refere-se especificamente aos dispositivos de ponta, como os sensores ESP32.
- A coluna **API** refere-se ao API Gateway central, que interage com a maioria das tecnologias de backend.
- **FE** (Frontend) depende das APIs para obter dados e interagir com o backend.
- O **OAC** (Orquestrador Agêntico Central) é o cérebro do sistema, integrando informações e coordenando ações através de múltiplos subsistemas e, portanto, tem dependências amplas.
- As dependências podem evoluir à medida que o projeto avança e novas funcionalidades são adicionadas ou refinadas.
- Para o MVP, o foco é em Python, FastAPI, PostgreSQL/TimescaleDB, InfluxDB, Docker, MQTT, e o stack de frontend para o dashboard do SACI. As demais são para a visão completa do sistema.

Este documento serve como um guia para entender as interconexões tecnológicas dentro do Sistema Guardião e auxiliar no planejamento de desenvolvimento e integração.
