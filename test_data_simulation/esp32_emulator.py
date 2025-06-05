#!/usr/bin/env python3
"""
ESP32 Emulator Script para testes do SACI MVP

Este script simula a saída do ESP32 com sensores DHT22 e MQ-135,
enviando dados formatados para stdout que podem ser capturados
pelo saci_mvp_integration_app.py através de pipes ou redirecionamento.

Uso:
    python3 esp32_emulator.py | python3 src/applications/saci_mvp_integration_app.py --stdin
    python3 esp32_emulator.py > /tmp/esp32_data.txt
"""

import time
import random
import sys
from typing import List, Tuple

# Cenários de dados predefinidos para testes controlados
TEST_SCENARIOS = [
    # Cenário 1: Condições normais (risco baixo)
    ("normal_low", [
        (22.0, 65.0, 150, "MINIMAL"),
        (20.5, 70.0, 100, "LOW"), 
        (18.0, 75.0, 80, "MINIMAL"),
        (24.0, 60.0, 120, "LOW")
    ]),
    
    # Cenário 2: Condições de alto risco/fogo
    ("high_risk", [
        (38.0, 25.0, 700, "HIGH"),
        (45.2, 15.0, 850, "CRITICAL"),
        (42.0, 20.0, 600, "HIGH"),
        (40.5, 18.0, 750, "CRITICAL")
    ]),
    
    # Cenário 3: Sensores com falhas (ERROR)
    ("sensor_errors", [
        ("ERROR", 45.0, 300, "N/A"),
        (25.0, "ERROR", "ERROR", "MEDIUM"),
        ("ERROR", "ERROR", 200, "UNKNOWN"),
        (30.0, "ERROR", 400, "MEDIUM")
    ]),
    
    # Cenário 4: Dados malformados
    ("malformed", [
        "Isto e uma linha completamente invalida",
        "Temp: C, Hum: %, Smoke: , Risk:",
        "Random text without any structure",
        "Temp: 25.0 C Hum: 50.0 % Smoke: 300 Risk: MEDIUM"
    ]),
    
    # Cenário 5: Misturado (dados válidos e inválidos)
    ("mixed", [
        (22.0, 65.0, 150, "MINIMAL"),
        "Invalid line here",
        (35.0, 30.0, 500, "MEDIUM"),
        ("ERROR", 50.0, 200, "LOW"),
        (40.0, 25.0, 600, "HIGH")
    ])
]

def format_sensor_reading(temp, hum, smoke, risk) -> str:
    """Formata uma leitura de sensor no formato esperado pelo ESP32"""
    if isinstance(temp, str) and temp == "ERROR":
        temp_str = "ERROR C"
    else:
        temp_str = f"{temp} C"
        
    if isinstance(hum, str) and hum == "ERROR":
        hum_str = "ERROR %"  
    else:
        hum_str = f"{hum} %"
        
    if isinstance(smoke, str) and smoke == "ERROR":
        smoke_str = "ERROR"
    else:
        smoke_str = str(smoke)
        
    return f"Temp: {temp_str}, Hum: {hum_str}, Smoke: {smoke_str}, Risk: {risk}"

def generate_random_reading() -> str:
    """Gera uma leitura aleatória de sensor"""
    temp = round(random.uniform(15.0, 50.0), 1)
    hum = round(random.uniform(10.0, 90.0), 1) 
    smoke = random.randint(50, 1000)
    
    # Determina risco baseado nos valores
    if temp > 35 and hum < 30 and smoke > 500:
        risk = "HIGH"
    elif temp > 30 and (hum < 40 or smoke > 300):
        risk = "MEDIUM"
    else:
        risk = "LOW"
        
    return format_sensor_reading(temp, hum, smoke, risk)

def emulate_esp32(scenario: str = "mixed", count: int = 10, delay: float = 1.0):
    """
    Emula saída do ESP32 baseada no cenário especificado
    
    Args:
        scenario: Nome do cenário de teste ou "random" para dados aleatórios
        count: Número de leituras a enviar (ignorado para cenários predefinidos)
        delay: Delay em segundos entre leituras
    """
    print(f"# ESP32 Emulator starting - Scenario: {scenario}", file=sys.stderr)
    print(f"# Sending data to stdout...", file=sys.stderr)
    
    if scenario == "random":
        # Gera dados aleatórios
        for i in range(count):
            reading = generate_random_reading()
            print(reading)
            sys.stdout.flush()
            if delay > 0:
                time.sleep(delay)
    else:
        # Usa cenário predefinido
        scenario_data = None
        for name, data in TEST_SCENARIOS:
            if name == scenario:
                scenario_data = data
                break
                
        if scenario_data is None:
            print(f"Error: Unknown scenario '{scenario}'", file=sys.stderr)
            print("Available scenarios:", file=sys.stderr)
            for name, _ in TEST_SCENARIOS:
                print(f"  - {name}", file=sys.stderr)
            sys.exit(1)
            
        for item in scenario_data:
            if isinstance(item, str):
                # Linha malformada
                print(item)
            else:
                # Tupla com dados do sensor
                temp, hum, smoke, risk = item
                reading = format_sensor_reading(temp, hum, smoke, risk)
                print(reading)
            
            sys.stdout.flush()
            if delay > 0:
                time.sleep(delay)

def main():
    """Função principal com parsing de argumentos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ESP32 Sensor Emulator para testes SACI MVP')
    parser.add_argument('--scenario', '-s', default='mixed',
                       help='Cenário de teste (normal_low, high_risk, sensor_errors, malformed, mixed, random)')
    parser.add_argument('--count', '-c', type=int, default=10,
                       help='Número de leituras (apenas para scenario=random)')
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                       help='Delay entre leituras em segundos')
    parser.add_argument('--list-scenarios', action='store_true',
                       help='Lista cenários disponíveis')
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        print("Cenários disponíveis:")
        for name, data in TEST_SCENARIOS:
            print(f"  {name}: {len(data)} items")
        return
        
    try:
        emulate_esp32(args.scenario, args.count, args.delay)
    except KeyboardInterrupt:
        print("\n# ESP32 Emulator stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"# Error in ESP32 Emulator: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
