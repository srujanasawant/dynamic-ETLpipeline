# app/core/ingestion/markdown_parser.py
import re
import structlog
from typing import Dict, Any, List
from bs4 import BeautifulSoup

logger = structlog.get_logger()


class MarkdownParser:
    """Parse Markdown files with embedded code and HTML"""
    
    async def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract markdown, code blocks, and embedded content"""
        try:
            text = content.decode('utf-8')
            
            # Extract frontmatter (YAML)
            frontmatter = self._extract_frontmatter(text)
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(text)
            
            # Extract HTML snippets
            html_snippets = self._extract_html(text)
            
            # Remove code blocks from main text
            clean_text = re.sub(r'```[\s\S]*?```', '', text)
            
            return {
                "text": clean_text,
                "frontmatter": frontmatter,
                "code_blocks": code_blocks,
                "html_snippets": html_snippets,
                "metadata": {
                    "has_frontmatter": bool(frontmatter),
                    "code_block_count": len(code_blocks),
                    "html_snippet_count": len(html_snippets)
                }
            }
            
        except Exception as e:
            logger.error("Markdown parsing failed", exc_info=e)
            raise
    
    def _extract_frontmatter(self, text: str) -> Dict[str, Any]:
        """Extract YAML frontmatter"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
        if match:
            try:
                import yaml
                return yaml.safe_load(match.group(1))
            except:
                return {}
        return {}
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks with language"""
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        blocks = []
        for match in matches:
            blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2)
            })
        
        return blocks
    
    def _extract_html(self, text: str) -> List[str]:
        """Extract HTML snippets"""
        pattern = r'<[^>]+>[\s\S]*?</[^>]+>'
        matches = re.findall(pattern, text)
        return matches