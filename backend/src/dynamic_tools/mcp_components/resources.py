"""MCP Resource Definitions

Provides read-only access to tool metadata and configurations.
"""

import json
from loguru import logger

from ..core.registry import ToolRegistry


async def list_registered_tools() -> str:
    """List all currently registered tools with metadata."""
    try:
        registry = ToolRegistry()
        tools = registry.list_definitions()
        
        tool_list = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema
            }
            for tool in tools
        ]
        
        return json.dumps({
            "count": len(tool_list),
            "tools": tool_list
        }, indent=2)
        
    except Exception as e:
        logger.error(f"list_registered_tools failed: {e}")
        raise


async def get_tool_details(tool_id: str) -> str:
    """Get detailed configuration for a specific tool."""
    try:
        registry = ToolRegistry()
        
        if not registry.has_tool(tool_id):
            raise ValueError(f"Tool not found: {tool_id}")
        
        tool_def = registry.get_definition(tool_id)
        
        return json.dumps({
            "name": tool_def.name,
            "description": tool_def.description,
            "input_schema": tool_def.input_schema,
            "output_schema": tool_def.output_schema
        }, indent=2)
        
    except Exception as e:
        logger.error(f"get_tool_details failed: {e}")
        raise
