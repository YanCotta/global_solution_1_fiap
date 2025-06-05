# Plano de Implementação MVP Conceitual para Outros Subsistemas do Sistema Guardião

**Status:** Planejamento Conceitual (Global Solution FIAP 2025.1)  
**Data:** Junho 2025  
**Versão:** 1.0

---

## Introdução

Este documento detalha o plano de implementação conceitual para os Produtos Mínimos Viáveis (MVPs) dos subsistemas CURUPIRA, IARA, BOITATÁ e ANHANGÁ do Sistema Guardião. Dado o escopo do sprint atual, o foco é fornecer um roteiro claro para o desenvolvimento inicial e validação das funcionalidades centrais de cada um desses guardiões digitais.

---

## <a name="curupira-mvp"></a>🦶 CURUPIRA - Centro Unificado de Resposta e Proteção de Infraestruturas Críticas

**Inspiração Folclórica Breve:** O Curupira é o protetor das matas e dos animais, conhecido por confundir caçadores e proteger a natureza. No Sistema Guardião, ele é o guardião da infraestrutura crítica nacional, protegendo-a contra ameaças físicas e digitais.

### Objetivos Principais para um MVP

* **Funcionalidade Central Mínima:** Demonstrar a capacidade de correlacionar um evento físico simulado (ex: um alerta de sensor de vibração não autorizado em um data center crítico) com um evento cibernético simulado (ex: múltiplas tentativas de login malsucedidas nos servidores desse mesmo data center) ocorrendo em uma janela de tempo próxima.
* **Problema Principal a Validar:** A viabilidade de um sistema básico de regras para identificar potenciais ameaças híbridas (físico-digitais) que, isoladamente, poderiam não ser consideradas de alta criticidade.

### Componentes/Módulos de Software Chave (Conceitual)

* `AnalisadorEventosFisicosSimulados`: Módulo responsável por receber e interpretar dados de sensores físicos simulados (ex: vibração, temperatura, acesso não autorizado).
* `AnalisadorLogsCiberneticosSimulados`: Módulo para processar logs simulados de sistemas de segurança cibernética (ex: firewall, IDS/IPS, logs de acesso a servidores).
* `MotorCorrelacaoHibridaBasico`: Componente central do MVP que aplicará regras simples para identificar correlações entre os eventos físicos e cibernéticos.
* `GeradorAlertaHibrido`: Módulo que formata e envia um `ThreatEvent` para o `GuardianCentralOrchestrator` caso uma correlação suspeita seja identificada.

### Fontes de Dados e Entradas (Inputs) para o MVP

* **Logs de Rede Simulados:** Arquivos de log simulados contendo tentativas de acesso, alertas de firewall, tráfego de rede suspeito (referenciar `curupira_network_metrics` de `docs/DATA_MODELS.md`).
* **Leituras de Sensores Físicos Simulados:** Dados simulados de sensores como detectores de movimento, sensores de abertura de portas/janelas, sensores de vibração em locais críticos (referenciar `physical_anomalies` de `docs/DATA_MODELS.md`).
* **Contexto de Ativos Críticos:** Uma lista simplificada de ativos críticos e seus atributos (ex: localização, tipo de ativo).

### Saídas e Ações (Outputs) do MVP

* **Alerta de Ameaça Híbrida Potencial:** Um `ThreatEvent` enviado ao `GuardianCentralOrchestrator` indicando uma correlação detectada, com um nível de severidade e confiança calculados pelo `MotorCorrelacaoHibridaBasico`.
* **Relatório de Correlação Simples:** Um log interno detalhando os eventos físicos e cibernéticos que dispararam o alerta.

### Lógica Central / IA Básica para o MVP

* **Sistema de Regras:** A lógica central será baseada em um conjunto de regras predefinidas. Por exemplo:
    * `REGRA_1`: SE (Alerta de sensor de vibração no rack de servidores X) E (Múltiplas tentativas de login falhas no servidor Y do rack X em menos de 5 minutos) ENTÃO Gerar Alerta de Ameaça Híbrida (Confiança Média).
    * `REGRA_2`: SE (Alerta de acesso físico não autorizado à sala do gerador) E (Scan de portas detectado na rede interna do sistema de controle do gerador em menos de 10 minutos) ENTÃO Gerar Alerta de Ameaça Híbrida (Confiança Alta).
* Não envolverá os modelos de Redes Neurais Ensemble mencionados na especificação completa do CURUPIRA para o MVP, mas sim uma base para eles.

### Interação Conceitual com `GuardianCentralOrchestrator`

* **Recebimento de Tarefas/Eventos:** O MVP do CURUPIRA poderia ser "ativado" por um evento de infraestrutura reportado pelo BOITATÁ (via OAC) para focar seu monitoramento simulado.
* **Geração de `ThreatEvent`:**
    * `subsystem_source`: "CURUPIRA"
    * `threat_type`: Ex: "potential_hybrid_access_violation", "correlated_physical_cyber_anomaly"
    * `severity`: Calculada com base na criticidade do ativo e na força da regra de correlação.
    * `location`: Coordenadas do ativo crítico afetado.
    * `metadata`: Incluiria IDs dos eventos físicos e cibernéticos correlacionados, e a regra que disparou o alerta.
    * `origin_sensor_id`: Poderia ser uma concatenação simbólica como `physical_sensor_sim_XYZ;cyber_log_source_ABC`.

### Pontos de Integração Chave com Outros Subsistemas (Conceitual para MVP)

* **BOITATÁ:** Receber informações sobre o status e a criticidade de infraestruturas para priorizar a correlação de ameaças (fluxo de dados: BOITATÁ -> OAC -> CURUPIRA).
* **ANHANGÁ:** Em caso de detecção de ameaça crítica, o OAC poderia instruir ANHANGÁ a garantir a comunicação para as equipes de resposta, baseado no alerta do CURUPIRA.

### Fases de Implementação Sugeridas para o MVP

1.  **Fase 1: Definição de Dados e Estruturas:**
    * Especificar formatos detalhados para os logs e dados de sensores físicos simulados.
    * Definir a estrutura interna do `MotorCorrelacaoHibridaBasico` e as regras iniciais.
    * Modelar o `ThreatEvent` específico que o CURUPIRA MVP gerará.
2.  **Fase 2: Implementação dos Analisadores e Motor de Correlação:**
    * Desenvolver os módulos `AnalisadorEventosFisicosSimulados` e `AnalisadorLogsCiberneticosSimulados` para ler e normalizar os dados de entrada.
    * Implementar o `MotorCorrelacaoHibridaBasico` com o conjunto inicial de regras.
3.  **Fase 3: Simulação de Geração de Alertas e Interação:**
    * Criar um script para simular a chegada de eventos físicos e cibernéticos.
    * Testar a capacidade do motor de correlação de identificar ameaças e gerar o `ThreatEvent` correspondente.
    * Simular o envio deste `ThreatEvent` para uma interface mock do `GuardianCentralOrchestrator`.

---

## <a name="iara-mvp"></a>🏥 IARA - Inteligência Artificial para Resposta e Alerta Epidemiológico

**Inspiração Folclórica Breve:** Iara é a mãe d'água, uma sereia que encanta e protege os rios. No Sistema Guardião, IARA monitora a "saúde ambiental" e os sinais precoces de doenças, protegendo a saúde da população.

### Objetivos Principais para um MVP

* **Funcionalidade Central Mínima:** Calcular e exibir um "Nível de Risco de Surto" (ex: Baixo, Médio, Alto) para uma doença infecciosa fictícia (ou uma doença real simplificada como gripe) em uma ou mais regiões geográficas simuladas. Este cálculo se baseará em dados simulados de fatores ambientais (ex: temperatura, umidade, qualidade do ar) e um número simulado de casos reportados.
* **Problema Principal a Validar:** A viabilidade de integrar dados ambientais e de saúde simulados para gerar um indicador de risco epidemiológico, mesmo que de forma básica, validando o conceito central da IARA.

### Componentes/Módulos de Software Chave (Conceitual)

* `ColetorDadosSaudeSimulados`: Módulo para gerar ou ler dados simulados de incidência de casos de uma doença.
* `ColetorDadosAmbientaisSimulados`: Módulo para gerar ou ler dados ambientais simulados relevantes (ex: temperatura, umidade, poluição do ar).
* `CalculadoraRiscoEpidemiologicoSEIRBasico`: Implementação de um modelo SEIR (Suscetível, Exposto, Infectado, Removido) simplificado ou um sistema de pontuação baseado em regras para calcular o nível de risco.
* `GeradorAlertaEpidemiologico`: Módulo que formata o risco calculado como um `ThreatEvent` para o OAC.

### Fontes de Dados e Entradas (Inputs) para o MVP

* **Dados de Saúde Simulados:** Número de novos casos diários/semanais para uma doença fictícia ou gripe em regiões específicas (referenciar `disease_surveillance` de `docs/DATA_MODELS.md`).
* **Dados Ambientais Simulados:** Médias diárias/semanais de temperatura, umidade relativa, índice de qualidade do ar (AQI) para as mesmas regiões (referenciar `environmental_health` de `docs/DATA_MODELS.md`).
* **Parâmetros Populacionais Simulados:** População total estimada para as regiões (necessário para modelos como SEIR).

### Saídas e Ações (Outputs) do MVP

* **Nível de Risco de Surto Regional:** Um `ThreatEvent` por região avaliada, indicando o nível de risco (ex: "Baixo", "Médio", "Alto", "Crítico") e os principais fatores contribuintes.
* **Log Interno:** Registro das entradas de dados, parâmetros do modelo (se aplicável) e o risco calculado.

### Lógica Central / IA Básica para o MVP

* **Modelo SEIR Simplificado:** Implementar as equações diferenciais básicas do modelo SEIR.
    * Parâmetros como taxa de transmissão ($\beta$), período de incubação ($1/\sigma$), e período infeccioso ($1/\gamma$) seriam definidos com valores fixos e hipotéticos para o MVP.
    * O modelo poderia ser "influenciado" pelos dados ambientais de forma rudimentar (ex: $\beta$ aumenta ligeiramente com certas condições de temperatura/umidade).
* **OU Sistema de Pontuação Baseado em Regras:**
    * Ex: SE (temperatura > X E umidade < Y) => score_ambiental += Z
    * SE (novos_casos > W) => score_casos += V
    * Risco_Total = F(score_ambiental, score_casos).
* Para o MVP, não se implementará a análise biométrica distribuída ou correlação comportamental complexa citada na especificação completa da IARA. O foco é validar o fluxo de dados e o cálculo de risco básico.

### Interação Conceitual com `GuardianCentralOrchestrator`

* **Recebimento de Tarefas/Eventos:** O OAC poderia solicitar uma avaliação de risco para uma região específica ou fornecer dados agregados de fontes externas.
* **Geração de `ThreatEvent`:**
    * `subsystem_source`: "IARA"
    * `threat_type`: Ex: "epidemic_risk_influenza_like_illness", "potential_outbreak_alert"
    * `severity`: Mapeado a partir do nível de risco calculado (ex: Alto Risco = severidade 0.75).
    * `location`: Coordenadas ou identificador da região avaliada.
    * `metadata`: Incluiria o nível de risco (Baixo/Médio/Alto), os principais fatores (ex: "alta umidade", "aumento de casos"), e talvez a projeção de casos do SEIR para os próximos X dias.
    * `origin_sensor_id`: "simulated_regional_data_feed".

### Pontos de Integração Chave com Outros Subsistemas (Conceitual para MVP)

* **ANHANGÁ:** Em um cenário de risco "Alto" ou "Crítico", o OAC poderia instruir o ANHANGÁ a preparar a disseminação de alertas de saúde pública para a região afetada, com base no `ThreatEvent` da IARA.
* **SACI/BOITATÁ:** Embora menos direto para o MVP, dados ambientais coletados por outros subsistemas poderiam, no futuro, alimentar a IARA.

### Fases de Implementação Sugeridas para o MVP

1.  **Fase 1: Definição do Modelo e Dados Simulados:**
    * Escolher a doença alvo para simulação (ex: gripe).
    * Definir os parâmetros para o modelo SEIR básico ou as regras do sistema de pontuação.
    * Criar scripts para gerar dados simulados de saúde e ambientais para algumas regiões.
    * Definir a estrutura do `ThreatEvent` da IARA.
2.  **Fase 2: Implementação da Lógica de Cálculo de Risco:**
    * Implementar a `CalculadoraRiscoEpidemiologicoSEIRBasico` (ou o sistema de pontuação).
    * Desenvolver os coletores para processar os dados simulados.
3.  **Fase 3: Simulação da Geração de Alertas:**
    * Executar o sistema com os dados simulados.
    * Testar a geração dos níveis de risco e a criação do `ThreatEvent`.
    * Simular o envio do `ThreatEvent` para uma interface mock do `GuardianCentralOrchestrator`.

---

## <a name="boitata-mvp"></a>⚡ BOITATÁ - Bloco Operacional Integrado para Tratamento de Anomalias Urbanas

**Inspiração Folclórica Breve:** O Boitatá é uma serpente de fogo que protege os campos contra aqueles que os incendeiam. No Sistema Guardião, BOITATÁ protege as "veias" da cidade (infraestrutura) contra falhas em cascata.

### Objetivos Principais para um MVP

* **Funcionalidade Central Mínima:** Simular o impacto de uma falha em um componente de infraestrutura crítica (ex: uma subestação de energia principal) em outros componentes diretamente dependentes (ex: um hospital que depende dessa subestação, uma estação de bombeamento de água).
* **Problema Principal a Validar:** A capacidade de modelar dependências simples entre infraestruturas e identificar o primeiro nível de um efeito cascata.

### Componentes/Módulos de Software Chave (Conceitual)

* `ModeloInfraestruturaUrbanaSimples`: Uma estrutura de dados (ex: grafo ou dicionários aninhados) representando alguns ativos de infraestrutura e suas dependências diretas.
* `SimuladorFalhaPrimaria`: Módulo que permite "induzir" uma falha em um ativo do modelo.
* `AnalisadorImpactoCascataNivel1`: Componente que, dada uma falha primária, identifica os ativos diretamente dependentes que seriam afetados.
* `GeradorAlertaCascataBOITATA`: Módulo que cria um `ThreatEvent` para o OAC detalhando o risco de cascata.

### Fontes de Dados e Entradas (Inputs) para o MVP

* **Mapa de Dependências Simplificado:** Uma definição manual de alguns ativos (ex: `Subestacao_A`, `Hospital_X`, `EstacaoBombeamento_Y`) e suas relações de dependência (ex: `Hospital_X` depende de `Subestacao_A` para energia). (Referenciar conceitualmente `docs/DATA_MODELS.md`, especificamente o modelo de grafos para BOITATÁ).
* **Evento de Falha Inicial:** Um input simulado indicando que um ativo específico falhou (ex: `Subestacao_A` está offline).

### Saídas e Ações (Outputs) do MVP

* **Alerta de Risco de Falha em Cascata:** Um `ThreatEvent` para o OAC, identificando o ativo primário falho e os ativos secundários que estão em risco devido à dependência.
* **Log de Simulação:** Detalhes da falha inicial e dos impactos diretos identificados.

### Lógica Central / IA Básica para o MVP

* **Análise de Grafo de Dependência Direta:** A lógica central envolverá a travessia de um grafo (ou estrutura similar) para encontrar nós adjacentes que representam dependências.
    * Se o Nó A (falho) tem uma aresta de "fornece_para" para o Nó B, e o Nó A falha, então o Nó B está em risco.
* Não envolverá a modelagem de sistemas complexos ou predição avançada de falhas em cascata com Digital Twin, como especificado para a versão completa do BOITATÁ. O MVP foca no primeiro nível de impacto.

### Interação Conceitual com `GuardianCentralOrchestrator`

* **Recebimento de Tarefas/Eventos:** O OAC pode informar ao BOITATÁ sobre uma falha detectada por outro subsistema (ex: CURUPIRA detecta ataque cibernético que desliga uma subestação).
* **Geração de `ThreatEvent`:**
    * `subsystem_source`: "BOITATA"
    * `threat_type`: Ex: "cascade_risk_power_outage_impact_hospital", "infrastructure_dependency_failure"
    * `severity`: Calculada com base na criticidade dos ativos secundários afetados.
    * `location`: Pode ser a localização do ativo primário ou uma área geral impactada.
    * `metadata`: Detalhes como `{'primary_failure': 'Subestacao_A', 'affected_dependents': ['Hospital_X', 'EstacaoBombeamento_Y']}`.
    * `origin_sensor_id`: "simulated_infrastructure_status_feed".

### Pontos de Integração Chave com Outros Subsistemas (Conceitual para MVP)

* **CURUPIRA:** O BOITATÁ pode receber informações do CURUPIRA sobre ameaças a componentes de infraestrutura que podem levar a falhas (BOITATÁ analisa a cascata).
* **SACI:** Incêndios reportados pelo SACI podem ser a causa de uma falha primária em infraestrutura que o BOITATÁ analisará.
* **IARA:** Falhas em infraestrutura (ex: falta de energia em hospitais, falha no tratamento de água) podem agravar riscos epidemiológicos, informação que o OAC pode usar para correlacionar alertas do BOITATÁ e IARA.
* **ANHANGÁ:** O BOITATÁ pode identificar que uma falha em cascata afetará a infraestrutura de comunicação, informação que o OAC passaria ao ANHANGÁ.

### Fases de Implementação Sugeridas para o MVP

1.  **Fase 1: Modelagem de Dados e Dependências:**
    * Definir uma estrutura de dados simples para representar 5-10 ativos de infraestrutura e suas dependências diretas em uma cidade hipotética.
    * Especificar o formato do `ThreatEvent` de risco de cascata.
2.  **Fase 2: Implementação do Simulador e Analisador:**
    * Desenvolver o `SimuladorFalhaPrimaria` para marcar um ativo como "falho".
    * Implementar o `AnalisadorImpactoCascataNivel1` para percorrer as dependências diretas do ativo falho.
3.  **Fase 3: Geração de Alertas e Simulação:**
    * Criar o `GeradorAlertaCascataBOITATA`.
    * Executar simulações: introduzir uma falha e verificar se os alertas de impacto em cascata corretos são gerados e enviados (mock) para o OAC.

---

## <a name="anhanga-mvp"></a>📡 ANHANGÁ - Aliança Nacional Híbrida para Garantia de Atividades de Comunicação

**Inspiração Folclórica Breve:** Anhangá é um espírito protetor, muitas vezes associado à natureza e aos caminhos. No Sistema Guardião, ANHANGÁ protege os "caminhos da informação", garantindo a comunicação mesmo em crises.

### Objetivos Principais para um MVP

* **Funcionalidade Central Mínima:** Simular a detecção da falha de uma rede de comunicação principal (ex: internet fixa e rede celular primária) e, conceitualmente, "ativar" um canal de comunicação de emergência alternativo (ex: uma rede mesh simulada ou um sistema de rádio de emergência) para transmitir uma mensagem crítica.
* **Problema Principal a Validar:** O conceito de switching para uma rede de backup e o roteamento básico de uma mensagem prioritária quando a infraestrutura primária falha.

### Componentes/Módulos de Software Chave (Conceitual)

* `MonitorRedePrincipalSimulada`: Módulo que simula o status da rede de comunicação principal (operacional, degradada, offline).
* `GerenciadorRedeEmergenciaConceitual`: Lógica que "decide" ativar a rede de emergência com base no status da rede principal e na prioridade das mensagens pendentes.
* `RoteadorMensagemEmergenciaSimulado`: Simula o envio de uma mensagem através do canal de emergência "ativado".
* `FilaMensagensPrioritarias`: Uma fila para armazenar mensagens que precisam ser transmitidas.

### Fontes de Dados e Entradas (Inputs) para o MVP

* **Status da Rede Principal Simulado:** Um input que alterna o estado da rede principal (ex: de "ONLINE" para "OFFLINE").
* **Mensagens de Emergência Simuladas:** Uma ou mais mensagens com diferentes níveis de prioridade, originadas (conceitualmente) por outros subsistemas via OAC. (Referenciar `emergency_messages` de `docs/DATA_MODELS.md`).

### Saídas e Ações (Outputs) do MVP

* **Notificação de Ativação de Rede de Emergência:** Um `ThreatEvent` ou log para o OAC informando que a rede de emergência foi "ativada".
* **Confirmação de Transmissão (Simulada):** Log indicando que uma mensagem prioritária foi "roteada" pela rede de emergência.
* **Status da Rede:** Reportar ao OAC o status atual das redes (principal e de emergência).

### Lógica Central / IA Básica para o MVP

* **Sistema de Regras para Ativação e Roteamento:**
    * `REGRA_1`: SE (Status_Rede_Principal == "OFFLINE") E (FilaMensagensPrioritarias.contem_mensagem_critica()) ENTÃO `GerenciadorRedeEmergenciaConceitual.ativar()`.
    * `REGRA_2`: SE (`GerenciadorRedeEmergenciaConceitual.status_rede_emergencia()` == "ATIVA") E (FilaMensagensPrioritarias.tem_mensagens()) ENTÃO `RoteadorMensagemEmergenciaSimulado.enviar(FilaMensagensPrioritarias.proxima_mensagem())`.
* O MVP não implementará redes mesh auto-organizáveis complexas ou roteamento inteligente com NLP. Focará na lógica de decisão de switching e na simulação do envio.

### Interação Conceitual com `GuardianCentralOrchestrator`

* **Recebimento de Tarefas/Eventos:** O OAC envia mensagens (com metadados de prioridade e destino) para o ANHANGÁ para transmissão. O OAC também pode informar sobre falhas de rede detectadas por outros meios.
* **Geração de `ThreatEvent`:**
    * `subsystem_source`: "ANHANGA"
    * `threat_type`: Ex: "primary_communication_failure", "emergency_network_activated", "message_routed_via_backup_net"
    * `severity`: Pode variar. Ex: Falha da rede primária pode ser alta severidade.
    * `location`: Região afetada pela falha de comunicação.
    * `metadata`: Detalhes como `{'rede_principal_status': 'OFFLINE', 'rede_emergencia_status': 'ATIVA', 'ultima_mensagem_roteada_id': 'msg_001'}`.
    * `origin_sensor_id`: "simulated_network_monitor_feed".

### Pontos de Integração Chave com Outros Subsistemas (Conceitual para MVP)

* **Todos os Subsistemas (via OAC):** ANHANGÁ é o canal final para disseminação de alertas e comunicados críticos gerados por SACI, IARA, CURUPIRA, BOITATÁ quando as redes normais falham. O OAC priorizará e encaminhará essas mensagens.

### Fases de Implementação Sugeridas para o MVP

1.  **Fase 1: Definição de Mensagens e Estados de Rede:**
    * Modelar a estrutura de uma mensagem de emergência (conteúdo, prioridade, destinatário simulado).
    * Definir os estados simulados para a rede principal e de emergência.
    * Especificar os `ThreatEvents` que o ANHANGÁ MVP gerará.
2.  **Fase 2: Implementação da Lógica de Ativação e Fila:**
    * Desenvolver o `MonitorRedePrincipalSimulada`.
    * Implementar a `FilaMensagensPrioritarias`.
    * Implementar a lógica simples no `GerenciadorRedeEmergenciaConceitual` para "ativar" a rede de backup.
3.  **Fase 3: Simulação de Roteamento e Geração de Alertas:**
    * Implementar o `RoteadorMensagemEmergenciaSimulado` para processar mensagens da fila.
    * Testar o fluxo: simular falha da rede principal, chegada de mensagem prioritária, ativação da rede de emergência, "envio" da mensagem e geração do `ThreatEvent` para o OAC.

---

Este plano conceitual visa guiar os primeiros passos no desenvolvimento dos MVPs para CURUPIRA, IARA, BOITATÁ e ANHANGÁ, permitindo a validação de suas propostas de valor centrais dentro do ecossistema do Sistema Guardião.