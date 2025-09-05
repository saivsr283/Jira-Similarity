const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');
const winston = require('winston');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const config = require('./config/config');
const JIRASimilarityTool = require('./core/jira-similarity-tool');

class WebServer {
  constructor() {
    this.app = express();
    this.tool = new JIRASimilarityTool();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupSwagger();
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
    if (config.server.cors) {
      this.app.use(cors({
        origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : '*',
        credentials: true
      }));
    }

    // Rate limiting
    this.app.use(rateLimit({
      windowMs: config.server.rateLimit.windowMs,
      max: config.server.rateLimit.max,
      message: {
        error: 'Too many requests from this IP, please try again later.'
      }
    }));

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
   * Setup API routes
   */
  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: '2.0.0'
      });
    });

    // API routes
    this.app.use('/api/v1', this.createAPIRoutes());

    // Web interface
    this.app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, '../public/index.html'));
    });

    // Catch-all for SPA
    this.app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, '../public/index.html'));
    });

    // Error handling
    this.app.use((error, req, res, next) => {
      winston.error('API Error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message,
        timestamp: new Date().toISOString()
      });
    });
  }

  /**
   * Create API routes
   */
  createAPIRoutes() {
    const router = express.Router();

    // Test connection
    router.get('/test', async (req, res) => {
      try {
        const isConnected = await this.tool.testConnection();
        res.json({
          success: isConnected,
          message: isConnected ? 'JIRA connection successful' : 'JIRA connection failed',
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Analyze ticket
    router.post('/analyze', async (req, res) => {
      try {
        const { ticketKey, similarityThreshold, maxResults } = req.body;

        if (!ticketKey) {
          return res.status(400).json({
            success: false,
            error: 'Ticket key is required'
          });
        }

        const options = {
          similarityThreshold: similarityThreshold || config.analysis.similarityThreshold,
          maxResults: maxResults || config.analysis.maxResults
        };

        const result = await this.tool.analyzeTicket(ticketKey, options);
        
        if (result.success) {
          res.json(result);
        } else {
          res.status(400).json(result);
        }
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get ticket details
    router.get('/ticket/:ticketKey', async (req, res) => {
      try {
        const { ticketKey } = req.params;
        const details = await this.tool.getTicketDetails(ticketKey);
        res.json({
          success: true,
          data: details
        });
      } catch (error) {
        res.status(404).json({
          success: false,
          error: error.message
        });
      }
    });

    // Export results
    router.post('/export', async (req, res) => {
      try {
        const { analysisResult, format } = req.body;

        if (!analysisResult) {
          return res.status(400).json({
            success: false,
            error: 'Analysis result is required'
          });
        }

        const exportResult = await this.tool.exportResults(analysisResult, format);
        res.json({
          success: true,
          data: exportResult
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Batch analysis
    router.post('/batch-analyze', async (req, res) => {
      try {
        const { ticketKeys, options } = req.body;

        if (!ticketKeys || !Array.isArray(ticketKeys)) {
          return res.status(400).json({
            success: false,
            error: 'Ticket keys array is required'
          });
        }

        const results = await this.tool.batchAnalyze(ticketKeys, options);
        res.json({
          success: true,
          data: results,
          summary: {
            total: results.length,
            successful: results.filter(r => r.success).length,
            failed: results.filter(r => !r.success).length
          }
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get statistics
    router.get('/stats', async (req, res) => {
      try {
        const stats = await this.tool.getStats();
        res.json({
          success: true,
          data: stats
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Cache management
    router.get('/cache/stats', (req, res) => {
      const stats = this.tool.getCacheStats();
      res.json({
        success: true,
        data: stats
      });
    });

    router.delete('/cache', (req, res) => {
      this.tool.clearCache();
      res.json({
        success: true,
        message: 'Cache cleared'
      });
    });

    return router;
  }

  /**
   * Setup Swagger documentation
   */
  setupSwagger() {
    const options = {
      definition: {
        openapi: '3.0.0',
        info: {
          title: 'JIRA Similarity Tool API',
          version: '2.0.0',
          description: 'AI-powered JIRA ticket similarity analysis and fix recommendations',
          contact: {
            name: 'JIRA Similarity Tool Team'
          }
        },
        servers: [
          {
            url: `http://localhost:${config.server.port}`,
            description: 'Development server'
          }
        ]
      },
      apis: ['./src/web-server.js']
    };

    const specs = swaggerJsdoc(options);
    this.app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));
  }

  /**
   * Start the server
   */
  start() {
    const port = config.server.port;
    const host = config.server.host;

    this.app.listen(port, host, () => {
      winston.info(`🚀 JIRA Similarity Tool web server started`);
      winston.info(`📍 Server running at http://${host}:${port}`);
      winston.info(`📚 API documentation at http://${host}:${port}/api-docs`);
      winston.info(`🔍 Health check at http://${host}:${port}/health`);
    });
  }
}

// Start server if this file is run directly
if (require.main === module) {
  const server = new WebServer();
  server.start();
}

module.exports = WebServer; 