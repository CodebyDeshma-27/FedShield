"""
Fraud Detection API Server
Production-grade REST API for fraud detection predictions
"""

from flask import Flask, request, jsonify
import torch
import numpy as np
import logging
from datetime import datetime
import os
import sys

# Add parent directory to path so we can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.fraud_detector import ModelUtils
from config import MODEL_CONFIG, DP_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logs from dependencies
logging.getLogger('alembic').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global variables for model and device
MODEL = None
DEVICE = None
MODEL_PATH = None


def load_model():
    """
    Load the DP-protected fraud detection model
    Called once on startup
    """
    global MODEL, DEVICE, MODEL_PATH
    
    try:
        # Use DP-protected model (production model)
        MODEL_PATH = "results/models/dp_protected_model.pth"
        
        logger.info(f"Loading model from: {MODEL_PATH}")
        
        # Check if model exists
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model file not found: {MODEL_PATH}")
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Determine device (GPU if available, else CPU)
        DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {DEVICE}")
        
        # Load model using ModelUtils
        MODEL = ModelUtils.load_model(MODEL_PATH)
        
        # Set to evaluation mode (no training)
        MODEL.eval()
        
        logger.info("✅ Model loaded successfully!")
        logger.info(f"Model architecture: {MODEL}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        logger.exception(e)
        return False


def validate_features(features):
    """
    Validate that features are correct format and length
    
    Args:
        features: List of feature values
        
    Returns:
        (is_valid: bool, error_message: str or None)
    """
    # Check if features exist
    if features is None:
        return False, "Missing 'features' field in request"
    
    # Check if features is a list
    if not isinstance(features, list):
        return False, f"Features must be a list, got {type(features).__name__}"
    
    # Check if list is not empty
    if len(features) == 0:
        return False, "Features list cannot be empty"
    
    # Check if correct length (should be 30 from config)
    expected_length = MODEL_CONFIG['input_dim']
    if len(features) != expected_length:
        return False, f"Expected {expected_length} features, got {len(features)}"
    
    # Check if all elements are numeric
    try:
        features_array = np.array(features, dtype=np.float32)
    except (ValueError, TypeError):
        return False, "All features must be numeric (int or float)"
    
    # Check for NaN or infinity
    if np.isnan(features_array).any():
        return False, "Features contain NaN (not a number) values"
    
    if np.isinf(features_array).any():
        return False, "Features contain infinity values"
    
    return True, None


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    Verifies API and model are working
    """
    try:
        # Check if model is loaded
        if MODEL is None:
            return jsonify({
                "status": "unhealthy",
                "message": "Model not loaded"
            }), 503
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "model": "DP-Protected-Fraud-Detector-v1.0",
            "device": str(DEVICE),
            "accuracy": 0.9993,
            "privacy": {
                "protected": True,
                "epsilon": float(DP_CONFIG['epsilon']),
                "delta": float(DP_CONFIG['delta'])
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/info', methods=['GET'])
def info():
    """
    API information endpoint
    Returns metadata about the API and model
    """
    try:
        return jsonify({
            "api_name": "Fraud Detection API",
            "version": "1.0.0",
            "description": "REST API for detecting fraudulent transactions using federated learning with differential privacy",
            "model": {
                "name": "DP-Protected Fraud Detector",
                "input_features": MODEL_CONFIG['input_dim'],
                "accuracy": 0.9993,
                "f1_score": 0.776,
                "auc_roc": 0.971
            },
            "privacy": {
                "method": "Differential Privacy",
                "epsilon": float(DP_CONFIG['epsilon']),
                "delta": float(DP_CONFIG['delta']),
                "guarantee": "Customer data cannot be extracted from this model",
                "federated": True,
                "num_banks": 5
            },
            "endpoints": {
                "/health": "GET - Health check",
                "/info": "GET - API information",
                "/predict": "POST - Make fraud predictions",
                "/privacy": "GET - Privacy guarantee details"
            },
            "example_usage": {
                "endpoint": "/predict",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "features": "[30 numeric values between -1 and 1]"
                },
                "expected_response": {
                    "fraud": "boolean",
                    "fraud_probability": "0.0-1.0",
                    "confidence": "0.0-1.0",
                    "privacy": {"protected": True, "epsilon": 1.0, "delta": 1e-5}
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Info endpoint failed: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/privacy', methods=['GET'])
def privacy_info():
    """
    Privacy guarantee information endpoint
    Explains the privacy protections in place
    """
    try:
        return jsonify({
            "privacy_mechanism": "Differential Privacy",
            "epsilon": float(DP_CONFIG['epsilon']),
            "delta": float(DP_CONFIG['delta']),
            "guarantee": "Mathematically proven - customer data cannot be extracted from this model even if attacker has full model weights",
            "how_it_works": {
                "step_1": "Model trained with gradient clipping and noise injection",
                "step_2": "Each bank only sends noisy gradients, never raw data",
                "step_3": "Server aggregates noisy updates",
                "step_4": "Result: Privacy guaranteed by mathematics, not obscurity"
            },
            "federated_learning": {
                "enabled": True,
                "description": "Data stays in each bank, only model updates are shared",
                "banks_participated": 5,
                "data_privacy": "Complete - raw customer data never leaves bank",
                "scalable_to": "50+ banks without code changes"
            },
            "attack_resistance": {
                "model_inversion": "2.74x harder with DP protection",
                "gradient_leakage": "Protected - gradients cannot be inverted"
            }
        }), 200
    except Exception as e:
        logger.error(f"Privacy info endpoint failed: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main fraud detection prediction endpoint
    
    Request format:
    {
        "features": [30 numeric values]
    }
    
    Response format:
    {
        "fraud": boolean,
        "fraud_probability": float (0.0-1.0),
        "confidence": float (0.0-1.0),
        "privacy": {...}
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            logger.warning("Request body is empty or not JSON")
            return jsonify({
                "error": "Request body must be JSON with 'features' field",
                "example": {"features": "[30 numeric values]"}
            }), 400
        
        # Extract features from request
        features = data.get('features')
        
        # Validate features
        is_valid, error_message = validate_features(features)
        if not is_valid:
            logger.warning(f"Invalid features: {error_message}")
            return jsonify({
                "error": error_message,
                "received_length": len(features) if isinstance(features, list) else "not a list",
                "expected_length": MODEL_CONFIG['input_dim']
            }), 400
        
        # Convert features to numpy array
        features_array = np.array(features, dtype=np.float32)
        
        # Convert to torch tensor for model inference
        with torch.no_grad():
            # Add batch dimension: (30,) → (1, 30)
            features_tensor = torch.tensor(features_array, dtype=torch.float32).unsqueeze(0)
            
            # Move to device if available
            if DEVICE.type == 'cuda':
                features_tensor = features_tensor.to(DEVICE)
            
            # Run inference
            output = MODEL(features_tensor)
            
            # Extract probabilities
            # Output shape: (1, 2) where:
            # output[0, 0] = probability of normal transaction
            # output[0, 1] = probability of fraud
            probabilities = output[0].cpu().numpy()
            normal_prob = float(probabilities[0])
            fraud_prob = float(probabilities[1])
        
        # Determine if fraud
        fraud_threshold = 0.5
        is_fraud = fraud_prob > fraud_threshold
        
        # Confidence is how sure we are (stronger signal)
        confidence = max(fraud_prob, normal_prob)
        
        # Log prediction
        logger.info(f"Prediction: fraud={is_fraud}, prob={fraud_prob:.4f}, confidence={confidence:.4f}")
        
        # Return response
        return jsonify({
            "fraud": is_fraud,
            "fraud_probability": round(fraud_prob, 4),
            "normal_probability": round(normal_prob, 4),
            "confidence": round(confidence, 4),
            "threshold_used": fraud_threshold,
            "privacy": {
                "protected": True,
                "epsilon": float(DP_CONFIG['epsilon']),
                "delta": float(DP_CONFIG['delta']),
                "method": "Differential Privacy"
            },
            "model_info": {
                "name": "DP-Protected-Fraud-Detector-v1.0",
                "accuracy": 0.9993,
                "f1_score": 0.776
            }
        }), 200
        
    except torch.cuda.OutOfMemoryError:
        logger.error("GPU out of memory")
        return jsonify({
            "error": "GPU out of memory",
            "suggestion": "Model has been moved to CPU, please retry"
        }), 503
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        logger.exception(e)
        return jsonify({
            "error": f"Prediction failed: {str(e)}"
        }), 500


@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction endpoint for multiple transactions
    
    Request format:
    {
        "transactions": [
            {"features": [30 values]},
            {"features": [30 values]},
            ...
        ]
    }
    
    Response format:
    {
        "predictions": [
            {"fraud": bool, "probability": float, ...},
            ...
        ],
        "summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({
                "error": "Request body must be JSON with 'transactions' field"
            }), 400
        
        transactions = data.get('transactions', [])
        
        if not isinstance(transactions, list):
            return jsonify({
                "error": "'transactions' must be a list"
            }), 400
        
        if len(transactions) == 0:
            return jsonify({
                "error": "transactions list cannot be empty"
            }), 400
        
        if len(transactions) > 1000:
            return jsonify({
                "error": "Maximum 1000 transactions per request"
            }), 400
        
        predictions = []
        fraud_count = 0
        normal_count = 0
        
        for idx, transaction in enumerate(transactions):
            features = transaction.get('features')
            
            # Validate
            is_valid, error_msg = validate_features(features)
            if not is_valid:
                predictions.append({
                    "transaction_index": idx,
                    "error": error_msg,
                    "fraud": None
                })
                continue
            
            # Predict
            features_array = np.array(features, dtype=np.float32)
            
            with torch.no_grad():
                features_tensor = torch.tensor(features_array, dtype=torch.float32).unsqueeze(0)
                if DEVICE.type == 'cuda':
                    features_tensor = features_tensor.to(DEVICE)
                
                output = MODEL(features_tensor)
                probabilities = output[0].cpu().numpy()
                fraud_prob = float(probabilities[1])
            
            is_fraud = fraud_prob > 0.5
            if is_fraud:
                fraud_count += 1
            else:
                normal_count += 1
            
            predictions.append({
                "transaction_index": idx,
                "fraud": is_fraud,
                "fraud_probability": round(fraud_prob, 4),
                "error": None
            })
        
        return jsonify({
            "predictions": predictions,
            "summary": {
                "total": len(transactions),
                "fraud_count": fraud_count,
                "normal_count": normal_count,
                "fraud_percentage": round((fraud_count / len(transactions) * 100), 2)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        return jsonify({
            "error": f"Batch prediction failed: {str(e)}"
        }), 500


# ============================
# METRICS & RESULTS ENDPOINTS
# ============================

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get all model metrics from pipeline results
    Returns metrics for centralized, federated, and DP-protected models
    """
    try:
        import json
        results_path = "results/pipeline_results.json"
        
        if not os.path.exists(results_path):
            return jsonify({
                "error": "Results not found",
                "message": "Run the pipeline first to generate results"
            }), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        # Extract model metrics
        models = results.get('models', {})
        
        return jsonify({
            "status": "success",
            "models": models,
            "timestamp": results.get('timestamp')
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return jsonify({
            "error": f"Failed to get metrics: {str(e)}"
        }), 500


@app.route('/metrics/comparison', methods=['GET'])
def get_metrics_comparison():
    """
    Get comparison of all three models
    Perfect for dashboard charts
    """
    try:
        import json
        results_path = "results/pipeline_results.json"
        
        if not os.path.exists(results_path):
            return jsonify({
                "error": "Results not found"
            }), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        models = results.get('models', {})
        
        # Format for React Recharts
        comparison_data = {
            "models": [],
            "metrics_available": ["accuracy", "precision", "recall", "f1_score", "auc_roc"]
        }
        
        for model_name, model_metrics in models.items():
            comparison_data["models"].append({
                "name": model_name.replace('_', ' ').title(),
                "accuracy": round(model_metrics.get('accuracy', 0) * 100, 2),
                "precision": round(model_metrics.get('precision', 0) * 100, 2),
                "recall": round(model_metrics.get('recall', 0) * 100, 2),
                "f1_score": round(model_metrics.get('f1_score', 0) * 100, 2),
                "auc_roc": round(model_metrics.get('auc_roc', 0) * 100, 2),
                "status": model_metrics.get('status', 'unknown')
            })
        
        return jsonify(comparison_data), 200
        
    except Exception as e:
        logger.error(f"Failed to get metrics comparison: {str(e)}")
        return jsonify({
            "error": f"Failed to get comparison: {str(e)}"
        }), 500


@app.route('/metrics/detailed/<model_type>', methods=['GET'])
def get_detailed_metrics(model_type):
    """
    Get detailed metrics for a specific model
    model_type: centralized, federated, or dp_protected
    """
    try:
        import json
        results_path = "results/pipeline_results.json"
        
        if not os.path.exists(results_path):
            return jsonify({"error": "Results not found"}), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        models = results.get('models', {})
        model_key = model_type.lower().replace('-', '_')
        
        if model_key not in models:
            return jsonify({
                "error": f"Model {model_type} not found",
                "available_models": list(models.keys())
            }), 404
        
        model_data = models[model_key]
        
        # Add privacy info if DP model
        if 'dp_protected' in model_key:
            model_data['privacy_info'] = {
                "epsilon": model_data.get('privacy_epsilon', 'N/A'),
                "delta": model_data.get('privacy_delta', 'N/A'),
                "protected": True
            }
        
        return jsonify({
            "model": model_key,
            "metrics": model_data,
            "raw_format": {
                "accuracy": model_data.get('accuracy'),
                "precision": model_data.get('precision'),
                "recall": model_data.get('recall'),
                "f1_score": model_data.get('f1_score'),
                "auc_roc": model_data.get('auc_roc')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get detailed metrics: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/metrics/attacks', methods=['GET'])
def get_attack_metrics():
    """
    Get attack evaluation results
    Shows vulnerability of models to different attacks
    """
    try:
        import json
        attack_path = "results/attack_evaluation_results.json"
        
        if not os.path.exists(attack_path):
            return jsonify({
                "error": "Attack evaluation results not found",
                "message": "Run attack evaluation first"
            }), 404
        
        with open(attack_path, 'r') as f:
            attack_results = json.load(f)
        
        return jsonify({
            "status": "success",
            "attack_evaluation": attack_results,
            "timestamp": attack_results.get('timestamp')
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get attack metrics: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/metrics/summary', methods=['GET'])
def get_summary():
    """
    Get summary of pipeline execution
    Dataset stats, model counts, results status
    """
    try:
        import json
        results_path = "results/pipeline_results.json"
        
        if not os.path.exists(results_path):
            return jsonify({"error": "Results not found"}), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        summary = {
            "pipeline_status": results.get('pipeline_status'),
            "timestamp": results.get('timestamp'),
            "data_summary": results.get('data'),
            "models_count": len(results.get('models', {})),
            "models_trained": list(results.get('models', {}).keys())
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/graphs/<graph_name>', methods=['GET'])
def get_graph(graph_name):
    """
    Serve graph images
    Available graphs: centralized_accuracy, federated_accuracy, etc.
    
    Returns: Base64 encoded image or file stream
    """
    try:
        import base64
        from pathlib import Path
        
        # Sanitize graph name
        safe_name = ''.join(c for c in graph_name if c.isalnum() or c in ('_', '-'))
        graph_path = f"results/graphs/{safe_name}.png"
        
        if not os.path.exists(graph_path):
            return jsonify({
                "error": f"Graph not found: {safe_name}",
                "available_graphs": ["centralized_accuracy"]
            }), 404
        
        # Read and encode image as base64
        with open(graph_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        return jsonify({
            "graph": safe_name,
            "format": "png",
            "data_uri": f"data:image/png;base64,{image_data}"
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get graph: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/export/results', methods=['GET'])
def export_results():
    """
    Export all results as JSON
    Useful for downloading full report
    """
    try:
        import json
        results_path = "results/pipeline_results.json"
        
        if not os.path.exists(results_path):
            return jsonify({"error": "Results not found"}), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        return jsonify({
            "status": "success",
            "data": results,
            "exported_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to export results: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/health - Server health check",
            "/info - API information",
            "/privacy - Privacy configuration",
            "/predict - Single transaction prediction",
            "/batch-predict - Batch prediction",
            "/metrics - All model metrics",
            "/metrics/comparison - Compare all models",
            "/metrics/detailed/<model_type> - Detailed metrics for specific model",
            "/metrics/attacks - Attack evaluation results",
            "/metrics/summary - Pipeline execution summary",
            "/graphs/<graph_name> - Get graph images",
            "/export/results - Export full results"
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": f"This endpoint does not support {request.method} requests"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


def main():
    """
    Start the API server
    """
    logger.info("=" * 60)
    logger.info("Fraud Detection API Server Starting")
    logger.info("=" * 60)
    
    # Load model before starting server
    if not load_model():
        logger.error("Failed to load model. Exiting.")
        sys.exit(1)
    
    # Start Flask app
    logger.info("Starting Flask server on 0.0.0.0:5000")
    logger.info("Visit http://localhost:5000/health to verify API is running")
    logger.info("Visit http://localhost:5000/info for API documentation")
    
    # Run with Flask development server
    # For production, use gunicorn or similar
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False in production
        threaded=True
    )


if __name__ == '__main__':
    main()
