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

# Standard library imports first
import os
# import pickle # Alternative for model saving - Removed as joblib is used.

# Third-party imports
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.exceptions import NotFittedError


# --- Constants ---
# Define paths at the module level for easy configuration and reference.
# These could also be loaded from a config file or environment variables.
MODELS_DIR = 'models'  # Base directory for saving trained models
# Define paths at the module level for easy configuration and reference.
# These could also be loaded from a config file or environment variables.
MODELS_DIR = 'models'  # Base directory for saving trained models
DATASET_PATH = 'data/synthetic/fire_risk_dataset.csv' # Path to the dataset
LOG_REG_MODEL_FILENAME = 'saci_fire_risk_logistic_regression_model.joblib'
# Construct full path for the model file, ensuring OS compatibility
LOG_REG_MODEL_PATH = os.path.join(MODELS_DIR, LOG_REG_MODEL_FILENAME)


def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a specified CSV file into a pandas DataFrame.

    Args:
        file_path: The path to the CSV file.

    Returns:
        The loaded data as a pandas DataFrame.

    Raises:
        FileNotFoundError: If the CSV file is not found at the specified path.
        pd.errors.EmptyDataError: If the CSV file is empty.
        Exception: For other potential I/O errors during file loading (e.g., malformed CSV).
    """
    try:
        df = pd.read_csv(file_path)
        print(f"[INFO] Data loaded successfully from '{file_path}'. Shape: {df.shape}")
        if df.empty:
            # This warning is useful; actual error handling for empty df might be needed
            # depending on downstream requirements (e.g., raising a ValueError).
            print(f"[WARN] The file '{file_path}' is empty. Further processing may fail or be vacuous.")
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found: '{file_path}'. Please ensure the path is correct.")
        raise # Re-raise to be handled by the caller, likely terminating the script
    except pd.errors.EmptyDataError: # Specific pandas error for empty CSVs
        print(f"[ERROR] No data: The file '{file_path}' is empty.")
        raise # Re-raise
    except Exception as e:
        # Catching other pandas errors (e.g., CParserError for malformed CSVs)
        # or general exceptions during file I/O.
        print(f"[ERROR] An error occurred while loading or parsing data from '{file_path}': {e}")
        raise # Re-raise

def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Selects features and the target variable, and performs basic preprocessing.

    For the MVP, this function primarily handles:
    - Selection of predefined features: 'temperature', 'humidity', 'smoke_level'.
    - Selection of the target variable: 'fire_risk_label'.
    - Validates that these columns exist in the DataFrame.
    - Validates that there are no missing (NaN) values in the selected features or target,
      as the synthetic dataset is expected to be clean and models typically cannot handle NaNs.

    Args:
        df: The input DataFrame containing the raw data.

    Returns:
        A tuple containing:
            - X (pd.DataFrame): DataFrame with selected features.
            - y (pd.Series): Series representing the target variable.

    Raises:
        ValueError: If any of the specified feature or target columns are missing,
                    or if there are any NaN values in these columns after selection.
    """
    print("[INFO] Starting data preprocessing...")

    # Define the feature set and target variable name
    features = ['temperature', 'humidity', 'smoke_level']
    target_column = 'fire_risk_label' # Changed from 'target' for clarity

    # Check if all required feature columns are present in the DataFrame
    missing_feature_cols = [col for col in features if col not in df.columns]
    if missing_feature_cols:
        raise ValueError(f"Missing feature columns in DataFrame: {missing_feature_cols}. "
                         "Ensure the dataset includes these columns.")

    # Check if the target column is present
    if target_column not in df.columns:
        raise ValueError(f"Missing target column '{target_column}' in DataFrame. "
                         "Ensure the dataset includes this column.")

    # Select features (X) and target (y)
    # Using .copy() is a good practice to avoid SettingWithCopyWarning on potential future modifications
    # of X or y, ensuring they are independent copies of the DataFrame slices.
    X = df[features].copy()
    y = df[target_column].copy()

    # Verify that there are no missing values in the selected features or target variable.
    # This is a critical check as most scikit-learn models will fail if NaNs are present.
    if X.isnull().values.any():
        nan_counts_x = X.isnull().sum()
        print(f"[WARN] Missing values found in features (X) before processing:\n{nan_counts_x[nan_counts_x > 0]}")
        # For MVP, we raise an error. In a more complex scenario, imputation might occur here.
        raise ValueError("Features (X) contain missing values after selection. "
                         "Please clean the data or implement imputation.")
    if y.isnull().values.any():
        nan_count_y = y.isnull().sum()
        print(f"[WARN] Missing values found in target (y) before processing: {nan_count_y}")
        raise ValueError("Target variable (y) contains missing values. "
                         "Please clean the data or remove rows with missing target.")

    # Assuming 'fire_risk_label' is already numerically encoded (e.g., 0 for No Fire, 1 for Fire).
    # If it were categorical (e.g., strings "Low", "High"), encoding (like LabelEncoder) would be necessary here.
    print("[INFO] Data preprocessing complete. Features and target variable are selected and validated.")
    return X, y

def train_logistic_regression(X_train: pd.DataFrame,
                              y_train: pd.Series,
                              random_state: int = 42) -> LogisticRegression:
    """
    Trains a Logistic Regression model using the provided training data.

    Args:
        X_train: DataFrame containing the training features.
        y_train: Series containing the training target variable.
        random_state: Seed for random number generation to ensure reproducibility.

    Returns:
        The trained LogisticRegression model.
    """
    print("[INFO] Training Logistic Regression model...")
    # 'liblinear' solver is suitable for small datasets and supports L1/L2 regularization.
    # 'random_state' is used to ensure that results are reproducible across runs.
    model = LogisticRegression(random_state=random_state, solver='liblinear')
    model.fit(X_train, y_train)
    print("[INFO] Logistic Regression model training completed successfully.")
    return model

def evaluate_model(model: any,
                   X_test: pd.DataFrame,
                   y_test: pd.Series,
                   model_name: str) -> tuple[float, float, float, float, np.ndarray]:
    """
    Evaluates the performance of a trained model on the provided test set.

    Calculates and prints standard classification metrics: Accuracy, Precision (weighted),
    Recall (weighted), F1-score (weighted), and the Confusion Matrix.
    The `zero_division=0` parameter in score functions handles cases where a class
    is not predicted, preventing warnings and assigning a score of 0 for that metric.

    Args:
        model: The trained model object (e.g., an instance of LogisticRegression).
               It must implement a `predict(X)` method.
        X_test: DataFrame containing the features of the test set.
        y_test: Series containing the true labels for the test set.
        model_name: A descriptive name for the model being evaluated (used in print statements).

    Returns:
        A tuple containing the calculated metrics:
            - accuracy (float)
            - precision (float, weighted average)
            - recall (float, weighted average)
            - f1 (float, weighted average)
            - cm (np.ndarray): The confusion matrix.
    """
    print(f"\n--- Evaluating Model Performance: {model_name} ---")
    y_pred = model.predict(X_test) # Predictions on the test set

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    # 'weighted' average calculates metrics for each label and finds their average,
    # weighted by the number of true instances for each label (support).
    # This accounts for label imbalance.
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred) # Confusion matrix

    # Print the calculated metrics
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision (weighted avg): {precision:.4f}")
    print(f"  Recall (weighted avg): {recall:.4f}")
    print(f"  F1-score (weighted avg): {f1:.4f}")
    print("  Confusion Matrix:")
    # A simple way to print the confusion matrix. For more detail, one might
    # print TN, FP, FN, TP if classes are known and binary.
    # Example for binary classification with labels 0 and 1:
    # Assuming model.classes_ or sorted(y_test.unique()) gives [0, 1]
    class_labels = sorted(y_test.unique()) # Get unique class labels from test set
    if len(class_labels) == cm.shape[0]: # Check if cm dimensions match unique labels
        for i, label_i in enumerate(class_labels):
            row_str = f"    Actual Class {label_i}: ["
            for j, label_j in enumerate(class_labels):
                row_str += f"Pred as {label_j}: {cm[i, j]:<4} "
            row_str += "]"
            print(row_str)
    else: # Fallback if labels are not simple or don't match CM shape
        for row in cm:
            print(f"    {row}")

    return accuracy, precision, recall, f1, cm

def save_model(model: any, file_path: str) -> None:
    """
    Saves the trained model to a specified file path using joblib for efficient serialization.
    This function also ensures that the directory for the model file exists before saving.

    Args:
        model: The trained model object to be saved (e.g., a scikit-learn estimator).
        file_path: The full path (including filename, e.g., 'models/my_model.joblib')
                   where the model will be saved.

    Raises:
        OSError: If directory creation fails (e.g., due to permission issues).
        Exception: For other errors that might occur during model serialization by joblib.
    """
    try:
        # Ensure the directory for storing the model exists.
        # os.path.dirname() gets the directory part of the file_path.
        model_dir = os.path.dirname(file_path)
        if model_dir: # Check if model_dir is not an empty string (i.e., not saving in current dir)
            # exist_ok=True prevents an error if the directory already exists.
            os.makedirs(model_dir, exist_ok=True)
            print(f"[INFO] Ensured directory exists for model saving: '{model_dir}'")

        # Serialize and save the model using joblib.dump
        joblib.dump(model, file_path)
        print(f"[INFO] Model successfully saved to '{file_path}'")
    except OSError as e:
        print(f"[ERROR] Could not create directory for model at '{os.path.dirname(file_path)}': {e}")
        raise # Re-raise the OSError to be handled by the caller
    except Exception as e:
        print(f"[ERROR] Failed to save model to '{file_path}' using joblib: {e}")
        raise # Re-raise other exceptions

def load_model(file_path: str) -> any:
    """
    Loads a trained model from a specified file path using joblib.

    Args:
        file_path: The path to the .joblib model file.

    Returns:
        The loaded model object. This object can be used directly for predictions.

    Raises:
        FileNotFoundError: If the model file is not found at the specified path.
        Exception: For other errors during model deserialization by joblib (e.g.,
                   if the file is corrupted or not a valid joblib file).
    """
    try:
        model = joblib.load(file_path)
        print(f"[INFO] Model loaded successfully from '{file_path}'")
        return model
    except FileNotFoundError:
        print(f"[ERROR] Model file not found at '{file_path}'. Cannot load model.")
        raise # Re-raise FileNotFoundError
    except Exception as e: # joblib might raise various errors (e.g., PicklingError, ImportError)
        print(f"[ERROR] Failed to load model from '{file_path}'. File may be corrupted or incompatible: {e}")
        raise # Re-raise other exceptions

def predict_saci_fire_risk(model: LogisticRegression,
                             live_temp: float,
                             live_hum: float,
                             live_smoke_adc: float) -> tuple[int, np.ndarray]:
    """
    """
    Predicts the fire risk label and associated probabilities for a given set of
    live sensor readings using a trained model.

    The input features must match those used during model training:
    'temperature', 'humidity', 'smoke_level'. The order must also be the same.

    Args:
        model: A trained scikit-learn compatible classifier (e.g., LogisticRegression)
               that has `predict` and `predict_proba` methods.
        live_temp: Current temperature reading (float).
        live_hum: Current humidity reading (float).
        live_smoke_adc: Current smoke sensor ADC value (float or int).

    Returns:
        A tuple containing:
            - predicted_label (int): The predicted class label. For SACI, this is
                                     typically 0 (No Fire) or 1 (Fire).
            - predicted_probabilities (np.ndarray): An array of probabilities for each class.
                                                  For binary classification, this is usually
                                                  [P(class_0), P(class_1)].

    Raises:
        NotFittedError: If the provided model is not fitted (from sklearn.exceptions).
        ValueError: If input data cannot be converted to the required format.
        Exception: For other errors that may occur during the prediction process.
    """
    # Create a DataFrame from the live data with the correct feature names.
    # This ensures the input is in the same format (and order) as the training data.
    try:
        input_data = pd.DataFrame(
            [[float(live_temp), float(live_hum), float(live_smoke_adc)]], # Ensure float type
            columns=['temperature', 'humidity', 'smoke_level'] # Must match training feature names
        )
    except ValueError as ve:
        print(f"[ERROR] Invalid input data for prediction: {ve}. Ensure inputs are numeric.")
        raise

    try:
        # Get the predicted class label (e.g., 0 or 1)
        predicted_label = model.predict(input_data)[0]
        # Get the probabilities for each class
        predicted_probabilities = model.predict_proba(input_data)[0]
        # Ensure label is a standard Python int, as some models might return numpy int types
        return int(predicted_label), predicted_probabilities
    except NotFittedError as nfe:
        print(f"[ERROR] Prediction failed: The model '{type(model).__name__}' is not fitted. {nfe}")
        raise # Re-raise to indicate a programming or model setup error
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during prediction: {e}")
        raise # Re-raise other prediction-time errors


# --- Main Execution Block ---
if __name__ == '__main__':
    """
    Main execution flow for the SACI Fire Predictor script.
    This block orchestrates the loading of data, preprocessing, model training,
    evaluation, model saving, and demonstration of prediction capabilities.
    """
    print("===== SACI Fire Risk Prediction Model Script Initializing =====")

    # --- Step 1: Load and Preprocess Data ---
    # Encapsulate data loading and preprocessing in a try-except block
    # to handle critical errors like missing files or columns.
    try:
        print("\n[PHASE] 1. Data Loading and Preprocessing")
        data_df = load_data(DATASET_PATH)
        X, y = preprocess_data(data_df) # X = features, y = target
        print("[PHASE] 1. Data Loading and Preprocessing COMPLETED")
    except FileNotFoundError:
        # Specific handling for FileNotFoundError from load_data
        print(f"[FATAL] Script terminated: Dataset file '{DATASET_PATH}' not found.")
        exit(1) # Exit if data cannot be loaded
    except pd.errors.EmptyDataError:
        print(f"[FATAL] Script terminated: Dataset file '{DATASET_PATH}' is empty.")
        exit(1)
    except ValueError as ve:
        # Specific handling for ValueError from preprocess_data (e.g., missing columns)
        print(f"[FATAL] Script terminated: Error during data preprocessing: {ve}")
        exit(1)
    except Exception as e:
        # Catch-all for any other unexpected errors during this critical phase
        print(f"[FATAL] Script terminated: An unexpected error occurred during "
              f"data loading or preprocessing: {e}")
        exit(1)

    # --- Step 2: Split Data into Training and Testing Sets ---
    print("\n[PHASE] 2. Splitting Data into Training and Test Sets")
    # Using a standard 80/20 split. random_state ensures reproducibility.
    # stratify=y is important for classification tasks to maintain class proportion in splits.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"  Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features.")
    print(f"  Test set: {X_test.shape[0]} samples, {X_test.shape[1]} features.")
    print("[PHASE] 2. Data Splitting COMPLETED")

    # --- Step 3: Train Logistic Regression Model ---
    # This is the primary model for the MVP.
    print("\n[PHASE] 3. Training Logistic Regression Model")
    # The train_logistic_regression function encapsulates model instantiation and fitting.
    log_reg_model = train_logistic_regression(X_train, y_train, random_state=42)
    print("[PHASE] 3. Logistic Regression Model Training COMPLETED")

    # --- Step 4: Save the Trained Logistic Regression Model ---
    # Models are saved to enable later use without retraining.
    print("\n[PHASE] 4. Saving Trained Model")
    try:
        save_model(log_reg_model, LOG_REG_MODEL_PATH)
    except Exception as e:
        # Errors from save_model (directory creation, joblib dump) are critical.
        print(f"[FATAL] Script terminated: Could not save the model to '{LOG_REG_MODEL_PATH}': {e}")
        exit(1)
    print("[PHASE] 4. Model Saving COMPLETED")

    # --- Step 5: Evaluate the Logistic Regression Model ---
    # Evaluation provides insights into how well the model performs on unseen data.
    print("\n[PHASE] 5. Evaluating Logistic Regression Model")
    # evaluate_model returns multiple metrics; we can store them if needed for further analysis.
    lr_accuracy, lr_precision, lr_recall, lr_f1, _ = evaluate_model(
        log_reg_model, X_test, y_test, "Logistic Regression (Primary MVP Model)"
    )
    # Example: Further use of a specific metric
    print(f"  -> Logistic Regression weighted F1-score on test set: {lr_f1:.4f}")
    print("[PHASE] 5. Model Evaluation COMPLETED")

    # --- Step 6: Live Prediction Example (Using the Model Trained in This Session) ---
    # This demonstrates how the model can be used for real-time (or simulated real-time) predictions.
    print("\n[PHASE] 6. Live Prediction Example (with current session's model)")
    if log_reg_model: # Check if model was trained successfully
        # Define sample sensor readings for the prediction demonstration
        sample_temp_live, sample_hum_live, sample_smoke_live = 30.5, 55.2, 350.0

        print(f"  Input data for prediction: Temp={sample_temp_live}°C, "
              f"Hum={sample_hum_live}%, Smoke ADC={sample_smoke_live}")
        try:
            pred_label, pred_proba = predict_saci_fire_risk(
                log_reg_model, sample_temp_live, sample_hum_live, sample_smoke_live
            )
            risk_status_live = "Fire Detected" if pred_label == 1 else "No Fire Detected"
            print(f"  Predicted Label: {pred_label} ({risk_status_live})")
            # Probabilities are useful for understanding model confidence.
            if len(pred_proba) == 2: # Binary classification
                 print(f"  Prediction Probabilities: [P(No Fire)={pred_proba[0]:.4f}, P(Fire)={pred_proba[1]:.4f}]")
            else: # General case if model output is different
                print(f"  Prediction Probabilities: {pred_proba}")
        except Exception as e:
            print(f"  [ERROR] Live prediction failed: {e}")
    else:
        print("  Skipping live prediction example as the model was not trained in this session.")
    print("[PHASE] 6. Live Prediction Example COMPLETED")

    # --- Step 7: Prediction with Loaded Model Example ---
    # This demonstrates the full cycle: saving a model, then loading it back and using it.
    # This simulates how a separate application would use the pre-trained model.
    print("\n[PHASE] 7. Prediction with Loaded Model Example")
    # Define different sample data for this specific demonstration to distinguish from live example
    sample_temp_loaded, sample_hum_loaded, sample_smoke_loaded = 45.0, 30.0, 750.0

    try:
        print(f"  Attempting to load model from: '{LOG_REG_MODEL_PATH}'")
        # Load the Logistic Regression model that was saved earlier in this script.
        loaded_model_for_demo = load_model(LOG_REG_MODEL_PATH)

        if loaded_model_for_demo:
            print(f"  Input data for prediction with loaded model: Temp={sample_temp_loaded}°C, "
                  f"Hum={sample_hum_loaded}%, Smoke ADC={sample_smoke_loaded}")
            pred_label_loaded, pred_proba_loaded = predict_saci_fire_risk(
                loaded_model_for_demo, sample_temp_loaded, sample_hum_loaded, sample_smoke_loaded
            )
            risk_status_loaded = "Fire Detected" if pred_label_loaded == 1 else "No Fire Detected"
            print(f"  Predicted Label (from loaded model): {pred_label_loaded} ({risk_status_loaded})")
            if len(pred_proba_loaded) == 2: # Binary classification
                print(f"  Prediction Probabilities (from loaded model): "
                      f"[P(No Fire)={pred_proba_loaded[0]:.4f}, P(Fire)={pred_proba_loaded[1]:.4f}]")
            else: # Should not happen for binary logistic regression
                 print(f"  Prediction Probabilities (from loaded model): {pred_proba_loaded}")
    except FileNotFoundError:
        # This handles if LOG_REG_MODEL_PATH does not exist (e.g., script run for the first time and save failed)
        print(f"  [WARN] Demo with loaded model skipped: Model file '{LOG_REG_MODEL_PATH}' not found.")
    except Exception as e:
        # Catch other errors during loading or prediction with the loaded model
        print(f"  [WARN] Demo with loaded model skipped due to an error: {e}")
    print("[PHASE] 7. Prediction with Loaded Model Example COMPLETED")

    # --- Script Finished ---
    print("\n===== SACI Fire Predictor script execution finished. =====")
