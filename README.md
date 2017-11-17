# Conference Management

## Overview
This is a proof-of-concept solution to the problem of formulating an optimal
conference schedule, given a set of talks with talk durations. More generally,
this is a potential solution to the [NP-hard](https://en.wikipedia.org/wiki/NP-hardness)
[bin packing problem](https://en.wikipedia.org/wiki/Bin_packing_problem). It
uses a simple brute force approach, including optional randomness, to attempt
to optimise how talks are packed into parallel tracks.

Ultimately, it tries to minimise the number of tracks, as well as the amount
of time wasted (i.e. time from the last morning session talk until lunch, as
well as the time from the last afternoon session talk until the networking
event).

The code organises talks into a morning session (between 09h00 and 12h00),
a lunch break (always 12h00 to 13h00), an afternoon session (from 13h00 to
anywhere between 16h00 and 17h00), as well as a networking event. The
networking event, logically, should start at the same time from the perspective
of all tracks, and should start at the end of the talk that ends the latest
across all tracks.

## Requirements
Only [Python 3](https://www.python.org/downloads/) is required to run this
code.

## Running
There is a single script in the root folder called `sort_talks.py`, which is
executable given a particular version of Python. Both examples below assume
that a `python3` or `python` (v3) executable is available on your system path.

```bash
# Linux/macOS
> ./sort_talks.py

# Windows
> python sort_talks.py
```

To run this inside a virtual environment (the recommended approach for Python
applications in general):

```bash
> python3 -m venv venv
> source ./venv/bin/activate
```

## Usage
The `sort_talks.py` script can be used as follows:

```
usage: sort_talks.py [-h] [--max-permutations MAX_PERMUTATIONS] [--shuffle]
                     [-v]
                     input_file

positional arguments:
  input_file            A text file from which to read the list of talks (one
                        per line).

optional arguments:
  -h, --help            show this help message and exit
  --max-permutations MAX_PERMUTATIONS
                        The maximum number of permutations to allow before
                        forcibly deciding on a winner (default: 100000). Set
                        to -1 to process all possible permutations (could take
                        very, very long).
  --shuffle             Shuffles the inputs first before running through the
                        various possible permutations.
  -v, --verbose         Show more verbose information on the output as to the
                        winning solution.
```

## Usage Examples
Some examples as to how to use the script (Linux/macOS):

```bash
# Simple execution, 100000 permutations
> ./sort_talks.py testcase1.txt

# Shuffle the talks prior to optimising
> ./sort_talks.py --shuffle testcase1.txt

# Run with fewer permutations for quicker results
> ./sort_talks.py --max-permutations 1000 testcase1.txt

# Increase output verbosity, with all the options
> ./sort_talks.py -v --shuffle --max-permutations 1000 testcase1.txt
```

## Input Format
Each line of the input text file should contain the title of a talk, followed
by its duration. Durations are either in minutes (with `min` as a suffix),
or `lightning` (5mins). For example:

```
Using open to drive change 15min
The blockchain and open source: The new world order 15min
How InnerSource is like FLOSSing lightning
Evolving the JavaScript ecosystem lightning
Brilliant pebbles 15min
Distributed consensus: Making impossible possible 40min
```

## Sample Output
For `testcase1.txt` (pre-shuffled, 10,000 permutations):

```
Track 1

09:00AM Communicating Over Distance 60min
10:00AM Clojure Ate Scala (on my project) 45min
10:45AM Common Ruby Errors 45min
11:30AM Programming in the Boondocks of Seattle 30min
12:00PM Lunch
01:00PM Accounting-Driven Development 45min
01:45PM Ruby Errors from Mismatched Gem Versions 45min
02:30PM Rails for Python Developers lightning
02:35PM Lua for the Masses 30min
03:05PM User Interface CSS in Rails Apps 30min
03:35PM Ruby vs. Clojure for Back-End Development 30min
04:05PM Pair Programming vs Noise 45min
04:50PM Networking Event

Track 2

09:00AM A World Without HackerNews 30min
09:30AM Sit Down and Write 30min
10:00AM Rails Magic 60min
11:00AM Woah 30min
12:00PM Lunch
01:00PM Overdoing it in Python 45min
01:45PM Writing Fast Tests Against Enterprise Rails 60min
02:45PM Ruby on Rails Legacy App Maintenance 60min
03:45PM Ruby on Rails: Why We Should Move On 60min
04:50PM Networking Event
```

## Unit Tests
Unit tests are located in the `tests` folder. To run them, from the project
directory, run the following command:

```bash
> python3 -m unittest discover
```

There should be 14 tests in total at present that should execute.
