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

## 4. Requisitos Adicionais da API para Suporte ao Dashboard Detalhado

Nota: Os modelos de dados detalhados para as respostas da API, utilizando Pydantic, são definidos em `src/api/schemas.py`. As descrições de payload abaixo fornecem uma visão conceitual da estrutura esperada.

A análise das `DASHBOARD_SPECIFICATIONS.md` (Dia 6) indica a necessidade de expansão ou detalhamento de endpoints da API para suportar plenamente as visualizações de dados ricas propostas. Embora os endpoints existentes (ex: `/api/v1/events`, `/api/v1/saci/risks`) forneçam uma base, os seguintes endpoints e suas especificações são propostos:

1.  **`GET /api/v1/events/{event_id}/details`**
    *   **Descrição:** Retorna detalhes completos de um evento específico para exibição no painel de detalhes do evento do ThreatMap.
    *   **Path Parameters:** `event_id` (string).
    *   **Query Parameters:** Nenhum.
    *   **Response Payload Concept:** Um objeto JSON estruturado com chaves como `informacoes_basicas`, `detalhes_tecnicos`, `impacto_estimado`, e `acoes_sugeridas`. A estrutura e os campos dentro de cada uma dessas chaves devem espelhar fielmente as especificações detalhadas na Seção 1.2 ("Painel de Detalhes do Evento") do `docs/DASHBOARD_SPECIFICATIONS.md`.

2.  **`GET /api/v1/subsystems/{subsistema_nome}/kpis`**
    *   **Descrição:** Retorna os Key Performance Indicators (KPIs) para um subsistema específico (e.g., SACI, IARA), destinados ao painel `SystemStatus`.
    *   **Path Parameters:** `subsistema_nome` (string, e.g., "SACI", "IARA", "CURUPIRA", "BOITATA", "ANHANGA").
    *   **Query Parameters:** Nenhum.
    *   **Response Payload Concept:** Um objeto JSON com os campos `indicador_visual`, `status_operacional`, `alertas_ativas`, `kpi_principal` (este sendo um objeto com `metrica`, `valor`, `tendencia`), `ultima_atualizacao`, e um campo opcional `detalhes_degradacao`. A estrutura e os campos devem corresponder ao detalhamento da Seção 2.1 ("Painel de Status do Sistema (SystemStatus)") do `docs/DASHBOARD_SPECIFICATIONS.md`.

3.  **`GET /api/v1/saci/heatmap`**
    *   **Descrição:** Fornece dados para a geração do mapa de calor de risco de incêndio do SACI.
    *   **Path Parameters:** Nenhum.
    *   **Query Parameters (Conforme especificado na subtask):**
        *   `temporal` (string, opcional, e.g., "real_time", "last_hour", "12h", "24h", "proximas_6h_preditivo"). Default: "real_time".
        *   `tipos_vegetacao` (string, opcional, lista separada por vírgulas, e.g., "mata_atlantica,cerrado,campo_aberto").
        *   `fatores_risco` (string, opcional, e.g., "apenas_climatico", "combinado_climatico_historico", "atividade_humana_recente"). Default: "combinado_climatico_historico".
        *   `bbox` (string, opcional, coordenadas da bounding box no formato "minLon,minLat,maxLon,maxLat").
    *   **Response Payload Concept:** Uma lista de objetos JSON. Cada objeto deve conter `geolocalizacao` (com `latitude`, `longitude`), `risco_incendio_score` (float, 0.0-1.0), e opcionalmente `direcao_vento_predominante` (string), `umidade_relativa_media` (float), `temperatura_media` (float).

4.  **`GET /api/v1/iara/heatmap`**
    *   **Descrição:** Fornece dados para a geração do mapa de calor de risco epidemiológico do IARA.
    *   **Path Parameters:** Nenhum.
    *   **Query Parameters (Conforme especificado na subtask):**
        *   `temporal` (string, opcional, e.g., "last_24h", "ultimos_7_dias", "tendencia_proximos_14_dias_preditivo"). Default: "last_24h".
        *   `demograficos_faixa_etaria` (string, opcional, lista separada por vírgulas, e.g., "0-5_anos,60_mais_anos,todos").
        *   `demograficos_vulnerabilidade` (string, opcional, e.g., "alta_comorbidades", "media_densidade_populacional", "baixa").
        *   `patogenos` (string, opcional, lista separada por vírgulas, e.g., "influenza_h1n1,dengue_tipo2,sindrome_respiratoria_aguda"). Default: "todos_relevantes".
        *   `bbox` (string, opcional, coordenadas da bounding box no formato "minLon,minLat,maxLon,maxLat").
    *   **Response Payload Concept:** Uma lista de objetos JSON. Cada objeto deve conter `geolocalizacao` (com `latitude`, `longitude`), `risco_epidemiologico_score` (float, 0.0-1.0), e opcionalmente `patogeno_predominante` (string), `velocidade_propagacao_estimada` (string).

5.  **`GET /api/v1/boitata/dependency_graph`**
    *   **Descrição:** Fornece dados de nós e arestas para a visualização do grafo de dependências urbanas do BOITATÁ.
    *   **Path Parameters:** Nenhum.
    *   **Query Parameters (Conforme especificado na subtask):**
        *   `sector` (string, opcional, e.g., "energia_centro_sul", "hospital_principal").
        *   `depth` (integer, opcional, profundidade das dependências). Default: 3.
        *   `node_filter_type` (string, opcional, para filtrar nós por tipo, e.g., "hospital,subestacao_energia").
    *   **Response Payload Concept:** Um objeto JSON com chaves `nodes` e `edges`.
        *   `nodes`: Lista de objetos, cada um com `id`, `label`, `type`, e um objeto `data` detalhado (contendo `informacoes_basicas`, `status_operacional`, `dependencias_diretas_resumidas`, `capacidade_operacional_percentual`, `risco_impacto_falha`), conforme Seção 2.2 ("Grafos de Dependências Urbanas (BOITATÁ)") do `docs/DASHBOARD_SPECIFICATIONS.md`.
        *   `edges`: Lista de objetos, cada um com `source`, `target`, `type`, e um objeto `data` opcional (com `latencia_impacto_horas`, `forca_dependencia_score`), conforme Seção 2.2 do `docs/DASHBOARD_SPECIFICATIONS.md`.

6.  **`GET /api/v1/events/correlated_timeline`**
    *   **Descrição:** Fornece sequências de eventos correlacionados para a visualização da timeline.
    *   **Path Parameters:** Nenhum.
    *   **Query Parameters (Conforme especificado na subtask):**
        *   `severidade_minima` (string, opcional, e.g., "ALTO", "CRITICO").
        *   `subsistemas_envolvidos` (string, opcional, lista separada por vírgulas, e.g., "SACI,CURUPIRA").
        *   `tipo_correlacao_primaria` (string, opcional, e.g., "cascata_falhas_infra").
        *   `time_range_start` (datetime string, opcional, ISO 8601).
        *   `time_range_end` (datetime string, opcional, ISO 8601).
        *   `limit` (integer, opcional). Default: 10.
    *   **Response Payload Concept:** Uma lista de "cenários de correlação". Cada cenário (`CorrelatedScenario`) deve ter `scenario_id`, `scenario_title` (opcional), `evento_inicial` (`TimelineEvent`), uma lista `propagacao_eventos` (de `PropagationStep`), e um `resolucao_estimada_ou_atual` opcional (`ResolutionInfo`). As estruturas de `TimelineEvent`, `PropagationStep` e `ResolutionInfo` devem seguir o detalhamento da Seção 2.3 ("Timeline de Eventos Correlacionados") do `docs/DASHBOARD_SPECIFICATIONS.md`, incluindo campos como `correlacao_com_anterior` e `informacoes_tecnicas_link` dentro de `PropagationStep`.

Os schemas de resposta associados em `src/api/schemas.py` precisarão ser expandidos para acomodar esses conjuntos de dados detalhados.

## Considerações Futuras

- **API de Desenvolvedor Externo:** Para permitir que terceiros (aprovados) integrem com o Sistema Guardião.
- **Políticas de Dados Detalhadas:** Especificar como os dados são acessados, compartilhados e protegidos em cada endpoint.
- **Mecanismos de Consentimento:** Para dados sensíveis de cidadãos.

Esta especificação é de alto nível e será detalhada conforme cada subsistema e funcionalidade é desenvolvida. O `docker-compose.yml` já define um serviço `saci_api` que será a primeira implementação de uma API de subsistema, focada no MVP do SACI.
