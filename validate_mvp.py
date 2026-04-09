#!/usr/bin/env python
"""
FedShield MVP Quick Start Script
Runs the complete MVP pipeline and validates all components
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class MVPValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.status = {
            "data": False,
            "models": False,
            "api": False,
            "results": False,
            "ready_for_demo": False
        }
    
    def check_results_exist(self) -> bool:
        """Check if pipeline results exist"""
        print("\n📋 Checking Results Data...")
        
        results_dir = self.project_root / "results"
        required_files = [
            "pipeline_results.json",
            "attack_evaluation_results.json",
            "models/centralized_model.pth",
            "models/federated_model.pth",
            "models/dp_protected_model.pth"
        ]
        
        all_exist = True
        for file in required_files:
            file_path = results_dir / file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {file} ({size_mb:.2f} MB)")
                self.status["results"] = True
            else:
                print(f"  ❌ {file} - MISSING")
                all_exist = False
        
        return all_exist
    
    def validate_metrics(self) -> dict:
        """Validate metrics in results"""
        print("\n📊 Validating Metrics...")
        
        results_path = self.project_root / "results" / "pipeline_results.json"
        if not results_path.exists():
            print("  ❌ Results file not found")
            return {}
        
        try:
            with open(results_path) as f:
                results = json.load(f)
            
            models = results.get("models", {})
            print(f"  ✅ Found {len(models)} trained models:")
            
            metrics_summary = {}
            for model_name, model_data in models.items():
                accuracy = model_data.get("accuracy", 0)
                print(f"     • {model_name.replace('_', ' ').title()}: {accuracy*100:.2f}% accuracy")
                metrics_summary[model_name] = {
                    "accuracy": accuracy,
                    "auc_roc": model_data.get("auc_roc", 0),
                    "status": model_data.get("status", "unknown")
                }
            
            self.status["models"] = len(models) == 3
            return metrics_summary
        
        except Exception as e:
            print(f"  ❌ Error reading results: {e}")
            return {}
    
    def check_api_structure(self) -> bool:
        """Check if API has the necessary endpoints"""
        print("\n🔌 Checking API Structure...")
        
        api_file = self.project_root / "api" / "app.py"
        if not api_file.exists():
            print("  ❌ api/app.py not found")
            return False
        
        with open(api_file) as f:
            content = f.read()
        
        required_endpoints = [
            "/metrics",
            "/metrics/comparison",
            "/metrics/detailed",
            "/metrics/attacks",
            "/metrics/summary"
        ]
        
        endpoints_found = []
        for endpoint in required_endpoints:
            if endpoint in content:
                endpoints_found.append(endpoint)
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - NOT FOUND")
        
        self.status["api"] = len(endpoints_found) >= 4
        return self.status["api"]
    
    def generate_report(self) -> str:
        """Generate MVP readiness report"""
        print("\n" + "="*60)
        print("🎉 MVP READINESS REPORT")
        print("="*60)
        
        all_ready = all(self.status.values())
        
        print(f"""
Status Summary:
  📊 Results Data: {'✅' if self.status['results'] else '❌'}
  🤖 Models Trained: {'✅' if self.status['models'] else '❌'}
  🔌 API Endpoints: {'✅' if self.status['api'] else '❌'}
  📈 Metrics Valid: {'✅' if self.status.get('metrics', False) else '⚠️'}

Overall MVP Status: {'🚀 READY FOR DEMO' if all_ready else '⏳ NOT READY'}

Next Steps:
  1. Start API: cd api && python app.py
  2. Extract Dashboard: unzip your_dashboard.zip
  3. Install Dependencies: cd dashboard && npm install
  4. Create .env: REACT_APP_API_URL=http://localhost:5000
  5. Start Dashboard: npm start
  6. Open http://localhost:3000 in browser

Access Points:
  🔙 Backend API: http://localhost:5000
  📊 Dashboard: http://localhost:3000
  📋 Health Check: curl http://localhost:5000/health
  📈 Metrics API: curl http://localhost:5000/metrics
""")
        
        return "READY" if all_ready else "NOT_READY"
    
    def run_validation(self):
        """Run all validations"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║           FedShield MVP Validation Suite                     ║
║                                                              ║
║  This script validates your project is ready for demo        ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        self.check_results_exist()
        metrics = self.validate_metrics()
        self.status["metrics"] = bool(metrics)
        self.check_api_structure()
        
        report = self.generate_report()
        
        return report


def main():
    """Run MVP validation"""
    # Determine project root
    project_root = Path(__file__).parent.parent if Path(__file__).name == "validate_mvp.py" else Path(".")
    
    validator = MVPValidator(project_root)
    status = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if status == "READY" else 1)


if __name__ == "__main__":
    main()
