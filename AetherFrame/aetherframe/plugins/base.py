"""Plugin base class and manifest system.

This module defines the MANDATORY contract for all AetherFrame plugins.
Every plugin MUST:
1. Ship a plugin.yaml manifest
2. Implement the Plugin interface
3. Return a PluginResult from run()
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import yaml

from aetherframe.schemas import JobContext, PluginResult


class PluginKind(str, Enum):
    """Plugin classification."""
    detector = "detector"      # Umbriel, anti-analysis
    differ = "differ"          # Valkyrie, binary diff
    tracer = "tracer"          # LainTrace, dynamic hooks
    reconstructor = "reconstructor"  # Mnemosyne, state/memory
    inferencer = "inferencer"  # Noema, intent
    analyzer = "analyzer"      # Static analysis
    reporter = "reporter"      # Report generation


@dataclass
class PluginManifest:
    """Parsed plugin.yaml manifest.

    Required fields:
    - id: Unique plugin identifier (lowercase, no spaces)
    - name: Human-readable name
    - version: Semantic version (X.Y.Z)
    - kind: Plugin type from PluginKind enum
    - capabilities: List of capability strings

    Optional fields:
    - description: Plugin description
    - author: Author name/email
    - inputs: List of accepted input types
    - outputs: List of output types produced
    - dependencies: Other plugins this depends on
    - config_schema: JSON Schema for plugin config
    """
    id: str
    name: str
    version: str
    kind: PluginKind
    capabilities: List[str] = field(default_factory=list)
    description: Optional[str] = None
    author: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None

    @classmethod
    def from_yaml(cls, path: Path) -> "PluginManifest":
        """Load manifest from plugin.yaml file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """Parse manifest from dictionary."""
        required = ["id", "name", "version", "kind"]
        for key in required:
            if key not in data:
                raise ValueError(f"Missing required manifest field: {key}")

        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            kind=PluginKind(data["kind"]),
            capabilities=data.get("capabilities", []),
            description=data.get("description"),
            author=data.get("author"),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            dependencies=data.get("dependencies", []),
            config_schema=data.get("config_schema"),
        )

    def validate(self) -> List[str]:
        """Validate manifest, return list of errors."""
        errors = []
        if not self.id or not self.id.replace("_", "").replace("-", "").isalnum():
            errors.append(f"Invalid plugin id: {self.id}")
        if not self.version:
            errors.append("Version is required")
        if not self.capabilities:
            errors.append("At least one capability is required")
        return errors


class Plugin(ABC):
    """Base class for all AetherFrame plugins.

    Subclasses MUST implement:
    - validate(): Pre-execution validation
    - run(): Main execution logic returning PluginResult
    """

    def __init__(self, manifest: PluginManifest, config: Optional[Dict[str, Any]] = None):
        self.manifest = manifest
        self.config = config or {}

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    @property
    def capabilities(self) -> List[str]:
        return self.manifest.capabilities

    @abstractmethod
    def validate(self, ctx: JobContext) -> None:
        """Validate that the plugin can run with given context.

        Raises:
            PluginValidationError: If validation fails
        """
        pass

    @abstractmethod
    def run(self, ctx: JobContext) -> PluginResult:
        """Execute the plugin and return results.

        Args:
            ctx: Job context with target, workspace, and previous results

        Returns:
            PluginResult containing findings, artifacts, and events
        """
        pass

    def supports_capability(self, capability: str) -> bool:
        """Check if plugin supports a specific capability."""
        return capability in self.capabilities


class PluginValidationError(Exception):
    """Raised when plugin validation fails."""
    def __init__(self, plugin_id: str, message: str):
        self.plugin_id = plugin_id
        self.message = message
        super().__init__(f"[{plugin_id}] Validation failed: {message}")


class PluginExecutionError(Exception):
    """Raised when plugin execution fails."""
    def __init__(self, plugin_id: str, message: str, cause: Optional[Exception] = None):
        self.plugin_id = plugin_id
        self.message = message
        self.cause = cause
        super().__init__(f"[{plugin_id}] Execution failed: {message}")
