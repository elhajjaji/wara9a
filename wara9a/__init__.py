"""
Wara9a - Documentation IT automatique et intelligente.

Framework open-source Python qui transforme automatiquement 
vos projets IT en documentation claire et professionnelle.
"""

__version__ = "1.0.0"
__author__ = "elhajjaji"
__license__ = "MIT"

from wara9a.core.project import Project
from wara9a.core.generator import DocumentGenerator

__all__ = ["Project", "DocumentGenerator"]