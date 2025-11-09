"""MCP Prompt Definitions

Provides contextual instructions to LLM clients.
"""


async def tool_generation_instructions(tool_type: str = "generic") -> str:
    """Provide instructions for generating different types of tools."""
    instructions = {
        "generic": """Instructions for generating generic API tools:
    
    1. Name should be descriptive and concise (snake_case)
    2. Description should explain what the tool does and its primary use case
    3. Include all required input parameters with clear names
    4. Specify the API endpoint, HTTP method, and authentication method
    5. Include examples of input and expected output
    6. Document any rate limits or constraints
    7. Return format should be clearly specified (JSON, text, etc.)
    """,
        
        "rest": """Instructions for REST API tools:
    
    1. Base URL should be the API's root endpoint
    2. Path should be the specific resource path
    3. Method should be GET, POST, PUT, DELETE, etc.
    4. Headers should include Content-Type and Authorization if needed
    5. Query parameters and body parameters should be clearly separated
    6. Response format should match OpenAPI/Swagger specs if available
    7. Error handling should specify expected error codes
    """,
        
        "database": """Instructions for database tools:
    
    1. Connection string must include all authentication details
    2. Query parameters should be clearly typed (string, number, date, etc.)
    3. Result format should specify column names and data types
    4. Limit results to prevent large data transfers
    5. Include query timeout to prevent long-running operations
    6. Document any required permissions
    """
    }
    
    return instructions.get(tool_type, instructions["generic"])


async def execution_guide(api_type: str = "rest") -> str:
    """Guide for executing API calls safely and reliably."""
    guides = {
        "rest": """Guide for executing REST API calls:
    
    1. Validate the endpoint URL before making requests
    2. Include proper authentication headers (API key, OAuth token, etc.)
    3. Set appropriate timeouts (30 seconds typical for HTTP requests)
    4. Handle rate limits with exponential backoff
    5. Parse and validate the response before returning
    6. Log all requests and responses for debugging
    7. Handle common HTTP errors: 4xx (client error), 5xx (server error)
    8. Respect API documentation for rate limits and payload sizes
    """,
        
        "database": """Guide for database execution:
    
    1. Use prepared statements to prevent SQL injection
    2. Set query timeout to prevent hanging connections
    3. Validate all input parameters before building queries
    4. Handle connection pooling and cleanup
    5. Log all executed queries for auditing
    6. Implement connection retry logic for transient failures
    7. Limit result set size to prevent memory issues
    8. Properly encode/decode special characters
    """,
        
        "generic": """General execution guide:
    
    1. Always validate inputs against expected schemas
    2. Implement timeout mechanisms for all operations
    3. Log all executions for debugging and monitoring
    4. Handle errors gracefully with descriptive messages
    5. Implement retry logic for transient failures
    6. Clean up resources (connections, files, etc.)
    7. Rate limit requests according to API specifications
    8. Cache results when appropriate
    """
    }
    
    return guides.get(api_type, guides["generic"])
