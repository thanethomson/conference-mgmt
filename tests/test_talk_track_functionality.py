"""Test cases for checking that we manage talk tracks correctly."""

import unittest
from sort_talks import Talk, TalkTrack


class TestTalkTrackFunctionality(unittest.TestCase):
    def test_adding_talks(self):
        track = TalkTrack(1)
        self.assertTrue(track.add_talk(Talk("Talk 1", 60)))
        self.assertTrue(track.add_talk(Talk("Talk 2", 60)))
        self.assertTrue(track.add_talk(Talk("Talk 3", 60)))
        self.assertTrue(track.add_talk(Talk("Talk 4", 60)))
        self.assertTrue(track.add_talk(Talk("Talk 5", 60)))
        self.assertTrue(track.add_talk(Talk("Talk 6", 60)))

        self.assertEqual("Talk 1", track.morning_session.talks[0].title)
        self.assertEqual("Talk 3", track.morning_session.talks[-1].title)
        self.assertEqual("Talk 4", track.afternoon_session.talks[0].title)
        self.assertEqual("Talk 6", track.afternoon_session.talks[-1].title)

        self.assertEqual(60, track.get_wasted_time())
