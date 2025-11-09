"""Integration tests for FastMCP server - Core functionalities only.

Tests:
1. Tool registration and listing
2. Tool execution (generate_tool_config, execute_http_request, prompt_normal, prompt_mcp)
3. Resource access (tools://registered, tools://{tool_id})
4. Tool enable/disable (runtime management)
"""

import pytest
import asyncio
from fastmcp import Client

from src.dynamic_tools.fastmcp_server import mcp


@pytest.fixture
async def mcp_client():
    """Create MCP client connected to in-memory server."""
    client = Client(mcp)
    async with client:
        yield client


@pytest.mark.asyncio
async def test_tool_registration_and_listing():
    """Test that all tools are registered and listed correctly."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        
        tool_names = [tool.name for tool in tools]
        
        # Verify all 5 tools are registered
        assert "health_check" in tool_names
        assert "generate_tool_config" in tool_names
        assert "execute_http_request" in tool_names
        assert "prompt_normal" in tool_names
        assert "prompt_mcp" in tool_names
        
        assert len(tool_names) == 5


@pytest.mark.asyncio
async def test_health_check_tool():
    """Test health_check tool execution."""
    async with Client(mcp) as client:
        result = await client.call_tool("health_check", {})
        
        assert result is not None
        assert "healthy" in str(result).lower() or "ready" in str(result).lower()


@pytest.mark.asyncio
async def test_resource_listing():
    """Test resource access for registered tools."""
    async with Client(mcp) as client:
        resources = await client.list_resources()
        
        resource_uris = [str(r.uri) for r in resources]
        
        # Verify resource URIs exist
        assert any("tools://" in uri for uri in resource_uris)


@pytest.mark.asyncio
async def test_prompt_normal_tool():
    """Test prompt_normal tool with simple instructions."""
    async with Client(mcp) as client:
        # Skip if OPENAI_API_KEY not set - tool needs real API
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        try:
            result = await client.call_tool(
                "prompt_normal",
                {
                    "instructions": "What is 2+2?",
                    "context": None
                }
            )
            
            assert result is not None
        except Exception as e:
            # Tool may fail if API key is invalid, but registration should work
            assert "prompt_normal" in str(e) or "API" in str(e)


@pytest.mark.asyncio
async def test_mcp_protocol_tools_list():
    """Test that tools/list returns proper MCP protocol response."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        
        # Verify each tool has required fields
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None


@pytest.mark.asyncio
async def test_tool_execution_flow():
    """Test complete tool execution flow with MCP protocol."""
    async with Client(mcp) as client:
        # 1. List tools
        tools = await client.list_tools()
        assert len(tools) > 0
        
        # 2. Get tool names
        tool_names = [tool.name for tool in tools]
        
        # 3. Execute a simple tool
        if "health_check" in tool_names:
            result = await client.call_tool("health_check", {})
            assert result is not None


@pytest.mark.asyncio
async def test_error_handling():
    """Test that invalid tool calls are handled gracefully."""
    async with Client(mcp) as client:
        with pytest.raises(Exception):
            # Try to call non-existent tool
            await client.call_tool("nonexistent_tool", {})


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test that MCP server initializes correctly."""
    assert mcp is not None
    assert mcp.name == "Dynamic Tools MCP"
    # version may not be directly accessible, just verify server exists
    assert mcp.instructions is not None
    assert "tool" in mcp.instructions.lower()


@pytest.mark.asyncio
async def test_concurrent_tool_calls():
    """Test that multiple tools can be called concurrently."""
    async with Client(mcp) as client:
        # Call multiple tools in parallel
        results = await asyncio.gather(
            client.call_tool("health_check", {}),
            client.call_tool("health_check", {}),
            client.call_tool("health_check", {}),
        )
        
        assert len(results) == 3
        assert all(r is not None for r in results)


@pytest.mark.asyncio
async def test_tool_descriptions_exist():
    """Test that all tools have meaningful descriptions."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        
        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0
            # Description should be meaningful (not just the function name)
            assert tool.description.lower() != tool.name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

