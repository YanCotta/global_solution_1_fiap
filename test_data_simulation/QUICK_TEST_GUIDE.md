# SACI MVP - Quick Test Guide

## Prerequisites
```bash
# Navigate to project root
cd /home/yan/Documents/Git/global_solution_1_fiap

# Ensure Python environment is configured and packages are installed
pip install joblib numpy pandas scikit-learn pyserial
```

## Running Individual Tests

### Test Case 1: Low Risk Data
```bash
cd test_data_simulation
python saci_file_tester.py tc1_low_risk.txt
```

### Test Case 2: High Risk Data
```bash
python saci_file_tester.py tc2_high_risk.txt
```

### Test Case 3: Error Handling
```bash
python saci_file_tester.py tc3_sensor_errors.txt
```

### Test Case 4: Malformed Data
```bash
python saci_file_tester.py tc4_malformed.txt
```

### Test Case 5: Load Testing
```bash
python saci_file_tester.py simulated_esp_output.txt
```

### Test Case 7: Direct ML Testing
```bash
python tc7_direct_predictor_test.py
```

## Live Emulation Testing
```bash
# Terminal 1: Start emulator and pipe to tester
python esp32_emulator.py | python saci_emulator_tester.py

# Or run separately:
# Terminal 1: python esp32_emulator.py > /tmp/esp_data.txt
# Terminal 2: tail -f /tmp/esp_data.txt | python saci_emulator_tester.py
```

## Model Training (if needed)
```bash
cd ..
python -c "
from src.ml_models.saci_fire_predictor import train_model
train_model()
"
```

## Expected Results Summary
- **TC1 (Low Risk)**: Prediction < 0.5, "No fire detected"
- **TC2 (High Risk)**: Prediction > 0.5, "Fire detected!"  
- **TC3 (Errors)**: Graceful handling, no crashes
- **TC4 (Malformed)**: Parsing fails safely
- **TC5 (Load)**: All lines processed
- **TC7 (Direct)**: Model functions work correctly

## Troubleshooting
- If model file missing: Run model training first
- If import errors: Check Python path and dependencies
- If parsing errors: Use the simplified parser version

## Files Created
- All test scripts in `test_data_simulation/`
- Trained model in `models/`
- Test data files: `tc1_*.txt`, `tc2_*.txt`, etc.
