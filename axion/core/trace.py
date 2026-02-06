from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class TraceStep(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str
    details: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReasoningTrace(BaseModel):
    steps: List[TraceStep] = Field(default_factory=list)

    def add_step(self, action: str, details: str, metadata: Dict[str, Any] = None):
        self.steps.append(TraceStep(action=action, details=details, metadata=metadata or {}))

    def __str__(self):
        return "\n".join([f"[{s.timestamp.strftime('%H:%M:%S')}] {s.action}: {s.details}" for s in self.steps])
