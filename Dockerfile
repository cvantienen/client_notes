# Use Python image as a base
FROM python:3.9-slim

# Install make and other required packages
RUN apt-get update && apt-get install -y \
    make \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy everything into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for serving documentation (optional)
EXPOSE 8000

# Default command to generate HTML using Sphinx
CMD ["sphinx-autobuild", "-b", "html", "source", "_build/html"]
