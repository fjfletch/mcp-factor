"""FastMCP Server - Main Entry Point

This server implements the Model Context Protocol (MCP) for dynamic tool generation
and execution, providing native integration with OpenAI Responses API, Claude Desktop,
and other MCP clients.

All business logic reuses existing services (ToolConfigGenerator, HTTPClientService, etc).
This module provides only the MCP protocol layer via @mcp.tool decorators.
"""

from fastmcp import FastMCP

from .mcp_components.tools import (
    health_check,
    generate_tool_config,
    execute_http_request,
    prompt_normal,
    prompt_mcp
)
from .mcp_components.resources import (
    list_registered_tools,
    get_tool_details
)
from .mcp_components.prompts import (
    tool_generation_instructions,
    execution_guide
)

# Initialize FastMCP server
mcp = FastMCP(
    name="Dynamic Tools MCP",
    version="1.0.0",
    instructions="Dynamically generate and execute tools from API descriptions using LLM-powered configuration"
)

# Register all tools
mcp.tool(health_check, name="health_check")
mcp.tool(generate_tool_config, name="generate_tool_config")
mcp.tool(execute_http_request, name="execute_http_request")
mcp.tool(prompt_normal, name="prompt_normal")
mcp.tool(prompt_mcp, name="prompt_mcp")

# Register resources
mcp.resource("tools://registered")(list_registered_tools)
mcp.resource("tools://{tool_id}")(get_tool_details)

# Register prompts
mcp.prompt(tool_generation_instructions, name="tool_generation_instructions")
mcp.prompt(execution_guide, name="execution_guide")

# Export ASGI app for deployment
app = mcp.http_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

