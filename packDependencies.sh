#!/bin/bash

#####################################################
# Pack dependencies for Linux using Docker
#####################################################

echo "######################################## Pack dependencies for Linux with Docker"

# Clean up previous builds
TARGET_PATH="target"
mkdir -p ./${TARGET_PATH}/dependenciesVenv/lib/python3.9/site-packages

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

echo "Found requirements.txt, starting Docker build..."

# Create a temporary Dockerfile for better control
cat > Dockerfile.temp << 'EOF'
FROM python:3.9-slim-bullseye
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -t /build/site-packages -r requirements.txt
EOF

# Build and extract dependencies
docker build -f Dockerfile.temp -t temp-deps-builder .
docker create --name temp-deps-container temp-deps-builder
docker cp temp-deps-container:/build/site-packages/. ./${TARGET_PATH}/dependenciesVenv/lib/python3.9/site-packages/
docker rm temp-deps-container
docker rmi temp-deps-builder
rm Dockerfile.temp

echo "######################################## Dependencies successfully packed for Linux"
echo "Size of dependencies:"
du -sh ./${TARGET_PATH}/dependenciesVenv/lib/python3.9/site-packages

# List main packages installed
echo "Main packages installed:"
ls -d ./${TARGET_PATH}/dependenciesVenv/lib/python3.9/site-packages/*/ | grep -v "__pycache__" | grep -v ".dist-info" | head -10