const fs = require('fs').promises;
const path = require('path');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const winston = require('winston');
const config = require('../config/config');

class ExportService {
  constructor() {
    this.outputDirectory = config.export.outputDirectory;
    this.ensureOutputDirectory();
  }

  /**
   * Ensure output directory exists
   */
  async ensureOutputDirectory() {
    try {
      await fs.mkdir(this.outputDirectory, { recursive: true });
    } catch (error) {
      winston.error('Error creating output directory:', error.message);
    }
  }

  /**
   * Export analysis results to JSON
   * @param {Object} analysisResult - Analysis results
   * @param {string} ticketKey - Ticket key for filename
   * @returns {Promise<string>} File path
   */
  async exportToJSON(analysisResult, ticketKey) {
    try {
      const filename = `${ticketKey}_analysis.json`;
      const filepath = path.join(this.outputDirectory, filename);

      const exportData = {
        referenceTicket: analysisResult.referenceTicket,
        similarTickets: analysisResult.similarTickets.map(similar => ({
          ticket: similar.ticket,
          similarityScore: similar.similarityScore,
          summarySimilarity: similar.summarySimilarity,
          descriptionSimilarity: similar.descriptionSimilarity,
          metadataSimilarity: similar.metadataSimilarity,
          commonPatterns: similar.commonPatterns,
          recommendedFixes: similar.recommendedFixes
        })),
        analysisSummary: analysisResult.analysisSummary,
        searchQuery: analysisResult.searchQuery,
        exportedAt: new Date().toISOString(),
        metadata: {
          toolVersion: '2.0.0',
          analysisThreshold: config.analysis.similarityThreshold,
          maxResults: config.analysis.maxResults,
          totalFound: analysisResult.totalFound,
          similarCount: analysisResult.similarCount
        }
      };

      await fs.writeFile(filepath, JSON.stringify(exportData, null, 2));
      winston.info(`✅ Exported JSON to ${filepath}`);
      return filepath;
    } catch (error) {
      winston.error('Error exporting to JSON:', error.message);
      throw error;
    }
  }

  /**
   * Export similar tickets to CSV
   * @param {Array} similarTickets - Similar tickets array
   * @param {string} ticketKey - Ticket key for filename
   * @returns {Promise<string>} File path
   */
  async exportToCSV(similarTickets, ticketKey) {
    try {
      const filename = `${ticketKey}_similar_tickets.csv`;
      const filepath = path.join(this.outputDirectory, filename);

      const csvWriter = createCsvWriter({
        path: filepath,
        header: [
          { id: 'key', title: 'Key' },
          { id: 'summary', title: 'Summary' },
          { id: 'similarityScore', title: 'Similarity Score' },
          { id: 'status', title: 'Status' },
          { id: 'issueType', title: 'Issue Type' },
          { id: 'priority', title: 'Priority' },
          { id: 'components', title: 'Components' },
          { id: 'labels', title: 'Labels' },
          { id: 'resolution', title: 'Resolution' },
          { id: 'assignee', title: 'Assignee' },
          { id: 'created', title: 'Created' },
          { id: 'updated', title: 'Updated' }
        ]
      });

      const records = similarTickets.map(similar => ({
        key: similar.ticket.key,
        summary: similar.ticket.summary,
        similarityScore: similar.similarityScore.toFixed(3),
        status: similar.ticket.status,
        issueType: similar.ticket.issueType,
        priority: similar.ticket.priority,
        components: similar.ticket.components.join(', '),
        labels: similar.ticket.labels.join(', '),
        resolution: similar.ticket.resolution || 'N/A',
        assignee: similar.ticket.assignee || 'Unassigned',
        created: similar.ticket.created,
        updated: similar.ticket.updated
      }));

      await csvWriter.writeRecords(records);
      winston.info(`✅ Exported CSV to ${filepath}`);
      return filepath;
    } catch (error) {
      winston.error('Error exporting to CSV:', error.message);
      throw error;
    }
  }

  /**
   * Export analysis summary to JSON
   * @param {Object} analysisSummary - Analysis summary
   * @param {string} ticketKey - Ticket key for filename
   * @returns {Promise<string>} File path
   */
  async exportSummary(analysisSummary, ticketKey) {
    try {
      const filename = `${ticketKey}_summary.json`;
      const filepath = path.join(this.outputDirectory, filename);

      const summaryData = {
        ticketKey: ticketKey,
        analysisDate: new Date().toISOString(),
        summary: analysisSummary,
        metadata: {
          toolVersion: '2.0.0',
          analysisThreshold: config.analysis.similarityThreshold
        }
      };

      await fs.writeFile(filepath, JSON.stringify(summaryData, null, 2));
      winston.info(`✅ Exported summary to ${filepath}`);
      return filepath;
    } catch (error) {
      winston.error('Error exporting summary:', error.message);
      throw error;
    }
  }

  /**
   * Export fix recommendations to JSON
   * @param {Array} similarTickets - Similar tickets with fixes
   * @param {string} ticketKey - Ticket key for filename
   * @returns {Promise<string>} File path
   */
  async exportFixes(similarTickets, ticketKey) {
    try {
      const filename = `${ticketKey}_fixes.json`;
      const filepath = path.join(this.outputDirectory, filename);

      // Collect all unique fixes
      const allFixes = new Set();
      similarTickets.forEach(similar => {
        similar.recommendedFixes.forEach(fix => allFixes.add(fix));
      });

      const fixesData = {
        ticketKey: ticketKey,
        exportDate: new Date().toISOString(),
        totalSimilarTickets: similarTickets.length,
        uniqueFixes: Array.from(allFixes),
        fixesByTicket: similarTickets.map(similar => ({
          ticketKey: similar.ticket.key,
          similarityScore: similar.similarityScore,
          fixes: similar.recommendedFixes
        }))
      };

      await fs.writeFile(filepath, JSON.stringify(fixesData, null, 2));
      winston.info(`✅ Exported fixes to ${filepath}`);
      return filepath;
    } catch (error) {
      winston.error('Error exporting fixes:', error.message);
      throw error;
    }
  }

  /**
   * Export all analysis data
   * @param {Object} analysisResult - Complete analysis results
   * @param {string} ticketKey - Ticket key
   * @returns {Promise<Object>} Export results
   */
  async exportAll(analysisResult, ticketKey) {
    try {
      const results = {};

      // Export JSON analysis
      results.json = await this.exportToJSON(analysisResult, ticketKey);

      // Export CSV similar tickets
      results.csv = await this.exportToCSV(analysisResult.similarTickets, ticketKey);

      // Export summary
      results.summary = await this.exportSummary(analysisResult.analysisSummary, ticketKey);

      // Export fixes
      results.fixes = await this.exportFixes(analysisResult.similarTickets, ticketKey);

      winston.info(`✅ Exported all data for ${ticketKey}`);
      return results;
    } catch (error) {
      winston.error('Error exporting all data:', error.message);
      throw error;
    }
  }

  /**
   * Get export statistics
   * @returns {Promise<Object>} Export statistics
   */
  async getExportStats() {
    try {
      const files = await fs.readdir(this.outputDirectory);
      const stats = {
        totalFiles: files.length,
        fileTypes: {},
        totalSize: 0
      };

      for (const file of files) {
        const filepath = path.join(this.outputDirectory, file);
        const fileStats = await fs.stat(filepath);
        const ext = path.extname(file).toLowerCase();

        stats.fileTypes[ext] = (stats.fileTypes[ext] || 0) + 1;
        stats.totalSize += fileStats.size;
      }

      return stats;
    } catch (error) {
      winston.error('Error getting export stats:', error.message);
      return { totalFiles: 0, fileTypes: {}, totalSize: 0 };
    }
  }

  /**
   * Clean old exports
   * @param {number} daysOld - Number of days old to clean
   * @returns {Promise<number>} Number of files cleaned
   */
  async cleanOldExports(daysOld = 30) {
    try {
      const files = await fs.readdir(this.outputDirectory);
      const cutoffDate = new Date(Date.now() - (daysOld * 24 * 60 * 60 * 1000));
      let cleanedCount = 0;

      for (const file of files) {
        const filepath = path.join(this.outputDirectory, file);
        const fileStats = await fs.stat(filepath);

        if (fileStats.mtime < cutoffDate) {
          await fs.unlink(filepath);
          cleanedCount++;
        }
      }

      winston.info(`✅ Cleaned ${cleanedCount} old export files`);
      return cleanedCount;
    } catch (error) {
      winston.error('Error cleaning old exports:', error.message);
      return 0;
    }
  }
}

module.exports = ExportService; 