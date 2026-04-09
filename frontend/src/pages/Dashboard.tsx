import { Activity, AlertTriangle, Shield, Server, RefreshCw } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { useTheme } from "@/context/ThemeContext";
import StatCard from "@/components/ui/StatCard";
import SectionCard from "@/components/ui/SectionCard";
import useMetrics from "@/hooks/useMetrics";

function DatasetSummary({ summary }: { summary: any }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Total Samples", value: summary?.data_summary?.total_samples ?? "n/a" },
          { label: "Fraud Cases", value: summary?.data_summary?.fraud_count ?? "n/a" },
          { label: "Training Samples", value: summary?.data_summary?.train_samples ?? "n/a" },
          { label: "Validation Samples", value: summary?.data_summary?.val_samples ?? "n/a" },
        ].map((item) => (
          <div key={item.label} className="rounded-xl border border-border bg-muted/30 p-4">
            <p className="text-xs text-muted-foreground">{item.label}</p>
            <p className="text-lg font-semibold text-foreground mt-1">{item.value.toLocaleString ? item.value.toLocaleString() : item.value}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border border-border bg-muted/30 p-4">
        <p className="text-xs text-muted-foreground">Dataset File</p>
        <p className="text-sm font-semibolid text-foreground mt-1">{summary?.data_summary?.dataset ?? "Unknown"}</p>
        <p className="text-xs text-muted-foreground mt-2">Features: {summary?.data_summary?.features ?? "n/a"}</p>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { chartColors } = useTheme();
  const { metrics, summary, apiHealth, loading, error, refetch } = useMetrics();
  const federated = metrics?.models?.federated;
  const dpProtected = metrics?.models?.dp_protected;
  const centralized = metrics?.models?.centralized;
  const trainedCount = [centralized, federated, dpProtected].filter((model) => model?.status === "trained").length;
  const sampleSplitData = [
    { label: "Total", value: summary?.data_summary?.total_samples ?? 0 },
    { label: "Fraud", value: summary?.data_summary?.fraud_count ?? 0 },
    { label: "Normal", value: summary?.data_summary?.normal_count ?? 0 },
  ];

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 rounded-xl skeleton" />
          ))}
        </div>
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="h-64 rounded-xl skeleton" />
          <div className="h-64 rounded-xl skeleton" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* KPI Cards */}
      {error ? (
        <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-700">
          Failed to load backend metrics: {error}
        </div>
      ) : null}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Federated Accuracy"
          value={federated?.accuracy ? `${(federated.accuracy * 100).toFixed(2)}%` : "Loading..."}
          subtitle="From backend metrics"
          icon={<Activity className="w-5 h-5" />}
          color="blue"
        />
        <StatCard
          title="Federated F1 Score"
          value={federated?.f1_score ? `${(federated.f1_score * 100).toFixed(2)}%` : "Loading..."}
          subtitle="Latest trained model"
          icon={<AlertTriangle className="w-5 h-5" />}
          color="red"
        />
        <StatCard
          title="DP Privacy Budget"
          value={dpProtected?.privacy_epsilon !== undefined ? `ε ${dpProtected.privacy_epsilon}/10` : "Loading..."}
          subtitle={dpProtected?.privacy_delta !== undefined ? `δ ${dpProtected.privacy_delta}` : "Using backend DP model"}
          icon={<Shield className="w-5 h-5" />}
          color="amber"
        >
          <div className="w-full bg-muted rounded-full h-1.5 mt-1">
            <div
              className="bg-amber-500 h-1.5 rounded-full"
              style={{ width: dpProtected?.privacy_epsilon ? `${Math.min(dpProtected.privacy_epsilon * 10, 100)}%` : "20%" }}
            />
          </div>
        </StatCard>
        <StatCard
          title="Models Trained"
          value={`${trainedCount} / 3`}
          subtitle={apiHealth?.status ? `API ${apiHealth.status}` : "Backend health"}
          icon={<Server className="w-5 h-5" />}
          color="green"
        />
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-4">
        <SectionCard title="Dataset Sample Counts" subtitle="Backend dataset summary from pipeline results">
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
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={sampleSplitData} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
              <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
              <Tooltip
                contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                formatter={(value: number) => [value.toLocaleString(), "Samples"]}
              />
              <Line type="monotone" dataKey="value" stroke={chartColors.primary} strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="Pipeline Summary" subtitle="Counts, dataset path and feature size">
          <DatasetSummary summary={summary} />
        </SectionCard>
      </div>

      <SectionCard title="Pipeline and Model Summary" subtitle="Real metadata from the backend results file">
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            { label: "Pipeline Status", value: summary?.pipeline_status ?? "unknown" },
            { label: "Models Trained", value: summary?.models_count ?? 0 },
            { label: "Trained Model IDs", value: summary?.models_trained?.join(", ") ?? "none" },
            { label: "Backend Health", value: apiHealth?.status ?? "unknown" },
          ].map((item) => (
            <div key={item.label} className="rounded-xl border border-border bg-muted/30 p-4">
              <p className="text-xs text-muted-foreground">{item.label}</p>
              <p className="text-sm font-semibold text-foreground mt-1">{item.value}</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
