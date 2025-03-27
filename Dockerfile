# Use Python 3.12 image as a base
FROM python:3.12-slim

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

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Explicitly install sphinx-rtd-theme to ensure it is available
RUN pip install sphinx-rtd-theme

# Build the Sphinx documentation
WORKDIR /app/docs
RUN make html

# Expose port for serving documentation
EXPOSE 8000

# Use sphinx-autobuild to serve and auto-update the documentation
CMD ["sphinx-autobuild", "/app/docs", "/app/docs/_build/html", "--host", "0.0.0.0", "--port", "8000"]

# run with command below 
# docker build -t sphinx-docs . && docker run -p 8000:8000 -v $(pwd)/docs:/app/docs sphinx-docs    