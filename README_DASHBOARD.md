# 📊 JIRA Dashboard Analyzer

A specialized tool for analyzing JIRA dashboard tickets and grouping similar issues together. This tool helps teams identify patterns, recurring problems, and similar tickets across their dashboard.

## 🎯 Purpose

The Dashboard Analyzer is designed to:
- **Group similar tickets** from your JIRA dashboard
- **Identify recurring problems** and patterns
- **Improve team collaboration** by highlighting related issues
- **Export findings** for further analysis

## 🚀 Quick Start

### 1. Start the Dashboard Analyzer
```bash
./start_dashboard.sh
```

### 2. Access the Application
Open your browser and go to: **http://localhost:8502**

### 3. Configure Settings
- Enter your JIRA credentials (or leave blank to use config.json)
- Set the dashboard URL: `https://koreteam.atlassian.net/jira/dashboards/26043`
- Adjust similarity threshold (default: 30%)
- Set maximum tickets to analyze

### 4. Analyze Dashboard
Click "🔍 Analyze Dashboard" to start the analysis.

## 🔧 Features

### 📊 Smart Grouping
- **Content-based similarity**: Analyzes ticket summaries and descriptions
- **Keyword extraction**: Identifies common technical terms and problem patterns
- **Jaccard similarity**: Uses mathematical similarity scoring
- **Configurable threshold**: Adjust how strict the grouping should be

### 🏷️ Pattern Recognition
- **Issue type matching**: Groups similar bug types, features, tasks
- **Priority analysis**: Identifies patterns in priority levels
- **Component clustering**: Groups tickets by affected components
- **Label analysis**: Uses JIRA labels for additional grouping

### 📈 Export Capabilities
- **JSON export**: Complete analysis data with metadata
- **CSV export**: Flattened data for spreadsheet analysis
- **Grouped results**: Organized by similarity groups
- **Timestamps**: Analysis date and time included

## 🎛️ Configuration

### Dashboard URL
The default dashboard URL is: `https://koreteam.atlassian.net/jira/dashboards/26043`

You can change this to any JIRA dashboard URL in the format:
```
https://your-domain.atlassian.net/jira/dashboards/DASHBOARD_ID
```

### Similarity Threshold
- **30% (default)**: Balanced grouping, catches most related issues
- **50%**: Strict grouping, only very similar tickets
- **20%**: Loose grouping, includes more potential matches

### Max Tickets
- **50 (default)**: Good balance for analysis speed
- **100+**: More comprehensive analysis, slower processing
- **20**: Quick analysis, fewer results

## 📋 How It Works

### 1. Dashboard Access
The tool connects to your JIRA instance and fetches tickets from the specified dashboard using the JIRA REST API.

### 2. Content Analysis
For each ticket, it:
- Extracts keywords from summaries and descriptions
- Removes common stop words
- Identifies technical terms and problem patterns
- Normalizes text for comparison

### 3. Similarity Calculation
Uses Jaccard similarity to compare tickets:
```
Similarity = (Common Keywords) / (Total Unique Keywords)
```

### 4. Grouping Algorithm
- Starts with the first ungrouped ticket
- Finds all tickets with similarity ≥ threshold
- Creates a group and marks tickets as used
- Repeats until all tickets are processed

### 5. Results Display
- Shows grouped tickets with similarity scores
- Highlights common keywords and patterns
- Provides export options for further analysis

## 🔍 Example Output

### Group #1 - 3 tickets (85.2% similarity)
**Common Keywords:** timeout, api, response, generation, dialoggpt

**Tickets:**
- 🎫 PLAT-45148: DialogGPT API timeout during response generation
- 🎫 PLAT-44923: API response timeout in DialogGPT service
- 🎫 PLAT-44789: DialogGPT generation timeout error

## 🛠️ Troubleshooting

### Common Issues

**"No tickets found in dashboard"**
- Check dashboard URL is correct
- Verify you have access to the dashboard
- Ensure dashboard contains tickets

**"No similar groups found"**
- Lower the similarity threshold
- Check if tickets have meaningful summaries
- Try analyzing more tickets

**"Authentication failed"**
- Verify JIRA credentials
- Check API token permissions
- Ensure username is email format

### Performance Tips

- **Lower max tickets** for faster analysis
- **Increase similarity threshold** for fewer, more relevant groups
- **Use specific dashboard URLs** rather than general project queries

## 📤 Export Formats

### JSON Export
```json
{
  "dashboard_url": "https://koreteam.atlassian.net/jira/dashboards/26043",
  "analysis_date": "2025-09-04T08:30:00",
  "similarity_threshold": 0.3,
  "total_tickets": 45,
  "total_groups": 8,
  "groups": [...]
}
```

### CSV Export
Columns: Group_ID, Ticket_Position, Ticket_Key, Summary, Status, Priority, Issue_Type, Assignee, Reporter, Created, Components, Labels

## 🔗 Integration

### With Existing PLAT Tool
- **Separate ports**: Dashboard (8502) vs PLAT (8501)
- **Shared configuration**: Uses same config.json
- **Independent operation**: Can run both simultaneously

### JIRA Integration
- **REST API**: Uses official JIRA REST API
- **Authentication**: Supports username/token auth
- **Permissions**: Respects JIRA access controls

## 🚀 Advanced Usage

### Custom Analysis
1. Export results as JSON
2. Use external tools for further analysis
3. Import into BI tools for visualization
4. Create automated reports

### Team Workflows
1. **Daily standup**: Review grouped issues
2. **Sprint planning**: Identify recurring problems
3. **Retrospectives**: Analyze patterns over time
4. **Knowledge sharing**: Document common solutions

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review JIRA API documentation
- Verify network connectivity to JIRA
- Check container logs: `docker logs jira-dashboard-web`

---

**Dashboard Analyzer** - Making JIRA insights accessible and actionable! 📊✨ 