#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t my-app .

echo "Starting application..."
docker-compose up -d

echo "Application deployed successfully!"
echo "Access your app at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs