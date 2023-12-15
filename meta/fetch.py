#!/usr/bin/env python3

################################################################################
#                      Fetch AOC input / sample input
# 
# This script will download the input for the current day, and will also attempt
# to scrape the sample input from the AoC problem definition for the day. To use
# this, you will need to get your Session cookie from the AoC website, which
# can be acquired from your browser's dev tools. Place this session value in any
# of the following places (checked in this order):
#
#      - As the environment variable AOC_SESSION
#      - In an arbitrary file which is passed in through the CLI
#      - <cwd>/.session
#      - ~/.aocsession
#      - ~/aoc/session
#      - ~/.config/aoc/session
#
# Run the script as follows:
#       python3 fetch.py [--sample] [--session <session_file>] <year> <day> [-o <output_file>]
#
# The following non-standard libraries are required: (requests, beautifulsoup4)
#       pip install requests beautifulsoup4
#
################################################################################

from argparse import ArgumentParser
from functools import cache
from pathlib import Path
import os
import re
import requests

@cache
def get_session(session_file=None):
    if key := os.environ.get("AOC_SESSION"):
        return key.strip()

    paths = [
        Path.cwd() / ".session",
        Path.home() / ".aocsession",
        Path.home() / "aoc" / "session",
        Path.home() / ".config" / "aoc" / "session",
    ]
    if session_file is not None:
        paths = [session_file, *paths]

    for path in paths:
        if path.exists():
            with path.open() as fp:
                return fp.read().strip()

    print("No session key found anywhere.")
    os.exit(1)


def get_input(year, day, session_file=None):
    session = requests.Session()
    session.cookies.set("session", get_session(session_file), domain=".adventofcode.com")

    input_url = f"https://adventofcode.com/{year}/day/{day}/input"
    body = session.get(input_url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    })
    if body.status_code != 200:
        print(f"[-] Could not download {input_url}.")
        return None

    return body.text.rstrip()


def get_expected(year, day, session_file=None):
    session = requests.Session()
    session.cookies.set("session", get_session(session_file), domain=".adventofcode.com")

    input_url = f"https://adventofcode.com/{year}/day/{day}"
    body = session.get(input_url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    })
    if body.status_code != 200:
        raise Exception(f"Failed to get input for day {day}: {body.status_code}")
    text = body.text
    matches = re.findall(r"Your puzzle answer was[^\d-]*-?(\d+)", text)
    assert len(matches) == 2, f"Expected 2 answers, got {len(matches)}: {matches}"
    return '\n'.join(matches)


def get_sample(year, day, session_file=None):
    from bs4 import BeautifulSoup

    response = requests.get(f"https://adventofcode.com/{year}/day/{day}")
    parser = BeautifulSoup(response.text, 'html.parser')
    tags = parser.find_all(["p", "pre"])
    
    found_marker = False
    sample_text = None
    for t in tags:
        if t.name == "p":
            if "(your puzzle input)" in t.text:
                found_marker = True
        if found_marker and t.name == "pre":
            print("Found sample input.")
            sample_text = t.text
            break
    
    if sample_text is None:
        print("[-] Could not find sample input.")
        return

    return sample_text


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("year", type=int, help="Year of the Advent of Code")
    parser.add_argument("day", type=int, help="Day of the Advent of Code")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file", required=False)
    parser.add_argument("--sample", "-s", action="store_true", help="Fetch sample input instead of full input")
    parser.add_argument("--expected", "-e", action="store_true", help="Fetch expected output instead of input")
    parser.add_argument("--session", type=str, help="Custom session file", default=None)
    args = parser.parse_args()

    assert not (args.sample and args.expected), "Cannot fetch both sample and expected input."

    if args.expected:
        text = get_expected(args.year, args.day, args.session)
    elif args.sample:
        text = get_sample(args.year, args.day, args.session)
    else:
        text = get_input(args.year, args.day, args.session)

    if text is None:
        exit(1)
    
    if args.output is None:
        print(text)
        exit(0)
    
    with open(args.output, "w") as fp:
        fp.write(text)

    print(f"[+] Wrote input to {args.output}.")
