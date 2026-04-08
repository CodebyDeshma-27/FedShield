"""
Generate UPI Burst Attack Patterns (Indian Banking Context)
UPI Burst: Rapid-fire fraudulent UPI transactions targeting merchant or individual accounts
Common in India post-UPI proliferation (sim swap attacks, compromised APIs)
"""

import numpy as np
import pandas as pd
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BurstAttackGenerator:
    """
    Generate UPI burst/rapid transaction fraud patterns
    
    Characteristics of UPI burst attacks in India:
    - Extremely high frequency transactions (10-100 per minute)
    - Consistent small amounts (₹100-₹500 per transaction)
    - All directed to same merchant/account (or few accounts)
    - Happens within very short time window (minutes to hours)
    - Decimal amounts to bypass common fraud filters (₹199, ₹298)
    - Usually at odd hours to avoid customer noticing
    - After account compromise or OTP theft
    - Targets UPI payment apps and merchant QR codes
    """
    
    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def generate_burst_transactions(self, n_samples: int = 500) -> np.ndarray:
        """
        Generate UPI burst attack transaction features
        
        Args:
            n_samples: Number of burst fraud transactions
            
        Returns:
            Array of shape (n_samples, 30) with burst attack features
        """
        logger.info(f"💥 Generating {n_samples} UPI BURST ATTACK transactions...")
        
        features = np.zeros((n_samples, 30))
        
        # ========== Burst Attack Signature Features ==========
        
        # Feature 0-3: EXTREME abnormality - rapid firing behavior
        # These features capture the velocity pattern
        for i in range(4):
            # Very high values - this is THE signature of burst attacks
            features[:, i] = np.random.normal(loc=3.0, scale=0.5, size=n_samples)
        
        # Feature 4-9: Sequential transaction markers
        # Burst = transactions 1,2,3,4,5... at predictable intervals
        for i in range(4, 10):
            features[:, i] = np.random.normal(loc=2.5, scale=0.6, size=n_samples)
        
        # Feature 10-19: Temporal concentration patterns
        # All transactions within short window → high correlation
        for i in range(10, 20):
            features[:, i] = np.random.normal(loc=2.0, scale=0.4, size=n_samples)
        
        # Feature 20-27: Same recipient pattern (low recipient diversity)
        for i in range(20, 28):
            features[:, i] = np.random.normal(loc=-1.5, scale=0.5, size=n_samples)
        
        # ========== Burst-Specific Behavioral Features ==========
        
        # Feature 28: Transaction Amount - Consistent small amounts
        # Burst uses ₹100-₹500, often with decimals to evade filters
        amounts = np.random.uniform(100, 500, size=n_samples)
        # Add decimal amounts (₹199, ₹298, etc.)
        amounts = amounts + np.random.uniform(-0.99, 0.99, size=n_samples)
        features[:, 28] = np.log1p(amounts)
        features[:, 28] = (features[:, 28] - features[:, 28].mean()) / (features[:, 28].std() + 1e-6)
        
        # Feature 29: Time pattern - UPI bursts happen at NIGHT/EARLY MORNING
        # When customer is less likely to notice (2 AM - 5 AM IST)
        odd_hours = np.random.uniform(2, 5, size=n_samples)
        features[:, 29] = odd_hours / 24
        
        # ========== Add Burst-Specific Cross-Features ==========
        
        # Very high transaction velocity (20+ per minute window)
        features[:, 0] += np.random.uniform(2, 3, size=n_samples)
        
        # Zero merchant diversity (same receiver)
        features[:, 5] -= np.random.uniform(2, 3, size=n_samples)
        
        # Temporal clustering (all within 30 minutes)
        features[:, 10] += np.random.uniform(2.5, 3.5, size=n_samples)
        
        # Identical amounts (or ₹1 increments) - pattern recognition signature
        features[:, 15] -= np.random.uniform(1.5, 2.0, size=n_samples)
        
        logger.info(f"✅ Generated {n_samples} UPI burst attack transactions")
        logger.info(f"   Shape: {features.shape}")
        logger.info(f"   Mean magnitude: {np.linalg.norm(features, axis=1).mean():.4f}")
        
        return features
    
    def get_burst_characteristics(self) -> dict:
        """
        Return characteristics of UPI burst attacks for documentation
        
        Returns:
            Dictionary describing burst attack patterns
        """
        return {
            'attack_type': 'UPI Burst Attack',
            'description': 'Rapid-fire UPI transactions to drain account or load money',
            'transaction_rate': '10-100 per minute',
            'typical_amount_range': (100, 500),  # ₹100-₹500
            'temporal_window': '5-60 minutes',
            'recipient_concentration': 'Same merchant/account (1-3 unique)',
            'preferred_timing': 'Night hours (2-5 AM IST) when unmonitored',
            'velocity_signature': 'EXTREME - strongest fraud signal',
            'detection_difficulty': 'Low (velocity rules work)',
            'model_evasion_potential': 'HIGHEST - completely different microstructure',
            'privacy_threat': 'HIGHEST - Strongest deviation from training data',
            'indian_context': 'Post-UPI explosion (2016+), targets compromised accounts, payment app vulnerabilities'
        }
    
    def apply_clustering_pattern(self, features: np.ndarray) -> np.ndarray:
        """
        Apply temporal clustering pattern (all transactions within 30-60 min window)
        
        Args:
            features: Feature array
            
        Returns:
            Features with clustering pattern applied
        """
        adjusted = features.copy()
        
        n_samples = adjusted.shape[0]
        
        # Simulate multiple burst clusters (e.g., 5 bursts of 100 txns each)
        n_clusters = max(1, n_samples // 100)
        cluster_size = n_samples // n_clusters
        
        for cluster_idx in range(n_clusters):
            start_idx = cluster_idx * cluster_size
            end_idx = min(start_idx + cluster_size, n_samples)
            cluster_mask = np.arange(start_idx, end_idx)
            
            # Amplify burst signature for this cluster
            adjusted[cluster_mask, 0] += np.random.uniform(1, 2, size=len(cluster_mask))
            adjusted[cluster_mask, 10] += np.random.uniform(1.5, 2.5, size=len(cluster_mask))
        
        return adjusted


def generate_sample_burst_batch() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a batch of UPI burst attack transactions for testing
    
    Returns:
        Tuple of (features, labels) where labels are all 1 (fraud)
    """
    generator = BurstAttackGenerator()
    features = generator.generate_burst_transactions(n_samples=300)
    features = generator.apply_clustering_pattern(features)
    labels = np.ones(features.shape[0], dtype=np.int64)
    
    return features, labels


if __name__ == "__main__":
    generator = BurstAttackGenerator()
    
    print("\n" + "="*70)
    print("UPI BURST ATTACK PATTERN GENERATION")
    print("="*70)
    
    burst_features = generator.generate_burst_transactions(n_samples=1000)
    burst_features = generator.apply_clustering_pattern(burst_features)
    
    print("\n[INFO] UPI Burst Attack Characteristics:")
    chars = generator.get_burst_characteristics()
    for key, value in chars.items():
        print(f"   {key}: {value}")
    
    print(f"\n[INFO] Generated Burst Features:")
    print(f"   Shape: {burst_features.shape}")
    print(f"   Mean magnitude: {np.linalg.norm(burst_features, axis=1).mean():.4f}")
    
    print("\n[OK] UPI burst attack generator ready!")
