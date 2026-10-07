from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class AgentState(BaseModel):
    goal: str
    status: str = "running" # running, terminated, success, failed
    current_step: int = 0
    max_steps: int = 10
    retry_count: int = 0
    max_retries: int = 2
    last_action: Optional[Dict[str, Any]] = None
    last_observation: Optional[Dict[str, Any]] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    current_url: Optional[str] = None
    current_title: Optional[str] = None
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
