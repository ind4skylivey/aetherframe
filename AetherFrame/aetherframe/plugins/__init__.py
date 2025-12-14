"""AetherFrame plugins package."""

from .base import Plugin, PluginManifest, PluginKind, PluginValidationError, PluginExecutionError
from .registry import PluginRegistry, get_registry, register_plugin

__all__ = [
    "Plugin",
    "PluginManifest",
    "PluginKind",
    "PluginValidationError",
    "PluginExecutionError",
    "PluginRegistry",
    "get_registry",
    "register_plugin",
]
