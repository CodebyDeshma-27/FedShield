"""
Generate Normal Transaction Patterns
Creates synthetic normal transactions with realistic Indian banking characteristics
"""

import numpy as np
import pandas as pd
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NormalTransactionGenerator:
    """Generate realistic normal transaction patterns for Indian banking"""
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize generator
        
        Args:
            random_seed: Random seed for reproducibility
        """
        np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def generate_transactions(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate normal transaction features
        
        Args:
            n_samples: Number of transactions to generate
            
        Returns:
            Array of shape (n_samples, 30) with realistic transaction features
        """
        logger.info(f"Generating {n_samples} normal transactions...")
        
        features = np.zeros((n_samples, 30))
        
        # Feature 1-28: PCA components of transaction data (realistic values)
        # These simulate normalized transaction amounts, merchant categories, etc.
        for i in range(28):
            if i < 5:  # Strong components
                features[:, i] = np.random.normal(loc=0.5, scale=0.3, size=n_samples)
            elif i < 15:  # Medium components
                features[:, i] = np.random.normal(loc=0.0, scale=0.2, size=n_samples)
            else:  # Weak components
                features[:, i] = np.random.normal(loc=0.0, scale=0.1, size=n_samples)
        
        # Feature 29: Amount (log-transformed for realistic distribution)
        amounts = np.random.exponential(scale=3000, size=n_samples)  # ₹ distribution
        amounts = np.log1p(amounts)  # Log transform
        features[:, 28] = (amounts - amounts.mean()) / amounts.std()  # Normalize
        
        # Feature 30: Time of day pattern (more transactions during business hours)
        hours = np.random.normal(loc=10, scale=3, size=n_samples)  # Peak at 10 AM IST
        hours = np.clip(hours, 6, 23)  # Between 6 AM and 11 PM
        features[:, 29] = hours / 24  # Normalize to [0, 1]
        
        logger.info(f"✅ Generated {n_samples} normal transactions")
        logger.info(f"   Shape: {features.shape}")
        logger.info(f"   Mean magnitude: {np.linalg.norm(features, axis=1).mean():.4f}")
        
        return features
    
    def add_realistic_variation(self, features: np.ndarray) -> np.ndarray:
        """
        Add realistic variation to features (seasonal patterns, customer behavior)
        
        Args:
            features: Base features
            
        Returns:
            Features with realistic variation
        """
        varied = features.copy()
        
        # Add some customer behavior patterns
        n_samples = features.shape[0]
        customer_segments = np.random.randint(0, 5, size=n_samples)
        
        for segment in range(5):
            mask = customer_segments == segment
            varied[mask] += np.random.normal(0, 0.05, size=(mask.sum(), 30))
        
        # Clip to realistic ranges
        varied = np.clip(varied, -3, 3)
        
        return varied
    
    def get_statistics(self, features: np.ndarray) -> dict:
        """
        Get statistics of generated features
        
        Args:
            features: Feature array
            
        Returns:
            Dictionary with statistics
        """
        return {
            'mean': features.mean(axis=0),
            'std': features.std(axis=0),
            'min': features.min(axis=0),
            'max': features.max(axis=0),
            'magnitude': np.linalg.norm(features, axis=1)
        }


def generate_sample_normal_batch() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a batch of normal transactions for testing
    
    Returns:
        Tuple of (features, labels) where labels are all 0 (normal)
    """
    generator = NormalTransactionGenerator()
    features = generator.generate_transactions(n_samples=500)
    features = generator.add_realistic_variation(features)
    labels = np.zeros(features.shape[0], dtype=np.int64)
    
    return features, labels


if __name__ == "__main__":
    # Generate and save sample
    generator = NormalTransactionGenerator()
    
    print("\n" + "="*70)
    print("NORMAL TRANSACTION GENERATION")
    print("="*70)
    
    normal_features = generator.generate_transactions(n_samples=1000)
    normal_features = generator.add_realistic_variation(normal_features)
    
    stats = generator.get_statistics(normal_features)
    
    print("\n[INFO] Feature Statistics:")
    print(f"   Feature magnitude: {stats['magnitude'].mean():.4f} ± {stats['magnitude'].std():.4f}")
    print(f"   Feature range: [{stats['min'].min():.4f}, {stats['max'].max():.4f}]")
    
    print("\n[OK] Normal transaction generator ready!")
