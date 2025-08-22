# Base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Create input/output folders
RUN mkdir input output

# Run main.py
CMD ["python", "main.py"]
