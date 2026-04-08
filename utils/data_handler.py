"""
Data Handler for Fraud Detection System
Handles loading, preprocessing, and distribution of data across banks
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from imblearn.over_sampling import SMOTE
from typing import Dict, List, Tuple
import logging

from config import DATA_CONFIG, RANDOM_SEED

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataHandler:
    """Handles all data operations for the fraud detection system"""
    
    def __init__(self, config: Dict = None):
        self.config = config or DATA_CONFIG
        self.scaler = None
        self.num_features = None
        
    def load_dataset(self, path: str = None) -> pd.DataFrame:
        """
        Load fraud detection dataset
        
        Args:
            path: Path to CSV file
            
        Returns:
            DataFrame with fraud data
        """
        path = path or self.config['dataset_path']
        logger.info(f"Loading dataset from {path}")
        
        try:
            df = pd.read_csv(path)
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            logger.info(f"Fraud cases: {df['Class'].sum()}, Normal: {len(df) - df['Class'].sum()}")
            return df
        except FileNotFoundError:
            logger.error(f"Dataset not found at {path}")
            logger.info("Creating synthetic fraud dataset for demonstration...")
            return self._create_synthetic_dataset()
    
    def _create_synthetic_dataset(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Create synthetic fraud dataset for testing
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Synthetic fraud DataFrame
        """
        np.random.seed(RANDOM_SEED)
        
        # Generate features (simulating transaction features)
        n_features = 28
        X = np.random.randn(n_samples, n_features)
        
        # Generate labels (5% fraud rate)
        y = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
        
        # Make fraud transactions slightly different
        fraud_indices = np.where(y == 1)[0]
        X[fraud_indices] += np.random.randn(len(fraud_indices), n_features) * 2
        
        # Add Amount and Time columns (typical in fraud datasets)
        amounts = np.random.exponential(scale=50, size=n_samples)
        times = np.random.uniform(0, 172800, size=n_samples)  # 48 hours in seconds
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=[f'V{i}' for i in range(1, n_features + 1)])
        df['Time'] = times
        df['Amount'] = amounts
        df['Class'] = y
        
        logger.info(f"Created synthetic dataset with {n_samples} samples")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess the dataset
        
        Args:
            df: Raw DataFrame
            
        Returns:
            X (features), y (labels)
        """
        # Separate features and labels
        X = df.drop('Class', axis=1).values
        y = df['Class'].values
        
        # Store number of features
        self.num_features = X.shape[1]
        
        # Scale features
        if self.config['scaling'] == 'standard':
            self.scaler = StandardScaler()
        else:
            self.scaler = MinMaxScaler()
        
        X = self.scaler.fit_transform(X)
        
        logger.info(f"Preprocessed data. Features: {X.shape[1]}, Samples: {X.shape[0]}")
        return X, y
    
    def balance_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Balance the dataset using SMOTE
        
        Args:
            X: Feature array
            y: Label array
            
        Returns:
            Balanced X, y
        """
        if not self.config['balance_data']:
            return X, y
        
        logger.info("Balancing dataset using SMOTE...")
        original_counts = np.bincount(y.astype(int))
        
        smote = SMOTE(random_state=RANDOM_SEED)
        X_balanced, y_balanced = smote.fit_resample(X, y)
        
        new_counts = np.bincount(y_balanced.astype(int))
        logger.info(f"Original distribution: {original_counts}")
        logger.info(f"Balanced distribution: {new_counts}")
        
        return X_balanced, y_balanced
    
    def split_data(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Tuple]:
        """
        Split data into train, validation, and test sets
        
        Args:
            X: Features
            y: Labels
            
        Returns:
            Dictionary with train, val, test splits
        """
        train_size = self.config['train_split']
        val_size = self.config['val_split']
        test_size = self.config['test_split']
        
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_SEED, stratify=y
        )
        
        # Second split: separate train and validation
        relative_val_size = val_size / (train_size + val_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=relative_val_size, 
            random_state=RANDOM_SEED, stratify=y_temp
        )
        
        logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return {
            'train': (X_train, y_train),
            'val': (X_val, y_val),
            'test': (X_test, y_test)
        }
    
    def distribute_to_banks(self, X: np.ndarray, y: np.ndarray, 
                           num_banks: int = None) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Distribute data across multiple banks (IID distribution)
        
        Args:
            X: Features
            y: Labels
            num_banks: Number of banks to simulate
            
        Returns:
            List of (X, y) tuples, one per bank
        """
        num_banks = num_banks or self.config['num_banks']
        
        # Shuffle data
        indices = np.random.permutation(len(X))
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        # Split into equal parts
        bank_data = []
        samples_per_bank = len(X) // num_banks
        
        for i in range(num_banks):
            start_idx = i * samples_per_bank
            end_idx = start_idx + samples_per_bank if i < num_banks - 1 else len(X)
            
            X_bank = X_shuffled[start_idx:end_idx]
            y_bank = y_shuffled[start_idx:end_idx]
            
            bank_data.append((X_bank, y_bank))
            logger.info(f"Bank {i+1}: {len(X_bank)} samples, "
                       f"Fraud ratio: {y_bank.sum() / len(y_bank):.4f}")
        
        return bank_data
    
    def distribute_non_iid(self, X: np.ndarray, y: np.ndarray, 
                          num_banks: int = None, 
                          alpha: float = 0.5) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Distribute data in a non-IID manner (more realistic)
        Uses Dirichlet distribution to create imbalanced data across banks
        
        Args:
            X: Features
            y: Labels
            num_banks: Number of banks
            alpha: Dirichlet concentration parameter (lower = more non-IID)
            
        Returns:
            List of (X, y) tuples with non-IID distribution
        """
        num_banks = num_banks or self.config['num_banks']
        num_classes = len(np.unique(y))
        
        # Get indices for each class
        class_indices = [np.where(y == i)[0] for i in range(num_classes)]
        
        bank_data = [[] for _ in range(num_banks)]
        
        # Distribute each class according to Dirichlet distribution
        for c_idx in class_indices:
            np.random.shuffle(c_idx)
            proportions = np.random.dirichlet([alpha] * num_banks)
            proportions = (np.cumsum(proportions) * len(c_idx)).astype(int)[:-1]
            
            class_splits = np.split(c_idx, proportions)
            
            for bank_id, indices in enumerate(class_splits):
                bank_data[bank_id].extend(indices)
        
        # Convert to arrays
        result = []
        for bank_id, indices in enumerate(bank_data):
            indices = np.array(indices)
            np.random.shuffle(indices)
            
            X_bank = X[indices]
            y_bank = y[indices]
            
            result.append((X_bank, y_bank))
            logger.info(f"Bank {bank_id+1} (Non-IID): {len(X_bank)} samples, "
                       f"Fraud ratio: {y_bank.sum() / len(y_bank):.4f}")
        
        return result
    
    def get_data_statistics(self, bank_datasets: List[Tuple]) -> Dict:
        """
        Calculate statistics about the distributed data
        
        Args:
            bank_datasets: List of (X, y) tuples per bank
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'num_banks': len(bank_datasets),
            'total_samples': sum(len(y) for _, y in bank_datasets),
            'bank_sizes': [len(y) for _, y in bank_datasets],
            'fraud_ratios': [y.sum() / len(y) for _, y in bank_datasets],
            'total_fraud_cases': sum(y.sum() for _, y in bank_datasets)
        }
        
        logger.info(f"Data Statistics: {stats}")
        return stats


# ===========================
# USAGE EXAMPLE
# ===========================
if __name__ == "__main__":
    # Initialize handler
    handler = DataHandler()
    
    # Load and preprocess data
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    
    # Balance if needed
    X, y = handler.balance_data(X, y)
    
    # Split data
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    
    # Distribute to banks (IID)
    bank_data_iid = handler.distribute_to_banks(X_train, y_train, num_banks=5)
    
    # Distribute to banks (Non-IID)
    bank_data_non_iid = handler.distribute_non_iid(X_train, y_train, num_banks=5, alpha=0.5)
    
    # Get statistics
    stats = handler.get_data_statistics(bank_data_iid)
    
    print("\n✅ Data handler working successfully!")
    print(f"Total banks: {stats['num_banks']}")
    print(f"Total samples: {stats['total_samples']}")
