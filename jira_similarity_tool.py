#!/usr/bin/env python3
"""
JIRA Similarity Analysis Tool
A Python-based tool for analyzing JIRA tickets and finding similar tickets.
"""

import os
import json
import requests
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from urllib.parse import urljoin
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JIRATicket:
    """Data class for JIRA ticket information"""
    key: str
    summary: str
    description: str
    issue_type: str
    priority: str
    status: str
    assignee: str
    reporter: str
    created: str
    updated: str
    labels: List[str]
    components: List[str]
    project: str
    escalation_weightage: Optional[str] = None

class JIRAClient:
    """Client for interacting with JIRA API"""
    
    def __init__(self, base_url: str, username: str, api_token: str, project_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.project_key = project_key or 'PLAT'  # Default to PLAT if not specified
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"JIRA Client initialized:")
        logger.info(f"  Base URL: {self.base_url}")
        logger.info(f"  Username: {self.username}")
        logger.info("  API Token: [REDACTED]")
        logger.info(f"  Project Key: {self.project_key}")
    
    def get_ticket(self, ticket_key: str) -> Optional[JIRATicket]:
        """Fetch a single JIRA ticket by key"""
        try:
            # Try API v2 first, then fallback to v3
            for api_version in ['2', '3']:
                url = urljoin(self.base_url, f'/rest/api/{api_version}/issue/{ticket_key}')
                logger.info(f"🔍 Attempting to fetch ticket {ticket_key} via API v{api_version}")
                logger.info(f"   URL: {url}")
                logger.info(f"   Auth: {self.username}:{self.api_token[:10]}...")
                
                response = self.session.get(url)
                logger.info(f"   Response Status: {response.status_code}")
                logger.info(f"   Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    logger.info(f"✅ Successfully fetched ticket {ticket_key} via API v{api_version}")
                    data = response.json()
                    fields = data['fields']
                    
                    # Extract escalation weightage from custom fields
                    escalation_weightage = None
                    for field_name in ['customfield_escalation_weightage', 'escalation_weightage']:
                        if field_name in fields:
                            value = fields[field_name]
                            if value is not None and value != '':
                                escalation_weightage = str(value)
                                break
                    
                    return JIRATicket(
                        key=data['key'],
                        summary=fields.get('summary', ''),
                        description=fields.get('description', ''),
                        issue_type=fields.get('issuetype', {}).get('name', ''),
                        priority=fields.get('priority', {}).get('name', ''),
                        status=fields.get('status', {}).get('name', ''),
                        assignee=fields.get('assignee', {}).get('displayName', ''),
                        reporter=fields.get('reporter', {}).get('displayName', ''),
                        created=fields.get('created', ''),
                        updated=fields.get('updated', ''),
                        labels=fields.get('labels', []),
                        components=[c.get('name', '') for c in fields.get('components', [])],
                        project=fields.get('project', {}).get('key', ''),
                        escalation_weightage=escalation_weightage
                    )
                elif response.status_code == 404:
                    logger.warning(f"❌ Ticket {ticket_key} not found with API v{api_version}")
                    logger.warning(f"   Response Body: {response.text[:200]}...")
                    continue
                elif response.status_code == 401:
                    logger.error(f"❌ Authentication failed with API v{api_version}")
                    logger.error(f"   Response Body: {response.text[:200]}...")
                    continue
                elif response.status_code == 403:
                    logger.error(f"❌ Access forbidden with API v{api_version}")
                    logger.error(f"   Response Body: {response.text[:200]}...")
                    continue
                else:
                    logger.error(f"❌ Error fetching ticket {ticket_key} with API v{api_version}: {response.status_code}")
                    logger.error(f"   Response Body: {response.text[:200]}...")
                    continue
            
            logger.error(f"❌ Could not fetch ticket {ticket_key} with any API version")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error fetching ticket {ticket_key}: {e}")
            return None
    
    def search_tickets(self, query: str = None, max_results: int = 100) -> List[JIRATicket]:
        """Search for tickets with intelligent content-based queries - INCLUDING CLOSED TICKETS"""
        if not query:
            # Default search for all tickets in the project - INCLUDING CLOSED
            jql = f"project = {self.project_key} ORDER BY created DESC"
        else:
            # Enhanced search with FOCUSED content-based JQL - ONLY summary and description, INCLUDING CLOSED
            # Remove 'text' field which searches comments and causes irrelevant results
            jql = f'project = {self.project_key} AND (summary ~ "{query}" OR description ~ "{query}") ORDER BY created DESC'
        
        logger.info(f"🔍 Searching tickets with JQL: {jql}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/search/jql",
                params={
                    'jql': jql,
                    'maxResults': max_results,
                    'fields': 'key,summary,description,issuetype,priority,status,components,labels,project,assignee,reporter,created,updated'
                },
                headers={'Accept': 'application/json'}
            )
            
            logger.info(f"🔍 Search URL: {response.url}")
            logger.info(f"🔍 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tickets = []
                
                for issue in data.get('issues', []):
                    fields = issue.get('fields', {})
                    
                    # Handle description which might be a dict (rich text) or string
                    description = fields.get('description')
                    if isinstance(description, dict):
                        description = description.get('content', [])
                        if isinstance(description, list):
                            description = ' '.join([str(item.get('text', '')) for item in description])
                        else:
                            description = str(description)
                    
                    ticket = JIRATicket(
                        key=issue.get('key'),
                        summary=fields.get('summary', ''),
                        description=description or '',
                        issue_type=fields.get('issuetype', {}).get('name', ''),
                        priority=fields.get('priority', {}).get('name', ''),
                        status=fields.get('status', {}).get('name', ''),
                        components=[comp.get('name', '') for comp in fields.get('components', [])],
                        labels=fields.get('labels', []),
                        project=fields.get('project', {}).get('key', ''),
                        assignee=fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
                        reporter=fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
                        created=fields.get('created', ''),
                        updated=fields.get('updated', '')
                    )
                    tickets.append(ticket)
                
                logger.info(f"✅ Found {len(tickets)} tickets (including closed tickets)")
                return tickets
            else:
                logger.error(f"❌ Search failed with status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error during search: {e}")
            return []

    def search_tickets_projects_issue_type(self, query: str, projects: List[str], issue_types: List[str], max_results: int = 100) -> List[JIRATicket]:
        """Search tickets constrained to specific projects and issue types."""
        try:
            projects_clause = ', '.join(projects)
            # Quote issue types that contain spaces or hyphens
            issue_types_quoted = []
            for it in issue_types:
                itq = f'"{it}"' if (' ' in it or '-' in it) else it
                issue_types_quoted.append(itq)
            issue_types_clause = ', '.join(issue_types_quoted)
            
            if query and query.strip():
                jql = f'(project in ({projects_clause}) AND issuetype in ({issue_types_clause}) AND (summary ~ "{query}" OR description ~ "{query}")) ORDER BY created DESC'
            else:
                jql = f'(project in ({projects_clause}) AND issuetype in ({issue_types_clause})) ORDER BY created DESC'
            
            response = self.session.get(
                f"{self.base_url}/rest/api/3/search/jql",
                params={
                    'jql': jql,
                    'maxResults': max_results,
                    'fields': 'key,summary,description,issuetype,priority,status,components,labels,project,assignee,reporter,created,updated'
                },
                headers={'Accept': 'application/json'}
            )
            if response.status_code != 200:
                logger.warning(f"Project/type search failed: {response.status_code} {response.text[:180]}")
                return []
            data = response.json()
            tickets: List[JIRATicket] = []
            for issue in data.get('issues', []):
                fields = issue.get('fields', {})
                description = fields.get('description')
                if isinstance(description, dict):
                    description = description.get('content', [])
                    if isinstance(description, list):
                        description = ' '.join([str(item.get('text', '')) for item in description])
                    else:
                        description = str(description)
                tickets.append(JIRATicket(
                    key=issue.get('key'),
                    summary=fields.get('summary', ''),
                    description=description or '',
                    issue_type=fields.get('issuetype', {}).get('name', ''),
                    priority=fields.get('priority', {}).get('name', ''),
                    status=fields.get('status', {}).get('name', ''),
                    components=[comp.get('name', '') for comp in fields.get('components', [])],
                    labels=fields.get('labels', []),
                    project=fields.get('project', {}).get('key', ''),
                    assignee=fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
                    reporter=fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
                    created=fields.get('created', ''),
                    updated=fields.get('updated', '')
                ))
            return tickets
        except Exception as e:
            logger.error(f"❌ Error in project/type search: {e}")
            return []

    def get_comments(self, ticket_key: str) -> list:
        """Get comments for a specific ticket"""
        try:
            logger.info(f"🔍 Fetching comments for ticket: {ticket_key}")
            
            # Try API v3 first using the configured session
            url = f"{self.base_url}/rest/api/3/issue/{ticket_key}/comment"
            
            response = self.session.get(url, timeout=30)
            
            logger.info(f"🔍 Comments API URL: {url}")
            logger.info(f"🔍 Comments Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                comments = data.get('comments', [])
                logger.info(f"✅ Successfully fetched {len(comments)} comments for {ticket_key}")
                return comments
            elif response.status_code == 404:
                logger.warning(f"⚠️ Ticket {ticket_key} not found")
                return []
            else:
                logger.warning(f"⚠️ API v3 failed with status {response.status_code}, trying v2 for comments")
                # Fallback to API v2
                url = f"{self.base_url}/rest/api/2/issue/{ticket_key}/comment"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    comments = data.get('comments', [])
                    logger.info(f"✅ Successfully fetched {len(comments)} comments for {ticket_key} using API v2")
                    return comments
                else:
                    logger.error(f"❌ Failed to get comments with both API v3 and v2: {response.status_code}")
                    logger.error(f"❌ Response content: {response.text[:200]}...")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error getting comments for {ticket_key}: {e}")
            return []

class SimilarityAnalyzer:
    """Analyzes similarity between JIRA tickets"""
    
    def __init__(self):
        # Enhanced stop words for JIRA context
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'i', 'me', 'my', 'myself',
            'we', 'our', 'ours', 'ourselves', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'will', 'would', 'should', 'could', 'may', 'might', 'must', 'shall',
            # JIRA-specific stop words
            'ticket', 'issue', 'bug', 'feature', 'story', 'task', 'epic', 'incident',
            'request', 'problem', 'error', 'failure', 'broken', 'fixed', 'resolved',
            'closed', 'open', 'pending', 'in progress', 'done', 'blocked', 'ready',
            'test', 'testing', 'deploy', 'deployment', 'release', 'version', 'build',
            'code', 'codebase', 'repository', 'branch', 'merge', 'commit', 'push',
            'pull', 'request', 'review', 'approve', 'reject', 'comment', 'update',
            'create', 'delete', 'modify', 'change', 'add', 'remove', 'implement',
            'develop', 'design', 'plan', 'document', 'documentation', 'user', 'customer',
            'client', 'team', 'developer', 'tester', 'analyst', 'manager', 'admin'
        }
        
        # Common technical terms that should be weighted higher
        self.technical_terms = {
            'api', 'database', 'server', 'client', 'frontend', 'backend', 'ui', 'ux',
            'authentication', 'authorization', 'login', 'logout', 'session', 'token',
            'password', 'encryption', 'security', 'ssl', 'https', 'http', 'rest',
            'json', 'xml', 'sql', 'query', 'database', 'table', 'index', 'cache',
            'memory', 'cpu', 'disk', 'network', 'connection', 'timeout', 'error',
            'exception', 'crash', 'hang', 'freeze', 'slow', 'performance', 'latency',
            'throughput', 'bandwidth', 'load', 'stress', 'test', 'unit', 'integration',
            'deployment', 'production', 'staging', 'development', 'environment',
            'configuration', 'setting', 'parameter', 'variable', 'function', 'method',
            'class', 'object', 'interface', 'module', 'component', 'service', 'library',
            'framework', 'plugin', 'extension', 'addon', 'widget', 'button', 'form',
            'input', 'output', 'data', 'file', 'upload', 'download', 'import', 'export',
            'sync', 'async', 'thread', 'process', 'job', 'task', 'queue', 'message',
            'event', 'trigger', 'callback', 'hook', 'webhook', 'notification', 'alert',
            'log', 'logging', 'monitor', 'dashboard', 'report', 'analytics', 'metric',
            'statistic', 'chart', 'graph', 'visualization', 'display', 'render',
            'browser', 'mobile', 'desktop', 'app', 'application', 'website', 'web',
            'cloud', 'aws', 'azure', 'gcp', 'docker', 'container', 'kubernetes',
            'microservice', 'monolith', 'architecture', 'pattern', 'design', 'model',
            # Conversational AI specific terms
            'conversational', 'chatbot', 'bot', 'nlp', 'natural', 'language', 'processing',
            'intent', 'entity', 'utterance', 'response', 'dialog', 'conversation', 'chat',
            'voice', 'speech', 'recognition', 'asr', 'tts', 'text', 'speech', 'synthesis',
            'validation', 'testing', 'test', 'scenario', 'flow', 'workflow', 'pipeline',
            'training', 'model', 'ai', 'machine', 'learning', 'ml', 'algorithm',
            'confidence', 'accuracy', 'precision', 'recall', 'f1', 'score',
            'false', 'positive', 'negative', 'true', 'positive', 'negative',
            'threshold', 'sensitivity', 'specificity', 'roc', 'auc', 'curve',
            'dataset', 'training', 'validation', 'test', 'split', 'cross', 'fold',
            'overfitting', 'underfitting', 'bias', 'variance', 'regularization',
            'feature', 'engineering', 'preprocessing', 'normalization', 'standardization',
            'tokenization', 'lemmatization', 'stemming', 'stop', 'words', 'n-gram',
            'bag', 'words', 'tfidf', 'word2vec', 'glove', 'bert', 'transformer',
            'attention', 'mechanism', 'encoder', 'decoder', 'sequence', 'model',
            'recurrent', 'neural', 'network', 'rnn', 'lstm', 'gru', 'cnn',
            'convolutional', 'neural', 'network', 'deep', 'learning', 'neural', 'network',
            'supervised', 'unsupervised', 'semi', 'supervised', 'reinforcement', 'learning',
            'clustering', 'classification', 'regression', 'prediction', 'forecasting',
            'anomaly', 'detection', 'outlier', 'detection', 'pattern', 'recognition',
            'computer', 'vision', 'image', 'processing', 'object', 'detection',
            'segmentation', 'recognition', 'face', 'detection', 'optical', 'character',
            'ocr', 'text', 'extraction', 'document', 'processing', 'information', 'retrieval',
            'search', 'engine', 'indexing', 'ranking', 'relevance', 'similarity',
            'recommendation', 'system', 'collaborative', 'filtering', 'content', 'based',
            'hybrid', 'recommendation', 'personalization', 'customization', 'adaptation',
            'context', 'aware', 'situational', 'awareness', 'environmental', 'context',
            'user', 'profile', 'preference', 'behavior', 'interaction', 'engagement',
            'retention', 'conversion', 'churn', 'lifetime', 'value', 'ltv', 'roi',
            'kpi', 'metric', 'analytics', 'insight', 'dashboard', 'reporting',
            'real', 'time', 'streaming', 'batch', 'processing', 'data', 'pipeline',
            'etl', 'extract', 'transform', 'load', 'data', 'warehouse', 'lake',
            'big', 'data', 'distributed', 'computing', 'mapreduce', 'hadoop', 'spark',
            'kafka', 'stream', 'processing', 'event', 'driven', 'architecture',
            'microservices', 'api', 'gateway', 'service', 'mesh', 'load', 'balancer',
            'circuit', 'breaker', 'retry', 'mechanism', 'fallback', 'graceful', 'degradation',
            'fault', 'tolerance', 'high', 'availability', 'scalability', 'performance',
            'optimization', 'caching', 'database', 'sharding', 'partitioning', 'replication',
            'backup', 'recovery', 'disaster', 'recovery', 'business', 'continuity',
            'security', 'authentication', 'authorization', 'encryption', 'privacy',
            'gdpr', 'compliance', 'audit', 'logging', 'monitoring', 'alerting',
            'devops', 'ci', 'cd', 'continuous', 'integration', 'deployment',
            'containerization', 'orchestration', 'kubernetes', 'docker', 'swarm',
            'infrastructure', 'as', 'code', 'terraform', 'ansible', 'chef', 'puppet',
            'cloud', 'native', 'serverless', 'function', 'lambda', 'edge', 'computing',
            'edge', 'computing', 'fog', 'computing', 'distributed', 'systems',
            'distributed', 'databases', 'nosql', 'mongodb', 'cassandra', 'redis',
            'elasticsearch', 'solr', 'lucene', 'inverted', 'index', 'full', 'text', 'search',
            'graph', 'database', 'neo4j', 'graphql', 'query', 'language', 'schema',
            'api', 'design', 'rest', 'graphql', 'soap', 'grpc', 'protocol', 'buffers',
            'serialization', 'deserialization', 'marshalling', 'unmarshalling',
            'message', 'queue', 'rabbitmq', 'activemq', 'kafka', 'pub', 'sub',
            'event', 'sourcing', 'cqrs', 'command', 'query', 'responsibility', 'segregation',
            'domain', 'driven', 'design', 'ddd', 'bounded', 'context', 'aggregate',
            'entity', 'value', 'object', 'repository', 'pattern', 'factory', 'pattern',
            'strategy', 'pattern', 'observer', 'pattern', 'decorator', 'pattern',
            'adapter', 'pattern', 'facade', 'pattern', 'proxy', 'pattern', 'singleton',
            'pattern', 'builder', 'pattern', 'template', 'method', 'pattern',
            'state', 'pattern', 'command', 'pattern', 'chain', 'responsibility', 'pattern',
            'interpreter', 'pattern', 'iterator', 'pattern', 'mediator', 'pattern',
            'memento', 'pattern', 'flyweight', 'pattern', 'abstract', 'factory', 'pattern',
            'bridge', 'pattern', 'composite', 'pattern', 'decorator', 'pattern',
            'facade', 'pattern', 'flyweight', 'pattern', 'proxy', 'pattern', 'chain',
            'responsibility', 'pattern', 'command', 'pattern', 'interpreter', 'pattern',
            'iterator', 'pattern', 'mediator', 'pattern', 'memento', 'pattern', 'observer',
            'pattern', 'state', 'pattern', 'strategy', 'pattern', 'template', 'method',
            'pattern', 'visitor', 'pattern', 'abstract', 'factory', 'pattern', 'builder',
            'pattern', 'factory', 'method', 'pattern', 'prototype', 'pattern', 'singleton',
            'pattern', 'adapter', 'pattern', 'bridge', 'pattern', 'composite', 'pattern',
            'decorator', 'pattern', 'facade', 'pattern', 'flyweight', 'pattern', 'proxy',
            'pattern', 'chain', 'responsibility', 'pattern', 'command', 'pattern',
            'interpreter', 'pattern', 'iterator', 'pattern', 'mediator', 'pattern',
            'memento', 'pattern', 'observer', 'pattern', 'state', 'pattern', 'strategy',
            'pattern', 'template', 'method', 'pattern', 'visitor', 'pattern'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Strip generic status/problem phrasing to focus on subject/feature
        for phrase in [
            'not functioning', 'not working', 'as expected', 'unexpected', 'issue with',
            'error occurred', 'failed', 'failure', 'failing', 'throws error', 'showing error'
        ]:
            text = text.replace(phrase, ' ')
        
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text with balanced filtering"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        # Balanced keyword extraction - less restrictive
        keywords = []
        for word in words:
            # Skip obvious stop words and very short words
            if word in self.stop_words or len(word) < 2:
                continue
                
            # Skip obvious noise words
            if word in ['http', 'https', 'www', 'com', 'org', 'net', 'io', 'co', 'uk', 'us']:
                continue
            
            # Keep meaningful words - more inclusive
            if (word in self.technical_terms or 
                len(word) >= 3 or 
                word in ['test', 'testing', 'validation', 'fail', 'failure', 'error', 'bug', 'issue', 'bot', 'conversational', 'conversation']):
                keywords.append(word)
        
        return keywords
    
    def extract_subject_terms(self, text: str) -> set:
        """Extract subject/feature terms (e.g., nodes, flags, fields, dashboards, filters)."""
        heads = {
            'node','flag','field','feature','event','function','handler','endpoint','api',
            'parameter','property','setting','toggle','connector','channel','task','job',
            'queue','session','token','key','header','intent','entity','language','locale',
            'analytics','dashboard','report','metric','filter','log','usage','userid','summary',
            'console','import','migration','genai','llm','openai','gpt','dialoggpt','searchai','websdk'
        }
        processed = self.preprocess_text(text)
        tokens = processed.split()
        subjects = set()
        # unigram and adjacent bigrams around head terms
        for i, token in enumerate(tokens):
            if token in heads:
                subjects.add(token)
                if i + 1 < len(tokens):
                    subjects.add(f"{token} {tokens[i+1]}")
                if i - 1 >= 0:
                    subjects.add(f"{tokens[i-1]} {token}")
            if i + 1 < len(tokens) and tokens[i+1] in heads:
                subjects.add(f"{tokens[i]} {tokens[i+1]}")
        # common phrases
        for phrase in ['goal completion rate','performance dashboard','user id filter','userid filter','usage logs','gen ai node','dialog gpt','openai connector','admin console','full bot import']:
            if phrase in processed:
                subjects.add(phrase)
        # fallback: keep meaningful tokens
        for t in tokens:
            if ('-' in t or t.isalnum()) and len(t) > 3 and t not in self.stop_words:
                subjects.add(t)
        return subjects
    
    def calculate_similarity(self, ticket1: JIRATicket, ticket2: JIRATicket) -> float:
        """Calculate similarity score between two tickets with enhanced content-aware algorithm"""
        # Handle description which might be a dict (rich text) or string
        desc1 = ticket1.description
        if isinstance(desc1, dict):
            desc1 = desc1.get('content', [])
            if isinstance(desc1, list):
                desc1 = ' '.join([str(item.get('text', '')) for item in desc1])
            else:
                desc1 = str(desc1)
        else:
            desc1 = str(desc1) if desc1 else ''
            
        desc2 = ticket2.description
        if isinstance(desc2, dict):
            desc2 = desc2.get('content', [])
            if isinstance(desc2, list):
                desc2 = ' '.join([str(item.get('text', '')) for item in desc2])
            else:
                desc2 = str(desc2)
        else:
            desc2 = str(desc2) if desc2 else ''
        
        # Extract keywords from summary and description
        summary1_keywords = set(self.extract_keywords(ticket1.summary))
        desc1_keywords = set(self.extract_keywords(desc1))
        summary2_keywords = set(self.extract_keywords(ticket2.summary))
        desc2_keywords = set(self.extract_keywords(desc2))
        
        # Combine keywords with different weights
        keywords1 = summary1_keywords | desc1_keywords  # Summary gets higher weight
        keywords2 = summary2_keywords | desc2_keywords
        
        if not keywords1 and not keywords2:
            return 0.0
        
        # Subject/feature similarity (core)
        subj1 = self.extract_subject_terms(ticket1.summary)
        subj2 = self.extract_subject_terms(ticket2.summary)
        subject_intersection = len(subj1.intersection(subj2))
        subject_union = len(subj1.union(subj2))
        subject_similarity = subject_intersection / subject_union if subject_union > 0 else 0.0
        
        # 1. Summary similarity (weighted higher for content relevance)
        summary_intersection = len(summary1_keywords.intersection(summary2_keywords))
        summary_union = len(summary1_keywords.union(summary2_keywords))
        summary_similarity = summary_intersection / summary_union if summary_union > 0 else 0.0
        
        # 2. Problem pattern similarity (ignored)
        pattern_similarity = 0.0
        
        # 3. Technology/component similarity
        tech1 = keywords1.intersection(self.technical_terms)
        tech2 = keywords2.intersection(self.technical_terms)
        tech_intersection = len(tech1.intersection(tech2))
        tech_union = len(tech1.union(tech2))
        tech_similarity = tech_intersection / tech_union if tech_union > 0 else 0.0
        
        # 4. Jaccard similarity for overall keyword overlap
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # 5. Metadata similarity (reduced weight)
        type_similarity = 1.0 if ticket1.issue_type == ticket2.issue_type else 0.0
        priority_similarity = 1.0 if ticket1.priority == ticket2.priority else 0.0
        comp1 = set(ticket1.components)
        comp2 = set(ticket2.components)
        component_similarity = len(comp1.intersection(comp2)) / max(len(comp1), len(comp2), 1)
        label1 = set(ticket1.labels)
        label2 = set(ticket2.labels)
        label_similarity = len(label1.intersection(label2)) / max(len(label1), len(label2), 1)
        project_similarity = 1.0 if ticket1.project == ticket2.project else 0.0
        
        # Subject + summary focused weighting
        final_similarity = (
            subject_similarity * 0.5 +
            summary_similarity * 0.35 +
            tech_similarity * 0.1 +
            jaccard_similarity * 0.05 +
            type_similarity * 0.0 +
            component_similarity * 0.0 +
            priority_similarity * 0.0 +
            label_similarity * 0.0 +
            project_similarity * 0.0
        )
        
        # Bonus for similar summary length
        len1, len2 = len(ticket1.summary), len(ticket2.summary)
        length_similarity = 1.0 - abs(len1 - len2) / max(len1, len2, 1)
        if length_similarity > 0.8:
            final_similarity += 0.01
        
        final_similarity = max(0.0, round(final_similarity, 6))
        return final_similarity
    
    def extract_problem_patterns(self, text: str) -> set:
        """Extract problem patterns from text for better content matching"""
        patterns = set()
        
        # Problem indicators
        problem_indicators = [
            'not getting', 'not generated', 'not created', 'not working', 'not functioning',
            'failed to', 'failure', 'failures', 'error', 'errors', 'broken', 'issue', 'issues',
            'problem', 'problems', 'bug', 'bugs', 'intermittent', 'intermittently', 'randomly',
            'sometimes', 'occasionally', 'sporadically', 'unexpected', 'unexpectedly',
            'timeout', 'timeouts', 'slow', 'slower', 'hanging', 'freezing', 'crashing'
        ]
        
        for indicator in problem_indicators:
            if indicator in text:
                patterns.add(indicator)
        
        # Technology patterns
        tech_patterns = [
            'dialoggpt', 'dialog gpt', 'chunks', 'chunk', 'generation', 'generated',
            'orchestration', 'retrieval', 'embedding', 'vector', 'search', 'indexing'
        ]
        
        for pattern in tech_patterns:
            if pattern in text:
                patterns.add(pattern)
        
        return patterns
    
    def find_similar_tickets(self, target_ticket: JIRATicket, all_tickets: List[JIRATicket], 
                           threshold: float = 0.3, max_results: int = 10) -> List[Dict[str, Any]]:
        """Find tickets similar to the target ticket with enhanced filtering"""
        similarities = []
        
        logger.info(f"🔍 Starting similarity search with threshold: {threshold}")
        
        for ticket in all_tickets:
            if ticket.key != target_ticket.key:  # Don't compare with itself
                similarity = self.calculate_similarity(target_ticket, ticket)
                
                # Debug logging for low similarity scores
                if similarity > 0.0 and similarity < 0.01:
                    logger.warning(f"⚠️ Very low similarity detected: {ticket.key} vs {target_ticket.key} = {similarity:.6f}")
                
                # ENHANCED THRESHOLD LOGIC: Don't include tickets with only metadata similarity
                # If content similarity is 0% but metadata gives a small score, exclude them
                content_similarity = self.calculate_content_similarity(target_ticket, ticket)
                

                
                # VERY PERMISSIVE FILTERING: Include if overall similarity meets threshold
                # Allow tickets with even minimal content similarity to be included
                if (similarity > 0.0 and 
                    similarity >= threshold):  # Remove content similarity requirement entirely
                    logger.info(f"✅ Including ticket {ticket.key} with similarity {similarity:.3f} (content: {content_similarity:.3f})")
                    similarities.append({
                        'ticket': ticket,
                        'similarity_score': similarity,
                        'content_similarity': content_similarity
                    })
                else:
                    logger.debug(f"❌ Excluding ticket {ticket.key} with similarity {similarity:.3f} (content: {content_similarity:.3f}) - below threshold")
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"📊 Found {len(similarities)} tickets above threshold {threshold} with meaningful content similarity")
        return similarities[:max_results]
    
    def calculate_content_similarity(self, ticket1: JIRATicket, ticket2: JIRATicket) -> float:
        """Calculate only content-based similarity (excluding metadata)"""
        # Handle description which might be a dict (rich text) or string
        desc1 = ticket1.description
        if isinstance(desc1, dict):
            desc1 = desc1.get('content', [])
            if isinstance(desc1, list):
                desc1 = ' '.join([str(item.get('text', '')) for item in desc1])
            else:
                desc1 = str(desc1)
        else:
            desc1 = str(desc1) if desc1 else ''
            
        desc2 = ticket2.description
        if isinstance(desc2, dict):
            desc2 = desc2.get('content', [])
            if isinstance(desc2, list):
                desc2 = ' '.join([str(item.get('text', '')) for item in desc2])
            else:
                desc2 = str(desc2)
        else:
            desc2 = str(desc2) if desc2 else ''
        
        # Extract keywords from summary and description
        summary1_keywords = set(self.extract_keywords(ticket1.summary))
        desc1_keywords = set(self.extract_keywords(desc1))
        summary2_keywords = set(self.extract_keywords(ticket2.summary))
        desc2_keywords = set(self.extract_keywords(desc2))
        
        # Combine keywords
        keywords1 = summary1_keywords | desc1_keywords
        keywords2 = summary2_keywords | desc2_keywords
        
        if not keywords1 and not keywords2:
            return 0.0
        
        # Calculate content-based similarities only
        summary_intersection = len(summary1_keywords.intersection(summary2_keywords))
        summary_union = len(summary1_keywords.union(summary2_keywords))
        summary_similarity = summary_intersection / summary_union if summary_union > 0 else 0.0
        
        # Subject similarity
        subj1 = self.extract_subject_terms(ticket1.summary)
        subj2 = self.extract_subject_terms(ticket2.summary)
        subject_intersection = len(subj1.intersection(subj2))
        subject_union = len(subj1.union(subj2))
        subject_similarity = subject_intersection / subject_union if subject_union > 0 else 0.0
        
        # Technical terms
        tech1 = keywords1.intersection(self.technical_terms)
        tech2 = keywords2.intersection(self.technical_terms)
        tech_intersection = len(tech1.intersection(tech2))
        tech_union = len(tech1.union(tech2))
        tech_similarity = tech_intersection / tech_union if tech_union > 0 else 0.0
        
        # Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Content-only weighted combination focusing on subject + summary
        content_similarity = (
            subject_similarity * 0.5 +
            summary_similarity * 0.35 +
            tech_similarity * 0.1 +
            jaccard_similarity * 0.05
        )
        
        return round(content_similarity, 6)
    
    def extract_fix_suggestions(self, candidate_ticket: JIRATicket, target_ticket: JIRATicket) -> Dict[str, Any]:
        """Extract fix suggestions from a candidate ticket that could apply to the target ticket"""
        suggestions = {
            'has_fix': False,
            'fix_type': None,
            'suggested_solution': None,
            'workaround': None,
            'root_cause': None,
            'applicable': False,
            'confidence': 0.0
        }
        
        # Check if this ticket has a resolution (closed/resolved)
        if candidate_ticket.status.lower() in ['closed', 'resolved', 'done', 'successfully deployed']:
            suggestions['has_fix'] = True
            suggestions['fix_type'] = 'resolved'
            
            # Analyze the description for fix information
            description_text = str(candidate_ticket.description).lower()
            
            # Look for common fix patterns
            fix_patterns = {
                'configuration': ['config', 'setting', 'parameter', 'environment variable', 'env var'],
                'code_change': ['code', 'fix', 'patch', 'update', 'modification', 'change'],
                'workaround': ['workaround', 'temporary', 'interim', 'bypass', 'alternative'],
                'root_cause': ['root cause', 'cause', 'reason', 'due to', 'because'],
                'solution': ['solution', 'resolution', 'fix', 'resolve', 'address']
            }
            
            # Extract fix information
            for fix_type, keywords in fix_patterns.items():
                for keyword in keywords:
                    if keyword in description_text:
                        if fix_type == 'solution':
                            suggestions['suggested_solution'] = self.extract_context(description_text, keyword)
                        elif fix_type == 'workaround':
                            suggestions['workaround'] = self.extract_context(description_text, keyword)
                        elif fix_type == 'root_cause':
                            suggestions['root_cause'] = self.extract_context(description_text, keyword)
            
            # Check if the fix is applicable to the target ticket
            suggestions['applicable'] = self.check_applicability(candidate_ticket, target_ticket)
            
            # Calculate confidence based on similarity and status
            suggestions['confidence'] = min(0.9, 0.5 + (suggestions['applicable'] * 0.4))
        
        # For open tickets, look for workarounds or temporary solutions
        elif candidate_ticket.status.lower() in ['open', 'in progress', 'ready for qa']:
            description_text = str(candidate_ticket.description).lower()
            
            if any(word in description_text for word in ['workaround', 'temporary', 'interim', 'bypass']):
                suggestions['has_fix'] = True
                suggestions['fix_type'] = 'workaround'
                suggestions['workaround'] = self.extract_context(description_text, 'workaround')
                suggestions['applicable'] = self.check_applicability(candidate_ticket, target_ticket)
                suggestions['confidence'] = 0.6
        
        return suggestions
    
    def extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword in the text"""
        try:
            # Find the keyword position
            pos = text.find(keyword)
            if pos == -1:
                return ""
            
            # Extract context (100 characters before and after)
            start = max(0, pos - 100)
            end = min(len(text), pos + len(keyword) + 100)
            
            context = text[start:end]
            
            # Clean up the context
            context = context.replace('\n', ' ').replace('\r', ' ')
            context = ' '.join(context.split())  # Remove extra whitespace
            
            return context
        except:
            return ""
    
    def check_applicability(self, candidate_ticket: JIRATicket, target_ticket: JIRATicket) -> bool:
        """Check if the fix from candidate ticket is applicable to target ticket"""
        # Compare key characteristics
        similarity_factors = []
        
        # Same technology/component
        if self.has_common_technology(candidate_ticket, target_ticket):
            similarity_factors.append(1.0)
        
        # Same issue type
        if candidate_ticket.issue_type.lower() == target_ticket.issue_type.lower():
            similarity_factors.append(0.8)
        
        # Same priority level
        if candidate_ticket.priority.lower() == target_ticket.priority.lower():
            similarity_factors.append(0.6)
        
        # Similar problem patterns
        if self.has_similar_problem_patterns(candidate_ticket, target_ticket):
            similarity_factors.append(0.9)
        
        # Calculate overall applicability score
        if similarity_factors:
            return sum(similarity_factors) / len(similarity_factors) > 0.6
        else:
            return False
    
    def has_common_technology(self, ticket1: JIRATicket, ticket2: JIRATicket) -> bool:
        """Check if two tickets share common technology/component keywords"""
        tech_keywords = ['dialoggpt', 'chunks', 'searchai', 'orchestration', 'embedding', 'vector', 'generation']
        
        text1 = (ticket1.summary + " " + str(ticket1.description)).lower()
        text2 = (ticket2.summary + " " + str(ticket2.description)).lower()
        
        for keyword in tech_keywords:
            if keyword in text1 and keyword in text2:
                return True
        
        return False
    
    def has_similar_problem_patterns(self, ticket1: JIRATicket, ticket2: JIRATicket) -> bool:
        """Check if two tickets have similar problem patterns"""
        problem_patterns = [
            'not getting', 'not generated', 'failed', 'error', 'intermittent',
            'timeout', 'slow', 'hanging', 'broken', 'not working'
        ]
        
        text1 = (ticket1.summary + " " + str(ticket1.description)).lower()
        text2 = (ticket2.summary + " " + str(ticket2.description)).lower()
        
        common_patterns = 0
        for pattern in problem_patterns:
            if pattern in text1 and pattern in text2:
                common_patterns += 1
        
        return common_patterns >= 2  # At least 2 common problem patterns
    
    def export_results(self, results: Dict[str, Any], output_file: str):
        """Export results to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results exported to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting results: {e}")

class JIRASimilarityTool:
    """Main class for JIRA similarity analysis"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.jira_client = None
        self.analyzer = SimilarityAnalyzer()
        
        if self.config:
            # Initialize JIRA client
            self.jira_client = JIRAClient(
                base_url=self.config['jira_url'],
                username=self.config['username'],
                api_token=self.config['api_token'],
                project_key=self.config.get('project_key', 'PLAT')
            )
    
    def load_config(self, config_file: str = None) -> Optional[Dict[str, str]]:
        """Load configuration from file or environment variables"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Try environment variables
        config = {
            'jira_url': os.getenv('JIRA_URL'),
            'username': os.getenv('JIRA_USERNAME'),
            'api_token': None
        }
        
        if config.get('jira_url') and config.get('username') and config.get('api_token'):
            return config
        
        return None
    
    def analyze_similarity(self, ticket_key: str, threshold: float = 0.2, max_results: int = 10) -> List[Dict]:
        """Analyze similarity for a given ticket with content-based search and fix suggestions"""
        logger.info(f"🔍 Starting similarity analysis for ticket: {ticket_key}")
        
        # Get the target ticket
        target_ticket = self.jira_client.get_ticket(ticket_key)
        if not target_ticket:
            logger.error(f"❌ Could not fetch target ticket {ticket_key}")
            return []
        
        logger.info(f"✅ Successfully fetched target ticket: {target_ticket.key}")
        logger.info(f"📋 Target ticket summary: {target_ticket.summary}")
        
        # Extract key terms from the target ticket for content-based search
        analyzer = SimilarityAnalyzer()
        target_keywords = analyzer.extract_keywords(target_ticket.summary + " " + str(target_ticket.description))
        target_subject_terms = analyzer.extract_subject_terms(target_ticket.summary)
        
        # Create content-based search queries - ENHANCED AND MORE COMPREHENSIVE
        search_queries = []
        
        # Primary search: Use the EXACT summary terms
        summary_lower = target_ticket.summary.lower()
        
        # 1. Add the original summary as primary search
        search_queries.append(target_ticket.summary)
        
        # 2. Extract ALL meaningful keywords
        for keyword in target_keywords:
            if len(keyword) > 2:
                search_queries.append(keyword)
        
        # 3. Add GenAI/subject terms explicitly if present
        for term in target_subject_terms:
            if len(term) > 2:
                search_queries.append(term)
        
        # 4. Add 2-gram and 3-gram phrases from summary
        words = summary_lower.split()
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:
                search_queries.append(phrase)
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 8:
                search_queries.append(phrase)
        
        # Deduplicate and cap
        search_queries = list(set(search_queries))[:25]
        logger.info(f"🔍 Generated {len(search_queries)} search queries:")
        for q in search_queries:
            logger.info(f"   - {q}")
        
        # Prefer PLAT/XOP and issue types Bug/Customer-Incident/Customer-Defect
        all_candidates: List[JIRATicket] = []
        allowed_projects = ['PLAT', 'XOP']
        allowed_issue_types = ['Bug', 'Customer-Incident', 'Customer-Defect']
        
        for q in search_queries:
            logger.info(f"🔍 Searching PLAT/XOP (Bug/Customer-Incident/Customer-Defect) for: '{q}'")
            cands = self.jira_client.search_tickets_projects_issue_type(
                q, allowed_projects, allowed_issue_types, max_results=50
            )
            if not cands:
                # Fallback to current project scope
                cands = self.jira_client.search_tickets(q, max_results=50)
            if cands:
                all_candidates.extend(cands)
        
        # Remove duplicates by key
        unique_map: Dict[str, JIRATicket] = {}
        for t in all_candidates:
            if t.key not in unique_map:
                unique_map[t.key] = t
        unique_candidates = list(unique_map.values())
        logger.info(f"📊 Total unique candidate tickets found: {len(unique_candidates)}")
        
        # Enforce subject-overlap filtering
        filtered_candidates: List[JIRATicket] = []
        for t in unique_candidates:
            cand_subjects = analyzer.extract_subject_terms(t.summary)
            if cand_subjects.intersection(target_subject_terms):
                filtered_candidates.append(t)
        logger.info(f"📊 Candidates after subject-overlap filtering: {len(filtered_candidates)}")
        
        # Score
        similar: List[Dict[str, Any]] = []
        for cand in filtered_candidates:
            if cand.key == target_ticket.key:
                continue
            score = analyzer.calculate_similarity(target_ticket, cand)
            if score >= threshold:
                similar.append({
                    'key': cand.key,
                    'summary': cand.summary,
                    'issue_type': cand.issue_type,
                    'priority': cand.priority,
                    'status': cand.status,
                    'similarity_score': score,
                    'url': f"{self.config['jira_url']}/browse/{cand.key}",
                    'fix_suggestions': self.extract_fix_suggestions(cand, target_ticket),
                    'description': cand.description,
                    'assignee': cand.assignee,
                    'reporter': cand.reporter,
                    'created': cand.created,
                    'updated': cand.updated
                })
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        similar = similar[:max_results]
        
        # Fallback: lower threshold once if empty and we have candidates
        if not similar and filtered_candidates:
            fallback_threshold = max(0.1, threshold - 0.1)
            logger.info(f"🔁 No results at threshold {threshold}. Retrying with {fallback_threshold}")
            for cand in filtered_candidates:
                if cand.key == target_ticket.key:
                    continue
                score = analyzer.calculate_similarity(target_ticket, cand)
                if score >= fallback_threshold:
                    similar.append({
                        'key': cand.key,
                        'summary': cand.summary,
                        'issue_type': cand.issue_type,
                        'priority': cand.priority,
                        'status': cand.status,
                        'similarity_score': score,
                        'url': f"{self.config['jira_url']}/browse/{cand.key}",
                        'fix_suggestions': self.extract_fix_suggestions(cand, target_ticket),
                        'description': cand.description,
                        'assignee': cand.assignee,
                        'reporter': cand.reporter,
                        'created': cand.created,
                        'updated': cand.updated
                    })
            similar.sort(key=lambda x: x['similarity_score'], reverse=True)
            similar = similar[:max_results]
        
        logger.info(f"✅ Found {len(similar)} similar tickets above threshold {threshold}")
        return similar
    
    def extract_fix_suggestions(self, candidate_ticket: JIRATicket, target_ticket: JIRATicket) -> Dict[str, Any]:
        """Extract fix suggestions from a candidate ticket that could apply to the target ticket"""
        suggestions = {
            'has_fix': False,
            'fix_type': None,
            'suggested_solution': None,
            'workaround': None,
            'root_cause': None,
            'applicable': False,
            'confidence': 0.0
        }
        
        # Check if this ticket has a resolution (closed/resolved)
        if candidate_ticket.status.lower() in ['closed', 'resolved', 'done', 'successfully deployed']:
            suggestions['has_fix'] = True
            suggestions['fix_type'] = 'resolved'
            
            # Analyze the description for fix information
            description_text = str(candidate_ticket.description).lower()
            
            # Look for common fix patterns
            fix_patterns = {
                'configuration': ['config', 'setting', 'parameter', 'environment variable', 'env var'],
                'code_change': ['code', 'fix', 'patch', 'update', 'modification', 'change'],
                'workaround': ['workaround', 'temporary', 'interim', 'bypass', 'alternative'],
                'root_cause': ['root cause', 'cause', 'reason', 'due to', 'because'],
                'solution': ['solution', 'resolution', 'fix', 'resolve', 'address']
            }
            
            # Extract fix information
            for fix_type, keywords in fix_patterns.items():
                for keyword in keywords:
                    if keyword in description_text:
                        if fix_type == 'solution':
                            suggestions['suggested_solution'] = self.extract_context(description_text, keyword)
                        elif fix_type == 'workaround':
                            suggestions['workaround'] = self.extract_context(description_text, keyword)
                        elif fix_type == 'root_cause':
                            suggestions['root_cause'] = self.extract_context(description_text, keyword)
            
            # Check if the fix is applicable to the target ticket
            suggestions['applicable'] = self.check_applicability(candidate_ticket, target_ticket)
            
            # Calculate confidence based on similarity and status
            suggestions['confidence'] = min(0.9, 0.5 + (suggestions['applicable'] * 0.4))
        
        # For open tickets, look for workarounds or temporary solutions
        elif candidate_ticket.status.lower() in ['open', 'in progress', 'ready for qa']:
            description_text = str(candidate_ticket.description).lower()
            
            if any(word in description_text for word in ['workaround', 'temporary', 'interim', 'bypass']):
                suggestions['has_fix'] = True
                suggestions['fix_type'] = 'workaround'
                suggestions['workaround'] = self.extract_context(description_text, 'workaround')
                suggestions['applicable'] = self.check_applicability(candidate_ticket, target_ticket)
                suggestions['confidence'] = 0.6
        
        return suggestions
    
    def extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword in the text"""
        try:
            # Find the keyword position
            pos = text.find(keyword)
            if pos == -1:
                return ""
            
            # Extract context (100 characters before and after)
            start = max(0, pos - 100)
            end = min(len(text), pos + len(keyword) + 100)
            
            context = text[start:end]
            
            # Clean up the context
            context = context.replace('\n', ' ').replace('\r', ' ')
            context = ' '.join(context.split())  # Remove extra whitespace
            
            return context
        except:
            return ""
    
    def check_applicability(self, candidate_ticket: JIRATicket, target_ticket: JIRATicket) -> bool:
        """Check if a fix from candidate ticket is applicable to target ticket"""
        # Simple applicability check based on common technology and problem patterns
        analyzer = SimilarityAnalyzer()
        
        # Check if they share common technology keywords
        if analyzer.has_common_technology(candidate_ticket, target_ticket):
            return True
        
        # Check if they have similar problem patterns
        if analyzer.has_similar_problem_patterns(candidate_ticket, target_ticket):
                return True
        
        return False

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='JIRA Similarity Analysis Tool')
    parser.add_argument('ticket_key', help='JIRA ticket key to analyze')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--jql', help='JQL query for searching tickets')
    parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold (0.0-1.0)')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of similar tickets')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    # Create the tool
    tool = JIRASimilarityTool(args.config)
    
    if not tool.config:
        print("Error: JIRA configuration not found. Please set environment variables or provide a config file.")
        print("Required environment variables: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN")
        return
    
    # Analyze the ticket
    print(f"Analyzing ticket {args.ticket_key}...")
    results = tool.analyze_similarity(
        args.ticket_key,
        args.threshold,
        args.max_results
    )
    
    if not results:
        print(f"No similar tickets found for {args.ticket_key}.")
        return
    
    # Display results
    print(f"\nTarget Ticket: {args.ticket_key}")
    
    # Get target ticket info for display
    target_ticket = tool.jira_client.get_ticket(args.ticket_key)
    if target_ticket:
        print(f"Summary: {target_ticket.summary}")
        print(f"Type: {target_ticket.issue_type}")
        print(f"Priority: {target_ticket.priority}")
        print(f"Status: {target_ticket.status}")
    
    print(f"\nFound {len(results)} similar tickets:")
    print("-" * 80)
    
    for i, ticket in enumerate(results, 1):
        print(f"{i}. {ticket['key']} (Similarity: {ticket['similarity_score']:.3f})")
        print(f"   Summary: {ticket['summary']}")
        print(f"   Type: {ticket['issue_type']}, Priority: {ticket['priority']}, Status: {ticket['status']}")
        print(f"   URL: {ticket['url']}")
        print()
    
    # Export if requested
    if args.output:
        tool.export_results(results, args.output)

if __name__ == "__main__":
    main() 