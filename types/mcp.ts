export interface MCPIntegration {
  id: string;
  name: string;
  description: string;
  version: string;
  format: string;
  author: string;
  createdAt: string;
  updatedAt: string;
  published: boolean;
  apis: APIConfig[];
  tools: MCPTool[];
  prompts: MCPPrompt[];
  resources: MCPResource[];
  configuration: MCPConfiguration;
  stars?: number;
  reviews?: number;
  uses?: number;
  emoji?: string;
}

export interface APIConfig {
  id: string;
  name: string;
  baseUrl: string;
  authentication: {
    type: 'none' | 'api-key' | 'bearer' | 'oauth2' | 'basic' | 'custom';
    config?: Record<string, any>;
  };
  routes: APIRoute[];
  headers?: Record<string, string>;
  timeout?: number;
  status?: 'connected' | 'error' | 'no-key';
}

export interface APIRoute {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
}

export interface MCPTool {
  id: string;
  name: string;
  displayName: string;
  description: string;
  apiId: string;
  method: string;
  endpoint: string;
  inputSchema: Record<string, any>;
  responseMapping?: {
    successPath?: string;
    errorHandling?: string;
  };
}

export interface MCPPrompt {
  id: string;
  type: 'system' | 'contextual';
  content: string;
}

export interface MCPResource {
  id: string;
  name: string;
  type: string;
  uri: string;
}

export interface MCPConfiguration {
  globalPrompt: string;
  model: string;
  temperature: number;
  maxTokens: number;
}

export interface FlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    type?: string;
    details?: any;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}

export interface TestResult {
  success: boolean;
  response?: string;
  executionFlow?: ExecutionStep[];
  tokenUsage?: {
    prompt: number;
    completion: number;
    total: number;
  };
  cost?: number;
  error?: string;
}

export interface ExecutionStep {
  step: number;
  action: string;
  details: string;
}