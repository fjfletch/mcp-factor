"""API request and response models."""

from typing import Any, Optional, Literal, Union
from pydantic import BaseModel, Field
from .http_spec import HTTPRequestSpec, HTTPResponseSpec


class PromptRequest(BaseModel):
    """Model for normal prompt requests.
    
    This model represents a request for standard LLM prompting
    without API integration.
    
    Attributes:
        instructions: The main instruction or question for the LLM
        context: Optional contextual information for the LLM
        response_format_prompt: Optional instruction for response formatting
    """
    
    instructions: str = Field(
        ...,
        description="Main instruction or question for the LLM",
        min_length=1
    )
    context: Optional[str] = Field(
        default=None,
        description="Contextual information to help the LLM"
    )
    response_format_prompt: Optional[str] = Field(
        default=None,
        description="Instructions for how to format the response"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "instructions": "Explain what REST APIs are",
                    "context": "The user is a beginner developer",
                    "response_format_prompt": "Keep it simple and concise"
                }
            ]
        }
    }


class PromptResponse(BaseModel):
    """Model for prompt responses.
    
    This model represents the response from an LLM prompt,
    which can be either text or an HTTP specification.
    
    Attributes:
        content: The response content (text string or dict for http_spec)
        type: The type of response ('text' or 'http_spec')
    """
    
    content: Any = Field(
        ...,
        description="Response content (text or HTTP specification)"
    )
    type: Literal["text", "http_spec"] = Field(
        ...,
        description="Type of response content"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "REST APIs are interfaces that allow...",
                    "type": "text"
                },
                {
                    "content": {
                        "method": "GET",
                        "url": "https://api.example.com/data",
                        "headers": {}
                    },
                    "type": "http_spec"
                }
            ]
        }
    }


class MCPPromptRequest(BaseModel):
    """Model for MCP (Model Context Protocol) prompt requests.
    
    This model represents a request for LLM prompting with API context,
    intended to generate HTTP request specifications.
    
    Attributes:
        instructions: The main instruction for what API call to make
        api_docs: API documentation or context for the LLM
        response_format_prompt: Optional instruction for response formatting
    """
    
    instructions: str = Field(
        ...,
        description="Instruction for what API call to generate",
        min_length=1
    )
    api_docs: str = Field(
        ...,
        description="API documentation or context",
        min_length=1
    )
    response_format_prompt: Optional[str] = Field(
        default=None,
        description="Instructions for response formatting"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "instructions": "Get the current weather for New York City",
                    "api_docs": "OpenWeatherMap API: GET https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}",
                    "response_format_prompt": "Return as HTTP request specification"
                }
            ]
        }
    }


class ExecuteRequest(BaseModel):
    """Model for HTTP request execution.
    
    This model represents a request to execute an HTTP call
    based on an HTTPRequestSpec.
    
    Attributes:
        http_spec: The HTTP request specification to execute
    """
    
    http_spec: HTTPRequestSpec = Field(
        ...,
        description="HTTP request specification to execute"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "http_spec": {
                        "method": "GET",
                        "url": "https://api.example.com/data",
                        "headers": {"Authorization": "Bearer token"}
                    }
                }
            ]
        }
    }


class ExecuteResponse(BaseModel):
    """Model for HTTP request execution response.
    
    This model represents the result of executing an HTTP request,
    which can be either successful (with data) or failed (with error).
    
    Attributes:
        status: Execution status ('success' or 'error')
        data: Optional HTTP response data (present on success)
        error: Optional error message (present on error)
    """
    
    status: Literal["success", "error"] = Field(
        ...,
        description="Execution status"
    )
    data: Optional[HTTPResponseSpec] = Field(
        default=None,
        description="HTTP response data (present on success)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (present on error)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "data": {
                        "status_code": 200,
                        "body": {"result": "data"},
                        "execution_time_ms": 245.6
                    }
                },
                {
                    "status": "error",
                    "error": "Connection timeout after 30 seconds"
                }
            ]
        }
    }


class GenerateToolConfigRequest(BaseModel):
    """Model for tool config generation requests.
    
    This model represents a request to automatically generate a ToolConfig
    from a natural language description and API documentation.
    
    Attributes:
        tool_name: Unique name for the tool
        tool_description: Human-readable description of what the tool does
        api_docs: API documentation or endpoint information
        input_schema_description: Optional description of expected input fields
        output_schema_description: Optional description of expected output fields
    """
    
    tool_name: str = Field(
        ...,
        description="Unique name for the tool (e.g., get_stock_price)",
        min_length=1,
        max_length=100
    )
    tool_description: str = Field(
        ...,
        description="What the tool does and how to use it",
        min_length=10,
        max_length=500
    )
    api_docs: str = Field(
        ...,
        description="API documentation, endpoint, or technical specification",
        min_length=10
    )
    input_schema_description: Optional[str] = Field(
        default=None,
        description="Optional guidance for input schema generation (e.g., 'symbol as string, time_period as integer')",
        max_length=500
    )
    output_schema_description: Optional[str] = Field(
        default=None,
        description="Optional guidance for output schema generation (e.g., 'price as number, currency as string')",
        max_length=500
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tool_name": "get_weather",
                    "tool_description": "Get current weather information for a city",
                    "api_docs": "GET https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}",
                    "input_schema_description": "city as string parameter",
                    "output_schema_description": "temperature, humidity, conditions as strings"
                }
            ]
        }
    }


class GenerateToolConfigResponse(BaseModel):
    """Model for tool config generation response.
    
    This model represents the response from the tool config generation endpoint,
    containing the generated ToolConfig or an error message.
    
    Attributes:
        status: Generation status ('success' or 'error')
        tool_config: The generated ToolConfig as a dictionary (present on success)
        error: Error message if generation failed (present on error)
    """
    
    status: Literal["success", "error"] = Field(
        ...,
        description="Whether config generation succeeded or failed"
    )
    tool_config: Optional[dict] = Field(
        default=None,
        description="Generated ToolConfig as a dictionary (present on success)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message describing what went wrong (present on error)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "tool_config": {
                        "name": "get_weather",
                        "description": "Get current weather information",
                        "version": 1,
                        "enabled": True,
                        "api": {
                            "base_url": "https://api.openweathermap.org",
                            "path": "/data/2.5/weather",
                            "method": "GET",
                            "headers": {},
                            "params": {},
                            "auth": {"method": "none"},
                            "timeout": 30.0
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {"city": {"type": "string"}},
                            "required": ["city"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {"temperature": {"type": "number"}},
                            "required": ["temperature"]
                        },
                        "mapping": {
                            "input_to_params": {"city": "q"},
                            "input_to_body": {},
                            "response_to_output": {"temperature": "main.temp"},
                            "response_path": None
                        },
                        "tags": [],
                        "metadata": {}
                    }
                },
                {
                    "status": "error",
                    "error": "Failed to generate config: Invalid API documentation provided"
                }
            ]
        }
    }

