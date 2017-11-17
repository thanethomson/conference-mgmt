# Conference Management

## Overview
This is a proof-of-concept solution to the problem of formulating an optimal
conference schedule, given a set of talks with talk durations. More generally,
this is a potential solution to the [NP-hard](https://en.wikipedia.org/wiki/NP-hardness)
[bin packing problem](https://en.wikipedia.org/wiki/Bin_packing_problem). It
uses the simple [Best Fit Decreasing (BFD)](https://en.wikipedia.org/wiki/Bin_packing_problem#Analysis_of_approximate_algorithms)
algorithm, along with a random pre-shuffle, to get decent results quickly.
The random pre-shuffle is largely for aesthetic purposes (reorganising talks of
equal lengths).

Some modification of the algorithm was necessary to account for
the uneven bin sizes (the morning and afternoon talk sessions are not the same
duration, and a choice was made to rather fully pack one track's morning and
afternoon session prior to packing the next track).

[More optimal solutions exist](http://www.aaai.org/Papers/AAAI/2002/AAAI02-110.pdf),
but for practical purposes BFD seems adequate.

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
usage: sort_talks.py [-h] [--shuffle] [--prefer-mornings] [-v] input_file

positional arguments:
  input_file         A text file from which to read the list of talks (one per
                     line).

optional arguments:
  -h, --help         show this help message and exit
  --shuffle          Shuffles the inputs first before scheduling the talks.
  --prefer-mornings  Indicate to prefer to fill up morning sessions before
                     filling up the afternoon sessions.
  -v, --verbose      Adds some verbose output about the quality of the
                     solution.
```

## Usage Examples
Some examples as to how to use the script (Linux/macOS):

```bash
> ./sort_talks.py testcase1.txt

# Shuffle the talks prior to optimising
> ./sort_talks.py --shuffle testcase1.txt

# Prefer filling up morning sessions prior to afternoon ones (seems to
# give a better aesthetic to the schedule, and keeps afternoon talks shorter,
# which could be beneficial in terms of people's attention spans)
> ./sort_talks.py --shuffle --prefer-mornings testcase1.txt
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
For `testcase1.txt` (pre-shuffled):

```
Track 1

09:00AM Ruby on Rails: Why We Should Move On 60min
10:00AM Communicating Over Distance 60min
11:00AM Rails Magic 60min
12:00PM Lunch
01:00PM Ruby on Rails Legacy App Maintenance 60min
02:00PM Writing Fast Tests Against Enterprise Rails 60min
03:00PM Clojure Ate Scala (on my project) 45min
03:45PM Accounting-Driven Development 45min
04:30PM Programming in the Boondocks of Seattle 30min
05:00PM Networking Event

Track 2

09:00AM Pair Programming vs Noise 45min
09:45AM Ruby Errors from Mismatched Gem Versions 45min
10:30AM Overdoing it in Python 45min
11:15AM Common Ruby Errors 45min
12:00PM Lunch
01:00PM Sit Down and Write 30min
01:30PM Lua for the Masses 30min
02:00PM User Interface CSS in Rails Apps 30min
02:30PM Woah 30min
03:00PM Ruby vs. Clojure for Back-End Development 30min
03:30PM A World Without HackerNews 30min
04:00PM Rails for Python Developers lightning
05:00PM Networking Event
```

## Unit Tests
Unit tests are located in the `tests` folder. To run them, from the project
directory, run the following command:

```bash
> python3 -m unittest discover
```

There should be 14 tests in total at present that should execute.
