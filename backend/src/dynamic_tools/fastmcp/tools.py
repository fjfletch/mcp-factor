"""MCP Tool Implementations

Reuses existing services without modification:
- ToolConfigGenerator for generate_tool_config
- HTTPClientService for execute_http_request
- PromptService for prompt_normal and prompt_mcp
"""

from fastmcp import Context
from loguru import logger

from ..services.tool_generator import ToolConfigGenerator
from ..services.http_client import HTTPClientService
from ..services.prompt_service import PromptService
from ..models.http_spec import HTTPRequestSpec
from ..models.api_requests import PromptRequest, MCPPromptRequest
from ..config.settings import get_settings


async def health_check() -> str:
    """Health check tool - verify FastMCP server is running."""
    return "✅ FastMCP server is healthy and ready!"


async def generate_tool_config(
    tool_name: str,
    tool_description: str,
    api_docs: str,
    input_schema_description: str | None = None,
    output_schema_description: str | None = None,
    ctx: Context | None = None
) -> dict:
    """Auto-generate a tool configuration from natural language API description."""
    try:
        if ctx:
            await ctx.info(f"📝 Generating config for: {tool_name}")
        
        settings = get_settings()
        generator = ToolConfigGenerator(
            api_key=settings.openai_api_key,
            max_retries=settings.llm_max_retries
        )
        
        config = await generator.generate_tool_config(
            tool_name=tool_name,
            tool_description=tool_description,
            api_docs=api_docs,
            input_schema_description=input_schema_description,
            output_schema_description=output_schema_description
        )
        
        if ctx:
            await ctx.info(f"✅ Generated config: {tool_name}")
        
        return config
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Failed: {e}")
        logger.error(f"generate_tool_config failed: {e}")
        raise


async def execute_http_request(
    method: str,
    url: str,
    headers: dict | None = None,
    body: dict | None = None,
    ctx: Context | None = None
) -> dict:
    """Execute an HTTP request and return the response."""
    try:
        if ctx:
            await ctx.info(f"🔗 Executing {method} {url}")
        
        http_client = HTTPClientService()
        spec = HTTPRequestSpec(
            method=method,
            url=url,
            headers=headers or {},
            body=body
        )
        
        response = await http_client.execute(spec)
        
        if ctx:
            await ctx.info(f"✅ Response: {response.status_code}")
        
        return response.model_dump()
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Failed: {e}")
        logger.error(f"execute_http_request failed: {e}")
        raise


async def prompt_normal(
    instructions: str,
    context: str | None = None,
    ctx: Context | None = None
) -> dict:
    """Send a prompt to LLM and get text response."""
    try:
        if ctx:
            await ctx.info(f"💬 Processing prompt")
        
        settings = get_settings()
        prompt_service = PromptService(
            api_key=settings.openai_api_key,
            max_retries=settings.llm_max_retries
        )
        
        request = PromptRequest(instructions=instructions, context=context)
        response = await prompt_service.prompt_normal(request)
        
        if ctx:
            await ctx.info(f"✅ Prompt processed")
        
        return response.model_dump()
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Failed: {e}")
        logger.error(f"prompt_normal failed: {e}")
        raise


async def prompt_mcp(
    instructions: str,
    api_docs: str,
    response_format_prompt: str | None = None,
    ctx: Context | None = None
) -> dict:
    """Send MCP prompt to LLM with API documentation."""
    try:
        if ctx:
            await ctx.info(f"💬 Processing MCP prompt")
        
        settings = get_settings()
        prompt_service = PromptService(
            api_key=settings.openai_api_key,
            max_retries=settings.llm_max_retries
        )
        
        request = MCPPromptRequest(
            instructions=instructions,
            api_docs=api_docs,
            response_format_prompt=response_format_prompt
        )
        response = await prompt_service.prompt_mcp(request)
        
        if ctx:
            await ctx.info(f"✅ MCP prompt processed")
        
        return response.model_dump()
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Failed: {e}")
        logger.error(f"prompt_mcp failed: {e}")
        raise
