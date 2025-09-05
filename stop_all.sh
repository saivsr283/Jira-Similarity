#!/bin/bash

echo "🛑 Stopping All JIRA Analysis Services..."
echo ""

# Stop all services
sudo docker-compose down

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "📋 To restart all services: ./start_all.sh" 