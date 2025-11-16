# app/core/schema/evolution.py
import structlog
from typing import List
from app.models.schema_models import SchemaResponse, SchemaDiff

logger = structlog.get_logger()


class SchemaEvolutionManager:
    """Manage schema evolution and generate diffs"""
    
    def generate_diffs(self, versions: List[SchemaResponse]) -> List[SchemaDiff]:
        """Generate diffs between consecutive schema versions"""
        diffs = []
        
        for i in range(len(versions) - 1):
            current = versions[i]
            next_ver = versions[i + 1]
            
            diff = self._compute_diff(current, next_ver)
            diffs.append(diff)
        
        return diffs
    
    def _compute_diff(self, v1: SchemaResponse, v2: SchemaResponse) -> SchemaDiff:
        """Compute diff between two schema versions"""
        v1_fields = {f.name: f for f in v1.fields}
        v2_fields = {f.name: f for f in v2.fields}
        
        v1_names = set(v1_fields.keys())
        v2_names = set(v2_fields.keys())
        
        added = list(v2_names - v1_names)
        removed = list(v1_names - v2_names)
        
        # Check for modifications in common fields
        common = v1_names & v2_names
        modified = []
        type_changes = []
        
        for name in common:
            f1 = v1_fields[name]
            f2 = v2_fields[name]
            
            if f1.type != f2.type:
                type_changes.append({
                    "field": name,
                    "from": f1.type,
                    "to": f2.type
                })
            
            if f1.nullable != f2.nullable:
                modified.append({
                    "field": name,
                    "change": "nullable",
                    "from": f1.nullable,
                    "to": f2.nullable
                })
        
        return SchemaDiff(
            version_from=v1.version,
            version_to=v2.version,
            added_fields=added,
            removed_fields=removed,
            modified_fields=modified,
            type_changes=type_changes
        )