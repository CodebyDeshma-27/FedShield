"""
Test script for Fraud Detection API
Run this to verify the API is working correctly
"""

import requests
import json
import numpy as np
import time

# API Configuration
API_URL = "http://localhost:5000"

def print_response(response):
    """Pretty print API response"""
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")

def test_health():
    """Test health check endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/health")
        print_response(response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Health check passed\n")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}\n")
        return False

def test_info():
    """Test info endpoint"""
    print("=" * 60)
    print("TEST 2: API Info")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/info")
        print_response(response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Info endpoint passed\n")
        return True
    except Exception as e:
        print(f"❌ Info endpoint failed: {str(e)}\n")
        return False

def test_privacy():
    """Test privacy info endpoint"""
    print("=" * 60)
    print("TEST 3: Privacy Information")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/privacy")
        print_response(response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Privacy endpoint passed\n")
        return True
    except Exception as e:
        print(f"❌ Privacy endpoint failed: {str(e)}\n")
        return False

def test_predict_valid():
    """Test prediction with valid input"""
    print("=" * 60)
    print("TEST 4: Predict - Valid Input (Normal Transaction)")
    print("=" * 60)
    try:
        # Generate random normal transaction features
        features = np.random.randn(30).tolist()
        
        payload = {"features": features}
        print(f"Request: {json.dumps({'features': [f'value{i}' for i in range(30)]}, indent=2)}")
        
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "fraud" in data, "Missing 'fraud' in response"
        assert "fraud_probability" in data, "Missing 'fraud_probability' in response"
        
        print(f"✅ Prediction passed - Fraud: {data['fraud']}, Probability: {data['fraud_probability']}\n")
        return True
    except Exception as e:
        print(f"❌ Prediction failed: {str(e)}\n")
        return False

def test_predict_fraud():
    """Test prediction with features that might indicate fraud"""
    print("=" * 60)
    print("TEST 5: Predict - Features with High Fraud Risk")
    print("=" * 60)
    try:
        # Create features with high values (might indicate fraud)
        features = [1.0] * 30
        
        payload = {"features": features}
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ High-risk prediction passed\n")
        return True
    except Exception as e:
        print(f"❌ High-risk prediction failed: {str(e)}\n")
        return False

def test_predict_invalid_length():
    """Test prediction with invalid feature length"""
    print("=" * 60)
    print("TEST 6: Predict - Invalid Feature Length")
    print("=" * 60)
    try:
        # Wrong number of features (should be 30)
        features = [0.1, 0.2, 0.3]  # Only 3 instead of 30
        
        payload = {"features": features}
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Invalid length validation passed\n")
        return True
    except Exception as e:
        print(f"❌ Invalid length test failed: {str(e)}\n")
        return False

def test_predict_invalid_type():
    """Test prediction with invalid data type"""
    print("=" * 60)
    print("TEST 7: Predict - Invalid Data Type")
    print("=" * 60)
    try:
        payload = {"features": "not a list"}
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Invalid type validation passed\n")
        return True
    except Exception as e:
        print(f"❌ Invalid type test failed: {str(e)}\n")
        return False

def test_predict_missing_field():
    """Test prediction with missing required field"""
    print("=" * 60)
    print("TEST 8: Predict - Missing Features Field")
    print("=" * 60)
    try:
        payload = {}  # Empty payload
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Missing field validation passed\n")
        return True
    except Exception as e:
        print(f"❌ Missing field test failed: {str(e)}\n")
        return False

def test_batch_predict():
    """Test batch prediction endpoint"""
    print("=" * 60)
    print("TEST 9: Batch Predict - Multiple Transactions")
    print("=" * 60)
    try:
        # Create 5 test transactions
        transactions = [
            {"features": np.random.randn(30).tolist()},
            {"features": np.random.randn(30).tolist()},
            {"features": [1.0] * 30},
            {"features": [-1.0] * 30},
            {"features": np.random.randn(30).tolist()},
        ]
        
        payload = {"transactions": transactions}
        response = requests.post(
            f"{API_URL}/batch-predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "predictions" in data, "Missing 'predictions' in response"
        assert "summary" in data, "Missing 'summary' in response"
        
        print(f"✅ Batch prediction passed - {len(data['predictions'])} predictions made\n")
        return True
    except Exception as e:
        print(f"❌ Batch prediction failed: {str(e)}\n")
        return False

def test_404():
    """Test 404 error handling"""
    print("=" * 60)
    print("TEST 10: Error Handling - 404 Not Found")
    print("=" * 60)
    try:
        response = requests.get(f"{API_URL}/nonexistent")
        print_response(response)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ 404 error handling passed\n")
        return True
    except Exception as e:
        print(f"❌ 404 error handling failed: {str(e)}\n")
        return False

def main():
    """Run all tests"""
    print("\n" * 2)
    print("╔" + "=" * 58 + "╗")
    print("║" + " FRAUD DETECTION API - TEST SUITE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"\nTesting API at: {API_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"❌ API is not responding correctly")
            print(f"Status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_URL}")
        print("Make sure the API is running with: python api/app.py\n")
        return
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}\n")
        return
    
    # Run tests
    tests = [
        test_health,
        test_info,
        test_privacy,
        test_predict_valid,
        test_predict_fraud,
        test_predict_invalid_length,
        test_predict_invalid_type,
        test_predict_missing_field,
        test_batch_predict,
        test_404,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}\n")
            results.append(False)
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! API is working correctly.\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above.\n")

if __name__ == "__main__":
    main()
