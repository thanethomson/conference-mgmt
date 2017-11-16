#!/usr/bin/env python3

import argparse
import itertools
import random
import time

__all__ = [
    "Talk",
    "TalkSession",
    "TalkTrack",
    "ConferenceSchedule",
    "main",
    "minutes_to_friendly_time",
    "read_talks_from_file"
]

# Some constants
DAY_START_HOUR = 9
LUNCH_START_HOUR = 12
LUNCH_END_HOUR = 13
NETWORKING_START_HOUR_MIN = 16
NETWORKING_START_HOUR_MAX = 17
HOURS_BEFORE_LUNCH = LUNCH_START_HOUR - DAY_START_HOUR
HOURS_AFTER_LUNCH = NETWORKING_START_HOUR_MAX - LUNCH_END_HOUR
MAX_TALK_DURATION = 60*min(HOURS_BEFORE_LUNCH, HOURS_AFTER_LUNCH)


def minutes_to_friendly_time(minutes, start_hour=0):
    """Converts the given number of minutes to a friendly time string."""
    hour = start_hour + (minutes // 60)
    minutes = minutes % 60
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return "%.2d:%.2d%s" % (
        hour_12,
        minutes,
        "AM" if hour < 12 else "PM"
    )


class Talk:
    """Represents a single talk for our conference."""

    def __init__(self, title, duration, start_time=None):
        """Constructor.

        Args:
            title: The title of the talk (string).
            duration: The duration of the talk in minutes (int).
            start_time: The start time (in minutes) of this talk relative to
                the start of the session.
        """
        self.title = title
        self.duration = duration
        self.start_time, self.end_time = None, None
        if start_time is not None:
            self.start_at(start_time)

    def start_at(self, minutes):
        self.start_time = minutes
        self.end_time = minutes + self.duration
        return self

    def get_friendly_duration(self):
        return "lightning" if self.duration == 5 else ("%dmin" % self.duration)

    def to_string(self, session_start_hour):
        return "%s %s %s" % (
            minutes_to_friendly_time(self.start_time, start_hour=session_start_hour),
            self.title,
            self.get_friendly_duration()
        )

    @classmethod
    def parse(cls, source_str):
        """Parses the given string into a Talk instance.

        Args:
            source_str: A string containing the details of the talk.
        
        Returns:
            On success, a Talk instance. On failure, raises an exception.
        """
        parts = source_str.split(' ')
        if len(parts) < 2:
            raise Exception("Invalid talk format: %s" % source_str)
        duration = parts[-1]
        if duration != 'lightning' and not duration.endswith('min'):
            raise Exception("Invalid duration for talk: %s" % source_str)
        # convert to minutes
        duration = 5 if duration == 'lightning' else int(duration.replace('min', ''))
        if duration > MAX_TALK_DURATION:
            raise Exception("Talk exceeds maximum duration: %s (maximum is %d mins)" % (
                source_str,
                MAX_TALK_DURATION
            ))
        return Talk(' '.join(parts[:-1]), duration)

    @classmethod
    def copy_of(cls, other):
        talk = Talk(other.title, other.duration)
        talk.start_time = other.start_time
        talk.end_time = other.end_time
        return talk


class TalkSession:
    """Represents a single session (either morning or afternoon) that can
    contain talks. In the bin packing algorithm, this represents a bin whose
    contents we want to maximise."""

    def __init__(self, is_morning_session):
        self.start_hour = DAY_START_HOUR if is_morning_session else LUNCH_END_HOUR
        self.is_morning_session = is_morning_session
        # how many minutes do we have in this session?
        self.total_time = (HOURS_BEFORE_LUNCH if is_morning_session else HOURS_AFTER_LUNCH)*60
        self.talks = []
        # this we want to maximise
        self.used_time = 0
        self.wasted_time = self.total_time

    def has_space(self):
        return (self.used_time < self.total_time)

    def use_time(self, duration):
        self.used_time += duration
        self.wasted_time -= duration
    
    def add_talk(self, talk):
        """Attempts to add the given talk to this session.
        
        Args:
            talk: The talk to add to this session.

        Returns:
            True if the talk was successfully added, otherwise False.
        """
        last_talk_end_time = self.talks[-1].end_time if len(self.talks) > 0 else 0
        # if the talk fits into this session
        if last_talk_end_time + talk.duration <= self.total_time:
            self.talks.append(talk.start_at(last_talk_end_time))
            self.use_time(talk.duration)
            return True
        # no more space
        return False

    def __str__(self):
        return "\n".join(["%s" % talk.to_string(self.start_hour) for talk in self.talks])

    @classmethod
    def copy_of(cls, other):
        session = TalkSession(other.is_morning_session)
        session.talks = [Talk.copy_of(talk) for talk in other.talks]
        session.used_time = other.used_time
        session.wasted_time = other.wasted_time
        return session


class TalkTrack:
    """Represents a single track, which contains a morning and afternoon
    talk session."""

    def __init__(self, track_no):
        self.track_no = track_no
        self.morning_session = TalkSession(True)
        self.afternoon_session = TalkSession(False)

    def add_talk(self, talk):
        added = False
        if self.morning_session.has_space():
            added = self.morning_session.add_talk(talk)
        if not added and self.afternoon_session.has_space():
            added = self.afternoon_session.add_talk(talk)
        return added

    def get_lunchtime_string(self):
        hour = LUNCH_START_HOUR
        return "%s Lunch" % minutes_to_friendly_time(0, start_hour=LUNCH_START_HOUR)

    def get_wasted_time(self):
        return self.morning_session.wasted_time + self.afternoon_session.wasted_time

    def get_latest_talk(self):
        return self.afternoon_session.talks[-1]

    def to_string(self, latest_talk_end_time):
        return (
            ('Track %d\n\n' % self.track_no) +
            ('%s' % self.morning_session) +
            '\n' + self.get_lunchtime_string() + '\n' +
            ('%s' % self.afternoon_session) +
            '\n' + minutes_to_friendly_time(latest_talk_end_time, start_hour=LUNCH_END_HOUR) +
            ' Networking Event'
        )

    @classmethod
    def copy_of(cls, other):
        track = TalkTrack(other.track_no)
        track.morning_session = TalkSession.copy_of(other.morning_session)
        track.afternoon_session = TalkSession.copy_of(other.afternoon_session)
        return track


class ConferenceSchedule:
    """Allows us to organise our talks into a schedule with multiple tracks,
    giving additional information about the schedule to help with finding the
    optimal schedule later."""

    def __init__(self):
        self.tracks = []
        self.next_track_no = 1

    def add_talks(self, talks):
        self.tracks = []
        track = self.create_track()
        for talk in talks:
            added = False
            while not added:
                added = track.add_talk(talk)
                if not added:
                    track = self.create_track()

    def create_track(self):
        track = TalkTrack(self.next_track_no)
        self.tracks.append(track)
        self.next_track_no += 1
        return track

    def get_latest_talk(self):
        return max(
            [track.get_latest_talk() for track in self.tracks],
            key=lambda talk: talk.end_time
        )

    def get_wasted_time(self):
        return sum([track.get_wasted_time() for track in self.tracks])

    def __str__(self):
        latest_talk = self.get_latest_talk()
        return "\n\n".join(['%s' % track.to_string(latest_talk.end_time) for track in self.tracks])

    @classmethod
    def copy_of(cls, other):
        schedule = ConferenceSchedule()
        schedule.tracks = [TalkTrack.copy_of(track) for track in other.tracks]
        schedule.next_track_no = other.next_track_no
        return schedule


def read_talks_from_file(filename):
    """Reads all of the talks from the given file.

    Args:
        filename: The name of the file from which to read the talks (one per line).
    
    Returns:
        An iterator which yields Talk instances, parsed from each non-empty
        line of the given input file.
    """
    with open(filename, "rt", encoding="utf-8") as inf:
        for line in inf:
            stripped = line.strip()
            if stripped and len(stripped) > 0:
                yield Talk.parse(stripped)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="A text file from which to read the list of talks (one per line)."
    )
    parser.add_argument(
        "--max-permutations",
        type=int,
        default=100000,
        help="The maximum number of permutations to allow before forcibly " +
            "deciding on a winner (default: 100000). Set to -1 to process " +
            "all possible permutations (could take very, very long)."
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffles the inputs first before running through the various " +
            "possible permutations."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show more verbose information on the output as to the winning " +
            "solution."
    )
    args = parser.parse_args()
    talks = [talk for talk in read_talks_from_file(args.input_file)]
    if args.shuffle:
        random.seed(time.time())
        talks = random.sample(talks, k=len(talks))
    best_schedule = None
    min_tracks = len(talks)
    min_wasted_time = sum([talk.duration for talk in talks])

    perm_counter = 0

    for talk_perm in itertools.permutations(talks):
        schedule = ConferenceSchedule()
        schedule.add_talks(talk_perm)
        
        wasted_time = schedule.get_wasted_time()
        track_count = len(schedule.tracks)
        if track_count < min_tracks or wasted_time < min_wasted_time:
            # make a deep copy of the conference schedule
            best_schedule = ConferenceSchedule.copy_of(schedule)
            min_tracks = track_count
            min_wasted_time = wasted_time

        perm_counter += 1
        if args.max_permutations > -1 and perm_counter >= args.max_permutations:
            break

        if args.verbose and perm_counter % 1000 == 0:
            print("Processed %d permutations so far" % perm_counter)
    
    if args.verbose:
        print("\nTotal permutations tested          : %d" % perm_counter)
        print("Wasted time in winning permutation : %d mins\n" % min_wasted_time)

    print("%s\n" % best_schedule)


if __name__ == "__main__":
    main()
