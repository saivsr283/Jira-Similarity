#!/bin/bash

echo "🚀 Starting JIRA PLAT and Filter Services..."
echo ""

# Start PLAT (web) and Filter services only
sudo docker-compose --profile web --profile filter up -d --build

echo ""
echo "✅ Both services started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   📋 PLAT Interface: http://localhost:8501"
echo "   🔎 Filter Interface: http://localhost:8503"
echo ""
echo "📋 Services:"
echo "   - PLAT Ticket Analysis (Port 8501) - Find similar tickets"
echo "   - Filter Analysis (Port 8503) - Fetch and group tickets via JQL"
echo ""
echo "🔧 To stop both services: ./stop_both.sh" 