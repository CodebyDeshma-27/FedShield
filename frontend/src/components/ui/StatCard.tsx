import { useTheme } from "@/context/ThemeContext";

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  color?: "blue" | "green" | "amber" | "red" | "purple";
  children?: React.ReactNode;
}

const colorMap = {
  blue: { bg: "bg-blue-500/10", text: "text-blue-500", border: "border-blue-500/30" },
  green: { bg: "bg-green-500/10", text: "text-green-500", border: "border-green-500/30" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-500", border: "border-amber-500/30" },
  red: { bg: "bg-red-500/10", text: "text-red-500", border: "border-red-500/30" },
  purple: { bg: "bg-purple-500/10", text: "text-purple-500", border: "border-purple-500/30" },
};

export default function StatCard({ title, value, subtitle, icon, color = "blue", children }: StatCardProps) {
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";
  const c = colorMap[color];

  return (
    <div
      className={`rounded-xl border p-4 bg-card transition-all duration-200 hover:scale-[1.01] ${
        isCyberpunk ? `border-card-border card-glow` : "border-card-border shadow-sm hover:shadow-md"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide truncate">{title}</p>
          <p className={`mt-1 text-2xl font-bold ${isCyberpunk ? "text-primary" : "text-foreground"}`}>{value}</p>
          {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
          {children && <div className="mt-2">{children}</div>}
        </div>
        <div className={`p-2.5 rounded-lg shrink-0 ${c.bg} ${isCyberpunk ? `border ${c.border}` : ""}`}>
          <div className={c.text}>{icon}</div>
        </div>
      </div>
    </div>
  );
}
