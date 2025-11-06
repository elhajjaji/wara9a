"""
Base class for all Wara9a output generators.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class GeneratorBase(ABC):
    """
    Base class for all output format generators.
    
    Each generator takes content rendered by templates
    and converts it to a specific format (HTML, PDF, etc.).
    """
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Returns the name of the generated format."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Returns the default file extension."""
        pass
    
    @abstractmethod
    def generate(self, content: str, output_path: Path, context: Dict[str, Any]) -> Path:
        """
        Generate the output file in the appropriate format.
        
        Args:
            content: Content rendered by the template
            output_path: Desired output path
            context: Template context (for metadata, etc.)
            
        Returns:
            Path of the generated file
        """
        pass
    
    def prepare_output_path(self, output_path: Path) -> Path:
        """
        Prepare the output path with the appropriate extension.
        
        Args:
            output_path: Base path
            
        Returns:
            Path with correct extension
        """
        if output_path.suffix != self.file_extension:
            output_path = output_path.with_suffix(self.file_extension)
        
        # Create parent directory if necessary
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path