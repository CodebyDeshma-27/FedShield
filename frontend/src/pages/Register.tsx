import { useState } from "react";
import { useLocation } from "wouter";
import { Shield, Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

function getPasswordStrength(password: string): { label: string; score: number; color: string } {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (score <= 1) return { label: "Weak", score, color: "bg-red-500" };
  if (score === 2) return { label: "Fair", score, color: "bg-amber-500" };
  if (score === 3) return { label: "Good", score, color: "bg-yellow-400" };
  return { label: "Strong", score, color: "bg-green-500" };
}

const rules = [
  { test: (p: string) => p.length >= 8, label: "At least 8 characters" },
  { test: (p: string) => /[A-Z]/.test(p), label: "One uppercase letter" },
  { test: (p: string) => /[0-9]/.test(p), label: "One number" },
  { test: (p: string) => /[^A-Za-z0-9]/.test(p), label: "One special character" },
];

export default function Register() {
  const [, navigate] = useLocation();
  const { register } = useAuth();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  const [form, setForm] = useState({ bankName: "", adminName: "", email: "", password: "", confirm: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const strength = getPasswordStrength(form.password);
  const passwordMismatch = form.confirm.length > 0 && form.password !== form.confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) { setError("Passwords do not match"); return; }
    if (strength.score < 3) { setError("Please use a stronger password"); return; }
    setLoading(true);
    try {
      await register(form.bankName, form.adminName, form.email, form.password);
      navigate("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
      {isCyberpunk && (
        <>
          <div className="fixed top-1/4 left-1/4 w-96 h-96 bg-fuchsia-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="fixed bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        </>
      )}

      <div className={`w-full max-w-md rounded-2xl backdrop-blur-md p-8 ${cardClass} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
        {/* Logo */}
        <div className="flex flex-col items-center mb-6">
          <div className={`p-3 rounded-2xl mb-3 ${isCyberpunk ? "bg-fuchsia-500/20 border border-fuchsia-500/40" : "bg-primary/10"}`}>
            <Shield className={`w-7 h-7 ${isCyberpunk ? "text-fuchsia-400" : "text-primary"}`} />
          </div>
          <h1 className={`text-xl font-bold ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>Create Account</h1>
          <p className="text-xs text-muted-foreground mt-1 text-center">Register your bank on FedShield</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Bank Name</label>
              <input
                required placeholder="First National Bank"
                className={inputClass}
                value={form.bankName}
                onChange={(e) => setForm({ ...form, bankName: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Admin Name</label>
              <input
                required placeholder="John Smith"
                className={inputClass}
                value={form.adminName}
                onChange={(e) => setForm({ ...form, adminName: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email Address</label>
            <input
              type="email" required placeholder="admin@bank.com"
              className={inputClass}
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required placeholder="••••••••"
                className={`${inputClass} pr-10`}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            {/* Strength bar */}
            {form.password.length > 0 && (
              <div className="mt-2 space-y-1.5">
                <div className="flex gap-1">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className={`h-1 flex-1 rounded-full transition-all duration-300 ${i <= strength.score ? strength.color : "bg-muted"}`} />
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">Password strength: <span className={`font-medium ${strength.score >= 3 ? "text-green-500" : strength.score >= 2 ? "text-amber-500" : "text-red-500"}`}>{strength.label}</span></p>
                <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
                  {rules.map((r) => (
                    <div key={r.label} className={`flex items-center gap-1 text-xs ${r.test(form.password) ? "text-green-500" : "text-muted-foreground"}`}>
                      <CheckCircle className="w-3 h-3" />
                      {r.label}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                required placeholder="••••••••"
                className={`${inputClass} pr-10 ${passwordMismatch ? "border-destructive focus:ring-destructive/30" : ""}`}
                value={form.confirm}
                onChange={(e) => setForm({ ...form, confirm: e.target.value })}
              />
              <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowConfirm(!showConfirm)}>
                {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {passwordMismatch && <p className="text-xs text-destructive mt-1">Passwords do not match</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 mt-1 ${
              isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black glow-primary" : "bg-primary hover:opacity-90 text-primary-foreground"
            }`}
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-5 text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <button onClick={() => navigate("/login")} className={`font-medium transition-colors ${isCyberpunk ? "text-cyan-400 hover:text-cyan-300" : "text-primary hover:text-primary/80"}`}>
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
