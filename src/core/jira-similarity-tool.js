const JIRAClient = require('../services/jira-client');
const SimilarityEngine = require('../services/similarity-engine');
const ExportService = require('../services/export-service');
const winston = require('winston');
const config = require('../config/config');

class JIRASimilarityTool {
  constructor() {
    this.jiraClient = new JIRAClient();
    this.similarityEngine = new SimilarityEngine();
    this.exportService = new ExportService();
    this.cache = new Map();
  }

  /**
   * Test JIRA connection
   * @returns {Promise<boolean>}
   */
  async testConnection() {
    try {
      return await this.jiraClient.testConnection();
    } catch (error) {
      winston.error('Connection test failed:', error.message);
      return false;
    }
  }

  /**
   * Analyze a ticket and find similar issues
   * @param {string} ticketKey - Ticket key to analyze
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeTicket(ticketKey, options = {}) {
    const startTime = Date.now();
    
    try {
      winston.info(`🔍 Starting analysis for ticket: ${ticketKey}`);

      // Validate input
      if (!ticketKey || typeof ticketKey !== 'string') {
        throw new Error('Invalid ticket key provided');
      }

      // Check cache first
      const cacheKey = `${ticketKey}_${JSON.stringify(options)}`;
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < config.cache.ttl) {
          winston.info('✅ Returning cached results');
          return cached.data;
        }
      }

      // Get reference ticket
      winston.info('📋 Fetching reference ticket...');
      const referenceTicket = await this.jiraClient.getTicket(ticketKey);
      
      if (!referenceTicket) {
        throw new Error(`Failed to fetch ticket ${ticketKey}`);
      }

      // Build search query
      winston.info('🔍 Building search query...');
      const searchQuery = this.jiraClient.buildSimilarityJQL(referenceTicket);

      // Search for similar tickets
      winston.info('🔍 Searching for similar tickets...');
      const maxResults = options.maxResults || config.analysis.maxResults;
      const allTickets = await this.jiraClient.searchTickets(searchQuery, maxResults);

      // Find similar tickets using AI
      winston.info('🤖 Analyzing similarities...');
      const threshold = options.similarityThreshold || config.analysis.similarityThreshold;
      const similarTickets = this.similarityEngine.findSimilarTickets(
        referenceTicket, 
        allTickets, 
        threshold
      );

      // Generate analysis summary
      winston.info('📊 Generating analysis summary...');
      const analysisSummary = this.generateAnalysisSummary(referenceTicket, similarTickets);

      // Prepare results
      const results = {
        success: true,
        referenceTicket: referenceTicket,
        similarTickets: similarTickets,
        analysisSummary: analysisSummary,
        searchQuery: searchQuery,
        totalFound: allTickets.length,
        similarCount: similarTickets.length,
        analysisTime: Date.now() - startTime,
        metadata: {
          toolVersion: '2.0.0',
          analysisDate: new Date().toISOString(),
          threshold: threshold,
          maxResults: maxResults
        }
      };

      // Cache results
      if (config.cache.enabled) {
        this.cache.set(cacheKey, {
          data: results,
          timestamp: Date.now()
        });

        // Clean cache if too large
        if (this.cache.size > config.cache.maxSize) {
          this.cleanCache();
        }
      }

      winston.info(`✅ Analysis completed in ${results.analysisTime}ms`);
      return results;

    } catch (error) {
      winston.error('❌ Analysis failed:', error.message);
      return {
        success: false,
        error: error.message,
        ticketKey: ticketKey,
        analysisTime: Date.now() - startTime
      };
    }
  }

  /**
   * Generate comprehensive analysis summary
   * @param {Object} referenceTicket - Reference ticket
   * @param {Array} similarTickets - Similar tickets
   * @returns {Object} Analysis summary
   */
  generateAnalysisSummary(referenceTicket, similarTickets) {
    try {
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

      // Calculate similarity distribution
      const highSimilarity = similarTickets.filter(s => s.similarityScore >= 0.7).length;
      const mediumSimilarity = similarTickets.filter(s => s.similarityScore >= 0.4 && s.similarityScore < 0.7).length;
      const lowSimilarity = similarTickets.filter(s => s.similarityScore < 0.4).length;

      // Count resolved tickets
      const resolvedCount = similarTickets.filter(s => s.ticket.status === 'Resolved').length;

      // Extract common patterns
      const allPatterns = new Set();
      similarTickets.forEach(similar => {
        similar.commonPatterns.forEach(pattern => allPatterns.add(pattern));
      });

      // Extract top fixes
      const allFixes = new Set();
      similarTickets.forEach(similar => {
        similar.recommendedFixes.forEach(fix => allFixes.add(fix));
      });

      // Calculate average similarity
      const averageSimilarity = similarTickets.reduce((sum, s) => sum + s.similarityScore, 0) / similarTickets.length;

      // Calculate time savings
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
    } catch (error) {
      winston.error('Error generating analysis summary:', error.message);
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
  }

  /**
   * Export analysis results
   * @param {Object} analysisResult - Analysis results
   * @param {string} format - Export format (json, csv, all)
   * @returns {Promise<Object>} Export results
   */
  async exportResults(analysisResult, format = 'all') {
    try {
      if (!analysisResult.success) {
        throw new Error('Cannot export failed analysis');
      }

      const ticketKey = analysisResult.referenceTicket.key;

      switch (format.toLowerCase()) {
        case 'json':
          return { json: await this.exportService.exportToJSON(analysisResult, ticketKey) };
        
        case 'csv':
          return { csv: await this.exportService.exportToCSV(analysisResult.similarTickets, ticketKey) };
        
        case 'summary':
          return { summary: await this.exportService.exportSummary(analysisResult.analysisSummary, ticketKey) };
        
        case 'fixes':
          return { fixes: await this.exportService.exportFixes(analysisResult.similarTickets, ticketKey) };
        
        case 'all':
        default:
          return await this.exportService.exportAll(analysisResult, ticketKey);
      }
    } catch (error) {
      winston.error('Error exporting results:', error.message);
      throw error;
    }
  }

  /**
   * Get ticket details
   * @param {string} ticketKey - Ticket key
   * @returns {Promise<Object>} Ticket details
   */
  async getTicketDetails(ticketKey) {
    try {
      const ticket = await this.jiraClient.getTicket(ticketKey);
      if (!ticket) {
        throw new Error(`Ticket ${ticketKey} not found`);
      }

      // Get additional details
      const [comments, worklog] = await Promise.all([
        this.jiraClient.getComments(ticketKey),
        this.jiraClient.getWorklog(ticketKey)
      ]);

      return {
        ticket: ticket,
        comments: comments,
        worklog: worklog,
        metadata: {
          totalComments: comments.length,
          totalWorklogEntries: worklog.length,
          totalTimeSpent: worklog.reduce((sum, entry) => sum + (entry.timeSpentSeconds || 0), 0)
        }
      };
    } catch (error) {
      winston.error(`Error getting ticket details for ${ticketKey}:`, error.message);
      throw error;
    }
  }

  /**
   * Batch analyze multiple tickets
   * @param {Array<string>} ticketKeys - Array of ticket keys
   * @param {Object} options - Analysis options
   * @returns {Promise<Array>} Analysis results
   */
  async batchAnalyze(ticketKeys, options = {}) {
    try {
      winston.info(`🔄 Starting batch analysis for ${ticketKeys.length} tickets`);

      const results = [];
      const batchSize = options.batchSize || 5;
      const delay = options.delay || 1000; // 1 second delay between batches

      for (let i = 0; i < ticketKeys.length; i += batchSize) {
        const batch = ticketKeys.slice(i, i + batchSize);
        
        winston.info(`Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(ticketKeys.length / batchSize)}`);
        
        const batchResults = await Promise.all(
          batch.map(ticketKey => this.analyzeTicket(ticketKey, options))
        );
        
        results.push(...batchResults);

        // Add delay between batches to avoid rate limiting
        if (i + batchSize < ticketKeys.length) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }

      winston.info(`✅ Batch analysis completed for ${results.length} tickets`);
      return results;
    } catch (error) {
      winston.error('Error in batch analysis:', error.message);
      throw error;
    }
  }

  /**
   * Clean cache
   */
  cleanCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > config.cache.ttl) {
        this.cache.delete(key);
      }
    }
    winston.debug(`Cache cleaned, ${this.cache.size} entries remaining`);
  }

  /**
   * Get cache statistics
   * @returns {Object} Cache statistics
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: config.cache.maxSize,
      ttl: config.cache.ttl,
      enabled: config.cache.enabled
    };
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    winston.info('Cache cleared');
  }

  /**
   * Get tool statistics
   * @returns {Promise<Object>} Tool statistics
   */
  async getStats() {
    try {
      const [exportStats, cacheStats] = await Promise.all([
        this.exportService.getExportStats(),
        Promise.resolve(this.getCacheStats())
      ]);

      return {
        tool: {
          version: '2.0.0',
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          config: {
            similarityThreshold: config.analysis.similarityThreshold,
            maxResults: config.analysis.maxResults,
            enableNLP: config.analysis.enableNLP
          }
        },
        cache: cacheStats,
        exports: exportStats
      };
    } catch (error) {
      winston.error('Error getting tool stats:', error.message);
      throw error;
    }
  }
}

module.exports = JIRASimilarityTool; 