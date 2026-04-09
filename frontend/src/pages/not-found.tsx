import { Shield } from "lucide-react";
import { useLocation } from "wouter";

export default function NotFound() {
  const [, navigate] = useLocation();
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <Shield className="w-12 h-12 text-muted-foreground mx-auto" />
        <h1 className="text-2xl font-bold text-foreground">404 — Page Not Found</h1>
        <p className="text-muted-foreground text-sm">This page does not exist in FedShield.</p>
        <button
          onClick={() => navigate("/")}
          className="inline-block mt-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-90 transition-all"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}
