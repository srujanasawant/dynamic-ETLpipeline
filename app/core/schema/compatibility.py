# app/core/schema/compatibility.py
import structlog
from typing import List, Dict

logger = structlog.get_logger()


class CompatibilityChecker:
    """Check schema compatibility with different databases"""
    
    def check_compatibility(self, fields: List[Dict]) -> List[str]:
        """Determine which databases can support this schema"""
        compatible = []
        
        # PostgreSQL - most permissive
        if self._check_postgresql(fields):
            compatible.append("postgresql")
        
        # MongoDB - always compatible with flexible schema
        compatible.append("mongodb")
        
        # Neo4j - if there are relationship-like fields
        if self._check_neo4j(fields):
            compatible.append("neo4j")
        
        return compatible
    
    def _check_postgresql(self, fields: List[Dict]) -> bool:
        """Check PostgreSQL compatibility"""
        # PostgreSQL with JSONB can handle most schemas
        for field in fields:
            # Check if we have types PostgreSQL can't easily handle
            if field["type"] in ["unknown", "mixed"]:
                return False
        
        return True
    
    def _check_neo4j(self, fields: List[Dict]) -> bool:
        """Check if schema might benefit from graph database"""
        # Look for relationship indicators
        relationship_keywords = ['_id', 'ref', 'parent', 'child', 'relation']
        
        relationship_count = sum(
            1 for f in fields
            if any(kw in f["name"].lower() for kw in relationship_keywords)
        )
        
        return relationship_count >= 2
