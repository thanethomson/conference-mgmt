
import unittest
from sort_talks import ConferenceSchedule, Talk


class TestConferenceScheduleFunctionality(unittest.TestCase):
    def test_adding_talks(self):
        schedule = ConferenceSchedule()
        schedule.add_talks([
            Talk("Talk 1, Track 1", 60),
            Talk("Talk 2, Track 1", 60),
            Talk("Talk 3, Track 1", 60),
            Talk("Talk 4, Track 1", 60),
            Talk("Talk 5, Track 1", 60),
            Talk("Talk 6, Track 1", 60),
            Talk("Talk 7, Track 1", 60),
            Talk("Talk 1, Track 2", 60),
            Talk("Talk 2, Track 2", 60),
            Talk("Talk 3, Track 2", 60),
            Talk("Talk 4, Track 2", 60),
            Talk("Talk 5, Track 2", 60),
            Talk("Talk 6, Track 2", 60),
            Talk("Talk 7, Track 2", 60)
        ])

        self.assertEqual(2, len(schedule.tracks))
        self.assertEqual(0, schedule.tracks[0].get_wasted_time())
        self.assertEqual(0, schedule.tracks[1].get_wasted_time())
