import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useTheme } from "@/context/ThemeContext";
import SectionCard from "@/components/ui/SectionCard";
import RiskBadge from "@/components/ui/RiskBadge";

interface PredictionResult {
  fraud_probability: number;
  risk_level: string;
  important_features: { feature: string; score: number }[];
}

interface TxHistory {
  id: string;
  amount: string;
  merchant: string;
  hour: number;
  risk: string;
  probability: number;
}

const merchantOptions = ["Food", "Travel", "Shopping", "Entertainment", "Utilities", "Other"];
const dayOptions = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function GaugeChart({ probability }: { probability: number }) {
  const pct = Math.round(probability * 100);
  const color = pct >= 70 ? "#EF4444" : pct >= 40 ? "#F59E0B" : "#10B981";
  const angle = -90 + pct * 1.8;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox="0 0 200 120" className="w-48">
        <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="hsl(var(--muted))" strokeWidth="16" strokeLinecap="round" />
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={`${pct * 2.513} 999`}
        />
        <line
          x1="100" y1="100"
          x2={100 + 55 * Math.cos((angle * Math.PI) / 180)}
          y2={100 + 55 * Math.sin((angle * Math.PI) / 180)}
          stroke={color} strokeWidth="3" strokeLinecap="round"
        />
        <circle cx="100" cy="100" r="5" fill={color} />
        <text x="100" y="85" textAnchor="middle" fontSize="22" fontWeight="700" fill={color}>{pct}%</text>
        <text x="100" y="112" textAnchor="middle" fontSize="10" fill="hsl(var(--muted-foreground))">Fraud Probability</text>
      </svg>
      <div className="flex gap-4 text-xs text-muted-foreground">
        <span>0%</span><span className="flex-1 text-center">50%</span><span>100%</span>
      </div>
    </div>
  );
}

let txCounter = 1000;

export default function TransactionAnalyzer() {
  const { chartColors } = useTheme();
  const [form, setForm] = useState({
    amount: "",
    merchant: "Shopping",
    hour: 12,
    day: "Monday",
    distance: "",
    online: false,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [history, setHistory] = useState<TxHistory[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    // TODO: Replace with real API call to http://localhost:5000/predict
    await new Promise((r) => setTimeout(r, 1200));

    const amt = parseFloat(form.amount) || 100;
    const dist = parseFloat(form.distance) || 10;
    const prob = Math.min(0.99, Math.max(0.01,
      (amt > 5000 ? 0.35 : 0) +
      (dist > 100 ? 0.25 : 0) +
      (form.online ? 0.1 : 0) +
      (form.hour < 4 || form.hour > 22 ? 0.15 : 0) +
      Math.random() * 0.2
    ));

    const mock: PredictionResult = {
      fraud_probability: parseFloat(prob.toFixed(2)),
      risk_level: prob >= 0.7 ? "HIGH" : prob >= 0.4 ? "MEDIUM" : "LOW",
      important_features: [
        { feature: "amount", score: parseFloat((0.6 + Math.random() * 0.3).toFixed(2)) },
        { feature: "distance_from_home", score: parseFloat((0.4 + Math.random() * 0.3).toFixed(2)) },
        { feature: "merchant_category", score: parseFloat((0.2 + Math.random() * 0.3).toFixed(2)) },
        { feature: "transaction_hour", score: parseFloat((0.1 + Math.random() * 0.2).toFixed(2)) },
      ].sort((a, b) => b.score - a.score),
    };

    setResult(mock);
    txCounter++;
    setHistory((prev) => [
      {
        id: `TX-${txCounter}`,
        amount: `$${amt.toFixed(2)}`,
        merchant: form.merchant,
        hour: form.hour,
        risk: mock.risk_level,
        probability: mock.fraud_probability,
      },
      ...prev.slice(0, 9),
    ]);
    setLoading(false);
  };

  return (
    <div className="space-y-5">
      <div className="grid lg:grid-cols-2 gap-5">
        {/* Form */}
        <SectionCard title="Transaction Details" subtitle="Enter transaction attributes">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Amount ($)</label>
                <input
                  type="number" min="0" step="0.01"
                  placeholder="e.g. 1250.00"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-muted/30 text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Distance from Home (km)</label>
                <input
                  type="number" min="0" step="0.1"
                  placeholder="e.g. 45"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-muted/30 text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  value={form.distance}
                  onChange={(e) => setForm({ ...form, distance: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Merchant Category</label>
                <select
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-muted/30 text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  value={form.merchant}
                  onChange={(e) => setForm({ ...form, merchant: e.target.value })}
                >
                  {merchantOptions.map((m) => <option key={m}>{m}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Day of Week</label>
                <select
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-muted/30 text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  value={form.day}
                  onChange={(e) => setForm({ ...form, day: e.target.value })}
                >
                  {dayOptions.map((d) => <option key={d}>{d}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-2">
                Transaction Hour: {form.hour}:00
              </label>
              <input
                type="range" min={0} max={23} step={1}
                className="w-full accent-primary"
                value={form.hour}
                onChange={(e) => setForm({ ...form, hour: parseInt(e.target.value) })}
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-0.5">
                <span>0:00</span><span>12:00</span><span>23:00</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setForm({ ...form, online: !form.online })}
                className={`relative inline-flex h-5 w-10 shrink-0 rounded-full border-2 transition-all ${
                  form.online ? "bg-primary border-primary" : "bg-muted border-border"
                }`}
              >
                <span className={`inline-block h-3.5 w-3.5 mt-0.5 rounded-full bg-white shadow transition-transform ${form.online ? "translate-x-4.5" : "translate-x-0.5"}`} />
              </button>
              <span className="text-sm text-foreground">
                {form.online ? "Online Transaction" : "In-Person Transaction"}
              </span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2.5 bg-primary text-primary-foreground rounded-lg text-sm font-semibold hover:opacity-90 disabled:opacity-50 transition-all"
            >
              {loading ? "Analyzing..." : "Analyze Transaction"}
            </button>
          </form>
        </SectionCard>

        {/* Result */}
        <div className="space-y-4">
          {loading && (
            <SectionCard title="Analyzing...">
              <div className="space-y-3">
                <div className="h-32 skeleton rounded-xl" />
                <div className="h-4 skeleton rounded" />
                <div className="h-4 skeleton rounded w-3/4" />
              </div>
            </SectionCard>
          )}

          {!loading && result && (
            <>
              <SectionCard title="Prediction Result">
                <div className="flex flex-col items-center gap-3">
                  <GaugeChart probability={result.fraud_probability} />
                  <RiskBadge level={result.risk_level.toUpperCase()} />
                  <p className="text-xs text-muted-foreground text-center">
                    Model confidence: {(result.fraud_probability * 100).toFixed(1)}% fraud probability
                  </p>
                </div>
              </SectionCard>

              <SectionCard title="Feature Importance">
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={result.important_features} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis type="number" domain={[0, 1]} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
                    <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} width={110} />
                    <Tooltip
                      contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                    />
                    <Bar dataKey="score" fill={chartColors.primary} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </SectionCard>
            </>
          )}

          {!loading && !result && (
            <SectionCard title="Result">
              <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
                Submit a transaction to see the prediction
              </div>
            </SectionCard>
          )}
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <SectionCard title="Transaction History" subtitle="Last 10 analyzed transactions">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  {["TX ID", "Amount", "Merchant", "Hour", "Probability", "Risk"].map((h) => (
                    <th key={h} className="pb-2 text-left text-xs font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((tx) => (
                  <tr key={tx.id} className="hover:bg-muted/30 transition-colors">
                    <td className="py-2 font-mono text-xs">{tx.id}</td>
                    <td className="py-2 text-xs font-semibold">{tx.amount}</td>
                    <td className="py-2 text-xs">{tx.merchant}</td>
                    <td className="py-2 text-xs">{tx.hour}:00</td>
                    <td className="py-2 text-xs">{(tx.probability * 100).toFixed(1)}%</td>
                    <td className="py-2"><RiskBadge level={tx.risk} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}
    </div>
  );
}
