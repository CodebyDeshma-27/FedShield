"""
Generate all graphs from experiment results CSVs
Run from project root: python -m experiments.generate_graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
TABLES_DIR = BASE_DIR / "results" / "tables"
GRAPHS_DIR = BASE_DIR / "results" / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    'figure.dpi':      150,
    'font.size':       11,
    'axes.titlesize':  13,
    'axes.labelsize':  11,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
})

COLORS = {
    'centralized': '#2196F3',
    'federated':   '#4CAF50',
    'dp':          '#FF9800',
    'attack':      '#F44336',
    'safe':        '#4CAF50',
}

# ── Graph 1: Model Accuracy Comparison ───────────────────────────────────────
def graph1_accuracy():
    df = pd.read_csv(TABLES_DIR / "exp1_accuracy_comparison.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    x      = np.arange(len(df))
    width  = 0.2
    colors = [COLORS['centralized'], COLORS['federated'], COLORS['dp']]
    metrics = ['Accuracy', 'Precision', 'F1-Score']

    for i, (metric, col) in enumerate(zip(metrics, colors)):
        bars = ax.bar(x + i * width, df[metric] * 100, width,
                      label=metric, color=col, alpha=0.85)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f'{bar.get_height():.2f}%',
                    ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x + width)
    ax.set_xticklabels(df['Model'])
    ax.set_ylim(99.6, 100.1)
    ax.set_ylabel('Score (%)')
    ax.set_title('Experiment 1: Model Accuracy Comparison\n(Centralized vs Federated vs Federated+DP)')
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.2f}%'))

    plt.tight_layout()
    out = GRAPHS_DIR / "exp1_accuracy_comparison.png"
    plt.savefig(out)
    plt.close()
    print(f"  Saved: {out.name}")


# ── Graph 2: Privacy-Accuracy Tradeoff ───────────────────────────────────────
def graph2_privacy_tradeoff():
    df = pd.read_csv(TABLES_DIR / "exp2_privacy_tradeoff.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df['epsilon'], df['accuracy'] * 100,
            marker='o', color=COLORS['dp'], linewidth=2.5,
            markersize=8, label='Accuracy')
    ax.fill_between(df['epsilon'], df['accuracy'] * 100,
                    df['accuracy'].min() * 100,
                    alpha=0.15, color=COLORS['dp'])

    # Annotate each point
    for _, row in df.iterrows():
        ax.annotate(f"{row['accuracy']*100:.3f}%",
                    (row['epsilon'], row['accuracy'] * 100),
                    textcoords="offset points", xytext=(0, 10),
                    ha='center', fontsize=8)

    ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.6, label='ε=1.0 (chosen)')
    ax.set_xscale('log')
    ax.set_xlabel('Privacy Budget (ε)  —  lower = more private')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Experiment 2: Privacy-Accuracy Tradeoff\n(Lower ε = Stronger Privacy)')
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.2f}%'))

    plt.tight_layout()
    out = GRAPHS_DIR / "exp2_privacy_tradeoff.png"
    plt.savefig(out)
    plt.close()
    print(f"  Saved: {out.name}")


# ── Graph 3: Attack Resistance ────────────────────────────────────────────────
def graph3_attack_resistance():
    df = pd.read_csv(TABLES_DIR / "exp3_attack_resistance.csv")

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Left: MSE bar chart
    ax = axes[0]
    bar_colors = [COLORS['attack'], COLORS['safe']]
    bars = ax.bar(df['Model'], df['MSE'], color=bar_colors, alpha=0.85, width=0.5)
    for bar, val in zip(bars, df['MSE']):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 10,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel('Reconstruction MSE\n(higher = harder to attack)')
    ax.set_title('Attack Reconstruction MSE\n(Higher = Better Privacy)')
    improvement = (df['MSE'].iloc[0] - df['MSE'].iloc[1]) / df['MSE'].iloc[0] * 100
    ax.text(0.5, 0.95, f'DP reduces attack success by {improvement:.1f}%',
            transform=ax.transAxes, ha='center', va='top',
            fontsize=9, color='green',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    # Right: Attack success label
    ax2 = axes[1]
    success_map = {'High': 85, 'Low': 25}
    vals   = [success_map[s] for s in df['Attack_Success']]
    colors = [COLORS['attack'], COLORS['safe']]
    bars2  = ax2.bar(df['Model'], vals, color=colors, alpha=0.85, width=0.5)
    for bar, label in zip(bars2, df['Attack_Success']):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 2,
                 label, ha='center', va='bottom', fontweight='bold')

    ax2.set_ylabel('Attack Success Level')
    ax2.set_ylim(0, 100)
    ax2.set_title('Attack Success Rate\n(Lower = Better Privacy)')
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])

    plt.suptitle('Experiment 3: Privacy Attack Resistance', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = GRAPHS_DIR / "exp3_attack_resistance.png"
    plt.savefig(out)
    plt.close()
    print(f"  Saved: {out.name}")


# ── Graph 4: Communication Efficiency ────────────────────────────────────────
def graph4_communication():
    df = pd.read_csv(TABLES_DIR / "exp4_communication.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Left: Total MB bar chart
    ax = axes[0]
    colors = [COLORS['centralized'], COLORS['federated']]
    bars = ax.bar(df['Approach'], df['Total_MB'], color=colors, alpha=0.85, width=0.5)
    for bar, val in zip(bars, df['Total_MB']):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f'{val:.1f} MB', ha='center', va='bottom', fontweight='bold')

    reduction = (1 - df['Total_MB'].iloc[1] / df['Total_MB'].iloc[0]) * 100
    ax.set_ylabel('Data Transmitted (MB)')
    ax.set_title(f'Total Data Transmitted\n({reduction:.1f}% Reduction with Federated)')
    ax.text(0.5, 0.95, f'{reduction:.1f}% bandwidth saved',
            transform=ax.transAxes, ha='center', va='top',
            fontsize=10, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    # Right: Stacked breakdown
    ax2 = axes[1]
    x      = np.arange(len(df))
    width  = 0.5
    p1 = ax2.bar(x, df['Data_Transmitted_MB'], width,
                 label='Raw Data (MB)', color='#FF7043', alpha=0.85)
    p2 = ax2.bar(x, df['Model_Updates_MB'], width,
                 bottom=df['Data_Transmitted_MB'],
                 label='Model Updates (MB)', color='#42A5F5', alpha=0.85)

    ax2.set_xticks(x)
    ax2.set_xticklabels(df['Approach'])
    ax2.set_ylabel('Data (MB)')
    ax2.set_title('Data Breakdown\n(Raw Data vs Model Updates)')
    ax2.legend()

    plt.suptitle('Experiment 4: Communication Efficiency', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = GRAPHS_DIR / "exp4_communication.png"
    plt.savefig(out)
    plt.close()
    print(f"  Saved: {out.name}")


# ── Graph 5: Federated Learning Convergence ───────────────────────────────────
def graph5_convergence():
    df = pd.read_csv(TABLES_DIR / "federated_round_metrics.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Left: Loss curve
    ax = axes[0]
    ax.plot(df['round'], df['loss'], marker='o', color=COLORS['federated'],
            linewidth=2.5, markersize=6)
    ax.fill_between(df['round'], df['loss'], alpha=0.15, color=COLORS['federated'])
    ax.set_xlabel('Federated Round')
    ax.set_ylabel('Loss')
    ax.set_title('Training Loss per Round\n(5 Banks, FedAvg)')

    # Right: Accuracy curve
    ax2 = axes[1]
    ax2.plot(df['round'], df['accuracy'] * 100, marker='s',
             color=COLORS['centralized'], linewidth=2.5, markersize=6, label='Accuracy')
    ax2.plot(df['round'], df['f1_score'] * 100, marker='^',
             color=COLORS['dp'], linewidth=2.5, markersize=6,
             linestyle='--', label='F1-Score')
    ax2.set_xlabel('Federated Round')
    ax2.set_ylabel('Score (%)')
    ax2.set_title('Accuracy & F1 per Round\n(5 Banks, FedAvg)')
    ax2.legend()
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.2f}%'))

    plt.suptitle('Experiment 5: Federated Learning Convergence', fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = GRAPHS_DIR / "exp5_convergence.png"
    plt.savefig(out)
    plt.close()
    print(f"  Saved: {out.name}")


# ── Graph 6: Overall Summary Dashboard ───────────────────────────────────────
def graph6_summary_dashboard():
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle('Privacy-Preserving Fraud Detection — Results Summary',
                 fontsize=14, fontweight='bold', y=1.01)

    # Top-left: Accuracy comparison
    df1 = pd.read_csv(TABLES_DIR / "exp1_accuracy_comparison.csv")
    ax  = axes[0, 0]
    colors = [COLORS['centralized'], COLORS['federated'], COLORS['dp']]
    ax.bar(df1['Model'], df1['F1-Score'] * 100, color=colors, alpha=0.85)
    ax.set_ylim(99.7, 100.05)
    ax.set_ylabel('F1-Score (%)')
    ax.set_title('Model F1-Score Comparison')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.2f}%'))
    for i, val in enumerate(df1['F1-Score']):
        ax.text(i, val * 100 + 0.005, f'{val*100:.3f}%',
                ha='center', va='bottom', fontsize=8)

    # Top-right: Privacy tradeoff
    df2 = pd.read_csv(TABLES_DIR / "exp2_privacy_tradeoff.csv")
    ax2  = axes[0, 1]
    ax2.plot(df2['epsilon'], df2['accuracy'] * 100,
             marker='o', color=COLORS['dp'], linewidth=2)
    ax2.axvline(x=1.0, color='gray', linestyle='--', alpha=0.6)
    ax2.set_xscale('log')
    ax2.set_xlabel('ε (Privacy Budget)')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Privacy-Accuracy Tradeoff')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.2f}%'))

    # Bottom-left: Attack resistance
    df3    = pd.read_csv(TABLES_DIR / "exp3_attack_resistance.csv")
    ax3    = axes[1, 0]
    bcolors = [COLORS['attack'], COLORS['safe']]
    ax3.bar(df3['Model'], df3['MSE'], color=bcolors, alpha=0.85)
    ax3.set_ylabel('Reconstruction MSE')
    ax3.set_title('Attack Resistance (Higher = Safer)')

    # Bottom-right: Communication
    df4 = pd.read_csv(TABLES_DIR / "exp4_communication.csv")
    ax4  = axes[1, 1]
    ax4.bar(df4['Approach'], df4['Total_MB'],
            color=[COLORS['centralized'], COLORS['federated']], alpha=0.85)
    ax4.set_ylabel('Total MB Transmitted')
    ax4.set_title('Communication Efficiency')

    plt.tight_layout()
    out = GRAPHS_DIR / "exp6_summary_dashboard.png"
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out.name}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GENERATING EXPERIMENT GRAPHS")
    print("="*60)

    print("\n[1/6] Accuracy Comparison...")
    graph1_accuracy()

    print("[2/6] Privacy-Accuracy Tradeoff...")
    graph2_privacy_tradeoff()

    print("[3/6] Attack Resistance...")
    graph3_attack_resistance()

    print("[4/6] Communication Efficiency...")
    graph4_communication()

    print("[5/6] Federated Convergence...")
    graph5_convergence()

    print("[6/6] Summary Dashboard...")
    graph6_summary_dashboard()

    print("\n" + "="*60)
    print("ALL GRAPHS GENERATED")
    print("="*60)
    print(f"\nSaved to: {GRAPHS_DIR}")
    print("\nFiles:")
    for f in sorted(GRAPHS_DIR.glob("*.png")):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name:45s} {size_kb:>4d} KB")