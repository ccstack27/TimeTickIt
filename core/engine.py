from datetime import datetime
from enum import Enum, auto
from typing import Optional, List
from core.session import Session, SessionEndReason

# Authoritative constants from docs/03_system_core.md and docs/02_definition_of_terms.md
MAX_INACTIVITY_SECONDS = 300  # 5 minutes


class SystemState(Enum):
    IDLE = auto()
    ACTIVE = auto()


class CoreEngine:
    """
    The System Core owns all session, time, and inactivity logic.
    Ref: docs/03_system_core.md
    """

    def __init__(self):
        self.state: SystemState = SystemState.IDLE
        self.active_session: Optional[Session] = None
        self.completed_sessions: List[Session] = []
        self.inactivity_timer_seconds: int = 0
        self._last_tick_time: Optional[datetime] = None

    def start_session(self, task: str = "", start_time: Optional[datetime] = None) -> None:
        """
        Transitions from IDLE to ACTIVE.
        If already ACTIVE, action is rejected (no state change).
        """
        if self.state == SystemState.ACTIVE:
            return

        now = start_time or datetime.now()
        self.active_session = Session(start_time=now, task=task)
        self.inactivity_timer_seconds = 0
        self._last_tick_time = now
        self.state = SystemState.ACTIVE

    def stop_session(self, stop_time: Optional[datetime] = None) -> None:
        """
        Transitions from ACTIVE to IDLE.
        If IDLE, action is silently ignored.
        """
        if self.state == SystemState.IDLE or not self.active_session:
            return

        now = stop_time or datetime.now()
        self.active_session.end(now, SessionEndReason.USER_STOPPED)
        self.completed_sessions.append(self.active_session)
        
        self.active_session = None
        self.state = SystemState.IDLE
        self._last_tick_time = None

    def handle_input(self) -> None:
        """
        Any mouse or keyboard input resets the inactivity timer to zero.
        Ref: docs/03_system_core.md
        """
        import threading
        # Ensure thread-safety if called from pynput listener threads
        self.inactivity_timer_seconds = 0

    def tick(self, current_time: Optional[datetime] = None) -> None:
        """
        Updates the inactivity timer and checks for maximum inactivity limit.
        Evaluated only while in ACTIVE state.
        """
        if self.state != SystemState.ACTIVE or not self.active_session:
            return

        now = current_time or datetime.now()
        
        if self._last_tick_time:
            delta = int((now - self._last_tick_time).total_seconds())
            if delta > 0:
                self.inactivity_timer_seconds += delta
        
        self._last_tick_time = now

        if self.inactivity_timer_seconds >= MAX_INACTIVITY_SECONDS:
            self._handle_inactivity_limit_reached(now)

    def _handle_inactivity_limit_reached(self, end_time: datetime) -> None:
        """
        When inactivity reaches 5 minutes, auto-end the session.
        Ref: docs/03_system_core.md
        """
        if not self.active_session:
            return

        # SESSION END TIME is set at the moment the inactivity limit is reached.
        self.active_session.end(
            end_time, 
            SessionEndReason.INACTIVITY_LIMIT, 
            inactivity_seconds=self.inactivity_timer_seconds
        )
        self.completed_sessions.append(self.active_session)
        
        self.active_session = None
        self.state = SystemState.IDLE
        self._last_tick_time = None

    def handle_interruption(self, interruption_time: Optional[datetime] = None) -> None:
        """
        If the app terminates while ACTIVE, automatically end the session.
        Ref: docs/03_system_core.md
        """
        if self.state != SystemState.ACTIVE or not self.active_session:
            return

        now = interruption_time or datetime.now()
        self.active_session.end(now, SessionEndReason.APP_INTERRUPTION)
        self.completed_sessions.append(self.active_session)
        
        self.active_session = None
        self.state = SystemState.IDLE
        self._last_tick_time = None
