FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY wiki_client.py .

# Expose port
EXPOSE 9000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
