from datetime import datetime
from enum import Enum, auto
from typing import Optional


class SessionEndReason(Enum):
    USER_STOPPED = auto()
    INACTIVITY_LIMIT = auto()
    APP_INTERRUPTION = auto()


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
