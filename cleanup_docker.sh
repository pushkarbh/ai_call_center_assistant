#!/bin/bash

# Script to stop and cleanup Docker container and image

echo "🧹 Cleaning up Docker resources..."
echo "=================================="

# Stop the container
echo "Stopping container..."
docker stop call-center-test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Container stopped"
else
    echo "ℹ️  No running container found"
fi

# Remove the container
echo "Removing container..."
docker rm call-center-test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Container removed"
else
    echo "ℹ️  No container to remove"
fi

# Remove the image
echo "Removing image..."
docker rmi call-center-assistant:test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Image removed"
else
    echo "ℹ️  No image to remove"
fi

echo ""
echo "✅ Cleanup complete!"
