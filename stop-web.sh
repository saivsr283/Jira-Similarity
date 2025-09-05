#!/bin/bash

# Stop JIRA Similarity Tool Web UI

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping JIRA Similarity Tool Web UI...${NC}"

# Stop and remove the container
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker stop jira-similarity-web 2>/dev/null || true
    docker rm jira-similarity-web 2>/dev/null || true
else
    sudo docker stop jira-similarity-web 2>/dev/null || true
    sudo docker rm jira-similarity-web 2>/dev/null || true
fi

echo -e "${GREEN}✅ Web UI stopped successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 To start again:${NC}"
echo "   ./start-web.sh" 