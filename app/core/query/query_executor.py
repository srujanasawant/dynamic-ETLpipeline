# app/core/query/query_executor.py
import structlog
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.database import get_mongo

logger = structlog.get_logger()


class QueryExecutor:
    """Execute database queries"""
    
    async def execute(
        self,
        query: str,
        source_id: str,
        target_db: str,
        db_session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        try:
            if target_db == "postgresql":
                return await self._execute_sql(query, source_id, db_session)
            elif target_db == "mongodb":
                return await self._execute_mongo(query, source_id)
            else:
                raise ValueError(f"Unsupported database: {target_db}")
                
        except Exception as e:
            logger.error("Query execution failed", exc_info=e, query=query)
            raise
    
    async def _execute_sql(
        self,
        query: str,
        source_id: str,
        db_session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Execute SQL query"""
        # Security: Basic SQL injection prevention
        if any(keyword in query.upper() for keyword in ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']):
            raise ValueError("Destructive SQL operations not allowed")
        
        result = await db_session.execute(text(query))
        rows = result.fetchall()
        
        # Convert to list of dicts
        if rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
        
        return []
    
    async def _execute_mongo(self, query: str, source_id: str) -> List[Dict[str, Any]]:
        """Execute MongoDB query"""
        import ast
        
        # Parse query string to dict
        try:
            query_dict = ast.literal_eval(query)
        except:
            query_dict = {}
        
        mongo_db = get_mongo()
        collection = mongo_db.parsed_data
        
        cursor = collection.find({"source_id": source_id, **query_dict})
        results = await cursor.to_list(length=100)
        
        # Remove MongoDB _id
        for result in results:
            result.pop('_id', None)
        
        return results