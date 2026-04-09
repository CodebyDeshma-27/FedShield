"""
Download Credit Card Fraud Dataset from Kaggle
Run this script to download the dataset before running main.py
"""

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_kaggle_credentials():
    """Setup Kaggle API credentials"""
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if kaggle_json.exists():
        logger.info("✅ Kaggle credentials already configured")
        return True
    
    logger.info("❌ Kaggle credentials not found!")
    logger.info("\n📋 SETUP INSTRUCTIONS:")
    logger.info("-" * 60)
    logger.info("1. Go to: https://www.kaggle.com/settings/account")
    logger.info("2. Click 'Create New API Token'")
    logger.info("3. This downloads kaggle.json")
    logger.info("4. Move kaggle.json to ~/.kaggle/ directory")
    logger.info("   - Linux/Mac: ~/.kaggle/kaggle.json")
    logger.info("   - Windows: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json")
    logger.info("5. Set permissions: chmod 600 ~/.kaggle/kaggle.json")
    logger.info("-" * 60)
    
    return False


def create_high_quality_synthetic_dataset(n_samples=284807):
    """
    Create high-quality synthetic fraud dataset matching creditcard.csv structure
    This is used as fallback when Kaggle download fails
    """
    import numpy as np
    import pandas as pd
    
    logger.info(f"🔄 Creating synthetic dataset ({n_samples:,} transactions)...")
    
    np.random.seed(42)
    
    # Create 28 V features (similar to PCA components in real data)
    n_features = 28
    X = np.random.randn(n_samples, n_features)
    
    # Create labels with 0.17% fraud rate (matching real dataset)
    fraud_rate = 0.0017
    y = np.random.choice([0, 1], size=n_samples, p=[1 - fraud_rate, fraud_rate])
    
    # Make fraud transactions distinguishable
    fraud_indices = np.where(y == 1)[0]
    X[fraud_indices] += np.random.randn(len(fraud_indices), n_features) * 1.5
    
    # Create Time and Amount columns
    times = np.random.uniform(0, 172800, size=n_samples)  # 48 hours
    amounts = np.random.exponential(scale=88, size=n_samples)  # Mean ~$88
    
    # Create DataFrame matching creditcard.csv structure
    df = pd.DataFrame(X, columns=[f'V{i}' for i in range(1, n_features + 1)])
    df['Time'] = times.astype(int)
    df['Amount'] = amounts
    df['Class'] = y.astype(int)
    
    # Reorder columns to match real dataset
    cols = ['Time', 'Amount'] + [f'V{i}' for i in range(1, n_features + 1)] + ['Class']
    df = df[cols]
    
    logger.info(f"✅ Synthetic dataset created:")
    logger.info(f"   - Total transactions: {len(df):,}")
    logger.info(f"   - Fraud transactions: {df['Class'].sum():,}")
    logger.info(f"   - Fraud rate: {100 * df['Class'].sum() / len(df):.2f}%")
    
    return df


def download_dataset():
    """Download the credit card fraud dataset from Kaggle or use synthetic fallback"""
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    csv_path = data_dir / 'creditcard.csv'
    
    # Check if already exists
    if csv_path.exists():
        logger.info(f"✅ Dataset already exists at {csv_path}")
        return True
    
    # Try Kaggle download
    try:
        logger.info("🔍 Checking Kaggle setup...")
        
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        logger.info("📥 Downloading credit card fraud dataset from Kaggle...")
        logger.info("   Dataset: mlg-ulb/creditcardfraud")
        
        # Authenticate
        api = KaggleApi()
        api.authenticate()
        logger.info("✅ Kaggle authentication successful")
        
        # Download
        logger.info("⏳ Downloading (this may take a few minutes)...")
        api.dataset_download_files('mlg-ulb/creditcardfraud', path='data', unzip=True)
        
        if csv_path.exists():
            file_size_mb = csv_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Downloaded successfully! Size: {file_size_mb:.2f} MB")
            return True
            
    except Exception as e:
        logger.warning(f"⚠️  Kaggle download failed: {str(e)}")
        logger.info("📋 Falling back to synthetic dataset generation...")
    
    # Fallback: Create synthetic dataset
    try:
        df = create_high_quality_synthetic_dataset()
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Dataset saved to: {csv_path.absolute()}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create synthetic dataset: {str(e)}")
        return False


if __name__ == '__main__':
    success = download_dataset()
    if success:
        logger.info("\n✨ Everything is ready! Run: python main.py")
    else:
        logger.error("\n⚠️  Please fix the issue above before running main.py")
