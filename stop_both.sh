#!/bin/bash

echo "🛑 Stopping JIRA PLAT and Dashboard Services..."
echo ""

# Stop both services
sudo docker-compose down

echo ""
echo "✅ Both services stopped successfully!"
echo ""
echo "📋 To restart both services: ./start_both.sh" 