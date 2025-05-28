# Fluxos de Dados Entre Subsistemas - Sistema Guardião

Este documento detalha os principais fluxos de dados entre os cinco subsistemas do Sistema Guardião: CURUPIRA, IARA, SACI, BOITATÁ e ANHANGÁ, coordenados pelo Orquestrador Agêntico Central.

## Diagrama de Fluxo de Alto Nível (Conceitual)

```mermaid
graph LR
    subgraph Cidadãos & Agências Externas
        direction LR
        CIT[👥 Cidadãos]
        GOV[🏛️ Agências Governamentais]
        EMR[🚨 Serviços de Emergência]
        UTL[⚡ Utilities]
        INT[🌎 Sistemas Internacionais]
    end

    subgraph Sistema Guardião Central
        direction LR
        ORCH[🎯 Orquestrador Agêntico Central]
    end

    subgraph Subsistemas Guardiões
        direction TB
        CURUPIRA[🦶 CURUPIRA]
        IARA[🏥 IARA]
        SACI[🔥 SACI]
        BOITATA[⚡ BOITATÁ]
        ANHANGA[📡 ANHANGÁ]
    end

    subgraph Bases de Dados Comuns
        direction LR
        TSDB[📊 TimeSeries DB (InfluxDB)]
        GDB[🕸️ Graph DB (Neo4j)]
        VDB[🧠 Vector DB (Pinecone)]
        RDB[🗃️ Relational DB (PostgreSQL)]
        MBUS[📨 Message Bus (Kafka)]
    end

    %% Conexões Externas ao Orquestrador
    CIT -->|Alertas, Dados Saúde, Localização| ORCH
    GOV -->|Diretivas, Autorizações| ORCH
    EMR -->|Status Campo, Capacidades| ORCH
    UTL -->|Status Infra, Capacidade| ORCH
    INT -->|Inteligência Global, Alertas| ORCH

    ORCH -->|Alertas, Instruções, Coordenação Recursos| CIT
    ORCH -->|Inteligência, Recomendações, Status| GOV
    ORCH -->|Coordenação, Inteligência Tática| EMR
    ORCH -->|Alertas Proteção, Priorização| UTL
    ORCH -->|Status Regional, Cooperação| INT

    %% Orquestrador para Message Bus
    ORCH --> MBUS

    %% Message Bus para Subsistemas
    MBUS --> CURUPIRA
    MBUS --> IARA
    MBUS --> SACI
    MBUS --> BOITATA
    MBUS --> ANHANGA

    %% Subsistemas para Message Bus (para outros subsistemas ou Orquestrador)
    CURUPIRA --> MBUS
    IARA --> MBUS
    SACI --> MBUS
    BOITATA --> MBUS
    ANHANGA --> MBUS

    %% Subsistemas para Bases de Dados
    CURUPIRA -->|Dados de Segurança, Logs| TSDB
    CURUPIRA -->|Metadados, Políticas| RDB
    SACI -->|Dados Sensores Incêndio, Alertas| TSDB
    SACI -->|Modelos Risco, Mapas Vegetação| RDB
    IARA -->|Dados Epidemiológicos, Sintomas| TSDB
    IARA -->|Modelos Preditivos, Histórico Saúde| RDB
    BOITATA -->|Status Infraestrutura Crítica, Dependências| GDB
    BOITATA -->|Dados Sensores Urbanos, Simulações| TSDB
    BOITATA -->|Configurações, Planos Mitigação| RDB
    ANHANGA -->|Status Rede Mesh, Qualidade Sinal| TSDB
    ANHANGA -->|Configurações Rede, Prioridades| RDB

    %% Orquestrador para Bases de Dados (para contexto e aprendizado)
    ORCH --> VDB
    ORCH --> RDB

    %% Interações diretas (conceituais, primariamente via Orquestrador/MessageBus)
    CURUPIRA -.->|Inteligência Cibernética| BOITATA
    BOITATA -.->|Status de Infraestrutura para Riscos| SACI
    SACI -.->|Necessidade de Comunicação Emergencial| ANHANGA
    IARA -.->|Alertas de Saúde para Agências| GOV
```

## Detalhamento dos Fluxos por Subsistema

### 1. 🎯 Orquestrador Agêntico Central (OAC)
- **Recebe de:**
    - **Cidadãos:** Relatos de emergência, dados de saúde (consentidos), localização.
    - **Agências Governamentais:** Diretivas políticas, autorização de recursos, pedidos de coordenação.
    - **Serviços de Emergência:** Capacidades de resposta, relatórios de campo, status de recursos.
    - **Utilities:** Status de infraestrutura (energia, água, comms), dados de capacidade, agendamentos de manutenção.
    - **Sistemas Internacionais:** Inteligência de ameaças globais, melhores práticas, ofertas de ajuda.
    - **Subsistemas (via Message Bus):** Alertas processados, inteligência local, pedidos de coordenação inter-subsistema, status.
- **Envia para:**
    - **Cidadãos:** Alertas e avisos, instruções de segurança, coordenação de recursos.
    - **Agências Governamentais:** Inteligência de ameaças, recomendações de resposta, relatórios de status.
    - **Serviços de Emergência:** Coordenação de emergências, envio de recursos, inteligência tática.
    - **Utilities:** Alertas de proteção, balanceamento de carga, roteamento prioritário.
    - **Sistemas Internacionais:** Status regional, pedidos de cooperação, inteligência compartilhada.
    - **Message Bus (Kafka):** Tarefas para subsistemas, pedidos de dados, diretivas de ação.
- **Interage com Bases de Dados:**
    - **PostgreSQL:** Dados operacionais, configuração de usuários, políticas.
    - **VectorDB (Pinecone):** Contexto para LLMs, busca semântica para RAG.

### 2. 🦶 CURUPIRA (Segurança Ciberfísica)
- **Recebe de (via Message Bus/OAC):**
    - **OAC:** Diretivas de monitoramento, pedidos de análise de ameaças.
    - **BOITATÁ:** Alertas sobre vulnerabilidades físicas em infraestruturas críticas que podem ter componentes cibernéticos.
    - **Fontes Externas (via OAC/Threat Intel Hub):** Feeds de inteligência de ameaças.
- **Envia para (via Message Bus/OAC):**
    - **OAC:** Alertas de ameaças ciberfísicas, relatórios de vulnerabilidade, recomendações de contramedidas.
    - **BOITATÁ:** Inteligência sobre ameaças cibernéticas a sistemas de controle industrial (ICS/SCADA).
- **Interage com Bases de Dados:**
    - **TimeSeriesDB (InfluxDB):** Logs de segurança, métricas de tráfego de rede, dados de sensores físicos.
    - **PostgreSQL:** Inventário de ativos, políticas de segurança, registros de incidentes.

### 3. 🏥 IARA (Vigilância Epidemiológica)
- **Recebe de (via Message Bus/OAC):**
    - **OAC:** Pedidos de análise epidemiológica, dados demográficos.
    - **Cidadãos (via OAC):** Relatos de sintomas, dados de saúde (anonimizados e consentidos).
    - **Fontes Externas (via OAC):** Dados de hospitais, laboratórios, pesquisa de saúde.
- **Envia para (via Message Bus/OAC):**
    - **OAC:** Alertas de surtos potenciais, previsões epidemiológicas, recomendações de saúde pública.
    - **ANHANGÁ:** Necessidade de disseminação de informações de saúde urgentes em áreas afetadas.
- **Interage com Bases de Dados:**
    - **TimeSeriesDB (InfluxDB):** Séries temporais de sintomas, taxas de infecção, dados ambientais correlacionados.
    - **PostgreSQL:** Registros de saúde (anonimizados), modelos epidemiológicos, dados demográficos.

### 4. 🔥 SACI (Prevenção de Incêndios)
- **Recebe de (via Message Bus/OAC e diretamente de sensores):**
    - **Sensores IoT (ESP32):** Dados de temperatura, umidade, fumaça, localização. (MQTT -> Kafka)
    - **OAC:** Pedidos de avaliação de risco de incêndio, dados meteorológicos, mapas de vegetação.
    - **BOITATÁ:** Informações sobre infraestruturas em risco de incêndio.
    - **CAIPORA (se integrado no futuro):** Dados de monitoramento ambiental detalhado.
- **Envia para (via Message Bus/OAC):**
    - **OAC:** Alertas de risco de incêndio, previsões de propagação, recomendações de evacuação/combate.
    - **ANHANGÁ:** Necessidade de comunicação de alerta de incêndio e rotas de evacuação.
    - **Serviços de Emergência (via OAC):** Localização de focos, intensidade, recursos necessários.
- **Interage com Bases de Dados:**
    - **TimeSeriesDB (InfluxDB):** Dados de sensores de incêndio, condições meteorológicas.
    - **PostgreSQL:** Mapas de risco, modelos de propagação, inventário de recursos de combate.

### 5. ⚡ BOITATÁ (Resiliência Urbana)
- **Recebe de (via Message Bus/OAC):**
    - **OAC:** Pedidos de análise de resiliência, dados de infraestrutura.
    - **CURUPIRA:** Alertas sobre ameaças ciberfísicas a infraestruturas.
    - **SACI:** Informações sobre incêndios impactando infraestruturas.
    - **Utilities (via OAC):** Dados em tempo real de redes de energia, água, transporte.
- **Envia para (via Message Bus/OAC):**
    - **OAC:** Avaliações de impacto cascata, recomendações de mitigação, status de infraestrutura crítica.
    - **CURUPIRA:** Pedidos de varredura de segurança em sistemas SCADA.
    - **SACI:** Alertas sobre infraestruturas vulneráveis a incêndios.
- **Interage com Bases de Dados:**
    - **GraphDB (Neo4j):** Mapeamento de dependências de infraestrutura.
    - **TimeSeriesDB (InfluxDB):** Dados de sensores urbanos (tráfego, energia, etc.).
    - **PostgreSQL:** Modelos de simulação, planos de mitigação, inventário de infraestrutura.

### 6. 📡 ANHANGÁ (Comunicações de Emergência)
- **Recebe de (via Message Bus/OAC):**
    - **OAC:** Diretivas para ativação de redes de emergência, conteúdo de mensagens prioritárias.
    - **Todos os outros subsistemas (via OAC):** Pedidos de disseminação de alertas críticos (ex: alertas de incêndio do SACI, alertas de saúde da IARA, avisos de segurança do CURUPIRA/BOITATÁ).
- **Envia para (via Message Bus/OAC e diretamente para dispositivos):**
    - **OAC:** Status da rede de comunicações, confirmações de entrega.
    - **Cidadãos/Equipes de Emergência (diretamente ou via OAC):** Mensagens de alerta, instruções.
- **Interage com Bases de Dados:**
    - **TimeSeriesDB (InfluxDB):** Qualidade do sinal da rede mesh, tráfego de dados.
    - **PostgreSQL:** Configuração da rede, prioridades de mensagens, logs de comunicação.

## Protocolos Chave:

- **Interno (Subsistemas <-> OAC):** Apache Kafka para mensageria assíncrona e eventos. APIs gRPC/REST para comunicação síncrona específica.
- **IoT (Sensores -> SACI/Plataforma):** MQTT primariamente, com potencial uso de CoAP para dispositivos com restrições extremas. LoRaWAN para comunicação de longo alcance e baixo consumo.
- **Externo (OAC <-> Agências):** APIs RESTful/GraphQL seguras. Protocolos específicos de agências (ex: CAP para alertas).

Este documento é uma visão geral e será refinado à medida que os subsistemas são detalhados e implementados.
