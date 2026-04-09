# 🚀 FedShield Frontend-Backend Integration Setup

**⚠️ IMPORTANT**: This guide connects your React frontend to Python backend WITHOUT modifying the ML engine.

---

## 📋 What You Have

✅ **Backend** (Working):
- Flask REST API at `http://localhost:5000`
- Machine Learning pipeline (main.py)
- Real metrics in `results/` directory
- All endpoints ready: `/metrics`, `/graphs`, `/export/csv`, etc.

✅ **Frontend** (To Connect):
- React 18 dashboard with charts
- TypeScript for type safety
- Tailwind CSS for styling
- Recharts for data visualization

---

## 🎯 Integration Layers

```
┌─────────────────────────────────────────────────────┐
│  React Frontend (Port 5173)                         │
│  Dashboard / Charts / Tables                        │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP Requests
                 │ (REST API calls)
                 │
┌────────────────▼────────────────────────────────────┐
│  API Client (apiClient.ts)                          │
│  - Fetch metrics from backend                       │
│  - Download CSVs                                    │
│  - Stream graphs                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Fetch from
                 │ /metrics, /graphs, /export/csv
                 │
┌────────────────▼────────────────────────────────────┐
│  Flask Backend (Port 5000) - DO NOT MODIFY          │
│  - Serves real ML results                           │
│  - Generates metrics JSONs                          │
│  - Serves graph images & CSVs                       │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start (5 minutes)

### **Step 1: Install Frontend Dependencies** 

```bash
cd c:\Projects\FedShield\frontend
npm install
```

Or with pnpm (if Replit used it):
```bash
pnpm install
```

### **Step 2: Install Backend CORS Support**

```bash
cd c:\Projects\FedShield
# Activate venv
.\venv\Scripts\Activate

# Install flask-cors (already added to requirements.txt)
pip install flask-cors
```

### **Step 3: Run Backend API**

In one terminal (keep it running):
```bash
cd c:\Projects\FedShield
python api/app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### **Step 4: Run Frontend**

In another terminal:
```bash
cd c:\Projects\FedShield\frontend
npm run dev
```

Expected output:
```
VITE v4.3.0  ready in XYZ ms

➜  Local:   http://localhost:5173/
```

### **Step 5: Open in Browser**

Navigate to: **http://localhost:5173**

---

## 🔧 Integration Details

### **What Changed**

1. **backend**: Added CORS support in `api/app.py` (line ~36)
   - Allows frontend to request data from different port
   - No changes to ML logic or models

2. **frontend**: Created integration layer
   - `src/lib/apiClient.ts` - HTTP client for API calls
   - `src/hooks/useMetrics.ts` - React hook to fetch real metrics
   - `.env` - Configuration file

3. **Real data flow**:
   ```
   Frontend Component
   ↓ (uses hook)
   useMetrics()
   ↓ (calls function)
   apiClient.fetchMetrics()
   ↓ (HTTP GET)
   http://localhost:5000/metrics
   ↓ (returns JSON)
   Display in Dashboard
   ```

---

## 📊 What Data Displays

### **Dashboard Section** - Real Metrics
- Centralized model accuracy: **99.71%**
- Federated model accuracy: **99.69%**
- Privacy budget (ε): **0.5**
- Training time: Real from backend

### **Federated Learning Page** - Training Graphs
- Per-round loss curves
- Convergence plots
- Privacy epsilon spending
- Bank contribution charts

### **Privacy Monitor** - Real DP Metrics
- Privacy budget breakdown
- Attack resistance scores
- Privacy-utility tradeoff

### **Experiments** - Model Comparison
- All 5 models side-by-side
- Accuracy, Precision, Recall, F1
- Downloaded from results/tables/*.csv

---

## 🔌 API Endpoints Being Used

| Endpoint | Purpose | Frontend Page |
|----------|---------|--------------|
| `GET /health` | Check API status | ApiHealth |
| `GET /metrics` | Get all model metrics | Dashboard |
| `GET /metrics/comparison` | Compare models | Experiments |
| `GET /metrics/summary` | Summary stats | Dashboard |
| `GET /graphs` | List available graphs | FederatedLearning |
| `GET /export/csv?model=X` | Download CSV | Any page |

---

## 🐛 Troubleshooting

### **Error: "Cannot reach backend"**
```
Solution:
1. Verify Flask is running: http://localhost:5000 in browser
2. Check frontend .env has: VITE_API_URL=http://localhost:5000
3. Restart both services
```

### **Error: "CORS error" or "blocked by CORS"**
```
Solution:
1. Verify CORS is enabled in api/app.py (line ~36)
2. Check flask-cors is installed: pip install flask-cors
3. Restart Flask API
```

### **Metrics show as 0 or NaN**
```
Solution:
1. Run: python main.py (to generate metrics)
2. Check results/ directory has data
3. Verify backend /metrics endpoint returns JSON
4. Check browser console for API errors
```

### **Frontend won't start**
```
Solution:
1. Delete node_modules: rm -r node_modules
2. Clear cache: npm cache clean --force
3. Reinstall: npm install
4. Start: npm run dev
```

---

## 📁 File Structure

```
c:\Projects\FedShield\
├── frontend/                          ← React app
│   ├── src/
│   │   ├── lib/
│   │   │   ├── apiClient.ts          ← NEW: API HTTP client
│   │   │   └── api.ts                ← OLD: mock data (keep)
│   │   ├── hooks/
│   │   │   ├── useMetrics.ts         ← NEW: fetch metrics hook
│   │   │   └── use-*.ts              ← Other hooks
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          ← Shows real metrics
│   │   │   ├── FederatedLearning.tsx ← Shows training graphs
│   │   │   └── Experiments.tsx        ← Model comparison
│   │   └── data/
│   │       └── mockData.ts            ← Fallback if API fails
│   ├── .env                           ← NEW: API URL config
│   ├── package.json
│   └── tsconfig.json
│
├── api/
│   ├── app.py                         ← MODIFIED: Added CORS
│   ├── requirements.txt               ← MODIFIED: Added flask-cors
│   └── README.md
│
├── main.py                            ← ML pipeline (UNCHANGED)
├── config.py                          ← Config (UNCHANGED)
└── results/
    ├── tables/                        ← CSVs generated by main.py
    └── graphs/                        ← PNGs generated by main.py
```

---

## ✅ Success Checklist

- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend CORS configured (checked api/app.py line ~36)
- [ ] flask-cors installed (`pip install flask-cors`)
- [ ] .env file exists with `VITE_API_URL=http://localhost:5000`
- [ ] Backend running (`python api/app.py` on port 5000)
- [ ] Frontend running (`npm run dev` on port 5173)
- [ ] Frontend opens without errors at `http://localhost:5173`
- [ ] Dashboard shows real metrics (not mock data)
- [ ] Can see model accuracy: 99.7%+
- [ ] Graphs/charts are displaying
- [ ] Can download CSVs

---

## 🎯 Showing to Your Mentor

### **Demo Flow**

1. **Open Frontend** → http://localhost:5173
2. **Login** (any email/password for demo)
3. **Dashboard Page**
   - Shows: "Centralized Model 99.71% Accuracy"
   - Shows: "Federated Model 99.69% Accuracy"
   - Real data from backend
4. **Federated Learning Page**
   - Shows: Training convergence curves
   - Shows: 5 banks, 10 rounds
   - Real graphs from results/graphs/
5. **Experiments Page**
   - Shows: Model comparison table
   - Shows: All 5 models side-by-side
   - Real CSVs from results/tables/
6. **Privacy Monitor**
   - Shows: Privacy budget spending (ε)
   - Shows: Attack resistance
   - Real DP metrics

---

## 🚨 IMPORTANT: Do NOT Modify

These files control your ML pipeline. **Leave them alone**:
- ✅ `main.py` - Don't change
- ✅ `federated/server.py` - Don't change
- ✅ `federated/client.py` - Don't change
- ✅ `models/fraud_detector.py` - Don't change
- ✅ `config.py` - Don't change

Only modify frontend (`frontend/src`) and API wrapper (`api/app.py` CORS).

---

## 📞 Quick Reference

### **Start Everything**
```bash
# Terminal 1 - Backend
cd c:\Projects\FedShield
python api/app.py

# Terminal 2 - Frontend  
cd c:\Projects\FedShield\frontend
npm run dev

# Terminal 3 - Generate fresh metrics (optional)
cd c:\Projects\FedShield
python main.py
```

### **Test Endpoints**
```bash
# Check backend
curl http://localhost:5000/health

# Get metrics
curl http://localhost:5000/metrics

# Download CSV
curl http://localhost:5000/export/csv?model=centralized > results.csv
```

### **Common Ports**
- Backend API: `5000`
- Frontend Dev: `5173` (Vite) or `3000` (if using Create React App)
- Metrics Dashboard: `http://localhost:5173`

---

## 🎓 What You're Teaching Your Mentor

1. **Federated Learning** - Real metrics showing distributed training
2. **Privacy-Preserving ML** - DP implementation with epsilon tracking
3. **Full-Stack Architecture** - React frontend + Python backend
4. **REST API Integration** - Real-time data sync
5. **Professional UI/UX** - Charts, tables, live metrics

---

**Created**: April 9, 2026  
**Status**: Ready for Integration ✅
