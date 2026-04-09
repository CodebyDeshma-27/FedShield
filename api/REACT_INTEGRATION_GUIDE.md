# React Dashboard Integration Guide

## Overview
Your FedShield API now provides metrics endpoints that your React dashboard can consume. This guide shows how to integrate them.

---

## Available Endpoints

### Metrics Endpoints
- `GET /metrics` - All model metrics
- `GET /metrics/comparison` - Compare all three models (for charts)
- `GET /metrics/detailed/<model_type>` - Specific model details
- `GET /metrics/attacks` - Attack evaluation results
- `GET /metrics/summary` - Pipeline execution summary
- `GET /graphs/<graph_name>` - Graph images (base64 encoded)
- `GET /export/results` - Full results export

---

## Setup Instructions

### 1. Update Your React Environment Variables
Add to your `.env` file:

```env
REACT_APP_API_URL=http://localhost:5000
```

### 2. Create an API Client Hook

Create `src/hooks/useMetrics.js`:

```javascript
import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const useMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/metrics`);
        if (!response.ok) throw new Error('Failed to fetch metrics');
        const data = await response.json();
        setMetrics(data.models);
        setError(null);
      } catch (err) {
        setError(err.message);
        setMetrics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    // Optionally refresh every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  return { metrics, loading, error };
};

export const useMetricsComparison = () => {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/metrics/comparison`);
        if (!response.ok) throw new Error('Failed to fetch comparison');
        const data = await response.json();
        setComparison(data.models);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, []);

  return { comparison, loading, error };
};
```

---

## React Component Examples

### Example 1: Metrics Summary Card

Create `src/components/MetricsSummary.jsx`:

```jsx
import { useMetrics } from '../hooks/useMetrics';
import { Card } from 'lucide-react';

export const MetricsSummary = () => {
  const { metrics, loading, error } = useMetrics();

  if (loading) return <div className="p-4">Loading metrics...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
  if (!metrics) return null;

  const centralizedModel = metrics.centralized || {};

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card className="p-4">
        <div className="text-sm text-gray-500">Accuracy</div>
        <div className="text-2xl font-bold">{(centralizedModel.accuracy * 100).toFixed(2)}%</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-500">Precision</div>
        <div className="text-2xl font-bold">{(centralizedModel.precision * 100).toFixed(2)}%</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-500">Recall</div>
        <div className="text-2xl font-bold">{(centralizedModel.recall * 100).toFixed(2)}%</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-gray-500">AUC-ROC</div>
        <div className="text-2xl font-bold">{(centralizedModel.auc_roc * 100).toFixed(2)}%</div>
      </Card>
    </div>
  );
};
```

### Example 2: Model Comparison Chart (Recharts)

Create `src/components/ModelComparison.jsx`:

```jsx
import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const ModelComparison = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await fetch(`${API_URL}/metrics/comparison`);
        const result = await response.json();
        setData(result.models);
      } catch (err) {
        console.error('Failed to fetch comparison:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, []);

  if (loading) return <div>Loading comparison...</div>;

  return (
    <div className="w-full h-96 bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Model Performance Comparison</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="accuracy" fill="#3b82f6" name="Accuracy" />
          <Bar dataKey="precision" fill="#10b981" name="Precision" />
          <Bar dataKey="recall" fill="#f59e0b" name="Recall" />
          <Bar dataKey="f1_score" fill="#8b5cf6" name="F1 Score" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### Example 3: Detailed Model Metrics

Create `src/components/DetailedMetrics.jsx`:

```jsx
import { useState, useEffect } from 'react';
import { Button } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const DetailedMetrics = () => {
  const [selectedModel, setSelectedModel] = useState('centralized');
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDetailedMetrics = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/metrics/detailed/${selectedModel}`);
        const data = await response.json();
        setMetrics(data.metrics);
      } catch (err) {
        console.error('Failed to fetch detailed metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetailedMetrics();
  }, [selectedModel]);

  const models = ['centralized', 'federated', 'dp_protected'];

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Detailed Model Metrics</h3>

      {/* Model Selector */}
      <div className="flex gap-2 mb-6">
        {models.map(model => (
          <button
            key={model}
            onClick={() => setSelectedModel(model)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedModel === model
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {model.replace('_', ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {loading && <div>Loading...</div>}

      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">Accuracy</div>
            <div className="text-2xl font-bold text-blue-600">
              {(metrics.accuracy * 100).toFixed(2)}%
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">Precision</div>
            <div className="text-2xl font-bold text-green-600">
              {(metrics.precision * 100).toFixed(2)}%
            </div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">Recall</div>
            <div className="text-2xl font-bold text-yellow-600">
              {(metrics.recall * 100).toFixed(2)}%
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">F1 Score</div>
            <div className="text-2xl font-bold text-purple-600">
              {(metrics.f1_score * 100).toFixed(2)}%
            </div>
          </div>
          <div className="bg-pink-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">AUC-ROC</div>
            <div className="text-2xl font-bold text-pink-600">
              {(metrics.auc_roc * 100).toFixed(2)}%
            </div>
          </div>
          {metrics.privacy_epsilon && (
            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Privacy ε</div>
              <div className="text-2xl font-bold text-indigo-600">
                {metrics.privacy_epsilon}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

### Example 4: Attack Evaluation Results

Create `src/components/AttackEvaluation.jsx`:

```jsx
import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const AttackEvaluation = () => {
  const [attacks, setAttacks] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttacks = async () => {
      try {
        const response = await fetch(`${API_URL}/metrics/attacks`);
        const data = await response.json();
        setAttacks(data.attack_evaluation);
      } catch (err) {
        console.error('Failed to fetch attack data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAttacks();
  }, []);

  if (loading) return <div>Loading attack evaluation...</div>;
  if (!attacks) return null;

  const vulnerable = attacks.vulnerable_model || {};
  const protected = attacks.dp_protected_model || {};

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="text-red-500" />
        <h3 className="text-lg font-semibold">Attack Evaluation Results</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Model Inversion */}
        <div className="border-l-4 border-red-500 pl-4">
          <h4 className="font-semibold mb-2">Model Inversion Attack</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Vulnerable Model MSE:</span>
              <span className="ml-2 font-bold text-red-600">
                {vulnerable.model_inversion?.mse?.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-gray-600">DP Protected Model MSE:</span>
              <span className="ml-2 font-bold text-green-600">
                {protected.model_inversion?.mse?.toFixed(2)}
              </span>
            </div>
            <div className="text-green-600 font-bold mt-2">
              ✓ {protected.model_inversion?.difficulty_multiplier?.toFixed(1)}x more difficult to attack
            </div>
          </div>
        </div>

        {/* Gradient Leakage */}
        <div className="border-l-4 border-orange-500 pl-4">
          <h4 className="font-semibold mb-2">Gradient Leakage Attack</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Vulnerable Reconstruction Loss:</span>
              <span className="ml-2 font-bold text-red-600">
                {vulnerable.gradient_leakage?.reconstruction_loss?.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-gray-600">DP Protected Reconstruction Loss:</span>
              <span className="ml-2 font-bold text-green-600">
                {protected.gradient_leakage?.reconstruction_loss?.toFixed(2)}
              </span>
            </div>
            <div className="text-green-600 font-bold mt-2">
              ✓ Significantly protected against gradient attacks
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## Integration Checklist

- [ ] API is running on `localhost:5000`
- [ ] `.env` file has `REACT_APP_API_URL`
- [ ] Created `useMetrics` hook
- [ ] Imported components in your dashboard
- [ ] Added components to your dashboard pages
- [ ] Tested API endpoints with Postman/Curl
- [ ] Dashboard displays real metrics from API

---

## Testing the API

### Test with Curl

```bash
# Get all metrics
curl http://localhost:5000/metrics

# Get comparison
curl http://localhost:5000/metrics/comparison

# Get detailed metrics for specific model
curl http://localhost:5000/metrics/detailed/centralized
curl http://localhost:5000/metrics/detailed/federated
curl http://localhost:5000/metrics/detailed/dp_protected

# Get attack evaluation
curl http://localhost:5000/metrics/attacks

# Get summary
curl http://localhost:5000/metrics/summary
```

### Test with Python/JavaScript

```javascript
// In your React component or browser console
fetch('http://localhost:5000/metrics/comparison')
  .then(r => r.json())
  .then(data => console.log(data))
```

---

## Dashboard Page Layout Example

```jsx
import { MetricsSummary } from './components/MetricsSummary';
import { ModelComparison } from './components/ModelComparison';
import { DetailedMetrics } from './components/DetailedMetrics';
import { AttackEvaluation } from './components/AttackEvaluation';

export const Dashboard = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">FedShield MVP Dashboard</h1>
      
      <MetricsSummary />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ModelComparison />
        <DetailedMetrics />
      </div>
      
      <AttackEvaluation />
    </div>
  );
};
```

---

## Troubleshooting

### CORS Issues
If you get CORS errors, update your Flask app:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Then install: `pip install flask-cors`

### API Not Responding
- Check API is running: `python api/app.py`
- Verify port 5000 is not blocked
- Check `.env` has correct API URL

### Missing Results
- Run the full pipeline first: `python main.py`
- Check `results/` folder has data

---

## Next Steps for MVP Presentation

1. **Run the full pipeline** to generate results
2. **Start the API**: `python api/app.py`
3. **Extract and run your React dashboard**
4. **Verify components are displaying real data**
5. **Show metrics comparison and attack evaluation results**

Your mentor will see:
- ✅ Real metrics from trained models
- ✅ Federated learning comparison
- ✅ Differential privacy protection evaluation
- ✅ Attack vulnerability analysis
- ✅ Professional React dashboard
