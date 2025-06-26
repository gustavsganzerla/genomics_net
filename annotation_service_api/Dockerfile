FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y python3-pip docker.io && rm -rf /var/lib/apt/lists/*

# Install Flask
RUN pip install flask python-decouple

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Expose Flask port
EXPOSE 5000

# Run app
CMD ["python3", "app.py"]