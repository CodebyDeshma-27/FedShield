import { useState } from "react";
import { useLocation } from "wouter";
import {
  User, Building2, Mail, Shield, KeyRound, LogOut, CheckCircle,
  AlertCircle, Loader2, Eye, EyeOff, Edit2, Save, X
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

function InfoRow({ label, value, icon: Icon }: { label: string; value: string; icon: React.ElementType }) {
  return (
    <div className="flex items-center gap-3 py-3 border-b border-border last:border-0">
      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
        <Icon className="w-4 h-4 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium text-foreground truncate">{value}</p>
      </div>
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";
  return (
    <div className={`rounded-2xl border p-6 ${isCyberpunk ? "bg-zinc-900/80 border-fuchsia-500/30" : "bg-card border-card-border"}`}>
      <h3 className={`text-sm font-semibold mb-4 ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>{title}</h3>
      {children}
    </div>
  );
}

export default function Profile() {
  const [, navigate] = useLocation();
  const { user, token, logout, updateProfile, changePassword } = useAuth();
  const { theme } = useTheme();
  const isCyberpunk = theme === "cyberpunk";

  // ── Edit profile state ────────────────────────────────────────────────────
  const [editing, setEditing]   = useState(false);
  const [editName, setEditName] = useState(user?.name ?? "");
  const [editBank, setEditBank] = useState(user?.bank ?? "");
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMsg, setSaveMsg]         = useState<{ type: "ok" | "err"; text: string } | null>(null);

  // ── Change password state ─────────────────────────────────────────────────
  const [currentPw, setCurrentPw]   = useState("");
  const [newPw, setNewPw]           = useState("");
  const [confirmPw, setConfirmPw]   = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew]         = useState(false);
  const [pwLoading, setPwLoading]   = useState(false);
  const [pwMsg, setPwMsg]           = useState<{ type: "ok" | "err"; text: string } | null>(null);

  const initials = user?.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase() ?? "??";

  const loginTime = (() => {
    try {
      const raw = localStorage.getItem("fedshield_token") ?? sessionStorage.getItem("fedshield_token");
      if (!raw) return "—";
      const ts = parseInt(raw.split("_").pop() ?? "0", 10);
      if (!ts) return "Active session";
      return new Date(ts).toLocaleString();
    } catch { return "Active session"; }
  })();

  // Token preview (first 24 chars + ellipsis)
  const tokenPreview = token ? token.slice(0, 24) + "…" : "—";

  const inputClass = `w-full px-3 py-2 rounded-lg border text-sm bg-transparent outline-none focus:ring-2 transition-all ${
    isCyberpunk
      ? "border-fuchsia-500/40 focus:ring-fuchsia-500/30 focus:border-fuchsia-500 text-foreground placeholder-muted-foreground"
      : "border-border focus:ring-primary/30 focus:border-primary text-foreground placeholder-muted-foreground"
  }`;

  const btnPrimary = `flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 ${
    isCyberpunk ? "bg-fuchsia-500 hover:bg-fuchsia-400 text-black" : "bg-primary hover:opacity-90 text-primary-foreground"
  }`;

  const handleSaveProfile = async () => {
    setSaveLoading(true);
    setSaveMsg(null);
    try {
      await updateProfile({ name: editName.trim(), bank: editBank.trim() });
      setSaveMsg({ type: "ok", text: "Profile updated successfully" });
      setEditing(false);
    } catch (e: unknown) {
      setSaveMsg({ type: "err", text: e instanceof Error ? e.message : "Update failed" });
    } finally {
      setSaveLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPw !== confirmPw) { setPwMsg({ type: "err", text: "New passwords do not match" }); return; }
    if (newPw.length < 8)    { setPwMsg({ type: "err", text: "New password must be at least 8 characters" }); return; }
    setPwLoading(true);
    setPwMsg(null);
    try {
      await changePassword(currentPw, newPw);
      setPwMsg({ type: "ok", text: "Password changed successfully" });
      setCurrentPw(""); setNewPw(""); setConfirmPw("");
    } catch (e: unknown) {
      setPwMsg({ type: "err", text: e instanceof Error ? e.message : "Password change failed" });
    } finally {
      setPwLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* ── Header Card ──────────────────────────────────────────────────── */}
      <div className={`rounded-2xl border p-6 ${isCyberpunk ? "bg-zinc-900/80 border-fuchsia-500/30" : "bg-card border-card-border"}`}>
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-5">
          {/* Avatar */}
          <div className={`w-20 h-20 rounded-2xl flex items-center justify-center text-2xl font-bold shrink-0 ${
            isCyberpunk ? "bg-fuchsia-500/20 border-2 border-fuchsia-500/50 text-fuchsia-400" : "bg-primary/15 text-primary border-2 border-primary/30"
          }`}>
            {initials}
          </div>

          {/* Info */}
          <div className="flex-1 text-center sm:text-left">
            <h2 className={`text-xl font-bold ${isCyberpunk ? "text-fuchsia-400 font-mono" : "text-foreground"}`}>{user?.name}</h2>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
            <div className="flex items-center justify-center sm:justify-start gap-2 mt-2">
              <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium ${
                isCyberpunk ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30" : "bg-green-500/10 text-green-600 border border-green-500/20"
              }`}>
                <Shield className="w-3 h-3" />
                {user?.role ?? "Admin"}
              </span>
              <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium ${
                isCyberpunk ? "bg-fuchsia-500/15 text-fuchsia-400 border border-fuchsia-500/30" : "bg-primary/10 text-primary border border-primary/20"
              }`}>
                <Building2 className="w-3 h-3" />
                {user?.bank}
              </span>
            </div>
          </div>

          {/* Sign Out button */}
          <button
            onClick={() => { logout(); navigate("/login"); }}
            className="flex items-center gap-1.5 text-xs text-destructive border border-destructive/30 hover:bg-destructive/10 px-3 py-1.5 rounded-lg transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        {/* ── Account Details ───────────────────────────────────────────── */}
        <SectionCard title="Account Details">
          {!editing ? (
            <>
              <InfoRow label="Full Name"   value={user?.name  ?? "—"} icon={User} />
              <InfoRow label="Email"       value={user?.email ?? "—"} icon={Mail} />
              <InfoRow label="Bank"        value={user?.bank  ?? "—"} icon={Building2} />
              <InfoRow label="Role"        value={user?.role  ?? "Admin"} icon={Shield} />
              {saveMsg?.type === "ok" && (
                <div className="flex items-center gap-2 mt-3 text-xs text-green-500">
                  <CheckCircle className="w-3.5 h-3.5" /> {saveMsg.text}
                </div>
              )}
              <button onClick={() => { setEditing(true); setSaveMsg(null); }} className={`mt-4 flex items-center gap-2 w-full justify-center py-2 rounded-lg text-sm font-medium border transition-all ${
                isCyberpunk ? "border-fuchsia-500/40 text-fuchsia-400 hover:bg-fuchsia-500/10" : "border-primary/40 text-primary hover:bg-primary/5"
              }`}>
                <Edit2 className="w-3.5 h-3.5" /> Edit Profile
              </button>
            </>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Full Name</label>
                <input value={editName} onChange={(e) => setEditName(e.target.value)} className={inputClass} placeholder="Your name" />
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">Bank Name</label>
                <input value={editBank} onChange={(e) => setEditBank(e.target.value)} className={inputClass} placeholder="Your bank" />
              </div>
              {saveMsg?.type === "err" && (
                <div className="flex items-center gap-2 text-xs text-destructive">
                  <AlertCircle className="w-3.5 h-3.5" /> {saveMsg.text}
                </div>
              )}
              <div className="flex gap-2 pt-1">
                <button onClick={handleSaveProfile} disabled={saveLoading} className={`${btnPrimary} flex-1`}>
                  {saveLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                  {saveLoading ? "Saving…" : "Save"}
                </button>
                <button onClick={() => { setEditing(false); setEditName(user?.name ?? ""); setEditBank(user?.bank ?? ""); setSaveMsg(null); }}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm border border-border hover:bg-muted/30 text-muted-foreground transition-all">
                  <X className="w-3.5 h-3.5" /> Cancel
                </button>
              </div>
            </div>
          )}
        </SectionCard>

        {/* ── Session Info ──────────────────────────────────────────────── */}
        <SectionCard title="Session Info">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Session Token</p>
              <code className={`block text-xs px-3 py-2 rounded-lg break-all font-mono ${
                isCyberpunk ? "bg-zinc-800 text-cyan-400" : "bg-muted text-foreground"
              }`}>{tokenPreview}</code>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Signed In</p>
              <p className="text-sm text-foreground">{loginTime}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Status</p>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-500">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                Active
              </span>
            </div>
          </div>
        </SectionCard>
      </div>

      {/* ── Change Password ────────────────────────────────────────────────── */}
      <SectionCard title="Change Password">
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Current Password</label>
              <div className="relative">
                <input
                  type={showCurrent ? "text" : "password"}
                  placeholder="••••••••"
                  required
                  className={`${inputClass} pr-9`}
                  value={currentPw}
                  onChange={(e) => setCurrentPw(e.target.value)}
                />
                <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowCurrent(!showCurrent)}>
                  {showCurrent ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">New Password</label>
              <div className="relative">
                <input
                  type={showNew ? "text" : "password"}
                  placeholder="••••••••"
                  required
                  className={`${inputClass} pr-9`}
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                />
                <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowNew(!showNew)}>
                  {showNew ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1.5">Confirm New</label>
              <input
                type="password"
                placeholder="••••••••"
                required
                className={`${inputClass} ${confirmPw && confirmPw !== newPw ? "border-destructive" : ""}`}
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
              />
            </div>
          </div>

          {pwMsg && (
            <div className={`flex items-center gap-2 text-xs ${pwMsg.type === "ok" ? "text-green-500" : "text-destructive"}`}>
              {pwMsg.type === "ok" ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {pwMsg.text}
            </div>
          )}

          <button type="submit" disabled={pwLoading} className={`${btnPrimary} w-full sm:w-auto`}>
            {pwLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
            {pwLoading ? "Changing…" : "Change Password"}
          </button>
        </form>
      </SectionCard>
    </div>
  );
}
