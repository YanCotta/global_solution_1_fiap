# TECH STACK JUSTIFICATION - Sistema Guardião

## Filosofia Tecnológica

A seleção tecnológica do Sistema Guardião segue três princípios fundamentais:

1. **Pragmatismo Operacional:** Tecnologias maduras e amplamente adotadas para garantir estabilidade e suporte da comunidade
2. **Performance Crítica:** Escolhas otimizadas para cenários de alta demanda e baixa latência em situações de emergência
3. **Soberania Tecnológica:** Preferência por soluções open-source que garantam independência tecnológica nacional

## Justificativas para o Stack Geral do Sistema

### 1. Linguagens de Programação

#### Python 3.11+ (85% do sistema) - Linguagem Principal

**Justificativa:** Python é a escolha estratégica principal devido ao seu ecossistema robusto para IA/ML (PyTorch, HuggingFace, Scikit-learn), facilidade de desenvolvimento e prototipagem rápida, e ampla disponibilidade de desenvolvedores qualificados no Brasil.

**Casos de Uso:**
* Todos os subsistemas principais (CURUPIRA, IARA, SACI, BOITATÁ, ANHANGÁ)
* APIs REST/GraphQL
* Pipelines de ML
* Orquestração de dados
* Integração com frameworks de IA agêntica

**Vantagens Específicas:**
* Time-to-market acelerado
* Bibliotecas especializadas para cada domínio
* Facilidade de manutenção por equipes distribuídas

#### Rust (10% do sistema) - Performance Crítica

**Justificativa:** Rust será empregado em componentes onde performance extrema e segurança de memória são críticas.

**Casos de Uso:**
* Parsers de alta performance para dados de sensores
* Componentes criptográficos críticos
* Drivers de baixo nível para hardware especializado
* Módulos de processamento de stream em tempo real no Kafka

**Vantagens Específicas:**
* Zero-cost abstractions
* Memory safety sem garbage collection
* Performance comparável a C/C++ com maior segurança

#### JavaScript/TypeScript (5% do sistema) - Interface e Dashboards

**Justificativa:** TypeScript para desenvolvimento de dashboards web interativos e aplicações móveis.

**Casos de Uso:**
* Dashboard executivo
* Interfaces de controle operacional
* Aplicativo móvel para cidadãos
* Visualizações de dados em tempo real

### 2. Frameworks de IA e Machine Learning

#### PyTorch 2.0+ - Modelos Principais

**Justificativa:** PyTorch é preferido para desenvolvimento e treinamento de modelos de deep learning devido à sua flexibilidade para pesquisa, debugging intuitivo com execução eager, e forte suporte para modelos transformer.

**Casos de Uso:**
* Modelos de predição epidemiológica (IARA)
* Redes neurais para detecção de incêndios (SACI)
* Sistemas de correlação de ameaças (CURUPIRA)
* Modelos de grafo para análise de dependências (BOITATÁ)

#### TensorFlow Lite - Inferência Edge

**Justificativa:** TF Lite é otimizado para inferência em dispositivos com recursos limitados, oferecendo quantização automática e otimizações específicas para hardware embarcado.

**Casos de Uso:**
* Modelos de classificação local em sensores inteligentes
* Pré-processamento de dados na borda
* Detecção de anomalias offline

#### HuggingFace Transformers - NLP e Modelos Pré-treinados

**Justificativa:** Acesso a modelos state-of-the-art pré-treinados em português, facilidade de fine-tuning para domínios específicos.

**Casos de Uso:**
* Análise de sentimento em redes sociais (IARA)
* Processamento de documentos de inteligência (CURUPIRA)
* Classificação automática de relatórios de incidentes

### 3. Infraestrutura e Orquestração

#### Kubernetes - Orquestração de Contêineres

**Justificativa:** Kubernetes garante alta disponibilidade, escalabilidade automática, e recuperação resiliente em falhas.

**Vantagens Específicas:**
* Auto-healing de serviços
* Rolling updates sem downtime
* Service discovery automático
* Suporte nativo para secrets management

#### Apache Kafka - Streaming de Eventos

**Justificativa:** Kafka é o padrão de facto para streaming de dados de alta performance, oferecendo durabilidade, particionamento horizontal, e capacidade de replay de eventos.

**Casos de Uso:**
* Event sourcing entre subsistemas
* Ingestão de dados de sensores IoT
* Comunicação assíncrona do GuardianCentralOrchestrator

### 4. Persistência de Dados Multi-Modal

#### PostgreSQL + TimescaleDB - Dados Relacionais e Séries Temporais

**Justificativa:** PostgreSQL oferece robustez ACID, extensibilidade, e forte suporte para dados geoespaciais (PostGIS). TimescaleDB adiciona otimizações específicas para séries temporais.

**Casos de Uso:**
* Metadados de sensores
* Políticas de coordenação
* Inventário de ativos críticos
* Dados históricos de performance

#### Neo4j - Grafos de Dependências

**Justificativa:** Neo4j é otimizado para consultas de grafos complexos, essencial para modelar interdependências urbanas.

**Casos de Uso:**
* Análise de cascata de falhas
* Otimização de rotas de comunicação
* Mapeamento de infraestruturas críticas

#### InfluxDB - Métricas IoT de Alta Frequência

**Justificativa:** InfluxDB é especializado em dados de sensores com timestamps, oferecendo compressão otimizada e consultas de agregação temporal eficientes.

**Casos de Uso:**
* Dados de sensores ambientais
* Métricas de performance de rede
* Logs de sistema de alta frequência

## Justificativas para o SACI MVP

### Stack Simplificado para Prototipagem Rápida

#### Python com Scikit-learn - Modelos Iniciais

**Justificativa para MVP:** Scikit-learn oferece implementações robustas de algoritmos clássicos (Random Forest, SVM, Gradient Boosting) suficientes para validar a viabilidade do conceito.

**Vantagens para Prototipagem:**
* Desenvolvimento rápido
* Interpretabilidade dos modelos
* Menor overhead computacional
* Facilidade de integração com dados tabulares

**Migração Futura:** O pipeline de dados desenvolvido em Python será reutilizado quando migrarmos para PyTorch.

#### MicroPython vs Arduino C++ para ESP32

**MicroPython (Escolha Recomendada):**

*Vantagens:*
* Desenvolvimento mais rápido
* Debugging interativo via REPL
* Facilidade de modificação sem recompilação
* Sintaxe consistente com o backend Python

*Desvantagens:*
* Menor performance
* Maior consumo de memória

*Justificativa para MVP:* A facilidade de desenvolvimento supera as limitações de performance para sensores de baixa frequência.

**Arduino C++ (Alternativa para Produção):**

*Vantagens:*
* Performance máxima
* Menor consumo energético
* Controle total sobre recursos de hardware

*Desvantagens:*
* Desenvolvimento mais lento
* Debugging complexo
* Necessidade de recompilação para mudanças

### Sensores Selecionados para MVP

#### DHT22 (Temperatura e Umidade)

**Justificativa:** Sensor robusto, baixo custo, interface digital simples, adequado para condições ambientais adversas.

**Limitações Aceitáveis:** Precisão moderada (±0.5°C, ±2% RH) é suficiente para validação de conceito.

#### MQ-135 (Qualidade do Ar/Gases)

**Justificativa:** Sensor analógico de propósito geral que detecta múltiplos gases (CO2, NH3, fumaça).

**Limitações Aceitáveis:** Requer calibração manual e é sensível a variações ambientais, mas oferece indicação qualitativa suficiente para testes.

## Roadmap de Evolução Tecnológica

### Curto Prazo (MVP - 3 meses)
* MicroPython + sensores básicos + Scikit-learn
* Comunicação serial/WiFi simples
* Algoritmos de threshold estático

### Médio Prazo (Piloto - 12 meses)
* Migração para PyTorch com modelos neurais
* Sensores industriais de maior precisão
* Comunicação LoRaWAN para maior alcance

### Longo Prazo (Produção - 24+ meses)
* Firmware C++ otimizado para eficiência energética
* Sensores especializados com certificação IP67
* Edge AI com TensorFlow Lite para processamento local
