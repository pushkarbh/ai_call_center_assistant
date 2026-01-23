#!/bin/bash

# Script to test Docker build and run locally
# This simulates the exact HF Spaces deployment environment

echo "🐳 Testing Docker Deployment (HF Spaces simulation)"
echo "===================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build the image
echo "🔨 Building Docker image..."
docker build -t call-center-assistant:test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker build successful"
echo ""

# Stop any existing container
echo "🧹 Cleaning up existing containers..."
docker stop call-center-test 2>/dev/null
docker rm call-center-test 2>/dev/null

# Run the container
echo "🚀 Starting container on port 7860..."
docker run -d \
    --name call-center-test \
    -p 7860:7860 \
    call-center-assistant:test

if [ $? -ne 0 ]; then
    echo "❌ Docker run failed!"
    exit 1
fi

echo ""
echo "✅ Container started successfully!"
echo ""
echo "📱 App should be available at: http://localhost:7860"
echo ""
echo "To view logs:    docker logs -f call-center-test"
echo "To stop:         docker stop call-center-test"
echo "To clean up:     docker rm call-center-test && docker rmi call-center-assistant:test"
