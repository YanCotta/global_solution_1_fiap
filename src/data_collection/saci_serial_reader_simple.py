#!/usr/bin/env python3
"""
Versão simplificada do SACISerialReader para testes
Remove problemas de sintaxe nas docstrings mantendo funcionalidade essencial
"""

import re
from typing import Optional, Tuple

class SACISerialReader:
    """Leitor e parser de dados seriais do ESP32 para o subsistema SACI"""
    
    def __init__(self):
        """Inicializa o leitor serial com regex para parsing de dados"""
        # Regex pattern para parsing de dados do formato esperado:
        # "Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL"
        self.sensor_data_pattern = re.compile(
            r'Temp:\s*(\S+)\s*C,\s*Hum:\s*(\S+)\s*%,\s*Smoke:\s*(\S+)(?:,\s*Risk:\s*(\S+))?',
            re.IGNORECASE
        )

    def _parse_value(self, value_str: str, target_type):
        """Helper para fazer parse de valores individuais, tratando ERROR"""
        if not value_str or value_str.upper() == 'ERROR':
            return None
        try:
            return target_type(value_str)
        except (ValueError, TypeError):
            return None

    def parse_sensor_data(self, line: str) -> Optional[Tuple[float, float, int, str]]:
        """
        Faz parse de uma linha de dados do sensor ESP32
        
        Formato esperado: "Temp: XX.X C, Hum: XX.X %, Smoke: XXXX, Risk: LEVEL"
        
        Returns:
            Tupla (temperatura, umidade, smoke_level, risk_level) ou None se parse falhar
        """
        if not line or not line.strip():
            return None
            
        line_stripped = line.strip()
        
        # Approach mais simples: buscar por palavras-chave específicas
        try:
            # Extrai temperatura
            temp_match = re.search(r'Temp:\s*(\S+)\s*C', line_stripped, re.IGNORECASE)
            temp_str = temp_match.group(1) if temp_match else None
            
            # Extrai umidade  
            hum_match = re.search(r'Hum:\s*(\S+)\s*%', line_stripped, re.IGNORECASE)
            hum_str = hum_match.group(1) if hum_match else None
            
            # Extrai smoke
            smoke_match = re.search(r'Smoke:\s*(\S+?)(?:,|$)', line_stripped, re.IGNORECASE)
            smoke_str = smoke_match.group(1) if smoke_match else None
            
            # Extrai risk
            risk_match = re.search(r'Risk:\s*(\S+?)(?:,|$)', line_stripped, re.IGNORECASE)
            risk_str = risk_match.group(1) if risk_match else "UNKNOWN"
            
            # Se não conseguiu extrair pelo menos temp, hum ou smoke, falha
            if not temp_str and not hum_str and not smoke_str:
                return None
            
            # Parse dos valores numéricos
            temperature = self._parse_value(temp_str, float)
            humidity = self._parse_value(hum_str, float)  
            smoke_level = self._parse_value(smoke_str, int)
            
            return (temperature, humidity, smoke_level, risk_str)
            
        except Exception as e:
            print(f"[ERROR] Erro processando linha '{line_stripped}': {e}")
            return None

def main():
    """Função principal para testes básicos"""
    reader = SACISerialReader()
    
    # Casos de teste básicos
    test_cases = [
        "Temp: 22.0 C, Hum: 65.0 %, Smoke: 150, Risk: MINIMAL",
        "Temp: 38.0 C, Hum: 25.0 %, Smoke: 700, Risk: HIGH",
        "Temp: ERROR C, Hum: 45.0 %, Smoke: 300, Risk: N/A",
        "Temp: 25.0 C, Hum: ERROR %, Smoke: ERROR, Risk: MEDIUM",
        "Invalid line format",
        "Temp: C, Hum: %, Smoke: , Risk:"
    ]
    
    print("=== Teste do SACISerialReader Simplificado ===")
    for i, test_line in enumerate(test_cases, 1):
        print(f"\nTeste {i}: {test_line}")
        result = reader.parse_sensor_data(test_line)
        if result:
            temp, hum, smoke, risk = result
            print(f"  Resultado: Temp={temp}°C, Hum={hum}%, Smoke={smoke}, Risk={risk}")
        else:
            print("  Resultado: Parse falhou (None)")

if __name__ == "__main__":
    main()
