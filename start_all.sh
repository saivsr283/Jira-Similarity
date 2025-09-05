#!/bin/bash

echo "🚀 Starting All JIRA Analysis Services..."
echo ""

# Start all services
sudo docker-compose --profile web --profile dashboard --profile filter up -d --build

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   📋 PLAT Interface: http://localhost:8501"
echo "   📊 Dashboard Interface: http://localhost:8502"
echo "   🔍 Filter Interface: http://localhost:8503"
echo ""
echo "📋 Services:"
echo "   - PLAT Ticket Analysis (Port 8501) - Find similar tickets for specific PLAT issues"
echo "   - Dashboard Issue Grouping (Port 8502) - Group similar issues from dashboard"
echo "   - Filter Analysis (Port 8503) - Analyze filtered tickets by categories"
echo ""
echo "🔧 To stop all services: ./stop_all.sh" 