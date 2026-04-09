/**
 * Example FedShield Dashboard Component
 * Copy this to your React project and customize as needed
 * 
 * Requirements:
 * - React 18+
 * - Recharts (npm install recharts)
 * - Tailwind CSS configured
 * - .env file with REACT_APP_API_URL
 * 
 * Usage:
 * import Dashboard from './Dashboard';
 * 
 * Then use: <Dashboard />
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { AlertTriangle, TrendingUp, ShieldCheck, Database } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Metric Card Component
const MetricCard = ({ title, value, unit = '%', color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
    red: 'bg-red-50 text-red-600 border-red-200',
  };

  return (
    <div className={`p-6 rounded-lg border-l-4 ${colorClasses[color]}`}>
      <div className="text-sm font-medium text-gray-600">{title}</div>
      <div className="text-3xl font-bold mt-2">
        {typeof value === 'number' ? value.toFixed(2) : value}
        <span className="text-lg ml-1">{unit}</span>
      </div>
    </div>
  );
};

// Metrics Summary Section
const MetricsSummary = ({ metrics }) => {
  if (!metrics || !metrics.centralized) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    );
  }

  const m = metrics.centralized;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <MetricCard
        title="Accuracy"
        value={m.accuracy * 100}
        color="blue"
      />
      <MetricCard
        title="Precision"
        value={m.precision * 100}
        color="green"
      />
      <MetricCard
        title="Recall"
        value={m.recall * 100}
        color="orange"
      />
      <MetricCard
        title="F1 Score"
        value={m.f1_score * 100}
        color="purple"
      />
      <MetricCard
        title="AUC-ROC"
        value={m.auc_roc * 100}
        color="blue"
      />
    </div>
  );
};

// Model Comparison Chart
const ModelComparisonChart = ({ comparisonData }) => {
  if (!comparisonData || comparisonData.length === 0) {
    return (
      <div className="w-full h-96 bg-white p-6 rounded-lg shadow flex items-center justify-center">
        <div className="text-gray-400">Loading comparison data...</div>
      </div>
    );
  }

  const colors = ['#3b82f6', '#10b981', '#8b5cf6'];

  return (
    <div className="w-full h-full bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <TrendingUp size={20} />
        Model Performance Comparison
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={comparisonData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="accuracy" fill="#3b82f6" name="Accuracy" />
          <Bar dataKey="precision" fill="#10b981" name="Precision" />
          <Bar dataKey="recall" fill="#f59e0b" name="Recall" />
          <Bar dataKey="auc_roc" fill="#8b5cf6" name="AUC-ROC" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Detailed Metrics Section
const DetailedMetrics = ({ metrics }) => {
  const [selectedModel, setSelectedModel] = useState('centralized');

  if (!metrics) {
    return <div className="text-gray-400">Loading metrics...</div>;
  }

  const modelData = metrics[selectedModel];
  const models = Object.keys(metrics);
  const modelNames = {
    'centralized': 'Centralized',
    'federated': 'Federated Learning',
    'dp_protected': 'DP-Protected'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Database size={20} />
        Detailed Model Metrics
      </h3>

      {/* Model Selector */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {models.map(model => (
          <button
            key={model}
            onClick={() => setSelectedModel(model)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedModel === model
                ? 'bg-blue-500 text-white shadow-lg'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {modelNames[model] || model}
          </button>
        ))}
      </div>

      {/* Metrics Grid */}
      {modelData && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <MetricCard title="Accuracy" value={modelData.accuracy * 100} color="blue" />
          <MetricCard title="Precision" value={modelData.precision * 100} color="green" />
          <MetricCard title="Recall" value={modelData.recall * 100} color="orange" />
          <MetricCard title="F1 Score" value={modelData.f1_score * 100} color="purple" />
          <MetricCard title="AUC-ROC" value={modelData.auc_roc * 100} color="pink" />
          
          {modelData.privacy_epsilon && (
            <MetricCard
              title="Privacy ε (epsilon)"
              value={modelData.privacy_epsilon}
              unit=""
              color="red"
            />
          )}
        </div>
      )}

      {/* Model Info */}
      {modelData && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-gray-700">
            <strong>Status:</strong> {modelData.status || 'trained'}
          </p>
          {modelData.privacy_epsilon && (
            <p className="text-sm text-gray-700 mt-2">
              <strong>Privacy Protected:</strong> Model trained with differential privacy (ε={modelData.privacy_epsilon})
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Attack Evaluation Section
const AttackEvaluation = ({ attacks }) => {
  if (!attacks || !attacks.vulnerable_model) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle size={20} className="text-red-500" />
          Attack Evaluation Results
        </h3>
        <div className="text-gray-400">Loading attack evaluation...</div>
      </div>
    );
  }

  const vulnerable = attacks.vulnerable_model || {};
  const protected_model = attacks.dp_protected_model || {};

  const modelInversionVul = vulnerable.model_inversion || {};
  const modelInversionProt = protected_model.model_inversion || {};
  const gradientLeakageVul = vulnerable.gradient_leakage || {};
  const gradientLeakageProt = protected_model.gradient_leakage || {};

  const miDifficulty = modelInversionProt.difficulty_multiplier || 1;
  const glDifficulty = gradientLeakageProt.reconstruction_loss/ gradientLeakageVul.reconstruction_loss || 1;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <ShieldCheck size={20} className="text-green-500" />
        Attack Evaluation Results
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Inversion Attack */}
        <div className="border-l-4 border-red-500 pl-4 py-2">
          <h4 className="font-semibold text-red-700 mb-3">Model Inversion Attack</h4>
          <div className="space-y-2 text-sm mb-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Vulnerable Model MSE:</span>
              <span className="font-bold text-red-600">{modelInversionVul.mse?.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">DP Protected Model MSE:</span>
              <span className="font-bold text-green-600">{modelInversionProt.mse?.toFixed(2)}</span>
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <p className="text-green-700 font-bold">
              ✓ {miDifficulty.toFixed(1)}x more difficult to attack
            </p>
            <p className="text-xs text-green-600 mt-1">
              Higher MSE means harder to reconstruct data
            </p>
          </div>
        </div>

        {/* Gradient Leakage Attack */}
        <div className="border-l-4 border-orange-500 pl-4 py-2">
          <h4 className="font-semibold text-orange-700 mb-3">Gradient Leakage Attack</h4>
          <div className="space-y-2 text-sm mb-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Vulnerable Recon Loss:</span>
              <span className="font-bold text-red-600">
                {gradientLeakageVul.reconstruction_loss?.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">DP Protected Recon Loss:</span>
              <span className="font-bold text-green-600">
                {gradientLeakageProt.reconstruction_loss?.toFixed(2)}
              </span>
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <p className="text-green-700 font-bold">
              ✓ {glDifficulty.toFixed(1)}x higher reconstruction loss
            </p>
            <p className="text-xs text-green-600 mt-1">
              Significantly protected against gradient attacks
            </p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Summary:</strong> Differential Privacy protection makes model attacks significantly harder.
          The DP-protected model demonstrates concrete privacy guarantees against real attacks.
        </p>
      </div>
    </div>
  );
};

// Main Dashboard Component
export const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [comparison, setComparison] = useState([]);
  const [attacks, setAttacks] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch metrics
        const metricsRes = await fetch(`${API_URL}/metrics`);
        if (!metricsRes.ok) throw new Error('Failed to fetch metrics');
        const metricsData = await metricsRes.json();
        setMetrics(metricsData.models);

        // Fetch comparison data
        const compRes = await fetch(`${API_URL}/metrics/comparison`);
        if (!compRes.ok) throw new Error('Failed to fetch comparison');
        const compData = await compRes.json();
        setComparison(compData.models || []);

        // Fetch attack data
        const attackRes = await fetch(`${API_URL}/metrics/attacks`);
        if (!attackRes.ok) throw new Error('Failed to fetch attacks');
        const attackData = await attackRes.json();
        setAttacks(attackData.attack_evaluation);
      } catch (err) {
        setError(err.message);
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-bold mb-2">Connection Error</h2>
            <p className="text-red-700">
              Cannot connect to API at {API_URL}
            </p>
            <p className="text-red-700 text-sm mt-2">
              Make sure the API is running: <code className="bg-red-100 px-2 py-1">python api/app.py</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">FedShield MVP</h1>
          <p className="text-gray-600">
            Production-grade Federated Learning for Fraud Detection with Differential Privacy
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">Loading metrics from API...</p>
          </div>
        )}

        {/* Metrics Summary */}
        {!loading && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Current Model Metrics</h2>
              <MetricsSummary metrics={metrics} />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ModelComparisonChart comparisonData={comparison} />
              <DetailedMetrics metrics={metrics} />
            </div>

            {/* Attack Evaluation */}
            <AttackEvaluation attacks={attacks} />

            {/* Footer Info */}
            <div className="bg-gray-100 p-6 rounded-lg text-sm text-gray-600">
              <p>
                <strong>API Endpoint:</strong> {API_URL}
              </p>
              <p className="mt-2">
                Last updated: {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
