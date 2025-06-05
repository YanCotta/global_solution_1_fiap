#!/usr/bin/env python3
"""
TC7: Teste direto das funções do saci_fire_predictor.py
"""

import sys
import os

# Adiciona o diretório do projeto ao Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.ml_models.saci_fire_predictor import load_model, predict_saci_fire_risk

def test_direct_prediction():
    """Testa chamadas diretas às funções do modelo ML"""
    
    print("===== TC7: Teste Direto do saci_fire_predictor.py =====")
    
    # Carrega o modelo
    model_path = os.path.join(PROJECT_ROOT, 'models', 'saci_fire_risk_model.joblib')
    
    try:
        print(f"[INFO] Carregando modelo de: {model_path}")
        model = load_model(model_path)
        print("[SUCCESS] Modelo carregado com sucesso!")
    except Exception as e:
        print(f"[FATAL ERROR] Falha ao carregar modelo: {e}")
        return False
    
    # Casos de teste diretos
    test_cases = [
        # (temp, hum, smoke, descrição)
        (22.0, 65.0, 150, "Condições normais - baixo risco"),
        (18.0, 75.0, 80, "Condições frias e úmidas - muito baixo risco"),
        (38.0, 25.0, 700, "Condições quentes e secas - alto risco"),
        (45.0, 15.0, 850, "Condições críticas - muito alto risco"),
        (30.0, 50.0, 400, "Condições moderadas - risco médio"),
        (15.0, 80.0, 50, "Condições muito frias e úmidas - baixíssimo risco")
    ]
    
    print("\n[INFO] Executando predições diretas...")
    
    for i, (temp, hum, smoke, desc) in enumerate(test_cases, 1):
        print(f"\n--- Teste {i}: {desc} ---")
        print(f"Entrada: Temp={temp}°C, Hum={hum}%, Smoke={smoke}")
        
        try:
            predicted_label, probabilities = predict_saci_fire_risk(model, temp, hum, smoke)
            
            # Interpreta resultados
            fire_detected = predicted_label == 1
            fire_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            no_fire_prob = probabilities[0] if len(probabilities) > 1 else (1 - probabilities[0])
            
            print(f"Predição: {'🔥 FOGO DETECTADO' if fire_detected else '✅ SEM FOGO'}")
            print(f"Probabilidades: P(Sem Fogo)={no_fire_prob:.4f}, P(Fogo)={fire_prob:.4f}")
            print(f"Confiança: {max(fire_prob, no_fire_prob)*100:.1f}%")
            
        except Exception as e:
            print(f"[ERROR] Erro na predição: {e}")
    
    print(f"\n===== TC7 Concluído =====")
    return True

if __name__ == "__main__":
    success = test_direct_prediction()
    sys.exit(0 if success else 1)
