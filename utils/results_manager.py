"""
Results Manager
Handles saving metrics, plots, and model results
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ResultsManager:
    """Manage saving and organizing results from federated learning"""
    
    def __init__(self, results_dir: str = "results"):
        """
        Initialize results manager
        
        Args:
            results_dir: Root directory to save results
        """
        self.results_dir = results_dir
        self.tables_dir = os.path.join(results_dir, "tables")
        self.graphs_dir = os.path.join(results_dir, "graphs")
        
        # Create directories
        os.makedirs(self.tables_dir, exist_ok=True)
        os.makedirs(self.graphs_dir, exist_ok=True)
    
    def _clean_nan_values(self, value):
        """Convert NaN values to None for JSON serialization"""
        if isinstance(value, float):
            if np.isnan(value) or np.isinf(value):
                return None
        elif isinstance(value, dict):
            return {k: self._clean_nan_values(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._clean_nan_values(v) for v in value]
        return value
        
    def save_round_metrics(self, round_metrics):
        """
        Save metrics from each round (handles both dict and list)
        
        Args:
            round_metrics: Dictionary or list of metrics per round
        """
        try:
            # Clean NaN values
            if isinstance(round_metrics, dict):
                round_metrics = {k: self._clean_nan_values(v) for k, v in round_metrics.items()}
            elif isinstance(round_metrics, list):
                round_metrics = [self._clean_nan_values(item) for item in round_metrics]
            
            metrics_path = os.path.join(self.results_dir, "round_metrics.json")
            with open(metrics_path, 'w') as f:
                json.dump(round_metrics, f, indent=2)
            logger.info(f"✅ Round metrics saved → {metrics_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save round metrics: {e}")
            
    def save_accuracy_plot(self, round_metrics):
        """
        Generate and save accuracy plot (handles both dict and list)
        
        Args:
            round_metrics: Dictionary or list of metrics per round
        """
        try:
            if not round_metrics:
                logger.warning("⚠️ No metrics to plot")
                return
            
            # Handle both dict and list formats
            if isinstance(round_metrics, dict):
                rounds = sorted([int(r) for r in round_metrics.keys()])
                accuracies = [round_metrics[str(r)].get('accuracy', 0) for r in rounds]
            elif isinstance(round_metrics, list):
                rounds = [item.get('round', idx) for idx, item in enumerate(round_metrics, 1)]
                accuracies = [item.get('accuracy', 0) for item in round_metrics]
                losses = [item.get('loss', 0) for item in round_metrics]
            else:
                logger.warning("⚠️ Unknown metrics format")
                return
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Plot 1: Accuracy
            ax1.plot(rounds, accuracies, marker='o', linewidth=2, markersize=8, color='#3b82f6')
            ax1.set_xlabel('Round', fontsize=12)
            ax1.set_ylabel('Accuracy', fontsize=12)
            ax1.set_title('Federated Learning - Accuracy Over Rounds', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim([0, 1.0])
            for i, acc in enumerate(accuracies):
                ax1.text(rounds[i], acc + 0.02, f'{acc:.3f}', ha='center', fontsize=9)
            
            # Plot 2: Loss (if available)
            if isinstance(round_metrics, list) and losses:
                # Filter out NaN values
                valid_rounds = []
                valid_losses = []
                for r, l in zip(rounds, losses):
                    if l is not None and not (isinstance(l, float) and (np.isnan(l) or np.isinf(l))):
                        valid_rounds.append(r)
                        valid_losses.append(l)
                
                if valid_losses:
                    ax2.plot(valid_rounds, valid_losses, marker='s', linewidth=2, markersize=8, color='#ef4444')
                    ax2.set_xlabel('Round', fontsize=12)
                    ax2.set_ylabel('Loss', fontsize=12)
                    ax2.set_title('Federated Learning - Loss Over Rounds', fontsize=14, fontweight='bold')
                    ax2.grid(True, alpha=0.3)
                    for r, l in zip(valid_rounds, valid_losses):
                        ax2.text(r, l + (max(valid_losses) * 0.02), f'{l:.2f}', ha='center', fontsize=9)
            
            plt.tight_layout()
            plot_path = os.path.join(self.graphs_dir, "federated_training_metrics.png")
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Training metrics plot saved → {plot_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save accuracy plot: {e}")
            import traceback
            traceback.print_exc()
    
    def save_model_comparison_plots(self, models_metrics: dict):
        """
        Generate comparison plots for all models
        
        Args:
            models_metrics: Dictionary with model names as keys and metrics dict as values
        """
        try:
            if not models_metrics:
                return
            
            # Extract metrics
            model_names = []
            accuracies = []
            precisions = []
            recalls = []
            f1_scores = []
            auc_rocs = []
            
            for model_name, metrics in models_metrics.items():
                model_names.append(model_name.replace('_', ' ').title())
                accuracies.append(metrics.get('accuracy', 0))
                precisions.append(metrics.get('precision', 0))
                recalls.append(metrics.get('recall', 0))
                f1_scores.append(metrics.get('f1_score', 0))
                auc_rocs.append(metrics.get('auc_roc', 0))
            
            # Create comparison figure
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
            
            # Accuracy
            axes[0, 0].bar(model_names, accuracies, color=colors[:len(model_names)], alpha=0.8, edgecolor='black')
            axes[0, 0].set_ylabel('Score', fontsize=11)
            axes[0, 0].set_title('Model Accuracy Comparison', fontsize=12, fontweight='bold')
            axes[0, 0].set_ylim([0, 1.0])
            axes[0, 0].grid(True, alpha=0.3, axis='y')
            for i, v in enumerate(accuracies):
                axes[0, 0].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=9)
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Precision
            axes[0, 1].bar(model_names, precisions, color=colors[:len(model_names)], alpha=0.8, edgecolor='black')
            axes[0, 1].set_ylabel('Score', fontsize=11)
            axes[0, 1].set_title('Model Precision Comparison', fontsize=12, fontweight='bold')
            axes[0, 1].set_ylim([0, 1.0])
            axes[0, 1].grid(True, alpha=0.3, axis='y')
            for i, v in enumerate(precisions):
                axes[0, 1].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=9)
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Recall
            axes[1, 0].bar(model_names, recalls, color=colors[:len(model_names)], alpha=0.8, edgecolor='black')
            axes[1, 0].set_ylabel('Score', fontsize=11)
            axes[1, 0].set_title('Model Recall Comparison', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylim([0, 1.0])
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            for i, v in enumerate(recalls):
                axes[1, 0].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=9)
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # F1 Score
            axes[1, 1].bar(model_names, f1_scores, color=colors[:len(model_names)], alpha=0.8, edgecolor='black')
            axes[1, 1].set_ylabel('Score', fontsize=11)
            axes[1, 1].set_title('Model F1-Score Comparison', fontsize=12, fontweight='bold')
            axes[1, 1].set_ylim([0, 1.0])
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            for i, v in enumerate(f1_scores):
                axes[1, 1].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=9)
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plot_path = os.path.join(self.graphs_dir, "model_comparison.png")
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Model comparison plot saved → {plot_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save model comparison plot: {e}")
    
    def save_metrics_csv(self, metrics: dict, filename: str = "federated_results.csv"):
        """
        Save metrics to CSV
        
        Args:
            metrics: Dictionary of metrics
            filename: Output CSV filename
        """
        try:
            df = pd.DataFrame([metrics])
            csv_path = os.path.join(self.tables_dir, filename)
            df.to_csv(csv_path, index=False)
            logger.info(f"✅ Metrics saved → {csv_path}")
            return csv_path
        except Exception as e:
            logger.error(f"❌ Failed to save metrics CSV: {e}")
            return None
    
    def save_all_models_csv(self, models_metrics: dict):
        """
        Save metrics for all models to separate CSV files
        
        Args:
            models_metrics: Dictionary with model names as keys and metrics dict as values
        """
        try:
            for model_name, metrics in models_metrics.items():
                filename = f"{model_name}_results.csv"
                self.save_metrics_csv(metrics, filename)
        except Exception as e:
            logger.error(f"❌ Failed to save models CSV: {e}")