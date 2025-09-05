# JIRA Similarity Analysis Tool (Python)

A Python-based tool for analyzing JIRA tickets and finding similar tickets based on content similarity, issue type, priority, and components.

## Features

- **Content Analysis**: Analyzes ticket summaries and descriptions using keyword extraction
- **Similarity Scoring**: Uses Jaccard similarity with weighted factors for issue type, priority, and components
- **Flexible Search**: Supports custom JQL queries for ticket comparison
- **Multiple Output Formats**: Command-line interface and programmatic API
- **Configurable Thresholds**: Adjustable similarity thresholds and result limits

## Installation

1. **Clone or download the tool**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Option 1: Environment Variables
Set these environment variables:
```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"
```

### Option 2: Configuration File
Create a `config.json` file:
```json
{
  "jira_url": "https://your-company.atlassian.net",
  "username": "your-email@company.com",
  "api_token": "your-jira-api-token"
}
```

## Usage

### Command Line Interface

**Basic usage**:
```bash
python jira_similarity_tool.py PLAT-45148
```

**Advanced usage**:
```bash
python jira_similarity_tool.py PLAT-45148 \
  --jql "project = PLAT AND status != Closed" \
  --threshold 0.5 \
  --max-results 20 \
  --output results.json
```

**Command line options**:
- `ticket_key`: The JIRA ticket key to analyze
- `--config`: Path to configuration file
- `--jql`: Custom JQL query for searching tickets
- `--threshold`: Similarity threshold (0.0-1.0, default: 0.3)
- `--max-results`: Maximum number of similar tickets (default: 10)
- `--output`: Output file for results

### Programmatic Usage

```python
from jira_similarity_tool import JIRASimilarityTool

# Initialize the tool
tool = JIRASimilarityTool('config.json')

# Analyze a ticket
results = tool.analyze_ticket(
    ticket_key='PLAT-45148',
    search_jql='project = PLAT AND status != Closed',
    threshold=0.3,
    max_results=10
)

# Print results
print(f"Target Ticket: {results['target_ticket']['key']}")
print(f"Summary: {results['target_ticket']['summary']}")

for ticket in results['similar_tickets']:
    print(f"{ticket['key']}: {ticket['similarity_score']}")
    print(f"  Summary: {ticket['summary']}")
    print(f"  URL: {ticket['url']}")
```

## How It Works

### Similarity Algorithm

1. **Text Preprocessing**: 
   - Converts text to lowercase
   - Removes special characters
   - Filters out stop words

2. **Keyword Extraction**: 
   - Extracts meaningful keywords from summaries and descriptions
   - Removes common stop words and short words

3. **Similarity Calculation**:
   - **Jaccard Similarity** (60% weight): Based on keyword overlap
   - **Issue Type Similarity** (20% weight): Exact match for issue types
   - **Priority Similarity** (10% weight): Exact match for priorities
   - **Component Similarity** (10% weight): Overlap in components

### Example Output

```
Target Ticket: PLAT-45148
Summary: Fix authentication issue in login module
Type: Bug
Priority: High
Status: In Progress

Found 5 similar tickets:
1. PLAT-45150 (Similarity: 0.85)
   Summary: Authentication bug in user login
   Type: Bug, Priority: High, Status: Open
   URL: https://your-company.atlassian.net/browse/PLAT-45150

2. PLAT-45145 (Similarity: 0.72)
   Summary: Login module not working properly
   Type: Bug, Priority: Medium, Status: In Progress
   URL: https://your-company.atlassian.net/browse/PLAT-45145
```

## API Reference

### JIRASimilarityTool

Main class for JIRA similarity analysis.

#### Methods

- `__init__(config_file=None)`: Initialize the tool
- `analyze_ticket(ticket_key, search_jql=None, threshold=0.3, max_results=10)`: Analyze a ticket and find similar tickets
- `export_results(results, output_file)`: Export results to JSON file

### JIRAClient

Client for interacting with JIRA API.

#### Methods

- `get_ticket(ticket_key)`: Fetch a single JIRA ticket
- `search_tickets(jql, max_results=100)`: Search for tickets using JQL

### SimilarityAnalyzer

Analyzes similarity between JIRA tickets.

#### Methods

- `calculate_similarity(ticket1, ticket2)`: Calculate similarity score between two tickets
- `find_similar_tickets(target_ticket, all_tickets, threshold=0.3, max_results=10)`: Find tickets similar to target

## Examples

### Example 1: Find similar bugs
```bash
python jira_similarity_tool.py PLAT-45148 \
  --jql "project = PLAT AND issuetype = Bug" \
  --threshold 0.4
```

### Example 2: Compare with recent tickets
```bash
python jira_similarity_tool.py PLAT-45148 \
  --jql "project = PLAT AND created >= -30d" \
  --max-results 15
```

### Example 3: High similarity only
```bash
python jira_similarity_tool.py PLAT-45148 \
  --threshold 0.7 \
  --max-results 5
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your JIRA URL, username, and API token
2. **No Results**: Try lowering the similarity threshold or expanding the JQL search
3. **Rate Limiting**: The tool respects JIRA API rate limits

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 