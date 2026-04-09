import { createContext, useContext, useEffect, useState } from "react";

export type Theme = "dark" | "light" | "cyberpunk";

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  chartColors: { primary: string; secondary: string };
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "dark",
  setTheme: () => {},
  chartColors: { primary: "#3B82F6", secondary: "#10B981" },
});

const CHART_COLORS: Record<Theme, { primary: string; secondary: string }> = {
  dark: { primary: "#3B82F6", secondary: "#10B981" },
  light: { primary: "#2563EB", secondary: "#059669" },
  cyberpunk: { primary: "#FF00FF", secondary: "#00FFFF" },
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem("fedshield-theme");
    if (stored === "dark" || stored === "light" || stored === "cyberpunk") return stored;
    return "dark";
  });

  const setTheme = (t: Theme) => {
    setThemeState(t);
    localStorage.setItem("fedshield-theme", t);
  };

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("dark", "cyberpunk", "light");
    if (theme === "dark") root.classList.add("dark");
    else if (theme === "cyberpunk") root.classList.add("cyberpunk", "dark");
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, chartColors: CHART_COLORS[theme] }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
