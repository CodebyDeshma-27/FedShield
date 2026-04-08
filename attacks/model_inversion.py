"""
Model Inversion Attack
Tries to reconstruct training data from a trained model
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class ModelInversionAttack:
    """
    Attempts to reconstruct training data by exploiting model predictions
    
    HOW IT WORKS (Simple Explanation):
    1. Start with random noise
    2. Pass through model
    3. If model says "fraud", adjust noise to look MORE like fraud
    4. Repeat 1000 times
    5. Final noise should look like original training data
    """
    
    def __init__(self, model, input_dim=30):
        """
        Initialize attack
        
        Args:
            model: Trained neural network
            input_dim: Number of input features
        """
        self.model = model
        self.model.eval()  # Set to evaluation mode
        self.input_dim = input_dim
    
    def attack(self, target_class=1, num_iterations=1000, learning_rate=0.1):
        """
        Perform model inversion attack
        
        Args:
            target_class: Class to reconstruct (0=normal, 1=fraud)
            num_iterations: How many times to optimize
            learning_rate: How fast to learn
            
        Returns:
            Reconstructed data, attack loss history
        """
        print(f"\n[TARGET] Starting Model Inversion Attack...")
        print(f"   Target class: {target_class}")
        print(f"   Iterations: {num_iterations}")
        
        # Start with random noise
        reconstructed = torch.randn(1, self.input_dim, requires_grad=True)
        optimizer = torch.optim.Adam([reconstructed], lr=learning_rate)
        
        loss_history = []
        
        # Optimize to reconstruct data
        for i in range(num_iterations):
            optimizer.zero_grad()
            
            # Pass through model
            output = self.model(reconstructed)
            
            # Loss: We want to MAXIMIZE probability of target class
            # (Negative because we minimize in PyTorch)
            loss = -output[0, target_class]
            
            # Optional: Add regularization to make reconstruction realistic
            # This prevents reconstructed data from being too extreme
            reg_loss = 0.001 * torch.sum(reconstructed ** 2)
            total_loss = loss + reg_loss
            
            # Backpropagate and update
            total_loss.backward()
            optimizer.step()
            
            loss_history.append(total_loss.item())
            
            if (i + 1) % 200 == 0:
                print(f"   Iteration {i+1}/{num_iterations}, Loss: {total_loss.item():.4f}")
        
        print(f"[OK] Attack complete!")
        
        return reconstructed.detach().numpy()[0], loss_history
    
    def evaluate_attack(self, reconstructed, real_sample):
        """
        Measure how successful the attack was
        
        Args:
            reconstructed: Data reconstructed by attack
            real_sample: Real training data sample
            
        Returns:
            Dictionary with metrics
        """
        # Mean Squared Error (lower = better reconstruction = worse for privacy)
        mse = np.mean((reconstructed - real_sample) ** 2)
        
        # Cosine similarity (higher = more similar = worse for privacy)
        dot_product = np.dot(reconstructed, real_sample)
        norm_recon = np.linalg.norm(reconstructed)
        norm_real = np.linalg.norm(real_sample)
        cosine_sim = dot_product / (norm_recon * norm_real)
        
        # Correlation
        correlation = np.corrcoef(reconstructed, real_sample)[0, 1]
        
        return {
            'mse': mse,
            'cosine_similarity': cosine_sim,
            'correlation': correlation
        }
    
    def visualize_attack(self, reconstructed, real_sample, save_path=None):
        """
        Visualize the attack results
        
        Args:
            reconstructed: Reconstructed data
            real_sample: Real data
            save_path: Where to save plot
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        # Plot 1: Real data
        axes[0].plot(real_sample, 'b-', linewidth=2)
        axes[0].set_title('Real Training Data', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Feature Index')
        axes[0].set_ylabel('Value')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Reconstructed data
        axes[1].plot(reconstructed, 'r-', linewidth=2)
        axes[1].set_title('Reconstructed Data (Attack)', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Feature Index')
        axes[1].set_ylabel('Value')
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Comparison
        axes[2].plot(real_sample, 'b-', linewidth=2, label='Real', alpha=0.7)
        axes[2].plot(reconstructed, 'r--', linewidth=2, label='Reconstructed', alpha=0.7)
        axes[2].set_title('Comparison', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('Feature Index')
        axes[2].set_ylabel('Value')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Visualization saved to {save_path}")
        
        return fig


# Example usage
if __name__ == "__main__":
    print("""
    MODEL INVERSION ATTACK
    =====================
    
    This attack tries to reconstruct training data from a trained model.
    
    Steps:
    1. Start with random noise
    2. Pass through model → get prediction
    3. Adjust noise to maximize fraud probability
    4. Repeat until noise looks like fraud transaction
    
    If MSE is LOW (< 0.5) → Attack SUCCEEDED (bad for privacy)
    If MSE is HIGH (> 1.0) → Attack FAILED (good for privacy)
    """)
