import { useState, useEffect } from 'react';
import { fetchMetrics, fetchComparisonMetrics, fetchSummaryMetrics, checkApiHealth, MetricsResponse, ComparisonMetrics, SummaryMetrics } from '@/lib/apiClient';

interface UseMetricsReturn {
  metrics: MetricsResponse | null;
  comparison: ComparisonMetrics | null;
  summary: SummaryMetrics | null;
  apiHealth: {
    status: string;
    timestamp?: string;
    model?: string;
    device?: string;
    accuracy?: number;
    privacy?: {
      protected?: boolean;
      epsilon?: number;
      delta?: number;
    };
  } | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Custom hook to fetch and manage real metrics from backend
 */
export function useMetrics(): UseMetricsReturn {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [comparison, setComparison] = useState<ComparisonMetrics | null>(null);
  const [apiHealth, setApiHealth] = useState<{
    status: string;
    timestamp?: string;
    model?: string;
    device?: string;
    accuracy?: number;
    privacy?: {
      protected?: boolean;
      epsilon?: number;
      delta?: number;
    };
  } | null>(null);
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check API health
      const health = await checkApiHealth();
      setApiHealth(health);

      // Fetch real metrics
      const metricsData = await fetchMetrics();
      setMetrics(metricsData);

      // Fetch comparison metrics
      const comparisonData = await fetchComparisonMetrics();
      setComparison(comparisonData);

      // Fetch pipeline summary metrics
      const summaryData = await fetchSummaryMetrics();
      setSummary(summaryData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch metrics';
      setError(errorMessage);
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    metrics,
    comparison,
    summary,
    apiHealth,
    loading,
    error,
    refetch: fetchData,
  };
}

export default useMetrics;
