# Especificação da API (Conceitual) - Sistema Guardião

Este documento descreve a especificação conceitual para as APIs RESTful e GraphQL do Sistema Guardião, focando no API Gateway Central e na interação com os subsistemas.

## Princípios Gerais da API

- **Segurança:** Todas as chamadas devem ser autenticadas (OAuth 2.0 / OIDC) e autorizadas. HTTPS obrigatório.
- **Versionamento:** As APIs serão versionadas (ex: `/api/v1/...`).
- **Padronização:** Respostas em JSON. Códigos de status HTTP padronizados.
- **Rate Limiting:** Implementado para proteger contra abuso.
- **Documentação:** Auto-documentação via OpenAPI (Swagger) para REST e introspecção para GraphQL.

## 1. API Gateway Central

O API Gateway Central será o ponto único de entrada para a maioria das interações externas e internas (entre UIs e o backend). Ele roteará requisições para o Orquestrador Agêntico Central ou diretamente para subsistemas em casos específicos.

### 1.1. Endpoints RESTful (Exemplos)

#### Autenticação (Responsabilidade de um Identity Provider, ex: Keycloak)

- `POST /auth/token` - Obter token de acesso.
- `POST /auth/refresh` - Atualizar token de acesso.

#### Relato de Eventos de Ameaça

- `POST /api/v1/events/report`
  - **Request Body:** `ThreatEventInput` (conforme definido em `src/api/schemas.py` - contendo `subsystem_source`, `threat_type`, `severity`, `location`, `metadata`, `confidence_score`, `origin_sensor_id`).
  - **Ação Conceitual:** Recebe um novo evento de ameaça, valida-o e o encaminha para o `GuardianCentralOrchestrator` para processamento e correlação. Um ID de evento único é gerado.
  - **Response:** `AlertConfirmationResponse` (contendo `event_id`, `status`, `message`, `timestamp`).

#### Status do Sistema

- `GET /api/v1/system/status`
  - **Request Body:** Nenhum.
  - **Ação Conceitual:** Retorna o status operacional geral do Sistema Guardião, incluindo o status de cada subsistema individual e a contagem de ameaças ativas.
  - **Response:** `SystemStatusResponse` (contendo `overall_status`, `timestamp`, `active_threats_count`, e uma lista de `subsystems` com seus `name`, `status`, `alerts_count`, etc.).

#### Listagem e Filtragem de Eventos

- `GET /api/v1/events`
  - **Request Body:** Nenhum.
  - **Query Parameters (Opcionais):**
    - `subsystem: Optional[str]` - Filtra eventos pela subsistema de origem (ex: "SACI").
    - `severity_threshold: Optional[float]` - Filtra eventos por um limiar mínimo de severidade (0.0 a 1.0).
    - `limit: int` (default: 100) - Número máximo de eventos a serem retornados.
  - **Ação Conceitual:** Retorna uma lista de eventos de ameaça recentes ou filtrados, recuperados do banco de dados de eventos.
  - **Response:** Lista de objetos `ThreatEventResponse`.

#### Alerta Manual Específico do Subsistema (Exemplo SACI)

- `POST /api/v1/saci/manual_alert`
  - **Request Body:** `SaciManualAlertRequest` (contendo `location`, `description`, `reported_by`, `urgency`, `metadata`).
  - **Ação Conceitual:** Permite o registro de um alerta manual para o subsistema SACI. Isso pode gerar um `ThreatEvent` que é então processado pelo orquestrador ou enviado diretamente ao SACI.
  - **Response:** `AlertConfirmationResponse` (confirmando o recebimento e o ID do alerta manual gerado).

#### Alertas e Notificações (Endpoints Genéricos Existentes - a serem revisados/integrados)
Ainda existem definições para:
- `GET /api/v1/alerts` - Obter alertas ativos para o usuário/sistema autenticado. (Considerar integração com `GET /api/v1/events` ou diferenciar claramente o propósito).
  - **Query Params:** `?severity=high&region=MG&type=fire`
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Confirmar recebimento de um alerta.
- `GET /api/v1/notifications/preferences` - Gerenciar preferências de notificação.
- `PUT /api/v1/notifications/preferences` - Atualizar preferências.

#### Dados de Subsistemas (Exemplos, acesso controlado pelo OAC - a serem revisados/integrados)
Ainda existem definições para interações diretas com subsistemas. A estratégia primária é via Orquestrador, mas estes podem ser mantidos para casos de uso específicos, com devida justificação e controle.
- **SACI (Incêndios)**
  - `GET /api/v1/saci/risks`
- **IARA (Saúde)**
  - `GET /api/v1/iara/epidemiology/trends`
- **BOITATÁ (Infraestrutura)**
  - `GET /api/v1/boitata/infrastructure/status`
- **CURUPIRA (Segurança Ciberfísica)**
  - `GET /api/v1/curupira/threats/active`
- **ANHANGÁ (Comunicações)**
  - `GET /api/v1/anhanga/network/status`

#### Administração (Acesso Restrito - a serem revisados/integrados)
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users`
- `GET /api/v1/admin/system/logs`

### 1.2. Endpoints GraphQL (Exemplos)

GraphQL será usado para consultas complexas e flexíveis, especialmente para dashboards e aplicações que necessitam de dados agregados de múltiplos domínios.

**Exemplo de Query:** Obter detalhes de um evento de incêndio, incluindo dados de sensores próximos e o status da infraestrutura elétrica na área.

```graphql
query FireIncidentDetails($incidentId: ID!) {
  incident(id: $incidentId) {
    id
    type
    location {
      latitude
      longitude
    }
    reportedAt
    status
    saciData {
      riskLevel
      windSpeed
      humidity
      nearbySensors(radius: "1km") {
        id
        type
        lastReading
      }
    }
    boitataData {
      infrastructureImpact(type: POWER_GRID) {
        assetId
        status
        estimatedRecoveryTime
      }
    }
    anhangaAlerts {
      message
      sentAt
      channel
    }
  }
}
```

**Exemplo de Mutation:** Atualizar o status de um plano de mitigação.

```graphql
mutation UpdateMitigationPlanStatus($planId: ID!, $newStatus: MitigationStatus!) {
  updateMitigationPlan(id: $planId, status: $newStatus) {
    id
    name
    status
    updatedAt
  }
}
```

## 2. APIs Internas (Entre Subsistemas)

A comunicação entre subsistemas será primariamente via Message Bus (Kafka) para garantir desacoplamento e resiliência. No entanto, para interações síncronas específicas ou de alta performance, APIs internas (possivelmente gRPC para eficiência) podem ser usadas. Estas não seriam expostas pelo API Gateway Central.

**Exemplo:**

- CURUPIRA pode expor uma API gRPC para BOITATÁ consultar rapidamente o status de segurança de um ativo específico.
- `service CurupiraInternalService { rpc GetAssetSecurityStatus(AssetRequest) returns (AssetSecurityResponse); }`

## 3. WebSockets

Para comunicação em tempo real (ex: atualizações de dashboard, alertas instantâneos):

- `WS /ws/v1/alerts`
  - **Ação Conceitual:** Clientes (como dashboards de monitoramento) conectam-se a este endpoint WebSocket. O servidor envia mensagens em tempo real para os clientes conectados sempre que novos alertas são gerados ou atualizações importantes do sistema ocorrem. As mensagens podem ser novos `ThreatEventResponse` completos ou notificações resumidas.
  - **Formato da Mensagem (Servidor para Cliente - Exemplo JSON):**
    ```json
    {
      "alert_id": "evt_uuid_timestamp", // ID do evento ou do alerta específico
      "type": "new_threat_event", // Tipos podem incluir: "new_threat_event", "event_update", "system_notification"
      "timestamp": "2023-10-27T12:00:00Z", // ISO 8601 timestamp
      "payload": {
        // O payload pode ser um objeto ThreatEventResponse completo ou um resumo customizado.
        // Exemplo de resumo:
        "event_id": "evt_uuid_timestamp",
        "subsystem_source": "SACI",
        "threat_type": "wildfire",
        "severity": 0.85,
        "location": [-19.9174, -43.9343],
        "message": "Alerta de incêndio de alta severidade detectado na Zona Industrial."
      }
    }
    ```
  - **Interação:** Conexão persistente. O servidor envia mensagens de forma assíncrona.
- `WS /ws/v1/saci/sensor_data` - Stream de dados de sensores do SACI (para visualizações ao vivo). (Este é um exemplo pré-existente, manter para referência ou integrar com a lógica de alertas se aplicável).


### Nota sobre Autenticação e Autorização (Conceitual)

Para um ambiente de produção, a API Central do Sistema Guardião exigirá mecanismos robustos de autenticação e autorização para proteger seus recursos e dados. A abordagem recomendada seria:

- **Autenticação:** OAuth 2.0 com OpenID Connect (OIDC), utilizando JWT (JSON Web Tokens) como tokens de acesso. Um Identity Provider (IdP) dedicado (como Keycloak, Auth0, ou similar) seria responsável pela emissão e validação dos tokens.
- **Autorização:** Mecanismos baseados em roles (RBAC - Role-Based Access Control) e possivelmente em atributos (ABAC - Attribute-Based Access Control) seriam implementados. As permissões definiriam quais usuários ou sistemas clientes podem acessar quais endpoints e executar quais operações.

A implementação detalhada destes mecanismos de segurança está fora do escopo da fase conceitual atual do MVP (Minimum Viable Product), mas é um requisito fundamental para implantações futuras. Os "Princípios Gerais da API" sobre segurança (HTTPS, etc.) devem ser observados desde o início.

## 4. Requisitos da API para Suporte ao Dashboard

Esta seção especifica os endpoints e estruturas de dados necessários para popular todas as visualizações detalhadas descritas em `docs/DASHBOARD_SPECIFICATIONS.md`. Cada endpoint é projetado para fornecer dados otimizados para componentes específicos do dashboard executivo e dashboards especializados.

### 4.1. API para ThreatMap (Mapa Principal de Ameaças)

#### 4.1.1. Eventos Georreferenciados em Tempo Real
- `GET /api/v1/dashboard/threat_map/events`
  - **Query Parameters:**
    - `subsystems: Optional[str]` - Lista separada por vírgulas (e.g., "SACI,CURUPIRA,IARA")
    - `severity_levels: Optional[str]` - Lista separada por vírgulas (e.g., "ALTO,CRITICO")
    - `time_range: Optional[str]` - Período (e.g., "1h", "6h", "24h", "7d", "30d")
    - `bbox: Optional[str]` - Bounding box "minLon,minLat,maxLon,maxLat"
    - `include_infrastructure: Optional[bool]` - Include infrastructure context
  - **Response:** Lista de `ThreatEventResponse` com campos adicionais para visualização no mapa
  - **Uso no Dashboard:** Popular marcadores no ThreatMap com cores por severidade e ícones por subsistema

#### 4.1.2. Detalhes de Evento Individual
- `GET /api/v1/dashboard/events/{event_id}/details`
  - **Path Parameters:** `event_id: str`
  - **Response:** `EventDetailsResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Painel de detalhes que aparece no hover/click de eventos no mapa

#### 4.1.3. Camadas de Contexto do Mapa
- `GET /api/v1/dashboard/map_layers/infrastructure`
  - **Query Parameters:**
    - `layer_types: Optional[str]` - "hospitais,escolas,bombeiros,energia,agua,telecom"
    - `bbox: Optional[str]` - Bounding box para filtrar por região
  - **Response:** GeoJSON com pontos de infraestrutura crítica
  - **Uso no Dashboard:** Camadas opcionais sobre o ThreatMap

### 4.2. API para SystemStatus (Painel de Status dos Subsistemas)

#### 4.2.1. Status Consolidado de Todos os Subsistemas
- `GET /api/v1/dashboard/system/status_overview`
  - **Response:** `SystemStatusResponse` expandido com KPIs por subsistema
  - **Uso no Dashboard:** Painel SystemStatus mostrando status operacional de cada Guardian

#### 4.2.2. KPIs Detalhados por Subsistema
- `GET /api/v1/dashboard/subsystems/{subsystem_name}/kpis`
  - **Path Parameters:** `subsystem_name: str` (e.g., "SACI", "CURUPIRA")
  - **Response:** `SubsystemKpiResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Cards detalhados de status com indicadores visuais e métricas principais

### 4.3. API para Mapas de Calor Especializados

#### 4.3.1. Mapa de Calor de Risco de Incêndio (SACI)
- `GET /api/v1/dashboard/saci/heatmap`
  - **Query Parameters:**
    - `temporal: Optional[str]` - "real_time", "last_hour", "12h", "24h", "proximas_6h_preditivo"
    - `tipos_vegetacao: Optional[str]` - "mata_atlantica,cerrado,campo_aberto"
    - `fatores_risco: Optional[str]` - "apenas_climatico", "combinado_climatico_historico"
    - `bbox: Optional[str]` - Bounding box
  - **Response:** `SaciHeatmapResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Visualização de calor sobreposta ao mapa com gradientes de risco

#### 4.3.2. Mapa de Calor Epidemiológico (IARA)
- `GET /api/v1/dashboard/iara/heatmap`
  - **Query Parameters:**
    - `temporal: Optional[str]` - "last_24h", "ultimos_7_dias", "tendencia_proximos_14_dias"
    - `demograficos_faixa_etaria: Optional[str]` - "0-5_anos,60_mais_anos,todos"
    - `patogenos: Optional[str]` - "influenza_h1n1,dengue_tipo2,sindrome_respiratoria_aguda"
    - `bbox: Optional[str]` - Bounding box
  - **Response:** `IaraHeatmapResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Sobreposição de risco epidemiológico com informações de patógenos

### 4.4. API para Grafo de Dependências Urbanas (BOITATÁ)

#### 4.4.1. Dados do Grafo de Dependências
- `GET /api/v1/dashboard/boitata/dependency_graph`
  - **Query Parameters:**
    - `sector: Optional[str]` - "energia_centro_sul", "hospital_principal"
    - `depth: Optional[int]` - Profundidade das dependências (default: 3)
    - `node_filter_type: Optional[str]` - "hospital,subestacao_energia,telecom"
    - `include_failure_simulation: Optional[bool]` - Incluir dados de simulação de falha
  - **Response:** `DependencyGraphResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Visualização interativa de nós e arestas representando infraestrutura crítica

#### 4.4.2. Simulação de Impacto de Falha
- `POST /api/v1/dashboard/boitata/failure_simulation`
  - **Request Body:** 
    ```json
    {
      "target_node_id": "HOSP-BH-001",
      "failure_type": "complete_shutdown",
      "propagation_depth": 3
    }
    ```
  - **Response:** Grafo atualizado com impactos simulados
  - **Uso no Dashboard:** Análise "what-if" em tempo real no grafo de dependências

### 4.5. API para Timeline de Eventos Correlacionados

#### 4.5.1. Cenários de Correlação Temporal
- `GET /api/v1/dashboard/events/correlated_timeline`
  - **Query Parameters:**
    - `severidade_minima: Optional[str]` - "ALTO", "CRITICO"
    - `subsistemas_envolvidos: Optional[str]` - "SACI,CURUPIRA,BOITATA"
    - `tipo_correlacao_primaria: Optional[str]` - "cascata_falhas_infra", "propagacao_espacial"
    - `time_range_start: Optional[datetime]` - ISO 8601 format
    - `time_range_end: Optional[datetime]` - ISO 8601 format
    - `limit: Optional[int]` - Máximo de cenários (default: 10)
  - **Response:** `CorrelatedEventTimelineResponse` (definido em schemas.py)
  - **Uso no Dashboard:** Timeline interativa mostrando cascatas de eventos e suas correlações

#### 4.5.2. Análise de Propagação de Eventos
- `GET /api/v1/dashboard/events/{scenario_id}/propagation_analysis`
  - **Path Parameters:** `scenario_id: str`
  - **Response:** Análise detalhada de como eventos se propagaram através dos subsistemas
  - **Uso no Dashboard:** Drill-down detalhado de cenários específicos na timeline

### 4.6. API para Alertas e Notificações (AlertCenter)

#### 4.6.1. Alertas Ativos Priorizados
- `GET /api/v1/dashboard/alerts/active`
  - **Query Parameters:**
    - `priority_level: Optional[str]` - "LOW", "MEDIUM", "HIGH", "CRITICAL"
    - `subsystems: Optional[str]` - Filtrar por subsistemas
    - `limit: Optional[int]` - Máximo de alertas (default: 50)
  - **Response:** Lista de alertas ordenados por prioridade e timestamp
  - **Uso no Dashboard:** Painel AlertCenter no dashboard executivo

#### 4.6.2. Histórico de Ações de Resposta
- `GET /api/v1/dashboard/alerts/{alert_id}/response_history`
  - **Path Parameters:** `alert_id: str`
  - **Response:** Histórico completo de ações tomadas para um alerta específico
  - **Uso no Dashboard:** Tracking de resolução de alertas

### 4.7. APIs para Dashboards Especializados por Subsistema

#### 4.7.1. Dashboard Específico do SACI
- `GET /api/v1/dashboard/saci/overview`
  - **Response:** Métricas específicas do SACI: índices de risco, sensores ativos, predições
  - **Uso no Dashboard:** Dashboard especializado para monitoramento de incêndios

#### 4.7.2. Dashboard Específico do CURUPIRA
- `GET /api/v1/dashboard/curupira/security_overview`
  - **Response:** Métricas de segurança: tentativas de intrusão, vulnerabilidades, status de proteção
  - **Uso no Dashboard:** Dashboard especializado para monitoramento de segurança ciberfísica

#### 4.7.3. Dashboard Específico da IARA
- `GET /api/v1/dashboard/iara/health_overview`
  - **Response:** Métricas epidemiológicas: surtos ativos, capacidade hospitalar, indicadores de saúde
  - **Uso no Dashboard:** Dashboard especializado para monitoramento de saúde pública

#### 4.7.4. Dashboard Específico do BOITATÁ
- `GET /api/v1/dashboard/boitata/infrastructure_overview`
  - **Response:** Status de infraestrutura crítica: energia, água, telecomunicações, transportes
  - **Uso no Dashboard:** Dashboard especializado para monitoramento de infraestrutura

#### 4.7.5. Dashboard Específico do ANHANGÁ
- `GET /api/v1/dashboard/anhanga/communications_overview`
  - **Response:** Status de comunicações de emergência: cobertura, latência, redundância
  - **Uso no Dashboard:** Dashboard especializado para monitoramento de comunicações

### 4.8. APIs para Performance e Métricas Operacionais

#### 4.8.1. Métricas de Performance do Sistema
- `GET /api/v1/dashboard/system/performance_metrics`
  - **Query Parameters:**
    - `time_range: Optional[str]` - Período para agregação de métricas
    - `metrics: Optional[str]` - "latency,throughput,error_rate,resource_usage"
  - **Response:** Métricas operacionais agregadas
  - **Uso no Dashboard:** Monitoramento de saúde técnica do sistema

#### 4.8.2. Análise de Capacidade e Escalabilidade
- `GET /api/v1/dashboard/system/capacity_analysis`
  - **Response:** Análise de utilização de recursos e projeções de capacidade
  - **Uso no Dashboard:** Planejamento de capacidade e alertas de resource exhaustion

### 4.9. Estruturas de Resposta Otimizadas para Dashboard

Todos os endpoints utilizam os modelos Pydantic definidos em `src/api/schemas.py`, com as seguintes otimizações para dashboard:

1. **Campos de Visualização Adicionais:**
   - `display_color`: Cor sugerida para visualização
   - `icon_type`: Tipo de ícone a ser usado
   - `priority_score`: Score numérico para ordenação
   - `formatted_values`: Valores pré-formatados para exibição

2. **Metadados de Cache:**
   - `cache_timestamp`: Timestamp dos dados para invalidação de cache
   - `refresh_interval_seconds`: Intervalo sugerido para atualização

3. **Informações de Contexto:**
   - `related_events`: Links para eventos relacionados
   - `drill_down_links`: URLs para análises mais detalhadas
   - `export_options`: Formatos disponíveis para exportação

### 4.10. Considerações de Performance para Dashboard

1. **Pagination e Lazy Loading:**
   - Todos os endpoints que retornam listas suportam paginação
   - Implementação de lazy loading para componentes pesados como grafos

2. **WebSocket para Atualizações em Tempo Real:**
   - `WS /api/v1/dashboard/realtime_updates`
   - Stream de eventos para atualização automática do dashboard

3. **Caching Estratégico:**
   - Redis cache para dados frequentemente acessados
   - Cache invalidation baseado em eventos de mudança de estado

4. **Compression e Otimização:**
   - Compressão gzip para payloads grandes
   - Campos opcionais para controle de tamanho de resposta

Esta especificação garante que cada componente visual descrito em `DASHBOARD_SPECIFICATIONS.md` tenha endpoints de API correspondentes bem definidos, criando uma ponte sólida entre o frontend conceitual e o backend implementável.

## Considerações Futuras

- **API de Desenvolvedor Externo:** Para permitir que terceiros (aprovados) integrem com o Sistema Guardião.
- **Políticas de Dados Detalhadas:** Especificar como os dados são acessados, compartilhados e protegidos em cada endpoint.
- **Mecanismos de Consentimento:** Para dados sensíveis de cidadãos.

Esta especificação é de alto nível e será detalhada conforme cada subsistema e funcionalidade é desenvolvida. O `docker-compose.yml` já define um serviço `saci_api` que será a primeira implementação de uma API de subsistema, focada no MVP do SACI.
