import { useState, useEffect, useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
  LineChart, Line,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";
import { useTheme } from "@/context/ThemeContext";
import SectionCard from "@/components/ui/SectionCard";
import { ChevronDown, ChevronUp, RefreshCw } from "lucide-react";
import useMetrics from "@/hooks/useMetrics";
import { fetchAttackMetrics } from "@/lib/apiClient";

function ExperimentCard({ title, description, children, onRefresh }: { title: string; description: string; children: React.ReactNode; onRefresh?: () => void }) {
  const [open, setOpen] = useState(true);
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  return (
    <div className={`rounded-xl border bg-card overflow-hidden ${isCyberpunk ? "border-card-border card-glow" : "border-card-border shadow-sm"}`}>
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-muted/20 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <div>
          <h3 className={`font-semibold text-sm ${isCyberpunk ? "text-primary" : "text-foreground"}`}>{title}</h3>
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={(e) => { e.stopPropagation(); onRefresh(); }}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
              title="Refresh data"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          )}
          {open ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
        </div>
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-border">
          <div className="pt-4">{children}</div>
        </div>
      )}
    </div>
  );
}

export default function Experiments() {
  const { chartColors, theme } = useTheme();
  const [attackMetrics, setAttackMetrics] = useState<Record<string, any> | null>(null);
  const { metrics, comparison, error, refetch } = useMetrics();
  const isCyberpunk = theme === "cyberpunk";

  const c3 = isCyberpunk ? "#FFFF00" : theme === "dark" ? "#8B5CF6" : "#7C3AED";
  const radarColor = chartColors.primary;

  const centralizedComparison = comparison?.models?.find((m) => m.name.toLowerCase().includes("centralized"));
  const federatedComparison = comparison?.models?.find((m) => m.name.toLowerCase() === "federated");
  const dpComparison = comparison?.models?.find((m) => m.name.toLowerCase().includes("dp"));

  useEffect(() => {
    fetchAttackMetrics()
      .then((result) => setAttackMetrics(result))
      .catch(() => setAttackMetrics(null));
  }, []);

  const experimentAccuracyData = useMemo(() => {
    if (!comparison?.models?.length) {
      return [];
    }

    return [
      {
        metric: "Accuracy",
        centralized: centralizedComparison?.accuracy ?? 0,
        federated: federatedComparison?.accuracy ?? 0,
        federatedDP: dpComparison?.accuracy ?? 0,
      },
      {
        metric: "Precision",
        centralized: centralizedComparison?.precision ?? 0,
        federated: federatedComparison?.precision ?? 0,
        federatedDP: dpComparison?.precision ?? 0,
      },
      {
        metric: "Recall",
        centralized: centralizedComparison?.recall ?? 0,
        federated: federatedComparison?.recall ?? 0,
        federatedDP: dpComparison?.recall ?? 0,
      },
      {
        metric: "F1 Score",
        centralized: centralizedComparison?.f1_score ?? 0,
        federated: federatedComparison?.f1_score ?? 0,
        federatedDP: dpComparison?.f1_score ?? 0,
      },
    ];
  }, [comparison, centralizedComparison, federatedComparison, dpComparison]);

  const privacyUtilityTradeoff = useMemo(() => {
    if (!comparison?.models?.length) {
      return [];
    }

    return [
      {
        epsilon: 0,
        accuracy: centralizedComparison?.accuracy ?? 0,
        label: "Centralized",
      },
      {
        epsilon: metrics?.models?.dp_protected?.privacy_epsilon ?? 1,
        accuracy: dpComparison?.accuracy ?? 0,
        label: "DP Protected",
      },
    ];
  }, [comparison, metrics, centralizedComparison, dpComparison]);

  const attackRadarData = useMemo(() => {
    const evaluation = attackMetrics?.attack_evaluation ?? {};

    return [
      {
        attack: "Model Inversion",
        score: Math.min(100, ((evaluation?.model_inversion as any)?.difficulty_multiplier ?? 1) * 20),
      },
      {
        attack: "Gradient Leakage",
        score: Math.min(100, ((evaluation?.gradient_leakage as any)?.difficulty_multiplier ?? 1) * 20),
      },
      {
        attack: "Synthetic Patterns",
        score: Math.min(100, ((evaluation?.synthetic_patterns as any)?.normal ?? 100)),
      },
    ];
  }, [attackMetrics]);

  const commEfficiencyData = useMemo(() => {
    if (!comparison?.models?.length) {
      return [];
    }

    return [
      { model: centralizedComparison?.name ?? "Centralized", accuracy: centralizedComparison?.accuracy ?? 0 },
      { model: federatedComparison?.name ?? "Federated", accuracy: federatedComparison?.accuracy ?? 0 },
      { model: dpComparison?.name ?? "Federated+DP", accuracy: dpComparison?.accuracy ?? 0 },
    ];
  }, [comparison, centralizedComparison, federatedComparison, dpComparison]);

  return (
    <div className="space-y-4">
      {/* Exp 1: Accuracy Comparison */}
      <ExperimentCard
        title="Experiment 1 — Accuracy Comparison"
        description="Centralized vs Federated vs Federated+DP across key metrics"
        onRefresh={refetch}
      >
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={experimentAccuracyData} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="metric" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis domain={[0, 100]} tickFormatter={(v) => `${v.toFixed(0)}%`} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              formatter={(val: number) => `${val.toFixed(2)}%`}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="centralized" name="Centralized" fill={chartColors.primary} radius={[4, 4, 0, 0]} />
            <Bar dataKey="federated" name="Federated" fill={chartColors.secondary} radius={[4, 4, 0, 0]} />
            <Bar dataKey="federatedDP" name="Federated+DP" fill={c3} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ExperimentCard>

      {/* Exp 2: Privacy-Utility Tradeoff */}
      <ExperimentCard
        title="Experiment 2 — Privacy-Utility Tradeoff"
        description="Model accuracy as differential privacy budget (ε) increases"
        onRefresh={refetch}
      >
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={privacyUtilityTradeoff}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="epsilon" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} label={{ value: "ε (epsilon)", position: "insideBottom", offset: -2, fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis domain={[0.7, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              formatter={(val: number) => [`${(val * 100).toFixed(1)}%`, "Accuracy"]}
            />
            <Line type="monotone" dataKey="accuracy" stroke={chartColors.primary} strokeWidth={2.5} dot={{ r: 4, fill: chartColors.primary }} />
          </LineChart>
        </ResponsiveContainer>
      </ExperimentCard>

      {/* Exp 3: Attack Resistance Radar */}
      <ExperimentCard
        title="Experiment 3 — Attack Resistance"
        description="Resistance scores across different adversarial attack types"
        onRefresh={refetch}
      >
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={attackRadarData} cx="50%" cy="50%" outerRadius={100}>
            <PolarGrid stroke="hsl(var(--border))" />
            <PolarAngleAxis dataKey="attack" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }} />
            <Radar
              name="Resistance Score"
              dataKey="score"
              stroke={radarColor}
              fill={radarColor}
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              formatter={(val: number) => [`${val}/100`, "Score"]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </ExperimentCard>

      {/* Exp 4: Communication Efficiency */}
      <ExperimentCard
        title="Experiment 4 — Communication Efficiency"
        description="Model accuracy across centralized, federated and DP-protected variants"
        onRefresh={refetch}
      >
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={commEfficiencyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="model" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} label={{ value: "Model Variant", position: "insideBottom", offset: -2, fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis domain={[0.55, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              formatter={(val: number) => [`${(val * 100).toFixed(1)}%`, "Accuracy"]}
            />
            <Line type="monotone" dataKey="accuracy" stroke={chartColors.secondary} strokeWidth={2.5} dot={{ r: 3, fill: chartColors.secondary }} />
          </LineChart>
        </ResponsiveContainer>
      </ExperimentCard>
    </div>
  );
}
