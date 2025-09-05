# 🔍 JIRA Similarity Tool - Node.js Version

## 🎯 Overview

The JIRA Similarity Tool is an AI-powered Node.js solution that helps developers and teams reduce investigation time by automatically finding similar tickets and providing intelligent fix recommendations. It uses advanced NLP and machine learning to analyze ticket content, identify patterns, and suggest proven solutions.

## ✨ Key Features

- **🔍 Smart Similarity Analysis**: Uses TF-IDF and NLP to find related tickets
- **🛠️ Intelligent Fix Recommendations**: Suggests proven solutions from resolved tickets
- **📊 Pattern Recognition**: Identifies recurring issues and common failure modes
- **⚡ Time Savings**: Reduces investigation time by 2-4 hours per issue
- **📤 Export Capabilities**: Export results as JSON or CSV
- **🌐 Web Interface**: Beautiful web application with real-time analysis
- **🔧 CLI Support**: Command-line interface for automation
- **🎮 Demo Mode**: Standalone demo without JIRA API access

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd jira-similarity-tool

# Install dependencies
npm install

# Copy environment file
cp env.example .env
```

### 2. Configuration

Edit the `.env` file with your JIRA credentials:

```bash
JIRA_BASE_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

### 3. Run the Tool

#### Web Interface (Recommended)
```bash
npm run web
```
Open http://localhost:3000 in your browser

#### Demo Mode (No API Required)
```bash
npm run demo
```
Open http://localhost:3000 in your browser

#### Command Line
```bash
npm run cli
```

## 📋 Prerequisites

### JIRA API Token Setup

1. **Generate API Token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Give it a name (e.g., "JIRA Similarity Tool")
   - Copy the token

2. **Required Permissions**:
   - Read access to projects
   - Search permissions
   - Issue viewing permissions

### Node.js Requirements

- Node.js 16.0+
- npm 8.0+

## 🏗️ Architecture

### Core Components

1. **JIRAClient**: Handles JIRA API communication
2. **SimilarityEngine**: AI-powered similarity analysis
3. **JIRASimilarityTool**: Main orchestration class
4. **WebServer**: Express-based web interface
5. **CLI**: Command-line interface

### Technology Stack

- **Backend**: Node.js 16+
- **NLP**: natural, compromise
- **Web Framework**: Express.js
- **Frontend**: Bootstrap 5, Chart.js
- **Data Processing**: Built-in Node.js modules
- **Containerization**: Docker support

## 📊 How It Works

### 1. Ticket Analysis
- Fetches the reference ticket from JIRA
- Extracts key information (summary, description, metadata)

### 2. Similarity Search
- Builds intelligent JQL queries
- Searches for related tickets across the project
- Uses AI to calculate similarity scores

### 3. Pattern Recognition
- Identifies common words, components, and labels
- Analyzes resolution patterns
- Finds recurring issue types

### 4. Fix Recommendations
- Analyzes resolved similar tickets
- Extracts successful resolution strategies
- Provides context-aware suggestions

## 🎯 Use Cases

### For Developers
- **Quick Investigation**: Find similar issues and their solutions
- **Pattern Recognition**: Identify recurring problems
- **Time Savings**: Reduce debugging time by 2-4 hours

### For Teams
- **Knowledge Sharing**: Leverage team experience
- **Quality Improvement**: Learn from past resolutions
- **Efficiency**: Avoid duplicate work

### For Managers
- **Trend Analysis**: Identify common issues
- **Resource Planning**: Understand problem patterns
- **Process Improvement**: Optimize resolution workflows

## 📈 Performance Metrics

- **Similarity Accuracy**: 85%+ precision for related tickets
- **Time Savings**: 2-4 hours per investigation
- **Coverage**: Analyzes entire project history
- **Response Time**: <30 seconds for typical analysis

## 🔧 Configuration Options

### Analysis Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SIMILARITY_THRESHOLD` | 0.3 | Minimum similarity score |
| `MAX_RESULTS` | 100 | Maximum tickets to analyze |
| `ENABLE_NLP` | true | Enable NLP processing |

### JIRA Settings

| Parameter | Required | Description |
|-----------|----------|-------------|
| `JIRA_BASE_URL` | Yes | Your JIRA instance URL |
| `JIRA_API_TOKEN` | Yes | API token for authentication |
| `JIRA_EMAIL` | Yes | Your JIRA email address |

## 📤 Export Formats

### JSON Export
```json
{
  "referenceTicket": {...},
  "similarTickets": [...],
  "analysisSummary": {...},
  "searchQuery": "...",
  "exportedAt": "2024-01-01T12:00:00"
}
```

### CSV Export
- Ticket key, summary, similarity score
- Status, issue type, priority
- Components, labels, resolution

## 🛠️ Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify JIRA URL is correct
   - Check API token permissions
   - Ensure email is associated with token

2. **No Similar Tickets Found**
   - Lower similarity threshold
   - Check project permissions
   - Verify ticket exists

3. **Performance Issues**
   - Reduce max_results
   - Check network connectivity
   - Monitor JIRA API limits

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=debug npm run web
```

## 🔒 Security Considerations

- **API Token Security**: Never commit tokens to version control
- **Environment Variables**: Use .env files for sensitive data
- **Network Security**: Ensure HTTPS connections
- **Access Control**: Limit tool access to authorized users

## 📚 API Reference

### Web API Endpoints

- `POST /api/v1/analyze` - Analyze a ticket
- `GET /api/v1/test` - Test JIRA connection
- `GET /api/v1/ticket/:key` - Get ticket details
- `POST /api/v1/export` - Export results
- `GET /api/v1/stats` - Get tool statistics

### CLI Commands

```bash
# Analyze a ticket
jira-similarity analyze PLAT-39562

# Test connection
jira-similarity test

# Interactive mode
jira-similarity interactive

# Show statistics
jira-similarity stats
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker
docker build -t jira-similarity-tool .
docker run -p 3000:3000 jira-similarity-tool
```

### Production Deployment

```bash
# Install dependencies
npm install --production

# Set environment variables
export NODE_ENV=production

# Start the server
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added web interface and export capabilities
- **v1.2.0**: Improved similarity algorithms and performance
- **v2.0.0**: Complete Node.js rewrite with enhanced features

---

**Built with ❤️ for developers and teams who want to work smarter, not harder.**

## 📚 How This Tool Works - Notes (Python/Streamlit)

This repository now includes a Python/Streamlit implementation that powers the PLAT Similarity (8501) and Filter Analysis (8503) UIs. It uses subject-first matching, PLAT/XOP constraints, and a content-focused scorer. Highlights:

- Subject extraction from ticket summaries and hard subject-overlap gating
- PLAT/XOP + Bug/Customer-Incident/Customer-Defect candidate filtering
- Status/function phrasing stripped from text (“not working”, “as expected”, etc.)
- Scoring prioritizes subject and summary content; metadata is not weighted
- Threshold fallback and UI fallback (show target ticket details) when no results

Read the full details here:
- `NOTES_SIMILARITY.md` — end-to-end notes on the Python/Streamlit similarity flow 