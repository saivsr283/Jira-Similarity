#!/usr/bin/env python3
"""
Unified JIRA Analysis Tool - PLAT Similarity + Filter Analysis
Combines both services into a single UI endpoint
"""

import streamlit as st
import json
import tempfile
import os
from datetime import datetime
from jira_similarity_tool import JIRASimilarityTool, JIRAClient
import pandas as pd
import re
from bs4 import BeautifulSoup
import html
import logging
from typing import Dict, List, Optional, Any
import requests
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="JIRA Analysis Suite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS with beautiful design
st.markdown("""
<style>
    /* Beautiful Color Palette */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --background: #1e293b;
        --surface: #334155;
        --surface-dark: #475569;
        --text-primary: #ffffff;
        --text-secondary: #e2e8f0;
        --text-muted: #cbd5e1;
        --border: #475569;
        --border-dark: #64748b;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }

    /* Main App Styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: var(--shadow);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8fafc;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary);
        color: white;
    }

    /* Card Styling */
    .modern-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }

    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Priority badges */
    .priority-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Similarity score styling */
    .similarity-score {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 8px;
        text-align: center;
    }

    .score-high { background-color: #dcfce7; color: #166534; }
    .score-medium { background-color: #fef3c7; color: #92400e; }
    .score-low { background-color: #fee2e2; color: #991b1b; }

    /* Group styling */
    .group-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
    }

    /* Ticket card styling */
    .ticket-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8fafc;
    }

    /* Fallback target card styling */
    .fallback-target-card { 
        border: 2px solid #1e88e5 !important; 
        border-radius: 10px !important; 
        background: #ffffff !important; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important; 
        margin: 10px 0 !important; 
        overflow: hidden !important; 
    }
    
    .fallback-target-header { 
        background: #e3f2fd !important; 
        color: #111111 !important; 
        padding: 12px 16px !important; 
        border-radius: 8px 8px 0 0 !important; 
        font-weight: 800 !important; 
    }
    
    .fallback-target-body { 
        padding: 14px 16px !important; 
        background: #f8fafc !important; 
        color: #111111 !important; 
    }
    
    .fallback-grid { 
        display: grid !important; 
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important; 
        gap: 12px !important; 
    }
    
    .fallback-chip { 
        background: #ffffff !important; 
        border: 1px solid #d1d5db !important; 
        border-radius: 8px !important; 
        padding: 10px !important; 
    }
    
    .fallback-chip-label { 
        font-size: 11px !important; 
        color: #111111 !important; 
        text-transform: uppercase !important; 
        font-weight: 700 !important; 
        display: block !important; 
        margin-bottom: 4px !important; 
    }
    
    .fallback-chip-value { 
        font-size: 14px !important; 
        color: #111111 !important; 
        font-weight: 700 !important; 
    }
    
    .fallback-target-header a { 
        color: #0b5ed7 !important; 
        text-decoration: underline !important; 
    }
    
    .fallback-summary { 
        font-weight: 800 !important; 
        margin-bottom: 8px !important; 
        color: #111111 !important; 
        font-size: 15px !important; 
    }
</style>
""", unsafe_allow_html=True)

def get_status_color(status):
    """Get color for status badge"""
    status_colors = {
        'open': '#10b981',
        'in progress': '#f59e0b', 
        'closed': '#6b7280',
        'resolved': '#10b981',
        'done': '#10b981',
        'analysis in progress': '#f59e0b',
        'successfully deployed': '#10b981',
        'staging validated': '#10b981',
        'qa validated': '#10b981',
        'ready for qa': '#f59e0b'
    }
    return status_colors.get(status.lower(), '#6b7280')

def get_priority_color(priority):
    """Get color for priority badge"""
    priority_colors = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#10b981',
        'critical': '#dc2626',
        'highest': '#dc2626'
    }
    return priority_colors.get(priority.lower(), '#6b7280')

def clean_html_content_with_markdown(html_content):
    """Clean HTML content and convert to markdown"""
    if not html_content:
        return ""
    
    try:
        # Parse HTML
        soup = BeautifulSoup(str(html_content), 'html.parser')
        
        # Convert to markdown-like format
        return format_jira_content_improved(str(html_content))
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {e}")
        return str(html_content)

def format_jira_content_improved(html_content):
    """Improved JIRA content formatting"""
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Convert various JIRA elements
        section_content = ""
        
        # Handle headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            section_content += f"\n{'#' * level} {heading.get_text().strip()}\n"
        
        # Handle paragraphs
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                section_content += f"{text}\n\n"
        
        # Handle lists
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                section_content += f"- {li.get_text().strip()}\n"
            section_content += "\n"
        
        for ol in soup.find_all('ol'):
            for i, li in enumerate(ol.find_all('li'), 1):
                section_content += f"{i}. {li.get_text().strip()}\n"
            section_content += "\n"
        
        # Handle code blocks
        for code in soup.find_all('code'):
            section_content += f"`{code.get_text().strip()}`"
        
        # Handle blockquotes
        for blockquote in soup.find_all('blockquote'):
            section_content += f"> {blockquote.get_text().strip()}\n\n"
        
        # Handle tables
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if rows:
                # Header row
                header_cells = rows[0].find_all(['th', 'td'])
                if header_cells:
                    section_content += "| " + " | ".join(cell.get_text().strip() for cell in header_cells) + " |\n"
                    section_content += "| " + " | ".join("---" for _ in header_cells) + " |\n"
                
                # Data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        section_content += "| " + " | ".join(cell.get_text().strip() for cell in cells) + " |\n"
                section_content += "\n"
        
        # Clean up extra whitespace
        section_content = re.sub(r'\n\s*\n\s*\n', '\n\n', section_content)
        section_content = section_content.strip()
        
        return section_content if section_content else html.escape(html_content)
        
    except Exception as e:
        logger.error(f"Error formatting content: {e}")
        return html.escape(html_content)

def display_results(results, ticket_key, threshold, max_results, tool):
    """Display similarity results"""
    if not results or len(results) == 0:
        st.error("❌ No similar tickets found or results are empty")
        
        # Fallback: Show target ticket details
        target_ticket = None
        try:
            if tool and hasattr(tool, 'jira_client') and tool.jira_client:
                target_ticket = tool.jira_client.get_ticket(ticket_key)
        except Exception as e:
            logger.error(f"Error fetching target ticket: {e}")
            target_ticket = None
        
        if target_ticket:
            try:
                base_url = tool.config.get('jira_url') if hasattr(tool, 'config') and tool.config else None
                ticket_url = f"{base_url.rstrip('/')}/browse/{ticket_key}" if base_url else None
            except Exception:
                ticket_url = None
            
            header_html = f'<div class="fallback-target-header">🎯 Target Ticket: {ticket_key}'
            link_html = f'<a href="{ticket_url}" target="_blank">Open in JIRA ↗</a>' if ticket_url else ""
            
            st.markdown(f"""
            <div class="fallback-target-card">
                {header_html}{link_html}</div>
                <div class="fallback-target-body">
                    <div class="fallback-summary">{target_ticket.summary or ""}</div>
                    <div class="fallback-grid">
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Status</span>
                            <span class="fallback-chip-value">{target_ticket.status or ""}</span>
                        </div>
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Type</span>
                            <span class="fallback-chip-value">{target_ticket.issue_type or ""}</span>
                        </div>
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Assignee</span>
                            <span class="fallback-chip-value">{target_ticket.assignee or ""}</span>
                        </div>
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Reporter</span>
                            <span class="fallback-chip-value">{target_ticket.reporter or ""}</span>
                        </div>
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Created</span>
                            <span class="fallback-chip-value">{target_ticket.created[:10] if target_ticket.created else ""}</span>
                        </div>
                        <div class="fallback-chip">
                            <span class="fallback-chip-label">Priority</span>
                            <span class="fallback-chip-value">{target_ticket.priority or ""}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        return
    
    st.success(f"✅ Found {len(results)} similar tickets!")
    
    # Display results
    for i, result in enumerate(results[:max_results], 1):
        # Result entries from tool.analyze_similarity are dicts
        similarity_score = result.get('similarity_score', 0.0)
        
        # Build a lightweight ticket-like object for rendering
        class _T:
            pass
        ticket = _T()
        ticket.key = result.get('key')
        ticket.summary = result.get('summary')
        ticket.issue_type = result.get('issue_type')
        ticket.priority = result.get('priority')
        ticket.status = result.get('status')
        ticket.assignee = result.get('assignee')
        ticket.reporter = result.get('reporter')
        ticket.created = result.get('created')
        ticket.updated = result.get('updated')
        ticket.description = result.get('description')
        
        # Determine score color
        if similarity_score >= 0.7:
            score_class = "score-high"
        elif similarity_score >= 0.4:
            score_class = "score-medium"
        else:
            score_class = "score-low"
        
        # Create ticket card
        with st.container():
            st.markdown(f"""
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: var(--primary);">🎫 #{i} - {ticket.key} [{similarity_score:.1%} Match]</h3>
                    <div class="similarity-score {score_class}">{similarity_score:.1%}</div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <strong>📝 Summary:</strong> {ticket.summary or "N/A"}
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <strong>Status:</strong><br>
                        <span class="status-badge" style="background: {get_status_color(ticket.status)}; color: white;">
                            {ticket.status or "N/A"}
                        </span>
                    </div>
                    <div>
                        <strong>Type:</strong><br>
                        {ticket.issue_type or "N/A"}
                    </div>
                    <div>
                        <strong>Assignee:</strong><br>
                        {ticket.assignee or "N/A"}
                    </div>
                    <div>
                        <strong>Priority:</strong><br>
                        <span class="priority-badge" style="background: {get_priority_color(ticket.priority)}; color: white;">
                            {ticket.priority or "N/A"}
                        </span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <div><strong>Reporter:</strong> {ticket.reporter or "N/A"}</div>
                    <div><strong>Created:</strong> {ticket.created[:10] if ticket.created else "N/A"}</div>
                    <div><strong>Updated:</strong> {ticket.updated[:10] if ticket.updated else "N/A"}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show description if available
            if ticket.description:
                with st.expander(f"📋 Description for {ticket.key}"):
                    clean_description = clean_html_content_with_markdown(ticket.description)
                    st.markdown(clean_description)

def analyze_tickets_similarity(tickets, threshold=0.2):
    """Analyze ticket similarities using TF-IDF and cosine similarity"""
    if len(tickets) < 2:
        return []
    
    # Extract summaries
    summaries = []
    ticket_indices = []
    
    for i, ticket in enumerate(tickets):
        if ticket.summary:
            summaries.append(ticket.summary)
            ticket_indices.append(i)
    
    if len(summaries) < 2:
        return []
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(summaries)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Group similar tickets
        groups = []
        used_indices = set()
        
        for i in range(len(summaries)):
            if i in used_indices:
                continue
                
            group = [i]
            used_indices.add(i)
            
            for j in range(i + 1, len(summaries)):
                if j in used_indices:
                    continue
                    
                if similarity_matrix[i][j] >= threshold:
                    group.append(j)
                    used_indices.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        # Convert groups to ticket groups
        ticket_groups = []
        for group in groups:
            group_tickets = []
            for idx in group:
                original_idx = ticket_indices[idx]
                group_tickets.append(tickets[original_idx])
            ticket_groups.append(group_tickets)
        
        return ticket_groups
        
    except Exception as e:
        st.error(f"Error analyzing similarities: {e}")
        return []

def display_filter_results(tickets, groups):
    """Display filter analysis results"""
    st.success(f"✅ Found {len(tickets)} tickets!")
    
    if groups:
        st.success(f"✅ Found {len(groups)} groups of similar tickets!")
        
        for i, group in enumerate(groups, 1):
            with st.expander(f"🔍 Group {i} Details ({len(group)} tickets)", expanded=False):
                # Group header
                st.markdown(f"""
                <div class="group-header">
                    📋 Group {i}: {len(group)} Similar Tickets
                </div>
                """, unsafe_allow_html=True)
                
                # Group basis
                st.markdown("""
                <div class="modern-card">
                    <strong>🎯 Grouping Basis:</strong> Tickets were grouped together because their summaries have similar content, keywords, and meaning. The similarity is calculated using TF-IDF text analysis and cosine similarity.
                </div>
                """, unsafe_allow_html=True)
                
                # Representative summary
                if group:
                    st.markdown(f"""
                    <div class="modern-card">
                        <strong>📝 Representative Summary:</strong> {group[0].summary}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Individual tickets
                with st.expander("📋 All Individual Tickets", expanded=False):
                    for j, ticket in enumerate(group, 1):
                        st.markdown(f"""
                        <div class="ticket-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0; color: var(--primary);">🎫 Ticket {j}: {ticket.key} - {ticket.summary}</h4>
                                <div style="font-size: 0.8rem; color: #666;">Position: #{j} in Group {i}</div>
                            </div>
                            
                            <div style="margin-top: 0.5rem;">
                                <strong>Status:</strong> <span class="status-badge" style="background: {get_status_color(ticket.status)};">{ticket.status}</span><br>
                                <strong>Type:</strong> {ticket.issue_type}<br>
                                <strong>Assignee:</strong> {ticket.assignee}<br>
                                <strong>Created:</strong> {ticket.created[:10] if ticket.created else "N/A"}<br>
                                <strong>Reporter:</strong> {ticket.reporter}<br>
                                <strong>Priority:</strong> <span class="priority-badge" style="background: {get_priority_color(ticket.priority)};">{ticket.priority}</span>
                            </div>
                            
                            <div style="margin-top: 0.5rem;">
                                <strong>Summary:</strong> {ticket.summary}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No similar ticket groups found. All tickets are unique.")

def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 JIRA Analysis Suite</h1>
        <p>PLAT Similarity Tool + Filter Analysis in One Interface</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["🎯 PLAT Similarity Tool", "📊 Filter Analysis"])
    
    with tab1:
        st.markdown("### 🎯 Find Similar JIRA Tickets")
        
        # Sidebar configuration
        with st.sidebar:
            st.markdown("### ⚙️ Configuration")
            
            # JIRA credentials
            st.markdown("#### 🔐 JIRA Credentials")
            username = st.text_input("Username", value="", help="Leave empty to use environment variables")
            auth_token = st.text_input("Auth Token", type="password", value="", help="Leave empty to use environment variables")
            
            # Analysis parameters
            st.markdown("#### 📊 Analysis Parameters")
            threshold = st.slider("Similarity Threshold", min_value=0.1, max_value=1.0, value=0.2, step=0.05, help="Minimum similarity score to consider tickets similar")
            max_results = st.slider("Max Results", min_value=5, max_value=50, value=10, help="Maximum number of similar tickets to display")
        
        # Main input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ticket_key = st.text_input(
                "🎫 Enter JIRA Ticket Key",
                placeholder="e.g., PLAT-12345",
                help="Enter the JIRA ticket key you want to find similar tickets for"
            )
        
        with col2:
            analyze_button = st.button("🔍 Find Similar Tickets", type="primary", use_container_width=True)
        
        # Analysis
        if analyze_button:
            if not ticket_key:
                st.error("❌ Please enter a JIRA ticket key")
            else:
                try:
                    # Initialize tool with proper credentials
                    with st.spinner("🔄 Initializing JIRA Similarity Tool..."):
                        # Get credentials from environment or user input
                        jira_url = os.getenv('JIRA_URL', 'https://koreteam.atlassian.net')
                        jira_username = username if username else os.getenv('JIRA_USERNAME', 'hemanth.bandaru@kore.com')
                        jira_token = auth_token
                        
                        if not jira_token:
                            st.error("❌ JIRA API token is required. Please enter it in the sidebar.")
                            return
                        
                        # Initialize JIRA client first
                        jira_client = JIRAClient(
                            base_url=jira_url,
                            username=jira_username,
                            api_token=jira_token
                        )
                        
                        # Initialize tool with the client
                        tool = JIRASimilarityTool()
                        tool.jira_client = jira_client
                        tool.config = {
                            'jira_url': jira_url,
                            'username': jira_username,
                            'auth_token': jira_token
                        }
                        
                        st.success("✅ Tool initialized successfully!")
                    
                    # Analyze similarity
                    with st.spinner(f"🔍 Analyzing similarity for {ticket_key}..."):
                        results = tool.analyze_similarity(ticket_key, threshold=threshold, max_results=max_results)
                        st.success("✅ Similar tickets fetched successfully!")
                    
                    # Display results
                    display_results(results, ticket_key, threshold, max_results, tool)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error("💡 Make sure to provide valid JIRA credentials in the sidebar")
        
        # Notes section
        with st.expander("📚 How This Tool Works - Notes", expanded=False):
            st.markdown("""
            ### 🎯 Subject-First Similarity Analysis
            
            **Core Logic:**
            - **Subject-First Matching**: Focuses on specific features/subjects (nodes, flags, dashboards, filters) rather than generic problem phrases
            - **Status Phrase Stripping**: Ignores generic phrases like "not functioning", "not working", "as expected" to focus on core issues
            - **Hard Subject Overlap**: Candidate tickets must share at least one extracted subject term with the target ticket
            - **Project Constraints**: Searches PLAT and XOP projects only
            - **Issue Type Filtering**: Considers Bug, Customer-Incident, and Customer-Defect only
            
            **Scoring Weights:**
            - Subject Similarity: 50% (highest priority)
            - Summary Similarity: 35%
            - Technical Terms: 10%
            - Jaccard Similarity: 5%
            - Metadata factors: 0% (ignored)
            
            **Example - DialogGPT Issues:**
            - Target: "DialogGPT: Custom Integration: Task Failure Event"
            - Matches: Other DialogGPT task failure, integration, or custom event issues
            - Ignores: Generic "not working" or "error occurred" phrases
            
            **Fallback Behavior:**
            - If no similar tickets found, displays target ticket details
            - Threshold relaxation: Retries with threshold - 0.1 if no results
            - UI fallback: Shows target ticket card when no matches
            
            **Where to Adjust Logic:**
            - `jira_similarity_tool.py`: SimilarityAnalyzer class methods
            - `extract_subject_terms()`: Add new feature keywords
            - `preprocess_text()`: Modify text cleaning rules
            - `calculate_similarity()`: Adjust scoring weights
            """)
    
    with tab2:
        st.markdown("### 📊 JQL Filter Analysis")
        
        # JQL Query Input
        st.markdown("#### 📝 Enter JQL Query")
        jql_query = st.text_area(
            "JQL Query",
            height=100,
            placeholder="project in (PLAT) and issuetype in (Bug, \"Customer-Incident\", \"Customer-Defect\") and created >= 2024-01-01",
            help="Enter your JQL query to fetch and analyze tickets"
        )
        
        # Analysis parameters
        col1, col2 = st.columns(2)
        with col1:
            similarity_threshold = st.slider("Grouping Threshold", min_value=0.1, max_value=1.0, value=0.2, step=0.05, help="Minimum similarity score to group tickets together")
        with col2:
            analyze_filter_button = st.button("🔍 Analyze Tickets", type="primary", use_container_width=True)
        
        # Filter Analysis
        if analyze_filter_button:
            if not jql_query:
                st.error("❌ Please enter a JQL query")
            else:
                try:
                    # Initialize JIRA client with proper credentials
                    with st.spinner("🔄 Initializing JIRA client..."):
                        # Get credentials from environment or user input
                        jira_url = os.getenv('JIRA_URL', 'https://koreteam.atlassian.net')
                        jira_username = username if username else os.getenv('JIRA_USERNAME', 'hemanth.bandaru@kore.com')
                        jira_token = auth_token
                        
                        if not jira_token:
                            st.error("❌ JIRA API token is required. Please enter it in the sidebar.")
                            return
                        
                        jira_client = JIRAClient(
                            base_url=jira_url,
                            username=jira_username,
                            api_token=jira_token
                        )
                        st.success("✅ Filter Analyzer initialized successfully!")
                    
                    # Fetch tickets
                    with st.spinner(f"🔍 Fetching tickets with JQL..."):
                        tickets = jira_client.search_tickets(jql_query, max_results=100)
                        st.success(f"✅ Found {len(tickets)} tickets!")
                    
                    if tickets:
                        # Analyze similarities
                        with st.spinner("🔍 Analyzing ticket similarities..."):
                            groups = analyze_tickets_similarity(tickets, similarity_threshold)
                            st.success(f"✅ Found {len(groups)} groups of similar tickets!")
                        
                        # Display results
                        display_filter_results(tickets, groups)
                    else:
                        st.warning("⚠️ No tickets found. Please check your JQL query.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error("💡 Make sure to provide valid JIRA credentials in the sidebar")

if __name__ == "__main__":
    main()
