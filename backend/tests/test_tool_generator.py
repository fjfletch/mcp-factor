"""Tests for ToolConfigGenerator."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from dynamic_tools.models.tool_config import ToolConfig
from dynamic_tools.models.api_requests import PromptResponse, MCPPromptRequest


@pytest.fixture
def mock_openai_client():
    """Mock AsyncOpenAI client."""
    return AsyncMock()


@pytest.fixture
def sample_http_spec():
    """Sample HTTPRequestSpec response."""
    return {
        "method": "GET",
        "url": "https://api.openweathermap.org/data/2.5/weather",
        "headers": {"Accept": "application/json"},
        "query_params": {"q": "city", "appid": "key"}
    }


@pytest.fixture
def sample_input_schema():
    """Sample input JSON Schema."""
    return {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name"
            }
        },
        "required": ["city"]
    }


@pytest.fixture
def sample_output_schema():
    """Sample output JSON Schema."""
    return {
        "type": "object",
        "properties": {
            "temperature": {
                "type": "number",
                "description": "Temperature in Celsius"
            },
            "humidity": {
                "type": "integer",
                "description": "Humidity percentage"
            }
        },
        "required": ["temperature"]
    }


@pytest.mark.asyncio
async def test_tool_config_generator_initialization():
    """Test ToolConfigGenerator can be initialized.
    
    Given: Valid OpenAI API key
    When: Creating ToolConfigGenerator instance
    Then: Should initialize successfully
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service:
        generator = ToolConfigGenerator(api_key="test-key")
        
        assert generator is not None
        assert generator.prompt_service is not None
        assert generator.max_retries == 3


@pytest.mark.asyncio
async def test_generate_tool_config_success(sample_http_spec, sample_input_schema, sample_output_schema):
    """Test successful tool config generation.
    
    Given: Valid tool metadata and API documentation
    When: Calling generate_tool_config()
    Then: Should return complete ToolConfig dictionary
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        
        # Mock MCP prompt response (HTTPRequestSpec)
        mcp_response = PromptResponse(
            content=sample_http_spec,
            type="http_spec"
        )
        mock_service.prompt_mcp = AsyncMock(return_value=mcp_response)
        
        # Mock normal prompts for schema generation
        input_schema_response = PromptResponse(
            content=json.dumps(sample_input_schema),
            type="text"
        )
        output_schema_response = PromptResponse(
            content=json.dumps(sample_output_schema),
            type="text"
        )
        
        # Set up prompt_normal to return different schemas
        mock_service.prompt_normal = AsyncMock(
            side_effect=[input_schema_response, output_schema_response]
        )
        
        generator = ToolConfigGenerator(api_key="test-key")
        
        result = await generator.generate_tool_config(
            tool_name="get_weather",
            tool_description="Get weather information for a city",
            api_docs="GET https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}"
        )
        
        # Verify result is a dictionary (serialized ToolConfig)
        assert isinstance(result, dict)
        assert result["name"] == "get_weather"
        assert result["description"] == "Get weather information for a city"
        assert result["version"] == 1
        assert result["enabled"] is True
        
        # Verify API config
        assert "api" in result
        assert result["api"]["method"] == "GET"
        assert "openweathermap" in result["api"]["base_url"].lower()
        
        # Verify schemas exist
        assert "input_schema" in result
        assert "output_schema" in result
        assert "mapping" in result


@pytest.mark.asyncio
async def test_generate_tool_config_with_schema_descriptions(
    sample_http_spec,
    sample_input_schema,
    sample_output_schema
):
    """Test tool config generation with schema descriptions.
    
    Given: Tool metadata with optional schema descriptions
    When: Calling generate_tool_config()
    Then: Should pass descriptions to schema generation
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        
        # Mock responses
        mcp_response = PromptResponse(
            content=sample_http_spec,
            type="http_spec"
        )
        mock_service.prompt_mcp = AsyncMock(return_value=mcp_response)
        
        input_response = PromptResponse(
            content=json.dumps(sample_input_schema),
            type="text"
        )
        output_response = PromptResponse(
            content=json.dumps(sample_output_schema),
            type="text"
        )
        
        mock_service.prompt_normal = AsyncMock(
            side_effect=[input_response, output_response]
        )
        
        generator = ToolConfigGenerator(api_key="test-key")
        
        result = await generator.generate_tool_config(
            tool_name="test_tool",
            tool_description="Test tool description",
            api_docs="Test API docs",
            input_schema_description="city as string",
            output_schema_description="temperature and humidity"
        )
        
        assert isinstance(result, dict)
        assert result["name"] == "test_tool"
        
        # Verify prompt_normal was called twice (for input and output schemas)
        assert mock_service.prompt_normal.call_count == 2


@pytest.mark.asyncio
async def test_split_url():
    """Test URL splitting into base_url and path.
    
    Given: Various URL formats
    When: Calling _split_url()
    Then: Should correctly split into components
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    generator = ToolConfigGenerator(api_key="test-key")
    
    # Test with full URL
    base, path = generator._split_url("https://api.example.com/v1/weather")
    assert base == "https://api.example.com"
    assert path == "/v1/weather"
    
    # Test with base URL only
    base, path = generator._split_url("https://api.example.com")
    assert base == "https://api.example.com"
    assert path == ""
    
    # Test with single path segment
    base, path = generator._split_url("https://api.example.com/data")
    assert base == "https://api.example.com"
    assert path == "/data"


@pytest.mark.asyncio
async def test_extract_api_config(sample_http_spec):
    """Test extraction of ApiConfig from HTTPRequestSpec.
    
    Given: HTTPRequestSpec dictionary
    When: Calling _extract_api_config()
    Then: Should return valid ApiConfig
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    from dynamic_tools.models.tool_config import ApiConfig
    
    generator = ToolConfigGenerator(api_key="test-key")
    
    api_config = generator._extract_api_config(sample_http_spec)
    
    assert isinstance(api_config, ApiConfig)
    assert api_config.method.value == "GET"
    assert "openweathermap" in api_config.base_url.lower()
    assert api_config.timeout == 30.0


@pytest.mark.asyncio
async def test_generate_tool_config_with_invalid_api_docs(sample_input_schema, sample_output_schema):
    """Test tool config generation handles invalid API docs gracefully.
    
    Given: Invalid or minimal API documentation
    When: Calling generate_tool_config()
    Then: Should still generate a valid config with defaults
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        
        # Mock minimal HTTPRequestSpec
        mcp_response = PromptResponse(
            content={
                "method": "GET",
                "url": "https://example.com",
                "headers": {},
                "query_params": {}
            },
            type="http_spec"
        )
        mock_service.prompt_mcp = AsyncMock(return_value=mcp_response)
        
        input_response = PromptResponse(
            content=json.dumps(sample_input_schema),
            type="text"
        )
        output_response = PromptResponse(
            content=json.dumps(sample_output_schema),
            type="text"
        )
        
        mock_service.prompt_normal = AsyncMock(
            side_effect=[input_response, output_response]
        )
        
        generator = ToolConfigGenerator(api_key="test-key")
        
        result = await generator.generate_tool_config(
            tool_name="minimal_tool",
            tool_description="Tool with minimal API docs",
            api_docs="Just a URL"
        )
        
        assert isinstance(result, dict)
        assert result["name"] == "minimal_tool"
        assert result["enabled"] is True


@pytest.mark.asyncio
async def test_generate_input_schema_default_on_error():
    """Test input schema generation returns default on LLM error.
    
    Given: PromptService that raises an exception
    When: Calling _generate_input_schema()
    Then: Should return default empty schema
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        
        # Mock exception on prompt_normal
        mock_service.prompt_normal = AsyncMock(
            side_effect=Exception("LLM error")
        )
        
        generator = ToolConfigGenerator(api_key="test-key")
        
        result = await generator._generate_input_schema(
            tool_description="Test",
            api_docs="Test docs"
        )
        
        # Should return default schema
        assert isinstance(result, dict)
        assert result["type"] == "object"
        assert "properties" in result


@pytest.mark.asyncio
async def test_generate_output_schema_default_on_error():
    """Test output schema generation returns default on LLM error.
    
    Given: PromptService that raises an exception
    When: Calling _generate_output_schema()
    Then: Should return default empty schema
    """
    from dynamic_tools.services.tool_generator import ToolConfigGenerator
    
    with patch('dynamic_tools.services.tool_generator.PromptService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        
        # Mock exception on prompt_normal
        mock_service.prompt_normal = AsyncMock(
            side_effect=Exception("LLM error")
        )
        
        generator = ToolConfigGenerator(api_key="test-key")
        
        result = await generator._generate_output_schema(
            tool_description="Test",
            api_docs="Test docs"
        )
        
        # Should return default schema
        assert isinstance(result, dict)
        assert result["type"] == "object"
        assert "properties" in result


