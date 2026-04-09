#!/usr/bin/env python
"""
Simple launcher - just delegates to main.py
"""

if __name__ == '__main__':
    import sys
    import logging
    
    # Suppress dependency logs
    for lib in ['alembic', 'alembic.runtime', 'alembic.runtime.plugins', 'sqlalchemy']:
        logging.getLogger(lib).setLevel(logging.CRITICAL)
    
    from main import main
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='FedShield - Privacy-Preserving Fraud Detection')
    parser.add_argument('--mode', type=str, choices=['centralized', 'federated', 'federated_dp', 'all'], default='all')
    parser.add_argument('--num_rounds', type=int, default=10)
    parser.add_argument('--num_clients', type=int, default=5)
    parser.add_argument('--epsilon', type=float, default=1.0)
    parser.add_argument('--distribution', type=str, choices=['iid', 'non-iid'], default='iid')
    
    args = parser.parse_args()
    
    # Add num_banks attribute (same as num_clients for compatibility)
    if not hasattr(args, 'num_banks'):
        args.num_banks = args.num_clients
    
    # Run
    main(args)
