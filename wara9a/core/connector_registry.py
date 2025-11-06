"""
Registre des connecteurs Wara9a.

Gère l'enregistrement, la découverte et l'instanciation des connecteurs.
Supporte les connecteurs intégrés et les plugins tiers.
"""

import logging
from typing import Dict, List, Type, Optional, Set
import importlib
import pkgutil

from wara9a.core.connector_base import ConnectorBase


logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """
    Registre centralisé des connecteurs disponibles.
    
    Permet l'enregistrement automatique des connecteurs intégrés
    et le chargement dynamique de connecteurs tiers via des plugins.
    """
    
    def __init__(self):
        self._connectors: Dict[str, Type[ConnectorBase]] = {}
        self._instances: Dict[str, ConnectorBase] = {}
        self._loaded_plugins: Set[str] = set()
        
        # Load built-in connectors
        self._load_builtin_connectors()
    
    def register_connector(self, connector_class: Type[ConnectorBase]) -> None:
        """
        Enregistre un nouveau connecteur.
        
        Args:
            connector_class: Classe du connecteur à enregistrer
            
        Raises:
            ValueError: Si le connecteur est déjà enregistré ou invalide
        """
        if not issubclass(connector_class, ConnectorBase):
            raise ValueError(f"{connector_class} doit hériter de ConnectorBase")
        
        # Create temporary instance to get type
        temp_instance = connector_class()
        connector_type = temp_instance.connector_type
        
        if connector_type in self._connectors:
            existing = self._connectors[connector_type]
            logger.warning(f"Remplacement du connecteur {connector_type}: "
                         f"{existing} -> {connector_class}")
        
        self._connectors[connector_type] = connector_class
        # Invalider l'instance en cache
        self._instances.pop(connector_type, None)
        
        logger.info(f"Connecteur enregistré: {connector_type} ({connector_class.__name__})")
    
    def get_connector(self, connector_type: str) -> ConnectorBase:
        """
        Obtient une instance d'un connecteur par son type.
        
        Args:
            connector_type: Type du connecteur (ex: 'github', 'jira')
            
        Returns:
            Instance du connecteur
            
        Raises:
            ValueError: Si le connecteur n'est pas trouvé
        """
        if connector_type not in self._connectors:
            # Essayer de charger le connecteur dynamiquement
            self._try_load_connector(connector_type)
        
        if connector_type not in self._connectors:
            available = list(self._connectors.keys())
            raise ValueError(
                f"Connecteur non trouvé: {connector_type}. "
                f"Connecteurs disponibles: {available}"
            )
        
        # Use cached instance or create new one
        if connector_type not in self._instances:
            connector_class = self._connectors[connector_type]
            self._instances[connector_type] = connector_class()
        
        return self._instances[connector_type]
    
    def has_connector(self, connector_type: str) -> bool:
        """Vérifie si un connecteur est disponible."""
        if connector_type in self._connectors:
            return True
        
        # Essayer de charger dynamiquement
        self._try_load_connector(connector_type)
        return connector_type in self._connectors
    
    def list_connectors(self) -> List[ConnectorBase]:
        """Retourne la liste de tous les connecteurs disponibles."""
        connectors = []
        for connector_type in self._connectors:
            try:
                connectors.append(self.get_connector(connector_type))
            except Exception as e:
                logger.error(f"Erreur lors du chargement du connecteur {connector_type}: {e}")
        return connectors
    
    def list_connector_types(self) -> List[str]:
        """Retourne la liste des types de connecteurs disponibles."""
        return list(self._connectors.keys())
    
    def get_connector_info(self, connector_type: str) -> Dict[str, str]:
        """Retourne les informations sur un connecteur."""
        connector = self.get_connector(connector_type)
        return {
            "type": connector.connector_type,
            "name": connector.display_name,
            "description": connector.description,
            "required_fields": connector.required_config_fields,
            "optional_fields": connector.optional_config_fields,
        }
    
    def _load_builtin_connectors(self) -> None:
        """Charge automatiquement tous les connecteurs intégrés."""
        try:
            import wara9a.connectors
            
            # Parcourir tous les modules dans le package connectors
            for finder, name, ispkg in pkgutil.iter_modules(wara9a.connectors.__path__, 
                                                           wara9a.connectors.__name__ + "."):
                if not ispkg:  # On veut seulement les modules, pas les packages
                    try:
                        module = importlib.import_module(name)
                        self._register_connectors_from_module(module)
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement du module {name}: {e}")
                        
        except ImportError:
            logger.warning("Package wara9a.connectors non trouvé")
    
    def _register_connectors_from_module(self, module) -> None:
        """Enregistre tous les connecteurs trouvés dans un module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a connector class
            if (isinstance(attr, type) and 
                issubclass(attr, ConnectorBase) and 
                attr != ConnectorBase):
                
                try:
                    self.register_connector(attr)
                except Exception as e:
                    logger.error(f"Erreur lors de l'enregistrement du connecteur {attr}: {e}")
    
    def _try_load_connector(self, connector_type: str) -> None:
        """Essaie de charger un connecteur dynamiquement."""
        if connector_type in self._loaded_plugins:
            return  # Already tried
        
        self._loaded_plugins.add(connector_type)
        
        # Essayer de charger depuis wara9a.connectors.{type}
        module_name = f"wara9a.connectors.{connector_type}"
        try:
            module = importlib.import_module(module_name)
            self._register_connectors_from_module(module)
            logger.info(f"Connecteur {connector_type} chargé dynamiquement")
        except ImportError:
            logger.debug(f"Module {module_name} non trouvé")
        except Exception as e:
            logger.error(f"Erreur lors du chargement dynamique de {module_name}: {e}")
    
    def load_plugin_connector(self, module_path: str) -> None:
        """
        Charge un connecteur depuis un module externe.
        
        Args:
            module_path: Chemin vers le module (ex: 'my_package.my_connector')
        """
        try:
            module = importlib.import_module(module_path)
            self._register_connectors_from_module(module)
            logger.info(f"Plugin connecteur chargé: {module_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du plugin {module_path}: {e}")
            raise
    
    def clear(self) -> None:
        """Vide le registre (utile pour les tests)."""
        self._connectors.clear()
        self._instances.clear()
        self._loaded_plugins.clear()


# Instance globale du registre
_global_registry: Optional[ConnectorRegistry] = None


def get_global_registry() -> ConnectorRegistry:
    """Retourne l'instance globale du registre des connecteurs."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ConnectorRegistry()
    return _global_registry


def register_connector(connector_class: Type[ConnectorBase]) -> None:
    """Raccourci pour enregistrer un connecteur dans le registre global."""
    get_global_registry().register_connector(connector_class)