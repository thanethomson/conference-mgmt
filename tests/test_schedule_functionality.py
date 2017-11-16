
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
        self.assertEqual("Talk 1, Track 1", schedule.tracks[0].morning_session.talks[0].title)
        self.assertEqual("Talk 7, Track 1", schedule.tracks[0].afternoon_session.talks[-1].title)
        self.assertEqual("Talk 1, Track 2", schedule.tracks[1].morning_session.talks[0].title)
        self.assertEqual("Talk 7, Track 2", schedule.tracks[1].afternoon_session.talks[-1].title)
