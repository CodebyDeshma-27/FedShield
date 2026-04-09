"""
Fraud Detection Models
Neural network architectures for fraud detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List
import logging

from config import MODEL_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudDetectorNN(nn.Module):
    """
    Neural Network for Fraud Detection
    Flexible architecture with configurable layers
    """
    
    def __init__(self, 
                 input_dim: int = 30,
                 hidden_layers: List[int] = [128, 64, 32],
                 output_dim: int = 2,
                 dropout_rate: float = 0.3,
                 batch_norm: bool = True):
        """
        Initialize fraud detection neural network
        
        Args:
            input_dim: Number of input features
            hidden_layers: List of hidden layer sizes
            output_dim: Number of output classes (2 for binary)
            dropout_rate: Dropout probability
            batch_norm: Whether to use batch normalization
        """
        super(FraudDetectorNN, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_layers_config = hidden_layers
        self.output_dim = output_dim
        self.dropout_rate = dropout_rate
        self.use_batch_norm = batch_norm
        
        # Build layers
        layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_layers):
            # Linear layer
            layers.append(nn.Linear(prev_dim, hidden_dim))
            
            # Batch normalization
            if batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))
            
            # Activation
            layers.append(nn.ReLU())
            
            # Dropout
            if dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))
            
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
        
        logger.info(f"Initialized FraudDetectorNN with architecture: "
                   f"{input_dim} -> {hidden_layers} -> {output_dim}")
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """Forward pass"""
        return self.network(x)
    
    def get_embedding(self, x):
        """Get intermediate representation (before final layer)"""
        for layer in self.network[:-1]:
            x = layer(x)
        return x


class FraudDetectorLSTM(nn.Module):
    """
    LSTM-based Fraud Detector for sequential transaction data
    Useful if modeling transaction sequences
    """
    
    def __init__(self,
                 input_dim: int = 30,
                 hidden_dim: int = 128,
                 num_layers: int = 2,
                 output_dim: int = 2,
                 dropout_rate: float = 0.3):
        super(FraudDetectorLSTM, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_dim, 
            hidden_dim, 
            num_layers, 
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(64, output_dim)
        
        logger.info(f"Initialized LSTM model with {num_layers} layers, "
                   f"hidden_dim={hidden_dim}")
    
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        x = F.relu(self.fc1(last_output))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


class ModelFactory:
    """Factory class to create different model types"""
    
    @staticmethod
    def create_model(model_type: str = 'neural_network', 
                    config: dict = None) -> nn.Module:
        """
        Create model based on type
        
        Args:
            model_type: Type of model ('neural_network', 'lstm')
            config: Model configuration
            
        Returns:
            PyTorch model
        """
        config = config or MODEL_CONFIG
        
        if model_type == 'neural_network':
            return FraudDetectorNN(
                input_dim=config['input_dim'],
                hidden_layers=config['hidden_layers'],
                output_dim=config['output_dim'],
                dropout_rate=config['dropout_rate'],
                batch_norm=config['batch_norm']
            )
        
        elif model_type == 'lstm':
            return FraudDetectorLSTM(
                input_dim=config['input_dim'],
                hidden_dim=128,
                num_layers=2,
                output_dim=config['output_dim'],
                dropout_rate=config['dropout_rate']
            )
        
        else:
            raise ValueError(f"Unknown model type: {model_type}")


class ModelUtils:
    """Utility functions for models"""
    
    @staticmethod
    def count_parameters(model: nn.Module) -> int:
        """Count trainable parameters in model"""
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    @staticmethod
    def get_model_size(model: nn.Module) -> float:
        """Get model size in MB"""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / 1024**2
        return size_mb
    
    @staticmethod
    def save_model(model: nn.Module, path: str):
        """Save model to disk"""
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_config': {
                'input_dim': model.input_dim,
                'hidden_layers': model.hidden_layers_config,
                'output_dim': model.output_dim,
                'dropout_rate': model.dropout_rate
            }
        }, path)
        logger.info(f"Model saved to {path}")
    
    @staticmethod
    def _model_config_from_checkpoint(checkpoint: dict) -> dict:
        config = checkpoint.get('model_config')
        if config is not None:
            return {
                'input_dim': config.get('input_dim', MODEL_CONFIG['input_dim']),
                'hidden_layers': config.get('hidden_layers', MODEL_CONFIG['hidden_layers']),
                'output_dim': config.get('output_dim', MODEL_CONFIG['output_dim']),
                'dropout_rate': config.get('dropout_rate', MODEL_CONFIG['dropout_rate']),
                'batch_norm': config.get('batch_norm', MODEL_CONFIG.get('batch_norm', True)),
            }

        logger.warning("Checkpoint does not include model_config; falling back to MODEL_CONFIG.")
        return {
            'input_dim': MODEL_CONFIG['input_dim'],
            'hidden_layers': MODEL_CONFIG['hidden_layers'],
            'output_dim': MODEL_CONFIG['output_dim'],
            'dropout_rate': MODEL_CONFIG['dropout_rate'],
            'batch_norm': MODEL_CONFIG.get('batch_norm', True),
        }

    @staticmethod
    def load_model(path: str, model_class=FraudDetectorNN) -> nn.Module:
        """Load model from disk"""
        checkpoint = torch.load(path)

        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            config = ModelUtils._model_config_from_checkpoint(checkpoint)
        elif isinstance(checkpoint, dict) and all(isinstance(k, str) for k in checkpoint.keys()):
            state_dict = checkpoint
            config = {
                'input_dim': MODEL_CONFIG['input_dim'],
                'hidden_layers': MODEL_CONFIG['hidden_layers'],
                'output_dim': MODEL_CONFIG['output_dim'],
                'dropout_rate': MODEL_CONFIG['dropout_rate'],
                'batch_norm': MODEL_CONFIG.get('batch_norm', True),
            }
            logger.warning("Loaded legacy state dict checkpoint without model_config; using default MODEL_CONFIG.")
        else:
            raise ValueError("Unsupported checkpoint format for model loading.")

        model = model_class(**config)
        model.load_state_dict(state_dict)

        logger.info(f"Model loaded from {path}")
        return model


# ===========================
# USAGE EXAMPLE
# ===========================
if __name__ == "__main__":
    # Create model
    model = ModelFactory.create_model('neural_network')
    
    print(f"\n✅ Model created successfully!")
    print(f"Total parameters: {ModelUtils.count_parameters(model):,}")
    print(f"Model size: {ModelUtils.get_model_size(model):.2f} MB")
    
    # Test forward pass
    batch_size = 32
    input_dim = 30
    dummy_input = torch.randn(batch_size, input_dim)
    
    output = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    
    # Test model saving
    ModelUtils.save_model(model, '/tmp/test_model.pth')
    loaded_model = ModelUtils.load_model('/tmp/test_model.pth')
    print("✅ Model save/load working!")
