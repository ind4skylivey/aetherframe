"""Analyzer interface definitions."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Analyzer(ABC):
    name: str = "base"

    @abstractmethod
    def analyze(self, target: str) -> Dict[str, Any]:
        """Run analysis over a target and return results."""


class StaticAnalyzer(Analyzer):
    name = "static"

    def analyze(self, target: str) -> Dict[str, Any]:
        return {"target": target, "result": "static-analysis-placeholder"}


class DynamicAnalyzer(Analyzer):
    name = "dynamic"

    def analyze(self, target: str) -> Dict[str, Any]:
        return {"target": target, "result": "dynamic-analysis-placeholder"}


class SymbolicAnalyzer(Analyzer):
    name = "symbolic"

    def analyze(self, target: str) -> Dict[str, Any]:
        return {"target": target, "result": "symbolic-analysis-placeholder"}
