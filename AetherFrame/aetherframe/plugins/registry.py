"""Plugin registry — discovers, loads, and manages plugins.

The registry is the central authority for plugin management:
- Auto-discovery from plugins directory
- Manifest validation
- Dependency resolution
- Plugin instantiation
"""

from __future__ import annotations
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
import logging

from .base import Plugin, PluginManifest, PluginKind

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all AetherFrame plugins."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        self._plugins: Dict[str, Type[Plugin]] = {}
        self._manifests: Dict[str, PluginManifest] = {}
        self._instances: Dict[str, Plugin] = {}
        self.plugins_dir = plugins_dir or Path(__file__).parent

    def discover(self) -> List[str]:
        """Discover all plugins in the plugins directory.

        Returns:
            List of discovered plugin IDs
        """
        discovered = []
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            if plugin_dir.name.startswith("_"):
                continue

            manifest_path = plugin_dir / "plugin.yaml"
            if not manifest_path.exists():
                logger.warning(f"Skipping {plugin_dir.name}: no plugin.yaml")
                continue

            try:
                manifest = PluginManifest.from_yaml(manifest_path)
                errors = manifest.validate()
                if errors:
                    logger.error(f"Invalid manifest for {plugin_dir.name}: {errors}")
                    continue

                self._manifests[manifest.id] = manifest
                discovered.append(manifest.id)
                logger.info(f"Discovered plugin: {manifest.id} v{manifest.version}")

            except Exception as e:
                logger.error(f"Failed to load manifest from {plugin_dir.name}: {e}")
                continue

        return discovered

    def load(self, plugin_id: str) -> Type[Plugin]:
        """Load a plugin class by ID.

        Args:
            plugin_id: The plugin identifier

        Returns:
            The plugin class (not instantiated)

        Raises:
            KeyError: If plugin not found
            ImportError: If plugin module fails to load
        """
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]

        if plugin_id not in self._manifests:
            raise KeyError(f"Plugin not found: {plugin_id}")

        plugin_dir = self.plugins_dir / plugin_id
        plugin_module = plugin_dir / "plugin.py"

        if not plugin_module.exists():
            raise ImportError(f"No plugin.py found for {plugin_id}")

        spec = importlib.util.spec_from_file_location(
            f"aetherframe.plugins.{plugin_id}",
            plugin_module
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to create module spec for {plugin_id}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"aetherframe.plugins.{plugin_id}"] = module
        spec.loader.exec_module(module)

        # Find the Plugin subclass in the module
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, Plugin) and
                attr is not Plugin):
                plugin_class = attr
                break

        if plugin_class is None:
            raise ImportError(f"No Plugin subclass found in {plugin_id}/plugin.py")

        self._plugins[plugin_id] = plugin_class
        return plugin_class

    def get_instance(self, plugin_id: str, config: Optional[Dict] = None) -> Plugin:
        """Get or create a plugin instance.

        Args:
            plugin_id: The plugin identifier
            config: Optional plugin configuration

        Returns:
            Plugin instance
        """
        cache_key = f"{plugin_id}:{hash(frozenset((config or {}).items()))}"

        if cache_key not in self._instances:
            plugin_class = self.load(plugin_id)
            manifest = self._manifests[plugin_id]
            self._instances[cache_key] = plugin_class(manifest, config)

        return self._instances[cache_key]

    def get_manifest(self, plugin_id: str) -> PluginManifest:
        """Get plugin manifest by ID."""
        if plugin_id not in self._manifests:
            raise KeyError(f"Plugin manifest not found: {plugin_id}")
        return self._manifests[plugin_id]

    def list_plugins(self, kind: Optional[PluginKind] = None) -> List[PluginManifest]:
        """List all registered plugins, optionally filtered by kind."""
        manifests = list(self._manifests.values())
        if kind:
            manifests = [m for m in manifests if m.kind == kind]
        return manifests

    def find_by_capability(self, capability: str) -> List[str]:
        """Find plugins that support a specific capability.

        Args:
            capability: Capability string (e.g., "anti_analysis.scan")

        Returns:
            List of plugin IDs
        """
        return [
            m.id for m in self._manifests.values()
            if capability in m.capabilities
        ]

    def resolve_dependencies(self, plugin_id: str) -> List[str]:
        """Resolve plugin dependencies in topological order.

        Returns:
            List of plugin IDs to load in order
        """
        manifest = self.get_manifest(plugin_id)
        resolved = []
        visited = set()

        def visit(pid: str):
            if pid in visited:
                return
            visited.add(pid)
            m = self._manifests.get(pid)
            if m:
                for dep in m.dependencies:
                    visit(dep)
                resolved.append(pid)

        visit(plugin_id)
        return resolved


# Global registry instance
_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
        _registry.discover()
    return _registry


def register_plugin(plugin_class: Type[Plugin], manifest: PluginManifest) -> None:
    """Manually register a plugin (for testing or dynamic loading)."""
    registry = get_registry()
    registry._plugins[manifest.id] = plugin_class
    registry._manifests[manifest.id] = manifest
