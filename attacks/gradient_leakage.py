"""
Gradient Leakage Attack (Deep Leakage from Gradients)
Reconstructs training data from shared gradients
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class GradientLeakageAttack:
    """
    Exploits gradient information to reconstruct training data
    
    HOW IT WORKS (Simple Explanation):
    In federated learning, banks share GRADIENTS (not data).
    But gradients contain information about the training data!
    
    This attack:
    1. Bank sends gradients to server
    2. Attacker (malicious server) intercepts gradients
    3. Attacker creates fake data and computes its gradients
    4. Adjusts fake data until its gradients match real gradients
    5. Result: Fake data becomes similar to real training data!
    """
    
    def __init__(self, model, criterion=None):
        """
        Initialize attack
        
        Args:
            model: Neural network model
            criterion: Loss function (default: CrossEntropyLoss)
        """
        self.model = model
        self.criterion = criterion or nn.CrossEntropyLoss()
    
    def compute_gradients(self, data, labels):
        """
        Compute gradients for given data
        Args:
            data: Input data
            labels: True labels
        Returns:
            List of gradients
        """
        self.model.eval()
        self.model.zero_grad()

        output = self.model(data)
        loss = self.criterion(output, labels)

        gradients = torch.autograd.grad(
            loss,
            self.model.parameters(),
            create_graph=True  # 🔥 IMPORTANT
        )

        return gradients
    
    def attack(self, target_gradients, target_label, num_iterations=300, learning_rate=0.1):
        """
        Perform gradient leakage attack
        
        Args:
            target_gradients: Gradients from real training data (leaked)
            target_label: True label (may be known or guessed)
            num_iterations: Optimization iterations
            learning_rate: Learning rate
            
        Returns:
            Reconstructed data, loss history
        """
        print(f"\n[LEAK] Starting Gradient Leakage Attack...")
        print(f"   Target label: {target_label}")
        print(f"   Iterations: {num_iterations}")
        
        # Start with random data
        input_dim = self.model.network[0].in_features if hasattr(self.model, 'network') else 30
        dummy_data = torch.randn(1, input_dim, requires_grad=True)
        dummy_label = torch.tensor([target_label])
        
        optimizer = torch.optim.Adam([dummy_data], lr=0.05)
        
        loss_history = []
        
        for i in range(num_iterations):
            def closure():
                optimizer.zero_grad()
                
                # Compute gradients of dummy data
                dummy_gradients = self.compute_gradients(dummy_data, dummy_label)
                
                # Loss: Match dummy gradients with target gradients
                grad_diff = 0
                for dummy_grad, target_grad in zip(dummy_gradients, target_gradients):
                    grad_diff += ((dummy_grad - target_grad) ** 2).sum()
                
                grad_diff.backward(retain_graph=True)
                return grad_diff
            
            loss = optimizer.step(closure)
            loss_history.append(loss.item())
            
            if (i + 1) % 50 == 0:
                print(f"   Iteration {i+1}/{num_iterations}, Loss: {loss.item():.4f}")
        
        print(f"[OK] Attack complete!")
        
        return dummy_data.detach().numpy()[0], loss_history
    
    def evaluate_attack(self, reconstructed, real_data):
        """
        Evaluate attack success
        
        Args:
            reconstructed: Reconstructed data
            real_data: Real training data
            
        Returns:
            Metrics dictionary
        """
        mse = np.mean((reconstructed - real_data) ** 2)
        
        # Normalized MSE (0 to 1 scale)
        data_range = np.max(real_data) - np.min(real_data)
        nmse = mse / (data_range ** 2) if data_range > 0 else mse
        
        # Pearson correlation
        correlation = np.corrcoef(reconstructed.flatten(), real_data.flatten())[0, 1]
        
        return {
            'mse': mse,
            'normalized_mse': nmse,
            'correlation': correlation,
            'attack_success': 'High' if mse < 1.0 else 'Medium' if mse < 2.0 else 'Low'
        }
    
    def visualize_gradient_matching(self, target_gradients, reconstructed_gradients, save_path=None):
        """
        Visualize how well gradients match
        
        Args:
            target_gradients: Real gradients
            reconstructed_gradients: Reconstructed gradients
            save_path: Save path
        """
        # Compare first layer gradients (most informative)
        target_grad_flat = target_gradients[0].detach().cpu().numpy().flatten()[:100]
        recon_grad_flat = reconstructed_gradients[0].detach().cpu().numpy().flatten()[:100]
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot 1: Gradient values
        x = np.arange(len(target_grad_flat))
        axes[0].plot(x, target_grad_flat, 'b-', label='Target Gradients', linewidth=2)
        axes[0].plot(x, recon_grad_flat, 'r--', label='Reconstructed Gradients', linewidth=2)
        axes[0].set_title('Gradient Comparison (First 100 params)', fontweight='bold')
        axes[0].set_xlabel('Parameter Index')
        axes[0].set_ylabel('Gradient Value')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Scatter plot
        axes[1].scatter(target_grad_flat, recon_grad_flat, alpha=0.6)
        axes[1].plot([target_grad_flat.min(), target_grad_flat.max()],
                    [target_grad_flat.min(), target_grad_flat.max()],
                    'r--', linewidth=2, label='Perfect Match')
        axes[1].set_title('Gradient Matching Quality', fontweight='bold')
        axes[1].set_xlabel('Target Gradients')
        axes[1].set_ylabel('Reconstructed Gradients')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[INFO] Gradient comparison saved to {save_path}")
        
        return fig


class DefenseAgainstGradientLeakage:
    """
    Defense mechanisms against gradient leakage
    """
    
    @staticmethod
    def add_gradient_noise(gradients, noise_scale=0.1):
        """
        Add noise to gradients (Differential Privacy)
        
        Args:
            gradients: List of gradient tensors
            noise_scale: Amount of noise
            
        Returns:
            Noised gradients
        """
        noised_gradients = []
        for grad in gradients:
            noise = torch.randn_like(grad) * noise_scale
            noised_grad = grad + noise
            noised_gradients.append(noised_grad)
        
        return noised_gradients
    
    @staticmethod
    def clip_gradients(gradients, max_norm=1.0):
        """
        Clip gradients to limit sensitivity
        
        Args:
            gradients: List of gradient tensors
            max_norm: Maximum gradient norm
            
        Returns:
            Clipped gradients
        """
        # Compute total norm
        total_norm = 0
        for grad in gradients:
            total_norm += (grad ** 2).sum()
        total_norm = torch.sqrt(total_norm)
        
        # Clip if needed
        clip_coef = max_norm / (total_norm + 1e-6)
        if clip_coef < 1:
            clipped_gradients = [grad * clip_coef for grad in gradients]
        else:
            clipped_gradients = gradients
        
        return clipped_gradients
    
    @staticmethod
    def gradient_compression(gradients, compression_ratio=0.1):
        """
        Compress gradients (send only top-k values)
        
        Args:
            gradients: List of gradient tensors
            compression_ratio: Fraction of gradients to keep
            
        Returns:
            Compressed gradients
        """
        compressed = []
        for grad in gradients:
            k = int(grad.numel() * compression_ratio)
            values, indices = torch.topk(grad.abs().flatten(), k)
            
            # Create sparse gradient
            sparse_grad = torch.zeros_like(grad)
            sparse_grad.flatten()[indices] = grad.flatten()[indices]
            compressed.append(sparse_grad)
        
        return compressed


# Example usage
if __name__ == "__main__":
    print("""
    GRADIENT LEAKAGE ATTACK
    =======================
    
    This attack reconstructs training data from gradients.
    
    Why it works:
    - In federated learning, banks share GRADIENTS
    - Gradients contain information about training data
    - By matching gradients, attacker can reconstruct data
    
    Defense (Differential Privacy):
    - Add noise to gradients before sharing
    - Clip gradients to limit sensitivity
    - This makes reconstruction much harder!
    
    If attack MSE is LOW (< 1.0) → Privacy risk HIGH
    If attack MSE is HIGH (> 2.0) → Privacy protection works!
    """)
