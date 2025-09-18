import joblib
import os
from django.conf import settings

# Load model once when server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, "admissions", "resources", "rf_model.pkl")
rf_model = joblib.load(MODEL_PATH)

def predict_enrollment(features):
    """
    features: dict or list of input values matching your training data
    """
    # Example: if your model expects a list of numerical features
    X = [features]  
    prediction = rf_model.predict(X)
    return prediction[0]