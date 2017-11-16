"""Test cases to ensure talk-related functionality (parsing, setting of times)
works as intended."""

import unittest
from sort_talks import Talk, MAX_TALK_DURATION


class TalkParsingTestCase(unittest.TestCase):
    def test_parsing_talk_with_specific_time(self):
        talk = Talk.parse("Writing Fast Tests Against Enterprise Rails 60min")
        self.assertEqual("Writing Fast Tests Against Enterprise Rails", talk.title)
        self.assertEqual(60, talk.duration)

    def test_parsing_lightning_talk(self):
        talk = Talk.parse("Rails for Python Developers lightning")
        self.assertEqual("Rails for Python Developers", talk.title)
        self.assertEqual(5, talk.duration)

    def test_parsing_non_string(self):
        with self.assertRaises(Exception):
            Talk.parse(12345)
    
    def test_parsing_talk_with_missing_time(self):
        with self.assertRaises(Exception):
            Talk.parse("Some Talk Without a Time")

    def test_parsing_talk_with_invalid_time(self):
        with self.assertRaises(Exception):
            Talk.parse("Some Talk With an Invalid Time 2hrs")

    def test_parsing_incredibly_long_talk(self):
        with self.assertRaises(Exception):
            Talk.parse("A Very Long Talk %dmin" % (MAX_TALK_DURATION+1))


class TalkTimingTestCase(unittest.TestCase):
    def test_setting_morning_talk_start_times(self):
        talk = Talk("Sample Talk", 30)
        talk.start_at(30)
        self.assertEqual("09:30AM Sample Talk 30min", talk.to_string(9))
        talk.start_at(60)
        self.assertEqual("10:00AM Sample Talk 30min", talk.to_string(9))

    def test_setting_afternoon_talk_start_times(self):
        talk = Talk("Sample Talk", 30)
        talk.start_at(30)
        self.assertEqual("12:30PM Sample Talk 30min", talk.to_string(12))
        talk.start_at(60)
        self.assertEqual("01:00PM Sample Talk 30min", talk.to_string(12))
