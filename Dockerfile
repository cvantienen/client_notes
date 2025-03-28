# Use Python 3.12 image as a base
FROM python:3.12-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    make \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy everything into the container
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose port for serving documentation
EXPOSE 8000

# Use mkdocs to serve the documentation
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]

# run with command below 
# docker build -t mkdocs-docs . && docker run -p 8000:8000 -v $(pwd):/app mkdocs-docs