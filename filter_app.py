import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from collections import defaultdict
import pandas as pd
from jira_similarity_tool import JIRASimilarityTool, JIRAClient
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid
from urllib.parse import quote

# Page configuration
st.set_page_config(
    page_title="JIRA Filter Analyzer",
    page_icon="",
    layout="wide"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .hero-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .hero-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .modern-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }
    .category-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .ticket-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .similarity-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
    .high-similarity { background-color: #28a745; }
    .medium-similarity { background-color: #ffc107; color: #000; }
    .low-similarity { background-color: #dc3545; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
</style>
""", unsafe_allow_html=True)

def save_config(config_data: Dict[str, str]) -> tuple[bool, str]:
    """Save configuration to file"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        return True, "✅ Configuration saved successfully!"
    except Exception as e:
        return False, f"❌ Failed to save configuration: {e}"

def get_status_color(status: str) -> str:
    """Get color for status"""
    status_lower = status.lower()
    if 'open' in status_lower or 'to do' in status_lower:
        return '#007bff'
    elif 'in progress' in status_lower or 'progress' in status_lower:
        return '#ffc107'
    elif 'done' in status_lower or 'closed' in status_lower or 'resolved' in status_lower:
        return '#28a745'
    elif 'blocked' in status_lower or 'block' in status_lower:
        return '#dc3545'
    else:
        return '#6c757d'

def get_priority_color(priority: str) -> str:
    """Get color for priority"""
    priority_lower = priority.lower()
    if 'high' in priority_lower:
        return '#dc3545'
    elif 'medium' in priority_lower:
        return '#ffc107'
    elif 'low' in priority_lower:
        return '#28a745'
    else:
        return '#6c757d'

def categorize_ticket(ticket: Dict) -> str:
    """Categorize ticket based on summary and description"""
    summary = ticket.get('summary', '').lower()
    description = ticket.get('description', '').lower()
    combined_text = f"{summary} {description}"
    
    # Define category keywords
    categories = {
        'DialogGPT': ['dialoggpt', 'dialog gpt', 'chatgpt', 'conversational ai', 'ai chat', 'gpt', 'openai'],
        'Language Switch': ['language switch', 'language switching', 'multilingual', 'language change', 'locale', 'translation'],
        'Session Closure': ['session closure', 'session close', 'session timeout', 'session end', 'logout', 'session management'],
        'Authentication': ['authentication', 'auth', 'login', 'logout', 'password', 'credentials', 'token'],
        'Performance': ['performance', 'slow', 'timeout', 'latency', 'response time', 'speed'],
        'API Issues': ['api', 'rest api', 'endpoint', 'http', 'request', 'response'],
        'Database': ['database', 'db', 'sql', 'query', 'connection', 'data'],
        'UI/UX': ['ui', 'ux', 'interface', 'frontend', 'user interface', 'display', 'visual'],
        'Integration': ['integration', 'webhook', 'third party', 'external', 'connector'],
        'Deployment': ['deployment', 'deploy', 'release', 'production', 'staging', 'environment']
    }
    
    # Find matching category
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in combined_text:
                return category
    
    return 'Other'

def suggest_simplified_jql(original_jql):
    """Suggest simplified JQL queries when the original fails"""
    suggestions = [
        {
            "name": "Basic PLAT Issues",
            "query": "project = PLAT ORDER BY created DESC",
            "description": "All PLAT issues, ordered by creation date"
        },
        {
            "name": "PLAT Open Issues",
            "query": "project = PLAT AND status != Closed ORDER BY created DESC",
            "description": "All non-closed PLAT issues"
        },
        {
            "name": "PLAT Recent Issues",
            "query": "project = PLAT AND created >= 2024-01-01 ORDER BY created DESC",
            "description": "PLAT issues created since 2024"
        },
        {
            "name": "PLAT Bug Issues",
            "query": "project = PLAT AND issuetype = Bug ORDER BY created DESC",
            "description": "All PLAT bug issues"
        },
        {
            "name": "PLAT Customer Issues",
            "query": "project = PLAT AND (issuetype = Customer-Defect OR issuetype = Customer-Incident) ORDER BY created DESC",
            "description": "PLAT customer defect and incident issues"
        },
        {
            "name": "Your Query Simplified",
            "query": "project = PLAT AND issuetype in (Bug, \"Incident Analysis\", Customer-Defect, Customer-Incident) AND created >= 2024-01-01 AND status not in (Closed, \"Staging Validated\", \"QA VALIDATED\", \"Ready for QA\", \"Successfully Deployed\") ORDER BY created ASC",
            "description": "Simplified version of your complex query - removed custom fields and duplicates"
        }
    ]
    return suggestions

def fetch_filtered_tickets(jira_client, jql):
    """Fetch tickets using JQL query"""
    try:
        response = jira_client.session.get(
            f"{jira_client.base_url}/rest/api/3/search/jql",
            params={
                'jql': jql,
                'maxResults': 1000,
                'fields': 'summary,status,assignee,reporter,created,priority,issuetype'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('issues', [])
        else:
            st.error(f"Failed to fetch tickets: {response.status_code}")
            if response.status_code == 410:
                st.error(f"410 error: Invalid JQL syntax. Query that failed: {jql}")
                st.error("Please check your query syntax.")
                
                # Show suggestions for simplified queries
                st.markdown("### 💡 Try these simplified queries instead:")
                suggestions = suggest_simplified_jql(jql)
                
                for suggestion in suggestions:
                    with st.expander(f"🔍 {suggestion['name']}"):
                        st.write(f"**Description:** {suggestion['description']}")
                        st.code(suggestion['query'], language="sql")
                        if st.button(f"Use this query", key=f"use_{suggestion['name']}"):
                            st.session_state.suggested_jql = suggestion['query']
                            st.rerun()
                
                st.info("💡 **Common JQL syntax tips:**")
                st.info("- Use 'project = PLAT' for specific project")
                st.info("- Use 'status != Closed' for non-closed issues")
                st.info("- Use 'issuetype = Bug' for specific issue types")
                st.info("- Use 'created >= 2024-01-01' for date filters")
                st.info("- Use 'assignee = \"username\"' for specific assignee")
                st.info("- Use 'priority = High' for priority filters")
                st.info("- Avoid complex custom field names with special characters")
            elif response.status_code == 403:
                st.error("403 error: Access denied. Check your permissions.")
            elif response.status_code == 401:
                st.error("401 error: Authentication failed. Check your credentials.")
            return []
            
    except Exception as e:
        st.error(f"Error fetching tickets: {str(e)}")
        return []

def calculate_similarity_groups(tickets, similarity_threshold=0.3):
    """Group tickets based on summary similarity"""
    if not tickets or len(tickets) < 2:
        return []
    
    # Extract summaries
    summaries = []
    for ticket in tickets:
        summary = ticket.get('fields', {}).get('summary', '')
        summaries.append(summary)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(summaries)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Group similar tickets
        groups = []
        used_indices = set()
        
        for i in range(len(tickets)):
            if i in used_indices:
                continue
                
            # Find similar tickets
            similar_indices = [i]
            used_indices.add(i)
            
            for j in range(i + 1, len(tickets)):
                if j not in used_indices and similarity_matrix[i][j] >= similarity_threshold:
                    similar_indices.append(j)
                    used_indices.add(j)
            
            if len(similar_indices) > 1:  # Only create groups with multiple tickets
                group_tickets = [tickets[idx] for idx in similar_indices]
                avg_similarity = np.mean([similarity_matrix[i][j] for j in similar_indices if j != i])
                groups.append({
                    'tickets': group_tickets,
                    'size': len(group_tickets),
                    'avg_similarity': avg_similarity,
                    'representative_summary': summaries[i]  # Use first ticket as representative
                })
        
        # Sort groups by size (largest first)
        groups.sort(key=lambda x: x['size'], reverse=True)
        return groups
        
    except Exception as e:
        st.error(f"Error calculating similarity: {str(e)}")
        return []

def display_similarity_groups(groups, jira_client=None, similarity_threshold=0.3):
    """Display similarity groups in a compact table format and allow per-group global similarity search"""
    if not groups:
        st.info("ℹ️ **No similar ticket groups found with the current threshold.**")
        return
    
    st.markdown(f"""
    <div style="background-color: #27ae60; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-weight: bold;">
        ✅ Found {len(groups)} groups of similar tickets!
    </div>
    """, unsafe_allow_html=True)

    # Stable keys needed across reruns for button click detection
    
    # Show detailed tickets for each group in expandable sections
    for i, group in enumerate(groups, 1):
        # Determine saved results and open state before rendering header
        group_state_key = f"group_sim_{i}"
        saved = st.session_state.get(group_state_key, {}) if jira_client is not None else {}
        is_open = bool(saved) or bool(st.session_state.get(f'group_open_{i}', False))
        icon_char = '▼' if is_open else '▶'
        content_display = 'block' if is_open else 'none'

        # Create custom header and container
        st.markdown(f"""
        <div id="group-{i}-header" style="background-color: #3498db; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-weight: bold; cursor: pointer; border: 1px solid #2980b9;" onclick="toggleGroup({i})">
            🔍 Group {i} Details ({len(group['tickets'])} tickets) <span id="group-{i}-icon" style="float: right; font-size: 16px;">{icon_char}</span>
        </div>
        <div id="group-{i}-content" style="display: {content_display};">
        """, unsafe_allow_html=True)
        
        # Create a simple table for tickets in this group
        tickets_data = []
        for j, ticket in enumerate(group['tickets'], 1):
            fields = ticket.get('fields', {})
            
            ticket_key = ticket['key']
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown')
            issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
            assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
            priority = fields.get('priority', {}).get('name', 'Unknown')
            created = fields.get('created', 'Unknown')
            
            if created and created != 'Unknown':
                created_date = created[:10]
            else:
                created_date = 'Unknown'
            
            # Truncate summary
            if len(summary) > 60:
                summary = summary[:57] + "..."
            
            tickets_data.append({
                '#': j,
                'Ticket': ticket_key,
                'Summary': summary,
                'Status': status,
                'Type': issue_type,
                'Assignee': assignee,
                'Priority': priority,
                'Created': created_date
            })
        
        # Display tickets table for this group
        tickets_df = pd.DataFrame(tickets_data)
        st.dataframe(tickets_df, use_container_width=True, hide_index=True)
        
        # Per-group similar tickets (global search) - manual trigger
        if jira_client is not None:
            if group_state_key not in st.session_state:
                st.session_state[group_state_key] = {}
            
            # Unique key per render and group to avoid duplicate keys
            group_key = f"btn_group_sim_{i}"
            if st.button(f"🔁 Find similar tickets for Group {i}", key=group_key):
                try:
                    tool = JIRASimilarityTool()
                    # Ensure tool has both client and config for URL building
                    tool.jira_client = jira_client
                    if not getattr(tool, 'config', None):
                        tool.config = {'jira_url': jira_client.base_url}
                    elif 'jira_url' not in tool.config:
                        tool.config['jira_url'] = jira_client.base_url
                    
                    group_results = {}
                    # Limit per group to avoid excessive calls
                    for ticket in group['tickets'][:3]:
                        base_key = ticket['key']
                        sims = tool.analyze_similarity(base_key, threshold=similarity_threshold, max_results=5)
                        group_results[base_key] = sims
                    st.session_state[group_state_key] = group_results
                    # Keep group open after rerun
                    st.session_state[f'group_open_{i}'] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error finding similar tickets for group {i}: {e}")
            
            # Render saved results
            saved = st.session_state.get(group_state_key, {})
            if saved:
                st.markdown(f"<div style=\"margin-top: 8px; font-weight: bold;\">🔗 Similar tickets from overall JIRA</div>", unsafe_allow_html=True)
                for base_key, sims in saved.items():
                    with st.expander(f"{base_key} — Top similar tickets ({len(sims)})", expanded=False):
                        sim_rows = []
                        for s in sims:
                            # Support both structures: {'ticket': JIRATicket, 'similarity_score': ...}
                            # and flattened dict from analyze_similarity
                            score = s.get('similarity_score', 0)
                            t = s.get('ticket')
                            if t:
                                ticket_key = getattr(t, 'key', '')
                                summary = getattr(t, 'summary', '')
                                status_val = getattr(t, 'status', '')
                                type_val = getattr(t, 'issue_type', '')
                                priority_val = getattr(t, 'priority', '')
                                created_val = getattr(t, 'created', '')
                            else:
                                ticket_key = s.get('key', '')
                                summary = s.get('summary', '')
                                status_val = s.get('status', '')
                                type_val = s.get('issue_type', '')
                                priority_val = s.get('priority', '')
                                created_val = s.get('created', '')
                            if ticket_key:
                                trimmed = summary[:80] + ('...' if len(summary) > 80 else '')
                                sim_rows.append({
                                    'Ticket': ticket_key,
                                    'Summary': trimmed,
                                    'Score': round(score * 100, 1),
                                    'Status': status_val,
                                    'Type': type_val,
                                    'Priority': priority_val,
                                    'Created': created_val[:10] if created_val else ''
                                })
                        if sim_rows:
                            sim_df = pd.DataFrame(sim_rows)
                            st.dataframe(sim_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No similar tickets found for this ticket.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add JavaScript for group toggles
    st.markdown("""
    <script>
    function toggleGroup(groupNum) {
        var content = document.getElementById('group-' + groupNum + '-content');
        var icon = document.getElementById('group-' + groupNum + '-icon');
        if (content.style.display === 'none') {
            content.style.display = 'block';
            icon.textContent = '▼';
        } else {
            content.style.display = 'none';
            icon.textContent = '▶';
        }
    }
    </script>
    """, unsafe_allow_html=True)

def display_tickets(tickets):
    """Display tickets in a compact table format"""
    if not tickets:
        return
    
    # Create a compact table using pandas DataFrame
    import pandas as pd
    
    # Prepare data for table
    table_data = []
    for i, ticket in enumerate(tickets, 1):
        fields = ticket.get('fields', {})
        
        # Extract ticket information
        ticket_key = ticket['key']
        summary = fields.get('summary', 'No summary')
        status = fields.get('status', {}).get('name', 'Unknown')
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
        priority = fields.get('priority', {}).get('name', 'Unknown')
        created = fields.get('created', 'Unknown')
        
        # Format date
        if created and created != 'Unknown':
            created_date = created[:10]
        else:
            created_date = 'Unknown'
        
        # Truncate summary if too long
        if len(summary) > 60:
            summary = summary[:57] + "..."
        
        table_data.append({
            '#': i,
            'Ticket': ticket_key,
            'Summary': summary,
            'Status': status,
            'Type': issue_type,
            'Assignee': assignee,
            'Priority': priority,
            'Created': created_date
        })
    
    # Create DataFrame and display as table
    df = pd.DataFrame(table_data)
    
    # Apply custom styling to the table
    st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }
    .dataframe th {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border: 1px solid #2980b9;
    }
    .dataframe td {
        padding: 10px;
        border: 1px solid #dee2e6;
        background-color: #ffffff;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .dataframe tr:hover {
        background-color: #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_ticket_card(ticket, position, group_num):
    """Display a single ticket card with enhanced styling"""
    fields = ticket.get('fields', {})
    
    # Extract ticket information
    ticket_key = ticket['key']
    summary = fields.get('summary', 'No summary')
    status = fields.get('status', {}).get('name', 'Unknown')
    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
    reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'Unknown')
    created = fields.get('created', 'Unknown')
    
    # Format date
    if created and created != 'Unknown':
        created_date = created[:10]
    else:
        created_date = 'Unknown'
    
    # Status color mapping
    status_colors = {
        'Open': '#3498db',
        'In Progress': '#f39c12',
        'Analysis in Progress': '#f39c12',
        'Development In Progress': '#f39c12',
        'Closed': '#27ae60',
        'Resolved': '#27ae60'
    }
    
    # Priority color mapping
    priority_colors = {
        'High': '#e74c3c',
        'Medium': '#f39c12',
        'Low': '#27ae60',
        'Highest': '#e74c3c',
        'Lowest': '#27ae60'
    }
    
    status_color = status_colors.get(status, '#95a5a6')
    priority_color = priority_colors.get(priority, '#95a5a6')
    
    # Start ticket card
    st.markdown(f"""
    <div class="ticket-card">
        <div class="ticket-header">🎫 Ticket {position}: {ticket_key} - {summary}</div>
    """, unsafe_allow_html=True)
    
    # Position indicator
    st.markdown(f"""
    <div class="position-indicator">Position: #{position} in Group {group_num}</div>
    """, unsafe_allow_html=True)
    
    # Ticket details
    st.markdown(f"""
    <div class="ticket-details">
        <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
            <div><strong>Status:</strong> <span class="status-badge" style="background: {status_color};">{status}</span></div>
            <div><strong>Type:</strong> {issue_type}</div>
            <div><strong>Assignee:</strong> {assignee}</div>
            <div><strong>Created:</strong> {created_date}</div>
            <div><strong>Reporter:</strong> {reporter}</div>
            <div><strong>Priority:</strong> <span class="priority-badge" style="background: {priority_color};">{priority}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ticket summary
    st.markdown(f"""
    <div class="ticket-summary">
        <strong>Summary:</strong> {summary}
    </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Add JavaScript for individual tickets toggle (always available)
    st.markdown("""
    <script>
    function toggleIndividualTickets() {
        var content = document.getElementById('individual-tickets-content');
        var icon = document.getElementById('toggle-icon');
        if (content && icon) {
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                icon.textContent = '▼';
            } else {
                content.style.display = 'none';
                icon.textContent = '▶';
            }
        }
    }
    </script>
    """, unsafe_allow_html=True)

    # Page hero header
    st.markdown("""
    <div class="hero-header">
        <h1>🔍 JIRA Filter Analyzer</h1>
        <p>Analyze JIRA tickets with custom JQL queries and similarity grouping</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        st.error("❌ config.json not found. Please ensure the configuration file exists.")
        return
    
    # Credentials from UI
    st.sidebar.markdown("### 🔐 JIRA Credentials")
    ui_username = st.sidebar.text_input("Username (email)", value=config.get('username', '') or '')
    ui_token = st.sidebar.text_input("API Token", type="password", value="", placeholder="Paste your token")

    # Initialize JIRA client
    try:
        jira_url = config.get('jira_url') or os.getenv('JIRA_URL', 'https://koreteam.atlassian.net')
        username = ui_username or os.getenv('JIRA_USERNAME', '')
        api_token = ui_token
        if not api_token:
            st.error("❌ JIRA API token is required. Please enter it in the sidebar.")
            return
        jira_client = JIRAClient(
            jira_url,
            username,
            api_token
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize JIRA client: {str(e)}")
        return
    
    # Sidebar for similarity settings
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>⚙️ Similarity Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.3,
            step=0.1,
            help="Higher values = more strict similarity matching"
        )
        
        # Detect threshold change and reset analysis state
        prev_threshold = st.session_state.get('prev_threshold')
        if prev_threshold is None:
            st.session_state['prev_threshold'] = similarity_threshold
        else:
            if similarity_threshold != prev_threshold:
                # Clear group-level cached similar results
                keys_to_clear = [k for k in st.session_state.keys() if str(k).startswith('group_sim_')]
                for k in keys_to_clear:
                    del st.session_state[k]
                # Reset group analysis and UI toggles
                st.session_state['last_groups'] = []
                st.session_state['last_groups_threshold'] = None
                st.session_state['individual_open'] = False
                # Mark change
                st.session_state['threshold_changed'] = True
                st.session_state['prev_threshold'] = similarity_threshold
        
        # Simple threshold indicator
        if similarity_threshold > 0.7:
            threshold_color = "#e74c3c"
            threshold_text = "Strict"
        elif similarity_threshold > 0.4:
            threshold_color = "#f39c12"
            threshold_text = "Balanced"
        else:
            threshold_color = "#27ae60"
            threshold_text = "Loose"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; background: {threshold_color}; color: white; border-radius: 5px; margin: 0.5rem 0; font-weight: bold;">
            <strong>Threshold: {similarity_threshold}</strong><br>
            <small>{threshold_text} Grouping</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4>💡 Tips</h4>
            <ul>
                <li><strong>0.1-0.3:</strong> Loose grouping (more groups)</li>
                <li><strong>0.4-0.6:</strong> Balanced grouping</li>
                <li><strong>0.7-0.9:</strong> Strict grouping (fewer groups)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Single Ticket Similarity quick link
        st.markdown("""
        <div class="sidebar-section">
            <h3>🔎 Single Ticket Similarity</h3>
        </div>
        """, unsafe_allow_html=True)
        single_ticket_key = st.text_input("Ticket Key (e.g., PLAT-12345)", key="single_ticket_key")
        # If deployed in Streamlit Cloud, use the cloud URL; else default to localhost
        try:
            cloud_url = (st.secrets["SIMILARITY_APP_URL"].strip() if "SIMILARITY_APP_URL" in st.secrets else "")
        except Exception:
            cloud_url = ""
        base_url = cloud_url or "http://localhost:8501"
        if single_ticket_key.strip():
            similarity_url = f"{base_url}/?ticket={quote(single_ticket_key.strip())}"
        else:
            similarity_url = base_url
        try:
            st.link_button("Open Similarity Tool", similarity_url, use_container_width=True)
        except Exception:
            st.markdown(f"<a href=\"{similarity_url}\" target=\"_blank\" style=\"display:inline-block;padding:0.5rem 1rem;border-radius:6px;background:#3498db;color:#fff;text-decoration:none;text-align:center;width:100%;\">Open Similarity Tool</a>", unsafe_allow_html=True)

    # JQL Query Input with simple styling
    st.markdown("""
    <div class="query-section">
        <h3>📝 Enter JQL Query</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if there's a suggested query from session state
    default_query = st.session_state.get('suggested_jql', '')
    
    jql_query = st.text_area(
        "Enter your JQL query:",
        value=default_query,
        height=80,
        placeholder="Example: project = ZTP AND status != Closed ORDER BY created DESC"
    )
    
    # Enhanced button with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Fetch & Analyze Tickets", type="primary", use_container_width=True)
    
    if analyze_button:
        if not jql_query.strip():
            st.warning("⚠️ Please enter a JQL query.")
        
        else:
            st.info(f"🔍 **Fetching tickets with JQL:** {jql_query}")
            
            # Fetch tickets using the JQL query
            tickets = fetch_filtered_tickets(jira_client, jql_query)
            
            # Persist tickets for rendering outside of the button run
            st.session_state['last_tickets'] = tickets or []

    # Render from session state so UI persists across reruns
    tickets_to_render = st.session_state.get('last_tickets', [])
    if tickets_to_render:
        st.markdown(f"""
        <div style=\"background-color: #27ae60; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-weight: bold;\">
            ✅ Found {len(tickets_to_render)} tickets!
        </div>
        """, unsafe_allow_html=True)
        
        # If threshold changed, ask for re-analysis and do not show old groups
        if st.session_state.get('threshold_changed'):
            st.warning("Similarity threshold changed. Click '🔍 Fetch & Analyze Tickets' to recompute groups.")
            # Optional quick action: recompute groups with current tickets
            if len(tickets_to_render) > 1:
                if st.button("🔁 Recompute groups", key="recompute_groups"):
                    groups = calculate_similarity_groups(tickets_to_render, similarity_threshold)
                    st.session_state['last_groups'] = groups
                    st.session_state['last_groups_threshold'] = similarity_threshold
                    st.session_state['threshold_changed'] = False
                    st.rerun()
        
        if len(tickets_to_render) > 1:
            # Show previous analysis if available
            last_groups = [] if st.session_state.get('threshold_changed') else st.session_state.get('last_groups', [])
            last_threshold = st.session_state.get('last_groups_threshold')
            if last_groups:
                st.markdown(f"""
                <div style=\"background-color: #3498db; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-weight: bold;\">
                    🔍 Showing {len(last_groups)} groups analyzed at threshold {last_threshold}.
                </div>
                """, unsafe_allow_html=True)
                display_similarity_groups(last_groups, jira_client, last_threshold)
            else:
                st.info("ℹ️ No analysis yet. Set a threshold and click Analyze.")

            # Analyze automatically only when explicitly fetched (no extra Analyze button)
            if not st.session_state.get('threshold_changed') and not st.session_state.get('last_groups'):
                groups = calculate_similarity_groups(tickets_to_render, similarity_threshold)
                st.session_state['last_groups'] = groups
                st.session_state['last_groups_threshold'] = similarity_threshold
                if groups:
                    display_similarity_groups(groups, jira_client, similarity_threshold)
                else:
                    st.info("ℹ️ No similar ticket groups found with the current threshold.")
        else:
            st.markdown("""
            <div style=\"background-color: #3498db; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-weight: bold;\">
                ℹ️ Only 1 ticket found - no similarity analysis needed.
            </div>
            """, unsafe_allow_html=True)
        
        # Reliable toggle for individual tickets using session state
        if 'individual_open' not in st.session_state:
            st.session_state['individual_open'] = False
        
        icon = "▼" if st.session_state['individual_open'] else "▶"
        label = f"📋 All Individual Tickets {icon}"
        if st.button(label, key="toggle_individual", use_container_width=True):
            st.session_state['individual_open'] = not st.session_state['individual_open']
        
        if st.session_state['individual_open']:
            display_tickets(tickets_to_render)
    else:
        # When there are no tickets to render (either not fetched or empty result)
        pass

if __name__ == "__main__":
    main() 