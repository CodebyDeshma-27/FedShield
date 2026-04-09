import { useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { useTheme } from "@/context/ThemeContext";
import SectionCard from "@/components/ui/SectionCard";
import { RefreshCw } from "lucide-react";
import useMetrics from "@/hooks/useMetrics";

const CURRENT_ROUND = 15;
const TOTAL_ROUNDS = 20;

export default function FederatedLearning() {
  const { chartColors } = useTheme();
  const { metrics, comparison, summary, error, refetch } = useMetrics();
  const federated = metrics?.models?.federated;
  const centralized = metrics?.models?.centralized;
  const dpProtected = metrics?.models?.dp_protected;
  const globalAccuracy = federated?.accuracy ?? 0.941;
  const progressPct = ((summary?.models_count ?? 3) / TOTAL_ROUNDS) * 100;

  const sampleSplitData = [
    { segment: "Train", value: summary?.data_summary?.train_samples ?? 0 },
    { segment: "Validation", value: summary?.data_summary?.val_samples ?? 0 },
    { segment: "Test", value: summary?.data_summary?.test_samples ?? 0 },
  ];

  const accuracyChartData = useMemo(() => {
    if (!comparison?.models?.length) {
      return [
        { model: "Centralized", accuracy: 94.1 },
        { model: "Federated", accuracy: 94.0 },
        { model: "Federated+DP", accuracy: 93.5 },
      ];
    }

    return comparison.models.map((item) => ({
      model: item.name,
      accuracy: item.accuracy,
    }));
  }, [comparison]);

  const modelStatusTable = [
    {
      name: "Centralized",
      status: centralized?.status ?? "unknown",
      localAccuracy: centralized?.accuracy ? `${(centralized.accuracy * 100).toFixed(2)}%` : "--",
      lastUpdate: centralized ? "Now" : "Pending",
    },
    {
      name: "Federated",
      status: federated?.status ?? "unknown",
      localAccuracy: federated?.accuracy ? `${(federated.accuracy * 100).toFixed(2)}%` : "--",
      lastUpdate: federated ? "Now" : "Pending",
    },
    {
      name: "Federated+DP",
      status: dpProtected?.status ?? "unknown",
      localAccuracy: dpProtected?.accuracy ? `${(dpProtected.accuracy * 100).toFixed(2)}%` : "--",
      lastUpdate: dpProtected ? "Now" : "Pending",
    },
  ];

  return (
    <div className="space-y-5">
      {/* FL Status */}
      <SectionCard title="Federated Learning Training Status">
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-foreground font-medium">
              Round {CURRENT_ROUND} of {TOTAL_ROUNDS}
            </span>
            <span className="font-semibold text-primary">
              Global Accuracy: {(globalAccuracy * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-3">
            <div
              className="bg-primary h-3 rounded-full transition-all duration-700"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Round 1</span>
            <span>{progressPct.toFixed(0)}% complete</span>
            <span>Round {TOTAL_ROUNDS}</span>
          </div>
          <div className="grid grid-cols-3 gap-3 mt-2">
            {[
              { label: "Aggregation", value: "FedAvg" },
              { label: "Participating Banks", value: "4/5" },
              { label: "Avg Local Epochs", value: "3" },
            ].map(({ label, value }) => (
              <div key={label} className="bg-muted/30 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-sm font-bold text-foreground mt-0.5">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionCard>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Data Split */}
        <SectionCard title="Dataset Split" subtitle="Training/validation/test sample counts from backend">
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
            <BarChart data={sampleSplitData} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="segment" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
              <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickFormatter={(v) => v.toLocaleString()} />
              <Tooltip
                contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                formatter={(val: number) => [val.toLocaleString(), "Samples"]}
              />
              <Bar dataKey="value" fill={chartColors.primary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>

        {/* Accuracy Comparison */}
        <SectionCard title="Model Accuracy Comparison" subtitle="Backend-driven model performance">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={accuracyChartData} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="model" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
              <YAxis domain={[0, 100]} tickFormatter={(v) => `${v.toFixed(0)}%`} tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} />
              <Tooltip
                contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                formatter={(val: number) => [`${val.toFixed(2)}%`, "Accuracy"]}
              />
              <Bar dataKey="accuracy" fill={chartColors.secondary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>
      </div>

      <SectionCard title="Model Training Status" subtitle="Current status for each saved model">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Model', 'Status', 'Accuracy', 'Last Update'].map((h) => (
                  <th key={h} className="pb-2 text-left text-xs font-medium text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {modelStatusTable.map((row) => (
                <tr key={row.name} className="hover:bg-muted/30 transition-colors">
                  <td className="py-2.5 text-sm font-medium text-foreground">{row.name}</td>
                  <td className="py-2.5">
                    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full ${
                      row.status === "trained"
                        ? "bg-green-500/10 text-green-500"
                        : row.status === "unknown"
                        ? "bg-yellow-500/10 text-yellow-500"
                        : "bg-red-500/10 text-red-500"
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${row.status === "trained" ? "bg-green-500" : row.status === "unknown" ? "bg-yellow-500" : "bg-red-500"}`} />
                      {row.status}
                    </span>
                  </td>
                  <td className="py-2.5 text-sm font-mono text-foreground">{row.localAccuracy}</td>
                  <td className="py-2.5 text-xs text-muted-foreground">{row.lastUpdate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}
