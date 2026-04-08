"""
Configuration file for Privacy-Preserving Fraud Detection System
"""

# ===========================
# GENERAL SETTINGS
# ===========================
PROJECT_NAME = "Privacy-Preserving Cross-Bank Fraud Intelligence Network"
RANDOM_SEED = 42

# ===========================
# DATA SETTINGS
# ===========================
DATA_CONFIG = {
    'dataset_path': 'data/creditcard.csv',  # Path to fraud dataset
    'num_banks': 5,  # Number of banks to simulate
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
    'balance_data': True,  # Handle class imbalance
    'scaling': 'standard'  # 'standard' or 'minmax'
}

# ===========================
# MODEL SETTINGS
# ===========================
MODEL_CONFIG = {
    'model_type': 'neural_network',  # 'neural_network', 'lstm', 'random_forest'
    'input_dim': 30,  # Number of features (depends on dataset)
    'hidden_layers': [128, 64, 32],
    'output_dim': 2,  # Binary classification (fraud/not fraud)
    'activation': 'relu',
    'dropout_rate': 0.3,
    'batch_norm': True
}

# ===========================
# TRAINING SETTINGS
# ===========================
TRAIN_CONFIG = {
    'batch_size': 256,
    'learning_rate': 0.001,
    'num_epochs': 10,
    'optimizer': 'adam',
    'loss_function': 'cross_entropy',
    'early_stopping_patience': 5,
    'weight_decay': 1e-5
}

# ===========================
# FEDERATED LEARNING SETTINGS
# ===========================
FL_CONFIG = {
    'num_rounds': 20,  # Number of federated rounds
    'fraction_fit': 1.0,  # Fraction of clients for training
    'fraction_evaluate': 1.0,  # Fraction of clients for evaluation
    'min_fit_clients': 3,  # Minimum clients to start training
    'min_evaluate_clients': 3,
    'min_available_clients': 3,
    'server_address': 'localhost:8080',
    'aggregation_strategy': 'fedavg'  # 'fedavg', 'fedprox', 'fedadam'
}

# ===========================
# DIFFERENTIAL PRIVACY SETTINGS
# ===========================
DP_CONFIG = {
    'enabled': True,
    'epsilon': 1.0,  # Privacy budget (lower = more private)
    'delta': 1e-5,  # Privacy parameter
    'max_grad_norm': 1.0,  # Gradient clipping threshold
    'noise_multiplier': 1.1,  # Amount of noise to add
    'target_epsilon': None,  # Target epsilon (if using accounting)
    'epochs': 10,
    'sample_rate': 0.01  # Sampling rate for privacy accounting
}

# Different epsilon values for experiments
EPSILON_VALUES = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

# ===========================
# SECURE AGGREGATION SETTINGS
# ===========================
SECURE_AGG_CONFIG = {
    'enabled': True,
    'num_shares': 3,  # Number of secret shares
    'threshold': 2,  # Minimum shares needed to reconstruct
    'encryption_type': 'additive_secret_sharing'  # or 'homomorphic'
}

# ===========================
# ATTACK SIMULATION SETTINGS
# ===========================
ATTACK_CONFIG = {
    'model_inversion': {
        'enabled': True,
        'num_iterations': 1000,
        'learning_rate': 0.1,
        'target_class': 1,  # Fraud class
        'regularization': 1e-4
    },
    'gradient_leakage': {
        'enabled': True,
        'num_samples': 100,
        'reconstruction_method': 'dlg'  # Deep Leakage from Gradients
    },
    'membership_inference': {
        'enabled': False,
        'attack_model': 'shadow_model'
    }
}

# ===========================
# EVALUATION METRICS
# ===========================
METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1_score',
    'auc_roc',
    'confusion_matrix',
    'privacy_loss'
]

# ===========================
# EXPERIMENT SETTINGS
# ===========================
EXPERIMENT_CONFIG = {
    'exp1_accuracy_comparison': {
        'models': ['centralized', 'federated', 'federated_dp'],
        'num_runs': 5,  # Repeat for statistical significance
        'save_results': True
    },
    'exp2_privacy_accuracy_tradeoff': {
        'epsilon_range': EPSILON_VALUES,
        'num_runs': 3,
        'plot_curve': True
    },
    'exp3_attack_resistance': {
        'models': ['no_privacy', 'with_privacy'],
        'attacks': ['model_inversion', 'gradient_leakage'],
        'num_attacks': 50
    },
    'exp4_communication_efficiency': {
        'measure_bandwidth': True,
        'compare_methods': ['centralized', 'federated']
    }
}

# ===========================
# LOGGING & OUTPUT
# ===========================
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'results/training.log',
    'tensorboard_dir': 'results/tensorboard',
    'save_checkpoints': True,
    'checkpoint_dir': 'results/checkpoints',
    'save_frequency': 5  # Save every N rounds
}

OUTPUT_CONFIG = {
    'results_dir': 'results',
    'graphs_dir': 'results/graphs',
    'tables_dir': 'results/tables',
    'models_dir': 'results/models',
    'save_format': ['csv', 'json', 'png']
}
