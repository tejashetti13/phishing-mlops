# Use official Python image
FROM python:3.11-slim

# Set work directory inside the container
WORKDIR /app

# Install system dependencies (optional, but helpful for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better build caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
