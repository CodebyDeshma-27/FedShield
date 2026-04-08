"""
Quick test with curl commands for the Fraud Detection API
Copy and paste these commands in your terminal to test the API
"""

# Start API first:
# python api/app.py

# ============================================================
# 1. TEST HEALTH CHECK
# ============================================================
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "model": "DP-Protected-Fraud-Detector-v1.0",
#   "accuracy": 0.9993,
#   ...
# }

# ============================================================
# 2. TEST API INFO
# ============================================================
curl http://localhost:5000/info

# ============================================================
# 3. TEST PRIVACY INFO
# ============================================================
curl http://localhost:5000/privacy

# ============================================================
# 4. TEST PREDICTION WITH NORMAL TRANSACTION
# ============================================================
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      0.1, -0.2, 0.05, 0.0, -0.1,
      0.2, -0.05, 0.0, 0.1, -0.2,
      0.05, 0.0, -0.1, 0.2, -0.05,
      0.0, 0.1, -0.2, 0.05, 0.0,
      -0.1, 0.2, -0.05, 0.0, 0.1,
      -0.2, 0.05, 0.0, -0.1, 0.2
    ]
  }'

# Expected response:
# {
#   "fraud": false,
#   "fraud_probability": 0.15,
#   "confidence": 0.85,
#   "privacy": {
#     "protected": true,
#     "epsilon": 1.0,
#     "delta": 1e-5
#   }
# }

# ============================================================
# 5. TEST PREDICTION WITH POSSIBLY FRAUDULENT TRANSACTION
# ============================================================
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 1.0, 1.0
    ]
  }'

# ============================================================
# 6. TEST ERROR: INVALID FEATURE LENGTH
# ============================================================
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [0.1, 0.2, 0.3]
  }'

# Expected response (400 Bad Request):
# {
#   "error": "Expected 30 features, got 3",
#   "expected_length": 30,
#   "received_length": 3
# }

# ============================================================
# 7. TEST ERROR: INVALID DATA TYPE
# ============================================================
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": "not a list"
  }'

# Expected response (400 Bad Request):
# {
#   "error": "Features must be a list, got str",
#   ...
# }

# ============================================================
# 8. TEST ERROR: MISSING FIELD
# ============================================================
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected response (400 Bad Request):
# {
#   "error": "Missing 'features' field in request",
#   ...
# }

# ============================================================
# 9. TEST BATCH PREDICTION
# ============================================================
curl -X POST http://localhost:5000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "features": [
          0.1, -0.2, 0.05, 0.0, -0.1,
          0.2, -0.05, 0.0, 0.1, -0.2,
          0.05, 0.0, -0.1, 0.2, -0.05,
          0.0, 0.1, -0.2, 0.05, 0.0,
          -0.1, 0.2, -0.05, 0.0, 0.1,
          -0.2, 0.05, 0.0, -0.1, 0.2
        ]
      },
      {
        "features": [
          1.0, 1.0, 1.0, 1.0, 1.0,
          1.0, 1.0, 1.0, 1.0, 1.0,
          1.0, 1.0, 1.0, 1.0, 1.0,
          1.0, 1.0, 1.0, 1.0, 1.0,
          1.0, 1.0, 1.0, 1.0, 1.0,
          1.0, 1.0, 1.0, 1.0, 1.0
        ]
      }
    ]
  }'

# Expected response:
# {
#   "predictions": [
#     {"transaction_index": 0, "fraud": false, "fraud_probability": ...},
#     {"transaction_index": 1, "fraud": true, "fraud_probability": ...}
#   ],
#   "summary": {
#     "total": 2,
#     "fraud_count": 1,
#     "normal_count": 1,
#     "fraud_percentage": 50.0
#   }
# }

# ============================================================
# 10. TEST 404 ERROR
# ============================================================
curl http://localhost:5000/nonexistent

# Expected response (404 Not Found):
# {
#   "error": "Endpoint not found",
#   "available_endpoints": [...]
# }
