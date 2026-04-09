"""
Site customization - suppresses verbose dependency logs
This file is automatically loaded by Python before anything else
"""

import logging
import sys

# Suppress alembic and other noisy libraries
for logger_name in ['alembic', 'alembic.runtime', 'alembic.runtime.plugins', 'sqlalchemy', 'urllib3', 'flask']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)
    logging.getLogger(logger_name).propagate = False
