const natural = require('natural');
const nlp = require('compromise');
const winston = require('winston');
const config = require('../config/config');

class SimilarityEngine {
  constructor() {
    this.tokenizer = new natural.WordTokenizer();
    this.tfidf = new natural.TfIdf();
    this.stopWords = new Set(natural.stopwords);
    
    // Initialize NLP models
    this.initializeNLP();
  }

  /**
   * Initialize NLP components
   */
  initializeNLP() {
    try {
      // Load additional stop words
      const additionalStopWords = [
        'bug', 'issue', 'problem', 'error', 'fix', 'resolve', 'ticket',
        'jira', 'atlassian', 'project', 'team', 'user', 'system'
      ];
      
      additionalStopWords.forEach(word => this.stopWords.add(word));
      
      winston.info('✅ NLP engine initialized successfully');
    } catch (error) {
      winston.error('❌ Error initializing NLP engine:', error.message);
    }
  }

  /**
   * Calculate text similarity using TF-IDF and cosine similarity
   * @param {string} text1 - First text
   * @param {string} text2 - Second text
   * @returns {number} Similarity score (0-1)
   */
  calculateTextSimilarity(text1, text2) {
    if (!text1 || !text2) return 0.0;

    try {
      // Preprocess texts
      const processedText1 = this.preprocessText(text1);
      const processedText2 = this.preprocessText(text2);

      if (!processedText1 || !processedText2) return 0.0;

      // Create TF-IDF vectors
      this.tfidf.resetDocument();
      this.tfidf.addDocument(processedText1);
      this.tfidf.addDocument(processedText2);

      // Calculate cosine similarity
      const similarity = this.calculateCosineSimilarity(processedText1, processedText2);
      
      return Math.max(0.0, Math.min(1.0, similarity));
    } catch (error) {
      winston.warn('Similarity calculation error:', error.message);
      return 0.0;
    }
  }

  /**
   * Preprocess text for analysis
   * @param {string} text - Raw text
   * @returns {string} Preprocessed text
   */
  preprocessText(text) {
    if (!text) return '';

    try {
      // Convert to lowercase
      let processed = text.toLowerCase();

      // Remove special characters and numbers
      processed = processed.replace(/[^a-zA-Z\s]/g, ' ');

      // Tokenize
      const tokens = this.tokenizer.tokenize(processed);

      // Remove stop words and short tokens
      const filteredTokens = tokens.filter(token => 
        token && 
        token.length > 2 && 
        !this.stopWords.has(token)
      );

      // Join tokens back into text
      return filteredTokens.join(' ');
    } catch (error) {
      winston.warn('Text preprocessing error:', error.message);
      return '';
    }
  }

  /**
   * Calculate cosine similarity between two texts
   * @param {string} text1 - First text
   * @param {string} text2 - Second text
   * @returns {number} Cosine similarity score
   */
  calculateCosineSimilarity(text1, text2) {
    try {
      // Create word frequency maps
      const freq1 = this.createWordFrequencyMap(text1);
      const freq2 = this.createWordFrequencyMap(text2);

      // Get all unique words
      const allWords = new Set([...Object.keys(freq1), ...Object.keys(freq2)]);

      // Calculate dot product and magnitudes
      let dotProduct = 0;
      let magnitude1 = 0;
      let magnitude2 = 0;

      for (const word of allWords) {
        const f1 = freq1[word] || 0;
        const f2 = freq2[word] || 0;

        dotProduct += f1 * f2;
        magnitude1 += f1 * f1;
        magnitude2 += f2 * f2;
      }

      // Calculate cosine similarity
      const magnitude = Math.sqrt(magnitude1) * Math.sqrt(magnitude2);
      return magnitude > 0 ? dotProduct / magnitude : 0;
    } catch (error) {
      winston.warn('Cosine similarity calculation error:', error.message);
      return 0;
    }
  }

  /**
   * Create word frequency map
   * @param {string} text - Input text
   * @returns {Object} Word frequency map
   */
  createWordFrequencyMap(text) {
    const words = text.split(/\s+/);
    const freqMap = {};

    words.forEach(word => {
      if (word && word.length > 2) {
        freqMap[word] = (freqMap[word] || 0) + 1;
      }
    });

    return freqMap;
  }

  /**
   * Calculate metadata similarity
   * @param {Object} ticket1 - First ticket
   * @param {Object} ticket2 - Second ticket
   * @returns {number} Metadata similarity score
   */
  calculateMetadataSimilarity(ticket1, ticket2) {
    let score = 0.0;

    try {
      // Component similarity
      if (ticket1.components && ticket2.components && ticket1.components.length > 0 && ticket2.components.length > 0) {
        const commonComponents = ticket1.components.filter(comp => ticket2.components.includes(comp));
        if (commonComponents.length > 0) {
          score += (commonComponents.length / Math.max(ticket1.components.length, ticket2.components.length)) * 0.3;
        }
      }

      // Label similarity
      if (ticket1.labels && ticket2.labels && ticket1.labels.length > 0 && ticket2.labels.length > 0) {
        const commonLabels = ticket1.labels.filter(label => ticket2.labels.includes(label));
        if (commonLabels.length > 0) {
          score += (commonLabels.length / Math.max(ticket1.labels.length, ticket2.labels.length)) * 0.2;
        }
      }

      // Issue type similarity
      if (ticket1.issueType === ticket2.issueType) {
        score += 0.2;
      }

      // Priority similarity
      if (ticket1.priority === ticket2.priority) {
        score += 0.1;
      }

      // Status similarity (resolved tickets are more valuable for recommendations)
      if (ticket1.status === ticket2.status) {
        score += 0.1;
      } else if (ticket1.status === 'Resolved' && ticket2.status === 'Resolved') {
        score += 0.2;
      }

      return Math.min(1.0, score);
    } catch (error) {
      winston.warn('Metadata similarity calculation error:', error.message);
      return 0.0;
    }
  }

  /**
   * Find similar tickets
   * @param {Object} referenceTicket - Reference ticket
   * @param {Array} allTickets - All tickets to compare against
   * @param {number} threshold - Similarity threshold
   * @returns {Array} Similar tickets with scores
   */
  findSimilarTickets(referenceTicket, allTickets, threshold = config.analysis.similarityThreshold) {
    const similarTickets = [];

    try {
      for (const ticket of allTickets) {
        if (ticket.key === referenceTicket.key) continue;

        // Calculate similarities
        const summarySimilarity = this.calculateTextSimilarity(
          referenceTicket.summary, ticket.summary
        );
        
        const descSimilarity = this.calculateTextSimilarity(
          referenceTicket.description, ticket.description
        );
        
        const metadataSimilarity = this.calculateMetadataSimilarity(referenceTicket, ticket);

        // Weighted overall similarity
        const overallSimilarity = (
          summarySimilarity * 0.4 +
          descSimilarity * 0.3 +
          metadataSimilarity * 0.3
        );

        if (overallSimilarity >= threshold) {
          similarTickets.push({
            ticket: ticket,
            similarityScore: overallSimilarity,
            summarySimilarity: summarySimilarity,
            descriptionSimilarity: descSimilarity,
            metadataSimilarity: metadataSimilarity,
            commonPatterns: this.extractCommonPatterns(referenceTicket, ticket),
            recommendedFixes: this.generateFixes(ticket)
          });
        }
      }

      // Sort by similarity score
      similarTickets.sort((a, b) => b.similarityScore - a.similarityScore);
      
      winston.info(`Found ${similarTickets.length} similar tickets`);
      return similarTickets;
    } catch (error) {
      winston.error('Error finding similar tickets:', error.message);
      return [];
    }
  }

  /**
   * Extract common patterns between two tickets
   * @param {Object} ticket1 - First ticket
   * @param {Object} ticket2 - Second ticket
   * @returns {Array} Common patterns
   */
  extractCommonPatterns(ticket1, ticket2) {
    const patterns = [];

    try {
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

      // Remove duplicates and limit results
      return [...new Set(patterns)].slice(0, 5);
    } catch (error) {
      winston.warn('Error extracting common patterns:', error.message);
      return [];
    }
  }

  /**
   * Generate fix recommendations based on ticket content
   * @param {Object} ticket - Ticket to analyze
   * @returns {Array} Recommended fixes
   */
  generateFixes(ticket) {
    const fixes = [];

    try {
      const summary = ticket.summary.toLowerCase();
      const description = ticket.description.toLowerCase();

      // Database-related issues
      if (summary.includes('database') || description.includes('database') || 
          summary.includes('connection') || description.includes('connection') ||
          summary.includes('timeout') || description.includes('timeout') ||
          summary.includes('pool') || description.includes('pool')) {
        fixes.push(
          'Check database connection pool settings',
          'Verify database server resources and load',
          'Add connection timeout handling and retry logic',
          'Implement connection monitoring and alerting',
          'Review database query performance and indexing'
        );
      }
      // Performance issues
      else if (summary.includes('performance') || description.includes('performance') ||
               summary.includes('slow') || description.includes('slow') ||
               summary.includes('timeout') || description.includes('timeout') ||
               summary.includes('response') || description.includes('response')) {
        fixes.push(
          'Profile application performance bottlenecks',
          'Optimize database queries and add proper indexing',
          'Implement caching mechanisms (Redis, Memcached)',
          'Review resource allocation and scaling',
          'Add performance monitoring and alerting'
        );
      }
      // Memory issues
      else if (summary.includes('memory') || description.includes('memory') ||
               summary.includes('leak') || description.includes('leak') ||
               summary.includes('out of memory') || description.includes('out of memory')) {
        fixes.push(
          'Check for memory leaks in application code',
          'Review object lifecycle and resource management',
          'Implement proper resource cleanup and disposal',
          'Add memory monitoring and garbage collection tuning',
          'Consider increasing heap size or optimizing data structures'
        );
      }
      // API issues
      else if (summary.includes('api') || description.includes('api') ||
               summary.includes('endpoint') || description.includes('endpoint') ||
               summary.includes('rest') || description.includes('rest')) {
        fixes.push(
          'Add proper API error handling and validation',
          'Implement rate limiting and throttling',
          'Add API monitoring and logging',
          'Review API response times and optimization',
          'Implement proper API versioning and backward compatibility'
        );
      }
      // General bug fixes
      else {
        fixes.push(
          'Add comprehensive error handling and logging',
          'Implement input validation and sanitization',
          'Add unit tests and integration tests',
          'Review error messages and user feedback',
          'Implement proper exception handling'
        );
      }

      return fixes.slice(0, 5);
    } catch (error) {
      winston.warn('Error generating fixes:', error.message);
      return ['Add proper error handling and logging'];
    }
  }

  /**
   * Analyze text sentiment
   * @param {string} text - Text to analyze
   * @returns {Object} Sentiment analysis results
   */
  analyzeSentiment(text) {
    try {
      const doc = nlp(text);
      const sentiment = doc.sentiment();
      
      return {
        score: sentiment.score,
        comparative: sentiment.comparative,
        tokens: sentiment.tokens,
        words: sentiment.words,
        positive: sentiment.positive,
        negative: sentiment.negative
      };
    } catch (error) {
      winston.warn('Sentiment analysis error:', error.message);
      return { score: 0, comparative: 0, tokens: [], words: [], positive: [], negative: [] };
    }
  }

  /**
   * Extract key phrases from text
   * @param {string} text - Text to analyze
   * @returns {Array} Key phrases
   */
  extractKeyPhrases(text) {
    try {
      const doc = nlp(text);
      const phrases = doc.match('#Noun+').out('array');
      return phrases.slice(0, 10);
    } catch (error) {
      winston.warn('Key phrase extraction error:', error.message);
      return [];
    }
  }
}

module.exports = SimilarityEngine; 