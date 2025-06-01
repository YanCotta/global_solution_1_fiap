"""
SACI Fire Prediction Model Training and Prediction Script.

This script handles the complete lifecycle of a fire risk prediction model, including:
- Loading data from a CSV file.
- Preprocessing the data: feature selection and handling missing values (if any).
- Training a classification model (primarily Logistic Regression, with provisions for others like Decision Trees if fully implemented).
- Evaluating the trained models using various metrics (accuracy, precision, recall, F1-score, confusion matrix).
- Saving the trained models to disk using joblib.
- Loading models from disk.
- Providing a function to predict fire risk based on live sensor data.
- Demonstrating the training, evaluation, saving, loading, and prediction processes.

The script is designed to be modular, with functions for each major step.
The main execution block (`if __name__ == '__main__':`) orchestrates these steps.
"""
# src/ml_models/saci_fire_predictor.py
# Machine Learning model for SACI Fire Prediction

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
# import pickle # Alternative for model saving

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a specified CSV file into a pandas DataFrame.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.

    Raises:
        FileNotFoundError: If the CSV file is not found at the specified path.
        Exception: For other potential errors during file loading.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Selects features and the target variable from the DataFrame and performs basic preprocessing.

    This version assumes a clean dataset and focuses on feature/target selection.
    The selected features are 'temperature', 'humidity', 'smoke_level'.
    The target variable is 'fire_risk_label'.

    Args:
        df (pd.DataFrame): The input DataFrame containing the raw data.

    Returns:
        tuple[pd.DataFrame, pd.Series]: A tuple containing:
            - X (pd.DataFrame): DataFrame with selected features.
            - y (pd.Series): Series representing the target variable.

    Raises:
        ValueError: If any of the specified feature or target columns are missing.
    """
    print("Preprocessing data...")
    # Check for missing values - assuming clean dataset for this task
    # print("Missing values per column before preprocessing:")
    # print(df.isnull().sum())

    features = ['temperature', 'humidity', 'smoke_level']
    target = 'fire_risk_label'

    if not all(feature in df.columns for feature in features):
        missing_cols = [feature for feature in features if feature not in df.columns]
        raise ValueError(f"One or more feature columns are missing from the DataFrame: {missing_cols}")
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' is missing from the DataFrame.")

    X = df[features].copy() # Use .copy() to avoid SettingWithCopyWarning on potential future modifications
    y = df[target].copy()
    # Assuming 'fire_risk_label' is encoded as: 0 for No Fire, 1 for Fire.
    # This should be consistent with the dataset generation process.

    # If specific imputation for selected features were needed, it would go here.
    # Example:
    # for col in X.columns:
    #     if X[col].isnull().any():
    #         X[col] = X[col].fillna(X[col].mean())

    # print("Missing values in X after potential processing:")
    # print(X.isnull().sum())
    # print("Missing values in y after potential processing:")
    # print(y.isnull().sum())
    print("Preprocessing complete.")
    return X, y

def train_logistic_regression(X_train: pd.DataFrame, y_train: pd.Series) -> LogisticRegression:
    """
    Trains a Logistic Regression model.

    Args:
        X_train (pd.DataFrame): DataFrame containing the training features.
        y_train (pd.Series): Series containing the training target variable.

    Returns:
        LogisticRegression: The trained Logistic Regression model.
    """
    model = LogisticRegression(random_state=42, solver='liblinear')
    model.fit(X_train, y_train)
    return model

def evaluate_model(model: any, X_test: pd.DataFrame, y_test: pd.Series, model_name: str) -> tuple[float, float, float, float, np.ndarray]:
    """
    Evaluates the given model using test data, prints various performance metrics,
    and returns these metrics.

    Metrics calculated: Accuracy, Precision (weighted), Recall (weighted),
                        F1-score (weighted), and Confusion Matrix.

    Args:
        model (any): The trained model object (must have `predict` method).
        X_test (pd.DataFrame): DataFrame containing the test features.
        y_test (pd.Series): Series containing the test target variable.
        model_name (str): Name of the model (e.g., "Logistic Regression") for printing.

    Returns:
        tuple[float, float, float, float, np.ndarray]: A tuple containing:
            - accuracy (float)
            - precision (float, weighted average)
            - recall (float, weighted average)
            - f1_score (float, weighted average)
            - confusion_matrix (np.ndarray)
    """
    print(f"\n--- {model_name} Evaluation ---")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    # Using average='weighted' for precision, recall, f1 as it's generally more robust
    # and was the previous setting. If binary classification with specific positive
    # class focus is needed, this might change (e.g. remove average or set pos_label)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision (weighted): {precision:.4f}")
    print(f"Recall (weighted): {recall:.4f}")
    print(f"F1-score (weighted): {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

    return accuracy, precision, recall, f1, cm

def save_model(model: any, file_path: str) -> None:
    """Saves the trained model to a file using joblib."""
    joblib.dump(model, file_path)
    print(f"Model saved to {file_path}")

def load_model(file_path: str) -> any:
    """Loads a trained model from a file using joblib."""
    model = joblib.load(file_path)
    print(f"Model loaded from {file_path}")
    return model

def predict_saci_fire_risk(model: LogisticRegression, live_temp: float, live_hum: float, live_smoke_adc: float) -> tuple[int, np.ndarray]:
    """
    Predicts fire risk label and probabilities for given live sensor data.

    Args:
        model: Trained scikit-learn classifier (e.g., LogisticRegression)
               with predict and predict_proba methods.
        live_temp: Live temperature reading (float).
        live_hum: Live humidity reading (float).
        live_smoke_adc: Live smoke sensor ADC value (float).

    Returns:
        A tuple containing:
            - predicted_label (int): The predicted class label (e.g., 0 for No Fire, 1 for Fire).
            - predicted_probability (np.ndarray): An array of probabilities for each class.
                                                 For binary classification, typically [P(class_0), P(class_1)].
    """
    input_data = pd.DataFrame(
        [[live_temp, live_hum, live_smoke_adc]],
        columns=['temperature', 'humidity', 'smoke_level']
    )
    predicted_label = model.predict(input_data)[0]
    predicted_probability = model.predict_proba(input_data)[0]
    return int(predicted_label), predicted_probability

# Further implementation will follow in subsequent steps.

if __name__ == '__main__':
    # --- Configuration: Define dataset and model file paths ---
    DATASET_PATH = 'data/synthetic/fire_risk_dataset.csv'
    LOG_REG_MODEL_PATH = 'models/saci_fire_risk_model.joblib'

    # --- Step 1: Load and Preprocess Data ---
    try:
        print("--- Initiating Data Loading and Preprocessing ---")
        data_df = load_data(DATASET_PATH)
        # Using .copy() in preprocess_data or here if data_df is reused elsewhere without modification
        X, y = preprocess_data(data_df)
        print("--- Data Loading and Preprocessing Completed ---")
    except FileNotFoundError:
        print(f"Exiting: Dataset file not found at {DATASET_PATH}. Please ensure the file exists.")
        exit(1) # Exit script if data can't be loaded
    except ValueError as ve:
        print(f"Exiting: Error during data preprocessing: {ve}")
        exit(1) # Exit if preprocessing fails (e.g., missing columns)
    except Exception as e:
        print(f"Exiting: An unexpected error occurred during data loading or preprocessing: {e}")
        exit(1) # Exit for any other unexpected errors

    # --- Step 2: Split Data into Training and Testing sets ---
    print("\n--- Splitting Data into Training and Test Sets ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set size: {X_train.shape[0]} samples")
    print(f"Test set size: {X_test.shape[0]} samples")
    print("--- Data Splitting Completed ---")

    # --- Step 3: Train and Save Logistic Regression Model ---
    print("\n--- Training Logistic Regression Model ---")
    log_reg_model = train_logistic_regression(X_train, y_train)
    print("Logistic Regression model trained successfully.")

    dir_path = os.path.dirname(LOG_REG_MODEL_PATH)
    if dir_path:  # Ensure the directory path is non-empty
        os.makedirs(dir_path, exist_ok=True)

    save_model(log_reg_model, LOG_REG_MODEL_PATH) # Save the trained model
    print("--- Logistic Regression Model Training and Saving Completed ---")

    # --- Step 5: Evaluate Models ---
    # Evaluate Logistic Regression model
    lr_accuracy, lr_precision, lr_recall, lr_f1, lr_conf_matrix = evaluate_model(
        log_reg_model, X_test, y_test, "Logistic Regression"
    )
    print(f"\nLogistic Regression weighted F1-score: {lr_f1:.4f}")


    # --- Step 7: Live Prediction Example (using Logistic Regression model) ---
    # This demonstrates using the `predict_saci_fire_risk` function with sample live data.
    # Ensure `log_reg_model` is available (trained in this script run).
    if 'log_reg_model' in locals() and log_reg_model is not None:
        sample_temp, sample_hum, sample_smoke = 30.5, 55.2, 350 # Example sensor readings

        print(f"\n--- Live Prediction Example (Using current Logistic Regression model) ---")
        # Using the directly trained log_reg_model for this example
        label, probability = predict_saci_fire_risk(log_reg_model, sample_temp, sample_hum, sample_smoke)
        print(f"Input: Temp={sample_temp}°C, Hum={sample_hum}%, Smoke ADC={sample_smoke}")
        risk_status = "Fire Detected" if label == 1 else "No Fire Detected" # Assuming 0: No Fire, 1: Fire
        print(f"Predicted Label: {label} ({risk_status})")
        if len(probability) == 2: # For binary classification
             print(f"Prediction Probabilities: [P(No Fire)={probability[0]:.4f}, P(Fire)={probability[1]:.4f}]")
        else:
            print(f"Prediction Probabilities: {probability}") # For multi-class or other cases

    # --- Step 8: Prediction with Loaded Model Example ---
    # This demonstrates loading a saved model and using it for prediction.
    # It uses the `sample_temp`, `sample_hum`, `sample_smoke` defined in the previous example.
    if 'LOG_REG_MODEL_PATH' in locals() and 'sample_temp' in locals(): # Check if model path and sample data exist
        try:
            print(f"\n--- Loading Model from {LOG_REG_MODEL_PATH} for Prediction Demo ---")
            loaded_log_reg_model_for_demo = load_model(LOG_REG_MODEL_PATH) # Load the specifically saved LR model

            if loaded_log_reg_model_for_demo:
                label_loaded, prob_loaded = predict_saci_fire_risk(
                    loaded_log_reg_model_for_demo, sample_temp, sample_hum, sample_smoke
                )
                print(f"\n--- Prediction with Loaded Model ({LOG_REG_MODEL_PATH}) ---")
                print(f"Input: Temp={sample_temp}°C, Hum={sample_hum}%, Smoke ADC={sample_smoke}")
                risk_status_loaded = "Fire Detected" if label_loaded == 1 else "No Fire Detected"
                print(f"Predicted Label (from loaded model): {label_loaded} ({risk_status_loaded})")
                if len(prob_loaded) == 2:
                    print(f"Prediction Probabilities (from loaded model): [P(No Fire)={prob_loaded[0]:.4f}, P(Fire)={prob_loaded[1]:.4f}]")
                else:
                    print(f"Prediction Probabilities (from loaded model): {prob_loaded}")
        except FileNotFoundError:
            print(f"Demo Skipped: Could not load model from {LOG_REG_MODEL_PATH}. File not found.")
        except Exception as e:
            print(f"Demo Skipped: An error occurred while using the loaded model for prediction: {e}")

    # --- Script Finished ---
    print("\nSACI Fire Predictor script finished.")
