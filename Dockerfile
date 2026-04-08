FROM python:3.10-slim

WORKDIR /app

# Copy all files
COPY requirements.txt .
COPY api/requirements.txt api/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy application code
COPY api/ api/
COPY models/ models/
COPY utils/ utils/
COPY config.py .
COPY results/ results/

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the API
CMD ["python", "-m", "api.app"]
