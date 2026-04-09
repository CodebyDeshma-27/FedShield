import { Switch, Route, Router as WouterRouter, Redirect } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/context/ThemeContext";
import { AuthProvider } from "@/context/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import TransactionAnalyzer from "@/pages/TransactionAnalyzer";
import PrivacyMonitor from "@/pages/PrivacyMonitor";
import FederatedLearning from "@/pages/FederatedLearning";
import Experiments from "@/pages/Experiments";
import ApiHealth from "@/pages/ApiHealth";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import ForgotPassword from "@/pages/ForgotPassword";
import ResetPassword from "@/pages/ResetPassword";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

function Router() {
  return (
    <Switch>
      {/* Public auth routes */}
      <Route path="/login" component={Login} />
      <Route path="/register" component={Register} />
      <Route path="/forgot-password" component={ForgotPassword} />
      <Route path="/reset-password" component={ResetPassword} />

      {/* Protected dashboard routes */}
      <Route path="/">
        {() => <ProtectedLayout><Dashboard /></ProtectedLayout>}
      </Route>
      <Route path="/analyzer">
        {() => <ProtectedLayout><TransactionAnalyzer /></ProtectedLayout>}
      </Route>
      <Route path="/privacy">
        {() => <ProtectedLayout><PrivacyMonitor /></ProtectedLayout>}
      </Route>
      <Route path="/federated">
        {() => <ProtectedLayout><FederatedLearning /></ProtectedLayout>}
      </Route>
      <Route path="/experiments">
        {() => <ProtectedLayout><Experiments /></ProtectedLayout>}
      </Route>
      <Route path="/api-health">
        {() => <ProtectedLayout><ApiHealth /></ProtectedLayout>}
      </Route>

      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <ThemeProvider>
          <AuthProvider>
            <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
              <Router />
            </WouterRouter>
          </AuthProvider>
        </ThemeProvider>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
