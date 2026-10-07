from typing import Callable, Dict, Any, Optional

class ToolRegistry:
    _tools: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, func: Callable, description: str, risk_level: str = "low", requires_approval: bool = False, schema: Optional[Dict] = None):
        cls._tools[name] = {
            "name": name,
            "func": func,
            "description": description,
            "risk_level": risk_level,
            "requires_approval": requires_approval,
            "schema": schema or {}
        }

    @classmethod
    def get_tool(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> Dict[str, Dict[str, Any]]:
        return cls._tools
