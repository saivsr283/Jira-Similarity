#!/usr/bin/env python3
"""
Simple JQL Test Script
Test JQL queries step by step to find what works
"""

import json
import requests
from jira_similarity_tool import JIRAClient

def test_jql_queries():
    """Test different JQL queries to find what works"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize client
    jira_client = JIRAClient(
        config.get('jira_url'),
        config.get('username'),
        None  # token must be provided via UI; this script is for basic connectivity only
    )
    
    # First, let's try to get available projects
    print("🔍 Testing Available Projects...")
    print("=" * 50)
    
    try:
        # Try to get projects
        response = jira_client.session.get(
            f"{jira_client.base_url}/rest/api/3/project",
            params={'maxResults': 50}
        )
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Found {len(projects)} projects:")
            for project in projects[:10]:  # Show first 10
                print(f"  - {project.get('key', 'N/A')}: {project.get('name', 'N/A')}")
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            print(f"Error: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error getting projects: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔍 Testing JQL Queries...")
    print("=" * 50)
    
    # Test queries from simple to complex
    test_queries = [
        {
            "name": "1. ZTP Project",
            "query": "project = ZTP",
            "description": "Zephyr Test Project"
        },
        {
            "name": "2. TFF Project",
            "query": "project = TFF",
            "description": "Test For Filters"
        },
        {
            "name": "3. BPS Project",
            "query": "project = BPS",
            "description": "Bots Platform - Support"
        },
        {
            "name": "4. ZTP with Bug",
            "query": "project = ZTP AND issuetype = Bug",
            "description": "ZTP with Bug issue type only"
        },
        {
            "name": "5. ZTP Recent",
            "query": "project = ZTP AND created >= 2024-01-01",
            "description": "ZTP issues since 2024"
        },
        {
            "name": "6. ZTP Open",
            "query": "project = ZTP AND status != Closed",
            "description": "ZTP non-closed issues"
        }
    ]
    
    for test in test_queries:
        print(f"\n📋 {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Query: {test['query']}")
        
        try:
            response = jira_client.session.get(
                f"{jira_client.base_url}/rest/api/3/search/jql",
                params={
                    'jql': test['query'],
                    'maxResults': 10,
                    'fields': 'key,summary,status'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                print(f"✅ SUCCESS! Found {total} tickets")
                if total > 0:
                    print("Sample tickets:")
                    for issue in data.get('issues', [])[:3]:
                        print(f"  - {issue['key']}: {issue['fields'].get('summary', 'No summary')}")
            else:
                print(f"❌ FAILED! Status: {response.status_code}")
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_jql_queries() 