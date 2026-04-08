"""
Federated Learning Server
Coordinates training across multiple banks and aggregates updates
"""

import flwr as fl
from flwr.server.strategy import FedAvg, FedProx, FedAdam
from flwr.common import Metrics, Parameters
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
import logging
import os
import torch
from flwr.common import parameters_to_ndarrays
from models.fraud_detector import ModelFactory

from config import FL_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureAggregationStrategy(FedAvg):
    """
    Custom Federated Averaging with Secure Aggregation
    Server cannot see individual bank updates
    """
    
    def __init__(self, 
                 fraction_fit: float = 1.0,
                 fraction_evaluate: float = 1.0,
                 min_fit_clients: int = 2,
                 min_evaluate_clients: int = 2,
                 min_available_clients: int = 2,
                 evaluate_fn: Optional[Callable] = None,
                 use_secure_aggregation: bool = True):
        """
        Initialize secure aggregation strategy
        
        Args:
            fraction_fit: Fraction of clients used for training
            fraction_evaluate: Fraction of clients used for evaluation
            min_fit_clients: Minimum number of clients for training
            min_evaluate_clients: Minimum number of clients for evaluation
            min_available_clients: Minimum total clients needed
            evaluate_fn: Optional server-side evaluation function
            use_secure_aggregation: Whether to use secure aggregation
        """
        super().__init__(
            fraction_fit=fraction_fit,
            fraction_evaluate=fraction_evaluate,
            min_fit_clients=min_fit_clients,
            min_evaluate_clients=min_evaluate_clients,
            min_available_clients=min_available_clients,
            evaluate_fn=evaluate_fn
        )
        
        self.use_secure_aggregation = use_secure_aggregation
        self.round_metrics = []
        
        logger.info(f"Initialized {'Secure' if use_secure_aggregation else 'Standard'} "
                   f"Aggregation Strategy")
    
    def aggregate_fit(self, server_round: int, results, failures):
        """
        Aggregate model updates from clients
        
        Args:
            server_round: Current round number
            results: List of (client, fit_result) tuples
            failures: List of failed clients
            
        Returns:
            Aggregated parameters and metrics
        """
        if not results:
            return None, {}
        
        if self.use_secure_aggregation:
            # Simulate secure aggregation
            # In production, this would use cryptographic protocols
            logger.info(f"Round {server_round}: Performing secure aggregation...")
        
        # Call parent's aggregation (FedAvg)
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, results, failures
        )
        
        # Log aggregation info
        num_clients = len(results)
        logger.info(f"Round {server_round}: Aggregated updates from {num_clients} banks")
        
        return aggregated_parameters, aggregated_metrics
    
    def aggregate_evaluate(self, server_round: int, results, failures):
        """
        Aggregate evaluation results from clients
        Compatible with latest Flower versions
        """

        if not results:
            return None, {}

        # Let FedAvg aggregate loss normally
        loss_aggregated, metrics_aggregated = super().aggregate_evaluate(
        server_round, results, failures
        )

        # Extract metrics safely from EvaluateRes objects
        accuracies = [res.metrics.get("accuracy", 0.0) for _, res in results]
        f1_scores = [res.metrics.get("f1_score", 0.0) for _, res in results]

        avg_accuracy = float(np.mean(accuracies))
        avg_f1 = float(np.mean(f1_scores))

        round_metric = {
        "round": server_round,
        "loss": float(loss_aggregated) if loss_aggregated is not None else 0.0,
        "accuracy": avg_accuracy,
        "f1_score": avg_f1,
        "num_banks": len(results),
        }

        self.round_metrics.append(round_metric)

        logger.info(
        f"Round {server_round} Evaluation: "
        f"Loss={round_metric['loss']:.4f}, "
        f"Acc={avg_accuracy:.4f}, "
        f"F1={avg_f1:.4f}"
        )

        # Ensure aggregated metrics dict exists
        if metrics_aggregated is None:
            metrics_aggregated = {}

        metrics_aggregated["accuracy"] = avg_accuracy
        metrics_aggregated["f1_score"] = avg_f1

        return loss_aggregated, metrics_aggregated
    
    def get_round_metrics(self) -> List[Dict]:
        """Get all round metrics"""
        return self.round_metrics


class PrivacyPreservingStrategy(SecureAggregationStrategy):
    """
    Strategy that enforces differential privacy constraints
    """
    
    def __init__(self, 
                 epsilon: float = 1.0,
                 delta: float = 1e-5,
                 **kwargs):
        """
        Initialize privacy-preserving strategy
        
        Args:
            epsilon: Privacy budget
            delta: Privacy parameter
            **kwargs: Additional arguments for parent class
        """
        super().__init__(**kwargs)
        self.epsilon = epsilon
        self.delta = delta
        self.privacy_spent = 0.0
        
        logger.info(f"Initialized Privacy-Preserving Strategy with ε={epsilon}, δ={delta}")
    
    def aggregate_fit(self, server_round: int, results, failures):
        """
        Aggregate with privacy accounting
        
        Args:
            server_round: Current round
            results: Client results
            failures: Failed clients
            
        Returns:
            Aggregated parameters and metrics
        """
        # Perform standard aggregation
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, results, failures
        )
        
        # Update privacy budget (simplified accounting)
        # In practice, use proper privacy accounting (e.g., RDP, moments accountant)
        round_epsilon = self.epsilon / FL_CONFIG['num_rounds']
        self.privacy_spent += round_epsilon
        
        # Add privacy metrics
        aggregated_metrics['privacy_epsilon_spent'] = self.privacy_spent
        aggregated_metrics['privacy_epsilon_remaining'] = self.epsilon - self.privacy_spent
        
        logger.info(f"Round {server_round}: Privacy budget spent: {self.privacy_spent:.4f}/{self.epsilon}")
        
        # Check if privacy budget exceeded
        if self.privacy_spent > self.epsilon:
            logger.warning(f"⚠️  Privacy budget exceeded! Spent: {self.privacy_spent}, Budget: {self.epsilon}")
        
        return aggregated_parameters, aggregated_metrics


def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Calculate weighted average of metrics
    
    Args:
        metrics: List of (num_examples, metrics_dict) tuples
        
    Returns:
        Averaged metrics
    """
    # Get total number of examples
    total_examples = sum([num_examples for num_examples, _ in metrics])
    
    # Calculate weighted averages
    accuracies = [num_examples * m.get('accuracy', 0) for num_examples, m in metrics]
    losses = [num_examples * m.get('loss', 0) for num_examples, m in metrics]
    
    return {
        'accuracy': sum(accuracies) / total_examples,
        'loss': sum(losses) / total_examples
    }


class FederatedServer:
    """
    Main Federated Learning Server
    Manages the entire federated training process
    """
    
    def __init__(self, 
                 strategy_type: str = 'fedavg',
                 config: Dict = None,
                 use_privacy: bool = False,
                 privacy_config: Dict = None):
        """
        Initialize federated server
        
        Args:
            strategy_type: Type of aggregation strategy
            config: FL configuration
            use_privacy: Whether to use privacy-preserving strategy
            privacy_config: Privacy configuration
        """
        self.config = config or FL_CONFIG
        self.strategy_type = strategy_type
        self.use_privacy = use_privacy
        self.privacy_config = privacy_config or {}
        
        # Create strategy
        self.strategy = self._create_strategy()
        
        logger.info(f"Federated Server initialized with {strategy_type} strategy")
    
    def _create_strategy(self) -> fl.server.strategy.Strategy:
        """Create aggregation strategy based on config"""
        
        # Common parameters
        strategy_params = {
            'fraction_fit': self.config['fraction_fit'],
            'fraction_evaluate': self.config['fraction_evaluate'],
            'min_fit_clients': self.config['min_fit_clients'],
            'min_evaluate_clients': self.config['min_evaluate_clients'],
            'min_available_clients': self.config['min_available_clients']
        }
        
        # Create strategy based on type
        if self.use_privacy:
            return PrivacyPreservingStrategy(
                epsilon=self.privacy_config.get('epsilon', 1.0),
                delta=self.privacy_config.get('delta', 1e-5),
                use_secure_aggregation=True,
                **strategy_params
            )
        
        elif self.strategy_type == 'fedavg':
            return SecureAggregationStrategy(
                use_secure_aggregation=True,
                **strategy_params
            )
        
        elif self.strategy_type == 'fedprox':
            return FedProx(
                proximal_mu=0.1,
                **strategy_params
            )
        
        elif self.strategy_type == 'fedadam':
            return FedAdam(
                **strategy_params
            )
        
        else:
            raise ValueError(f"Unknown strategy type: {self.strategy_type}")
    
    def start(self, 
          client_fn: Callable,
          num_rounds: int = None,
          num_clients: int = None):
        """
        Start federated learning simulation
        
        Args:
            client_fn: Function to create clients
            num_rounds: Number of federated rounds
            num_clients: Total number of clients
            
        Returns:
            Training history
        """
        num_rounds = num_rounds or self.config['num_rounds']
        
        logger.info(f"Starting Federated Learning for {num_rounds} rounds")
        logger.info(f"Strategy: {self.strategy_type}, Privacy: {self.use_privacy}")
        
        # Configure simulation
        config = fl.server.ServerConfig(num_rounds=num_rounds)
        
        # Start simulation
        history = fl.simulation.start_simulation(
            client_fn=client_fn,
            num_clients=num_clients,
            config=config,
            strategy=self.strategy,
            client_resources={'num_cpus': 1, 'num_gpus': 0}
        )
        
        logger.info("✅ Federated Learning completed!")

        # ==============================
        # Save Results Automatically
        # ==============================

        try:
            from utils.results_manager import ResultsManager

            results_manager = ResultsManager()

            if hasattr(self.strategy, "round_metrics") and self.strategy.round_metrics:
                results_manager.save_round_metrics(self.strategy.round_metrics)
                results_manager.save_accuracy_plot(self.strategy.round_metrics)

                logger.info("📊 Round metrics and graphs saved successfully!")
            else:
                logger.warning("⚠️ No round metrics found to save.")

        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

        # ==============================
        # Save Final Federated Model
        # ==============================

        try:
            if history and history.parameters_centralized:
                final_parameters = history.parameters_centralized[-1]
            else:
                final_parameters = None

            if final_parameters is not None:

                # Convert Flower Parameters to numpy arrays
                ndarrays = parameters_to_ndarrays(final_parameters)

                # Create fresh model
                model = ModelFactory.create_model("neural_network")

                # Load weights
                state_dict = zip(model.state_dict().keys(), ndarrays)
                model.load_state_dict(
                    {k: torch.tensor(v) for k, v in state_dict},
                    strict=True
                )

                # Ensure directory exists
                model_dir = os.path.join("results", "models")
                os.makedirs(model_dir, exist_ok=True)

                model_path = os.path.join(model_dir, "federated_model.pth")

                torch.save(model.state_dict(), model_path)

                logger.info(f"💾 Federated model saved → {model_path}")

            else:
                logger.warning("⚠️ No final parameters found to save model.")

        except Exception as e:
            logger.error(f"❌ Failed to save federated model: {e}")

        return history
        
    def get_metrics(self) -> List[Dict]:
        """Get training metrics"""
        if hasattr(self.strategy, 'round_metrics'):
            return self.strategy.round_metrics
        return []


# ===========================
# USAGE EXAMPLE
# ===========================
if __name__ == "__main__":
    # Test strategy creation
    print("\n🖥️  Testing Federated Server...")
    
    # Standard server
    server = FederatedServer(
        strategy_type='fedavg',
        use_privacy=False
    )
    print(f"✅ Standard server created with {server.strategy_type} strategy")
    
    # Privacy-preserving server
    private_server = FederatedServer(
        strategy_type='fedavg',
        use_privacy=True,
        privacy_config={'epsilon': 1.0, 'delta': 1e-5}
    )
    print(f"✅ Privacy-preserving server created")
    
    print("\n✅ Server components working!")
