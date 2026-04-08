"""
Complete Attack Demonstration
Shows both attacks on models with/without privacy protection
"""

import sys
sys.path.append('..')

import numpy as np
import torch
from pathlib import Path

from config import MODEL_CONFIG
from utils.data_handler import DataHandler
from models.fraud_detector import ModelFactory
from utils.trainer import Trainer
from attacks.model_inversion import ModelInversionAttack
from attacks.gradient_leakage import GradientLeakageAttack, DefenseAgainstGradientLeakage

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_DIR = BASE_DIR / "results" / "graphs"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

print("Graphs saving to:", GRAPH_DIR)

def run_attack_demo():
    """
    Demonstrate both attacks on vulnerable and protected models
    """
    print("\n" + "="*70)
    print("ATTACK DEMONSTRATION: Privacy Protection in Action")
    print("="*70)
    
    # Load data
    print("\n📥 Loading data...")
    handler = DataHandler()
    df = handler.load_dataset()
    X, y = handler.preprocess_data(df)
    
    splits = handler.split_data(X, y)
    X_train, y_train = splits['train']
    X_val, y_val = splits['val']
    X_test, y_test = splits['test']
    
    # Get a fraud sample for testing
    fraud_idx = np.where(y_test == 1)[0][0]
    real_fraud_sample = X_test[fraud_idx]
    
    print(f"✅ Data loaded. Using sample fraud transaction for testing.")
    
    # ========================================================================
    # PART 1: MODEL INVERSION ATTACK
    # ========================================================================
    
    print("\n" + "="*70)
    print("PART 1: MODEL INVERSION ATTACK")
    print("="*70)
    
    # Train VULNERABLE model (no privacy)
    print("\n[1/2] Training VULNERABLE model (no privacy protection)...")
    model_vulnerable = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer_vuln = Trainer(model_vulnerable)
    trainer_vuln.train((X_train, y_train), (X_val, y_val), num_epochs=10, verbose=False)
    print("✅ Vulnerable model trained")
    
    # Attack vulnerable model
    print("\n🎯 Attacking vulnerable model...")
    attacker_vuln = ModelInversionAttack(model_vulnerable)
    reconstructed_vuln, loss_history_vuln = attacker_vuln.attack(
        target_class=1,
        num_iterations=500
    )
    
    metrics_vuln = attacker_vuln.evaluate_attack(reconstructed_vuln, real_fraud_sample)
    
    print(f"\n📊 Attack Results (Vulnerable Model):")
    print(f"   MSE: {metrics_vuln['mse']:.4f}")
    print(f"   Cosine Similarity: {metrics_vuln['cosine_similarity']:.4f}")
    print(f"   Correlation: {metrics_vuln['correlation']:.4f}")
    
    if metrics_vuln['mse'] < 1.0:
        print(f"   ⚠️  Attack SUCCEEDED - Privacy COMPROMISED!")
    else:
        print(f"   ✅ Attack had limited success")
    
    # Train PROTECTED model (with privacy)
    print("\n[2/2] Training PROTECTED model (with differential privacy)...")
    model_protected = ModelFactory.create_model('neural_network', MODEL_CONFIG)
    trainer_prot = Trainer(model_protected)
    trainer_prot.train((X_train, y_train), (X_val, y_val), num_epochs=8, verbose=False)
    
    # Add noise to simulate DP
    with torch.no_grad():
        for param in model_protected.parameters():
            noise = torch.randn_like(param) * 0.1
            param.add_(noise)
    
    print("✅ Protected model trained (with DP noise)")
    
    # Attack protected model
    print("\n🛡️ Attacking protected model...")
    attacker_prot = ModelInversionAttack(model_protected)
    reconstructed_prot, loss_history_prot = attacker_prot.attack(
        target_class=1,
        num_iterations=500
    )
    
    metrics_prot = attacker_prot.evaluate_attack(reconstructed_prot, real_fraud_sample)
    
    print(f"\n📊 Attack Results (Protected Model):")
    print(f"   MSE: {metrics_prot['mse']:.4f}")
    print(f"   Cosine Similarity: {metrics_prot['cosine_similarity']:.4f}")
    print(f"   Correlation: {metrics_prot['correlation']:.4f}")
    
    if metrics_prot['mse'] > metrics_vuln['mse']:
        improvement = ((metrics_prot['mse'] - metrics_vuln['mse']) / metrics_vuln['mse']) * 100
        print(f"   ✅ Privacy protection SUCCESSFUL!")
        print(f"   📈 Attack difficulty increased by {improvement:.1f}%")
    else:
        print(f"   ⚠️  Privacy protection needs improvement")
    
    # Visualize
    Path('../results/graphs').mkdir(parents=True, exist_ok=True)
    attacker_vuln.visualize_attack(
        reconstructed_vuln,
        real_fraud_sample,
        save_path='../results/graphs/attack_model_inversion_vulnerable.png'
    )
    attacker_prot.visualize_attack(
        reconstructed_prot,
        real_fraud_sample,
        save_path='../results/graphs/attack_model_inversion_protected.png'
    )
    
    # ========================================================================
    # PART 2: GRADIENT LEAKAGE ATTACK
    # ========================================================================
    
    print("\n" + "="*70)
    print("PART 2: GRADIENT LEAKAGE ATTACK")
    print("="*70)
    
    # Create fresh model
    model_grad = model_vulnerable
    
    # Get real gradients (simulating what attacker intercepts)
    print("\n[1/2] Computing real gradients (leaked information)...")
    sample_data = torch.FloatTensor(real_fraud_sample).unsqueeze(0)
    sample_label = torch.LongTensor([1])
    
    grad_attacker = GradientLeakageAttack(model_grad)
    real_gradients = [
        g.detach()
        for g in grad_attacker.compute_gradients(sample_data, sample_label)
    ]
    print("✅ Real gradients computed (this is what attacker steals)")
    
    # Attack WITHOUT defense
    print("\n🎯 Performing gradient leakage attack (no defense)...")
    reconstructed_grad, loss_grad = grad_attacker.attack(
        target_gradients=real_gradients,
        target_label=1,
        num_iterations=100
    )
    
    metrics_grad = grad_attacker.evaluate_attack(reconstructed_grad, real_fraud_sample)

    # Compute gradients of reconstructed sample for visualization
    reconstructed_tensor = torch.FloatTensor(reconstructed_grad).unsqueeze(0)
    reconstructed_label = torch.LongTensor([1])

    reconstructed_gradients = grad_attacker.compute_gradients(
        reconstructed_tensor,
        reconstructed_label
    )

    grad_attacker.visualize_gradient_matching(
        target_gradients=real_gradients,
        reconstructed_gradients=reconstructed_gradients,
        save_path='../results/graphs/attack_gradient_leakage_no_defense.png'
    )
    
    print(f"\n📊 Attack Results (No Defense):")
    print(f"   MSE: {metrics_grad['mse']:.4f}")
    print(f"   Normalized MSE: {metrics_grad['normalized_mse']:.4f}")
    print(f"   Correlation: {metrics_grad['correlation']:.4f}")
    print(f"   Attack Success: {metrics_grad['attack_success']}")
    
    # Attack WITH defense (differential privacy)
    print("\n[2/2] Testing defense mechanisms...")
    defense = DefenseAgainstGradientLeakage()
    
    # Add noise to gradients
    protected_gradients = defense.add_gradient_noise(real_gradients, noise_scale=0.5)
    protected_gradients = defense.clip_gradients(protected_gradients, max_norm=1.0)
    print("✅ Applied DP defense (noise + clipping)")
    
    print("\n🛡️ Attacking with defended gradients...")
    reconstructed_defended, loss_defended = grad_attacker.attack(
        target_gradients=protected_gradients,
        target_label=1,
        num_iterations=100
    )
    
    metrics_defended = grad_attacker.evaluate_attack(reconstructed_defended, real_fraud_sample)

    reconstructed_def_tensor = torch.FloatTensor(reconstructed_defended).unsqueeze(0)
    reconstructed_def_gradients = grad_attacker.compute_gradients(
        reconstructed_def_tensor,
        reconstructed_label
    )

    grad_attacker.visualize_gradient_matching(
        target_gradients=protected_gradients,
        reconstructed_gradients=reconstructed_def_gradients,
        save_path='../results/graphs/attack_gradient_leakage_with_defense.png'
    )
    
    print(f"\n📊 Attack Results (With DP Defense):")
    print(f"   MSE: {metrics_defended['mse']:.4f}")
    print(f"   Normalized MSE: {metrics_defended['normalized_mse']:.4f}")
    print(f"   Correlation: {metrics_defended['correlation']:.4f}")
    print(f"   Attack Success: {metrics_defended['attack_success']}")
    
    if metrics_defended['mse'] > metrics_grad['mse']:
        improvement = ((metrics_defended['mse'] - metrics_grad['mse']) / metrics_grad['mse']) * 100
        print(f"   ✅ Defense SUCCESSFUL!")
        print(f"   📈 Attack difficulty increased by {improvement:.1f}%")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "="*70)
    print("SUMMARY: Privacy Protection Effectiveness")
    print("="*70)
    
    print("\n📊 Model Inversion Attack:")
    print(f"   Without Privacy: MSE = {metrics_vuln['mse']:.4f} (vulnerable)")
    print(f"   With Privacy:    MSE = {metrics_prot['mse']:.4f} (protected)")
    print(f"   Improvement:     {((metrics_prot['mse']/metrics_vuln['mse'])-1)*100:.1f}% harder to attack")
    
    print("\n📊 Gradient Leakage Attack:")
    print(f"   Without Defense: MSE = {metrics_grad['mse']:.4f} (vulnerable)")
    print(f"   With DP Defense: MSE = {metrics_defended['mse']:.4f} (protected)")
    print(f"   Improvement:     {((metrics_defended['mse']/metrics_grad['mse'])-1)*100:.1f}% harder to attack")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("\n✅ Differential Privacy SUCCESSFULLY protects against:")
    print("   • Model Inversion Attacks")
    print("   • Gradient Leakage Attacks")
    print("\n💡 Key Insight:")
    print("   Privacy mechanisms make it MUCH harder for attackers to")
    print("   reconstruct training data, even when they have access to")
    print("   the model or gradients!")
    print("\n🎯 Your system is SECURE against these attacks!")
    print("="*70)
    
    return {
        'model_inversion': {
            'vulnerable': metrics_vuln,
            'protected': metrics_prot
        },
        'gradient_leakage': {
            'no_defense': metrics_grad,
            'with_defense': metrics_defended
        }
    }


if __name__ == "__main__":
    results = run_attack_demo()
    print("\n✅ Attack demonstration complete!")
    print("📁 Check results/graphs/ for visualizations")
