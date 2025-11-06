"""
Markdown generator for Wara9a.

The simplest generator: directly writes content
rendered by templates to .md files.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from wara9a.generators.base import GeneratorBase


logger = logging.getLogger(__name__)


class MarkdownGenerator(GeneratorBase):
    """
    Generator for Markdown files.
    
    Directly writes template content to .md files
    without additional transformation.
    """
    
    @property
    def format_name(self) -> str:
        return "markdown"
    
    @property
    def file_extension(self) -> str:
        return ".md"
    
    def generate(self, content: str, output_path: Path, context: Dict[str, Any]) -> Path:
        """
        Generate a Markdown file.
        
        Args:
            content: Rendered Markdown content
            output_path: Output path
            context: Template context
            
        Returns:
            Path of generated file
        """
        output_path = self.prepare_output_path(output_path)
        
        try:
            # Add optional metadata header
            final_content = self._add_metadata(content, context)
            
            # Write file
            output_path.write_text(final_content, encoding='utf-8')
            
            logger.info(f"Markdown file generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Markdown to {output_path}: {e}")
            raise
    
    def _add_metadata(self, content: str, context: Dict[str, Any]) -> str:
        """
        Add optional YAML Front Matter metadata.
        
        Args:
            content: Markdown content
            context: Context with metadata
            
        Returns:
            Content with metadata
        """
        # If content already starts with ---, do nothing
        if content.strip().startswith('---'):
            return content
        
        # Extract some useful metadata from context
        metadata = {}
        
        if 'project' in context:
            project = context['project']
            metadata['title'] = project.get('name', 'Documentation')
            if project.get('description'):
                metadata['description'] = project['description']
            if project.get('author'):
                metadata['author'] = project['author']
        
        if 'template' in context:
            template = context['template']
            if template.get('name'):
                metadata['template'] = template['name']
        
        # Add generation date
        from datetime import datetime
        metadata['generated_at'] = datetime.now().isoformat()
        metadata['generator'] = 'Wara9a'
        
        # If we have metadata, add it as front matter
        if metadata:
            import yaml
            front_matter = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
            return f"---\n{front_matter}---\n\n{content}"
        
        return content