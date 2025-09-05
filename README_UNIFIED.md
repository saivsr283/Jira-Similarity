# 🔍 JIRA Unified Analyzer

A unified web application that provides both **PLAT Ticket Analysis** and **Dashboard Issue Grouping** in a single interface. This tool helps teams analyze individual tickets and group similar issues from dashboards.

## 🎯 Two Analysis Modes

### 📋 **PLAT Ticket Analysis**
- **Purpose**: Find similar tickets for a specific PLAT issue
- **Input**: Single JIRA ticket key (e.g., PLAT-45685)
- **Output**: List of similar tickets with similarity scores
- **Use Case**: When you have a specific issue and want to find related solutions

### 📊 **Dashboard Issue Grouping**
- **Purpose**: Group similar issues from a JIRA dashboard
- **Input**: Dashboard URL (e.g., https://koreteam.atlassian.net/jira/dashboards/26043)
- **Output**: Groups of similar tickets with pattern analysis
- **Use Case**: When you want to identify recurring problems across your dashboard

## 🚀 Quick Start

### 1. Start the Unified Server
```bash
./start.sh
```

### 2. Access the Application
Open your browser and go to: **http://localhost:8501**

### 3. Select Analysis Mode
In the sidebar, choose between:
- **PLAT Ticket Analysis** - for individual ticket analysis
- **Dashboard Issue Grouping** - for dashboard analysis

### 4. Configure Settings
- Enter your JIRA credentials (or leave blank to use config.json)
- Set project key (for PLAT mode) or dashboard URL (for Dashboard mode)
- Adjust similarity thresholds
- Set result limits

### 5. Run Analysis
- **PLAT Mode**: Enter ticket key and click "🔍 Analyze"
- **Dashboard Mode**: Click "🔍 Analyze Dashboard"

## 🔧 Features

### 🔍 **Smart Similarity Detection**
- **Content-based analysis**: Analyzes ticket summaries and descriptions
- **Keyword extraction**: Identifies technical terms and problem patterns
- **Jaccard similarity**: Mathematical similarity scoring
- **Configurable thresholds**: Adjust sensitivity levels

### 📊 **Pattern Recognition**
- **Issue type matching**: Groups similar bug types, features, tasks
- **Priority analysis**: Identifies patterns in priority levels
- **Component clustering**: Groups by affected components
- **Label analysis**: Uses JIRA labels for additional grouping

### 📈 **Export Capabilities**
- **JSON export**: Complete analysis data with metadata
- **CSV export**: Flattened data for spreadsheet analysis
- **Grouped results**: Organized by similarity groups
- **Timestamps**: Analysis date and time included

## 🎛️ Configuration

### JIRA Credentials
- **Username**: Your JIRA email address
- **API Token**: Your JIRA API token
- **URL**: Your JIRA instance URL

### PLAT Mode Settings
- **Project Key**: Usually "PLAT" for your project
- **Similarity Threshold**: 20% (default) - minimum similarity to include tickets
- **Max Results**: 10 (default) - maximum similar tickets to return

### Dashboard Mode Settings
- **Dashboard URL**: https://koreteam.atlassian.net/jira/dashboards/26043
- **Similarity Threshold**: 30% (default) - minimum similarity to group tickets
- **Max Tickets**: 50 (default) - maximum tickets to analyze

## 📋 How It Works

### PLAT Ticket Analysis Flow
1. **Input**: User enters a specific ticket key (e.g., PLAT-45685)
2. **Fetch**: Tool retrieves the target ticket details
3. **Search**: Finds similar tickets using JQL queries
4. **Analyze**: Calculates similarity scores using content analysis
5. **Display**: Shows similar tickets with detailed information
6. **Export**: Option to export results

### Dashboard Analysis Flow
1. **Input**: User provides dashboard URL
2. **Fetch**: Tool retrieves all tickets from the dashboard
3. **Group**: Groups tickets by content similarity
4. **Analyze**: Identifies common patterns and keywords
5. **Display**: Shows grouped tickets with similarity scores
6. **Export**: Option to export grouped results

## 🔍 Example Outputs

### PLAT Analysis Example
```
✅ Similar tickets fetched successfully! Found 8 similar tickets.

🎫 PLAT-45148 (85.2% Match)
Summary: DialogGPT API timeout during response generation
Status: Resolved | Priority: High | Type: Bug

🎫 PLAT-44923 (72.1% Match)
Summary: API response timeout in DialogGPT service
Status: In Progress | Priority: Medium | Type: Bug
```

### Dashboard Analysis Example
```
✅ Found 45 tickets in dashboard
✅ Found 8 groups of similar tickets

📋 Group #1 - 3 tickets (85.2% similarity)
Common Keywords: timeout, api, response, generation, dialoggpt

🎫 PLAT-45148: DialogGPT API timeout during response generation
🎫 PLAT-44923: API response timeout in DialogGPT service
🎫 PLAT-44789: DialogGPT generation timeout error
```

## 🛠️ Troubleshooting

### Common Issues

**"No tickets found"**
- Check JIRA credentials are correct
- Verify you have access to the project/dashboard
- Ensure the ticket key or dashboard URL is valid

**"No similar tickets/groups found"**
- Lower the similarity threshold
- Check if tickets have meaningful summaries
- Try analyzing more tickets (Dashboard mode)

**"Authentication failed"**
- Verify JIRA credentials
- Check API token permissions
- Ensure username is email format

### Performance Tips

- **Lower thresholds** for more results
- **Increase thresholds** for more relevant results
- **Limit max tickets** for faster analysis
- **Use specific URLs** rather than general queries

## 📤 Export Formats

### JSON Export
```json
{
  "analysis_mode": "PLAT",
  "ticket_key": "PLAT-45685",
  "analysis_date": "2025-09-04T08:30:00",
  "similarity_threshold": 0.2,
  "total_results": 8,
  "results": [...]
}
```

### CSV Export
**PLAT Mode**: Ticket_Key, Summary, Status, Priority, Issue_Type, Assignee, Reporter, Similarity_Score

**Dashboard Mode**: Group_ID, Ticket_Position, Ticket_Key, Summary, Status, Priority, Issue_Type, Assignee, Reporter, Created, Components, Labels

## 🔗 Integration

### JIRA Integration
- **REST API**: Uses official JIRA REST API
- **Authentication**: Supports username/token auth
- **Permissions**: Respects JIRA access controls
- **Real-time**: Fetches latest data from JIRA

### Team Workflows
1. **Daily standup**: Review grouped issues (Dashboard mode)
2. **Ticket analysis**: Find similar solutions (PLAT mode)
3. **Sprint planning**: Identify recurring problems
4. **Retrospectives**: Analyze patterns over time

## 🚀 Advanced Usage

### Switching Between Modes
1. Use the mode selector in the sidebar
2. Configure mode-specific settings
3. Run analysis for each mode independently
4. Export results in different formats

### Custom Analysis
1. Export results as JSON/CSV
2. Use external tools for further analysis
3. Import into BI tools for visualization
4. Create automated reports

### Team Collaboration
1. **Share findings**: Export and share analysis results
2. **Document patterns**: Use grouped results for documentation
3. **Improve processes**: Identify recurring issues
4. **Knowledge sharing**: Learn from similar solved issues

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review JIRA API documentation
- Verify network connectivity to JIRA
- Check container logs: `docker logs jira-unified-web`

---

**JIRA Unified Analyzer** - One tool, two powerful analysis modes! 🔍✨ 