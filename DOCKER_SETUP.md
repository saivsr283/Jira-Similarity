# JIRA Similarity Tool - Docker Setup Guide

## 🐳 Docker Setup Complete!

The JIRA Similarity Tool has been successfully containerized and is ready to use.

## ✅ What's Been Created

### Docker Files
- **`Dockerfile`** - Python 3.9 slim image with all dependencies
- **`docker-compose.yml`** - Multi-service setup for CLI and testing
- **`.dockerignore`** - Optimized build context
- **`docker-run.sh`** - Easy-to-use Docker wrapper script
- **`config.json`** - JIRA credentials configuration

### Docker Image Features
- ✅ Python 3.9 slim base image
- ✅ All required dependencies installed
- ✅ Non-root user for security
- ✅ Volume mounting for config and exports
- ✅ Optimized build with caching

## 🚀 Quick Start

### 1. Build the Docker Image
```bash
# Using the wrapper script
./docker-run.sh build

# Or directly
sudo docker build -t jira-similarity-tool .
```

### 2. Run Tests
```bash
# Using the wrapper script
./docker-run.sh test

# Or directly
sudo docker run --rm jira-similarity-tool python test_python_tool.py
```

### 3. Analyze a Ticket
```bash
# Using the wrapper script
./docker-run.sh analyze PLAT-44192

# Or directly
sudo docker run --rm \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/exports:/app/exports" \
  jira-similarity-tool PLAT-44192 --config /app/config.json
```

## 📋 Usage Examples

### Basic Ticket Analysis
```bash
sudo docker run --rm \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  jira-similarity-tool PLAT-44192 --config /app/config.json
```

### Advanced Analysis with Options
```bash
sudo docker run --rm \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/exports:/app/exports" \
  jira-similarity-tool PLAT-44192 \
  --jql "project = PLAT AND status != Closed" \
  --threshold 0.5 \
  --max-results 20 \
  --output /app/exports/results.json
```

### Run Tests
```bash
sudo docker run --rm jira-similarity-tool python test_python_tool.py
```

### Interactive Python Shell
```bash
sudo docker run --rm -it \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  jira-similarity-tool python
```

## 🔧 Configuration

### Environment Variables
```bash
export JIRA_URL="https://koreteam.atlassian.net"
export JIRA_USERNAME="hemanth.bandaru@kore.com"
export JIRA_API_TOKEN="your-api-token"
```

### Config File
The `config.json` file is mounted into the container:
```json
{
  "jira_url": "https://koreteam.atlassity.net",
  "username": "hemanth.bandaru@kore.com",
  "api_token": "your-api-token"
}
```

## 📁 Volume Mounts

- **`config.json`** - JIRA credentials (read-only)
- **`exports/`** - Output directory for results
- **`test_jira_connection.py`** - Connection test script

## 🧪 Testing

### Run All Tests
```bash
sudo docker run --rm jira-similarity-tool python test_python_tool.py
```

### Test JIRA Connection
```bash
sudo docker run --rm \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/test_jira_connection.py:/app/test_jira_connection.py:ro" \
  jira-similarity-tool python test_jira_connection.py
```

## 🐛 Troubleshooting

### Permission Issues
```bash
# Add user to docker group (one-time setup)
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

### API Connection Issues
- Verify JIRA URL is correct
- Check API token permissions
- Ensure username is correct
- Test with a known existing ticket

### Volume Mount Issues
```bash
# Check if config file exists
ls -la config.json

# Verify file permissions
chmod 644 config.json
```

## 📊 Docker Commands Reference

### Build
```bash
sudo docker build -t jira-similarity-tool .
```

### Run
```bash
sudo docker run --rm jira-similarity-tool [COMMAND]
```

### List Images
```bash
sudo docker images jira-similarity-tool
```

### Remove Image
```bash
sudo docker rmi jira-similarity-tool
```

### View Logs
```bash
sudo docker logs [CONTAINER_ID]
```

## 🎯 Next Steps

1. **Test the setup**: Run `./docker-run.sh test`
2. **Analyze a ticket**: Run `./docker-run.sh analyze YOUR-TICKET-KEY`
3. **Export results**: Use `--output` flag to save results
4. **Integrate into workflow**: Use in CI/CD pipelines

## 📞 Support

For issues:
1. Check Docker logs: `sudo docker logs [CONTAINER_ID]`
2. Run tests: `./docker-run.sh test`
3. Test connection: Use `test_jira_connection.py`
4. Verify configuration: Check `config.json`

---

**✅ Docker setup is complete and ready to use!** 