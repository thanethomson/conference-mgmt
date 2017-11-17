#!/usr/bin/env python3

import argparse
import random
import time
import math

__all__ = [
    "Talk",
    "TalkSession",
    "TalkTrack",
    "ConferenceSchedule",
    "main",
    "minutes_to_friendly_time",
    "read_talks_from_file"
]

# Some constants. NOTE: Changing these will necessarily also require some code
# changes, including possibly to the
# ConferenceSchedule.find_best_fit_session_prefer_mornings() function.
DAY_START_HOUR = 9
LUNCH_START_HOUR = 12
LUNCH_END_HOUR = 13
NETWORKING_START_HOUR_MIN = 16
NETWORKING_START_HOUR_MAX = 17
NETWORKING_LEEWAY = NETWORKING_START_HOUR_MAX - NETWORKING_START_HOUR_MIN
HOURS_BEFORE_LUNCH = LUNCH_START_HOUR - DAY_START_HOUR
HOURS_AFTER_LUNCH = NETWORKING_START_HOUR_MAX - LUNCH_END_HOUR
MAX_TALK_DURATION = 60*min(HOURS_BEFORE_LUNCH, HOURS_AFTER_LUNCH)
MORNING_SESSION_DURATION = HOURS_BEFORE_LUNCH*60
AFTERNOON_SESSION_DURATION = HOURS_AFTER_LUNCH*60
TRACK_DURATION = MORNING_SESSION_DURATION + AFTERNOON_SESSION_DURATION


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

    def __init__(self, is_morning_session, track=None, verbose=False):
        self.start_hour = DAY_START_HOUR if is_morning_session else LUNCH_END_HOUR
        self.is_morning_session = is_morning_session
        self.track = track
        self.verbose = verbose
        # how many minutes do we have in this session?
        self.total_time = (MORNING_SESSION_DURATION if is_morning_session else AFTERNOON_SESSION_DURATION)
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
            if self.verbose and self.track:
                print("Added talk \"%s\" to %s session of track %d (now only wasted %d mins)" % (
                    talk.title,
                    "morning" if self.is_morning_session else "afternoon",
                    self.track.track_no,
                    self.wasted_time
                ))
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

    def __init__(self, track_no, verbose=False):
        self.track_no = track_no
        self.verbose = verbose
        self.morning_session = TalkSession(True, track=self, verbose=verbose)
        self.afternoon_session = TalkSession(False, track=self, verbose=verbose)

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
        if len(self.afternoon_session.talks) > 0:
            return self.afternoon_session.talks[-1]
        elif len(self.morning_session.talks) > 0:
            return self.morning_session.talks[-1]
        else:
            return None

    def to_string(self, latest_talk_end_time):
        return (
            ('Track %d\n\n' % self.track_no) +
            ('%s' % self.morning_session) +
            '\n' + self.get_lunchtime_string() + '\n' +
            (('%s\n' % self.afternoon_session) if self.afternoon_session.talks else '') +
            minutes_to_friendly_time(latest_talk_end_time, start_hour=LUNCH_END_HOUR) +
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

    def __init__(self, prefer_mornings=False, verbose=False):
        self.tracks = []
        self.next_track_no = 1
        self.prefer_mornings = prefer_mornings
        self.verbose = verbose

    def add_talks(self, talks):
        """Adds the given collection of talks to this conference schedule. This
        will first clear out any existing talk tracks prior to adding the talks,
        and then add talks according to the Best Fit Decreasing (BFD) algorithm.

        Args:
            talks: A collection of Talk instances to add to the schedule.
        """
        # estimate total talk duration
        total_talks_duration = sum([talk.duration for talk in talks])
        # estimate minimum number of tracks
        est_tracks = int(math.ceil(total_talks_duration / TRACK_DURATION))
        self.tracks = [self.create_track() for i in range(est_tracks)]
        # sort talks according to decreasing duration (Best Fit Decreasing algorithm)
        sorted_talks = sorted(talks, key=lambda talk: -talk.duration)
        for talk in sorted_talks:
            # find the best session into which to insert this talk
            session = self.find_best_fit_session_prefer_mornings(talk) \
                if self.prefer_mornings else self.find_best_fit_session(talk)
            # no space anywhere
            if session is None:
                # add a new track
                self.tracks.append(self.create_track())
                session = self.find_best_fit_session_prefer_mornings(talk) \
                    if self.prefer_mornings else self.find_best_fit_session(talk)
                # paranoia here
                if session is None:
                    raise Exception("Something went horribly wrong")
            if not session.add_talk(talk):
                raise Exception("Something went horribly wrong")

    def get_all_sessions(self):
        for track in self.tracks:
            yield track.morning_session
            yield track.afternoon_session

    def find_best_fit_session(self, talk):
        """Attempts to find the session that best fits the given talk, as per
        the Best Fit Decreasing (BFD) algorithm.
        
        Args:
            talk: The talk that needs a home.
        
        Returns:
            The TalkSession into which to fit this talk.
        """
        best_morning_session, best_afternoon_session = None, None
        min_morning_wasted_time, min_afternoon_wasted_time = TRACK_DURATION, TRACK_DURATION
        for session in self.get_all_sessions():
            wasted_time = session.wasted_time - talk.duration
            if session.is_morning_session:
                if wasted_time >= 0 and wasted_time < min_morning_wasted_time:
                    best_morning_session = session
                    min_morning_wasted_time = wasted_time
            else:
                if wasted_time >= 0 and wasted_time < min_afternoon_wasted_time:
                    best_afternoon_session = session
                    min_afternoon_wasted_time = wasted_time
        # if we have competing morning and afternoon sessions here
        if best_morning_session and best_afternoon_session:
            # if the afternoon session is in an earlier track, prefer it
            if best_afternoon_session.track.track_no < best_morning_session.track.track_no:
                return best_afternoon_session
        # otherwise go for the morning session
        if best_morning_session:
            return best_morning_session
        return best_afternoon_session

    def find_best_fit_session_prefer_mornings(self, talk):
        """Similar to find_best_fit_session(), but prefers to fill up morning
        sessions prior to filling up afternoon ones. This is a natural consequence of
        having afternoon sessions of longer durations than morning ones (given the
        choice of algorithm)."""
        best_session = None
        min_wasted_time = TRACK_DURATION
        for session in self.get_all_sessions():
            wasted_time = session.wasted_time - talk.duration
            if wasted_time >= 0 and wasted_time < min_wasted_time:
                best_session = session
                min_wasted_time = wasted_time
        return best_session

    def create_track(self):
        track = TalkTrack(self.next_track_no, verbose=self.verbose)
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
        return "\n"+("\n\n".join(['%s' % track.to_string(latest_talk.end_time) for track in self.tracks]))

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
        "--shuffle",
        action="store_true",
        help="Shuffles the inputs first before scheduling the talks."
    )
    parser.add_argument(
        "--prefer-mornings",
        action="store_true",
        help="Indicate to prefer to fill up morning sessions before filling " +
            "up the afternoon sessions."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Adds some verbose output about the quality of the solution."
    )
    args = parser.parse_args()
    talks = [talk for talk in read_talks_from_file(args.input_file)]
    if args.shuffle:
        random.seed(time.time())
        talks = random.sample(talks, k=len(talks))

    schedule = ConferenceSchedule(prefer_mornings=args.prefer_mornings, verbose=args.verbose)
    schedule.add_talks(talks)
    print("%s\n" % schedule)

    if args.verbose:
        print("Total wasted time in solution: %d mins\n" % schedule.get_wasted_time())


if __name__ == "__main__":
    main()
