import { useTheme } from "@/context/ThemeContext";

interface RiskBadgeProps {
  level: "HIGH" | "MEDIUM" | "LOW" | string;
}

export default function RiskBadge({ level }: RiskBadgeProps) {
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  const classes: Record<string, string> = {
    HIGH: isCyberpunk
      ? "bg-red-500/20 text-red-400 border border-red-500/50"
      : "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
    MEDIUM: isCyberpunk
      ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/50"
      : "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400",
    LOW: isCyberpunk
      ? "bg-green-500/20 text-green-400 border border-green-500/50"
      : "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${classes[level] ?? classes.LOW}`}>
      {level}
    </span>
  );
}
