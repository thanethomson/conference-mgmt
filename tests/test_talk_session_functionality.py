"""Test cases to ensure the talk session management/ordering works as
expected."""

import unittest
from sort_talks import Talk, TalkSession


class TestTalkSessionFunctionality(unittest.TestCase):
    def test_morning_session_adding_talks(self):
        session = TalkSession(True)
        self.assertTrue(session.add_talk(Talk("Talk 1", 60)))
        self.assertTrue(session.add_talk(Talk("Talk 2", 60)))
        self.assertTrue(session.add_talk(Talk("Talk 3", 60)))
        # should be no more space for this one
        self.assertFalse(session.add_talk(Talk("Talk 4", 5)))

        # check the talk start/end times
        self.assertEqual(0, session.talks[0].start_time)
        self.assertEqual(60, session.talks[0].end_time)
        self.assertEqual(60, session.talks[1].start_time)
        self.assertEqual(120, session.talks[1].end_time)
        self.assertEqual(120, session.talks[2].start_time)
        self.assertEqual(180, session.talks[2].end_time)
    
    def test_afternoon_session_adding_talks(self):
        session = TalkSession(False)
        self.assertTrue(session.add_talk(Talk("Talk 1", 60)))
        self.assertTrue(session.add_talk(Talk("Talk 2", 60)))
        self.assertTrue(session.add_talk(Talk("Talk 3", 60)))
        self.assertTrue(session.add_talk(Talk("Talk 4", 60)))
        # should be no more space for this one
        self.assertFalse(session.add_talk(Talk("Talk 5", 5)))

        # check the talk start/end times
        self.assertEqual(0, session.talks[0].start_time)
        self.assertEqual(60, session.talks[0].end_time)
        self.assertEqual(60, session.talks[1].start_time)
        self.assertEqual(120, session.talks[1].end_time)
        self.assertEqual(120, session.talks[2].start_time)
        self.assertEqual(180, session.talks[2].end_time)
        self.assertEqual(180, session.talks[3].start_time)
        self.assertEqual(240, session.talks[3].end_time)

    def test_session_wasted_time_calculation(self):
        session = TalkSession(True)
        self.assertEqual(180, session.wasted_time)
        session.add_talk(Talk("Talk 1", 60))
        self.assertEqual(120, session.wasted_time)
        session.add_talk(Talk("Talk 2", 45))
        self.assertEqual(75, session.wasted_time)
