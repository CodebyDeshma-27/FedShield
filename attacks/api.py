from fastapi import FastAPI
from pydantic import BaseModel
import torch
import numpy as np
import os

from models.fraud_detector import ModelFactory
from config import MODEL_CONFIG

# =========================
# CREATE APP
# =========================
app = FastAPI(title="Fraud Detection API")

# =========================
# INPUT SCHEMA
# =========================
class Transaction(BaseModel):
    features: list[float]

# =========================
# LOAD MODEL (FIXED 🔥)
# =========================

# Safe path (no path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "results", "models", "dp_protected_model.pth")

# Create model
model = ModelFactory.create_model('neural_network', MODEL_CONFIG)

# Load checkpoint correctly ✅
checkpoint = torch.load(MODEL_PATH, map_location='cpu')

# Handle both cases (pro-level safety 🔥)
if "model_state_dict" in checkpoint:
    model.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)

model.eval()

print("✅ Model loaded successfully")

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# FRAUD PREDICTION
# =========================

@app.post("/predict")
def predict(transaction: Transaction):
    try:
        # Validate input size (VERY IMPORTANT 🔥)
        if len(transaction.features) != 30:
            return {"error": "Expected 30 features"}

        features = np.array(transaction.features, dtype=np.float32)

        # reshape for model
        x = torch.tensor(features).unsqueeze(0)

        with torch.no_grad():
            output = model(x)
            prob = torch.softmax(output, dim=1)[0][1].item()

        return {
            "fraud_probability": round(prob, 4),
            "is_fraud": prob > 0.5
        }

    except Exception as e:
        return {"error": str(e)}