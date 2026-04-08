import os
import torch
import pandas as pd
import matplotlib.pyplot as plt

from models.fraud_detector import ModelFactory
from utils.trainer import Trainer
from utils.data_handler import DataHandler

MODEL_PATH = "results/models/centralized_model.pth"

# ==============================
# Load Model
# ==============================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model = ModelFactory.create_model("neural_network")

checkpoint = torch.load(MODEL_PATH)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    model.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)

model.eval()
print("✅ Centralized model loaded successfully")

# ==============================
# Load & Process Data
# ==============================

handler = DataHandler()

df = handler.load_dataset()
X, y = handler.preprocess_data(df)
X, y = handler.balance_data(X, y)

splits = handler.split_data(X, y)

X_test, y_test = splits["test"]

trainer = Trainer(model)

# ==============================
# Evaluate
# ==============================

metrics = trainer.calculate_metrics(X_test, y_test)

print("\n📊 Centralized Metrics:")
for k, v in metrics.items():
    if k != "confusion_matrix":
        print(f"{k}: {v:.4f}")

# ==============================
# Save Results
# ==============================

os.makedirs("results/tables", exist_ok=True)
os.makedirs("results/graphs", exist_ok=True)

pd.DataFrame([metrics]).to_csv(
    "results/tables/centralized_results.csv",
    index=False
)

plt.figure()
plt.bar(["Centralized"], [metrics["accuracy"]])
plt.ylabel("Accuracy")
plt.title("Centralized Model Accuracy")
plt.grid(True)

plt.savefig("results/graphs/centralized_accuracy.png")
plt.close()

print("\n📄 Table saved → results/tables/centralized_results.csv")
print("📊 Graph saved → results/graphs/centralized_accuracy.png")
print("✅ Centralized evaluation complete!")