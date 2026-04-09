import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useTheme } from "@/context/ThemeContext";
import SectionCard from "@/components/ui/SectionCard";
import { CheckCircle } from "lucide-react";
import { RefreshCw } from "lucide-react";
import useMetrics from "@/hooks/useMetrics";
import { fetchAttackMetrics } from "@/lib/apiClient";

function CircularProgress({ pct, label, sublabel }: { pct: number; label: string; sublabel: string }) {
  const r = 60;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;

  return (
    <div className="flex flex-col items-center gap-3">
      <svg viewBox="0 0 160 160" className="w-40 h-40">
        <circle cx="80" cy="80" r={r} fill="none" stroke="hsl(var(--muted))" strokeWidth="14" />
        <circle
          cx="80" cy="80" r={r} fill="none"
          stroke="hsl(var(--primary))" strokeWidth="14"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 80 80)"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
        <text x="80" y="74" textAnchor="middle" fontSize="22" fontWeight="700" fill="hsl(var(--foreground))">{label}</text>
        <text x="80" y="94" textAnchor="middle" fontSize="10" fill="hsl(var(--muted-foreground))">{sublabel}</text>
      </svg>
      <p className="text-xs text-muted-foreground">{pct.toFixed(1)}% of total budget consumed</p>
    </div>
  );
}

export default function PrivacyMonitor() {
  const { chartColors } = useTheme();
  const { metrics, error, refetch } = useMetrics();
  const [attackMetrics, setAttackMetrics] = useState<Record<string, any> | null>(null);

  const dpProtected = metrics?.models?.dp_protected;
  const epsilonConsumed = dpProtected?.privacy_epsilon ?? 0;
  const epsilonTotal = 10.0;
  const budgetPct = Math.min(100, (epsilonConsumed / epsilonTotal) * 100);
  const privacyChartData = [
    { metric: "Accuracy", value: dpProtected?.accuracy ?? 0 },
    { metric: "Precision", value: dpProtected?.precision ?? 0 },
    { metric: "Recall", value: dpProtected?.recall ?? 0 },
    { metric: "F1 Score", value: dpProtected?.f1_score ?? 0 },
    { metric: "AUC", value: dpProtected?.auc_roc ?? 0 },
  ];

  useEffect(() => {
    fetchAttackMetrics()
      .then((result) => setAttackMetrics(result.attack_evaluation ?? null))
      .catch(() => setAttackMetrics(null));
  }, []);

  const attackStatuses = [
    {
      attack: "Model Inversion",
      status: attackMetrics?.model_inversion ? "Protected" : "Unknown",
      detail: attackMetrics?.model_inversion
        ? `DP raises attack cost by ${(attackMetrics.model_inversion.difficulty_multiplier ?? 1).toFixed(2)}x`
        : "Awaiting backend summary",
    },
    {
      attack: "Gradient Leakage",
      status: attackMetrics?.gradient_leakage ? "Protected" : "Unknown",
      detail: attackMetrics?.gradient_leakage
        ? `Adversarial leakage difficulty ${(attackMetrics.gradient_leakage.difficulty_multiplier ?? 1).toFixed(2)}x`
        : "Awaiting backend summary",
    },
    {
      attack: "Synthetic Patterns",
      status: attackMetrics?.synthetic_patterns ? "Monitored" : "Unknown",
      detail: attackMetrics?.synthetic_patterns
        ? "Pattern integrity checks active"
        : "Awaiting backend summary",
    },
  ];

  return (
    <div className="space-y-5">
      {error ? (
        <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-700">
          Backend metrics unavailable: {error}
        </div>
      ) : null}

      <div className="grid lg:grid-cols-2 gap-5">
        <SectionCard title="Privacy Budget Tracker" subtitle="Differential Privacy epsilon (ε) usage">
          <div className="flex flex-col items-center gap-4 py-2">
            <CircularProgress
              pct={budgetPct}
              label={`ε ${epsilonConsumed.toFixed(2)}`}
              sublabel={`of ${epsilonTotal.toFixed(1)}`}
            />
            <div className="w-full grid grid-cols-3 gap-3">
              {[
                { label: "Consumed", value: `ε ${epsilonConsumed.toFixed(2)}`, color: "text-primary" },
                { label: "Remaining", value: `ε ${(epsilonTotal - epsilonConsumed).toFixed(2)}`, color: "text-accent" },
                { label: "Total Budget", value: `ε ${epsilonTotal.toFixed(1)}`, color: "text-muted-foreground" },
              ].map(({ label, value, color }) => (
                <div key={label} className="text-center">
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className={`text-sm font-bold ${color}`}>{value}</p>
                </div>
              ))}
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Differential Privacy Configuration" subtitle="Current DP parameters">
          <div className="space-y-3">
            {[
              { label: "Privacy Budget (ε)", value: `ε ${epsilonConsumed.toFixed(2)}`, desc: "Overall privacy budget used" },
              { label: "Delta (δ)", value: dpProtected?.privacy_delta ?? 1e-5, desc: "Privacy failure probability" },
              { label: "Protected Model", value: dpProtected ? "True" : "Unknown", desc: "DP protects the federated model" },
              { label: "Model Accuracy", value: dpProtected?.accuracy ? `${(dpProtected.accuracy * 100).toFixed(2)}%` : "Loading...", desc: "DP model accuracy" },
              { label: "AUC-ROC", value: dpProtected?.auc_roc ? `${(dpProtected.auc_roc * 100).toFixed(2)}%` : "Loading...", desc: "DP model ROC score" },
            ].map(({ label, value, desc }) => (
              <div key={label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <p className="text-sm font-medium text-foreground">{label}</p>
                  <p className="text-xs text-muted-foreground">{desc}</p>
                </div>
                <span className="font-mono text-sm font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">{value}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Protected Model Metrics" subtitle="DP model performance from backend results">
        <div className="flex justify-end mb-2">
          <button
            onClick={refetch}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            title="Refresh data"
          >
            <RefreshCw className="w-3 h-3" />
            Refresh
          </button>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={privacyChartData} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="metric" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              formatter={(val: number) => [`${(val * 100).toFixed(2)}%`, "Value"]}
            />
            <Bar dataKey="value" fill={chartColors.primary} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </SectionCard>

      <SectionCard title="Attack Resistance Status" subtitle="Privacy-preserving defense mechanisms">
        <div className="grid sm:grid-cols-3 gap-4">
          {attackStatuses.map(({ attack, status, detail }) => (
            <div key={attack} className="rounded-xl border border-green-500/30 bg-green-500/5 p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
                <span className="text-sm font-semibold text-green-500">{status}</span>
              </div>
              <p className="text-sm font-medium text-foreground">{attack}</p>
              <p className="text-xs text-muted-foreground">{detail}</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
