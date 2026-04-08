"""
Trainer Module
Handles training, evaluation, and metrics calculation
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix)
from typing import Dict, Tuple, List
import logging
from tqdm import tqdm

from config import TRAIN_CONFIG, METRICS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Trainer:
    """Handles model training and evaluation"""
    
    def __init__(self, model: nn.Module, config: Dict = None, device: str = 'cpu'):
        """
        Initialize trainer
        
        Args:
            model: PyTorch model
            config: Training configuration
            device: Device to use ('cpu' or 'cuda')
        """
        self.model = model
        self.config = config or TRAIN_CONFIG
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Setup optimizer
        self.optimizer = self._setup_optimizer()
        
        # Setup loss function
        self.criterion = self._setup_criterion()
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        logger.info(f"Trainer initialized on device: {self.device}")
    
    def _setup_optimizer(self) -> optim.Optimizer:
        """Setup optimizer based on config"""
        opt_name = self.config.get('optimizer', 'adam').lower()
        lr = self.config.get('learning_rate', 0.001)
        weight_decay = self.config.get('weight_decay', 1e-5)
        
        if opt_name == 'adam':
            return optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        elif opt_name == 'sgd':
            return optim.SGD(self.model.parameters(), lr=lr, 
                           momentum=0.9, weight_decay=weight_decay)
        elif opt_name == 'adamw':
            return optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unknown optimizer: {opt_name}")
    
    def _setup_criterion(self) -> nn.Module:
        """Setup loss function"""
        loss_name = self.config.get('loss_function', 'cross_entropy').lower()
        
        if loss_name == 'cross_entropy':
            return nn.CrossEntropyLoss()
        elif loss_name == 'bce':
            return nn.BCEWithLogitsLoss()
        else:
            raise ValueError(f"Unknown loss function: {loss_name}")
    
    def create_dataloader(self, X: np.ndarray, y: np.ndarray, 
                         shuffle: bool = True) -> DataLoader:
        """
        Create PyTorch DataLoader from numpy arrays
        
        Args:
            X: Features
            y: Labels
            shuffle: Whether to shuffle data
            
        Returns:
            DataLoader
        """
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.LongTensor(y)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(
            dataset,
            batch_size=self.config['batch_size'],
            shuffle=shuffle,
            num_workers=0
        )
        
        return dataloader
    
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, float]:
        """
        Train for one epoch
        
        Args:
            train_loader: Training data loader
            
        Returns:
            Average loss and accuracy
        """
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Calculate accuracy
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100.0 * correct / total
        
        return avg_loss, accuracy
    
    def evaluate(self, test_loader: DataLoader) -> Tuple[float, float]:
        """
        Evaluate model
        
        Args:
            test_loader: Test data loader
            
        Returns:
            Average loss and accuracy
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        avg_loss = total_loss / len(test_loader)
        accuracy = 100.0 * correct / total
        
        return avg_loss, accuracy
    
    def train(self, train_data: Tuple[np.ndarray, np.ndarray],
              val_data: Tuple[np.ndarray, np.ndarray] = None,
              num_epochs: int = None,
              verbose: bool = True) -> Dict:
        """
        Complete training loop
        
        Args:
            train_data: (X_train, y_train)
            val_data: (X_val, y_val) optional
            num_epochs: Number of epochs
            verbose: Whether to print progress
            
        Returns:
            Training history
        """
        num_epochs = num_epochs or self.config['num_epochs']
        
        # Create data loaders
        X_train, y_train = train_data
        train_loader = self.create_dataloader(X_train, y_train, shuffle=True)
        
        val_loader = None
        if val_data is not None:
            X_val, y_val = val_data
            val_loader = self.create_dataloader(X_val, y_val, shuffle=False)
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        patience = self.config.get('early_stopping_patience', 5)
        
        for epoch in range(num_epochs):
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            
            # Validate
            if val_loader is not None:
                val_loss, val_acc = self.evaluate(val_loader)
                self.history['val_loss'].append(val_loss)
                self.history['val_acc'].append(val_acc)
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch+1}")
                    break
                
                if verbose:
                    logger.info(f"Epoch [{epoch+1}/{num_epochs}] - "
                              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
                              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            else:
                if verbose:
                    logger.info(f"Epoch [{epoch+1}/{num_epochs}] - "
                              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        
        return self.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features
            
        Returns:
            Predicted labels
        """
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(X_tensor)
            _, predicted = torch.max(outputs.data, 1)
        
        return predicted.cpu().numpy()
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities
        
        Args:
            X: Features
            
        Returns:
            Class probabilities
        """
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(X_tensor)
            probabilities = torch.softmax(outputs, dim=1)
        
        return probabilities.cpu().numpy()
    
    def calculate_metrics(self, X: np.ndarray, y_true: np.ndarray) -> Dict:
        """
        Calculate Flower-safe metrics (no arrays, no numpy types)
        """
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(
            y_true, y_pred, average="binary", zero_division=0
        )
        recall = recall_score(
            y_true, y_pred, average="binary", zero_division=0
        )
        f1 = f1_score(
            y_true, y_pred, average="binary", zero_division=0
        )
        # Safe ROC-AUC
        try:
            auc = roc_auc_score(y_true, y_proba[:, 1])
        except Exception:
            auc = 0.0

        # IMPORTANT: Return only pure Python floats
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "auc_roc": float(auc),
            }
    
    def get_model_updates(self) -> Dict[str, np.ndarray]:
        """
        Get model parameters as numpy arrays (for federated learning)
        
        Returns:
            Dictionary of parameter name -> numpy array
        """
        return {name: param.data.cpu().numpy() 
                for name, param in self.model.named_parameters()}
    
    def set_model_updates(self, updates: Dict[str, np.ndarray]):
        """
        Set model parameters from numpy arrays
        
        Args:
            updates: Dictionary of parameter name -> numpy array
        """
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                if name in updates:
                    param.copy_(torch.from_numpy(updates[name]))


# ===========================
# USAGE EXAMPLE
# ===========================
if __name__ == "__main__":
    from models.fraud_detector import ModelFactory
    
    # Create model
    model = ModelFactory.create_model('neural_network')
    
    # Create trainer
    trainer = Trainer(model, device='cpu')
    
    # Create dummy data
    X_train = np.random.randn(1000, 30)
    y_train = np.random.randint(0, 2, 1000)
    X_val = np.random.randn(200, 30)
    y_val = np.random.randint(0, 2, 200)
    
    # Train
    print("\n🚀 Starting training...")
    history = trainer.train(
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        num_epochs=5,
        verbose=True
    )
    
    # Evaluate
    metrics = trainer.calculate_metrics(X_val, y_val)
    print(f"\n✅ Training complete!")
    print(f"Validation Metrics:")
    for key, value in metrics.items():
        if key != 'confusion_matrix':
            print(f"  {key}: {value:.4f}")
