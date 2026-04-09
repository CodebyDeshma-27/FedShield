import { useTheme } from "@/context/ThemeContext";

interface SectionCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  headerRight?: React.ReactNode;
}

export default function SectionCard({ title, subtitle, children, className = "", headerRight }: SectionCardProps) {
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  return (
    <div
      className={`rounded-xl border bg-card ${
        isCyberpunk ? "border-card-border card-glow" : "border-card-border shadow-sm"
      } ${className}`}
    >
      <div className={`flex items-center justify-between px-5 py-3.5 border-b border-border`}>
        <div>
          <h3 className={`font-semibold text-sm ${isCyberpunk ? "text-primary" : "text-foreground"}`}>{title}</h3>
          {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
        </div>
        {headerRight}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}
