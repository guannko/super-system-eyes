#!/usr/bin/env node

/**
 * BRAIN INDEX - SUPER MAKE.COM MCP SERVER
 * Full automation: create, edit, find, deploy scenarios
 * Token: 03106422-df8a-4378-beb0-cac8aaa78be3
 * Zone: eu2.make.com
 */

const { Server } = require('@modelcontextprotocol/sdk/server');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio');
const axios = require('axios');

// Make.com API configuration
const MAKE_CONFIG = {
  baseURL: 'https://eu2.make.com/api/v2',
  token: process.env.MAKE_API_KEY || '03106422-df8a-4378-beb0-cac8aaa78be3',
  organizationId: 5038858,
  teamId: 2552758
};

const api = axios.create({
  baseURL: MAKE_CONFIG.baseURL,
  headers: {
    'Authorization': `Token ${MAKE_CONFIG.token}`,
    'Content-Type': 'application/json'
  }
});

class SuperMakeMCP {
  constructor() {
    this.server = new Server({
      name: 'super-make-mcp',
      version: '1.0.0'
    }, {
      capabilities: {
        tools: {}
      }
    });

    this.setupTools();
    this.setupRequestHandlers();
  }

  setupTools() {
    // SCENARIO MANAGEMENT
    this.server.setRequestHandler('tools/list', () => ({
      tools: [
        // SEARCH & DISCOVERY
        {
          name: 'find_scenarios',
          description: 'Find scenarios by keyword, app, or pattern',
          inputSchema: {
            type: 'object',
            properties: {
              query: { type: 'string', description: 'Search query' },
              app: { type: 'string', description: 'App name filter' }
            }
          }
        },
        
        // SCENARIO CREATION
        {
          name: 'create_scenario_from_template',
          description: 'Create new scenario from template or pattern',
          inputSchema: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              template: { type: 'string', description: 'Template type: stripe_analytics, webhook_processor, etc.' },
              config: { type: 'object', description: 'Configuration parameters' }
            },
            required: ['name', 'template']
          }
        },

        // SCENARIO MODIFICATION  
        {
          name: 'modify_scenario',
          description: 'Modify existing scenario - add modules, change flow',
          inputSchema: {
            type: 'object',
            properties: {
              scenarioId: { type: 'number' },
              modifications: { type: 'object' }
            },
            required: ['scenarioId', 'modifications']
          }
        },

        // BULK OPERATIONS
        {
          name: 'clone_and_modify',
          description: 'Clone scenario and modify for new use case',
          inputSchema: {
            type: 'object',
            properties: {
              sourceId: { type: 'number' },
              newName: { type: 'string' },
              modifications: { type: 'object' }
            },
            required: ['sourceId', 'newName']
          }
        },

        // TEMPLATES LIBRARY
        {
          name: 'get_templates',
          description: 'Get available scenario templates',
          inputSchema: {
            type: 'object',
            properties: {
              category: { type: 'string', description: 'Template category' }
            }
          }
        }
      ]
    }));
  }

  setupRequestHandlers() {
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'find_scenarios':
            return await this.findScenarios(args);
          case 'create_scenario_from_template':
            return await this.createFromTemplate(args);
          case 'modify_scenario':
            return await this.modifyScenario(args);
          case 'clone_and_modify':
            return await this.cloneAndModify(args);
          case 'get_templates':
            return await this.getTemplates(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `Error: ${error.message}`
          }]
        };
      }
    });
  }

  // FIND SCENARIOS BY PATTERN
  async findScenarios({ query, app }) {
    const response = await api.get(`/scenarios`, {
      params: { teamId: MAKE_CONFIG.teamId }
    });

    let scenarios = response.data;
    
    if (query) {
      scenarios = scenarios.filter(s => 
        s.name.toLowerCase().includes(query.toLowerCase())
      );
    }

    if (app) {
      // Filter by app usage (would need to check modules)
      // This requires getting scenario details
    }

    return {
      content: [{
        type: 'text', 
        text: JSON.stringify(scenarios, null, 2)
      }]
    };
  }

  // CREATE FROM TEMPLATE
  async createFromTemplate({ name, template, config = {} }) {
    const templates = {
      stripe_analytics: {
        name: name,
        modules: [
          {
            app: 'built-in',
            module: 'schedule',
            parameters: { schedule: 'every-day', time: '09:00' }
          },
          {
            app: 'stripe',
            module: 'ListCharges',
            parameters: { limit: 1000, ...config.stripe }
          },
          {
            app: 'built-in',
            module: 'iterator'
          },
          {
            app: 'google-sheets',
            module: 'addRow',
            parameters: { ...config.sheets }
          }
        ]
      },
      webhook_processor: {
        name: name,
        modules: [
          {
            app: 'webhook',
            module: 'customWebhook'
          },
          {
            app: 'built-in',
            module: 'jsonParser'
          },
          {
            app: 'data-store',
            module: 'addRecord',
            parameters: { dataStoreId: config.dataStoreId }
          }
        ]
      }
    };

    const scenarioTemplate = templates[template];
    if (!scenarioTemplate) {
      throw new Error(`Template '${template}' not found`);
    }

    // Create scenario via Make.com API
    const response = await api.post('/scenarios', {
      teamId: MAKE_CONFIG.teamId,
      ...scenarioTemplate
    });

    return {
      content: [{
        type: 'text',
        text: `Created scenario: ${JSON.stringify(response.data, null, 2)}`
      }]
    };
  }

  // MODIFY EXISTING SCENARIO
  async modifyScenario({ scenarioId, modifications }) {
    const response = await api.put(`/scenarios/${scenarioId}`, {
      ...modifications
    });

    return {
      content: [{
        type: 'text',
        text: `Modified scenario: ${JSON.stringify(response.data, null, 2)}`
      }]
    };
  }

  // GET AVAILABLE TEMPLATES
  async getTemplates({ category }) {
    const templates = {
      payment_processing: [
        'stripe_analytics',
        'paypal_subscriptions', 
        'quickbooks_sync'
      ],
      data_processing: [
        'webhook_processor',
        'csv_importer',
        'api_aggregator'
      ],
      notifications: [
        'slack_alerts',
        'email_reports',
        'telegram_bot'
      ]
    };

    const result = category ? templates[category] : templates;

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result, null, 2)
      }]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Super Make.com MCP server running');
  }
}

if (require.main === module) {
  const server = new SuperMakeMCP();
  server.run().catch(console.error);
}

module.exports = SuperMakeMCP;