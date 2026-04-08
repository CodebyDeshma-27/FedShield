"""
Generate Mule Account Fraud Patterns (Indian Banking Context)
Mule accounts: Intermediary accounts used to move/launder stolen money
Common in India for cybercrime rings and financial fraud
"""

import numpy as np
import pandas as pd
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MuleAccountAttackGenerator:
    """
    Generate realistic mule account fraud patterns
    
    Characteristics of mule account attacks in India:
    - Multiple small transactions to avoid RBI detection (>₹10 lakh threshold)
    - High frequency of rapid transfers to other accounts
    - Deposits typically from UPI/online channels
    - Withdrawals immediately via ATM/branches
    - No clear relationship between deposits and withdrawals
    - Geographically scattered transactions
    - Often involves fake/borrowed KYC
    """
    
    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def generate_mule_transactions(self, n_samples: int = 500) -> np.ndarray:
        """
        Generate mule account fraud transaction features
        
        Args:
            n_samples: Number of fraud transactions
            
        Returns:
            Array of shape (n_samples, 30) with mule account fraud features
        """
        logger.info(f"🚨 Generating {n_samples} MULE ACCOUNT attack transactions...")
        
        features = np.zeros((n_samples, 30))
        
        # ========== Mule Account Signature Features ==========
        
        # Feature 0-4: PCA components showing ABNORMAL patterns
        # Mule accounts have unusual patterns not seen in normal transactions
        for i in range(5):
            # Extreme values - much higher variance than normal
            features[:, i] = np.random.normal(loc=2.0, scale=0.8, size=n_samples)
        
        # Feature 5-14: Medium abnormality components
        for i in range(5, 15):
            # Higher than normal mean, indicating deviation
            features[:, i] = np.random.normal(loc=1.0, scale=0.4, size=n_samples)
        
        # Feature 15-27: Fine-grained fraud indicators
        for i in range(15, 28):
            # Moderate abnormality
            features[:, i] = np.random.normal(loc=0.5, scale=0.3, size=n_samples)
        
        # ========== Mule-Specific Behavioral Patterns ==========
        
        # Feature 28: Transaction Amount Pattern
        # Mule accounts use small amounts to avoid detection (typically ₹50K - ₹500K)
        amounts = np.random.uniform(50000, 500000, size=n_samples)
        features[:, 28] = np.log1p(amounts)
        features[:, 28] = (features[:, 28] - features[:, 28].mean()) / features[:, 28].std()
        
        # Feature 29: Time Pattern - Mules operate odd hours (24/7 activity, unusual hours)
        # Not concentrated in business hours like normal transactions
        hours = np.random.uniform(0, 24, size=n_samples)
        features[:, 29] = hours / 24  # Normalize
        
        # ========== Add Cross-features for Mule Behavior ==========
        
        # High velocity: Many transactions from same account (encoded in features)
        features[:, 0] += np.random.uniform(1, 2, size=n_samples)
        
        # Low merchant diversity: Repeatedly sends to same 2-3 receivers
        features[:, 1] -= np.random.uniform(0.5, 1.5, size=n_samples)
        
        # Fast money movement: Deposits received and sent out within hours
        features[:, 2] += np.random.uniform(1.5, 2.5, size=n_samples)
        
        logger.info(f"✅ Generated {n_samples} mule account transactions")
        logger.info(f"   Shape: {features.shape}")
        logger.info(f"   Mean magnitude: {np.linalg.norm(features, axis=1).mean():.4f}")
        
        return features
    
    def get_mule_characteristics(self) -> dict:
        """
        Return characteristics of mule account attacks for documentation
        
        Returns:
            Dictionary describing mule attack patterns
        """
        return {
            'attack_type': 'Mule Account Fraud',
            'description': 'Intermediary accounts used to move stolen money through banking system',
            'typical_amount_range': (50000, 500000),  # ₹50K - ₹500K
            'velocity_signature': 'Multiple small transactions, high frequency',
            'temporal_pattern': 'Round-the-clock activity, not business-hours concentrated',
            'geographical_pattern': 'Scattered locations, multiple cities',
            'detection_difficulty': 'Medium (volume-based rules can catch)',
            'model_evasion_potential': 'HIGH - Appears as normal microstructure',
            'privacy_threat': 'LOW - Doesn\'t leak individual training data, but shows pattern',
            'indian_context': 'Prime method for overseas cybercrime rings and gold loan scams'
        }
    
    def add_social_engineering_signals(self, features: np.ndarray) -> np.ndarray:
        """
        Add signals that indicate social engineering (often part of mule setup)
        
        Args:
            features: Feature array
            
        Returns:
            Features with social engineering signals
        """
        adjusted = features.copy()
        
        n_samples = adjusted.shape[0]
        
        # Some accounts show panic-selling behavior (needs speed)
        panic_portion = int(0.3 * n_samples)
        adjusted[:panic_portion, 2] += np.random.uniform(0.5, 1.0, size=panic_portion)
        
        # Some show coordinated activity (organized crime ring)
        coordinated_portion = int(0.4 * n_samples)
        coordinated_mask = np.random.choice(n_samples, size=coordinated_portion, replace=False)
        adjusted[coordinated_mask, 0] += np.random.uniform(0.5, 1.0, size=coordinated_portion)
        
        return adjusted


def generate_sample_mule_batch() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a batch of mule account transactions for testing
    
    Returns:
        Tuple of (features, labels) where labels are all 1 (fraud)
    """
    generator = MuleAccountAttackGenerator()
    features = generator.generate_mule_transactions(n_samples=300)
    features = generator.add_social_engineering_signals(features)
    labels = np.ones(features.shape[0], dtype=np.int64)
    
    return features, labels


if __name__ == "__main__":
    generator = MuleAccountAttackGenerator()
    
    print("\n" + "="*70)
    print("MULE ACCOUNT ATTACK PATTERN GENERATION")
    print("="*70)
    
    mule_features = generator.generate_mule_transactions(n_samples=1000)
    mule_features = generator.add_social_engineering_signals(mule_features)
    
    print("\n[INFO] Mule Attack Characteristics:")
    chars = generator.get_mule_characteristics()
    for key, value in chars.items():
        print(f"   {key}: {value}")
    
    print(f"\n[INFO] Generated Mule Features:")
    print(f"   Shape: {mule_features.shape}")
    print(f"   Mean magnitude: {np.linalg.norm(mule_features, axis=1).mean():.4f}")
    
    print("\n[OK] Mule account attack generator ready!")
