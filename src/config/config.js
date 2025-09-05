const dotenv = require('dotenv');
const path = require('path');
const Joi = require('joi');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../.env') });

// Configuration schema validation
const configSchema = Joi.object({
  // JIRA Configuration
  jira: Joi.object({
    baseUrl: Joi.string().uri().required(),
    email: Joi.string().email().required(),
    apiToken: Joi.string().min(1).required(),
    timeout: Joi.number().default(30000),
    maxRetries: Joi.number().default(3)
  }).required(),

  // Analysis Configuration
  analysis: Joi.object({
    similarityThreshold: Joi.number().min(0).max(1).default(0.3),
    maxResults: Joi.number().min(10).max(1000).default(100),
    minConfidence: Joi.number().min(0).max(1).default(0.2),
    enableNLP: Joi.boolean().default(true),
    enablePatternRecognition: Joi.boolean().default(true)
  }).required(),

  // Server Configuration
  server: Joi.object({
    port: Joi.number().min(1024).max(65535).default(3000),
    host: Joi.string().default('0.0.0.0'),
    cors: Joi.boolean().default(true),
    rateLimit: Joi.object({
      windowMs: Joi.number().default(15 * 60 * 1000), // 15 minutes
      max: Joi.number().default(100) // limit each IP to 100 requests per windowMs
    }).default()
  }).required(),

  // Logging Configuration
  logging: Joi.object({
    level: Joi.string().valid('error', 'warn', 'info', 'debug').default('info'),
    file: Joi.boolean().default(true),
    console: Joi.boolean().default(true),
    maxFiles: Joi.number().default(5),
    maxSize: Joi.string().default('10m')
  }).required(),

  // Export Configuration
  export: Joi.object({
    defaultFormat: Joi.string().valid('json', 'csv', 'xlsx').default('json'),
    outputDirectory: Joi.string().default('./exports'),
    includeMetadata: Joi.boolean().default(true),
    compressOutput: Joi.boolean().default(false)
  }).required(),

  // Security Configuration
  security: Joi.object({
    enableAuth: Joi.boolean().default(false),
    jwtSecret: Joi.string().default('your-secret-key'),
    bcryptRounds: Joi.number().default(10),
    sessionTimeout: Joi.number().default(24 * 60 * 60 * 1000) // 24 hours
  }).required(),

  // Cache Configuration
  cache: Joi.object({
    enabled: Joi.boolean().default(true),
    ttl: Joi.number().default(300000), // 5 minutes
    maxSize: Joi.number().default(1000)
  }).required()
});

// Default configuration
const defaultConfig = {
  jira: {
    baseUrl: process.env.JIRA_BASE_URL || 'https://koreteam.atlassian.net',
    email: process.env.JIRA_EMAIL || 'hemanth.bandaru@kore.com',
    apiToken: process.env.JIRA_API_TOKEN || 'ATATT3xFfGF0m02NU4ZUMj-S19L289vvA7kqh-g6RdU6vYzSYx-8ZBi4nbvCi6oln05pN6UcSN0BT4_UOAhSlP_0iS4FzLeAPSXjMW6sVRr6A-lK_PN-X_q7hoX28AXUhhqGYAsPWvN9QVx1eXi0MmPVaVwnFZnBb9FcnqICjRPKZnUd2AZR7go=009EED60',
    timeout: parseInt(process.env.JIRA_TIMEOUT) || 30000,
    maxRetries: parseInt(process.env.JIRA_MAX_RETRIES) || 3
  },
  analysis: {
    similarityThreshold: parseFloat(process.env.SIMILARITY_THRESHOLD) || 0.1,
    maxResults: parseInt(process.env.MAX_RESULTS) || 100,
    minConfidence: parseFloat(process.env.MIN_CONFIDENCE) || 0.2,
    enableNLP: process.env.ENABLE_NLP !== 'false',
    enablePatternRecognition: process.env.ENABLE_PATTERN_RECOGNITION !== 'false'
  },
  server: {
    port: parseInt(process.env.PORT) || 3000,
    host: process.env.HOST || '0.0.0.0',
    cors: process.env.ENABLE_CORS !== 'false',
    rateLimit: {
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100
    }
  },
  logging: {
    level: (process.env.LOG_LEVEL || 'info').toLowerCase(),
    file: process.env.LOG_TO_FILE !== 'false',
    console: process.env.LOG_TO_CONSOLE !== 'false',
    maxFiles: parseInt(process.env.LOG_MAX_FILES) || 5,
    maxSize: process.env.LOG_MAX_SIZE || '10m'
  },
  export: {
    defaultFormat: process.env.EXPORT_FORMAT || 'json',
    outputDirectory: process.env.OUTPUT_DIRECTORY || './exports',
    includeMetadata: process.env.INCLUDE_METADATA !== 'false',
    compressOutput: process.env.COMPRESS_OUTPUT === 'true'
  },
  security: {
    enableAuth: process.env.ENABLE_AUTH === 'true',
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 10,
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 24 * 60 * 60 * 1000
  },
  cache: {
    enabled: process.env.ENABLE_CACHE !== 'false',
    ttl: parseInt(process.env.CACHE_TTL) || 300000,
    maxSize: parseInt(process.env.CACHE_MAX_SIZE) || 1000
  }
};

// Validate configuration
const { error, value: config } = configSchema.validate(defaultConfig, {
  abortEarly: false,
  allowUnknown: true
});

if (error) {
  console.error('Configuration validation error:', error.details);
  process.exit(1);
}

// Export validated configuration
module.exports = config; 