import { useState } from "react";
import { useLocation } from "wouter";
import { Shield, Eye, EyeOff, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

export default function Login() {
  const [, navigate] = useLocation();
  const { login } = useAuth();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password, remember);
      navigate("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const bgClass = isCyberpunk
    ? "bg-gradient-to-br from-zinc-950 via-purple-950 to-zinc-950"
    : theme === "dark"
    ? "bg-gradient-to-br from-slate-900 via-slate-900 to-black"
    : "bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100";

  const cardClass = isCyberpunk
    ? "bg-zinc-900/80 border border-fuchsia-500/40 card-glow"
    : theme === "dark"
    ? "bg-slate-800/60 border border-slate-700/50"
    : "bg-white/80 border border-gray-200 shadow-xl";

  const inputClass = `w-full px-4 py-2.5 rounded-lg border text-sm transition-all outline-none focus:ring-2 bg-transparent ${
    isCyberpunk
      ? "border-fuchsia-500/40 focus:ring-fuchsia-500/40 focus:border-fuchsia-500 text-foreground placeholder-muted-foreground"
      : "border-border focus:ring-primary/30 focus:border-primary text-foreground placeholder-muted-foreground"
  }`;

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 ${bgClass}`}>
      {/* Background glow for cyberpunk */}
      {isCyberpunk && (
        <>
          <div className="fixed top-1/4 left-1/4 w-96 h-96 bg-fuchsia-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="fixed bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        </>
      )}

      <div
        className={`w-full max-w-md rounded-2xl backdrop-blur-md p-8 ${cardClass} animate-in fade-in slide-in-from-bottom-4 duration-500`}
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className={`p-3 rounded-2xl mb-4 ${isCyberpunk ? "bg-fuchsia-500/20 border border-fuchsia-500/40" : "bg-primary/10"}`}>
            <Shield className={`w-8 h-8 ${isCyberpunk ? "text-fuchsia-400" : "text-primary"}`} />
          </div>
          <h1 className={`text-2xl font-bold ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>
            FedShield
          </h1>
          <p className="text-xs text-muted-foreground mt-1 text-center">
            Secure Federated Intelligence for Fraud Detection
          </p>
        </div>

        <h2 className={`text-lg font-semibold mb-6 ${isCyberpunk ? "text-cyan-400 font-mono" : "text-foreground"}`}>
          Sign in to your account
        </h2>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email Address</label>
            <input
              type="email"
              required
              placeholder="admin@bank.com"
              className={inputClass}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                className={`${inputClass} pr-10`}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                className="w-4 h-4 accent-primary rounded"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <span className="text-xs text-muted-foreground">Remember me</span>
            </label>
            <button
              type="button"
              onClick={() => navigate("/forgot-password")}
              className={`text-xs font-medium transition-colors ${isCyberpunk ? "text-cyan-400 hover:text-cyan-300" : "text-primary hover:text-primary/80"}`}
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 ${
              isCyberpunk
                ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black glow-primary"
                : "bg-primary hover:opacity-90 text-primary-foreground"
            }`}
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Don't have an account?{" "}
          <button
            onClick={() => navigate("/register")}
            className={`font-medium transition-colors ${isCyberpunk ? "text-cyan-400 hover:text-cyan-300" : "text-primary hover:text-primary/80"}`}
          >
            Create account
          </button>
        </p>

        <p className="mt-3 text-center text-xs text-muted-foreground/50">
          Demo: any email + password (min 3 chars)
        </p>
      </div>
    </div>
  );
}
