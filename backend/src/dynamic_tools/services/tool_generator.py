"""Service for generating tool configurations from API descriptions."""

from typing import Optional
import json
from loguru import logger

from ..models.tool_config import ToolConfig, ApiConfig, FieldMapping, AuthConfig
from ..models.enums import HttpMethod, AuthMethod
from ..models.api_requests import MCPPromptRequest
from .prompt_service import PromptService
from .prompt_templates import PromptTemplates


class ToolConfigGenerator:
    """Service for generating ToolConfigs from natural language API descriptions.
    
    This service uses the PromptService to convert API documentation and descriptions
    into complete, valid ToolConfig objects that can be immediately used to register
    new tools.
    
    Attributes:
        prompt_service: PromptService for LLM interactions
        max_retries: Maximum number of retry attempts on failure
    """
    
    def __init__(self, api_key: str, max_retries: int = 3):
        """Initialize the ToolConfigGenerator.
        
        Args:
            api_key: OpenAI API key for LLM calls
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.prompt_service = PromptService(
            api_key=api_key,
            max_retries=max_retries
        )
        self.max_retries = max_retries
        logger.info("ToolConfigGenerator initialized")
    
    async def generate_tool_config(
        self,
        tool_name: str,
        tool_description: str,
        api_docs: str,
        input_schema_description: Optional[str] = None,
        output_schema_description: Optional[str] = None
    ) -> dict:
        """Generate a complete ToolConfig from API description.
        
        This method orchestrates the generation of all ToolConfig components:
        1. Uses /prompt-mcp to generate HTTPRequestSpec from API docs
        2. Extracts ApiConfig from the HTTPRequestSpec
        3. Generates input schema from description or API docs
        4. Generates output schema from description or API response
        5. Generates field mappings between input/output and API parameters
        6. Returns complete serialized ToolConfig
        
        Args:
            tool_name: Unique name for the tool
            tool_description: Human-readable description of what the tool does
            api_docs: API documentation or endpoint information
            input_schema_description: Optional description of expected input fields
            output_schema_description: Optional description of expected output fields
            
        Returns:
            Dictionary representation of complete ToolConfig
            
        Raises:
            Exception: If LLM generation fails or invalid config produced
        """
        try:
            logger.info(f"Starting tool config generation for: {tool_name}")
            logger.debug(f"Tool description: {tool_description[:100]}...")
            
            # Step 1: Generate HTTPRequestSpec from API docs via /prompt-mcp
            logger.info("Step 1/5: Generating HTTP request specification...")
            http_spec = await self._generate_http_spec(
                tool_description=tool_description,
                api_docs=api_docs
            )
            logger.debug(f"Generated HTTPRequestSpec: {http_spec}")
            
            # Step 2: Extract ApiConfig from HTTPRequestSpec
            logger.info("Step 2/5: Extracting API configuration...")
            api_config = self._extract_api_config(http_spec)
            logger.debug(f"Extracted ApiConfig: {api_config}")
            
            # Step 3: Generate input schema
            logger.info("Step 3/5: Generating input schema...")
            input_schema = await self._generate_input_schema(
                tool_description=tool_description,
                api_docs=api_docs,
                input_schema_description=input_schema_description
            )
            logger.debug(f"Generated input schema: {input_schema}")
            
            # Step 4: Generate output schema
            logger.info("Step 4/5: Generating output schema...")
            output_schema = await self._generate_output_schema(
                tool_description=tool_description,
                api_docs=api_docs,
                output_schema_description=output_schema_description
            )
            logger.debug(f"Generated output schema: {output_schema}")
            
            # Step 5: Generate field mappings
            logger.info("Step 5/5: Generating field mappings...")
            field_mapping = await self._generate_field_mapping(
                http_spec=http_spec,
                input_schema=input_schema,
                output_schema=output_schema,
                api_docs=api_docs
            )
            logger.debug(f"Generated field mapping: {field_mapping}")
            
            # Construct ToolConfig
            tool_config = ToolConfig(
                name=tool_name,
                description=tool_description,
                version=1,
                enabled=True,
                api=api_config,
                input_schema=input_schema,
                output_schema=output_schema,
                mapping=field_mapping,
                tags=[]
            )
            
            logger.info(f"✅ Successfully generated tool config for: {tool_name}")
            return tool_config.model_dump()
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tool config: {e}")
            raise
    
    async def _generate_http_spec(
        self,
        tool_description: str,
        api_docs: str
    ) -> dict:
        """Generate HTTPRequestSpec from API documentation.
        
        Uses the /prompt-mcp endpoint to intelligently construct an HTTP request
        specification from natural language API documentation.
        
        Args:
            tool_description: Description of what the tool should do
            api_docs: API documentation
            
        Returns:
            Dictionary with HTTP request specification
        """
        try:
            # Create MCP request
            mcp_request = MCPPromptRequest(
                instructions=f"Generate HTTP request specification for: {tool_description}",
                api_docs=api_docs,
                response_format_prompt="Return a valid HTTP request specification with method, url, headers, query_params, and body fields"
            )
            
            # Call prompt service
            response = await self.prompt_service.prompt_mcp(mcp_request)
            
            # Extract content
            if isinstance(response.content, dict):
                return response.content
            else:
                logger.warning(f"Unexpected response type: {type(response.content)}")
                return json.loads(response.content) if isinstance(response.content, str) else response.content
                
        except Exception as e:
            logger.error(f"Failed to generate HTTP spec: {e}")
            raise
    
    def _extract_api_config(self, http_spec: dict) -> ApiConfig:
        """Extract ApiConfig from HTTPRequestSpec.
        
        Transforms a generated HTTPRequestSpec into an ApiConfig with base_url,
        path, method, headers, params, and authentication configuration.
        
        Args:
            http_spec: Dictionary with HTTP request specification
            
        Returns:
            ApiConfig object
        """
        try:
            # Extract URL and split into base_url and path
            url = http_spec.get("url", "")
            base_url, path = self._split_url(url)
            
            # Extract HTTP method
            method_str = http_spec.get("method", "GET").upper()
            method = HttpMethod(method_str) if method_str in [m.value for m in HttpMethod] else HttpMethod.GET
            
            # Extract headers
            headers = http_spec.get("headers", {})
            
            # Extract query parameters
            query_params = http_spec.get("query_params", {})
            
            # Create ApiConfig
            api_config = ApiConfig(
                base_url=base_url,
                path=path,
                method=method,
                headers=headers,
                params=query_params,
                auth=AuthConfig(method=AuthMethod.NONE),
                timeout=30.0
            )
            
            logger.debug(f"Extracted ApiConfig: base_url={base_url}, path={path}, method={method}")
            return api_config
            
        except Exception as e:
            logger.error(f"Failed to extract API config: {e}")
            raise
    
    @staticmethod
    def _split_url(url: str) -> tuple[str, str]:
        """Split URL into base_url and path.
        
        Args:
            url: Complete URL
            
        Returns:
            Tuple of (base_url, path)
        """
        try:
            # Find the scheme and domain
            if "://" in url:
                scheme, rest = url.split("://", 1)
                parts = rest.split("/", 1)
                base_url = f"{scheme}://{parts[0]}"
                path = f"/{parts[1]}" if len(parts) > 1 else ""
            else:
                # Handle URLs without scheme
                parts = url.split("/", 1)
                base_url = parts[0]
                path = f"/{parts[1]}" if len(parts) > 1 else ""
            
            return base_url, path
        except Exception as e:
            logger.error(f"Failed to split URL: {e}")
            return url, ""
    
    async def _generate_input_schema(
        self,
        tool_description: str,
        api_docs: str,
        input_schema_description: Optional[str] = None
    ) -> dict:
        """Generate JSON Schema for tool input.
        
        Creates a comprehensive JSON Schema describing what inputs the tool accepts,
        inferred from the API documentation and tool description.
        
        Args:
            tool_description: Description of what the tool does
            api_docs: API documentation
            input_schema_description: Optional user-provided input description
            
        Returns:
            JSON Schema dictionary for inputs
        """
        try:
            # Build instructions
            instructions = f"""Generate a JSON Schema for the input parameters of this tool.
Tool: {tool_description}

The schema should be a valid JSON Schema (draft-7) with type='object', properties, and required fields.
Focus on extracting the key input parameters needed to call this API."""
            
            if input_schema_description:
                instructions += f"\n\nAdditional guidance: {input_schema_description}"
            
            # Call LLM for schema generation (using normal prompt)
            from ..models.api_requests import PromptRequest
            prompt_request = PromptRequest(
                instructions=instructions,
                context=api_docs,
                response_format_prompt="Return ONLY valid JSON Schema, nothing else. Start with { and end with }"
            )
            
            response = await self.prompt_service.prompt_normal(prompt_request)
            
            # Parse response
            schema_str = response.content
            if isinstance(schema_str, str):
                schema = json.loads(schema_str)
            else:
                schema = schema_str
            
            # Ensure it's a valid schema
            if not isinstance(schema, dict) or "type" not in schema:
                # Create default schema if parsing fails
                logger.warning("Generated schema invalid, creating default")
                schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            
            return schema
            
        except Exception as e:
            logger.error(f"Failed to generate input schema: {e}")
            # Return default schema on failure
            return {
                "type": "object",
                "properties": {},
                "required": []
            }
    
    async def _generate_output_schema(
        self,
        tool_description: str,
        api_docs: str,
        output_schema_description: Optional[str] = None
    ) -> dict:
        """Generate JSON Schema for tool output.
        
        Creates a comprehensive JSON Schema describing what the tool returns,
        inferred from the API response format and tool description.
        
        Args:
            tool_description: Description of what the tool does
            api_docs: API documentation
            output_schema_description: Optional user-provided output description
            
        Returns:
            JSON Schema dictionary for outputs
        """
        try:
            # Build instructions
            instructions = f"""Generate a JSON Schema for the output/response of this tool.
Tool: {tool_description}

The schema should be a valid JSON Schema (draft-7) with type='object', properties, and required fields.
Focus on extracting the key output fields that this API returns."""
            
            if output_schema_description:
                instructions += f"\n\nAdditional guidance: {output_schema_description}"
            
            # Call LLM for schema generation (using normal prompt)
            from ..models.api_requests import PromptRequest
            prompt_request = PromptRequest(
                instructions=instructions,
                context=api_docs,
                response_format_prompt="Return ONLY valid JSON Schema, nothing else. Start with { and end with }"
            )
            
            response = await self.prompt_service.prompt_normal(prompt_request)
            
            # Parse response
            schema_str = response.content
            if isinstance(schema_str, str):
                schema = json.loads(schema_str)
            else:
                schema = schema_str
            
            # Ensure it's a valid schema
            if not isinstance(schema, dict) or "type" not in schema:
                # Create default schema if parsing fails
                logger.warning("Generated schema invalid, creating default")
                schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            
            return schema
            
        except Exception as e:
            logger.error(f"Failed to generate output schema: {e}")
            # Return default schema on failure
            return {
                "type": "object",
                "properties": {},
                "required": []
            }
    
    async def _generate_field_mapping(
        self,
        http_spec: dict,
        input_schema: dict,
        output_schema: dict,
        api_docs: str
    ) -> FieldMapping:
        """Generate field mappings between input/output and API parameters.
        
        Creates mappings that connect tool input parameters to API request parameters,
        and API response fields to tool output fields.
        
        Args:
            http_spec: Generated HTTP request specification
            input_schema: Generated input JSON schema
            output_schema: Generated output JSON schema
            api_docs: API documentation
            
        Returns:
            FieldMapping object
        """
        try:
            # Extract properties from schemas
            input_properties = input_schema.get("properties", {})
            output_properties = output_schema.get("properties", {})
            
            # Build basic mappings
            input_to_params = {}
            for input_key in input_properties.keys():
                # Simple mapping: input field name -> API param name (same name)
                input_to_params[input_key] = input_key
            
            response_to_output = {}
            for output_key in output_properties.keys():
                # Simple mapping: API response field -> output field (same name)
                response_to_output[output_key] = output_key
            
            # Create FieldMapping
            mapping = FieldMapping(
                input_to_params=input_to_params,
                input_to_body={},
                response_to_output=response_to_output,
                response_path=None
            )
            
            logger.debug(f"Generated field mappings - input_to_params: {input_to_params}, response_to_output: {response_to_output}")
            return mapping
            
        except Exception as e:
            logger.error(f"Failed to generate field mapping: {e}")
            # Return empty mapping on failure
            return FieldMapping()

