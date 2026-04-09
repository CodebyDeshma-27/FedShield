import { CheckCircle, XCircle, RefreshCw } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import SectionCard from "@/components/ui/SectionCard";
import useMetrics from "@/hooks/useMetrics";

const ENDPOINTS = [
  {
    method: "GET",
    path: "/health",
    desc: "Backend health check",
  },
  {
    method: "GET",
    path: "/metrics",
    desc: "Latest model metrics",
  },
  {
    method: "GET",
    path: "/metrics/comparison",
    desc: "Model comparison metrics",
  },
];

export default function ApiHealth() {
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";
  const { apiHealth, summary, refetch } = useMetrics();
  const endpointStatus = apiHealth ? "Online" : "Offline";

  return (
    <div className="space-y-5">
      <SectionCard title="Backend Health Summary" subtitle="Live /health response from backend API">
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
        <div className="grid sm:grid-cols-4 gap-4">
          {[
            { label: "Status", value: apiHealth?.status ?? "unknown" },
            { label: "Model", value: apiHealth?.model ?? "unknown" },
            { label: "Privacy", value: apiHealth?.privacy?.protected ? `ε ${apiHealth?.privacy?.epsilon}, δ ${apiHealth?.privacy?.delta}` : "not available" },
            { label: "Accuracy", value: apiHealth?.accuracy ? `${(apiHealth.accuracy * 100).toFixed(2)}%` : "n/a" },
          ].map((item) => (
            <div key={item.label} className="rounded-xl border border-border p-3 bg-muted/50">
              <p className="text-xs text-muted-foreground">{item.label}</p>
              <p className="text-sm font-semibold text-foreground mt-1">{item.value}</p>
            </div>
          ))}
        </div>
      </SectionCard>

      {/* Endpoint Cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        {ENDPOINTS.map((ep) => (
          <div
            key={ep.path}
            className={`rounded-xl border p-4 bg-card ${isCyberpunk ? "border-card-border card-glow" : "border-card-border shadow-sm"} hover:scale-[1.01] transition-all`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-1.5">
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${ep.method === "GET" ? "bg-blue-500/10 text-blue-500" : "bg-purple-500/10 text-purple-500"}`}>
                  {ep.method}
                </span>
                <code className="text-xs text-foreground font-mono">{ep.path}</code>
              </div>
              {endpointStatus === "Online"
                ? <CheckCircle className="w-4 h-4 text-green-500" />
                : <XCircle className="w-4 h-4 text-red-500" />
              }
            </div>
            <p className="text-xs text-muted-foreground mb-3">{ep.desc}</p>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-muted/30 rounded-lg p-2">
                <p className="text-xs text-muted-foreground">Status</p>
                <p className="text-sm font-bold text-foreground mt-0.5">{endpointStatus}</p>
              </div>
              <div className="bg-muted/30 rounded-lg p-2">
                <p className="text-xs text-muted-foreground">Last Updated</p>
                <p className="text-sm font-bold text-foreground mt-0.5">{summary?.timestamp ? new Date(summary.timestamp).toLocaleString() : "n/a"}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <SectionCard title="Pipeline Summary" subtitle="Results extracted from `results/pipeline_results.json`">
          <div className="grid gap-3">
            {[
              { label: "Pipeline Status", value: summary?.pipeline_status ?? "unknown" },
              { label: "Dataset", value: summary?.data_summary?.dataset ?? "unknown" },
              { label: "Total Samples", value: summary?.data_summary?.total_samples?.toLocaleString() ?? "n/a" },
              { label: "Fraud Count", value: summary?.data_summary?.fraud_count?.toLocaleString() ?? "n/a" },
              { label: "Models Trained", value: summary?.models_count ?? 0 },
              { label: "Trained Models", value: summary?.models_trained?.join(", ") ?? "none" },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-border bg-muted/30 p-4">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="text-sm font-semibold text-foreground mt-1">{item.value}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="API / Model Details" subtitle="Live backend health and privacy state">
          <div className="space-y-4">
            <div className="rounded-xl border border-border bg-muted/30 p-4">
              <p className="text-xs text-muted-foreground">Backend Model</p>
              <p className="text-sm font-semibold text-foreground mt-1">{apiHealth?.model ?? "unknown"}</p>
            </div>
            <div className="rounded-xl border border-border bg-muted/30 p-4">
              <p className="text-xs text-muted-foreground">Device</p>
              <p className="text-sm font-semibold text-foreground mt-1">{apiHealth?.device ?? "unknown"}</p>
            </div>
            <div className="rounded-xl border border-border bg-muted/30 p-4">
              <p className="text-xs text-muted-foreground">DP Guarantee</p>
              <p className="text-sm font-semibold text-foreground mt-1">{apiHealth?.privacy?.protected ? "Enabled" : "Unavailable"}</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
