const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const path = require('path');
const winston = require('winston');

const config = require('./config/config');

class DemoServer {
  constructor() {
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    this.sampleData = this.createSampleData();
  }

  /**
   * Setup middleware
   */
  setupMiddleware() {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
          scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'"]
        }
      }
    }));

    // CORS
    this.app.use(cors());

    // Compression
    this.app.use(compression());

    // Logging
    this.app.use(morgan('combined', {
      stream: {
        write: (message) => winston.info(message.trim())
      }
    }));

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Static files
    this.app.use(express.static(path.join(__dirname, '../public')));
  }

  /**
   * Create sample data for demo
   */
  createSampleData() {
    return {
      tickets: [
        {
          key: 'PLAT-39562',
          summary: 'Database connection timeout in production environment',
          description: 'Users experiencing database connection timeouts during peak hours. The application server is unable to maintain stable connections to the PostgreSQL database, causing intermittent failures.',
          issueType: 'Bug',
          priority: 'High',
          status: 'Open',
          components: ['Backend', 'Database'],
          labels: ['bug', 'performance', 'database'],
          created: '2024-01-15T10:30:00.000Z',
          updated: '2024-01-15T14:45:00.000Z',
          assignee: 'John Developer',
          reporter: 'Jane Tester',
          resolution: null,
          resolutionDate: null
        },
        {
          key: 'PLAT-39560',
          summary: 'Database connection pool exhaustion',
          description: 'Connection pool is being exhausted during high traffic periods, leading to connection timeouts and application errors.',
          issueType: 'Bug',
          priority: 'High',
          status: 'Resolved',
          components: ['Backend', 'Database'],
          labels: ['bug', 'performance', 'database'],
          created: '2024-01-10T09:15:00.000Z',
          updated: '2024-01-12T16:20:00.000Z',
          assignee: 'Mike DevOps',
          reporter: 'Sarah QA',
          resolution: 'Fixed',
          resolutionDate: '2024-01-12T16:20:00.000Z'
        },
        {
          key: 'PLAT-39561',
          summary: 'API response time degradation',
          description: 'API endpoints taking longer than expected to respond, affecting user experience and system performance.',
          issueType: 'Bug',
          priority: 'High',
          status: 'In Progress',
          components: ['API', 'Backend'],
          labels: ['performance', 'bug', 'api'],
          created: '2024-01-14T11:00:00.000Z',
          updated: '2024-01-15T13:30:00.000Z',
          assignee: 'Alex Backend',
          reporter: 'Tom Frontend',
          resolution: null,
          resolutionDate: null
        },
        {
          key: 'PLAT-39563',
          summary: 'Memory leak in application server',
          description: 'Application server memory usage increasing over time, eventually causing out-of-memory errors and server crashes.',
          issueType: 'Bug',
          priority: 'High',
          status: 'Open',
          components: ['Backend'],
          labels: ['bug', 'performance', 'memory'],
          created: '2024-01-16T08:45:00.000Z',
          updated: '2024-01-16T12:15:00.000Z',
          assignee: 'David Backend',
          reporter: 'Lisa Monitoring',
          resolution: null,
          resolutionDate: null
        },
        {
          key: 'PLAT-39564',
          summary: 'Slow database queries affecting performance',
          description: 'Certain database queries are taking too long to execute, causing page load times to increase significantly.',
          issueType: 'Bug',
          priority: 'Medium',
          status: 'Resolved',
          components: ['Database', 'Backend'],
          labels: ['performance', 'database', 'optimization'],
          created: '2024-01-08T14:20:00.000Z',
          updated: '2024-01-11T10:30:00.000Z',
          assignee: 'Bob DBA',
          reporter: 'Carol PM',
          resolution: 'Fixed',
          resolutionDate: '2024-01-11T10:30:00.000Z'
        },
        {
          key: 'PLAT-39565',
          summary: 'Connection timeout in load balancer',
          description: 'Load balancer is timing out connections to backend services, causing 504 Gateway Timeout errors.',
          issueType: 'Bug',
          priority: 'High',
          status: 'Open',
          components: ['Infrastructure', 'Load Balancer'],
          labels: ['infrastructure', 'timeout', 'load-balancer'],
          created: '2024-01-17T07:30:00.000Z',
          updated: '2024-01-17T11:45:00.000Z',
          assignee: 'Frank DevOps',
          reporter: 'Grace SRE',
          resolution: null,
          resolutionDate: null
        },
        {
          key: 'PLAT-45148',
          summary: 'Database connection timeout in production environment',
          description: 'Users experiencing database connection timeouts during peak hours. The application server is unable to maintain stable connections to the PostgreSQL database, causing intermittent failures and 500 errors.',
          issueType: 'Bug',
          priority: 'High',
          status: 'Open',
          components: ['Backend', 'Database', 'Production'],
          labels: ['bug', 'performance', 'database', 'production', 'timeout'],
          created: '2024-01-20T09:30:00.000Z',
          updated: '2024-01-20T15:45:00.000Z',
          assignee: 'John Developer',
          reporter: 'Jane Tester',
          resolution: null,
          resolutionDate: null
        }
      ]
    };
  }

  /**
   * Setup routes
   */
  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        mode: 'demo',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: '2.0.0'
      });
    });

    // Demo API routes
    this.app.use('/api/v1', this.createDemoAPIRoutes());

    // Web interface
    this.app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, '../public/demo.html'));
    });

    // Catch-all for SPA
    this.app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, '../public/demo.html'));
    });

    // Error handling
    this.app.use((error, req, res, next) => {
      winston.error('Demo API Error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message,
        timestamp: new Date().toISOString()
      });
    });
  }

  /**
   * Create demo API routes
   */
  createDemoAPIRoutes() {
    const router = express.Router();

    // Test connection (always successful in demo)
    router.get('/test', (req, res) => {
      res.json({
        success: true,
        message: 'Demo mode - JIRA connection simulated successfully',
        mode: 'demo',
        timestamp: new Date().toISOString()
      });
    });

    // Analyze ticket (demo simulation)
    router.post('/analyze', (req, res) => {
      try {
        const { ticketKey, similarityThreshold = 0.3, maxResults = 100 } = req.body;

        if (!ticketKey) {
          return res.status(400).json({
            success: false,
            error: 'Ticket key is required'
          });
        }

        // Find reference ticket
        const referenceTicket = this.sampleData.tickets.find(t => t.key === ticketKey);
        if (!referenceTicket) {
          return res.status(404).json({
            success: false,
            error: `Ticket ${ticketKey} not found in demo data`
          });
        }

        // Simulate analysis delay
        setTimeout(() => {
          const result = this.simulateAnalysis(referenceTicket, similarityThreshold, maxResults);
          res.json(result);
        }, 1000);

      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get ticket details
    router.get('/ticket/:ticketKey', (req, res) => {
      try {
        const { ticketKey } = req.params;
        const ticket = this.sampleData.tickets.find(t => t.key === ticketKey);
        
        if (!ticket) {
          return res.status(404).json({
            success: false,
            error: `Ticket ${ticketKey} not found`
          });
        }

        res.json({
          success: true,
          data: {
            ticket: ticket,
            comments: this.generateDemoComments(ticketKey),
            worklog: this.generateDemoWorklog(ticketKey),
            metadata: {
              totalComments: 3,
              totalWorklogEntries: 2,
              totalTimeSpent: 14400 // 4 hours in seconds
            }
          }
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get all tickets
    router.get('/tickets', (req, res) => {
      res.json({
        success: true,
        data: this.sampleData.tickets
      });
    });

    // Get demo statistics
    router.get('/stats', (req, res) => {
      res.json({
        success: true,
        data: {
          tool: {
            version: '2.0.0',
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            mode: 'demo',
            config: {
              similarityThreshold: config.analysis.similarityThreshold,
              maxResults: config.analysis.maxResults,
              enableNLP: config.analysis.enableNLP
            }
          },
          cache: {
            size: 0,
            maxSize: config.cache.maxSize,
            ttl: config.cache.ttl,
            enabled: false
          },
          exports: {
            totalFiles: 0,
            fileTypes: {},
            totalSize: 0
          }
        }
      });
    });

    return router;
  }

  /**
   * Simulate analysis
   */
  simulateAnalysis(referenceTicket, threshold, maxResults) {
    const similarTickets = [];
    const allTickets = this.sampleData.tickets.filter(t => t.key !== referenceTicket.key);

    // Simulate similarity calculation
    allTickets.forEach(ticket => {
      // Calculate simple similarity based on components and labels
      let similarity = 0;

      // Component similarity
      const commonComponents = referenceTicket.components.filter(c => ticket.components.includes(c));
      if (commonComponents.length > 0) {
        similarity += (commonComponents.length / Math.max(referenceTicket.components.length, ticket.components.length)) * 0.4;
      }

      // Label similarity
      const commonLabels = referenceTicket.labels.filter(l => ticket.labels.includes(l));
      if (commonLabels.length > 0) {
        similarity += (commonLabels.length / Math.max(referenceTicket.labels.length, ticket.labels.length)) * 0.3;
      }

      // Issue type similarity
      if (referenceTicket.issueType === ticket.issueType) {
        similarity += 0.2;
      }

      // Priority similarity
      if (referenceTicket.priority === ticket.priority) {
        similarity += 0.1;
      }

      if (similarity >= threshold) {
        similarTickets.push({
          ticket: ticket,
          similarityScore: similarity,
          summarySimilarity: similarity * 0.8,
          descriptionSimilarity: similarity * 0.6,
          metadataSimilarity: similarity * 0.9,
          commonPatterns: this.extractCommonPatterns(referenceTicket, ticket),
          recommendedFixes: this.generateFixes(ticket)
        });
      }
    });

    // Sort by similarity
    similarTickets.sort((a, b) => b.similarityScore - a.similarityScore);

    // Generate analysis summary
    const analysisSummary = this.generateAnalysisSummary(referenceTicket, similarTickets);

    return {
      success: true,
      referenceTicket: referenceTicket,
      similarTickets: similarTickets.slice(0, maxResults),
      analysisSummary: analysisSummary,
      searchQuery: `project = PLAT AND component IN ("${referenceTicket.components.join('", "')}")`,
      totalFound: allTickets.length,
      similarCount: similarTickets.length,
      analysisTime: Math.floor(Math.random() * 2000) + 500, // 500-2500ms
      metadata: {
        toolVersion: '2.0.0',
        analysisDate: new Date().toISOString(),
        threshold: threshold,
        maxResults: maxResults,
        mode: 'demo'
      }
    };
  }

  /**
   * Extract common patterns
   */
  extractCommonPatterns(ticket1, ticket2) {
    const patterns = [];

    // Common words in summaries
    const words1 = new Set(ticket1.summary.toLowerCase().split(/\s+/));
    const words2 = new Set(ticket2.summary.toLowerCase().split(/\s+/));
    const commonWords = [...words1].filter(word => words2.has(word) && word.length > 3);
    patterns.push(...commonWords.slice(0, 3));

    // Common components and labels
    const commonComponents = ticket1.components.filter(comp => ticket2.components.includes(comp));
    const commonLabels = ticket1.labels.filter(label => ticket2.labels.includes(label));

    patterns.push(...commonComponents);
    patterns.push(...commonLabels);

    return [...new Set(patterns)].slice(0, 5);
  }

  /**
   * Generate fixes
   */
  generateFixes(ticket) {
    const fixes = [];
    const summary = ticket.summary.toLowerCase();
    const description = ticket.description.toLowerCase();

    if (summary.includes('database') || description.includes('database')) {
      fixes.push(
        'Check database connection pool settings',
        'Verify database server resources',
        'Add connection timeout handling',
        'Implement connection retry logic'
      );
    } else if (summary.includes('performance') || description.includes('performance')) {
      fixes.push(
        'Profile application performance',
        'Optimize database queries',
        'Add caching mechanisms',
        'Review resource allocation'
      );
    } else if (summary.includes('memory') || description.includes('memory')) {
      fixes.push(
        'Check for memory leaks in code',
        'Review object lifecycle management',
        'Implement proper resource cleanup',
        'Add memory monitoring'
      );
    } else {
      fixes.push(
        'Add proper error handling',
        'Implement logging for debugging',
        'Add input validation',
        'Review error messages'
      );
    }

    return fixes.slice(0, 4);
  }

  /**
   * Generate analysis summary
   */
  generateAnalysisSummary(referenceTicket, similarTickets) {
    if (similarTickets.length === 0) {
      return {
        totalSimilar: 0,
        highSimilarity: 0,
        mediumSimilarity: 0,
        lowSimilarity: 0,
        resolvedCount: 0,
        commonPatterns: [],
        topFixes: [],
        timeSaved: '0 hours',
        averageSimilarity: 0
      };
    }

    const highSimilarity = similarTickets.filter(s => s.similarityScore >= 0.7).length;
    const mediumSimilarity = similarTickets.filter(s => s.similarityScore >= 0.4 && s.similarityScore < 0.7).length;
    const lowSimilarity = similarTickets.filter(s => s.similarityScore < 0.4).length;
    const resolvedCount = similarTickets.filter(s => s.ticket.status === 'Resolved').length;

    const allPatterns = new Set();
    similarTickets.forEach(similar => {
      similar.commonPatterns.forEach(pattern => allPatterns.add(pattern));
    });

    const allFixes = new Set();
    similarTickets.forEach(similar => {
      similar.recommendedFixes.forEach(fix => allFixes.add(fix));
    });

    const averageSimilarity = similarTickets.reduce((sum, s) => sum + s.similarityScore, 0) / similarTickets.length;
    const timeSaved = `${similarTickets.length * 2}-${similarTickets.length * 4} hours`;

    return {
      totalSimilar: similarTickets.length,
      highSimilarity: highSimilarity,
      mediumSimilarity: mediumSimilarity,
      lowSimilarity: lowSimilarity,
      resolvedCount: resolvedCount,
      commonPatterns: Array.from(allPatterns).slice(0, 10),
      topFixes: Array.from(allFixes).slice(0, 8),
      timeSaved: timeSaved,
      averageSimilarity: parseFloat(averageSimilarity.toFixed(3))
    };
  }

  /**
   * Generate demo comments
   */
  generateDemoComments(ticketKey) {
    return [
      {
        id: '10001',
        author: 'John Developer',
        body: 'Investigating the issue. Will check database connection settings.',
        created: '2024-01-15T11:00:00.000Z'
      },
      {
        id: '10002',
        author: 'Jane Tester',
        body: 'Issue confirmed in staging environment as well.',
        created: '2024-01-15T12:30:00.000Z'
      },
      {
        id: '10003',
        author: 'Mike DevOps',
        body: 'Found the root cause. Connection pool configuration needs adjustment.',
        created: '2024-01-15T14:00:00.000Z'
      }
    ];
  }

  /**
   * Generate demo worklog
   */
  generateDemoWorklog(ticketKey) {
    return [
      {
        id: '20001',
        author: 'John Developer',
        timeSpentSeconds: 7200, // 2 hours
        comment: 'Initial investigation and debugging',
        started: '2024-01-15T10:30:00.000Z'
      },
      {
        id: '20002',
        author: 'Mike DevOps',
        timeSpentSeconds: 3600, // 1 hour
        comment: 'Configuration review and testing',
        started: '2024-01-15T14:00:00.000Z'
      }
    ];
  }

  /**
   * Start the demo server
   */
  start() {
    const port = config.server.port;
    const host = config.server.host;

    this.app.listen(port, host, () => {
      winston.info(`🎮 JIRA Similarity Tool Demo Server started`);
      winston.info(`📍 Demo running at http://${host}:${port}`);
      winston.info(`🔍 Health check at http://${host}:${port}/health`);
      winston.info(`📚 Demo API at http://${host}:${port}/api/v1`);
      winston.info(`💡 Available demo tickets: ${this.sampleData.tickets.map(t => t.key).join(', ')}`);
    });
  }
}

// Start demo server if this file is run directly
if (require.main === module) {
  const demoServer = new DemoServer();
  demoServer.start();
}

module.exports = DemoServer; 