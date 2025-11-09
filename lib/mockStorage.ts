import { MCPIntegration } from '@/types/mcp';

const MCP_STORAGE_PREFIX = 'mcp_';
const MCP_LIST_KEY = 'mcp_list';

export function saveMCPToStorage(mcp: MCPIntegration): void {
  if (typeof window === 'undefined') return;
  
  try {
    const key = `${MCP_STORAGE_PREFIX}${mcp.id}`;
    localStorage.setItem(key, JSON.stringify(mcp));
    
    // Update the list of MCP IDs
    const list = getMCPList();
    if (!list.includes(mcp.id)) {
      list.push(mcp.id);
      localStorage.setItem(MCP_LIST_KEY, JSON.stringify(list));
    }
  } catch (error) {
    console.error('Error saving MCP to storage:', error);
  }
}

export function loadMCPFromStorage(id: string): MCPIntegration | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const key = `${MCP_STORAGE_PREFIX}${id}`;
    const data = localStorage.getItem(key);
    if (!data) return null;
    return JSON.parse(data) as MCPIntegration;
  } catch (error) {
    console.error('Error loading MCP from storage:', error);
    return null;
  }
}

export function getAllMCPs(): MCPIntegration[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const list = getMCPList();
    return list
      .map((id) => loadMCPFromStorage(id))
      .filter((mcp): mcp is MCPIntegration => mcp !== null);
  } catch (error) {
    console.error('Error getting all MCPs:', error);
    return [];
  }
}

export function deleteMCPFromStorage(id: string): void {
  if (typeof window === 'undefined') return;
  
  try {
    const key = `${MCP_STORAGE_PREFIX}${id}`;
    localStorage.removeItem(key);
    
    // Update the list
    const list = getMCPList();
    const filtered = list.filter((mcpId) => mcpId !== id);
    localStorage.setItem(MCP_LIST_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error deleting MCP from storage:', error);
  }
}

export function createNewMCP(): MCPIntegration {
  return {
    id: Date.now().toString(),
    name: 'Untitled MCP',
    description: '',
    version: '1.0.0',
    format: 'gpt-4',
    author: 'Anonymous',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    published: false,
    apis: [],
    tools: [],
    prompts: [],
    resources: [],
    configuration: {
      globalPrompt: 'You are a helpful AI assistant.',
      model: 'gpt-3.5-turbo',
      temperature: 0.7,
      maxTokens: 2000,
    },
  };
}

function getMCPList(): string[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const data = localStorage.getItem(MCP_LIST_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting MCP list:', error);
    return [];
  }
}
