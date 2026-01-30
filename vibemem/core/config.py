"""Configuration management for vibemem."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

DEFAULT_CONFIG = {
    "version": 1,
    "token_budgets": {
        "claude-code": 10000,
        "cursor": 6000,
        "copilot": 3000,
        "aider": 4000,
        "windsurf": 5000,
        "cline": 5000,
        "continue": 4000,
        "zed": 4000,
        "default": 4000,
    },
    "compression": {
        "strategy": "smart",  # smart, summarize, truncate, pointer
        "preserve_categories": ["critical", "error", "arch"],
        "summarize_threshold": 0.8,  # compress when at 80% of budget
    },
    "sync": {
        "auto_detect_tools": True,
        "include_global": True,
        "include_errors": True,
        "max_errors": 10,
    },
    "extraction": {
        "model": "claude-haiku",
        "auto_categorize": True,
    },
}


class Config:
    """Configuration manager for vibemem."""

    def __init__(self, data: Dict[str, Any], path: Optional[Path] = None):
        self._data = data
        self._path = path

    @classmethod
    def global_path(cls) -> Path:
        """Get global vibemem directory path."""
        return Path.home() / ".vibemem"

    @classmethod
    def load(cls, project_path: Optional[Path] = None) -> "Config":
        """Load configuration, merging global and project configs."""
        global_config_path = cls.global_path() / "config.yml"
        project_config_path = (project_path or Path.cwd()) / ".vibemem" / "config.yml"

        # Start with defaults
        config = DEFAULT_CONFIG.copy()

        # Layer global config
        if global_config_path.exists():
            with open(global_config_path) as f:
                global_cfg = yaml.safe_load(f) or {}
                config = cls._deep_merge(config, global_cfg)

        # Layer project config
        if project_config_path.exists():
            with open(project_config_path) as f:
                project_cfg = yaml.safe_load(f) or {}
                config = cls._deep_merge(config, project_cfg)

        return cls(config, project_config_path)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def token_budgets(self) -> Dict[str, int]:
        return self._data.get("token_budgets", DEFAULT_CONFIG["token_budgets"])

    @property
    def compression(self) -> Dict[str, Any]:
        return self._data.get("compression", DEFAULT_CONFIG["compression"])

    @property
    def sync(self) -> Dict[str, Any]:
        return self._data.get("sync", DEFAULT_CONFIG["sync"])

    @property
    def extraction(self) -> Dict[str, Any]:
        return self._data.get("extraction", DEFAULT_CONFIG["extraction"])

    def get_budget(self, tool: str) -> int:
        """Get token budget for a specific tool."""
        budgets = self.token_budgets
        return budgets.get(tool, budgets.get("default", 4000))

    def save(self, path: Optional[Path] = None):
        """Save configuration to file."""
        save_path = path or self._path
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w") as f:
                yaml.dump(self._data, f, default_flow_style=False)

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()
