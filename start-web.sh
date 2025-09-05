#!/bin/bash

# JIRA Similarity Tool - Web UI Starter

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 JIRA Similarity Tool - Web UI${NC}"
echo "======================================"

# Function to build web image
build_web_image() {
    echo -e "${YELLOW}🔨 Building web UI Docker image...${NC}"
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        docker build -f Dockerfile.web -t jira-similarity-web .
        echo -e "${GREEN}✅ Web UI image built successfully!${NC}"
    else
        echo -e "${YELLOW}🔨 Building web UI image with sudo...${NC}"
        sudo docker build -f Dockerfile.web -t jira-similarity-web .
        echo -e "${GREEN}✅ Web UI image built successfully!${NC}"
    fi
}

# Function to start web UI
start_web_ui() {
    echo -e "${YELLOW}🚀 Starting web UI...${NC}"
    
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        docker run -d \
            --name jira-similarity-web \
            -p 8501:8501 \
            -v "$(pwd)/config.json:/app/config.json:ro" \
            -v "$(pwd)/exports:/app/exports" \
            jira-similarity-web
    else
        sudo docker run -d \
            --name jira-similarity-web \
            -p 8501:8501 \
            -v "$(pwd)/config.json:/app/config.json:ro" \
            -v "$(pwd)/exports:/app/exports" \
            jira-similarity-web
    fi
    
    echo -e "${GREEN}✅ Web UI started successfully!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Access your web UI at:${NC}"
    echo -e "${GREEN}   http://localhost:8501${NC}"
    echo ""
    echo -e "${YELLOW}📋 To stop the web UI:${NC}"
    echo "   ./stop-web.sh"
    echo ""
    echo -e "${YELLOW}📋 To view logs:${NC}"
    echo "   docker logs jira-similarity-web"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build    Build the web UI Docker image"
    echo "  start    Start the web UI (builds if needed)"
    echo "  stop     Stop the web UI"
    echo "  logs     Show web UI logs"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 build"
    echo "  $0 stop"
}

# Function to stop web UI
stop_web_ui() {
    echo -e "${YELLOW}🛑 Stopping web UI...${NC}"
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        docker stop jira-similarity-web 2>/dev/null || true
        docker rm jira-similarity-web 2>/dev/null || true
    else
        sudo docker stop jira-similarity-web 2>/dev/null || true
        sudo docker rm jira-similarity-web 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Web UI stopped!${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}📋 Web UI logs:${NC}"
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        docker logs jira-similarity-web
    else
        sudo docker logs jira-similarity-web
    fi
}

# Main script logic
case "${1:-start}" in
    "build")
        build_web_image
        ;;
    "start")
        # Check if image exists, build if not
        if ! docker images jira-similarity-web --format "{{.Repository}}" | grep -q jira-similarity-web; then
            build_web_image
        fi
        start_web_ui
        ;;
    "stop")
        stop_web_ui
        ;;
    "logs")
        show_logs
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_usage
        exit 1
        ;;
esac 