# SISTEMA GUARDIÃO - ESPECIFICAÇÕES DE DASHBOARD
## Dashboard Executivo e Visualizações Especializadas

**Documento:** Especificações Técnicas de Interface  
**Data:** Junho 2025 - Dia 6  
**Versão:** 1.0  
**Status:** Especificação para Implementação  

---

## 🎯 VISÃO GERAL DO SISTEMA DE DASHBOARDS

O Sistema Guardião utiliza uma abordagem **multi-camada** para visualização de dados, oferecendo desde uma visão executiva consolidada até dashboards especializados para cada subsistema. A arquitetura de interface é projetada para **tomada de decisão ágil** em situações de crise e **monitoramento preventivo** contínuo.

### Princípios de Design
- **Clareza Visual**: Informações críticas imediatamente identificáveis
- **Hierarquia de Informação**: Dados mais críticos em destaque visual
- **Responsividade Situacional**: Interface se adapta ao nível de criticidade
- **Acessibilidade**: Compatível com diferentes dispositivos e necessidades
- **Identidade Cultural**: Elementos visuais inspirados no folclore brasileiro

---

## 🖥️ GUARDIÃO DASHBOARD EXECUTIVO (GuardianDashboard.jsx)

### Layout Principal
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER: Sistema Guardião | Status Nacional | [Alertas: 3]  │
├─────────────────────────┬───────────────────────────────────┤
│                         │  SystemStatus                     │
│      ThreatMap          │  ┌─ SACI: ●Operacional            │
│    (Mapa Principal)     │  ├─ CURUPIRA: ●Operacional        │
│                         │  ├─ IARA: ⚠️Degradado             │
│                         │  ├─ BOITATÁ: ●Operacional         │
│                         │  └─ ANHANGÁ: ●Operacional         │
│                         ├───────────────────────────────────┤
│                         │  AlertCenter                      │
│                         │  🔴 Surto H1N1 - São Paulo       │
│                         │  🟡 Falha Rede - Brasília        │
│                         │  🟢 Manutenção - Rio de Janeiro   │
└─────────────────────────┴───────────────────────────────────┘
```

### 1. ThreatMap (Componente Principal - 70% da tela)

#### 1.1 Dados Visualizados
**Eventos por Subsistema:**
```javascript
const eventTypes = {
  SACI: {
    icon: "🔥",
    colors: {
      baixo: "#4CAF50",    // Verde
      medio: "#FF9800",    // Laranja
      alto: "#F44336",     // Vermelho
      critico: "#9C27B0"   // Roxo pulsante
    },
    dados: ["temperatura", "umidade", "fumaca", "vento"]
  },
  CURUPIRA: {
    icon: "🛡️",
    colors: {
      seguro: "#4CAF50",
      suspeito: "#FF9800",
      comprometido: "#F44336",
      breach: "#9C27B0"
    },
    dados: ["ips_ataques", "vulnerabilidades", "tentativas_invasao"]
  },
  IARA: {
    icon: "🏥",
    colors: {
      normal: "#4CAF50",
      atencao: "#FF9800",
      alerta: "#F44336",
      surto: "#9C27B0"
    },
    dados: ["casos_reportados", "r_naught", "ocupacao_uti"]
  },
  BOITATA: {
    icon: "⚡",
    colors: {
      estavel: "#4CAF50",
      sobrecarga: "#FF9800",
      falha_local: "#F44336",
      cascata: "#9C27B0"
    },
    dados: ["consumo_energia", "pressao_agua", "trafego_rede"]
  },
  ANHANGA: {
    icon: "📡",
    colors: {
      operacional: "#4CAF50",
      degradado: "#FF9800",
      falha: "#F44336",
      isolamento: "#9C27B0"
    },
    dados: ["latencia", "disponibilidade", "capacidade"]
  }
}
```

#### 1.2 Interações por Evento (Hover/Click)
**Painel de Detalhes do Evento:**
```yaml
Informações_Basicas:
  - event_id: "SACI-2025060601-001"
  - timestamp: "2025-06-01 14:23:45 BRT"
  - subsistema: "SACI"
  - tipo_evento: "Risco Alto de Incêndio"
  - severidade: "ALTO"
  - coordenadas: [-23.5505, -46.6333]
  - endereco: "Parque Ibirapuera, São Paulo - SP"

Detalhes_Tecnicos:
  - origem_sensor: "SACI-SP-IBR-001"
  - confiabilidade: "94.2%"
  - correlacao_historica: "12 eventos similares"
  - fatores_contribuintes: 
    - temperatura: "32.5°C (+8°C normal)"
    - umidade: "25% (-40% normal)"
    - vento: "25 km/h direção NE"

Impacto_Estimado:
  - raio_afetado: "2.5 km"
  - populacao_em_risco: "~45.000 pessoas"
  - infraestrutura_critica: "Hospital Sírio-Libanês, Colégio São Luís"
  - tempo_resposta_necessario: "< 15 minutos"

Acoes_Sugeridas:
  - primaria: "Notificar Corpo de Bombeiros"
  - secundaria: "Ativar protocolo evacuação preventiva"
  - preventiva: "Aumentar monitoramento área adjacente"
```

#### 1.3 Indicadores Visuais de Severidade
```css
/* Animations for severity levels */
.evento-baixo { 
  opacity: 0.7; 
  animation: none; 
}

.evento-medio { 
  opacity: 0.85; 
  animation: glow-medium 3s ease-in-out infinite; 
}

.evento-alto { 
  opacity: 1; 
  animation: glow-high 2s ease-in-out infinite;
  box-shadow: 0 0 20px rgba(244, 67, 54, 0.6);
}

.evento-critico { 
  opacity: 1; 
  animation: pulse-critical 1s ease-in-out infinite;
  box-shadow: 0 0 30px rgba(156, 39, 176, 0.8);
  z-index: 1000;
}
```

#### 1.4 Camadas e Filtros do Mapa
**Controles de Camada:**
```javascript
const mapLayers = {
  eventos: {
    subsistemas: ["SACI", "CURUPIRA", "IARA", "BOITATA", "ANHANGA"],
    severidades: ["BAIXO", "MEDIO", "ALTO", "CRITICO"],
    timeRange: "1h | 6h | 24h | 7d | 30d"
  },
  infraestrutura: {
    hospitais: true,
    escolas: true,
    delegacias: true,
    bombeiros: true,
    energia: false,
    agua: false,
    telecom: false
  },
  demograficos: {
    densidade_populacional: false,
    vulnerabilidade_social: false,
    faixa_etaria_risco: false
  },
  ambientais: {
    topografia: false,
    cobertura_vegetal: false,
    corpos_agua: false,
    condicoes_meteorologicas: true
  }
}
```

### 2. SystemStatus (Painel Lateral Direito - 30% superior)

#### 2.1 Status por Subsistema
```yaml
SACI_Status:
  indicador_visual: "●" # Verde/Amarelo/Vermelho
  status_operacional: "OPERACIONAL"
  alertas_ativas: 3
  kpi_principal: 
    metrica: "Área de Cobertura em Alto Risco"
    valor: "12.3%"
    tendencia: "↑" # Aumentando
  ultima_atualizacao: "há 23 segundos"

CURUPIRA_Status:
  indicador_visual: "●"
  status_operacional: "OPERACIONAL"
  alertas_ativas: 0
  kpi_principal:
    metrica: "Ativos Críticos Sob Ameaça"
    valor: "0"
    tendencia: "→" # Estável

IARA_Status:
  indicador_visual: "⚠️"
  status_operacional: "DEGRADADO"
  alertas_ativas: 1
  kpi_principal:
    metrica: "R₀ Estimado (Maior Ameaça)"
    valor: "1.4"
    tendencia: "↓" # Diminuindo
  detalhes_degradacao: "3 sensores offline em Manaus"

BOITATA_Status:
  indicador_visual: "●"
  status_operacional: "OPERACIONAL"
  alertas_ativas: 2
  kpi_principal:
    metrica: "Resiliência da Rede"
    valor: "87.2%"
    tendencia: "→"

ANHANGA_Status:
  indicador_visual: "●"
  status_operacional: "OPERACIONAL"  
  alertas_ativas: 1
  kpi_principal:
    metrica: "Disponibilidade Comunicações"
    valor: "99.1%"
    tendencia: "→"
```

#### 2.2 Status Agregado do Sistema
```yaml
Sistema_Guardiao_Geral:
  status_global: "OPERACIONAL COM ATENÇÃO"
  nivel_prontidao: "AMARELO" # Verde/Amarelo/Vermelho
  subsistemas_operacionais: 4/5
  eventos_em_monitoramento: 47
  resposta_media_alertas: "2.3 minutos"
  confiabilidade_sistema: "94.7%"
  capacidade_processamento: "67% utilizada"
```

### 3. AlertCenter (Painel Lateral Direito - 30% inferior)

#### 3.1 Tipologia de Alertas
```javascript
const alertTypes = {
  // Alertas de Sistema
  SISTEMA_CRITICO: {
    icon: "🔴",
    priority: 1,
    exemplo: "Falha crítica no servidor principal IARA"
  },
  
  // Alertas Multi-Sistema  
  CORRELACAO_ALTA: {
    icon: "🟠", 
    priority: 2,
    exemplo: "Surto epidêmico coincide com falha comunicações"
  },
  
  // Alertas de Threshold
  LIMITE_EXCEDIDO: {
    icon: "🟡",
    priority: 3,
    exemplo: "Temperatura 15°C acima da média sazonal"
  },
  
  // Alertas Informativos
  MANUTENCAO_PROGRAMADA: {
    icon: "🔵",
    priority: 4,
    exemplo: "Manutenção preventiva sensores SACI - Zona Sul"
  }
}
```

#### 3.2 Lógica de Priorização
```python
def calcular_prioridade_alerta(evento):
    """
    Algoritmo de priorização baseado em múltiplos fatores
    """
    score = 0
    
    # Severidade do evento
    score += evento.severidade * 25
    
    # Número de subsistemas envolvidos
    score += len(evento.subsistemas) * 15
    
    # População potencialmente afetada
    score += min(evento.populacao_afetada / 1000, 50)
    
    # Velocidade de propagação
    if evento.cascata_potencial:
        score += 30
    
    # Infraestrutura crítica afetada
    score += len(evento.infraestrutura_critica) * 10
    
    # Capacidade de resposta disponível
    score -= evento.recursos_disponiveis * 5
    
    return min(score, 100)
```

#### 3.3 Layout dos Alertas
```yaml
Alerta_Exemplo:
  layout_visual:
    header:
      - timestamp: "14:23"
      - severidade_badge: "🔴 CRÍTICO"
      - subsistemas_involved: "[IARA][ANHANGA]"
    
    corpo_principal:
      - titulo: "Surto H1N1 Detectado - São Paulo"
      - resumo_localizacao: "Zona Leste, 15 bairros afetados"
      - estatisticas_chave: "847 casos | R₀: 2.1 | Crescimento: +45%/dia"
    
    acoes_rapidas:
      - botao_reconhecer: "✓ Reconhecer"
      - botao_detalhes: "📊 Ver Detalhes"
      - botao_escalar: "⚠️ Escalar para NOC"
      - botao_recursos: "🚑 Mobilizar Recursos"
```

---

## 📊 VISUALIZAÇÕES ESPECIALIZADAS

### 1. Mapas de Calor de Risco

#### 1.1 IARA - Risco Epidemiológico
```yaml
Mapa_Calor_IARA:
  dados_entrada:
    casos_reportados:
      - fonte: "SIVEP, e-SUS, hospitais parceiros"
      - granularidade: "bairro/distrito"
      - update_frequency: "a cada 4 horas"
    
    fatores_ambientais:
      - temperatura: "estações meteorológicas"
      - umidade: "estações meteorológicas"  
      - qualidade_ar: "sensores ambientais"
      - saneamento: "base cadastral municipal"
    
    mobilidade_populacional:
      - transporte_publico: "dados anonimizados operadoras"
      - eventos_massivos: "agenda municipal"
      - fluxo_interestadual: "dados rodovias/aeroportos"
  
  representacao_visual:
    escala_cores:
      - risco_muito_baixo: "#E8F5E8" # Verde muito claro
      - risco_baixo: "#4CAF50"      # Verde
      - risco_moderado: "#FFC107"   # Amarelo
      - risco_alto: "#FF5722"       # Laranja
      - risco_muito_alto: "#D32F2F" # Vermelho escuro
    
    resolucao_geografica: "setor censitário (IBGE)"
    atualizacao_visual: "tempo real com interpolação"
  
  filtros_interativos:
    temporal:
      - "últimas 24h | 7 dias | 30 dias | tendência"
    demograficos:
      - "0-5 anos | 6-17 anos | 18-59 anos | 60+ anos"
      - "vulnerabilidade social (alta/média/baixa)"
    patogenos:
      - "influenza | COVID-19 | dengue | zika | chikungunya"
```

#### 1.2 SACI - Risco de Incêndio
```yaml
Mapa_Calor_SACI:
  dados_entrada:
    sensores_distribuidos:
      - temperatura: "rede de sensores ESP32"
      - umidade_ar: "estações meteorológicas + sensores"
      - umidade_solo: "sensores distribuídos"
      - velocidade_vento: "estações meteorológicas"
      - fumaca_gases: "sensores de qualidade do ar"
    
    dados_satelitais:
      - ndvi: "vegetação seca/úmida (Sentinel-2)"
      - temperatura_superficie: "MODIS/Landsat"
      - focos_calor: "INPE - satélite de referência"
    
    historico_ocorrencias:
      - corpo_bombeiros: "histórico atendimentos"
      - defesa_civil: "registros de queimadas"
      - inpe: "banco de dados focos"
  
  representacao_visual:
    escala_cores:
      - sem_risco: "#E8F5E8"
      - risco_baixo: "#81C784"
      - risco_medio: "#FFB74D"
      - risco_alto: "#FF7043"
      - risco_extremo: "#F44336"
    
    elementos_adicionais:
      - direcao_vento: "setas dinâmicas"
      - areas_protegidas: "overlay especial"
      - corpos_bombeiros: "ícones de proximidade"
  
  filtros_interativos:
    temporal:
      - "tempo real | última hora | 12h | 24h"
    tipos_vegetacao:
      - "mata atlântica | cerrado | caatinga | campos"
    fatores_risco:
      - "apenas climático | apenas vegetação | combinado"
```

### 2. Grafos de Dependências Urbanas (BOITATÁ)

#### 2.1 Elementos e Estrutura
```yaml
Grafo_Dependencias:
  tipos_nos:
    energia:
      - subestacoes: {cor: "#FFC107", tamanho: "grande"}
      - linhas_transmissao: {cor: "#FF9800", tamanho: "medio"}
      - geradores_backup: {cor: "#4CAF50", tamanho: "pequeno"}
    
    agua_saneamento:
      - etas: {cor: "#2196F3", tamanho: "grande"}
      - reservatorios: {cor: "#03A9F4", tamanho: "medio"}
      - bombas_recalque: {cor: "#00BCD4", tamanho: "pequeno"}
    
    telecomunicacoes:
      - centrais_telefonia: {cor: "#9C27B0", tamanho: "grande"}
      - torres_celular: {cor: "#E91E63", tamanho: "medio"}
      - repetidoras: {cor: "#F06292", tamanho: "pequeno"}
    
    servicos_essenciais:
      - hospitais: {cor: "#F44336", tamanho: "grande"}
      - escolas: {cor: "#795548", tamanho: "medio"}
      - delegacias: {cor: "#607D8B", tamanho: "medio"}
  
  tipos_arestas:
    dependencia_critica: 
      - cor: "#D32F2F"
      - espessura: "4px"
      - tracejado: false
    
    dependencia_importante:
      - cor: "#FF9800" 
      - espessura: "2px"
      - tracejado: false
    
    backup_redundancia:
      - cor: "#4CAF50"
      - espessura: "2px" 
      - tracejado: true
```

#### 2.2 Visualização de Efeitos Cascata
```javascript
// Animação de propagação de falha
const simulateCascadeFailure = (nodeInicial) => {
  const animationSteps = [
    {
      tempo: 0,
      no_falho: nodeInicial,
      cor: "#F44336", // Vermelho
      efeito: "pulseFailure"
    },
    {
      tempo: 2000, // 2 segundos
      nos_afetados: getDirectDependents(nodeInicial),
      cor: "#FF9800", // Laranja  
      efeito: "rippleEffect"
    },
    {
      tempo: 5000, // 5 segundos
      nos_afetados: getSecondaryDependents(nodeInicial),
      cor: "#FFC107", // Amarelo
      efeito: "cascadeWave"
    },
    {
      tempo: 10000, // 10 segundos
      nos_recuperados: getBackupActivated(nodeInicial),
      cor: "#4CAF50", // Verde
      efeito: "recoveryPulse"
    }
  ];
  
  return animationSteps;
};
```

#### 2.3 Informações Detalhadas por Nó
```yaml
Exemplo_No_Hospital:
  informacoes_basicas:
    nome: "Hospital das Clínicas - São Paulo"
    tipo: "Serviço Essencial - Saúde"
    codigo: "BOITATA-SP-HC-001"
    coordenadas: [-23.5558, -46.6566]
  
  status_operacional:
    energia: "NORMAL (100%)"
    agua: "NORMAL"
    telecomunicacoes: "DEGRADADO (75%)"
    equipamentos_criticos: "OPERACIONAL"
  
  dependencias_diretas:
    energia:
      - fonte_principal: "Subestação Vila Madalena"
      - backup_nivel1: "Gerador diesel 2000kVA"
      - backup_nivel2: "UPS 30 minutos"
    
    agua:
      - fonte_principal: "Reservatório Consolação"
      - backup: "Cisterna interna 500m³"
    
    telecomunicacoes:
      - internet_principal: "Fibra óptica Vivo"
      - internet_backup: "Link satelital"
      - telefonia: "Central digital + backup"
  
  impacto_falha:
    populacao_diretamente_afetada: "45.000 atendimentos/mês"
    servicos_criticos: 
      - "UTI (120 leitos)"
      - "Centro cirúrgico (24 salas)"
      - "Pronto-socorro (atendimento 24h)"
    
    tempo_backup_disponivel:
      - energia: "72 horas (gerador + UPS)"
      - agua: "48 horas (cisterna)"
      - comunicacao: "ilimitado (satelital)"
```

### 3. Timeline de Eventos Correlacionados

#### 3.1 Estrutura Visual
```yaml
Timeline_Layout:
  orientacao: "horizontal"
  swimlanes:
    - CURUPIRA: {cor: "#9C27B0", posicao: "superior"}
    - IARA: {cor: "#4CAF50", posicao: "segundo"}
    - SACI: {cor: "#FF5722", posicao: "centro"}
    - BOITATA: {cor: "#2196F3", posicao: "quarto"}
    - ANHANGA: {cor: "#FF9800", posicao: "inferior"}
  
  conexoes_correlacao:
    - tipo: "causal_direta"
      visual: "linha sólida + seta"
      cor: "#F44336"
    
    - tipo: "causal_indireta"  
      visual: "linha tracejada + seta"
      cor: "#FF9800"
    
    - tipo: "temporal_coincidente"
      visual: "linha pontilhada"
      cor: "#9E9E9E"
```

#### 3.2 Exemplo de Evento Correlacionado
```yaml
Cenario_Cascata_Cibernetica:
  evento_inicial:
    timestamp: "2025-06-01 09:15:00"
    subsistema: "CURUPIRA"
    tipo: "Ataque DDoS direcionado"
    descricao: "Ataque coordenado contra infraestrutura de energia"
    severidade: "ALTO"
    localizacao: "Subestação Principal - Brasília"
  
  propagacao:
    step_1:
      timestamp: "2025-06-01 09:23:00"
      subsistema: "BOITATA"
      tipo: "Falha cascata energia"
      descricao: "Sobrecarga por redistribuição automática"
      correlacao: "causal_direta"
      
    step_2:
      timestamp: "2025-06-01 09:45:00" 
      subsistema: "ANHANGA"
      tipo: "Perda comunicação"
      descricao: "Torres celular sem energia backup"
      correlacao: "causal_direta"
      
    step_3:
      timestamp: "2025-06-01 10:12:00"
      subsistema: "IARA"
      tipo: "Falha reportagem casos"
      descricao: "Hospitais sem conectividade para notificação"
      correlacao: "causal_indireta"
      
    step_4:
      timestamp: "2025-06-01 11:30:00"
      subsistema: "SACI"
      tipo: "Detecção comprometida"
      descricao: "Sensores sem comunicação com central"
      correlacao: "causal_indireta"
  
  resolucao:
    timestamp: "2025-06-01 14:45:00"
    acao_coordenada: "Ativação protocolo recuperação distribuída"
    subsistemas_envolvidos: ["CURUPIRA", "BOITATA", "ANHANGA"]
    tempo_total_evento: "5h 30min"
```

#### 3.3 Interações para Clareza Narrativa
```javascript
const timelineInteractions = {
  zoom: {
    niveis: ["1 hora", "6 horas", "24 horas", "1 semana"],
    foco_automatico: "eventos correlacionados"
  },
  
  filtros: {
    severidade: ["CRÍTICO", "ALTO", "MÉDIO", "BAIXO"],
    subsistemas: ["selecionar múltiplos"],
    tipo_correlacao: ["causal", "temporal", "todas"]
  },
  
  detalhes_evento: {
    trigger: "click no evento",
    painel_lateral: {
      informacoes_tecnicas: true,
      acoes_tomadas: true,
      recursos_mobilizados: true,
      licoes_aprendidas: true
    }
  },
  
  narrativa_explicativa: {
    mode: "storytelling",
    elementos: [
      "resumo_textual_automatico",
      "destaque_pontos_criticos", 
      "sugestoes_prevencao_futura"
    ]
  }
}
```

---

## 🎨 CONSIDERAÇÕES DE UX/UI

### Paleta de Cores Guardião
```css
:root {
  /* Cores principais dos subsistemas */
  --saci-primary: #FF5722;
  --curupira-primary: #9C27B0;
  --iara-primary: #4CAF50;
  --boitata-primary: #2196F3;
  --anhanga-primary: #FF9800;
  
  /* Estados do sistema */
  --status-ok: #4CAF50;
  --status-warning: #FF9800; 
  --status-error: #F44336;
  --status-critical: #9C27B0;
  
  /* Fundos e neutros */
  --bg-primary: #0D1421;
  --bg-secondary: #1A2332;
  --text-primary: #FFFFFF;
  --text-secondary: #B0BEC5;
  
  /* Elementos culturais */
  --folclore-accent: #DAA520; /* Dourado */
  --terra-brasileira: #8B4513; /* Terra */
}
```

### Responsividade
```yaml
Breakpoints:
  mobile: "< 768px"
    - layout: "stack vertical"
    - mapa: "tela cheia com overlays"
    - alertas: "modal bottom sheet"
  
  tablet: "768px - 1024px" 
    - layout: "mapa principal + sidebar"
    - interacoes: "touch optimized"
  
  desktop: "1024px - 1440px"
    - layout: "three-column optimal"
    - densidade_informacao: "alta"
  
  ultrawide: "> 1440px"
    - layout: "multi-monitor support"
    - dashboards_especializados: "side-by-side"
```

### Acessibilidade
```yaml
WCAG_Compliance:
  contrast_ratio: "> 4.5:1 (AA)"
  keyboard_navigation: "full support"
  screen_readers: "ARIA labels completos"
  color_blind_support: "padrões + ícones"
  high_contrast_mode: "alternativa disponível"
  
Usabilidade_Emergencia:
  fonts: "minimum 14px, sem serifa"
  clickable_areas: "minimum 44x44px"
  loading_states: "sempre visíveis"
  error_states: "claros e acionáveis"
```

---

## 📐 MÉTRICAS DE PERFORMANCE

### Tempos de Resposta Esperados
```yaml
Performance_Targets:
  carregamento_inicial: "< 3 segundos"
  atualizacao_mapa: "< 500ms"
  filtros_aplicados: "< 200ms"
  detalhes_evento: "< 1 segundo"
  
Otimizacoes:
  mapa_base: "tile caching + CDN"
  dados_tempo_real: "WebSocket + compression"
  graficos_complexos: "canvas rendering"
  mobile_performance: "lazy loading + prefetch"
```

Esta especificação serve como base completa para a implementação dos dashboards do Sistema Guardião, fornecendo detalhes técnicos suficientes para desenvolvimento e design visual.
