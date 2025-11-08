import { create } from 'zustand';
import { MCPIntegration, APIConfig, MCPTool, MCPPrompt, FlowNode } from '@/types/mcp';

interface MCPStore {
  currentMCP: MCPIntegration | null;
  selectedNode: FlowNode | null;
  
  setCurrentMCP: (mcp: MCPIntegration | null) => void;
  updateMCP: (updates: Partial<MCPIntegration>) => void;
  
  addAPI: (api: APIConfig) => void;
  updateAPI: (id: string, updates: Partial<APIConfig>) => void;
  deleteAPI: (id: string) => void;
  
  addTool: (tool: MCPTool) => void;
  updateTool: (id: string, updates: Partial<MCPTool>) => void;
  deleteTool: (id: string) => void;
  
  addPrompt: (prompt: MCPPrompt) => void;
  updatePrompt: (id: string, updates: Partial<MCPPrompt>) => void;
  deletePrompt: (id: string) => void;
  
  selectNode: (node: FlowNode | null) => void;
}

export const useMCPStore = create<MCPStore>((set) => ({
  currentMCP: null,
  selectedNode: null,
  
  setCurrentMCP: (mcp) => set({ currentMCP: mcp, selectedNode: null }),
  
  updateMCP: (updates) => set((state) => ({
    currentMCP: state.currentMCP ? { ...state.currentMCP, ...updates } : null,
  })),
  
  addAPI: (api) => set((state) => ({
    currentMCP: state.currentMCP
      ? { ...state.currentMCP, apis: [...state.currentMCP.apis, api] }
      : null,
  })),
  
  updateAPI: (id, updates) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          apis: state.currentMCP.apis.map((api) =>
            api.id === id ? { ...api, ...updates } : api
          ),
        }
      : null,
  })),
  
  deleteAPI: (id) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          apis: state.currentMCP.apis.filter((api) => api.id !== id),
        }
      : null,
  })),
  
  addTool: (tool) => set((state) => ({
    currentMCP: state.currentMCP
      ? { ...state.currentMCP, tools: [...state.currentMCP.tools, tool] }
      : null,
  })),
  
  updateTool: (id, updates) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          tools: state.currentMCP.tools.map((tool) =>
            tool.id === id ? { ...tool, ...updates } : tool
          ),
        }
      : null,
  })),
  
  deleteTool: (id) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          tools: state.currentMCP.tools.filter((tool) => tool.id !== id),
        }
      : null,
  })),
  
  addPrompt: (prompt) => set((state) => ({
    currentMCP: state.currentMCP
      ? { ...state.currentMCP, prompts: [...state.currentMCP.prompts, prompt] }
      : null,
  })),
  
  updatePrompt: (id, updates) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          prompts: state.currentMCP.prompts.map((prompt) =>
            prompt.id === id ? { ...prompt, ...updates } : prompt
          ),
        }
      : null,
  })),
  
  deletePrompt: (id) => set((state) => ({
    currentMCP: state.currentMCP
      ? {
          ...state.currentMCP,
          prompts: state.currentMCP.prompts.filter((prompt) => prompt.id !== id),
        }
      : null,
  })),
  
  selectNode: (node) => set({ selectedNode: node }),
}));