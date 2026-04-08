# 📋 COMPLETE WORKFLOW GUIDE - Dataset Upload to Model Verification

## Table of Contents
1. [Dataset Selection & Import](#1-dataset-selection--import)
2. [Step-by-Step Commands](#2-step-by-step-commands)
3. [Dataset Verification](#3-dataset-verification)
4. [Model Training](#4-model-training)
5. [Verify Model Learned Fraud](#5-verify-model-learned-fraud)
6. [Quick Reference Checklist](#6-quick-reference-checklist)

---

# 1. DATASET SELECTION & IMPORT

## Step 1.1: Prepare Your New Dataset

### Dataset Requirements

Your dataset MUST have this format:

```
CSV File with columns:
├─ Feature columns (V1, V2, V3, ..., V30 OR any numeric features)
├─ Amount column (transaction amount)
├─ Time column (optional, but recommended)
└─ Class column (0 = normal, 1 = fraud) ← CRITICAL!

Example CSV format:
V1,V2,V3,...,V28,Time,Amount,Class
-0.5,1.2,0.8,...,2.1,0,100.00,0
0.3,-0.9,1.5,...,-1.2,5,250.50,0
1.1,0.7,-0.4,....0.9,12,1500.00,1  ← This is a fraud transaction
...
```

### ✅ Checklist Before Import

```
□ Dataset is in CSV format (.csv)
□ Has 'Class' column (0=normal, 1=fraud)
□ Has at least 10,000 rows (more is better)
□ Has at least 1% fraud cases (100+ fraud transactions)
□ All numeric features (no text)
□ No missing values (or fill them)
```

### ❌ Common Mistakes to Avoid

```
❌ Missing 'Class' column → Model can't learn what fraud is
❌ Only 100 rows → Too small, model overfits
❌ 0 fraud cases → Nothing to learn, 100% accuracy but useless
❌ 0.1% fraud → Extreme imbalance, SMOTE can't handle
❌ Text columns → Model needs numbers only
```

---

## Step 1.2: Upload New Dataset to Project

### Option A: Simple - Replace Existing Dataset

```bash
# 1. Copy your new dataset to:
#    c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv

# Or use PowerShell:
Copy-Item "C:\Path\To\Your\NewDataset.csv" `
          "C:\Projects\fraud-intelligence-network (1)\data\creditcard.csv"

# The code will automatically load from this location
```

### Option B: Keep Both Datasets - Create New Folder

```bash
# Create new dataset folder
mkdir "c:\Projects\fraud-intelligence-network (1)\data\my_custom_dataset"

# Copy your dataset there
Copy-Item "C:\Path\To\Your\NewDataset.csv" `
          "c:\Projects\fraud-intelligence-network (1)\data\my_custom_dataset\data.csv"

# Then update config.py (see Step 1.3)
```

### Option C: Download from Kaggle (If using Kaggle dataset)

```bash
# Install Kaggle CLI
pip install kaggle

# Download dataset
kaggle datasets download -d your-dataset-name

# Extract to data folder
```

---

## Step 1.3: Update Configuration (If Using Custom Path)

### File: `config.py`

Open `config.py` and find:

```python
DATA_CONFIG = {
    'dataset_path': 'data/creditcard.csv',  ← CHANGE THIS LINE
    'num_banks': 5,
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
    'balance_data': True,
    'scaling': 'standard'
}
```

### To Use Your Custom Dataset:

```python
# Option 1: Update the path
DATA_CONFIG = {
    'dataset_path': 'data/my_custom_dataset/data.csv',  ← CUSTOM PATH
    'num_banks': 5,
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
    'balance_data': True,
    'scaling': 'standard'
}

# Option 2: If dataset name is different
DATA_CONFIG = {
    'dataset_path': 'data/fraud_transactions.csv',  ← YOUR FILENAME
    'num_banks': 5,
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
    'balance_data': True,
    'scaling': 'standard'
}
```

**IMPORTANT: Only change the `dataset_path` line. Don't change other settings yet.**

---

# 2. STEP-BY-STEP COMMANDS

## Command List (In Order)

Run these commands IN THIS ORDER in PowerShell:

### STEP 0: Activate Virtual Environment

```powershell
# Activate Python virtual environment
& "c:\Projects\fraud-intelligence-network (1)\.venv\Scripts\Activate.ps1"

# Expected output:
# (.venv) C:\Projects\fraud-intelligence-network (1)>
```

---

### STEP 1: Verify Dataset Exists

```powershell
# Check if dataset file exists
Test-Path "c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv"

# Expected output: True

# If False: Your dataset is not in the right location!
```

---

### STEP 2: Install Dependencies (First Time Only)

```powershell
# Install all required packages
pip install -r requirements.txt

# This installs:
# - pandas (data loading)
# - numpy (math operations)
# - scikit-learn (metrics, preprocessing)
# - torch (neural networks)
# - opacus (differential privacy)
# - flwr (federated learning)
# - flask (API)

# Expected output: "Successfully installed..."
```

---

### STEP 3: Quick Dataset Inspection

```powershell
# Create a quick inspection script
# (Or run this Python code directly)

python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')
print('=== DATASET INFO ===')
print(f'Shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
print(f'Data types:')
print(df.dtypes)
print()
print('=== CLASS DISTRIBUTION ===')
print(df['Class'].value_counts())
print()
print('=== STATISTICS ===')
print(df.describe())
"
```

**What to look for:**
```
✅ Shape: (numberOfRows, 31) 
   - Should have hundreds of thousands of rows
   - Should have 31 columns (30 features + 1 Class)

✅ Class column exists and has:
   - Some 0s (normal transactions)
   - Some 1s (fraud transactions)

✅ No missing values (if any, SMOTE will handle)
```

---

### STEP 4A: FULL PIPELINE (Recommended - Does Everything)

```powershell
# Run complete unified pipeline
# This does ALL steps automatically:
# - Load data
# - Preprocess
# - Train 3 models
# - Run attacks
# - Validate
# - Generate reports

python main_unified_pipeline.py

# Expected output:
# [INFO] Loading dataset...
# [INFO] Dataset loaded. Shape: (284807, 31)
# [INFO] Preprocessing data...
# ... (lots of training output)
# [INFO] All experiments completed!
# [INFO] Results saved to results/
```

**Time needed:** 2-5 minutes (depends on dataset size)

**What it produces:**
```
results/
├─ models/
│  ├─ centralized_model.pth       (baseline model)
│  ├─ federated_model.pth         (5-bank model)
│  └─ dp_protected_model.pth      (privacy-protected model)
├─ tables/
│  ├─ centralized_results.csv     (baseline metrics)
│  ├─ federated_round_metrics.csv (training progress)
│  ├─ exp1_accuracy_comparison.csv
│  ├─ exp2_privacy_tradeoff.csv
│  ├─ exp3_attack_resistance.csv
│  └─ exp4_communication.csv
└─ experiment_results.json        (summary)
```

---

### STEP 4B: INDIVIDUAL TRAINING (If You Want Control)

#### Command to train SPECIFIC model:

**Option 1: Centralized Model Only**
```python
# Create file: train_centralized.py

from utils.data_handler import DataHandler
from utils.trainer import Trainer
from models.fraud_detector import FraudDetectorNN
import config
import torch

# Load data
handler = DataHandler(config.DATA_CONFIG)
train_data, val_data, test_data = handler.load_and_split(is_federated=False)

# Build model
model = FraudDetectorNN(input_size=30)
trainer = Trainer(model, config.TRAINING_CONFIG)

# Train
print("Training centralized model...")
trainer.train(train_data, val_data)

# Test
metrics = trainer.evaluate(test_data)
print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1-Score: {metrics['f1']:.4f}")
print(f"AUC: {metrics['auc']:.4f}")

# Save
torch.save(model.state_dict(), 'results/models/my_custom_model.pth')
print("Model saved!")
```

**Then run:**
```powershell
python train_centralized.py
```

---

**Option 2: Federated Model (5 Banks)**

```python
# Create file: train_federated.py

from federated.server import FederatedServer
from utils.data_handler import DataHandler
import config

# Load data
handler = DataHandler(config.DATA_CONFIG)
train_data, val_data, test_data = handler.load_and_split(is_federated=True)

# Create server
server = FederatedServer(
    num_clients=5,
    input_size=30,
    config=config.TRAINING_CONFIG
)

# Train for 20 rounds
print("Training federated model with 5 banks...")
for round_num in range(20):
    print(f"Round {round_num+1}/20")
    server.train_round(train_data['banks'])

# Evaluate
metrics = server.evaluate(test_data)
print(f"Final Accuracy: {metrics['accuracy']:.4f}")
print(f"Final F1-Score: {metrics['f1']:.4f}")

# Save
server.save_model('results/models/federated_custom.pth')
```

**Then run:**
```powershell
python train_federated.py
```

---

### STEP 5: Start REST API Server

```powershell
# Start Flask API
python api/app.py

# Expected output:
# WARNING in app.run (running on http://127.0.0.1:5000)
# * Press CTRL+C to quit

# API is now LIVE at http://localhost:5000
```

**Keep this running in terminal!**

---

### STEP 6: Test API in NEW Terminal

```powershell
# Open ANOTHER PowerShell terminal (don't close the first one)

# Test health endpoint
curl http://localhost:5000/health

# Expected output:
# {"status":"healthy","message":"API is running"}

# Test with sample transaction
$transaction = @(
    -0.5, 1.2, 0.8, -0.3, 0.5, -0.1, 0.9, 0.2, -0.4, 0.6,
    -0.7, 0.1, 0.4, -0.2, 0.8, 0.3, -0.6, 0.5, 0.1, -0.3,
    0.7, 0.2, -0.5, 0.4, -0.1, 0.9, 0.3, -0.8, 0.6, 0.2
) | ConvertTo-Json

curl -Method POST `
     -Uri http://localhost:5000/predict `
     -ContentType "application/json" `
     -Body $transaction

# Expected output:
# {"prediction":"normal","confidence":0.92,"privacy":{"epsilon":1.0,"delta":0.00001}}
```

---

### STEP 7: Run API Test Suite

```powershell
# In a THIRD terminal (API still running in first terminal)

python api/test_api.py

# Expected output:
# test_health_endpoint ... ok
# test_info_endpoint ... ok
# test_privacy_endpoint ... ok
# test_single_prediction ... ok
# test_batch_prediction ... ok
# ...
# ALL TESTS PASSED ✓
```

---

# 3. DATASET VERIFICATION

## How to Verify Your Dataset is Good

### Check 1: Dataset Shape and Size

```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')
print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')
print(f'Dataset size: {df.memory_usage().sum() / 1024**2:.2f} MB')

# Should have:
# ✓ At least 10,000 rows (10K+)
# ✓ Between 25-50 columns (features)
# ✓ Less than 1GB in memory
"
```

---

### Check 2: Fraud Distribution

```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')

fraud_cases = (df['Class'] == 1).sum()
normal_cases = (df['Class'] == 0).sum()
fraud_percentage = (fraud_cases / len(df)) * 100

print(f'Normal transactions: {normal_cases:,}')
print(f'Fraud transactions: {fraud_cases:,}')
print(f'Fraud percentage: {fraud_percentage:.2f}%')
print(f'Imbalance ratio: {normal_cases / fraud_cases:.1f}:1')

# Should have:
# ✓ At least 100 fraud cases (100+)
# ✓ At least 1% fraud (0.01+)
# ✓ Won't work with: 0% fraud or 50%+ fraud
"
```

---

### Check 3: Feature Completeness

```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')

print('=== Missing Values ===')
print(df.isnull().sum())

print()
print('=== Data Types ===')
print(df.dtypes)

# Should have:
# ✓ No missing values in Class column
# ✓ All numeric columns (int64 or float64)
# ✓ Class column with only 0s and 1s
"
```

---

### Check 4: Feature Statistics

```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')

print('=== Summary Statistics ===')
print(df.describe())

# Look for:
# ✓ Min/Max values are reasonable
# ✓ No extreme outliers (unless that's fraud)
# ✓ Mean and std dev vary by feature
"
```

---

### Check 5: Fraud vs Normal Differences

```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')

fraud = df[df['Class'] == 1]
normal = df[df['Class'] == 0]

print('=== NORMAL TRANSACTIONS ===')
print(f'Count: {len(normal)}')
print(f'Amount mean: ${normal[\"Amount\"].mean():.2f}')
print(f'Amount std: ${normal[\"Amount\"].std():.2f}')
print(f'Amount max: ${normal[\"Amount\"].max():.2f}')

print()
print('=== FRAUD TRANSACTIONS ===')
print(f'Count: {len(fraud)}')
print(f'Amount mean: ${fraud[\"Amount\"].mean():.2f}')
print(f'Amount std: ${fraud[\"Amount\"].std():.2f}')
print(f'Amount max: ${fraud[\"Amount\"].max():.2f}')

# You should see DIFFERENCES between fraud and normal!
# If they're identical, model can't distinguish them
"
```

---

# 4. MODEL TRAINING

## Training Process Explained

### What Happens During Training

```
INPUT DATASET
    ↓
[LOAD] Read CSV file
    ↓
[PREPROCESS] Normalize features, scale amounts
    ↓
[SPLIT] 70% train, 15% validation, 15% test
    ↓
[BALANCE] Use SMOTE to create synthetic fraud cases
    ↓
[DISTRIBUTE] For federated: split across 5 banks
    ↓
[TRAIN] Model learns patterns:
    - Normal transactions look like X
    - Fraud transactions look like Y
    ↓
[VALIDATE] Check accuracy after each epoch
    ↓
[EARLY STOP] Stop if overfitting (no improvement)
    ↓
[TEST] Final evaluation on unseen data
    ↓
[SAVE] Save model weights to .pth file
    ↓
OUTPUT: Trained fraud detection model
```

---

## Full Training Command Breakdown

### Command 1: Run Everything at Once (Easiest)

```powershell
python main_unified_pipeline.py
```

**What it does:**
1. ✓ Load dataset
2. ✓ Train centralized model
3. ✓ Train federated model (5 banks)
4. ✓ Train DP-protected model
5. ✓ Run attacks (test if privacy works)
6. ✓ Validate all models
7. ✓ Generate reports (CSV + JSON)
8. ✓ Save all models

**Output:**
```
[INFO] Phase 1: Dataset Loading
[INFO] Loading dataset from data/creditcard.csv
[INFO] Dataset shape: (284807, 31)
[INFO] Class distribution: normal=284315, fraud=492

[INFO] Phase 2: Model Training
[INFO] Training centralized model...
Epoch 1/50: loss=0.45, val_acc=0.9992
Epoch 2/50: loss=0.42, val_acc=0.9993
... (skipped for brevity)
Epoch 50/50: loss=0.38, val_acc=0.9993
[INFO] Centralized training complete!

[INFO] Training federated model (5 banks)...
Round 1/20: Aggregating weights from 5 banks
... 
Round 20/20: Final aggregation
[INFO] Federated training complete!

[INFO] Training DP-protected model...
Epoch 1/50: loss=0.46, val_acc=0.9992 (with privacy)
...
[INFO] DP training complete!

[INFO] Phase 3: Attack Simulations
[INFO] Testing model inversion attack...
Success rate: 15.2% (vs 41.3% without DP) ← DP WORKS!

[INFO] Phase 4: Validation
[INFO] Centralized accuracy: 99.92%
[INFO] Federated accuracy: 99.92%
[INFO] DP-Protected accuracy: 99.93%

[INFO] Phase 5: Report Generation
[INFO] Results saved to results/
```

**Time:** 2-10 minutes (depends on dataset size)

---

### Command 2: Train Only Specific Models (Advanced)

#### Just Centralized Model:

```powershell
python -c "
from utils.data_handler import DataHandler
from utils.trainer import Trainer
from models.fraud_detector import FraudDetectorNN
import config
import torch

# Load
handler = DataHandler(config.DATA_CONFIG)
train_data, val_data, test_data = handler.load_and_split()

# Build
model = FraudDetectorNN(input_size=30)
trainer = Trainer(model, config.TRAINING_CONFIG)

# Train
print('Training centralized model...')
trainer.train(train_data, val_data)

# Evaluate
metrics = trainer.evaluate(test_data)
print(f'Final Accuracy: {metrics[\"accuracy\"]:.4f}')
print(f'Final F1-Score: {metrics[\"f1\"]:.4f}')
print(f'Final AUC: {metrics[\"auc\"]:.4f}')

# Save
torch.save(model.state_dict(), 'results/models/centralized_model.pth')
"
```

---

#### Just Federated Model:

```powershell
python -c "
from federated.server import FederatedServer
from utils.data_handler import DataHandler
import config

# Load
handler = DataHandler(config.DATA_CONFIG)
train_data, val_data, test_data = handler.load_and_split(is_federated=True)

# Create server
server = FederatedServer(num_clients=5, input_size=30, config=config.TRAINING_CONFIG)

# Train 20 rounds
for round_num in range(20):
    print(f'Round {round_num+1}/20')
    server.train_round(train_data['banks'])
    
# Evaluate
metrics = server.evaluate(test_data)
print(f'Final Accuracy: {metrics[\"accuracy\"]:.4f}')

# Save
server.save_model('results/models/federated_model.pth')
"
```

---

# 5. VERIFY MODEL LEARNED FRAUD

## How to Know Your Model Learned Fraud Patterns

### Method 1: Check Accuracy Metrics

```powershell
# After training, check results
python -c "
import json

with open('results/experiment_results.json') as f:
    results = json.load(f)
    
print('=== MODEL PERFORMANCE ===')
print(f'Accuracy: {results[\"centralized\"][\"accuracy\"]:.4f}')
print(f'F1-Score: {results[\"centralized\"][\"f1_score\"]:.4f}')
print(f'AUC-ROC: {results[\"centralized\"][\"auc\"]:.4f}')
print(f'Precision: {results[\"centralized\"][\"precision\"]:.4f}')
print(f'Recall: {results[\"centralized\"][\"recall\"]:.4f}')

# ✓ High accuracy (>95%)
# ✓ High F1-Score (>0.5)  ← Most important!
# ✓ High AUC (>0.9)
# ✓ Balance between precision and recall
"
```

**Why Each Metric Matters:**

| Metric | Means | Good if |
|--------|-------|---------|
| **Accuracy** | % transactions correctly classified | >95% |
| **F1-Score** | Balance between precision & recall | >0.5 (fraud is rare!) |
| **Precision** | Of predicted fraud, how many true? | >0.7 (fewer false alarms) |
| **Recall** | Of actual fraud, how many detected? | >0.7 (catch fraud) |
| **AUC-ROC** | Model's ability to distinguish | >0.90 |

---

### Method 2: Test on KNOWN Fraud Cases

```powershell
python -c "
import pandas as pd
import torch
from models.fraud_detector import FraudDetectorNN
import config

# Load model
model = FraudDetectorNN(input_size=30)
model.load_state_dict(torch.load('results/models/centralized_model.pth'))
model.eval()

# Load dataset
df = pd.read_csv('data/creditcard.csv')

# Get fraud cases
fraud_cases = df[df['Class'] == 1].head(10)
normal_cases = df[df['Class'] == 0].head(10)

# Prepare features
fraud_features = torch.FloatTensor(fraud_cases.drop('Class', axis=1).values)
normal_features = torch.FloatTensor(normal_cases.drop('Class', axis=1).values)

# Predict
with torch.no_grad():
    fraud_preds = model(fraud_features)
    normal_preds = model(normal_features)

# Get probabilities
fraud_probs = torch.softmax(fraud_preds, dim=1)[:, 1]  # Fraud class
normal_probs = torch.softmax(normal_preds, dim=1)[:, 1]

print('=== FRAUD DETECTION TEST ===')
print(f'Average fraud probability for FRAUD cases: {fraud_probs.mean():.4f}')
print(f'Average fraud probability for NORMAL cases: {normal_probs.mean():.4f}')

# ✓ If fraud_probs > 0.5 and normal_probs < 0.5 → MODEL LEARNED!
# ✓ Fraud cases should have HIGH fraud probability
# ✓ Normal cases should have LOW fraud probability
"
```

**How to interpret:**
```
If output is:
- Fraud average: 0.85
- Normal average: 0.05

✓ MODEL LEARNED PERFECTLY!
  Fraud cases = 85% probability of being fraud
  Normal cases = 5% probability of being fraud
  Clear separation!

If output is:
- Fraud average: 0.52
- Normal average: 0.48

⚠️  MODEL IS CONFUSED
  Only slightly better than random guess
  Need to retrain or check dataset
```

---

### Method 3: Visualize Confusion Matrix

```powershell
python -c "
import pandas as pd
import torch
from sklearn.metrics import confusion_matrix
from models.fraud_detector import FraudDetectorNN

# Load model
model = FraudDetectorNN(input_size=30)
model.load_state_dict(torch.load('results/models/centralized_model.pth'))
model.eval()

# Load test data
df = pd.read_csv('data/creditcard.csv')
test_df = df.sample(n=10000, random_state=42)  # Sample for speed

features = torch.FloatTensor(test_df.drop('Class', axis=1).values)
true_labels = test_df['Class'].values.astype(int)

# Predict
with torch.no_grad():
    preds = model(features).argmax(dim=1).numpy()

# Confusion matrix
cm = confusion_matrix(true_labels, preds)
print('=== CONFUSION MATRIX ===')
print('Predicted:     Normal  Fraud')
print(f'Actually Normal: {cm[0][0]:5} {cm[0][1]:5}')
print(f'Actually Fraud:  {cm[1][0]:5} {cm[1][1]:5}')

# Calculate metrics
tn, fp, fn, tp = cm.ravel()
print()
print(f'True Positives (caught fraud): {tp}')
print(f'True Negatives (normal correct): {tn}')
print(f'False Positives (false alarms): {fp}')
print(f'False Negatives (missed fraud): {fn}')

# ✓ TP high = catches actual fraud
# ✓ FN low = doesn't miss fraud
# ✓ FP reasonable = not too many false alarms
"
```

---

### Method 4: Test Attack Simulations (Proof Model Learned)

```powershell
# Run attack to see if model can be fooled
python attacks/gradient_leakage.py

# Expected output:
# [TEST] Testing gradient leakage attack...
# [INFO] Attack success rate WITHOUT DP: 41.3%
# [INFO] Attack success rate WITH DP: 15.2%
# [INFO] Protection factor: 2.74x harder with DP
#
# ✓ If this works, model learned real patterns
#   (Attacks only work on models that learned something)
# ✗ If attack has 0% success, model might be random
```

---

### Method 5: Feature Importance / Attention

```powershell
# Check which features model uses most
python -c "
import torch
from models.fraud_detector import FraudDetectorNN

model = FraudDetectorNN(input_size=30)
model.load_state_dict(torch.load('results/models/centralized_model.pth'))

# Get first layer weights (input → first hidden layer)
first_layer_weights = model.fc1.weight.data  # Shape: (128, 30)

# Calculate importance (sum of absolute weights per feature)
feature_importance = first_layer_weights.abs().sum(dim=0)
feature_importance = feature_importance / feature_importance.sum()

print('=== TOP 10 IMPORTANT FEATURES ===')
for i in range(30):
    print(f'Feature {i}: {feature_importance[i]:.4f}')
    
# ✓ Top features shouldn't all be identical
# ✓ Shows model uses different features
# ✓ Proves model learned patterns (not random)
"
```

---

### Method 6: Progressive Accuracy (Best Proof)

```powershell
python -c "
import json

# Read training history
with open('results/experiment_results.json') as f:
    results = json.load(f)

# Check if accuracy improved during training
print('=== TRAINING PROGRESS ===')
epochs = results['training_history']['epochs']
accuracies = results['training_history']['val_accuracies']

print(f'Epoch 1 accuracy: {accuracies[0]:.4f}')
print(f'Epoch {len(accuracies)} accuracy: {accuracies[-1]:.4f}')
print(f'Improvement: {(accuracies[-1] - accuracies[0]):.4f}')

# ✓ If accuracy went UP from epoch 1 → last epoch
#   → Model definitely learned!
# ✓ If accuracy stayed same or went DOWN
#   → Something wrong (check dataset/config)
"
```

---

# 6. QUICK REFERENCE CHECKLIST

## Before Running Anything

```
□ Dataset is in: c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv
□ Dataset format: CSV with 'Class' column (0=normal, 1=fraud)
□ Dataset size: 10K+ rows
□ Dataset has fraud: At least 100 fraud cases
□ Virtual env active: (.venv) in PowerShell prompt
□ Dependencies installed: pip install -r requirements.txt
```

## Command Execution Order

```
1. Activate env:
   & "c:\Projects\fraud-intelligence-network (1)\.venv\Scripts\Activate.ps1"

2. Verify dataset:
   Test-Path "c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv"

3. Install packages:
   pip install -r requirements.txt

4. Inspect data:
   python -c "import pandas as pd; df=pd.read_csv('data/creditcard.csv'); print(df['Class'].value_counts())"

5. RUN TRAINING (pick one):
   Option A: python main_unified_pipeline.py
   Option B: python train_centralized.py
   Option C: python train_federated.py

6. Start API:
   python api/app.py

7. Test API (in another terminal):
   python api/test_api.py
```

## Verification Checklist

After training completes, verify:

```
□ Accuracy > 95%
□ F1-Score > 0.5
□ Recall > 0.7 (catch fraud)
□ Precision > 0.7 (reduce false alarms)
□ AUC > 0.9
□ Fraud cases get HIGH fraud probability (>0.7)
□ Normal cases get LOW fraud probability (<0.3)
□ Confusion matrix shows few false negatives
□ Training history shows accuracy improving
□ Attack tests show model learned real patterns
```

## Files to Check After Training

```
results/models/
├─ centralized_model.pth          ← Your trained model
├─ federated_model.pth            
└─ dp_protected_model.pth

results/tables/
├─ centralized_results.csv        ← Metrics (accuracy, F1, etc)
├─ federated_round_metrics.csv    ← Training progress
└─ exp3_attack_resistance.csv     ← Proof model learned

results/
└─ experiment_results.json        ← All metrics in JSON
```

---

## Troubleshooting

### Problem: "FileNotFoundError: data/creditcard.csv"

**Solution:**
```powershell
# Make sure file exists in correct location
Test-Path "c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv"

# If False, copy your dataset:
Copy-Item "C:\Path\To\YourDataset.csv" `
          "c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv"
```

---

### Problem: "Class column not found"

**Solution:**
```powershell
# Your CSV must have 'Class' column with 0s and 1s
# Check column names:
python -c "import pandas as pd; print(pd.read_csv('data/creditcard.csv').columns.tolist())"

# If Class column is named differently (e.g., 'label', 'fraud'):
# Edit config.py and utils/data_handler.py

# Or rename in your CSV before uploading
```

---

### Problem: "Accuracy is 50% or random"

**Solution:**
```powershell
# Check if dataset has fraud cases:
python -c "
import pandas as pd
df = pd.read_csv('data/creditcard.csv')
fraud_count = (df['Class'] == 1).sum()
print(f'Fraud cases: {fraud_count}')
# Must be > 100!
"

# If fraud count is 0: Dataset has no fraud, model can't learn
# If fraud count is 1-100: Too few, may not work well
# If fraud count is 100+: Should work
```

---

### Problem: "Out of memory error"

**Solution:**
```powershell
# Dataset too large for GPU
# Edit config.py:

TRAINING_CONFIG = {
    'device': 'cpu',  # Use CPU instead of GPU
    'batch_size': 32,  # Reduce batch size
    ...
}

# Then retry:
python main_unified_pipeline.py
```

---

## Expected Outputs

### Successful Training Output:

```
Loading dataset...
Dataset shape: (284807, 31)
Class distribution:
 0    284315
 1       492
dtype: int64

Training centralized model...
Epoch 1/50: loss=0.4521, val_acc=0.9991
Epoch 2/50: loss=0.4387, val_acc=0.9992
Epoch 3/50: loss=0.4259, val_acc=0.9992
...
Epoch 50/50: loss=0.3856, val_acc=0.9993

Final Results:
Accuracy: 0.9992
Precision: 0.7503
Recall: 0.7729
F1-Score: 0.7615
AUC: 0.9670

Models saved to results/models/
Results saved to results/tables/
```

### Model Successfully Learned Fraud if:

```
✅ Accuracy > 95%
✅ F1-Score > 0.5
✅ Recall > 0.7
✅ Fraud probability > 0.7 for fraud cases
✅ Normal probability > 0.7 for normal cases
✅ Accuracy improved during training
✅ Can catch at least 70% of fraud cases
```

---

# Summary: Your Complete Workflow

```
1. PREPARE
   └─ Ensure dataset format is correct
   └─ Has Class column with 0=normal, 1=fraud

2. UPLOAD
   └─ Copy to: c:\Projects\fraud-intelligence-network (1)\data\creditcard.csv
   └─ Or update config.py with path

3. VERIFY
   └─ Check dataset has fraud cases
   └─ Check all columns are numeric
   └─ Check no missing values

4. TRAIN
   └─ Run: python main_unified_pipeline.py
   └─ Or run specific model training scripts

5. VERIFY MODEL LEARNED
   └─ Check accuracy metrics (>95%)
   └─ Check fraud detection on known cases
   └─ Check confusion matrix
   └─ Run attack simulations

6. DEPLOY
   └─ python api/app.py
   └─ Test: python api/test_api.py

7. USE
   └─ Send transactions to API
   └─ Get fraud predictions with confidence
```

**You're all set!** 🚀
