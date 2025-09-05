#!/usr/bin/env node

const { Command } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');
const { table } = require('table');
const winston = require('winston');
const path = require('path');

const config = require('./config/config');
const JIRASimilarityTool = require('./core/jira-similarity-tool');

// Configure logging for CLI
winston.configure({
  level: 'error', // Only show errors in CLI
  format: winston.format.simple()
});

class CLI {
  constructor() {
    this.program = new Command();
    this.tool = new JIRASimilarityTool();
    this.setupCommands();
  }

  /**
   * Setup CLI commands
   */
  setupCommands() {
    this.program
      .name('jira-similarity')
      .description('AI-powered JIRA ticket similarity analysis and fix recommendations')
      .version('2.0.0');

    // Test connection command
    this.program
      .command('test')
      .description('Test JIRA API connection')
      .action(async () => {
        await this.testConnection();
      });

    // Analyze command
    this.program
      .command('analyze')
      .description('Analyze a JIRA ticket for similar issues')
      .argument('<ticket-key>', 'JIRA ticket key (e.g., PLAT-39562)')
      .option('-t, --threshold <number>', 'Similarity threshold (0-1)', config.analysis.similarityThreshold)
      .option('-m, --max-results <number>', 'Maximum results to analyze', config.analysis.maxResults)
      .option('-e, --export <format>', 'Export format (json, csv, all)', 'json')
      .option('-o, --output <path>', 'Output directory', config.export.outputDirectory)
      .action(async (ticketKey, options) => {
        await this.analyzeTicket(ticketKey, options);
      });

    // Batch analyze command
    this.program
      .command('batch')
      .description('Analyze multiple tickets')
      .option('-f, --file <path>', 'File containing ticket keys (one per line)')
      .option('-t, --threshold <number>', 'Similarity threshold (0-1)', config.analysis.similarityThreshold)
      .option('-m, --max-results <number>', 'Maximum results per ticket', config.analysis.maxResults)
      .option('-e, --export <format>', 'Export format (json, csv, all)', 'json')
      .action(async (options) => {
        await this.batchAnalyze(options);
      });

    // Interactive command
    this.program
      .command('interactive')
      .description('Start interactive mode')
      .action(async () => {
        await this.interactiveMode();
      });

    // Stats command
    this.program
      .command('stats')
      .description('Show tool statistics')
      .action(async () => {
        await this.showStats();
      });

    // Cache commands
    this.program
      .command('cache')
      .description('Cache management')
      .option('-s, --stats', 'Show cache statistics')
      .option('-c, --clear', 'Clear cache')
      .action(async (options) => {
        await this.manageCache(options);
      });

    // Setup command
    this.program
      .command('setup')
      .description('Interactive setup and configuration')
      .action(async () => {
        await this.setup();
      });
  }

  /**
   * Test JIRA connection
   */
  async testConnection() {
    const spinner = ora('Testing JIRA connection...').start();

    try {
      const isConnected = await this.tool.testConnection();
      
      if (isConnected) {
        spinner.succeed(chalk.green('✅ JIRA connection successful'));
      } else {
        spinner.fail(chalk.red('❌ JIRA connection failed'));
        console.log(chalk.yellow('Please check your configuration in .env file'));
      }
    } catch (error) {
      spinner.fail(chalk.red('❌ Connection test failed'));
      console.error(chalk.red(error.message));
    }
  }

  /**
   * Analyze a single ticket
   */
  async analyzeTicket(ticketKey, options) {
    const spinner = ora(`Analyzing ticket ${ticketKey}...`).start();

    try {
      const analysisOptions = {
        similarityThreshold: parseFloat(options.threshold),
        maxResults: parseInt(options.maxResults)
      };

      const result = await this.tool.analyzeTicket(ticketKey, analysisOptions);

      if (result.success) {
        spinner.succeed(chalk.green(`✅ Analysis completed for ${ticketKey}`));
        
        // Display results
        this.displayAnalysisResults(result);

        // Export if requested
        if (options.export) {
          await this.exportResults(result, options.export, ticketKey);
        }
      } else {
        spinner.fail(chalk.red(`❌ Analysis failed for ${ticketKey}`));
        console.error(chalk.red(result.error));
      }
    } catch (error) {
      spinner.fail(chalk.red('❌ Analysis failed'));
      console.error(chalk.red(error.message));
    }
  }

  /**
   * Display analysis results
   */
  displayAnalysisResults(result) {
    console.log('\n' + chalk.blue.bold('📊 Analysis Results'));
    console.log(chalk.gray('─'.repeat(50)));

    // Summary metrics
    const summary = result.analysisSummary;
    console.log(chalk.cyan(`Total Similar Tickets: ${summary.totalSimilar}`));
    console.log(chalk.cyan(`High Similarity: ${summary.highSimilarity}`));
    console.log(chalk.cyan(`Medium Similarity: ${summary.mediumSimilarity}`));
    console.log(chalk.cyan(`Low Similarity: ${summary.lowSimilarity}`));
    console.log(chalk.cyan(`Resolved Tickets: ${summary.resolvedCount}`));
    console.log(chalk.cyan(`Time Saved: ${summary.timeSaved}`));
    console.log(chalk.cyan(`Average Similarity: ${summary.averageSimilarity}`));

    // Similar tickets table
    if (result.similarTickets.length > 0) {
      console.log('\n' + chalk.blue.bold('🔍 Similar Tickets'));
      console.log(chalk.gray('─'.repeat(80)));

      const tableData = [
        ['Key', 'Summary', 'Similarity', 'Status', 'Type', 'Priority']
      ];

      result.similarTickets.slice(0, 10).forEach(similar => {
        const ticket = similar.ticket;
        tableData.push([
          ticket.key,
          ticket.summary.length > 40 ? ticket.summary.substring(0, 40) + '...' : ticket.summary,
          similar.similarityScore.toFixed(3),
          ticket.status,
          ticket.issueType,
          ticket.priority
        ]);
      });

      console.log(table(tableData));
    }

    // Fix recommendations
    if (summary.topFixes.length > 0) {
      console.log('\n' + chalk.blue.bold('🛠️ Fix Recommendations'));
      console.log(chalk.gray('─'.repeat(50)));

      summary.topFixes.forEach((fix, index) => {
        console.log(chalk.green(`${index + 1}. ${fix}`));
      });
    }
  }

  /**
   * Export results
   */
  async exportResults(result, format, ticketKey) {
    const spinner = ora('Exporting results...').start();

    try {
      const exportResult = await this.tool.exportResults(result, format);
      spinner.succeed(chalk.green('✅ Export completed'));

      console.log(chalk.cyan('\n📤 Exported Files:'));
      Object.entries(exportResult).forEach(([type, filepath]) => {
        console.log(chalk.gray(`  ${type.toUpperCase()}: ${filepath}`));
      });
    } catch (error) {
      spinner.fail(chalk.red('❌ Export failed'));
      console.error(chalk.red(error.message));
    }
  }

  /**
   * Batch analyze tickets
   */
  async batchAnalyze(options) {
    let ticketKeys = [];

    if (options.file) {
      try {
        const fs = require('fs').promises;
        const content = await fs.readFile(options.file, 'utf8');
        ticketKeys = content.split('\n').filter(line => line.trim());
      } catch (error) {
        console.error(chalk.red(`❌ Error reading file: ${error.message}`));
        return;
      }
    } else {
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'ticketKeys',
          message: 'Enter ticket keys (comma-separated):',
          validate: (input) => input.trim().length > 0 ? true : 'Please enter ticket keys'
        }
      ]);
      ticketKeys = answers.ticketKeys.split(',').map(key => key.trim());
    }

    if (ticketKeys.length === 0) {
      console.error(chalk.red('❌ No ticket keys provided'));
      return;
    }

    const spinner = ora(`Analyzing ${ticketKeys.length} tickets...`).start();

    try {
      const batchOptions = {
        similarityThreshold: parseFloat(options.threshold),
        maxResults: parseInt(options.maxResults),
        batchSize: 5,
        delay: 1000
      };

      const results = await this.tool.batchAnalyze(ticketKeys, batchOptions);
      
      const successful = results.filter(r => r.success).length;
      const failed = results.filter(r => !r.success).length;

      spinner.succeed(chalk.green(`✅ Batch analysis completed`));
      console.log(chalk.cyan(`\n📊 Summary:`));
      console.log(chalk.cyan(`  Total: ${results.length}`));
      console.log(chalk.cyan(`  Successful: ${successful}`));
      console.log(chalk.cyan(`  Failed: ${failed}`));

      // Export if requested
      if (options.export) {
        for (const result of results) {
          if (result.success) {
            await this.exportResults(result, options.export, result.referenceTicket.key);
          }
        }
      }
    } catch (error) {
      spinner.fail(chalk.red('❌ Batch analysis failed'));
      console.error(chalk.red(error.message));
    }
  }

  /**
   * Interactive mode
   */
  async interactiveMode() {
    console.log(chalk.blue.bold('🎯 JIRA Similarity Tool - Interactive Mode'));
    console.log(chalk.gray('─'.repeat(50)));

    while (true) {
      const answers = await inquirer.prompt([
        {
          type: 'list',
          name: 'action',
          message: 'What would you like to do?',
          choices: [
            { name: '🔍 Analyze a ticket', value: 'analyze' },
            { name: '📊 Show statistics', value: 'stats' },
            { name: '🔗 Test connection', value: 'test' },
            { name: '⚙️ Setup configuration', value: 'setup' },
            { name: '🚪 Exit', value: 'exit' }
          ]
        }
      ]);

      switch (answers.action) {
        case 'analyze':
          await this.interactiveAnalyze();
          break;
        case 'stats':
          await this.showStats();
          break;
        case 'test':
          await this.testConnection();
          break;
        case 'setup':
          await this.setup();
          break;
        case 'exit':
          console.log(chalk.blue('👋 Goodbye!'));
          process.exit(0);
      }

      console.log('\n' + chalk.gray('─'.repeat(50)) + '\n');
    }
  }

  /**
   * Interactive analyze
   */
  async interactiveAnalyze() {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'ticketKey',
        message: 'Enter JIRA ticket key:',
        validate: (input) => input.trim().length > 0 ? true : 'Please enter a ticket key'
      },
      {
        type: 'number',
        name: 'threshold',
        message: 'Similarity threshold (0-1):',
        default: config.analysis.similarityThreshold,
        validate: (input) => input >= 0 && input <= 1 ? true : 'Please enter a value between 0 and 1'
      },
      {
        type: 'number',
        name: 'maxResults',
        message: 'Maximum results:',
        default: config.analysis.maxResults,
        validate: (input) => input > 0 ? true : 'Please enter a positive number'
      },
      {
        type: 'list',
        name: 'export',
        message: 'Export format:',
        choices: [
          { name: 'None', value: 'none' },
          { name: 'JSON', value: 'json' },
          { name: 'CSV', value: 'csv' },
          { name: 'All formats', value: 'all' }
        ]
      }
    ]);

    const options = {
      similarityThreshold: answers.threshold,
      maxResults: answers.maxResults,
      export: answers.export === 'none' ? null : answers.export
    };

    await this.analyzeTicket(answers.ticketKey, options);
  }

  /**
   * Show statistics
   */
  async showStats() {
    const spinner = ora('Loading statistics...').start();

    try {
      const stats = await this.tool.getStats();
      spinner.succeed(chalk.green('✅ Statistics loaded'));

      console.log('\n' + chalk.blue.bold('📊 Tool Statistics'));
      console.log(chalk.gray('─'.repeat(50)));

      console.log(chalk.cyan(`Version: ${stats.tool.version}`));
      console.log(chalk.cyan(`Uptime: ${Math.floor(stats.tool.uptime / 60)} minutes`));
      console.log(chalk.cyan(`Memory Usage: ${Math.round(stats.tool.memory.heapUsed / 1024 / 1024)} MB`));

      console.log('\n' + chalk.blue.bold('🗄️ Cache Statistics'));
      console.log(chalk.cyan(`Size: ${stats.cache.size}/${stats.cache.maxSize}`));
      console.log(chalk.cyan(`TTL: ${stats.cache.ttl / 1000} seconds`));
      console.log(chalk.cyan(`Enabled: ${stats.cache.enabled ? 'Yes' : 'No'}`));

      console.log('\n' + chalk.blue.bold('📁 Export Statistics'));
      console.log(chalk.cyan(`Total Files: ${stats.exports.totalFiles}`));
      console.log(chalk.cyan(`Total Size: ${Math.round(stats.exports.totalSize / 1024)} KB`));
    } catch (error) {
      spinner.fail(chalk.red('❌ Failed to load statistics'));
      console.error(chalk.red(error.message));
    }
  }

  /**
   * Manage cache
   */
  async manageCache(options) {
    if (options.stats) {
      const stats = this.tool.getCacheStats();
      console.log('\n' + chalk.blue.bold('🗄️ Cache Statistics'));
      console.log(chalk.gray('─'.repeat(30)));
      console.log(chalk.cyan(`Size: ${stats.size}/${stats.maxSize}`));
      console.log(chalk.cyan(`TTL: ${stats.ttl / 1000} seconds`));
      console.log(chalk.cyan(`Enabled: ${stats.enabled ? 'Yes' : 'No'}`));
    }

    if (options.clear) {
      this.tool.clearCache();
      console.log(chalk.green('✅ Cache cleared'));
    }
  }

  /**
   * Setup configuration
   */
  async setup() {
    console.log(chalk.blue.bold('⚙️ JIRA Similarity Tool Setup'));
    console.log(chalk.gray('─'.repeat(50)));

    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'baseUrl',
        message: 'JIRA Base URL:',
        default: config.jira.baseUrl,
        validate: (input) => input.trim().length > 0 ? true : 'Please enter JIRA base URL'
      },
      {
        type: 'input',
        name: 'email',
        message: 'JIRA Email:',
        default: config.jira.email,
        validate: (input) => input.includes('@') ? true : 'Please enter a valid email'
      },
      {
        type: 'password',
        name: 'apiToken',
        message: 'JIRA API Token:',
        validate: (input) => input.trim().length > 0 ? true : 'Please enter API token'
      },
      {
        type: 'number',
        name: 'threshold',
        message: 'Default similarity threshold (0-1):',
        default: config.analysis.similarityThreshold,
        validate: (input) => input >= 0 && input <= 1 ? true : 'Please enter a value between 0 and 1'
      },
      {
        type: 'number',
        name: 'maxResults',
        message: 'Default max results:',
        default: config.analysis.maxResults,
        validate: (input) => input > 0 ? true : 'Please enter a positive number'
      }
    ]);

    // Create .env file
    const envContent = `JIRA_BASE_URL=${answers.baseUrl}
JIRA_EMAIL=${answers.email}
JIRA_API_TOKEN=${answers.apiToken}
SIMILARITY_THRESHOLD=${answers.threshold}
MAX_RESULTS=${answers.maxResults}
LOG_LEVEL=info
`;

    try {
      const fs = require('fs').promises;
      await fs.writeFile('.env', envContent);
      console.log(chalk.green('✅ Configuration saved to .env file'));
      
      // Test connection
      console.log(chalk.blue('\n🔗 Testing connection...'));
      await this.testConnection();
    } catch (error) {
      console.error(chalk.red(`❌ Error saving configuration: ${error.message}`));
    }
  }

  /**
   * Run the CLI
   */
  run() {
    this.program.parse();
  }
}

// Run CLI if this file is executed directly
if (require.main === module) {
  const cli = new CLI();
  cli.run();
}

module.exports = CLI; 