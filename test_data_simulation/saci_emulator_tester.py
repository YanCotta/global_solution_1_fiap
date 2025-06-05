#!/usr/bin/env python3
"""
Script para testar SACI MVP usando pipe do emulador ESP32
"""

import os
import sys
import subprocess
import time

# Adiciona o diretório do projeto ao Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.data_collection.saci_serial_reader_simple import SACISerialReader
from src.ml_models.saci_fire_predictor import load_model, predict_saci_fire_risk

def test_with_emulator_pipe(scenario: str = "mixed"):
    """
    Testa SACI MVP usando dados do emulador ESP32 via pipe
    """
    print(f"===== SACI MVP Test with ESP32 Emulator (Scenario: {scenario}) =====")
    
    # Carrega o modelo ML
    model_path = os.path.join(PROJECT_ROOT, 'models', 'saci_fire_risk_model.joblib')
    try:
        print("[INFO] Loading ML model...")
        model = load_model(model_path)
        print(f"[SUCCESS] Model loaded successfully")
    except Exception as e:
        print(f"[FATAL ERROR] Failed to load model: {e}")
        return False
    
    # Inicializa o leitor serial
    serial_reader = SACISerialReader()
    
    # Executa emulador e captura saída
    emulator_cmd = [
        sys.executable, 
        os.path.join(PROJECT_ROOT, 'test_data_simulation', 'esp32_emulator.py'),
        '--scenario', scenario,
        '--delay', '0'  # Sem delay para teste rápido
    ]
    
    try:
        print(f"[INFO] Starting ESP32 emulator with scenario: {scenario}")
        result = subprocess.run(emulator_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"[ERROR] Emulator failed: {result.stderr}")
            return False
            
        lines = result.stdout.strip().split('\n')
        print(f"[INFO] Received {len(lines)} lines from emulator")
        print()
        
        successful_predictions = 0
        failed_parses = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            print(f"--- Line {i} from Emulator ---")
            print(f"RAW ESP32 Output: {line}")
            
            # Parse dos dados
            parsed_data = serial_reader.parse_sensor_data(line)
            
            if parsed_data is None:
                print("[WARN] Failed to parse sensor data from emulator line")
                failed_parses += 1
                continue
                
            temp, hum, smoke, risk_level = parsed_data
            print(f"[SUCCESS] Parsed data: Temp={temp}°C, Hum={hum}%, Smoke={smoke}, Risk={risk_level}")
            
            # Verifica se temos dados válidos para predição
            if temp is None or hum is None or smoke is None:
                print("[WARN] Some sensor readings are None/ERROR - skipping ML prediction")
                continue
                
            # Executa predição ML
            try:
                predicted_label, probabilities = predict_saci_fire_risk(model, temp, hum, smoke)
                
                fire_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                no_fire_prob = probabilities[0] if len(probabilities) > 1 else (1 - probabilities[0])
                
                print(f"[ML PREDICTION] Label: {predicted_label} ({'Fire Detected' if predicted_label == 1 else 'No Fire Detected'})")
                print(f"[ML PREDICTION] Probabilities: P(No Fire)={no_fire_prob:.4f}, P(Fire)={fire_prob:.4f}")
                
                successful_predictions += 1
                
            except Exception as e:
                print(f"[ERROR] ML prediction failed: {e}")
                
            print()
        
        print(f"===== Test Summary =====")
        print(f"Total lines from emulator: {len(lines)}")
        print(f"Successful ML predictions: {successful_predictions}")
        print(f"Failed parses: {failed_parses}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Emulator timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Error running emulator: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    else:
        scenario = "mixed"
        
    success = test_with_emulator_pipe(scenario)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
