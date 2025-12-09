# src/inference.py

import os
import joblib
import pandas as pd

from .features import extract_features

# Paths to model and feature columns
MODEL_PATH = os.path.join("models", "phishing_rf.pkl")
FEATURE_COLS_PATH = os.path.join("models", "feature_columns.pkl")

# Load model and feature columns once at import time
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. "
                            f"Make sure phishing_rf.pkl is in the 'models' folder.")

try:
    feature_columns = joblib.load(FEATURE_COLS_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Feature columns file not found at {FEATURE_COLS_PATH}. "
                            f"Make sure feature_columns.pkl is in the 'models' folder.")


def build_feature_dataframe(url: str) -> pd.DataFrame:
    """
    Take a URL string, compute features using extract_features,
    and return a pandas DataFrame with columns in the SAME ORDER
    as during training (feature_columns).
    """
    feats_dict = extract_features(url)

    # Check if any feature expected by the model is missing
    missing = [col for col in feature_columns if col not in feats_dict]
    if missing:
        raise ValueError(f"Missing features in extract_features(): {missing}")

    # Create a single-row DataFrame
    df = pd.DataFrame([feats_dict])

    # Reorder columns to match training
    df = df[feature_columns]

    return df


def predict_url(url: str):
    """
    Predict whether a URL is phishing or legitimate.
    Returns: (label, probability_of_phishing)
    label: 1 = phishing, 0 = legitimate
    """
    df = build_feature_dataframe(url)

    # Get probability for class '1' (phishing)
    proba_phishing = model.predict_proba(df)[0][1]
    label = int(proba_phishing >= 0.5)

    return label, float(proba_phishing)


# Optional: quick test when running this file directly
if __name__ == "__main__":
    test_url = "http://secure-login-bank-update.com/verify?user=abc&token=123"
    lbl, p = predict_url(test_url)
    print("URL:", test_url)
    print("Prediction:", "phishing" if lbl == 1 else "legitimate")
    print("Probability of phishing:", p)
