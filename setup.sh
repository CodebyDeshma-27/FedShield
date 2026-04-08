#!/bin/bash

# Installation Script for Privacy-Preserving Fraud Intelligence Network
# Run this script to set up the complete environment

echo "==========================================="
echo "🏦 Fraud Intelligence Network Setup"
echo "==========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo ""
echo "📥 Installing core dependencies..."
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "📥 Installing ML libraries..."
pip install numpy==1.24.3 pandas==2.0.3 scikit-learn==1.3.0

echo ""
echo "📥 Installing federated learning..."
pip install flwr==1.5.0

echo ""
echo "📥 Installing additional libraries..."
pip install matplotlib==3.7.2 seaborn==0.12.2 imbalanced-learn==0.11.0
pip install tqdm==4.66.1 pyyaml==6.0.1

echo ""
echo "✅ All dependencies installed!"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data
mkdir -p results/graphs
mkdir -p results/tables
mkdir -p results/models
echo "✅ Directories created"

# Download sample dataset (optional)
echo ""
echo "📥 Dataset setup..."
echo "Please download the Credit Card Fraud dataset from:"
echo "https://www.kaggle.com/mlg-ulb/creditcardfraud"
echo ""
echo "Place 'creditcard.csv' in the 'data/' folder"
echo "OR the system will generate a synthetic dataset automatically"

echo ""
echo "==========================================="
echo "✅ Setup Complete!"
echo "==========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run experiments:"
echo "  python main.py --mode all"
echo ""
echo "For more options:"
echo "  python main.py --help"
echo ""
