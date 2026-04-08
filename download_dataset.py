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


def download_dataset():
    """Download the credit card fraud dataset from Kaggle"""
    
    logger.info("🔍 Checking Kaggle setup...")
    if not setup_kaggle_credentials():
        logger.error("⚠️  Please configure Kaggle credentials first!")
        return False
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    csv_path = data_dir / 'creditcard.csv'
    
    # Check if already downloaded
    if csv_path.exists():
        logger.info(f"✅ Dataset already exists at {csv_path}")
        return True
    
    try:
        logger.info("📥 Downloading credit card fraud dataset from Kaggle...")
        logger.info("   Dataset: mlg-ulb/creditcardfraud")
        
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Authenticate
        api = KaggleApi()
        api.authenticate()
        logger.info("✅ Kaggle authentication successful")
        
        # Download dataset
        logger.info("⏳ Downloading dataset (this may take a few minutes)...")
        api.dataset_download_files('mlg-ulb/creditcardfraud', path='data', unzip=True)
        
        logger.info("✅ Dataset downloaded successfully!")
        logger.info(f"📂 Location: {csv_path.absolute()}")
        
        # Verify
        if csv_path.exists():
            file_size_mb = csv_path.stat().st_size / (1024 * 1024)
            logger.info(f"📊 File size: {file_size_mb:.2f} MB")
            return True
        else:
            logger.error("❌ Dataset file not found after download")
            return False
            
    except ImportError:
        logger.error("❌ kaggle-api not installed!")
        logger.info("📦 Install it with: pip install kaggle")
        return False
    except Exception as e:
        logger.error(f"❌ Download failed: {str(e)}")
        logger.info("\n💡 Alternative: Manual Download")
        logger.info("-" * 60)
        logger.info("1. Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
        logger.info("2. Click 'Download' button")
        logger.info("3. Extract to: ./data/creditcard.csv")
        logger.info("-" * 60)
        return False


if __name__ == '__main__':
    success = download_dataset()
    if success:
        logger.info("\n✨ Everything is ready! Run: python main.py")
    else:
        logger.error("\n⚠️  Please fix the issue above before running main.py")
