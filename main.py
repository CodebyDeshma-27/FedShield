"""
Main Execution Script
Run the complete Privacy-Preserving Fraud Detection System
"""

import argparse
import logging
import numpy as np
import torch
from pathlib import Path

from config import DATA_CONFIG, MODEL_CONFIG, FL_CONFIG, DP_CONFIG
from utils.data_handler import DataHandler
from models.fraud_detector import ModelFactory, ModelUtils
from federated.client import create_client_fn, PrivateBankClient
from federated.server import FederatedServer
from utils.trainer import Trainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary directories"""
    dirs = ['results', 'results/graphs', 'results/tables', 'results/models', 'data']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info("✅ Directories created")


def train_centralized_baseline(X_train, y_train, X_val, y_val, X_test, y_test):
    """
    Train centralized model (baseline comparison)
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        X_test, y_test: Test data
        
    Returns:
        Model and metrics
    """
    logger.info("\n" + "="*60)
    logger.info("TRAINING CENTRALIZED MODEL (BASELINE)")
    logger.info("="*60)
    
    # Create model
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    logger.info(f"Model parameters: {ModelUtils.count_parameters(model):,}")
    
    # Create trainer
    trainer = Trainer(model)
    
    # Train
    logger.info("Starting training...")
    history = trainer.train(
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        num_epochs=10,
        verbose=True
    )
    
    # Evaluate on test set
    test_metrics = trainer.calculate_metrics(X_test, y_test)
    
    logger.info("\n📊 CENTRALIZED MODEL RESULTS:")
    logger.info(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {test_metrics['precision']:.4f}")
    logger.info(f"  Recall:    {test_metrics['recall']:.4f}")
    logger.info(f"  F1-Score:  {test_metrics['f1_score']:.4f}")
    logger.info(f"  AUC-ROC:   {test_metrics['auc_roc']:.4f}")
    
    # Save model
    ModelUtils.save_model(model, 'results/models/centralized_model.pth')
    
    return model, test_metrics, history


def train_federated_without_privacy(bank_datasets, X_val, y_val, X_test, y_test, num_rounds=10):
    """
    Train federated model WITHOUT differential privacy
    
    Args:
        bank_datasets: List of (X, y) tuples per bank
        X_val, y_val: Validation data
        X_test, y_test: Test data
        num_rounds: Number of federated rounds
        
    Returns:
        Final model and metrics
    """
    logger.info("\n" + "="*60)
    logger.info("TRAINING FEDERATED MODEL (NO PRIVACY)")
    logger.info("="*60)
    
    num_banks = len(bank_datasets)
    logger.info(f"Number of banks: {num_banks}")
    
    # Create client function
    def client_fn(cid: str):
        bank_id = int(cid)
        X_bank, y_bank = bank_datasets[bank_id]
        
        # Split bank data into train/val
        split_idx = int(0.8 * len(X_bank))
        X_bank_train, X_bank_val = X_bank[:split_idx], X_bank[split_idx:]
        y_bank_train, y_bank_val = y_bank[:split_idx], y_bank[split_idx:]
        
        model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
        
        from federated.client import BankClient
        return BankClient(
            bank_id=bank_id,
            X_train=X_bank_train,
            y_train=y_bank_train,
            X_val=X_bank_val,
            y_val=y_bank_val,
            model=model
        ).to_client()
    
    # Create server
    server = FederatedServer(
        strategy_type='fedavg',
        use_privacy=False
    )
    
    # Start training
    logger.info(f"Starting federated training for {num_rounds} rounds...")
    history = server.start(
        client_fn=client_fn,
        num_rounds=num_rounds,
        num_clients=num_banks
    )
    
    # Evaluate final model (simulate by training on all data)
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model)
    
    # Combine all bank data for final evaluation
    X_all = np.vstack([X for X, y in bank_datasets])
    y_all = np.hstack([y for X, y in bank_datasets])
    
    trainer.train(
        train_data=(X_all, y_all),
        val_data=(X_val, y_val),
        num_epochs=10,
        verbose=False
    )
    
    test_metrics = trainer.calculate_metrics(X_test, y_test)
    
    logger.info("\n📊 FEDERATED MODEL RESULTS (No Privacy):")
    logger.info(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {test_metrics['precision']:.4f}")
    logger.info(f"  Recall:    {test_metrics['recall']:.4f}")
    logger.info(f"  F1-Score:  {test_metrics['f1_score']:.4f}")
    logger.info(f"  AUC-ROC:   {test_metrics['auc_roc']:.4f}")
    
    torch.save(model.state_dict(), "results/models/federated_model.pth")
    logger.info("💾 Federated model saved successfully!")
    
    return model, test_metrics, history


def train_federated_with_privacy(bank_datasets, X_val, y_val, X_test, y_test, 
                                 epsilon=1.0, num_rounds=20):
    """
    Train federated model WITH differential privacy
    
    Args:
        bank_datasets: List of (X, y) tuples per bank
        X_val, y_val: Validation data
        X_test, y_test: Test data
        epsilon: Privacy budget
        num_rounds: Number of federated rounds
        
    Returns:
        Final model and metrics
    """
    logger.info("\n" + "="*60)
    logger.info(f"TRAINING FEDERATED MODEL WITH PRIVACY (ε={epsilon})")
    logger.info("="*60)
    
    num_banks = len(bank_datasets)
    logger.info(f"Number of banks: {num_banks}")
    logger.info(f"Privacy budget (ε): {epsilon}")
    logger.info(f"Privacy parameter (δ): {DP_CONFIG['delta']}")
    
    privacy_config = {
        'epsilon': epsilon,
        'delta': DP_CONFIG['delta'],
        'max_grad_norm': DP_CONFIG['max_grad_norm']
    }
    
    # Create client function
    def client_fn(cid: str):
        bank_id = int(cid)
        X_bank, y_bank = bank_datasets[bank_id]
        
        # Split bank data
        split_idx = int(0.8 * len(X_bank))
        X_bank_train, X_bank_val = X_bank[:split_idx], X_bank[split_idx:]
        y_bank_train, y_bank_val = y_bank[:split_idx], y_bank[split_idx:]
        
        model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
        
        return PrivateBankClient(
            bank_id=bank_id,
            X_train=X_bank_train,
            y_train=y_bank_train,
            X_val=X_bank_val,
            y_val=y_bank_val,
            model=model,
            privacy_config=privacy_config
        ).to_client()
    
    # Create private server
    server = FederatedServer(
        strategy_type='fedavg',
        use_privacy=True,
        privacy_config=privacy_config
    )
    
    # Start training
    logger.info(f"Starting private federated training for {num_rounds} rounds...")
    history = server.start(
        client_fn=client_fn,
        num_rounds=num_rounds,
        num_clients=num_banks
    )
    
    # Evaluate final model
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model)
    
    X_all = np.vstack([X for X, y in bank_datasets])
    y_all = np.hstack([y for X, y in bank_datasets])
    
    trainer.train(
        train_data=(X_all, y_all),
        val_data=(X_val, y_val),
        num_epochs=10,
        verbose=False
    )
    
    test_metrics = trainer.calculate_metrics(X_test, y_test)
    test_metrics['privacy_epsilon'] = epsilon
    
    logger.info("\n📊 PRIVATE FEDERATED MODEL RESULTS:")
    logger.info(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {test_metrics['precision']:.4f}")
    logger.info(f"  Recall:    {test_metrics['recall']:.4f}")
    logger.info(f"  F1-Score:  {test_metrics['f1_score']:.4f}")
    logger.info(f"  AUC-ROC:   {test_metrics['auc_roc']:.4f}")
    logger.info(f"  Privacy (ε): {epsilon}")
    
    return model, test_metrics, history


def main(args):
    """Main execution function"""
    
    logger.info("\n" + "="*60)
    logger.info("🏦 PRIVACY-PRESERVING FRAUD INTELLIGENCE NETWORK")
    logger.info("="*60)
    
    # Setup
    setup_directories()
    
    # 1. Load and prepare data
    logger.info("\n📥 Loading and preparing data...")
    handler = DataHandler(DATA_CONFIG)
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    
    if DATA_CONFIG['balance_data']:
        X, y = handler.balance_data(X, y)
    
    # Split data
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    X_val, y_val = splits['val']
    X_test, y_test = splits['test']
    
    logger.info(f"✅ Data loaded: {len(X_train)} train, {len(X_val)} val, {len(X_test)} test")
    
    # 2. Distribute to banks
    if args.distribution == 'iid':
        logger.info(f"\n🏦 Distributing data to {args.num_banks} banks (IID)...")
        bank_datasets = handler.distribute_to_banks(X_train, y_train, num_banks=args.num_banks)
    else:
        logger.info(f"\n🏦 Distributing data to {args.num_banks} banks (Non-IID)...")
        bank_datasets = handler.distribute_non_iid(X_train, y_train, 
                                                   num_banks=args.num_banks, 
                                                   alpha=0.5)
    
    stats = handler.get_data_statistics(bank_datasets)
    
    # 3. Run experiments based on mode
    results = {}
    
    if args.mode == 'centralized':
        model, metrics, history = train_centralized_baseline(
            X_train, y_train, X_val, y_val, X_test, y_test
        )
        results['centralized'] = metrics
    
    elif args.mode == 'federated':
        model, metrics, history = train_federated_without_privacy(
            bank_datasets, X_val, y_val, X_test, y_test, 
            num_rounds=args.num_rounds
        )
        results['federated'] = metrics
    
    elif args.mode == 'federated_dp':
        model, metrics, history = train_federated_with_privacy(
            bank_datasets, X_val, y_val, X_test, y_test, 
            epsilon=args.epsilon, num_rounds=args.num_rounds
        )
        results['federated_dp'] = metrics
    
    elif args.mode == 'all':
        # Run all experiments
        logger.info("\n🔬 Running complete experimental suite...")
        
        # Centralized
        _, metrics_cent, _ = train_centralized_baseline(
            X_train, y_train, X_val, y_val, X_test, y_test
        )
        results['centralized'] = metrics_cent
        
        # Federated
        _, metrics_fed, _ = train_federated_without_privacy(
            bank_datasets, X_val, y_val, X_test, y_test,
            num_rounds=args.num_rounds
        )
        results['federated'] = metrics_fed
        
        # Federated with DP
        for eps in [10.0, 1.0, 0.5]:
            _, metrics_dp, _ = train_federated_with_privacy(
                bank_datasets, X_val, y_val, X_test, y_test,
                epsilon=eps, num_rounds=args.num_rounds
            )
            results[f'federated_dp_eps{eps}'] = metrics_dp
    
    # 4. Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 FINAL RESULTS SUMMARY")
    logger.info("="*60)
    
    for name, metrics in results.items():
        logger.info(f"\n{name.upper()}:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1-Score:  {metrics['f1_score']:.4f}")
        if 'privacy_epsilon' in metrics:
            logger.info(f"  Privacy ε: {metrics['privacy_epsilon']}")
    
    logger.info("\n✅ Execution complete!")
    logger.info("📁 Results saved to results/ directory")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Privacy-Preserving Cross-Bank Fraud Detection'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['centralized', 'federated', 'federated_dp', 'all'],
        default='all',
        help='Training mode'
    )
    
    parser.add_argument(
        '--num_banks',
        type=int,
        default=5,
        help='Number of banks to simulate'
    )
    
    parser.add_argument(
        '--num_rounds',
        type=int,
        default=10,
        help='Number of federated learning rounds'
    )
    
    parser.add_argument(
        '--epsilon',
        type=float,
        default=1.0,
        help='Privacy budget (epsilon) for differential privacy'
    )
    
    parser.add_argument(
        '--distribution',
        type=str,
        choices=['iid', 'non-iid'],
        default='iid',
        help='Data distribution across banks'
    )
    
    args = parser.parse_args()
    
    # Run main
    results = main(args)
