from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class SessionEndReason(Enum):
    USER_STOPPED = 1
    INACTIVITY_LIMIT = 2
    APP_INTERRUPTION = 3


class Session:
    """
    Represents a discrete, user-initiated time-tracking interval.
    Authoritative definition in docs/02_definition_of_terms.md and docs/03_system_core.md.
    """

    def __init__(self, start_time: datetime, task: str = ""):
        self.start_time: datetime = start_time
        self.end_time: Optional[datetime] = None
        self.task: str = task
        self.end_reason: Optional[SessionEndReason] = None
        self.max_inactivity_reached_seconds: int = 0
        self._is_immutable: bool = False

    def end(self, end_time: datetime, reason: SessionEndReason, inactivity_seconds: int = 0):
        if self._is_immutable:
            return

        self.end_time = end_time
        self.end_reason = reason
        self.max_inactivity_reached_seconds = inactivity_seconds
        self._is_immutable = True

    @property
    def is_complete(self) -> bool:
        return self._is_immutable

    def get_duration_seconds(self) -> int:
        """
        SESSION TIME is calculated as the difference between SESSION END TIME and SESSION START TIME.
        Includes periods of user inactivity.
        """
        if not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return int(delta.total_seconds())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "task": self.task,
            "end_reason": self.end_reason.value if self.end_reason else None,
            "max_inactivity_reached_seconds": self.max_inactivity_reached_seconds,
            "is_immutable": self._is_immutable
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        start_time = datetime.fromisoformat(data["start_time"])
        session = cls(start_time=start_time, task=data.get("task", ""))
        if data.get("end_time"):
            session.end_time = datetime.fromisoformat(data["end_time"])
        if data.get("end_reason"):
            session.end_reason = SessionEndReason(data["end_reason"])
        session.max_inactivity_reached_seconds = data.get("max_inactivity_reached_seconds", 0)
        session._is_immutable = data.get("is_immutable", False)
        return session
