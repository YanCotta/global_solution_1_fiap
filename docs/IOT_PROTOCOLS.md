# Protocolos de Comunicação IoT - Sistema Guardião

Este documento descreve os protocolos de comunicação IoT (Internet das Coisas) planejados para o Sistema Guardião, com foco inicial no MVP do SACI e sua rede de sensores ESP32.

## 1. Visão Geral da Comunicação IoT

A camada de IoT do Sistema Guardião envolve uma vasta rede de sensores distribuídos geograficamente para monitorar diversas condições (ambientais, de infraestrutura, de saúde, etc.). A escolha dos protocolos de comunicação é crucial para garantir:

- **Confiabilidade:** Entrega garantida de dados críticos.
- **Eficiência Energética:** Especialmente para dispositivos alimentados por bateria.
- **Escalabilidade:** Capacidade de suportar milhões de dispositivos.
- **Segurança:** Proteção contra acesso não autorizado e adulteração de dados.
- **Baixa Latência:** Para resposta rápida a eventos críticos.
- **Custo-efetividade:** Tanto em termos de hardware quanto de transmissão de dados.

## 2. Protocolos Primários para o MVP SACI (Sensores ESP32)

O MVP do SACI utilizará sensores baseados em ESP32 para detecção de incêndios. Os seguintes protocolos são considerados:

### 2.1. MQTT (Message Queuing Telemetry Transport)

- **Descrição:** Protocolo leve de publicação/assinatura (pub/sub) sobre TCP/IP. Ideal para comunicação de muitos-para-um (sensores para um broker central).
- **Uso no SACI:**
  - Sensores ESP32 publicarão dados (temperatura, umidade, fumaça, nível de bateria, status) em tópicos MQTT.
  - Um broker MQTT (ex: Mosquitto, definido no `docker-compose.yml`) receberá essas mensagens.
  - Um conector Kafka (ou um serviço customizado) consumirá as mensagens do broker MQTT e as encaminhará para o Apache Kafka para processamento pelo subsistema SACI e OAC.
- **Tópicos MQTT (Exemplo):**
  - `saci/sensors/{sensor_id}/data` (e.g., `saci/sensors/esp32-001A/data`)
  - `saci/sensors/{sensor_id}/status`
  - `saci/sensors/{sensor_id}/alerts`
- **Payload:** JSON ou formato binário eficiente (ex: Protocol Buffers) para minimizar o tamanho da mensagem.
  - Exemplo JSON: `{"timestamp": "2025-05-28T10:00:00Z", "temp": 28.5, "humidity": 60.2, "smoke_ppm": 450}`
- **Segurança:** MQTT sobre TLS (MQTTS) para criptografar a comunicação. Autenticação de dispositivos no broker (tokens, certificados).
- **QoS (Quality of Service):**
  - QoS 0 (At most once): Para dados não críticos, como leituras de status periódicas.
  - QoS 1 (At least once): Para dados de sensores e alertas, garantindo que cheguem ao broker.
  - QoS 2 (Exactly once): Pode ser considerado para comandos críticos, se houver comunicação bidirecional.

### 2.2. LoRaWAN (Long Range Wide Area Network) - Para Expansão Futura ou Áreas Remotas

- **Descrição:** Protocolo de camada MAC para redes de área ampla e baixa potência (LPWAN). Permite comunicação de longo alcance (vários quilômetros) com baixo consumo de energia.
- **Uso no SACI (Potencial):**
  - Em áreas rurais ou sem cobertura WiFi/celular confiável, os ESP32 podem ser equipados com módulos LoRa (ex: E32).
  - Os dispositivos LoRa (End Nodes) enviam dados para Gateways LoRaWAN.
  - Gateways encaminham os dados para um Network Server (ex: The Things Network, ChirpStack).
  - O Network Server integra com a plataforma Guardião via MQTT ou HTTP push.
- **Vantagens:** Alcance, baixo consumo, ideal para sensores dispersos.
- **Desvantagens:** Baixa taxa de transferência de dados, limitações no tamanho do payload, latência maior que WiFi/MQTT direto.

### 2.3. HTTP/HTTPS - Para Configuração e Firmware OTA

- **Descrição:** Protocolo padrão da web.
- **Uso no SACI:**
  - Os ESP32 podem usar HTTP/HTTPS para buscar atualizações de firmware Over-The-Air (OTA) de um servidor central.
  - Para configuração inicial ou diagnósticos, se uma interface web embarcada for implementada no ESP32 (menos provável para sensores de campo).

## 3. Outros Protocolos Considerados para o Sistema Guardião Completo

### 3.1. CoAP (Constrained Application Protocol)

- **Descrição:** Protocolo web para dispositivos e redes com restrições (baixo consumo, baixa largura de banda). Usa UDP e tem semelhanças com HTTP (RESTful).
- **Potencial Uso:** Para dispositivos IoT ainda mais restritos que os ESP32, ou em redes 6LoWPAN.

### 3.2. AMQP (Advanced Message Queuing Protocol)

- **Descrição:** Protocolo de mensageria mais robusto que MQTT, com mais funcionalidades de roteamento e garantia de entrega.
- **Potencial Uso:** Para comunicação entre backends ou integrações empresariais, mas geralmente não diretamente em dispositivos IoT de ponta devido ao seu overhead.

### 3.3. gRPC (Google Remote Procedure Call)

- **Descrição:** Framework de RPC de alta performance. Usa HTTP/2 para transporte e Protocol Buffers como linguagem de descrição de interface.
- **Potencial Uso:** Para comunicação interna entre microserviços do Sistema Guardião, incluindo aqueles que processam dados de IoT. Pode ser usado para comunicação entre gateways IoT e o backend.

## 4. Segurança em Protocolos IoT

A segurança é primordial:

- **Autenticação de Dispositivos:** Cada dispositivo IoT deve ser autenticado antes de poder enviar dados (certificados X.509, tokens, chaves pré-compartilhadas).
- **Criptografia em Trânsito:** Uso de TLS/DTLS (para CoAP) para proteger os dados durante a transmissão.
- **Criptografia em Repouso:** Dados armazenados nos dispositivos (se houver) e no backend devem ser criptografados.
- **Firmware Seguro:** Assinatura de firmware para OTA, verificação de integridade.
- **Segmentação de Rede:** Isolar redes IoT de outras redes corporativas.
- **Mínimo Privilégio:** Dispositivos devem ter apenas as permissões necessárias.

## 5. Gerenciamento de Dispositivos IoT

Uma plataforma de gerenciamento de dispositivos IoT será necessária para:

- Provisionamento e descomissionamento de dispositivos.
- Monitoramento de status e saúde dos dispositivos.
- Atualizações de firmware OTA.
- Gerenciamento de configurações.

## Conclusão

Para o MVP do SACI, **MQTT sobre TLS** será o protocolo primário para a coleta de dados dos sensores ESP32, com integração ao Apache Kafka. **HTTP/HTTPS** será usado para atualizações OTA. **LoRaWAN** é uma forte consideração para expansão futura em áreas apropriadas. A escolha de protocolos será continuamente avaliada com base nos requisitos de cada subsistema e na evolução da tecnologia IoT.
