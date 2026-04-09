import { useState } from "react";
import { useLocation } from "wouter";
import { Shield, Eye, EyeOff, CheckCircle, Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

export default function ResetPassword() {
  const [, navigate] = useLocation();
  const { resetPassword } = useAuth();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const mismatch = confirm.length > 0 && password !== confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) { setError("Passwords do not match"); return; }
    if (password.length < 8) { setError("Password must be at least 8 characters"); return; }
    setError("");
    setLoading(true);
    try {
      await resetPassword("mock_reset_token", password);
      setDone(true);
    } catch {
      setError("Password reset failed. The link may have expired.");
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

      <div className={`w-full max-w-sm rounded-2xl backdrop-blur-md p-8 ${cardClass} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
        <div className="flex flex-col items-center mb-7">
          <div className={`p-3 rounded-2xl mb-4 ${isCyberpunk ? "bg-fuchsia-500/20 border border-fuchsia-500/40" : "bg-primary/10"}`}>
            <Shield className={`w-7 h-7 ${isCyberpunk ? "text-fuchsia-400" : "text-primary"}`} />
          </div>
          <h1 className={`text-xl font-bold ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>New Password</h1>
          <p className="text-xs text-muted-foreground mt-1 text-center">Enter your new secure password below</p>
        </div>

        {done ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="p-3 rounded-full bg-green-500/10">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-foreground">Password updated!</p>
              <p className="text-sm text-muted-foreground mt-1">You can now sign in with your new password.</p>
            </div>
            <button
              onClick={() => navigate("/login")}
              className={`mt-2 w-full py-2.5 rounded-lg text-sm font-semibold transition-all ${
                isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black" : "bg-primary hover:opacity-90 text-primary-foreground"
              }`}
            >
              Go to Login
            </button>
          </div>
        ) : (
          <>
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm mb-4">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">New Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    required placeholder="••••••••"
                    className={`${inputClass} pr-10`}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Confirm Password</label>
                <div className="relative">
                  <input
                    type={showConfirm ? "text" : "password"}
                    required placeholder="••••••••"
                    className={`${inputClass} pr-10 ${mismatch ? "border-destructive" : ""}`}
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                  />
                  <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowConfirm(!showConfirm)}>
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {mismatch && <p className="text-xs text-destructive mt-1">Passwords do not match</p>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 ${
                  isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black glow-primary" : "bg-primary hover:opacity-90 text-primary-foreground"
                }`}
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {loading ? "Updating..." : "Update Password"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
