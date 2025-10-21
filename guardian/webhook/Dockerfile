FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY webhook_receiver.py .

# Run as non-root user
RUN useradd -m -u 1000 webhook && chown -R webhook:webhook /app
USER webhook

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "webhook_receiver.py"]
