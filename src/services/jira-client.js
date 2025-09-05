const axios = require('axios');
const winston = require('winston');
const config = require('../config/config');

class JIRAClient {
  constructor() {
    this.baseURL = config.jira.baseUrl;
    this.email = config.jira.email;
    this.apiToken = config.jira.apiToken;
    this.timeout = config.jira.timeout;
    this.maxRetries = config.jira.maxRetries;
    
    // Create axios instance with default configuration
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      auth: {
        username: this.email,
        password: this.apiToken
      },
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        winston.debug(`JIRA API Request: ${config.method ? config.method.toUpperCase() : 'UNKNOWN'} ${config.url}`);
        return config;
      },
      (error) => {
        winston.error('JIRA API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        winston.debug(`JIRA API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        winston.error('JIRA API Response Error:', {
          status: error.response ? error.response.status : null,
          statusText: error.response ? error.response.statusText : null,
          url: error.config ? error.config.url : null,
          message: error.message
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Test JIRA API connection
   * @returns {Promise<boolean>}
   */
      async testConnection() {
      try {
        const response = await this.client.get('/rest/api/3/myself');
        winston.info('✅ JIRA API connection successful');
        return true;
    } catch (error) {
      winston.error('❌ JIRA API connection failed:', error.message);
      return false;
    }
  }

  /**
   * Get a single JIRA ticket
   * @param {string} ticketKey - The ticket key (e.g., 'PLAT-39562')
   * @returns {Promise<Object|null>}
   */
      async getTicket(ticketKey) {
      try {
        const response = await this.client.get(`/rest/api/3/issue/${ticketKey}`, {
        params: {
          fields: 'summary,description,issuetype,priority,status,components,labels,created,updated,assignee,reporter,resolution,resolutiondate'
        }
      });

      return this.parseTicket(response.data);
    } catch (error) {
      winston.error(`❌ Failed to fetch ticket ${ticketKey}:`, error.message);
      return null;
    }
  }

  /**
   * Search JIRA tickets using JQL
   * @param {string} jql - JQL query string
   * @param {number} maxResults - Maximum number of results
   * @returns {Promise<Array>}
   */
      async searchTickets(jql, maxResults = config.analysis.maxResults) {
      try {
        const response = await this.client.post('/rest/api/3/search/jql', {
        jql: jql,
        maxResults: maxResults,
        fields: ['summary', 'description', 'issuetype', 'priority', 'status', 
                'components', 'labels', 'created', 'updated', 'assignee', 
                'reporter', 'resolution', 'resolutiondate']
      });

      const tickets = response.data.issues.map(issue => this.parseTicket(issue));
      winston.info(`✅ Found ${tickets.length} tickets`);
      return tickets;
    } catch (error) {
      winston.error('❌ Search failed:', error.message);
      return [];
    }
  }

  /**
   * Get project information
   * @param {string} projectKey - Project key
   * @returns {Promise<Object|null>}
   */
      async getProject(projectKey) {
      try {
        const response = await this.client.get(`/rest/api/3/project/${projectKey}`);
      return response.data;
    } catch (error) {
      winston.error(`❌ Failed to fetch project ${projectKey}:`, error.message);
      return null;
    }
  }

  /**
   * Get all projects
   * @returns {Promise<Array>}
   */
      async getProjects() {
      try {
        const response = await this.client.get('/rest/api/3/project');
      return response.data;
    } catch (error) {
      winston.error('❌ Failed to fetch projects:', error.message);
      return [];
    }
  }

  /**
   * Parse JIRA issue data into standardized format
   * @param {Object} issueData - Raw JIRA issue data
   * @returns {Object} Parsed ticket object
   */
  parseTicket(issueData) {
    try {
      const fields = issueData.fields || {};
      
      // Extract description (handle different formats)
      let description = '';
      const descField = fields.description;
      if (descField) {
        if (typeof descField === 'string') {
          description = descField;
        } else if (descField.content) {
          // Rich text format
          description = this.extractRichText(descField.content);
        }
      }

      // Extract components
      const components = (fields.components || []).map(comp => comp.name);

      // Extract labels
      const labels = fields.labels || [];

      // Extract assignee
      const assignee = fields.assignee && fields.assignee.displayName ? fields.assignee.displayName : null;

      // Extract reporter
      const reporter = fields.reporter && fields.reporter.displayName ? fields.reporter.displayName : '';

      // Extract resolution
      const resolution = fields.resolution && fields.resolution.name ? fields.resolution.name : null;

      return {
        key: issueData.key,
        summary: fields.summary || '',
        description: description,
        issueType: fields.issuetype && fields.issuetype.name ? fields.issuetype.name : '',
        priority: fields.priority && fields.priority.name ? fields.priority.name : '',
        status: fields.status && fields.status.name ? fields.status.name : '',
        components: components,
        labels: labels,
        created: fields.created || '',
        updated: fields.updated || '',
        assignee: assignee,
        reporter: reporter,
        resolution: resolution,
        resolutionDate: fields.resolutiondate || ''
      };
    } catch (error) {
      winston.error('❌ Error parsing ticket:', error.message);
      return null;
    }
  }

  /**
   * Extract text from rich text content
   * @param {Array} content - Rich text content array
   * @returns {string} Extracted text
   */
  extractRichText(content) {
    if (!Array.isArray(content)) return '';
    
    let text = '';
    content.forEach(item => {
      if (item.content) {
        item.content.forEach(textItem => {
          if (textItem.text) {
            text += textItem.text;
          }
        });
      }
    });
    
    return text;
  }

  /**
   * Build JQL query for finding similar tickets
   * @param {Object} ticket - Reference ticket
   * @returns {string} JQL query string
   */
  buildSimilarityJQL(ticket) {
    const project = ticket.key.split('-')[0];
    const filters = [`project = ${project}`];

    // Add component filter if available
    if (ticket.components && ticket.components.length > 0) {
      const componentFilter = ticket.components.map(comp => `component = "${comp}"`).join(' OR ');
      filters.push(`(${componentFilter})`);
    }

    // Add label filter if available
    if (ticket.labels && ticket.labels.length > 0) {
      const labelFilter = ticket.labels.slice(0, 3).map(label => `labels = "${label}"`).join(' OR ');
      filters.push(`(${labelFilter})`);
    }

    // Add issue type filter
    if (ticket.issueType) {
      filters.push(`issuetype = "${ticket.issueType}"`);
    }

    // Exclude the reference ticket
    filters.push(`key != ${ticket.key}`);

    // Order by updated date (most recent first)
    return filters.join(' AND ') + ' ORDER BY updated DESC';
  }

  /**
   * Get ticket comments
   * @param {string} ticketKey - Ticket key
   * @returns {Promise<Array>}
   */
      async getComments(ticketKey) {
      try {
        const response = await this.client.get(`/rest/api/3/issue/${ticketKey}/comment`);
      return response.data.comments || [];
    } catch (error) {
      winston.error(`❌ Failed to fetch comments for ${ticketKey}:`, error.message);
      return [];
    }
  }

  /**
   * Get ticket worklog
   * @param {string} ticketKey - Ticket key
   * @returns {Promise<Array>}
   */
      async getWorklog(ticketKey) {
      try {
        const response = await this.client.get(`/rest/api/3/issue/${ticketKey}/worklog`);
        return response.data.worklogs || [];
      } catch (error) {
        winston.error(`Failed to get worklog for ${ticketKey}:`, error.message);
        return [];
      }
    }
}

module.exports = JIRAClient; 