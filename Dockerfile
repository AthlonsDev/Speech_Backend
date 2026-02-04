# Use an official Python image
FROM python:3.11-slim

# Use PyTorch base image (includes Python + PyTorch + deps)
# FROM pytorch/pytorch:2.4.0-cpu

# Set working directory inside the container
WORKDIR /app

# Copy dependencies first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
