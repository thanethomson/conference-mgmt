"""Tests utility functions."""

import unittest
from sort_talks import minutes_to_friendly_time


class TestUtilityFunctions(unittest.TestCase):
    def test_minutes_to_friendly_time(self):
        self.assertEqual("09:00AM", minutes_to_friendly_time(0, 9))
        self.assertEqual("10:00AM", minutes_to_friendly_time(0, 10))
        self.assertEqual("11:00AM", minutes_to_friendly_time(0, 11))
        self.assertEqual("12:00PM", minutes_to_friendly_time(0, 12))
        self.assertEqual("01:00PM", minutes_to_friendly_time(0, 13))
        self.assertEqual("02:00PM", minutes_to_friendly_time(0, 14))
        self.assertEqual("03:00PM", minutes_to_friendly_time(0, 15))
        self.assertEqual("04:00PM", minutes_to_friendly_time(0, 16))
        self.assertEqual("05:00PM", minutes_to_friendly_time(0, 17))
