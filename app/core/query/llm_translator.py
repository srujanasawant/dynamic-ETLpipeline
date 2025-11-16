# app/core/query/llm_translator.py
import structlog
from typing import Optional
from anthropic import AsyncAnthropic
from app.config import settings
from app.models.schema_models import SchemaResponse

logger = structlog.get_logger()


class LLMQueryTranslator:
    """Translate natural language queries to database queries using LLM"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def translate(
        self,
        nl_query: str,
        schema: SchemaResponse,
        target_db: str = "postgresql"
    ) -> str:
        """
        Translate natural language to database query
        
        Args:
            nl_query: Natural language query
            schema: Current schema for the source
            target_db: Target database type (postgresql, mongodb)
        
        Returns:
            Database query string
        """
        try:
            # Build schema context
            schema_context = self._build_schema_context(schema, target_db)
            
            # Create prompt
            prompt = self._create_prompt(nl_query, schema_context, target_db)
            
            # Call Claude API
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            query = response.content[0].text.strip()
            
            # Extract query from code blocks if present
            if "```" in query:
                query = self._extract_query_from_codeblock(query)
            
            logger.info(
                "Query translated",
                nl_query=nl_query,
                target_db=target_db,
                generated_query=query[:200]
            )
            
            return query
            
        except Exception as e:
            logger.error("Query translation failed", exc_info=e)
            raise
    
    def _build_schema_context(self, schema: SchemaResponse, target_db: str) -> str:
        """Build schema description for LLM"""
        lines = [f"Table/Collection: data_{schema.source_id}", ""]
        lines.append("Fields:")
        
        for field in schema.fields:
            field_type = field.type
            if target_db == "postgresql":
                field_type = getattr(field, 'sql_type', field.type)
            
            nullable = "NULL" if field.nullable else "NOT NULL"
            lines.append(f"  - {field.name}: {field_type} {nullable}")
            
            if field.example_value:
                lines.append(f"    Example: {field.example_value[:50]}")
        
        return "\n".join(lines)
    
    def _create_prompt(self, nl_query: str, schema_context: str, target_db: str) -> str:
        """Create prompt for LLM"""
        if target_db == "postgresql":
            return f"""You are a SQL expert. Convert the following natural language query to a PostgreSQL SQL query.

Schema:
{schema_context}

Natural language query: {nl_query}

Return ONLY the SQL query, no explanations. Use proper SQL syntax.
Example format: SELECT field1, field2 FROM table WHERE condition;"""
        
        elif target_db == "mongodb":
            return f"""You are a MongoDB expert. Convert the following natural language query to a MongoDB query.

Collection Schema:
{schema_context}

Natural language query: {nl_query}

Return ONLY the MongoDB query as a Python dict, no explanations.
Example format: {{"field": {{"$gt": value}}}}"""
        
        else:
            raise ValueError(f"Unsupported target_db: {target_db}")
    
    def _extract_query_from_codeblock(self, text: str) -> str:
        """Extract query from markdown code block"""
        import re
        pattern = r'```(?:sql|python|mongodb)?\n(.*?)\n```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()