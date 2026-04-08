"""
Federated Learning Client
Represents a single bank in the federated system
"""

import flwr as fl
import torch
import numpy as np
from typing import Dict, List, Tuple
import logging

from models.fraud_detector import FraudDetectorNN
from utils.trainer import Trainer
from config import TRAIN_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankClient(fl.client.NumPyClient):
    """
    Federated Learning Client for a single bank
    Each bank trains locally and shares only model updates
    """
    
    def __init__(self, 
                 bank_id: int,
                 X_train: np.ndarray,
                 y_train: np.ndarray,
                 X_val: np.ndarray,
                 y_val: np.ndarray,
                 model: torch.nn.Module,
                 config: Dict = None):
        """
        Initialize bank client
        
        Args:
            bank_id: Unique identifier for this bank
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            model: PyTorch model
            config: Training configuration
        """
        self.bank_id = bank_id
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.model = model
        self.config = config or TRAIN_CONFIG
        
        # Create trainer
        self.trainer = Trainer(self.model, config=self.config)
        
        logger.info(f"Bank {bank_id} initialized with {len(X_train)} training samples")
    
    def get_parameters(self, config: Dict = None) -> List[np.ndarray]:
        """
        Get model parameters as list of numpy arrays
        
        Args:
            config: Optional configuration
            
        Returns:
            List of parameter arrays
        """
        return [val.cpu().numpy() for val in self.model.state_dict().values()]
    
    def set_parameters(self, parameters: List[np.ndarray]):
        """
        Set model parameters from list of numpy arrays
        
        Args:
            parameters: List of parameter arrays from server
        """
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)
    
    def fit(self, parameters: List[np.ndarray], config: Dict) -> Tuple[List[np.ndarray], int, Dict]:
        """
        Train model locally on bank's data
        
        Args:
            parameters: Global model parameters from server
            config: Training configuration from server
            
        Returns:
            Updated parameters, number of samples, metrics
        """
        # Set global parameters
        self.set_parameters(parameters)
        
        # Get local training config
        local_epochs = config.get('local_epochs', self.config['num_epochs'])
        
        logger.info(f"Bank {self.bank_id}: Starting local training for {local_epochs} epochs")
        
        # Train locally
        history = self.trainer.train(
            train_data=(self.X_train, self.y_train),
            val_data=(self.X_val, self.y_val),
            num_epochs=local_epochs,
            verbose=False
        )
        
        # Get updated parameters
        updated_parameters = self.get_parameters()
        
        # Calculate metrics
        raw_metrics = self.trainer.calculate_metrics(self.X_val, self.y_val)

        metrics = {
            "accuracy": float(raw_metrics["accuracy"]),
            "precision": float(raw_metrics["precision"]),
            "recall": float(raw_metrics["recall"]),
            "f1_score": float(raw_metrics["f1_score"]),
        }
        
        logger.info(f"Bank {self.bank_id}: Training complete. "
                   f"Val Acc: {metrics['accuracy']:.4f}, "
                   f"Val F1: {metrics['f1_score']:.4f}")
        
        # Return updated parameters, number of samples, and metrics
        return updated_parameters, len(self.X_train), metrics
    
    def evaluate(self, parameters: List[np.ndarray], config: Dict):

        self.set_parameters(parameters)

        val_loader = self.trainer.create_dataloader(
            self.X_val, self.y_val, shuffle=False
        )
        loss, _ = self.trainer.evaluate(val_loader)
        raw_metrics = self.trainer.calculate_metrics(self.X_val, self.y_val)
        metrics = {
            "loss": float(loss),
            "accuracy": float(raw_metrics["accuracy"]),
            "precision": float(raw_metrics["precision"]),
            "recall": float(raw_metrics["recall"]),
            "f1_score": float(raw_metrics["f1_score"]),
        }

        return float(loss), len(self.X_val), metrics

class PrivateBankClient(BankClient):
    """
    Bank Client with Differential Privacy
    Adds privacy-preserving mechanisms to the standard client
    """
    
    def __init__(self, 
                 bank_id: int,
                 X_train: np.ndarray,
                 y_train: np.ndarray,
                 X_val: np.ndarray,
                 y_val: np.ndarray,
                 model: torch.nn.Module,
                 config: Dict = None,
                 privacy_config: Dict = None):
        """
        Initialize private bank client with differential privacy
        
        Args:
            bank_id: Bank identifier
            X_train, y_train: Training data
            X_val, y_val: Validation data
            model: PyTorch model
            config: Training configuration
            privacy_config: Privacy configuration (epsilon, delta, etc.)
        """
        super().__init__(bank_id, X_train, y_train, X_val, y_val, model, config)
        
        self.privacy_config = privacy_config or {}
        self.epsilon = self.privacy_config.get('epsilon', 1.0)
        self.delta = self.privacy_config.get('delta', 1e-5)
        self.max_grad_norm = self.privacy_config.get('max_grad_norm', 1.0)
        
        logger.info(f"Private Bank {bank_id} initialized with "
                   f"ε={self.epsilon}, δ={self.delta}")
    
    def _add_noise_to_parameters(self, parameters: List[np.ndarray]) -> List[np.ndarray]:
        """
        Add Gaussian noise to parameters for differential privacy
        
        Args:
            parameters: Model parameters
            
        Returns:
            Noised parameters
        """
        noised_parameters = []
        
        # Calculate noise scale based on privacy budget
        sensitivity = self.max_grad_norm
        noise_scale = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        
        for param in parameters:
            # Add Gaussian noise
            noise = np.random.normal(0, noise_scale, param.shape)
            noised_param = param + noise
            noised_parameters.append(noised_param)
        
        return noised_parameters
    
    def _clip_gradients(self):
        """Clip gradients for privacy"""
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
    
    def fit(self, parameters: List[np.ndarray], config: Dict) -> Tuple[List[np.ndarray], int, Dict]:
        """
        Train with differential privacy
        
        Args:
            parameters: Global model parameters
            config: Training configuration
            
        Returns:
            Noised parameters, number of samples, metrics
        """
        # Standard training
        updated_parameters, num_samples, metrics = super().fit(parameters, config)
        
        # Add noise for privacy
        private_parameters = self._add_noise_to_parameters(updated_parameters)
        
        # Add privacy loss to metrics
        metrics["privacy_epsilon"] = float(self.epsilon)
        metrics["privacy_delta"] = float(self.delta)
        
        logger.info(f"Private Bank {self.bank_id}: Added DP noise (ε={self.epsilon})")
        
        return private_parameters, num_samples, metrics


def create_client_fn(bank_id: int,
                     bank_data: Tuple[np.ndarray, np.ndarray],
                     val_data: Tuple[np.ndarray, np.ndarray],
                     model_factory,
                     use_privacy: bool = False,
                     privacy_config: Dict = None):
    """
    Factory function to create client instances
    
    Args:
        bank_id: Bank identifier
        bank_data: (X_train, y_train) for this bank
        val_data: (X_val, y_val) for this bank
        model_factory: Function to create model
        use_privacy: Whether to use differential privacy
        privacy_config: Privacy configuration
        
    Returns:
        Client function for Flower
    """
    X_train, y_train = bank_data
    X_val, y_val = val_data
    
    def client_fn(cid: str) -> fl.client.Client:
        # Create model
        model = model_factory()
        
        # Create appropriate client
        if use_privacy:
            return PrivateBankClient(
                bank_id=bank_id,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                model=model,
                privacy_config=privacy_config
            ).to_client()
        else:
            return BankClient(
                bank_id=bank_id,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                model=model
            ).to_client()
    
    return client_fn


# ===========================
# USAGE EXAMPLE
# ===========================
if __name__ == "__main__":
    from models.fraud_detector import ModelFactory
    
    # Create dummy data for one bank
    X_train = np.random.randn(1000, 30)
    y_train = np.random.randint(0, 2, 1000)
    X_val = np.random.randn(200, 30)
    y_val = np.random.randint(0, 2, 200)
    
    # Create model
    model = ModelFactory.create_model('neural_network')
    
    # Test standard client
    print("\n📱 Testing Standard Bank Client...")
    client = BankClient(
        bank_id=1,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        model=model
    )
    
    # Get initial parameters
    params = client.get_parameters()
    print(f"✅ Got {len(params)} parameter arrays")
    
    # Simulate training
    updated_params, num_samples, metrics = client.fit(params, {'local_epochs': 2})
    print(f"✅ Training complete. Samples: {num_samples}")
    print(f"   Metrics: Accuracy={metrics['accuracy']:.4f}, F1={metrics['f1_score']:.4f}")
    
    # Test private client
    print("\n🔐 Testing Private Bank Client...")
    model2 = ModelFactory.create_model('neural_network')
    private_client = PrivateBankClient(
        bank_id=2,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        model=model2,
        privacy_config={'epsilon': 1.0, 'delta': 1e-5}
    )
    
    params2 = private_client.get_parameters()
    private_params, num_samples2, metrics2 = private_client.fit(params2, {'local_epochs': 2})
    print(f"✅ Private training complete with ε={metrics2['privacy_epsilon']}")
