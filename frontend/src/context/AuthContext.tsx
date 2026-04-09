import { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  apiLogin, apiRegister, apiForgotPassword, apiResetPassword, apiUpdateProfile, apiChangePassword,
} from "@/lib/api";

export interface AuthUser {
  name: string;
  email: string;
  bank: string;
  role?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (bankName: string, adminName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  updateProfile: (updates: { name?: string; bank?: string }) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  forgotPassword: async () => {},
  resetPassword: async () => {},
  updateProfile: async () => {},
  changePassword: async () => {},
});

const TOKEN_KEY = "fedshield_token";
const USER_KEY  = "fedshield_user";

// ─── Mock flag ───────────────────────────────────────────────────────────────
// Set to false once your real backend is running.
const USE_MOCK = true;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser]     = useState<AuthUser | null>(null);
  const [token, setToken]   = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const persistSession = (tok: string, u: AuthUser, remember: boolean) => {
    const store = remember ? localStorage : sessionStorage;
    store.setItem(TOKEN_KEY, tok);
    store.setItem(USER_KEY, JSON.stringify(u));
  };

  const clearSession = () => {
    [localStorage, sessionStorage].forEach((s) => {
      s.removeItem(TOKEN_KEY);
      s.removeItem(USER_KEY);
    });
  };

  // Auto-restore session on mount
  useEffect(() => {
    const tok  = localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY);
    const raw  = localStorage.getItem(USER_KEY)  ?? sessionStorage.getItem(USER_KEY);
    if (tok && raw) {
      try { setToken(tok); setUser(JSON.parse(raw)); } catch { clearSession(); }
    }
    setIsLoading(false);
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email: string, password: string, remember: boolean) => {
    let tok: string;
    let u: AuthUser;

    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 900));
      if (password.length < 3) throw new Error("Invalid email or password");
      tok = "mock_jwt_" + Date.now();
      u = {
        name:  email.split("@")[0].replace(/\./g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        email,
        bank:  "First National Bank",
        role:  "Admin",
      };
    } else {
      const res = await apiLogin({ email, password });
      tok = res.token;
      u   = res.user;
    }

    setToken(tok);
    setUser(u);
    persistSession(tok, u, remember);
  }, []);

  // ── Register ──────────────────────────────────────────────────────────────
  const register = useCallback(async (bankName: string, adminName: string, email: string, password: string) => {
    let tok: string;
    let u: AuthUser;

    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 1000));
      tok = "mock_jwt_" + Date.now();
      u   = { name: adminName, email, bank: bankName, role: "Admin" };
    } else {
      const res = await apiRegister({ bankName, adminName, email, password });
      tok = res.token;
      u   = res.user;
    }

    setToken(tok);
    setUser(u);
    persistSession(tok, u, true);
  }, []);

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    clearSession();
  }, []);

  // ── Forgot Password ───────────────────────────────────────────────────────
  const forgotPassword = useCallback(async (email: string) => {
    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 800));
    } else {
      await apiForgotPassword({ email });
    }
  }, []);

  // ── Reset Password ────────────────────────────────────────────────────────
  const resetPassword = useCallback(async (resetToken: string, newPassword: string) => {
    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 800));
    } else {
      await apiResetPassword({ token: resetToken, newPassword });
    }
  }, []);

  // ── Update Profile ────────────────────────────────────────────────────────
  const updateProfile = useCallback(async (updates: { name?: string; bank?: string }) => {
    let updated: AuthUser;

    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 700));
      updated = { ...user!, ...updates };
    } else {
      const res = await apiUpdateProfile(updates, token!);
      updated = res.user;
    }

    setUser(updated);
    // Update whichever storage currently holds the session
    const inLocal = !!localStorage.getItem(TOKEN_KEY);
    (inLocal ? localStorage : sessionStorage).setItem(USER_KEY, JSON.stringify(updated));
  }, [user, token]);

  // ── Change Password ───────────────────────────────────────────────────────
  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    if (USE_MOCK) {
      // TODO: Remove mock block below when real backend is ready
      await new Promise((r) => setTimeout(r, 800));
      if (currentPassword.length < 3) throw new Error("Current password is incorrect");
    } else {
      await apiChangePassword({ currentPassword, newPassword }, token!);
    }
  }, [token]);

  return (
    <AuthContext.Provider value={{
      user, token, isAuthenticated: !!user, isLoading,
      login, register, logout, forgotPassword, resetPassword,
      updateProfile, changePassword,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
