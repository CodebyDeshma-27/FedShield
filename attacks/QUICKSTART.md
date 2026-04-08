# Sprint 4: Quick Reference Card

## 🚀 ONE-LINE QUICK START

```bash
cd c:\Projects\fraud-intelligence-network && python attacks/run_evaluation.py
```

---

## 📋 Your Files

| File | Purpose | Run |
|------|---------|-----|
| `generate_normal.py` | Normal transaction patterns | `python attacks/generate_normal.py` |
| `generate_mule_attack.py` | Mule account fraud patterns | `python attacks/generate_mule_attack.py` |
| `generate_burst_attack.py` | UPI burst attack patterns | `python attacks/generate_burst_attack.py` |
| `run_evaluation.py` | **Main evaluation (use this)** | `python attacks/run_evaluation.py` |

---

## ✅ Dependency Check & Install

```bash
# Check Python version (need 3.8+)
python attacks/run_evaluation.py

# Check if dependencies installed
pip list | grep torch

# If missing, install all:
pip install -r requirements.txt

# Verify key packages:
python -c "import torch; import numpy; import pandas; import opacus; print('✅ All packages installed!')"
```

---

## 🎯 Step-by-Step Execution

### Step 1: Navigate to Project
```bash
cd c:\Projects\fraud-intelligence-network
```

### Step 2: Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 3: Run Complete Evaluation
```bash
python attacks/run_evaluation.py
```

**Expected runtime:** 3-5 minutes

### Step 4: Check Results
```bash
# View text report
type results\attack_evaluation_report.txt

# View JSON results
python -m json.tool results\attack_evaluation_results.json

# Check graphs
dir results\graphs
```

---

## 📊 What Gets Generated

```
results/
├── attack_evaluation_results.json   ---- Machine-readable results
├── attack_evaluation_report.txt     ---- Human-readable report
└── graphs/                          ---- Visualization graphs
    ├── model_inversion_comparison.png
    ├── gradient_leakage_comparison.png
    └── attack_difficulty_summary.png
```

---

## 🎭 Testing Individual Attacks (Optional)

```bash
# Test normal transaction generation
python attacks/generate_normal.py

# Test mule account attack generation
python attacks/generate_mule_attack.py

# Test UPI burst attack generation
python attacks/generate_burst_attack.py
```

---

## 📈 Expected Key Output Metrics

| Metric | Expected | Meaning |
|--------|----------|---------|
| **Model Inversion Difficulty** | 4-6x harder | DP model harder to invert |
| **Gradient Leakage Difficulty** | 5-7x harder | DP gradients harder to leak |
| **Difficulty %** | +400% to +600% | **TARGET: +530%** ✅ |
| **Model Inversion MSE** | Vulnerable: 0.1-0.3, DP: 0.5-0.8 | Higher = better privacy |
| **Gradient Loss** | Vulnerable: 2-5, DP: 10-30 | Higher = harder to attack |

---

## 🔧 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: torch` | `pip install torch` |
| `ModuleNotFoundError: opacus` | `pip install opacus` |
| `Out of Memory` | Reduce batch_size in config.py to 64 |
| `Model not converging` | Increase epochs in config.py to 20 |
| `CUDA out of memory` | Set device to CPU in code (already done) |

---

## 📝 Understanding Output Sections

### Example Output Structure:

```
STEP 1: SETTING UP MODELS
├─ Load dataset ✅
├─ Train vulnerable model (95.2% F1) ✅
└─ Train DP model (91.2% F1) ✅

STEP 2: MODEL INVERSION ATTACKS
├─ Attack vulnerable (MSE: 0.15) ✅
└─ Attack DP (MSE: 0.75) ✅
    → 5.0x harder with DP ✅

STEP 3: GRADIENT LEAKAGE ATTACKS
├─ Attack vulnerable (Loss: 3.2) ✅
└─ Attack DP (Loss: 18.6) ✅
    → 5.8x harder with DP ✅

STEP 4: SYNTHETIC ATTACKS
├─ Generated 500 normal transactions ✅
├─ Generated 300 mule account frauds ✅
└─ Generated 300 UPI burst frauds ✅

STEP 5: ATTACK DIFFICULTY
├─ MI Difficulty: 5.0x ✅
├─ GL Difficulty: 5.8x ✅
├─ Average: 5.4x ✅
└─ Target +530%: ✅ MET ✅

STEP 6: REPORTS GENERATED
├─ JSON results ✅
├─ Text report ✅
└─ Visualizations ✅
```

---

## 💻 File Locations After Execution

```
Your Project Root
│
├── results/
│   ├── attack_evaluation_results.json    ← JSON data
│   ├── attack_evaluation_report.txt      ← Text report
│   ├── graphs/
│   │   ├── model_inversion_comparison.png
│   │   ├── gradient_leakage_comparison.png
│   │   └── attack_difficulty_summary.png
│   └── ...
│
├── attacks/
│   ├── generate_normal.py                ← Your file
│   ├── generate_mule_attack.py           ← Your file
│   ├── generate_burst_attack.py          ← Your file
│   ├── run_evaluation.py                 ← Your main file
│   ├── model_inversion.py                ← Already exists
│   ├── gradient_leakage.py               ← Already exists
│   └── README_SPRINT4.md                 ← Detailed guide
│
└── ...
```

---

## 🎯 Success Criteria

✅ Code runs without errors
✅ `results/attack_evaluation_report.txt` generated
✅ `results/attack_evaluation_results.json` generated
✅ Attack difficulty shows +500% or higher
✅ All 4 attack types documented (MI, GL, Mule, Burst)

---

## 📚 Understanding Your Contribution

### What You're Proving:
1. **Differential Privacy works** ✅ (attacks 5-6x harder)
2. **Specific fraud patterns detected well** ✅ (mule, burst)
3. **Model resistant to gradient theft** ✅ (federated learning safe)
4. **No accuracy-privacy tradeoff needed** ✅ (acceptable F1 with DP)

### Your Attack Types:
- **Mule Account:** ₹50K-₹500K intermediary transfers
- **UPI Burst:** ₹100-₹500 rapid-fire transactions
- **Model Inversion:** Reconstruct training data from weights
- **Gradient Leakage:** Reconstruct training data from gradients

---

## ⏱️ Timeline

| Task | Time |
|------|------|
| Install deps | 1-2 min |
| Run evaluation | 3-5 min |
| Review results | 1-2 min |
| **TOTAL** | **5-10 min** ✅ |

---

## 🔗 Integration with Other Sprints

```
Sprint 1 ✅  Data Pipeline (friend did)
    ↓
Sprint 2 ✅  Federated Learning (friend did)
    ↓
Sprint 3 ✅  Differential Privacy (friend did)
    ↓
Sprint 4 → YOU → Attack Validation (+530% difficulty)
    ↓
Sprint 5 → Run all experiments + graphs
    ↓
Sprint 6 → Final report
```

---

## 🚀 Next Command After This Sprint

Once Sprint 4 complete:

```bash
python experiments/all_experiments.py
```

This runs all 4 experiments:
1. Accuracy comparison
2. Privacy-accuracy tradeoff
3. Attack resistance (your part)
4. Communication efficiency

---

**You're done with the basics! Run the command above and check results.** 🎉
