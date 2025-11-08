import axios from 'axios';
import { MCPIntegration, TestResult } from '@/types/mcp';

// Mock data for development
const mockMCPs: MCPIntegration[] = [
  {
    id: '1',
    name: 'Stripe Payment Gateway',
    emoji: '💳',
    description: 'Process payments, manage subscriptions, and handle refunds',
    version: '1.0.0',
    format: 'mcp',
    author: '@johndoe',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-20',
    published: true,
    stars: 4.8,
    reviews: 124,
    uses: 2300,
    apis: [],
    tools: [],
    prompts: [],
    resources: [],
    configuration: {
      globalPrompt: 'You are a payment processing assistant.',
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 1000,
    },
  },
  {
    id: '2',
    name: 'Weather API',
    emoji: '🌤️',
    description: 'Get real-time weather data and forecasts for any location',
    version: '1.2.0',
    format: 'mcp',
    author: '@weatherdev',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-18',
    published: true,
    stars: 4.6,
    reviews: 89,
    uses: 1800,
    apis: [],
    tools: [],
    prompts: [],
    resources: [],
    configuration: {
      globalPrompt: 'You are a weather information assistant.',
      model: 'gpt-4',
      temperature: 0.5,
      maxTokens: 800,
    },
  },
  {
    id: '3',
    name: 'GitHub Integration',
    emoji: '🐙',
    description: 'Manage repositories, issues, and pull requests',
    version: '2.0.0',
    format: 'mcp',
    author: '@devtools',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-22',
    published: true,
    stars: 4.9,
    reviews: 156,
    uses: 3200,
    apis: [],
    tools: [],
    prompts: [],
    resources: [],
    configuration: {
      globalPrompt: 'You are a GitHub assistant.',
      model: 'gpt-4-turbo',
      temperature: 0.6,
      maxTokens: 1200,
    },
  },
];

export const apiClient = {
  // MCP Management
  getMCPs: async (): Promise<MCPIntegration[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500));
    return mockMCPs;
  },

  getMCP: async (id: string): Promise<MCPIntegration | null> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockMCPs.find((mcp) => mcp.id === id) || null;
  },

  createMCP: async (data: Partial<MCPIntegration>): Promise<MCPIntegration> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const newMCP: MCPIntegration = {
      id: Date.now().toString(),
      name: data.name || 'New MCP',
      description: data.description || '',
      version: '1.0.0',
      format: 'mcp',
      author: '@currentuser',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      published: false,
      apis: [],
      tools: [],
      prompts: [],
      resources: [],
      configuration: {
        globalPrompt: '',
        model: 'gpt-4',
        temperature: 0.7,
        maxTokens: 1000,
      },
      ...data,
    };
    mockMCPs.push(newMCP);
    return newMCP;
  },

  updateMCP: async (id: string, data: Partial<MCPIntegration>): Promise<MCPIntegration> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const index = mockMCPs.findIndex((mcp) => mcp.id === id);
    if (index !== -1) {
      mockMCPs[index] = { ...mockMCPs[index], ...data, updatedAt: new Date().toISOString() };
      return mockMCPs[index];
    }
    throw new Error('MCP not found');
  },

  deleteMCP: async (id: string): Promise<void> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const index = mockMCPs.findIndex((mcp) => mcp.id === id);
    if (index !== -1) {
      mockMCPs.splice(index, 1);
    }
  },

  publishMCP: async (id: string): Promise<MCPIntegration> => {
    return apiClient.updateMCP(id, { published: true });
  },

  forkMCP: async (id: string): Promise<MCPIntegration> => {
    const original = await apiClient.getMCP(id);
    if (!original) throw new Error('MCP not found');
    
    return apiClient.createMCP({
      ...original,
      id: Date.now().toString(),
      name: `${original.name} (Fork)`,
      published: false,
      author: '@currentuser',
    });
  },

  // Testing
  executeMCP: async (id: string, query: string): Promise<TestResult> => {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    // Mock response
    return {
      success: true,
      response: 'This is a mock response from the MCP execution. The actual implementation would call the LLM and execute the tools.',
      executionFlow: [
        { step: 1, action: 'Received Query', details: query },
        { step: 2, action: 'LLM Decision', details: 'Analyzing query and selecting appropriate tools' },
        { step: 3, action: 'Tool Execution', details: 'Calling API endpoint' },
        { step: 4, action: 'Response Generation', details: 'Formatting response for user' },
      ],
      tokenUsage: {
        prompt: 150,
        completion: 75,
        total: 225,
      },
      cost: 0.0045,
    };
  },

  // Usage stats
  getUsageStats: async () => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return {
      apiCalls: { current: 2450, limit: 10000 },
      tokenUsage: { current: 450000, limit: 2000000 },
      cost: { current: 12.45, limit: 100 },
    };
  },
};