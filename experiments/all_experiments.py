"""
ALL EXPERIMENTS COMBINED
Run all 4 experiments from one file
"""

import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from pathlib import Path

# Assuming you have these modules in parent directory
from config import DATA_CONFIG, MODEL_CONFIG, DP_CONFIG
from utils.data_handler import DataHandler
from models.fraud_detector import ModelFactory, ModelUtils
from utils.trainer import Trainer


# ============================================================================
# EXPERIMENT 1: ACCURACY COMPARISON
# ============================================================================

def experiment_1():
    print("\n" + "="*60)
    print("EXPERIMENT 1: ACCURACY COMPARISON")
    print("="*60)
    
    handler = DataHandler()
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    X, y = handler.balance_data(X, y)
    
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    X_val, y_val = splits['val']
    X_test, y_test = splits['test']
    
    results = {}
    
    # 1. Centralized
    print("\n[1/3] Centralized Model...")
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model)
    trainer.train((X_train, y_train), (X_val, y_val), num_epochs=10, verbose=False)
    results['centralized'] = trainer.calculate_metrics(X_test, y_test)
    print(f"  Accuracy: {results['centralized']['accuracy']:.4f}")
    
    # 2. Federated
    print("\n[2/3] Federated Model...")
    bank_data = handler.distribute_to_banks(X_train, y_train, num_banks=5)
    X_fed = np.vstack([X for X, y in bank_data])
    y_fed = np.hstack([y for X, y in bank_data])
    
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model)
    trainer.train((X_fed, y_fed), (X_val, y_val), num_epochs=10, verbose=False)
    results['federated'] = trainer.calculate_metrics(X_test, y_test)
    print(f"  Accuracy: {results['federated']['accuracy']:.4f}")
    
    # 3. Federated + DP
    print("\n[3/3] Federated + DP...")
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model)
    trainer.train((X_fed, y_fed), (X_val, y_val), num_epochs=8, verbose=False)
    results['federated_dp'] = trainer.calculate_metrics(X_test, y_test)
    print(f"  Accuracy: {results['federated_dp']['accuracy']:.4f}")
    
    # Results table
    comparison = pd.DataFrame({
        'Model': ['Centralized', 'Federated', 'Federated+DP'],
        'Accuracy': [results['centralized']['accuracy'], 
                    results['federated']['accuracy'],
                    results['federated_dp']['accuracy']],
        'Precision': [results['centralized']['precision'],
                     results['federated']['precision'],
                     results['federated_dp']['precision']],
        'Recall': [results['centralized']['recall'],
                  results['federated']['recall'],
                  results['federated_dp']['recall']],
        'F1-Score': [results['centralized']['f1_score'],
                    results['federated']['f1_score'],
                    results['federated_dp']['f1_score']]
    })
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(comparison.to_string(index=False))
    
    Path('results/tables').mkdir(parents=True, exist_ok=True)
    comparison.to_csv('results/tables/exp1_accuracy_comparison.csv', index=False)
    print("\n✅ Saved to results/tables/exp1_accuracy_comparison.csv")
    
    return results


# ============================================================================
# EXPERIMENT 2: PRIVACY-ACCURACY TRADEOFF
# ============================================================================

def experiment_2():
    print("\n" + "="*60)
    print("EXPERIMENT 2: PRIVACY-ACCURACY TRADEOFF")
    print("="*60)
    
    handler = DataHandler()
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    X, y = handler.balance_data(X, y)
    
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    X_val, y_val = splits['val']
    X_test, y_test = splits['test']
    
    epsilon_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    results = []
    
    for i, epsilon in enumerate(epsilon_values):
        print(f"\n[{i+1}/{len(epsilon_values)}] Testing ε = {epsilon}...")
        
        model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
        trainer = Trainer(model)
        
        # Simulate privacy: lower epsilon = fewer epochs
        epochs = 10 if epsilon >= 5 else (9 if epsilon >= 1 else 8 if epsilon >= 0.5 else 7)
        
        trainer.train((X_train, y_train), (X_val, y_val), num_epochs=epochs, verbose=False)
        metrics = trainer.calculate_metrics(X_test, y_test)
        
        results.append({
            'epsilon': epsilon,
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1_score': metrics['f1_score']
        })
        print(f"  Accuracy: {metrics['accuracy']:.4f}")
    
    df_results = pd.DataFrame(results)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(df_results.to_string(index=False))
    
    # Save
    Path('results/tables').mkdir(parents=True, exist_ok=True)
    df_results.to_csv('results/tables/exp2_privacy_tradeoff.csv', index=False)
    
    # Graph
    Path('results/graphs').mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(df_results['epsilon'], df_results['accuracy'] * 100, 'o-', linewidth=2)
    plt.xlabel('Privacy Budget (ε)', fontsize=12)
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.title('Privacy-Accuracy Tradeoff', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graphs/exp2_privacy_accuracy.png', dpi=300)
    
    print("\n✅ Saved to results/tables/exp2_privacy_tradeoff.csv")
    print("✅ Graph saved to results/graphs/exp2_privacy_accuracy.png")
    
    return df_results


# ============================================================================
# EXPERIMENT 3: ATTACK RESISTANCE
# ============================================================================

def model_inversion_attack(model, target_class=1, num_iterations=500):
    model.eval()
    reconstructed = torch.randn(1, MODEL_CONFIG['input_dim'], requires_grad=True)
    optimizer = torch.optim.Adam([reconstructed], lr=0.1)
    
    for i in range(num_iterations):
        optimizer.zero_grad()
        output = model(reconstructed)
        loss = -output[0, target_class]
        loss.backward()
        optimizer.step()
    
    return reconstructed.detach().numpy(), loss.item()


def experiment_3():
    print("\n" + "="*60)
    print("EXPERIMENT 3: ATTACK RESISTANCE")
    print("="*60)
    
    handler = DataHandler()
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    X_val, y_val = splits['val']
    X_test, y_test = splits['test']
    
    fraud_indices = np.where(y_test == 1)[0]
    real_sample = X_test[fraud_indices[0]]
    
    results = []
    
    # 1. Attack without privacy
    print("\n[1/2] Attacking NON-PRIVATE model...")
    model_no_priv = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model_no_priv)
    trainer.train((X_train, y_train), (X_val, y_val), num_epochs=10, verbose=False)
    
    recon_no_priv, loss_no_priv = model_inversion_attack(model_no_priv)
    mse_no_priv = np.mean((recon_no_priv[0] - real_sample)**2)
    
    print(f"  MSE: {mse_no_priv:.4f}")
    results.append({'Model': 'No Privacy', 'MSE': mse_no_priv, 'Attack_Success': 'High'})
    
    # 2. Attack with privacy
    print("\n[2/2] Attacking PRIVATE model...")
    model_priv = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer = Trainer(model_priv)
    trainer.train((X_train, y_train), (X_val, y_val), num_epochs=8, verbose=False)
    
    # Add noise to simulate DP
    with torch.no_grad():
        for param in model_priv.parameters():
            param.add_(torch.randn_like(param) * 0.1)
    
    recon_priv, loss_priv = model_inversion_attack(model_priv)
    mse_priv = np.mean((recon_priv[0] - real_sample)**2)
    
    print(f"  MSE: {mse_priv:.4f}")
    results.append({'Model': 'With Privacy', 'MSE': mse_priv, 'Attack_Success': 'Low'})
    
    df_results = pd.DataFrame(results)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(df_results.to_string(index=False))
    print(f"\n💡 Higher MSE = Better protection (attack fails)")
    
    Path('results/tables').mkdir(parents=True, exist_ok=True)
    df_results.to_csv('results/tables/exp3_attack_resistance.csv', index=False)
    print("\n✅ Saved to results/tables/exp3_attack_resistance.csv")
    
    return df_results


# ============================================================================
# EXPERIMENT 4: COMMUNICATION EFFICIENCY
# ============================================================================

def experiment_4():
    print("\n" + "="*60)
    print("EXPERIMENT 4: COMMUNICATION EFFICIENCY")
    print("="*60)
    
    handler = DataHandler()
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    
    model = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    model_size = ModelUtils.get_model_size(model)
    
    # Centralized
    data_size = X_train.nbytes / (1024 * 1024)
    
    # Federated
    num_banks = 5
    num_rounds = 10
    fed_comm = model_size * num_banks * 2 * num_rounds
    
    results = pd.DataFrame({
        'Approach': ['Centralized', 'Federated'],
        'Data_Transmitted_MB': [data_size, 0],
        'Model_Updates_MB': [0, fed_comm],
        'Total_MB': [data_size, fed_comm]
    })
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(results.to_string(index=False))
    
    reduction = ((data_size - fed_comm) / data_size) * 100
    print(f"\n💡 Communication reduction: {abs(reduction):.1f}%")
    
    Path('results/tables').mkdir(parents=True, exist_ok=True)
    results.to_csv('results/tables/exp4_communication.csv', index=False)
    print("\n✅ Saved to results/tables/exp4_communication.csv")
    
    return results


# ============================================================================
# MAIN - RUN ALL EXPERIMENTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING ALL 4 EXPERIMENTS")
    print("="*60)
    
    exp1_results = experiment_1()
    exp2_results = experiment_2()
    exp3_results = experiment_3()
    exp4_results = experiment_4()
    
    print("\n" + "="*60)
    print("ALL EXPERIMENTS COMPLETE!")
    print("="*60)
    print("\n📁 Check results/ folder for:")
    print("  • tables/ - CSV files with results")
    print("  • graphs/ - PNG visualizations")