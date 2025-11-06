"""
HTML generator for Wara9a.

Converts Markdown content to HTML with a default theme.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from wara9a.generators.base import GeneratorBase


logger = logging.getLogger(__name__)


class HTMLGenerator(GeneratorBase):
    """
    Generator for HTML files.
    
    Converts Markdown content to HTML and applies a CSS theme.
    """
    
    @property
    def format_name(self) -> str:
        return "html"
    
    @property
    def file_extension(self) -> str:
        return ".html"
    
    def generate(self, content: str, output_path: Path, context: Dict[str, Any]) -> Path:
        """
        Generate an HTML file.
        
        Args:
            content: Markdown content to convert
            output_path: Output path
            context: Template context
            
        Returns:
            Path of generated file
        """
        output_path = self.prepare_output_path(output_path)
        
        try:
            # Convert Markdown to HTML
            html_content = self._markdown_to_html(content)
            
            # Apply HTML template
            final_html = self._apply_html_template(html_content, context)
            
            # Write file
            output_path.write_text(final_html, encoding='utf-8')
            
            logger.info(f"HTML file generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML to {output_path}: {e}")
            raise
    
    def _markdown_to_html(self, content: str) -> str:
        """
        Convert Markdown content to HTML.
        
        For now, a simple conversion. Later we can
        use a library like python-markdown or mistune.
        """
        try:
            # Try to import markdown if available
            import markdown
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
            return md.convert(content)
        except ImportError:
            # Simple fallback if markdown is not installed
            logger.warning("Module 'markdown' not available, using basic conversion")
            return self._simple_markdown_to_html(content)
    
    def _simple_markdown_to_html(self, content: str) -> str:
        """
        Very basic Markdown -> HTML conversion.
        
        Handles only the most common elements.
        """
        import re
        
        html = content
        
        # Titres
        html = re.sub(r'^# (.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*)', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Liens
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Gras et italique
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        # Code inline
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Listes
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'  <li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                
                # Paragraphes
                if line.strip() and not line.strip().startswith('<'):
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        return '\n'.join(result_lines)
    
    def _apply_html_template(self, html_content: str, context: Dict[str, Any]) -> str:
        """
        Applique un template HTML complet autour du contenu.
        
        Args:
            html_content: Contenu HTML converti
            context: Context for metadata
            
        Returns:
            HTML complet avec structure et CSS
        """
        project = context.get('project', {})
        title = project.get('name', 'Documentation Wara9a')
        description = project.get('description', '')
        
        css = self._get_default_css()
        
        template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {f'<meta name="description" content="{description}">' if description else ''}
    <meta name="generator" content="Wara9a">
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
        <main class="content">
{html_content}
        </main>
        <footer class="footer">
            <p>Generated with <a href="https://github.com/elhajjaji/wara9a">Wara9a</a></p>
        </footer>
    </div>
</body>
</html>"""
        
        return template
    
    def _get_default_css(self) -> str:
        """
        Returns default CSS for HTML documents.
        
        A simple, professional theme inspired by GitHub.
        """
        return """
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f6f8fa;
        }
        
        .container {
            max-width: 1024px;
            margin: 0 auto;
            padding: 2rem;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .content {
            min-height: 80vh;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #24292e;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3rem;
        }
        
        h1 {
            font-size: 2rem;
            border-bottom: 2px solid #0366d6;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.25rem;
            border-bottom: none;
        }
        
        p {
            margin-bottom: 1rem;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        code {
            background-color: #f6f8fa;
            border-radius: 3px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        }
        
        ul, ol {
            padding-left: 2rem;
            margin-bottom: 1rem;
        }
        
        li {
            margin-bottom: 0.5rem;
        }
        
        .footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #eaecef;
            text-align: center;
            color: #586069;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #0366d6;
            font-weight: 600;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
                margin: 0;
                box-shadow: none;
            }
            
            h1 {
                font-size: 1.75rem;
            }
        }
        """