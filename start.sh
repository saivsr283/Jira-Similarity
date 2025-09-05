#!/bin/bash

echo "🚀 Starting JIRA Unified Analyzer..."
echo "🔍 Single server with PLAT and DASHBOARD modes"
echo "🌐 Available at: http://localhost:8501"
echo ""

# Build and start the unified container
docker-compose --profile web up -d --build

echo ""
echo "✅ JIRA Unified Analyzer started successfully!"
echo "🌐 Access the application at: http://localhost:8501"
echo ""
echo "🎯 Available Modes:"
echo "   📋 PLAT Ticket Analysis - Find similar tickets for specific PLAT issues"
echo "   📊 Dashboard Issue Grouping - Group similar issues from dashboard"
echo ""
echo "📋 Features:"
echo "   - Unified interface for both PLAT and Dashboard analysis"
echo "   - Smart similarity detection and grouping"
echo "   - Export results in JSON and CSV formats"
echo "   - Real-time configuration updates"
echo ""
echo "🔧 To stop the server: ./stop.sh" 