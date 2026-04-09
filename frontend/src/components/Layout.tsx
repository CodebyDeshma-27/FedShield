import { useState, useRef, useEffect } from "react";
import { useLocation } from "wouter";
import {
  Shield, LayoutDashboard, Search, Lock, Network,
  FlaskConical, Activity, Menu, X, Sun, Moon, Zap, ChevronRight,
  LogOut, User, ChevronDown
} from "lucide-react";
import { useTheme, type Theme } from "@/context/ThemeContext";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/analyzer", label: "Transaction Analyzer", icon: Search },
  { path: "/privacy", label: "Privacy Monitor", icon: Lock },
  { path: "/federated", label: "Federated Learning", icon: Network },
  { path: "/experiments", label: "Experiments", icon: FlaskConical },
  { path: "/api-health", label: "API Health", icon: Activity },
];

const themeOptions: { value: Theme; label: string; icon: React.ReactNode }[] = [
  { value: "dark", label: "Dark", icon: <Moon className="w-4 h-4" /> },
  { value: "light", label: "Light", icon: <Sun className="w-4 h-4" /> },
  { value: "cyberpunk", label: "Cyberpunk", icon: <Zap className="w-4 h-4" /> },
];

function UserMenu() {
  const { user, logout } = useAuth();
  const [, navigate] = useLocation();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (!user) {
    return (
      <button
        onClick={() => navigate("/login")}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
          isCyberpunk ? "bg-fuchsia-500/20 border border-fuchsia-500/40 text-fuchsia-400 hover:bg-fuchsia-500/30" : "bg-primary text-primary-foreground hover:opacity-90"
        }`}
      >
        Login
      </button>
    );
  }

  const initials = user.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-2 px-2 py-1.5 rounded-lg transition-all hover:bg-muted/40 ${isCyberpunk ? "border border-fuchsia-500/20" : ""}`}
      >
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
          isCyberpunk ? "bg-fuchsia-500/30 text-fuchsia-400 border border-fuchsia-500/40" : "bg-primary/20 text-primary"
        }`}>
          {initials}
        </div>
        <div className="hidden sm:flex flex-col items-start leading-none">
          <span className="text-xs font-semibold text-foreground">{user.name}</span>
          <span className="text-xs text-muted-foreground">{user.bank}</span>
        </div>
        <ChevronDown className="w-3.5 h-3.5 text-muted-foreground hidden sm:block" />
      </button>

      {open && (
        <div className="absolute right-0 mt-1 w-48 rounded-xl border shadow-lg overflow-hidden bg-popover border-popover-border z-50">
          <div className="px-4 py-3 border-b border-border">
            <p className="text-xs font-semibold text-foreground truncate">{user.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
          <button
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-xs text-foreground hover:bg-muted/40 transition-colors"
            onClick={() => setOpen(false)}
          >
            <User className="w-3.5 h-3.5 text-muted-foreground" />
            Profile
          </button>
          <button
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-xs text-destructive hover:bg-destructive/10 transition-colors border-t border-border"
            onClick={() => { logout(); navigate("/login"); setOpen(false); }}
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location, navigate] = useLocation();
  const { theme, setTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showThemeDropdown, setShowThemeDropdown] = useState(false);
  const themeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (themeRef.current && !themeRef.current.contains(e.target as Node)) setShowThemeDropdown(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const currentPage = navItems.find((n) => n.path === location)?.label ?? "Dashboard";
  const isCyberpunk = theme === "cyberpunk";

  const sidebarBg = "bg-sidebar border-r border-sidebar-border";
  const navLinkBase = "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200";
  const navLinkActive = isCyberpunk
    ? "bg-primary/20 text-primary border border-primary/40 glow-primary"
    : "bg-sidebar-accent text-sidebar-primary";
  const navLinkInactive = "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground";

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative inset-y-0 left-0 z-30 w-64 flex flex-col ${sidebarBg} transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        } ${isCyberpunk ? "card-glow" : ""}`}
      >
        <div className="flex items-center gap-3 px-5 py-4 border-b border-sidebar-border">
          <div className={`p-2 rounded-lg ${isCyberpunk ? "bg-primary/20 border border-primary/40" : "bg-primary/10"}`}>
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <div>
            <span className={`text-base font-bold ${isCyberpunk ? "text-primary" : "text-foreground"}`}>FedShield</span>
            <p className="text-xs text-muted-foreground">Fraud Detection</p>
          </div>
          <button className="ml-auto lg:hidden text-muted-foreground" onClick={() => setSidebarOpen(false)}>
            <X className="w-4 h-4" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location === path;
            return (
              <a
                key={path}
                href={path}
                onClick={(e) => { e.preventDefault(); navigate(path); setSidebarOpen(false); }}
                className={`${navLinkBase} ${isActive ? navLinkActive : navLinkInactive}`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="flex-1">{label}</span>
                {isActive && <ChevronRight className="w-3 h-3 opacity-60" />}
              </a>
            );
          })}
        </nav>

        <div className="px-4 py-3 border-t border-sidebar-border">
          <p className="text-xs text-muted-foreground text-center">FedShield v2.4.1 — Secure</p>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className={`flex items-center gap-3 px-4 lg:px-6 py-3 border-b border-border bg-background/80 backdrop-blur-sm ${isCyberpunk ? "border-primary/40" : ""}`}>
          <button className="lg:hidden text-muted-foreground hover:text-foreground" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2 min-w-0">
            <Shield className="w-4 h-4 text-primary shrink-0" />
            <h1 className={`text-sm font-semibold truncate ${isCyberpunk ? "text-primary" : "text-foreground"}`}>{currentPage}</h1>
          </div>

          <div className="ml-auto flex items-center gap-2">
            {/* System Online badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-green-500 text-xs font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 pulse-dot" />
              System Online
            </div>

            {/* Theme switcher */}
            <div ref={themeRef} className="relative">
              <button
                onClick={() => setShowThemeDropdown(!showThemeDropdown)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                  isCyberpunk ? "border-primary/40 bg-primary/10 text-primary" : "border-border bg-secondary text-secondary-foreground hover:bg-accent/10"
                }`}
              >
                {themeOptions.find((t) => t.value === theme)?.icon}
                <span className="hidden sm:inline">{themeOptions.find((t) => t.value === theme)?.label}</span>
              </button>
              {showThemeDropdown && (
                <div className="absolute right-0 mt-1 w-36 rounded-lg border shadow-lg z-50 overflow-hidden bg-popover border-popover-border">
                  {themeOptions.map((opt) => (
                    <button
                      key={opt.value}
                      className={`w-full flex items-center gap-2 px-3 py-2 text-xs text-left transition-colors hover:bg-accent hover:text-accent-foreground ${
                        theme === opt.value ? "bg-accent/50 text-accent-foreground font-semibold" : "text-popover-foreground"
                      }`}
                      onClick={() => { setTheme(opt.value); setShowThemeDropdown(false); }}
                    >
                      {opt.icon}
                      {opt.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* User menu */}
            <UserMenu />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
