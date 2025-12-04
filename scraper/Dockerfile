# Use Python slim image (lightweight)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY scrape.py .

# Create output directory with proper permissions
RUN mkdir -p /output && chmod 777 /output

# Run the script
CMD ["python", "-u", "scrape.py"]

