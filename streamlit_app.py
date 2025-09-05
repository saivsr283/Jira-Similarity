#!/usr/bin/env python3
"""
JIRA Similarity Tool - Modern Web Interface
"""

import streamlit as st
import json
import tempfile
import os
from datetime import datetime
from jira_similarity_tool import JIRASimilarityTool
import pandas as pd
import re
from bs4 import BeautifulSoup
import html
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="JIRA Similarity Tool",
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
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main Container */
    .main .block-container {
        max-width: 1400px;
        padding: 0;
        background: var(--background);
    }
    
    /* Beautiful Header */
    .hero-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        color: white;
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        color: white;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-header p {
        font-size: 1.25rem;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        color: white;
        position: relative;
        z-index: 1;
        font-weight: 400;
    }
    
    /* Modern Cards */
    .modern-card {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    }
    
    .modern-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--primary);
    }
    
    .modern-card h3 {
        color: var(--primary);
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: var(--surface);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: var(--background);
    }
    
    /* Beautiful Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 100%);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    
    .sidebar-section {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
    }
    
    .sidebar-section h3 {
        color: var(--primary);
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    .css-1d391kg .stMarkdown {
        color: var(--text-primary);
    }
    
    .css-1d391kg .stMarkdown h1,
    .css-1d391kg .stMarkdown h2,
    .css-1d391kg .stMarkdown h3 {
        color: var(--primary);
        font-weight: 600;
    }
    
    .css-1d391kg .stMarkdown p {
        color: var(--text-secondary);
    }
    
    .css-1d391kg label {
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Slider Styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: none;
        box-shadow: var(--shadow);
    }
    
    .stError {
        background: linear-gradient(135deg, var(--error) 0%, #dc2626 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: none;
        box-shadow: var(--shadow);
    }
    
    .stWarning {
        background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: none;
        box-shadow: var(--shadow);
    }
    
    /* Ticket Cards */
    .ticket-card {
        border: 2px solid #007bff !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        background-color: #f8f9fa !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .ticket-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .ticket-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .ticket-card h4 {
        color: var(--primary);
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    .ticket-card p {
        color: var(--text-secondary);
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    /* Beautiful Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }
    
    .badge:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    .badge-success { 
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%); 
        color: white; 
    }
    .badge-warning { 
        background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%); 
        color: white; 
    }
    .badge-error { 
        background: linear-gradient(135deg, var(--error) 0%, #dc2626 100%); 
        color: white; 
    }
    .badge-info { 
        background: linear-gradient(135deg, var(--secondary) 0%, #7c3aed 100%); 
        color: white; 
    }
    
    /* Metrics */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderContent {
        background: var(--background) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
    }
    
    .stDataFrame td {
        background: var(--background);
        color: var(--text-primary);
        padding: 0.75rem;
    }
    
    /* Text Overrides */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stMarkdown p {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    /* Force all text to be visible */
    * {
        color: var(--text-primary) !important;
    }
    
    /* Exceptions for white text elements */
    .hero-header, .hero-header *, .stButton > button, .stSuccess, .stError, .stWarning,
    .badge-success, .badge-warning, .badge-error, .badge-info,
    .stDataFrame th {
        color: white !important;
    }
    
    /* Specific header overrides to ensure visibility */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* Streamlit markdown headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* Main content headers */
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar headers */
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3,
    .css-1d391kg h4,
    .css-1d391kg h5,
    .css-1d391kg h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* Override any light colored headers */
    *[style*="color: #6c757d"],
    *[style*="color: #495057"],
    *[style*="color: #adb5bd"],
    *[style*="color: #dee2e6"],
    *[style*="color: #f8f9fa"],
    *[style*="color: #64748b"] {
        color: var(--text-primary) !important;
    }
    
    /* Force all markdown text to be visible */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown * {
        color: var(--text-primary) !important;
    }
    
    /* Specific targeting for Quick Start and Configuration headers */
    .main .block-container .stMarkdown h2,
    .main .block-container h2 {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
    }
    
    /* Sidebar section headers */
    .css-1d391kg .stMarkdown h2,
    .css-1d391kg .stMarkdown h3 {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    /* Force all sidebar text to be visible */
    .css-1d391kg * {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg label {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg .stMarkdown p {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg .stMarkdown h1, 
    .css-1d391kg .stMarkdown h2, 
    .css-1d391kg .stMarkdown h3 {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stMarkdown strong {
        color: var(--primary) !important;
        font-weight: bold !important;
    }
    
    /* Sidebar input labels */
    .css-1d391kg .stTextInput > div > div > div > label {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stSelectbox > div > div > div > label {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stNumberInput > div > div > div > label {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stSlider > div > div > div > div > div > div {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar section titles */
    .css-1d391kg .sidebar-title {
        color: var(--primary) !important;
        font-weight: bold !important;
    }
    
    /* Sidebar text content */
    .css-1d391kg .sidebar-section p {
        color: var(--text-primary) !important;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    }
    
    /* Force all main content text to be visible */
    .main .block-container * {
        color: var(--text-primary) !important;
    }
    
    /* Main content headers with specific colors */
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6 {
        color: var(--primary) !important;
        font-weight: 600 !important;
    }
    
    /* Quick Start header specific styling */
    .main .block-container h2:contains("🚀 Quick Start"),
    .main .block-container .stMarkdown h2:contains("🚀 Quick Start") {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
    }
    
    /* Configuration header specific styling */
    .css-1d391kg h2:contains("⚙️ Configuration"),
    .css-1d391kg .stMarkdown h2:contains("⚙️ Configuration") {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    /* JIRA URL and API Token labels */
    .css-1d391kg label:contains("🌐 JIRA URL"),
    .css-1d391kg label:contains("🔑 API Token"),
    .css-1d391kg label:contains("👤 Username"),
    .css-1d391kg label:contains("📁 Project Key") {
        color: var(--primary) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Universal text color override for any black text on black background */
    *[style*="color: black"],
    *[style*="color: #000"],
    *[style*="color: #000000"],
    *[style*="color: #1e293b"],
    *[style*="color: #0f172a"] {
        color: var(--text-primary) !important;
    }
    
    /* Force all text elements to be visible */
    p, h1, h2, h3, h4, h5, h6, label, span, div, strong, em, b, i {
        color: var(--text-primary) !important;
    }
    
    /* Exception for elements that should remain white */
    .hero-header, .hero-header *, 
    .stButton > button, 
    .stSuccess, .stError, .stWarning,
    .badge-success, .badge-warning, .badge-error, .badge-info,
    .stDataFrame th {
        color: white !important;
    }
    
    /* Exception for primary colored elements */
    .css-1d391kg label,
    .css-1d391kg .stMarkdown h1,
    .css-1d391kg .stMarkdown h2,
    .css-1d391kg .stMarkdown h3,
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3 {
        color: var(--primary) !important;
    }
    
    /* Export section styling */
    .export-section {
        text-align: center;
        padding: 2rem;
        background: var(--surface);
        border-radius: 12px;
        margin: 2rem 0;
        border: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .export-section h3 {
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .export-section p {
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        font-size: 1rem;
    }
    .export-buttons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.5rem;
        flex-wrap: wrap;
        width: 100%;
    }
    .export-buttons .stButton {
        margin: 0;
    }
    .export-buttons button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        min-width: 120px;
    }
    .export-buttons button:hover {
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Badge alignment fixes */
    .badge-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-end;
    }
    
    .badge-row {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    
    /* Ticket card badge alignment */
    .ticket-badges {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-end;
        min-width: 120px;
    }
    
    .ticket-badges .badge {
        width: 100%;
        text-align: center;
        justify-content: center;
    }

    /* Text area styling for white text */
    .stTextArea textarea {
        color: white !important;
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
    }
    .stTextArea textarea:disabled {
        color: white !important;
        background-color: var(--surface) !important;
    }
    /* Override Streamlit's default text area styling */
    .stTextArea > div > div > textarea {
        color: white !important;
    }
    
    /* Ticket card styling */
    .ticket-card {
        border: 2px solid #ffffff !important;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: block;
        width: 100%;
        box-sizing: border-box;
    }
    .similarity-badge {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        color: #ffffff !important;
    }
    .high-similarity { 
        background-color: #28a745 !important; 
        color: #ffffff !important; 
        border: 1px solid #1e7e34;
    }
    .medium-similarity { 
        background-color: #ffc107 !important; 
        color: #212529 !important; 
        border: 1px solid #e0a800;
    }
    .low-similarity { 
        background-color: #17a2b8 !important; 
        color: #ffffff !important; 
        border: 1px solid #138496;
    }
</style>
""", unsafe_allow_html=True)

def save_config(config_data):
    """Save configuration to file with proper error handling"""
    try:
        # Try to save to the current directory first
        config_file = 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True, "Configuration saved successfully!"
    except PermissionError:
        # If permission denied, try to save to a temporary location
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            config_file = os.path.join(temp_dir, 'jira_config.json')
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True, f"Configuration saved to temporary location: {config_file}"
        except Exception as e:
            return False, f"Failed to save configuration: {str(e)}"
    except OSError as e:
        if e.errno == 30:  # Read-only file system
            # Try to save to a writable location
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                config_file = os.path.join(temp_dir, 'jira_config.json')
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                return True, f"Configuration saved to temporary location: {config_file}"
            except Exception as temp_e:
                return False, f"Read-only file system detected. Failed to save configuration: {str(temp_e)}"
        else:
            return False, f"Failed to save configuration: {str(e)}"
    except Exception as e:
        return False, f"Failed to save configuration: {str(e)}"

def analyze_ticket_safely(tool, ticket_key, threshold, max_results):
    """Safely analyze ticket with error handling"""
    try:
        results = tool.analyze_similarity(ticket_key, threshold=threshold, max_results=max_results)
        return {
            'success': True,
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def display_results(results, ticket_key, threshold, max_results, tool=None):
    """Display analysis results in a beautiful layout"""
    st.success(f"✅ Similar tickets fetched successfully! Found {len(results) if results else 0} similar tickets.")
    
    if not results or len(results) == 0:
        st.error("❌ No similar tickets found or results are empty")

        # Fallback: Show target ticket details
        target_ticket = None
        try:
            if tool and hasattr(tool, 'jira_client') and tool.jira_client:
                target_ticket = tool.jira_client.get_ticket(ticket_key)
        except Exception:
            target_ticket = None

        if target_ticket:
            try:
                base_url = tool.config.get('jira_url') if hasattr(tool, 'config') and tool.config else None
                ticket_url = f"{base_url.rstrip('/')}/browse/{ticket_key}" if base_url else None
            except Exception:
                ticket_url = None

            st.markdown("""
            <style>
            .fallback-target-card { border: 2px solid #1e88e5 !important; border-radius: 10px !important; background: #ffffff !important; box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important; margin: 10px 0 !important; overflow: hidden !important; }
            .fallback-target-header { background: #e3f2fd !important; color: #111111 !important; padding: 12px 16px !important; border-radius: 8px 8px 0 0 !important; font-weight: 800 !important; }
            .fallback-target-body { padding: 14px 16px !important; background: #f8fafc !important; color: #111111 !important; }
            .fallback-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0, 1fr)) !important; gap: 12px !important; }
            .fallback-chip { background: #ffffff !important; border: 1px solid #d1d5db !important; border-radius: 8px !important; padding: 10px !important; }
            .fallback-chip-label { font-size: 11px !important; color: #111111 !important; text-transform: uppercase !important; font-weight: 700 !important; display: block !important; margin-bottom: 4px !important; }
            .fallback-chip-value { font-size: 14px !important; color: #111111 !important; font-weight: 700 !important; }
            .fallback-target-header a { color: #0b5ed7 !important; text-decoration: underline !important; }
            .fallback-summary { font-weight: 800 !important; margin-bottom: 8px !important; color: #111111 !important; font-size: 15px !important; }
            </style>
            """, unsafe_allow_html=True)

            header_html = f"<div class='fallback-target-header'>🎯 Target Ticket: {target_ticket.key}</div>"
            link_html = f"<a href='{ticket_url}' target='_blank' style='color:#1e88e5; text-decoration: underline; float:right;'>Open in JIRA ↗</a>" if ticket_url else ""

            st.markdown("""
            <div class='fallback-target-card'>
              {header}
              <div class='fallback-target-body'>
                <div class='fallback-summary'>{summary}</div>
                <div class='fallback-grid'>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Status</span><span class='fallback-chip-value'>{status}</span></div>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Type</span><span class='fallback-chip-value'>{issuetype}</span></div>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Assignee</span><span class='fallback-chip-value'>{assignee}</span></div>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Reporter</span><span class='fallback-chip-value'>{reporter}</span></div>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Created</span><span class='fallback-chip-value'>{created}</span></div>
                  <div class='fallback-chip'><span class='fallback-chip-label'>Priority</span><span class='fallback-chip-value'>{priority}</span></div>
                </div>
              </div>
            </div>
            """.format(
                header=(header_html[:-6] + link_html + "</div>") if link_html else header_html,
                summary=(target_ticket.summary or "").replace("<", "&lt;").replace(">", "&gt;"),
                status=target_ticket.status or "",
                issuetype=target_ticket.issue_type or "",
                assignee=target_ticket.assignee or "",
                reporter=target_ticket.reporter or "",
                created=target_ticket.created[:10] if target_ticket.created else "",
                priority=target_ticket.priority or ""
            ), unsafe_allow_html=True)

        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get target ticket details from the results
    target_ticket = None
    if hasattr(tool, 'jira_client') and tool.jira_client:
        try:
            target_ticket = tool.jira_client.get_ticket(ticket_key)
        except Exception as e:
            # Silently handle target ticket fetch failure - main functionality still works
            pass
    
    # Display Target Ticket Information
    if target_ticket:
        st.markdown("## 🎯 Target Ticket Information")
        st.markdown("""
        <style>
        .target-ticket-card {
            border: 3px solid #28a745 !important;
            border-radius: 10px !important;
            padding: 0 !important;
            margin: 5px 0 !important;
            background-color: #f8fff9 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            display: block !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        .target-ticket-header {
            background-color: #28a745 !important;
            color: white !important;
            padding: 12px 16px !important;
            border-radius: 6px 6px 0 0 !important;
            margin: 0 !important;
            font-weight: bold !important;
            font-size: 18px !important;
        }
        .detail-card {
            background-color: #ffffff !important;
            border: 1px solid #dee2e6 !important;
            border-radius: 6px !important;
            padding: 12px !important;
            text-align: center !important;
            margin-bottom: 10px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        .detail-label {
            font-weight: bold !important;
            color: #495057 !important;
            font-size: 12px !important;
            margin-bottom: 4px !important;
            text-transform: uppercase !important;
        }
        .detail-value {
            color: #212529 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Build JIRA link if config is available
        jira_link = ""
        if tool and hasattr(tool, 'config') and tool.config.get('jira_url'):
            jira_link = f"{tool.config.get('jira_url').rstrip('/')}/browse/{target_ticket.key}"
        header_right = f'<a href="{jira_link}" target="_blank" style="color: white; text-decoration: underline;">Open in JIRA ↗</a>' if jira_link else ''
        st.markdown(
            f'<div class="target-ticket-card">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="target-ticket-header" style="display:flex; justify-content: space-between; align-items: center;">'
            f'<span>🎯 Target Ticket: {target_ticket.key}</span>'
            f'{header_right}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div style="padding: 16px;">', unsafe_allow_html=True)
        
        # Target ticket summary
        st.markdown(f"**📝 Summary:** {target_ticket.summary}")
        
        # Target ticket description and details - side by side layout with better proportions
        col_desc, col_details = st.columns([3, 1])  # 75% description, 25% details
        
        with col_desc:
            # Target ticket description
            if target_ticket.description:
                clean_target_description = clean_html_content_with_markdown(target_ticket.description)
                if clean_target_description:
                    st.markdown("**📄 Description:**")
                    st.markdown("""
                    <style>
                    .desc-normalize * { font-size: 14px !important; line-height: 1.6 !important; }
                    .desc-normalize h1, .desc-normalize h2, .desc-normalize h3, .desc-normalize h4, .desc-normalize h5, .desc-normalize h6 { font-size: 14px !important; }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<div class="desc-normalize" style="color: white; background-color: #2e2e2e; padding: 20px; border-radius: 8px; border: 1px solid #444; height: 500px; width: 95%; overflow-y: auto; line-height: 1.6; margin-left: 0;">{clean_target_description}</div>', unsafe_allow_html=True)
        
        with col_details:
            # Target ticket details in cards - compact vertical layout
            st.markdown("**📋 Ticket Details:**")
            
            # Status
            status_color = get_status_color(target_ticket.status)
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Status</div>
            <div class="detail-value" style="color: {status_color}; font-size: 13px;">{target_ticket.status}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Priority
            priority_color = get_priority_color(target_ticket.priority)
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Priority</div>
            <div class="detail-value" style="color: {priority_color}; font-size: 13px;">{target_ticket.priority}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Type
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Type</div>
            <div class="detail-value" style="font-size: 13px;">{target_ticket.issue_type}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Assignee
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Assignee</div>
            <div class="detail-value" style="font-size: 13px;">{target_ticket.assignee or 'Unassigned'}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Reporter
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Reporter</div>
            <div class="detail-value" style="font-size: 13px;">{target_ticket.reporter}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Created
            st.markdown(f'''
            <div class="detail-card" style="width: 100%; margin-left: 0; padding: 8px; margin-bottom: 6px;">
            <div class="detail-label" style="font-size: 11px;">Created</div>
            <div class="detail-value" style="font-size: 13px;">{format_date(target_ticket.created)[:10]}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close target-ticket-card wrapper
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Similar Tickets Cards View
    st.markdown("## 🔍 Similar Tickets")
    st.markdown("Below are the tickets most similar to your target ticket:")
    
    # Display tickets in a card layout
    for i, ticket in enumerate(results, 1):
        # Safely get ticket data with defaults
        ticket_key = ticket.get('key', 'Unknown')
        summary = ticket.get('summary', 'No summary')
        status = ticket.get('status', 'Unknown')
        priority = ticket.get('priority', 'Unknown')
        similarity = ticket.get('similarity_score', 0)  # Use similarity_score from the new format
        issue_type = ticket.get('issue_type', 'Unknown')
        assignee = ticket.get('assignee', 'Unassigned')
        reporter = ticket.get('reporter', 'Unknown')
        created = ticket.get('created', 'Unknown')
        updated = ticket.get('updated', 'Unknown')
        description = ticket.get('description', '')
        url = ticket.get('url', '')
        components = ticket.get('components', [])
        labels = ticket.get('labels', [])
        
        # Clean description
        clean_description = clean_html_content_with_markdown(description)
        
        # Create a comprehensive card for each ticket
        with st.container():
            # Simple card styling with border
            st.markdown("""
            <style>
            .ticket-card {
                border: 2px solid #007bff !important;
                border-radius: 8px !important;
                padding: 12px !important;
                margin: 8px 0 !important;
                background-color: #f8f9fa !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                display: block !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            .similarity-badge {
                display: inline-block;
                padding: 8px 12px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                color: #ffffff !important;
            }
            .high-similarity { 
                background-color: #28a745 !important; 
                color: #ffffff !important; 
                border: 1px solid #1e7e34;
            }
            .medium-similarity { 
                background-color: #ffc107 !important; 
                color: #212529 !important; 
                border: 1px solid #e0a800;
            }
            .low-similarity { 
                background-color: #17a2b8 !important; 
                color: #ffffff !important; 
                border: 1px solid #138496;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Card container with white border
            st.markdown('<div class="ticket-card">', unsafe_allow_html=True)
            
            # === TICKET HEADER ===
            # Ticket ID and match score aligned on the same line with match score on the right
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="margin: 0; color: #007bff;">🎫 #{i} - {ticket_key}</h3>
            <div class="similarity-badge {
                    'high-similarity' if similarity * 100 >= 70 else 
                    'medium-similarity' if similarity * 100 >= 40 else 
                    'low-similarity'
            }">{similarity * 100:.1f}% Match</div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown(f"**{summary}**")
            
            # Reduced divider spacing
            st.markdown('<hr style="margin: 8px 0;">', unsafe_allow_html=True)
            
            # === TICKET DETAILS SECTION ===
            # Status and Priority aligned properly
            status_color = get_status_color(status)
            priority_color = get_priority_color(priority)
            st.markdown(f'''
            <div style="display: flex; gap: 8px; margin-bottom: 12px; align-items: center;">
            <div style="background-color: {status_color}; padding: 6px 12px; border-radius: 4px; color: white; font-weight: bold; font-size: 16px; text-align: center;">
                    {status}
            </div>
            <div style="background-color: {priority_color}; padding: 6px 12px; border-radius: 4px; color: white; font-weight: bold; font-size: 16px; text-align: center;">
                    {priority}
            </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Individual cards for Type, Assignee, Reporter, Created in horizontal line with white background and black text
            st.markdown("**📋 Ticket Details**")
            
            # Add CSS with higher specificity to override Streamlit defaults
            st.markdown("""
            <style>
            .detail-card-custom {
                background-color: #ffffff !important;
                border: 2px solid #dee2e6 !important;
                border-radius: 8px !important;
                padding: 12px !important;
                margin: 4px !important;
                text-align: center !important;
                flex: 1 !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }
            .detail-card-custom .label {
                font-size: 12px !important;
                font-weight: bold !important;
                color: #000000 !important;
                margin-bottom: 6px !important;
                display: block !important;
            }
            .detail-card-custom .value {
                font-size: 14px !important;
                font-weight: bold !important;
                color: #000000 !important;
                display: block !important;
            }
            .detail-cards-container {
                display: flex !important;
                gap: 8px !important;
                margin-bottom: 16px !important;
                width: 100% !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create individual cards with custom CSS classes
            st.markdown(f'''
            <div class="detail-cards-container">
                <div class="detail-card-custom">
                    <span class="label">TYPE</span>
                    <span class="value">{issue_type}</span>
                </div>
                <div class="detail-card-custom">
                    <span class="label">ASSIGNEE</span>
                    <span class="value">{assignee}</span>
                </div>
                <div class="detail-card-custom">
                    <span class="label">REPORTER</span>
                    <span class="value">{reporter}</span>
                </div>
                <div class="detail-card-custom">
                    <span class="label">CREATED</span>
                    <span class="value">{format_date(created)[:10]}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # === DESCRIPTION SECTION ===
            if clean_description:
                # Create a balanced layout with description matching ticket details height
                col_desc, col_components = st.columns([3, 1])
                
                with col_desc:
                    with st.expander("📝 Description", expanded=False):
                        # Increased height to better match ticket details section (approximately 160px)
                        st.markdown("""
                        <style>
                        .desc-normalize * { font-size: 14px !important; line-height: 1.6 !important; }
                        .desc-normalize h1, .desc-normalize h2, .desc-normalize h3, .desc-normalize h4, .desc-normalize h5, .desc-normalize h6 { font-size: 14px !important; }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div class="desc-normalize" style="color: white; background-color: #2e2e2e; padding: 10px; border-radius: 6px; border: 1px solid #444; height: 160px; overflow-y: auto; line-height: 1.6;">{clean_description}</div>', unsafe_allow_html=True)
                
                with col_components:
                    # Components and Labels positioned next to description
                    if components:
                        st.markdown(f"**🏷️ Components:** {', '.join(components)}")
                    if labels:
                        st.markdown(f"**🏷️ Labels:** {', '.join(labels)}")
            else:
                # If no description, still show components/labels
                if components or labels:
                    if components:
                        st.markdown(f"**🏷️ Components:** {', '.join(components)}")
                if labels:
                        st.markdown(f"**🏷️ Labels:** {', '.join(labels)}")
            
            # === FIX SUGGESTIONS SECTION ===
            fix_suggestions = ticket.get('fix_suggestions', {})
            if fix_suggestions and fix_suggestions.get('has_fix'):
                st.markdown("#### 🔧 Fix Suggestions")
                
                # Fix suggestions in columns
                col_fix1, col_fix2 = st.columns(2)
                with col_fix1:
                    st.info(f"**Fix Type:** {fix_suggestions.get('fix_type', 'N/A')}")
                    st.info(f"**Confidence:** {fix_suggestions.get('confidence', 0):.1%}")
                
                with col_fix2:
                    if fix_suggestions.get('applicable'):
                        st.success("✅ **Applicable to your ticket**")
                    else:
                        st.warning("⚠️ **May not be directly applicable**")
                
                # Detailed fix information
                if fix_suggestions.get('suggested_solution'):
                    st.markdown("**💡 Suggested Solution:**")
                    st.info(fix_suggestions.get('suggested_solution'))
                    
                    if fix_suggestions.get('workaround'):
                        st.markdown("**🛠️ Workaround:**")
                        st.warning(fix_suggestions.get('workaround'))
            
                    if fix_suggestions.get('root_cause'):
                        st.markdown("**🔍 Root Cause:**")
                        st.error(fix_suggestions.get('root_cause'))
            
            # === COMMENT ANALYSIS SECTION ===
            comment_analysis = None
            if tool and hasattr(tool, 'jira_client') and tool.jira_client:
                try:
                    logger.info(f"🔍 Attempting comment analysis for {ticket_key}")
                    comment_analysis = analyze_comments_for_fixes(ticket_key, tool.jira_client)
                    logger.info(f"✅ Comment analysis completed for {ticket_key}")
                except Exception as e:
                    logger.error(f"❌ Error in comment analysis for {ticket_key}: {e}")
                # Don't show error message in UI for comment analysis failures
                comment_analysis = None
            else:
                logger.warning(f"⚠️ JIRA client not available for comment analysis of {ticket_key}")
                comment_analysis = None
            
            # Only display comment analysis section if there are actual comments
            if comment_analysis:
                st.markdown("#### 💬 Comment Analysis")
                st.markdown(comment_analysis)
            
            # === CARD FOOTER ===
            st.markdown('<hr style="margin: 6px 0; border-color: #ddd;">', unsafe_allow_html=True)
            col_footer1, col_footer2 = st.columns([3, 1])
            with col_footer1:
                st.caption(f"🔗 **JIRA URL:** {url}")
            with col_footer2:
                if url:
                    st.link_button("🔗 View in JIRA", url)
            
                # Close the card div
                st.markdown('</div>', unsafe_allow_html=True)
    
                # Export functionality
    st.markdown("---")
    st.markdown("## 📤 Export Results")
    
    # Center the export section
    col_export1, col_export2, col_export3 = st.columns([1, 2, 1])
    
    with col_export2:
        st.markdown("<h3 style='text-align: center;'>Export your analysis results</h3>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📊 Export as JSON", type="primary", use_container_width=True):
                export_json(results['results'], {'key': ticket_key})
        
        with col_btn2:
            if st.button("📋 Export as CSV", type="secondary", use_container_width=True):
                export_csv(results['results'], {'key': ticket_key})
    
            # Add spacing before notes section
            st.markdown("<br><br>", unsafe_allow_html=True)

def format_date(date_string):
    """Format date string to readable format"""
    if not date_string or date_string == 'Unknown':
        return 'N/A'
    
    try:
        # Handle ISO format dates
        if 'T' in date_string:
            # Parse ISO format: 2025-08-14T09:54:26.291+0530
            from datetime import datetime
            # Remove timezone info for parsing
            date_part = date_string.split('+')[0].split('.')[0]
            dt = datetime.fromisoformat(date_part)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Try other common formats
            from datetime import datetime
            dt = datetime.fromisoformat(date_string)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # If parsing fails, return the original string
        return date_string

def extract_escalation_weightage(ticket_data):
    """Extract escalation weightage from ticket data"""
    try:
        # Check if escalation weightage exists in custom fields
        if hasattr(ticket_data, 'fields'):
            fields = ticket_data.fields
            # Look for common escalation weightage field names
            escalation_fields = [
                'customfield_escalation_weightage',
                'escalation_weightage',
                'customfield_10001',  # Common custom field ID
                'customfield_10002',
                'customfield_10003'
            ]
            
            for field_name in escalation_fields:
                if hasattr(fields, field_name):
                    value = getattr(fields, field_name)
                    if value is not None and value != '':
                        return str(value)
        
        # Check if it's in the raw data
        if isinstance(ticket_data, dict):
            fields = ticket_data.get('fields', {})
            for field_name in ['customfield_escalation_weightage', 'escalation_weightage']:
                if field_name in fields:
                    value = fields[field_name]
                    if value is not None and value != '':
                        return str(value)
        
        return None
    except Exception:
        return None

def clean_html_content(html_content):
    """Clean HTML content and extract plain text"""
    if not html_content:
        return ""
    
    # If it's already a string, try to parse it
    if isinstance(html_content, str):
        try:
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Handle specific JIRA formatting
            # Replace <br> tags with newlines
            for br in soup.find_all('br'):
                br.replace_with('\n')
            
            # Replace <p> tags with newlines
            for p in soup.find_all('p'):
                p.replace_with(p.get_text() + '\n')
            
            # Replace <div> tags with newlines
            for div in soup.find_all('div'):
                div.replace_with(div.get_text() + '\n')
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace and normalize
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line:  # Only add non-empty lines
                    lines.append(line)
            
            # Join lines with proper spacing
            text = '\n'.join(lines)
            
            # Remove excessive whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newlines
            text = re.sub(r' +', ' ', text)  # Replace multiple spaces with single space
            
            return text.strip()
        except Exception as e:
            # If parsing fails, try to extract basic text
            try:
                # Simple regex to remove HTML tags
                text = re.sub(r'<[^>]+>', '', html_content)
                # Decode HTML entities
                text = html.unescape(text)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                return text
            except:
                # If all else fails, return the original content
                return str(html_content)
    else:
        return str(html_content)

def clean_html_content_with_markdown(html_content):
    """Clean HTML content and preserve markdown formatting with better readability"""
    if not html_content:
        return ""
    
    # If it's already a string, try to parse it
    if isinstance(html_content, str):
        try:
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Handle specific JIRA formatting while preserving markdown
            # Replace <br> tags with newlines
            for br in soup.find_all('br'):
                br.replace_with('\n')
            
            # Replace <p> tags with newlines
            for p in soup.find_all('p'):
                p.replace_with(p.get_text() + '\n')
            
            # Replace <div> tags with newlines
            for div in soup.find_all('div'):
                div.replace_with(div.get_text() + '\n')
            
            # Handle bold tags - convert to markdown
            for strong in soup.find_all(['strong', 'b']):
                strong.replace_with(f"**{strong.get_text()}**")
            
            # Handle italic tags - convert to markdown
            for em in soup.find_all(['em', 'i']):
                em.replace_with(f"*{em.get_text()}*")
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace and normalize
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line:  # Only add non-empty lines
                    lines.append(line)
            
            # Join lines with proper spacing
            text = '\n'.join(lines)
            
            # Remove excessive whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newlines
            text = re.sub(r' +', ' ', text)  # Replace multiple spaces with single space
            
            # Format the text for better readability
            text = format_jira_content_improved(text)
            
            return text.strip()
        except Exception as e:
            # If parsing fails, try to extract basic text
            try:
                # Simple regex to remove HTML tags but preserve markdown-like patterns
                text = re.sub(r'<(?!\/?(strong|b|em|i))[^>]+>', '', html_content)
                # Decode HTML entities
                text = html.unescape(text)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                # Format the text for better readability
                text = format_jira_content_improved(text)
                return text
            except:
                # If all else fails, return the original content formatted
                return format_jira_content_improved(str(html_content))
    else:
        return format_jira_content_improved(str(html_content))

def format_jira_content(text):
    """Format JIRA content for better readability"""
    if not text:
        return ""
    
    # Handle common JIRA formatting patterns
    formatted_lines = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle problem statement
        if line.startswith('*Problem statement:*'):
            formatted_lines.append('')
            formatted_lines.append('**🔍 Problem Statement:**')
            formatted_lines.append(line.replace('*Problem statement:*', '').strip())
            continue
            
        # Handle other section headers
        if line.startswith('*') and line.endswith('*:') and ':' in line:
            # Extract the section name
            section_name = line.replace('*', '').replace(':', '').strip()
            formatted_lines.append('')
            formatted_lines.append(f'**📋 {section_name}:**')
            continue
            
        # Handle account IDs
        if '[~accountid:' in line:
            # Skip account ID lines or format them nicely
            continue
            
        # Handle version information
        if '*XO Platform Version*:' in line or '*Product Line Version*:' in line:
            version_info = line.replace('*', '').strip()
            formatted_lines.append(f'**🔧 {version_info}**')
            continue
            
        # Handle regular content
        if line:
            # Clean up any remaining asterisks that aren't part of markdown
            cleaned_line = re.sub(r'(?<!\*)\*(?!\*)', '', line)  # Remove single asterisks
            if cleaned_line.strip():
                formatted_lines.append(cleaned_line.strip())
    
    # Join lines with proper spacing
    result = '\n'.join(formatted_lines)
    
    # Clean up excessive whitespace
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)  # Replace multiple newlines with double newlines
    result = re.sub(r' +', ' ', result)  # Replace multiple spaces with single space
    
    return result.strip()

def format_jira_content_improved(text):
    """Format JIRA content for better readability with proper line breaks and filtering"""
    if not text:
        return ""
    
    # Clean the text first
    text = str(text).strip()
    
    # Define all possible sections we want to format
    section_mappings = {
        '*Problem statement:*': '**🔍 Problem Statement:**',
        '*Is this replicating:*': '**🔄 Is this replicating:**',
        '*Frequency of replication:*': '**📊 Frequency of replication:**',
        '*Steps to replicate:*': '**📋 Steps to Reproduce:**',
        '*Steps to reproduce:*': '**📋 Steps to Reproduce:**',
        '*Analysis by L1:*': '**🔍 Analysis by L1:**',
        '*L1 analysis:*': '**🔍 L1 Analysis:**',
        '*Is the customer able to share the bot with us:*': '**🤝 Customer Bot Sharing:**',
        '*Prioritization criteria*': '**⚖️ Prioritization Criteria:**',
        '*Business impact for the customer:*': '**💼 Business Impact:**',
        '*Logs pulled already:*': '**📋 Logs Pulled:**',
        '*Logs awaited:*': '**⏳ Logs Awaited:**',
        '*Related/Similar internal tickets:*': '**🔗 Related Tickets:**',
        '*HAR file collected:*': '**📁 HAR File:**',
        '*Screenshots/Call/Screen-recordings:*': '**📸 Screenshots/Recordings:**',
        '*XO Platform Version*:': '**🔧 XO Platform Version:**',
        '*Product Line Version*:': '**🔧 Product Line Version:**'
    }
    
    # Split text into lines for processing
    lines = text.split('\n')
    formatted_sections = []
    current_section = None
    section_content = ""  # Initialize section_content variable
    current_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines at the beginning of processing
        if not line and not current_section:
            i += 1
            continue
        
        # Check if this line starts a new section
        section_found = False
        for jira_pattern, display_pattern in section_mappings.items():
            if line.startswith(jira_pattern) or jira_pattern.lower() in line.lower():
                # Save previous section if exists
                if current_section and current_content:
                    section_content = '\n'.join(current_content).strip()
                    if section_content:
                        if 'Steps to Reproduce' in current_section:
                            # Format steps as numbered list
                            formatted_sections.append(format_steps_section(current_section, section_content))
                        else:
                            formatted_sections.append(f'{current_section}\n{section_content}')
                
                # Start new section
                current_section = display_pattern
                current_content = []
                
                # Check if content is on the same line
                remaining_line = line.replace(jira_pattern, '').strip()
                if remaining_line:
                    current_content.append(remaining_line)
                
                section_found = True
                break
        
        if not section_found:
            # This line is content for the current section
            if current_section:
                # Clean up the line
                cleaned_line = clean_jira_line(line)
                if cleaned_line:
                    current_content.append(cleaned_line)
            else:
                # No section yet, treat as general content
                cleaned_line = clean_jira_line(line)
                if cleaned_line:
                    formatted_sections.append(cleaned_line)
        
        i += 1
    
    # Don't forget the last section
    if current_section and current_content:
        section_content = '\n'.join(current_content).strip()
        if section_content:
            if 'Steps to Reproduce' in current_section:
                formatted_sections.append(format_steps_section(current_section, section_content))
            else:
                formatted_sections.append(f'{current_section}\n{section_content}')
    
    # Join all sections with proper spacing
    result = '\n\n'.join(formatted_sections)
    
    # Final cleanup
    result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)  # Normalize multiple newlines
    result = re.sub(r' +', ' ', result)  # Normalize multiple spaces
    
    return result.strip()

def clean_jira_line(line):
    """Clean a single line of JIRA content"""
    if not line:
        return ""
    
    # Remove account IDs
    line = re.sub(r'\[~accountid:[^\]]+\]', '', line)
    
    # Remove file attachments and media
    line = re.sub(r'!.*?\.(mp4|zip|png|jpg|jpeg|gif|mov|avi|pdf|doc|docx)\|.*?!', '[File Attachment]', line)
    line = re.sub(r'\[.*?\.(mp4|zip|png|jpg|jpeg|gif|mov|avi|pdf|doc|docx)\]', '[File Attachment]', line)
    
    # Remove team mentions and cc sections
    line = re.sub(r'cc\s*:\s*\[.*?\]\s*\(.*?\)', '', line)
    
    # Remove complex external links but keep simple ones
    line = re.sub(r'\[([^\]]+)\|https?://[^\]]+\]', r'\1', line)  # Convert [text|url] to text
    
    # Clean up single asterisks that aren't markdown
    line = re.sub(r'(?<!\*)\*(?!\*)', '', line)
    
    # Clean up excessive whitespace
    line = re.sub(r'\s+', ' ', line).strip()
    
    return line

def format_steps_section(section_header, content):
    """Format steps to reproduce as a numbered list"""
    lines = content.split('\n')
    steps = []
    step_number = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip lines that are clearly not steps
        if (line.startswith('!') or line.startswith('[File') or 
            line.startswith('cc') or len(line) < 3):
            continue
        
        # Clean the step
        clean_step = clean_jira_line(line)
        if clean_step and len(clean_step) > 3:
            # Remove step numbering if it already exists
            clean_step = re.sub(r'^\d+\.\s*', '', clean_step)
            steps.append(f"{step_number}. {clean_step}")
            step_number += 1
    
    if steps:
        return f'{section_header}\n' + '\n'.join(steps)
    else:
        return f'{section_header}\n{content}'

def get_status_color(status):
    """Get color for status highlighting"""
    status_lower = status.lower()
    if status_lower in ['closed', 'resolved', 'done', 'completed']:
        return '#28a745'  # Green
    elif status_lower in ['open', 'to do', 'new']:
        return '#17a2b8'  # Blue
    elif status_lower in ['in progress', 'in development', 'working']:
        return '#ffc107'  # Yellow
    elif status_lower in ['blocked', 'waiting', 'on hold', 'pending']:
        return '#dc3545'  # Red
    elif status_lower in ['reopened', 'reopened']:
        return '#fd7e14'  # Orange
    else:
        return '#6c757d'  # Gray

def get_priority_color(priority):
    """Get color for priority highlighting"""
    priority_lower = priority.lower()
    if priority_lower in ['highest', 'critical', 'urgent']:
        return '#dc3545'  # Red
    elif priority_lower in ['high']:
        return '#fd7e14'  # Orange
    elif priority_lower in ['medium', 'normal']:
        return '#ffc107'  # Yellow
    elif priority_lower in ['low', 'lowest']:
        return '#28a745'  # Green
    else:
        return '#6c757d'  # Gray

def calculate_escalation_weightage(ticket):
    """Calculate escalation weightage based on ticket properties"""
    weightage = 0
    
    # Check for escalation labels
    labels = ticket.get('labels', [])
    if isinstance(labels, str):
        labels = [label.strip() for label in labels.split(',') if label.strip()]
    
    escalation_keywords = ['escalated', 'urgent', 'critical', 'high_priority']
    for label in labels:
        if any(keyword in label.lower() for keyword in escalation_keywords):
            weightage += 30
    
    # Check priority
    priority = ticket.get('priority', '').lower()
    if priority == 'high':
        weightage += 25
    elif priority == 'highest':
        weightage += 35
    elif priority == 'medium':
        weightage += 15
    elif priority == 'low':
        weightage += 5
    
    # Check status (some statuses indicate escalation)
    status = ticket.get('status', '').lower()
    escalation_statuses = ['blocked', 'waiting', 'on hold', 'escalated']
    if any(escalation_status in status for escalation_status in escalation_statuses):
        weightage += 20
    
    # Check if it's a bug (bugs often have higher escalation)
    issue_type = ticket.get('issue_type', '').lower()
    if issue_type == 'bug':
        weightage += 10
    
    return min(weightage, 100)  # Cap at 100%

def export_json(similar_tickets, target_ticket):
    """Export results as JSON"""
    export_data = {
        'analysis_date': datetime.now().isoformat(),
        'target_ticket': target_ticket,
        'similar_tickets': similar_tickets
    }
    st.download_button(
        label="⬇️ Download JSON",
        data=json.dumps(export_data, indent=2),
        file_name=f"jira_similarity_{target_ticket.get('key', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def export_csv(similar_tickets, target_ticket):
    """Export results as CSV"""
    import pandas as pd
    df = pd.DataFrame(similar_tickets)
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"jira_similarity_{target_ticket.get('key', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_summary(similar_tickets, target_ticket):
    """Export results as summary text"""
    summary = f"""
JIRA Similarity Analysis Summary
================================

Target Ticket: {target_ticket.get('key', 'Unknown')}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Similar Tickets Found: {len(similar_tickets)}

Top Similar Tickets:
"""
    
    for i, ticket in enumerate(similar_tickets[:5], 1):
        summary += f"""
{i}. {ticket.get('key', 'Unknown')} - {ticket.get('summary', 'No summary')}
   Similarity: {ticket.get('similarity', 0):.2%}
   Status: {ticket.get('status', 'Unknown')}
   Priority: {ticket.get('priority', 'Unknown')}
"""
    
    st.download_button(
        label="⬇️ Download Summary",
        data=summary,
        file_name=f"jira_similarity_summary_{target_ticket.get('key', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def analyze_comments_for_fixes(ticket_key, jira_client):
    """Comprehensive analysis of all comments in a ticket to understand what's happening"""
    try:
        # Get all ticket comments
        logger.info(f"🔍 Starting comment analysis for {ticket_key}")
        comments = jira_client.get_comments(ticket_key)
        
        if not comments:
            logger.warning(f"⚠️ No comments returned from JIRA API for {ticket_key}")
            return None  # Return None instead of a message when no comments
        
        logger.info(f"✅ Retrieved {len(comments)} comments for analysis")
        
        # Initialize analysis containers
        timeline_events = []
        stakeholders = set()
        problem_evolution = []
        solutions_attempted = []
        current_status_insights = []
        root_causes = []
        workarounds = []
        
        # Enhanced keyword categories for better analysis
        keywords = {
            'solutions': ['fix', 'solution', 'resolved', 'fixed', 'patch', 'update', 'workaround', 'resolve'],
            'problems': ['error', 'issue', 'problem', 'bug', 'failure', 'failed', 'broken', 'not working'],
            'actions': ['restart', 'clear', 'refresh', 'reinstall', 'reconfigure', 'deploy', 'test', 'check'],
            'status': ['working', 'testing', 'deployed', 'verified', 'confirmed', 'reproduced', 'investigating'],
            'escalation': ['urgent', 'critical', 'escalate', 'priority', 'customer', 'impact', 'production'],
            'technical': ['timeout', 'slow', 'hanging', 'crashing', 'config', 'configuration', 'api', 'service'],
            'root_cause': ['caused by', 'root cause', 'because of', 'due to', 'reason', 'source of'],
            'next_steps': ['next step', 'will', 'plan to', 'going to', 'need to', 'should', 'todo']
        }
        
        # Process each comment chronologically
        for i, comment in enumerate(comments):
            comment_text = comment.get('body', '')
            if isinstance(comment_text, str):
                clean_text = clean_html_content(comment_text)
                
                # Extract comment metadata
                author = comment.get('author', {}).get('displayName', 'Unknown')
                created = comment.get('created', 'Unknown')
                stakeholders.add(author)
                
                # Categorize comment content
                comment_analysis = {
                'index': i + 1,
                'author': author,
                'created': format_date(created) if created != 'Unknown' else 'Unknown',
                'text': clean_text,
                'categories': [],
                'insights': []
                }
                
                text_lower = clean_text.lower()
                
                # Analyze comment for different types of content
                for category, category_keywords in keywords.items():
                    if any(keyword in text_lower for keyword in category_keywords):
                        comment_analysis['categories'].append(category)
                        
                        # Extract specific insights based on category
                        if category == 'solutions':
                            solutions_attempted.extend(extract_solutions(clean_text, category_keywords))
                        elif category == 'problems':
                            problem_evolution.append({
                                'author': author,
                                'date': created,
                                'problem': extract_problem_details(clean_text, category_keywords)
                            })
                        elif category == 'root_cause':
                            root_causes.extend(extract_root_causes(clean_text))
                        elif category == 'status':
                            current_status_insights.append({
                                'author': author,
                                'date': created,
                                'status': extract_status_updates(clean_text, keywords['status'])
                            })
                
                timeline_events.append(comment_analysis)
        
        # Generate comprehensive analysis report
        return generate_comprehensive_comment_analysis(
            ticket_key, timeline_events, stakeholders, problem_evolution,
            solutions_attempted, current_status_insights, root_causes, workarounds
        )
        
    except Exception as e:
        return f"Error analyzing comments: {str(e)}"

def extract_solutions(text, solution_keywords):
    """Extract solution details from comment text"""
    solutions = []
    sentences = text.split('.')
                    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in solution_keywords):
            if len(sentence) > 15:  # Only substantial solutions
                solutions.append(sentence)
    
    return solutions

def extract_problem_details(text, problem_keywords):
    """Extract problem descriptions from comment text"""
    problems = []
    sentences = text.split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in problem_keywords):
            if len(sentence) > 10:
                problems.append(sentence)
    
    return ' '.join(problems) if problems else text[:100] + "..."

def extract_root_causes(text):
    """Extract root cause information from comment text"""
    root_causes = []
    # Look for sentences that explain causation
    patterns = ['caused by', 'due to', 'because of', 'root cause', 'reason is', 'issue is']
    
    for pattern in patterns:
        if pattern in text.lower():
            # Extract the sentence containing the root cause
            sentences = text.split('.')
            for sentence in sentences:
                if pattern in sentence.lower() and len(sentence.strip()) > 10:
                    root_causes.append(sentence.strip())
    
    return root_causes

def extract_status_updates(text, status_keywords):
    """Extract status update information from comment text"""
    status_info = []
    sentences = text.split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in status_keywords):
            if len(sentence) > 5:
                status_info.append(sentence)
    
    return ' '.join(status_info) if status_info else text[:50] + "..."

def generate_comprehensive_comment_analysis(ticket_key, timeline_events, stakeholders, 
                                          problem_evolution, solutions_attempted, 
                                          current_status_insights, root_causes, workarounds):
    """Generate a comprehensive analysis report of all comments"""
    
    # Don't generate a report if there are no comments or meaningful content
    if not timeline_events or len(timeline_events) == 0:
        return None
    
    # Check if there's any meaningful content beyond just basic comments
    has_meaningful_content = (
        len(solutions_attempted) > 0 or 
        len(problem_evolution) > 0 or 
        len(root_causes) > 0 or 
        len(current_status_insights) > 0 or
        len(timeline_events) > 2  # More than just 1-2 basic comments
    )
    
    # If no meaningful content, don't show the analysis
    if not has_meaningful_content:
        return None
    
    report = f"## 💬 Comprehensive Comment Analysis for {ticket_key}\n\n"
    report += f"**📊 Total Comments:** {len(timeline_events)} | **👥 Stakeholders:** {len(stakeholders)}\n\n"
    
    # Stakeholder Summary
    if stakeholders:
        report += "### 👥 Key Stakeholders Involved:\n"
        for stakeholder in sorted(stakeholders):
            report += f"• **{stakeholder}**\n"
        report += "\n"
    
    # Problem Evolution Timeline
    if problem_evolution:
        report += "### 🔄 Problem Evolution Timeline:\n"
        for i, problem in enumerate(problem_evolution[:3], 1):  # Show top 3
            report += f"**{i}.** *{problem['author']}* ({problem['date']}): {problem['problem'][:100]}...\n"
        report += "\n"
    
    # Solutions and Attempts
    if solutions_attempted:
        report += "### 🔧 Solutions & Fixes Attempted:\n"
        unique_solutions = list(set(solutions_attempted))[:5]  # Top 5 unique solutions
        for i, solution in enumerate(unique_solutions, 1):
            report += f"**{i}.** {solution[:150]}...\n"
        report += "\n"
    
    # Root Causes Identified
    if root_causes:
        report += "### 🎯 Root Causes Identified:\n"
        unique_causes = list(set(root_causes))[:3]  # Top 3 unique causes
        for i, cause in enumerate(unique_causes, 1):
            report += f"**{i}.** {cause[:150]}...\n"
        report += "\n"
    
    # Current Status Insights
    if current_status_insights:
        report += "### 📈 Latest Status Updates:\n"
        # Show the most recent status updates
        recent_updates = current_status_insights[-3:] if len(current_status_insights) > 3 else current_status_insights
        for update in recent_updates:
            report += f"• **{update['author']}**: {update['status'][:100]}...\n"
        report += "\n"
    
    # Key Insights Summary
    report += "### 🧠 Key Insights:\n"
    
    # Analyze comment patterns
    total_comments = len(timeline_events)
    if total_comments > 10:
        report += f"• **High Activity**: {total_comments} comments indicate active investigation/resolution\n"
    elif total_comments > 5:
        report += f"• **Moderate Activity**: {total_comments} comments show ongoing attention\n"
    else:
        report += f"• **Low Activity**: {total_comments} comments - may need more attention\n"
    
    if len(stakeholders) > 3:
        report += f"• **Multi-team Involvement**: {len(stakeholders)} people involved suggests complex issue\n"
    
    if solutions_attempted:
        report += f"• **Active Resolution**: {len(solutions_attempted)} solution attempts documented\n"
    
    if root_causes:
        report += f"• **Root Cause Analysis**: {len(root_causes)} potential causes identified\n"
    
    # Recent Activity Analysis
    if timeline_events:
        latest_comment = timeline_events[-1]
        report += f"• **Latest Activity**: Last comment by {latest_comment['author']} on {latest_comment['created']}\n"
    
    report += "\n"
    
    # Detailed Timeline (last 5 comments)
    report += "### 📅 Recent Comment Timeline:\n"
    recent_comments = timeline_events[-5:] if len(timeline_events) > 5 else timeline_events
    
    for comment in recent_comments:
        categories_str = ', '.join(comment['categories']) if comment['categories'] else 'General'
        report += f"**Comment #{comment['index']}** - *{comment['author']}* ({comment['created']})\n"
        report += f"📂 *Categories: {categories_str}*\n"
        report += f"{comment['text'][:200]}...\n\n"
        report += "---\n\n"
    
    return report

def generate_fix_suggestions(ticket, target_ticket):
    """Generates fix suggestions based on ticket status and content."""
    suggestions = {}
    
    # Get ticket status and description
    status = ticket.get('status', '').lower()
    description = ticket.get('description', '')
    
    # Check if ticket is resolved/closed
    if status in ['closed', 'resolved', 'done']:
        if description:
            desc_text = clean_html_content(description)
            suggestions['type'] = 'Resolved Ticket'
            suggestions['confidence'] = 'High'
            
            # Look for specific fix indicators
            if any(keyword in desc_text.lower() for keyword in ['fixed', 'resolved', 'solution', 'workaround']):
                suggestions['description'] = f"This ticket was resolved. Key details: {desc_text[:200]}..."
            else:
                suggestions['description'] = f"Ticket resolved. Description: {desc_text[:200]}..."
        else:
            suggestions['type'] = 'Resolved Ticket'
            suggestions['confidence'] = 'Medium'
            suggestions['description'] = "This ticket was resolved but no detailed description available."
    
    # Check if ticket is in progress
    elif status in ['in progress', 'ready for qa', 'testing']:
        if description:
            desc_text = clean_html_content(description)
            suggestions['type'] = 'In Progress'
            suggestions['confidence'] = 'Medium'
            suggestions['description'] = f"Ticket is being worked on. Current status: {desc_text[:200]}..."
        else:
            suggestions['type'] = 'In Progress'
            suggestions['confidence'] = 'Low'
            suggestions['description'] = "Ticket is currently being worked on."
    
    # Check if ticket is open/new
    elif status in ['open', 'new', 'to do']:
        if description:
            desc_text = clean_html_content(description)
            suggestions['type'] = 'Open Ticket'
            suggestions['confidence'] = 'Low'
            suggestions['description'] = f"Open ticket with description: {desc_text[:200]}..."
        else:
            suggestions['type'] = 'Open Ticket'
            suggestions['confidence'] = 'Low'
            suggestions['description'] = "Open ticket with no detailed description."
    
    # Default case
    else:
        suggestions['type'] = f'Ticket ({status.title()})'
        suggestions['confidence'] = 'Low'
        suggestions['description'] = f"Ticket status: {status}. Check comments for more details."
    
    # Add similarity context
    similarity = ticket.get('similarity', 0)
    if similarity > 0.5:
        suggestions['description'] += f"\n\n**High similarity ({similarity:.1%})** - This ticket is very similar to your issue."
    elif similarity > 0.3:
        suggestions['description'] += f"\n\n**Moderate similarity ({similarity:.1%})** - This ticket has some relevance to your issue."
    
    return suggestions

def main():
    """Main application"""
    # Beautiful Header
    st.markdown("""
    <div class="hero-header">
        <h1>🔍 JIRA Similarity Tool</h1>
        <p>Discover similar tickets and find solutions from past issues with intelligent analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Load existing config
        config = {}
        config_locations = ['config.json']
        
        # Also check temporary directory for config
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_config = os.path.join(temp_dir, 'jira_config.json')
            config_locations.append(temp_config)
        except:
            pass
        
        for config_file in config_locations:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        break  # Use the first valid config found
                except:
                    continue
        
        # Configuration inputs
        jira_url = st.text_input(
            "🌐 JIRA URL",
            value=config.get('jira_url', 'https://koreteam.atlassian.net'),
            help="Your JIRA instance URL"
        )
        
        username = st.text_input(
            "👤 Username",
            value="",
            help="Your JIRA username or email (leave blank to use configured value)"
        )
        
        api_token = st.text_input(
            "🔑 API Token",
            value="",
            type="password",
            help="Your JIRA API token (leave blank to use configured value)"
        )
        
        project_key = st.text_input(
            "📁 Project Key",
            value=config.get('project_key', 'PLAT'),
            help="JIRA project key (e.g., PLAT)"
        )
        
        # Save configuration
        if st.button("💾 Save Configuration", type="primary"):
            config_data = {
                'jira_url': jira_url,
                'username': username,
                'api_token': api_token,
                'project_key': project_key
            }
            success, message = save_config(config_data)
            if success:
                st.success(message)
            else:
                st.error(message)
        
        st.markdown("---")
        
        # Analysis settings
        st.markdown("## 🔧 Analysis Settings")
        
        threshold = st.slider(
            "🎯 Similarity Threshold (%)",
            min_value=0.10,
            max_value=1.0,
            value=0.20,
            step=0.10,
            help="Minimum similarity percentage to include tickets. Tickets with only metadata similarity (same project/type) but no content similarity will be excluded."
        )
        
        max_results = st.slider(
            "📊 Max Results",
            min_value=5,
            max_value=50,
            value=10,
            help="Maximum number of similar tickets to return"
        )
        
        st.markdown("---")
        
        # Features
        st.markdown("## ✨ Features")
        st.markdown("""
        - 🔍 **Content-aware search**
        - 🎯 **Problem pattern recognition**
        - 💡 **Fix suggestions**
        - 📊 **Detailed analysis**
        - 📤 **Export results**
        - 🚀 **Real-time updates**
        """)
    
    # Main content
    st.markdown("## 🚀 Quick Start")
    
    # Prefill from URL query params
    try:
        url_ticket = st.query_params.get('ticket')
        if url_ticket and 'prefilled_ticket_key' not in st.session_state:
            st.session_state['prefilled_ticket_key'] = url_ticket
    except Exception:
        pass
    
    # Input section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        ticket_key = st.text_input(
            "Enter JIRA Ticket Key",
            placeholder="e.g., PLAT-45685",
            help="Enter the ticket key you want to find similar tickets for",
            value=st.session_state.get('prefilled_ticket_key', "")
        )
        # Keep latest in session state
        st.session_state['prefilled_ticket_key'] = ticket_key
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary")
    
    # Analysis section
    if analyze_button and not ticket_key:
        st.error("❌ Please enter a JIRA Ticket Key before analyzing.")
        return
    
    if analyze_button and ticket_key:
        effective_username = username or config.get('username', '')
        effective_api_token = api_token or config.get('api_token', '')
        if not effective_username or not effective_api_token:
            st.error("❌ Please provide username and API token, or configure them in config.json.")
            return
        
        # Create configuration
        current_config = {
            'jira_url': jira_url,
            'username': effective_username,
            'api_token': effective_api_token,
            'project_key': project_key
        }
        
        # Initialize tool
        with st.spinner("🔍 Initializing JIRA Similarity Tool..."):
            try:
                # Save current config to a temporary file for the tool
                temp_config_file = f"temp_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_config_file, 'w') as f:
                    json.dump(current_config, f, indent=2)
                
                tool = JIRASimilarityTool(config_file=temp_config_file)
                
                # Clean up temporary file
                try:
                    os.remove(temp_config_file)
                except:
                    pass
                
                st.markdown("""
                <div style="background-color: #28a745; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: left; font-weight: bold;">
                ✅ Tool initialized successfully!
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Failed to initialize tool: {e}")
                return
        
        # Perform analysis
        results = None
        with st.spinner(f"🔍 Analyzing ticket {ticket_key}..."):
            try:
                # Perform the similarity analysis directly
                results = analyze_ticket_safely(tool, ticket_key, threshold, max_results)
                    
            except Exception as e:
                st.error(f"❌ **Analysis Error!** Failed to perform similarity analysis: {e}")
                st.info("💡 **Please check:**")
                st.info("1. Your JIRA URL is correct")
                st.info("2. Your username and API token are valid")
                return
        
        # Display results
        if results and results['success']:
            display_results(results['results'], ticket_key, threshold, max_results, tool)
        elif results:
            st.error(f"❌ Analysis failed: {results['message']}")
            
            # Show detailed error information
            with st.expander("🔍 Error Details"):
                st.code(results['message'])
        else:
            st.error("❌ Analysis could not be completed due to connection issues.")
    
    # Information section
    elif not analyze_button:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="modern-card" style="height: 300px; display: flex; flex-direction: column;">
                <h3>📋 How to Use</h3>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <ol style="margin: 0; padding-left: 1.5rem;">
                        <li>Configure your JIRA credentials in the sidebar</li>
                        <li>Enter a JIRA ticket key above</li>
                        <li>Click Analyze to find similar tickets</li>
                        <li>Review results and export if needed</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="modern-card" style="height: 300px; display: flex; flex-direction: column;">
                <h3>✨ Features</h3>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li>Content-aware search with problem pattern recognition</li>
                        <li>Includes closed tickets to find solutions</li>
                        <li>Smart similarity analysis focusing on content</li>
                        <li>Export results as JSON or CSV</li>
                        <li>Real-time configuration updates</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Add Notes section explaining how the tool works
    with st.expander("📚 How This Tool Works - Notes", expanded=False):
        st.markdown("""
        ## 🔍 JIRA Similarity Tool — How It Works (Current)
        
        ### 🎯 What this does
        Finds similar tickets that refer to the same subject/feature (e.g., "goal completion rate", "performance dashboard", "user id filter", "gen ai node"), so you can reuse fixes/workarounds.
        
        ### 🧱 Candidate search (where we look)
        - Projects: prefer `PLAT` and `XOP`
        - Issue types: `Bug`, `Customer-Incident`, `Customer-Defect`
        - Query terms from the target ticket:
          - Full summary
          - Subject/feature terms extracted from the summary
          - 2‑gram and 3‑gram phrases from the summary
        - Fallback: if a query yields nothing under the constraints, retry in the current project scope
        - Duplicates are removed by key
        
        ### ✂️ Text preprocessing (what we ignore)
        - Lowercases text
        - Strips generic status/function phrases so they don't affect similarity:
          "not functioning", "not working", "as expected", "unexpected", "issue with",
          "error occurred", "failed", "failure", "failing", "throws error", "showing error"
        - Removes punctuation (keeps hyphens) and normalizes whitespace
        
        ### 🎯 Subject-first matching (hard gate)
        - We extract subject/feature terms (e.g., dashboard/report/metric/filter/log/usage/userid/node/flag/field/api/connector/import/migration/genai/llm/gpt/dialoggpt)
        - A candidate is considered only if it shares at least one subject term with the target summary
        - This prevents unrelated tickets (e.g., migrations/admin console) from matching a "performance dashboard" subject
        
        ### 📐 Similarity scoring (content-first)
        - Subject similarity: 50%
        - Summary keyword overlap: 35%
        - Technical term overlap: 10%
        - Overall Jaccard overlap: 5%
        - Metadata (type, priority, labels, components, project): 0% (not weighted)
        - Small bonus for similar summary length
        
        ### 🎚️ Thresholds and fallback
        - Primary threshold is user‑controlled (default 0.20)
        - If no results pass and there are candidates, we retry once at `threshold − 0.10` (min 0.10)
        
        ### 🧩 When no similar tickets are found
        - The UI shows the target ticket's details (key, summary, status, type, assignee, reporter, created, priority) and a JIRA link so you can proceed with full context
        
        ### 🔧 Where this logic lives
        - Subject extraction and preprocessing: `SimilarityAnalyzer`
        - Search constraints and subject gate: `JIRASimilarityTool.analyze_similarity()`
        - Scoring: `SimilarityAnalyzer.calculate_similarity()`
        
        ### 📌 DialogGPT example (subject-first)
        - Target summary: "DialogGPT: Repeat Response Event firing incorrectly for imported app"
        - Extracted subjects: dialog gpt, repeat response event, event, response, imported app
        - Included (subject overlap):
          - [PLAT-45859](https://koreteam.atlassian.net/browse/PLAT-45859) — repeat response feature relates to Repeat Response Event / DialogGPT
          - [PLAT-46639](https://koreteam.atlassian.net/browse/PLAT-46639) — DialogGPT task failure event (same DialogGPT/event subject)
        - Excluded (no subject overlap):
          - [PLAT-46201](https://koreteam.atlassian.net/browse/PLAT-46201) — admin console / migration topics (different subject)
        
        Tip: Lower the threshold slightly if your summary is very generic, or refine the summary to include the concrete subject/feature.
        """)

if __name__ == "__main__":
    main() 
