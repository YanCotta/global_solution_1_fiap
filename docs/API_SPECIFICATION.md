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

#### Orquestrador Agêntico Central (OAC)

- `POST /api/v1/orchestrator/tasks` - Submeter uma nova tarefa ou evento para o orquestrador.
  - **Request Body:** `{ "type": "event_report", "source": "citizen_app", "payload": { ... } }`
- `GET /api/v1/orchestrator/status` - Obter o status geral do sistema e dos subsistemas.
- `GET /api/v1/orchestrator/tasks/{task_id}` - Obter status de uma tarefa específica.

#### Relato de Eventos/Ameaças (Entrada para o OAC)

- `POST /api/v1/events/report`
  - **Request Body:** Detalhes do evento (tipo, localização, descrição, mídia).
  - **Exemplo:** Reportar um foco de incêndio, um sintoma de doença, uma falha de infraestrutura.

#### Alertas e Notificações

- `GET /api/v1/alerts` - Obter alertas ativos para o usuário/sistema autenticado.
  - **Query Params:** `?severity=high&region=MG&type=fire`
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Confirmar recebimento de um alerta.
- `GET /api/v1/notifications/preferences` - Gerenciar preferências de notificação.
- `PUT /api/v1/notifications/preferences` - Atualizar preferências.

#### Dados de Subsistemas (Exemplos, acesso controlado pelo OAC)

- **SACI (Incêndios)**
  - `GET /api/v1/saci/risks` - Obter mapa de risco de incêndio.
    - **Query Params:** `?lat=-19.9&lon=-43.9&radius=50km`
  - `GET /api/v1/saci/sensors` - Obter dados de sensores específicos (requer alta permissão).
- **IARA (Saúde)**
  - `GET /api/v1/iara/epidemiology/trends` - Obter tendências epidemiológicas.
    - **Query Params:** `?disease=dengue&region=MG`
- **BOITATÁ (Infraestrutura)**
  - `GET /api/v1/boitata/infrastructure/status` - Obter status de infraestruturas críticas.
    - **Query Params:** `?type=power_grid&area=belo_horizonte`
- **CURUPIRA (Segurança Ciberfísica)**
  - `GET /api/v1/curupira/threats/active` - Obter ameaças ciberfísicas ativas.
- **ANHANGÁ (Comunicações)**
  - `GET /api/v1/anhanga/network/status` - Obter status da rede de comunicação de emergência.

#### Administração (Acesso Restrito)

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

- `WS /ws/v1/alerts` - Stream de alertas em tempo real.
- `WS /ws/v1/saci/sensor_data` - Stream de dados de sensores do SACI (para visualizações ao vivo).

## Considerações Futuras

- **API de Desenvolvedor Externo:** Para permitir que terceiros (aprovados) integrem com o Sistema Guardião.
- **Políticas de Dados Detalhadas:** Especificar como os dados são acessados, compartilhados e protegidos em cada endpoint.
- **Mecanismos de Consentimento:** Para dados sensíveis de cidadãos.

Esta especificação é de alto nível e será detalhada conforme cada subsistema e funcionalidade é desenvolvida. O `docker-compose.yml` já define um serviço `saci_api` que será a primeira implementação de uma API de subsistema, focada no MVP do SACI.
