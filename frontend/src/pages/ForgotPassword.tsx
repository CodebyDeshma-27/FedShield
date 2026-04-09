import { useState } from "react";
import { useLocation } from "wouter";
import { Shield, Mail, ArrowLeft, Loader2, CheckCircle } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

export default function ForgotPassword() {
  const [, navigate] = useLocation();
  const { forgotPassword } = useAuth();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await forgotPassword(email);
      setSent(true);
    } catch {
      setError("Something went wrong. Please try again.");
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
        <button
          onClick={() => navigate("/login")}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mb-6"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to login
        </button>

        <div className="flex flex-col items-center mb-7">
          <div className={`p-3 rounded-2xl mb-4 ${isCyberpunk ? "bg-fuchsia-500/20 border border-fuchsia-500/40" : "bg-primary/10"}`}>
            <Shield className={`w-7 h-7 ${isCyberpunk ? "text-fuchsia-400" : "text-primary"}`} />
          </div>
          <h1 className={`text-xl font-bold ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>Reset Password</h1>
          <p className="text-xs text-muted-foreground mt-1 text-center">We'll send a reset link to your email</p>
        </div>

        {sent ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="p-3 rounded-full bg-green-500/10">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-foreground">Reset link sent!</p>
              <p className="text-sm text-muted-foreground mt-1">Check <strong>{email}</strong> for a password reset link.</p>
            </div>
            <button
              onClick={() => navigate("/login")}
              className={`mt-2 w-full py-2.5 rounded-lg text-sm font-semibold transition-all ${
                isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black" : "bg-primary hover:opacity-90 text-primary-foreground"
              }`}
            >
              Return to Login
            </button>
          </div>
        ) : (
          <>
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm mb-4">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="email" required
                    placeholder="admin@bank.com"
                    className={`${inputClass} pl-9`}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 ${
                  isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black glow-primary" : "bg-primary hover:opacity-90 text-primary-foreground"
                }`}
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {loading ? "Sending..." : "Send Reset Link"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
