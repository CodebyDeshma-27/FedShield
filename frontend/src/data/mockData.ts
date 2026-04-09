export const fraudOverTime = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  fraud: Math.floor(Math.random() * 25) + 5,
  transactions: Math.floor(Math.random() * 500) + 200,
}));

export const recentAlerts = [
  { id: "TX-8821", bank: "Bank 1", amount: "$12,450", risk: "HIGH", timestamp: "2026-04-08 14:32:01" },
  { id: "TX-9034", bank: "Bank 3", amount: "$890", risk: "MEDIUM", timestamp: "2026-04-08 14:28:47" },
  { id: "TX-7712", bank: "Bank 2", amount: "$3,200", risk: "HIGH", timestamp: "2026-04-08 14:21:13" },
  { id: "TX-5530", bank: "Bank 5", amount: "$150", risk: "LOW", timestamp: "2026-04-08 14:19:55" },
  { id: "TX-6641", bank: "Bank 4", amount: "$7,800", risk: "HIGH", timestamp: "2026-04-08 14:11:22" },
  { id: "TX-3309", bank: "Bank 1", amount: "$320", risk: "MEDIUM", timestamp: "2026-04-08 14:08:09" },
  { id: "TX-2287", bank: "Bank 2", amount: "$56", risk: "LOW", timestamp: "2026-04-08 13:59:44" },
];

export const bankNodes = [
  { id: "bank1", name: "Bank 1", x: 100, y: 80, status: "active", accuracy: 0.94 },
  { id: "bank2", name: "Bank 2", x: 340, y: 60, status: "active", accuracy: 0.91 },
  { id: "bank3", name: "Bank 3", x: 400, y: 200, status: "active", accuracy: 0.93 },
  { id: "bank4", name: "Bank 4", x: 100, y: 240, status: "inactive", accuracy: 0.88 },
  { id: "bank5", name: "Bank 5", x: 230, y: 290, status: "active", accuracy: 0.96 },
];

export const privacyPerRound = Array.from({ length: 20 }, (_, i) => ({
  round: i + 1,
  epsilon: parseFloat((0.08 + Math.random() * 0.15).toFixed(3)),
}));

export const bankContributions = [
  { bank: "Bank 1", samples: 42000 },
  { bank: "Bank 2", samples: 38500 },
  { bank: "Bank 3", samples: 51200 },
  { bank: "Bank 4", samples: 29800 },
  { bank: "Bank 5", samples: 44700 },
];

export const convergenceData = Array.from({ length: 20 }, (_, i) => ({
  round: i + 1,
  accuracy: parseFloat(Math.min(0.65 + i * 0.018 + Math.random() * 0.008, 0.97).toFixed(3)),
}));

export const bankStatusTable = [
  { name: "Bank 1", status: "Active", localAccuracy: "94.2%", lastUpdate: "2 min ago" },
  { name: "Bank 2", status: "Active", localAccuracy: "91.7%", lastUpdate: "3 min ago" },
  { name: "Bank 3", status: "Active", localAccuracy: "93.4%", lastUpdate: "1 min ago" },
  { name: "Bank 4", status: "Inactive", localAccuracy: "88.1%", lastUpdate: "12 min ago" },
  { name: "Bank 5", status: "Active", localAccuracy: "96.0%", lastUpdate: "30 sec ago" },
];

export const experimentAccuracy = [
  { metric: "Accuracy", centralized: 0.97, federated: 0.94, federatedDP: 0.91 },
  { metric: "Precision", centralized: 0.96, federated: 0.92, federatedDP: 0.89 },
  { metric: "Recall", centralized: 0.95, federated: 0.91, federatedDP: 0.87 },
  { metric: "F1", centralized: 0.955, federated: 0.915, federatedDP: 0.88 },
];

export const privacyUtilityTradeoff = [
  { epsilon: 0.1, accuracy: 0.78 },
  { epsilon: 0.5, accuracy: 0.84 },
  { epsilon: 1.0, accuracy: 0.88 },
  { epsilon: 2.0, accuracy: 0.91 },
  { epsilon: 5.0, accuracy: 0.93 },
  { epsilon: 10.0, accuracy: 0.945 },
  { epsilon: 20.0, accuracy: 0.955 },
];

export const attackResistance = [
  { attack: "Model Inversion", score: 92 },
  { attack: "Gradient Leakage", score: 88 },
  { attack: "Membership Inference", score: 95 },
  { attack: "Data Poisoning", score: 85 },
  { attack: "Evasion", score: 79 },
];

export const commEfficiency = Array.from({ length: 20 }, (_, i) => ({
  round: i + 1,
  accuracy: parseFloat(Math.min(0.60 + i * 0.019 + Math.random() * 0.01, 0.97).toFixed(3)),
}));

export const apiLogs = [
  { time: "14:32:01", method: "POST", endpoint: "/predict", status: 200, latency: "42ms" },
  { time: "14:31:55", method: "GET", endpoint: "/health", status: 200, latency: "8ms" },
  { time: "14:31:48", method: "POST", endpoint: "/explain", status: 200, latency: "68ms" },
  { time: "14:31:39", method: "POST", endpoint: "/predict", status: 200, latency: "39ms" },
  { time: "14:31:30", method: "POST", endpoint: "/predict", status: 422, latency: "12ms" },
  { time: "14:31:22", method: "GET", endpoint: "/health", status: 200, latency: "9ms" },
  { time: "14:31:14", method: "POST", endpoint: "/explain", status: 200, latency: "71ms" },
  { time: "14:31:05", method: "POST", endpoint: "/predict", status: 200, latency: "44ms" },
  { time: "14:30:58", method: "GET", endpoint: "/health", status: 200, latency: "7ms" },
  { time: "14:30:49", method: "POST", endpoint: "/predict", status: 200, latency: "41ms" },
];
