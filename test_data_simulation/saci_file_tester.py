#!/usr/bin/env python3
"""
Script auxiliar para executar testes do SACI MVP com dados simulados de arquivo

Este script facilita a execução de testes lendo dados de um arquivo em vez
de uma porta serial real, simulando a funcionalidade do saci_mvp_integration_app.py
"""

import os
import sys
import argparse

# Adiciona o diretório do projeto ao Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.data_collection.saci_serial_reader_simple import SACISerialReader
from src.ml_models.saci_fire_predictor import load_model, predict_saci_fire_risk

def test_with_file_input(file_path: str, model_path: str):
    """
    Executa teste do SACI MVP lendo dados de arquivo em vez de porta serial
    
    Args:
        file_path: Caminho para arquivo com dados simulados
        model_path: Caminho para o modelo ML treinado
    """
    print("===== SACI MVP Test with File Input =====")
    print(f"Input file: {file_path}")
    print(f"Model path: {model_path}")
    print()
    
    # Carrega o modelo ML
    try:
        print("[INFO] Loading ML model...")
        model = load_model(model_path)
        print(f"[SUCCESS] Model loaded successfully from {model_path}")
    except Exception as e:
        print(f"[FATAL ERROR] Failed to load model: {e}")
        return False
    
    # Inicializa o leitor serial (mesmo parse, mas sem porta serial)
    serial_reader = SACISerialReader()
    
    # Lê e processa arquivo linha por linha
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_number = 0
            successful_predictions = 0
            failed_parses = 0
            
            for line in f:
                line_number += 1
                line = line.strip()
                
                # Pula linhas vazias ou comentários
                if not line or line.startswith('#'):
                    continue
                    
                print(f"\n--- Line {line_number} ---")
                print(f"RAW ESP32 Output: {line}")
                
                # Tenta fazer parse dos dados do sensor
                parsed_data = serial_reader.parse_sensor_data(line)
                
                if parsed_data is None:
                    print("[WARN] Failed to parse sensor data from line")
                    print("  -> Skipping ML prediction for this line")
                    failed_parses += 1
                    continue
                
                temp, hum, smoke, risk_level = parsed_data
                print(f"[SUCCESS] Parsed data: Temp={temp}°C, Hum={hum}%, Smoke={smoke}, Risk={risk_level}")
                
                # Verifica se temos dados válidos para predição ML
                if temp is None or hum is None or smoke is None:
                    print("[WARN] Some sensor readings are None/ERROR - skipping ML prediction")
                    continue
                
                # Executa predição ML
                try:
                    predicted_label, probabilities = predict_saci_fire_risk(
                        model, temp, hum, smoke
                    )
                    
                    fire_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                    no_fire_prob = probabilities[0] if len(probabilities) > 1 else (1 - probabilities[0])
                    
                    print(f"[ML PREDICTION] Label: {predicted_label} ({'Fire Detected' if predicted_label == 1 else 'No Fire Detected'})")
                    print(f"[ML PREDICTION] Probabilities: P(No Fire)={no_fire_prob:.4f}, P(Fire)={fire_prob:.4f}")
                    
                    successful_predictions += 1
                    
                except Exception as e:
                    print(f"[ERROR] ML prediction failed: {e}")
                    
    except FileNotFoundError:
        print(f"[FATAL ERROR] Input file not found: {file_path}")
        return False
    except Exception as e:
        print(f"[FATAL ERROR] Error reading input file: {e}")
        return False
    
    print(f"\n===== Test Summary =====")
    print(f"Total lines processed: {line_number}")
    print(f"Successful ML predictions: {successful_predictions}")
    print(f"Failed parses: {failed_parses}")
    print(f"Success rate: {(successful_predictions/max(1, line_number-failed_parses))*100:.1f}%")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='SACI MVP Tester with File Input')
    parser.add_argument('--input_file', '-i', 
                       default='test_data_simulation/simulated_esp_output.txt',
                       help='Path to simulated ESP32 data file')
    parser.add_argument('--model_path', '-m',
                       default='models/saci_fire_risk_model.joblib', 
                       help='Path to trained ML model')
    
    args = parser.parse_args()
    
    # Converte caminhos relativos para absolutos baseado no project root
    if not os.path.isabs(args.input_file):
        args.input_file = os.path.join(PROJECT_ROOT, args.input_file)
    if not os.path.isabs(args.model_path):
        args.model_path = os.path.join(PROJECT_ROOT, args.model_path)
    
    success = test_with_file_input(args.input_file, args.model_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
