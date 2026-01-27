import unittest
from datetime import datetime, timedelta
from core.engine import CoreEngine, SystemState, MAX_INACTIVITY_SECONDS
from core.session import SessionEndReason

class TestSystemCore(unittest.TestCase):
    def setUp(self):
        self.engine = CoreEngine()

    def test_initial_state_is_idle(self):
        self.assertEqual(self.engine.state, SystemState.IDLE)
        self.assertIsNone(self.engine.active_session)

    def test_start_session_transitions_to_active(self):
        start_time = datetime(2026, 1, 1, 10, 0, 0)
        self.engine.start_session(task="Test Task", start_time=start_time)
        self.assertEqual(self.engine.state, SystemState.ACTIVE)
        self.assertIsNotNone(self.engine.active_session)
        self.assertEqual(self.engine.active_session.start_time, start_time)
        self.assertEqual(self.engine.active_session.task, "Test Task")

    def test_start_session_while_active_is_rejected(self):
        self.engine.start_session(task="First")
        session1 = self.engine.active_session
        self.engine.start_session(task="Second")
        self.assertEqual(self.engine.active_session, session1)
        self.assertEqual(self.engine.active_session.task, "First")

    def test_stop_session_transitions_to_idle(self):
        self.engine.start_session()
        stop_time = datetime(2026, 1, 1, 11, 0, 0)
        self.engine.stop_session(stop_time=stop_time)
        self.assertEqual(self.engine.state, SystemState.IDLE)
        self.assertIsNone(self.engine.active_session)
        self.assertEqual(len(self.engine.completed_sessions), 1)
        self.assertEqual(self.engine.completed_sessions[0].end_time, stop_time)
        self.assertEqual(self.engine.completed_sessions[0].end_reason, SessionEndReason.USER_STOPPED)

    def test_stop_session_while_idle_is_ignored(self):
        self.engine.stop_session()
        self.assertEqual(self.engine.state, SystemState.IDLE)
        self.assertEqual(len(self.engine.completed_sessions), 0)

    def test_inactivity_auto_ends_session(self):
        start_time = datetime(2026, 1, 1, 10, 0, 0)
        self.engine.start_session(start_time=start_time)
        
        # Tick forward by MAX_INACTIVITY_SECONDS
        tick_time = start_time + timedelta(seconds=MAX_INACTIVITY_SECONDS)
        self.engine.tick(current_time=tick_time)
        
        self.assertEqual(self.engine.state, SystemState.IDLE)
        self.assertEqual(len(self.engine.completed_sessions), 1)
        session = self.engine.completed_sessions[0]
        self.assertEqual(session.end_reason, SessionEndReason.INACTIVITY_LIMIT)
        self.assertEqual(session.end_time, tick_time)
        self.assertEqual(session.get_duration_seconds(), MAX_INACTIVITY_SECONDS)

    def test_input_resets_inactivity_timer(self):
        start_time = datetime(2026, 1, 1, 10, 0, 0)
        self.engine.start_session(start_time=start_time)
        
        # Tick forward by half limit
        half_limit_time = start_time + timedelta(seconds=MAX_INACTIVITY_SECONDS // 2)
        self.engine.tick(current_time=half_limit_time)
        self.assertEqual(self.engine.inactivity_timer_seconds, MAX_INACTIVITY_SECONDS // 2)
        
        # Handle input
        self.engine.handle_input()
        self.assertEqual(self.engine.inactivity_timer_seconds, 0)
        
        # Tick forward again - should NOT end yet
        tick_time = half_limit_time + timedelta(seconds=MAX_INACTIVITY_SECONDS // 2)
        self.engine.tick(current_time=tick_time)
        self.assertEqual(self.engine.state, SystemState.ACTIVE)
        
    def test_app_interruption_ends_session(self):
        start_time = datetime(2026, 1, 1, 10, 0, 0)
        self.engine.start_session(start_time=start_time)
        
        interruption_time = start_time + timedelta(minutes=10)
        self.engine.handle_interruption(interruption_time=interruption_time)
        
        self.assertEqual(self.engine.state, SystemState.IDLE)
        self.assertEqual(len(self.engine.completed_sessions), 1)
        session = self.engine.completed_sessions[0]
        self.assertEqual(session.end_reason, SessionEndReason.APP_INTERRUPTION)
        self.assertEqual(session.end_time, interruption_time)

if __name__ == "__main__":
    unittest.main()
