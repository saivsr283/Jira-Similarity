#!/bin/bash

echo "🚀 Starting Unified JIRA Analysis Suite..."
echo "=========================================="

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.unified.yml down

# Build and start the unified service
echo "🔨 Building and starting unified service..."
docker-compose -f docker-compose.unified.yml up --build -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker ps | grep -q "jira-unified-web"; then
    echo ""
    echo "✅ Unified JIRA Analysis Suite is running!"
    echo "=========================================="
    echo "🌐 Access URLs:"
    echo "   • Unified Interface: http://localhost:8501"
    echo ""
    echo "📋 Available Features:"
    echo "   • 🎯 PLAT Similarity Tool (Tab 1)"
    echo "   • �� Filter Analysis (Tab 2)"
    echo ""
    echo "�� To stop the service:"
    echo "   docker-compose -f docker-compose.unified.yml down"
    echo ""
else
    echo "❌ Failed to start unified service"
    echo "Check logs with: docker-compose -f docker-compose.unified.yml logs"
fi
