#!/bin/bash

echo "🔄 Restarting JIRA Similarity Tool Web UI..."

# Stop the web UI
echo "🛑 Stopping web UI..."
./stop-web.sh

# Wait a moment for cleanup
sleep 2

# Start the web UI
echo "🚀 Starting web UI..."
./start-web.sh

echo "✅ Restart completed!"
echo "🌐 Access your web UI at: http://localhost:8501" 