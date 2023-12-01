import contextlib
import os
import os
import re
import requests

from pathlib import Path
from glob import glob

YEAR = 2023

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def get_session():
    if key := os.environ.get("AOC_SESSION"):
        return key.strip()

    paths = [
        Path.cwd() / ".session",
        Path.home() / ".aocsession",
        Path.home() / "aoc" / "session",
        Path.home() / ".config" / "aoc" / "session",
    ]

    for path in paths:
        if path.exists():
            with path.open() as fp:
                return fp.read().strip()

    print("No session key found anywhere.")
    os.exit(1)

session = requests.Session()
session.cookies.set("session", get_session(), domain=".adventofcode.com")

def get_input(day):
    day = int(day)
    input_url = f"https://adventofcode.com/{YEAR}/day/{day}/input"
    body = session.get(input_url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    })
    if body.status_code != 200:
        raise Exception(f"Failed to get input for day {day}: {body.status_code}")
    return body.text

def get_expected(day):
    day = int(day)
    input_url = f"https://adventofcode.com/{YEAR}/day/{day}"
    body = session.get(input_url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    })
    if body.status_code != 200:
        raise Exception(f"Failed to get input for day {day}: {body.status_code}")
    text = body.text
    matches = re.findall(r"Your puzzle answer was[^\d-]*-?(\d+)", text)
    assert len(matches) == 2, f"Expected 2 answers, got {len(matches)}: {matches}"
    return [int(x) for x in matches]

def cmd(c):
    if os.system(c) != 0:
        raise Exception(f"Command failed: {c}")

def run_day(dir):
    day = os.path.basename(d)
    inp = get_input(day).strip()+"\n"
    expected = get_expected(day)

    print(f"[+] Checking {d} ... ", end="", flush=True)
    with pushd(d):
        with open("in.txt", "w") as fp:
            fp.write(inp)
        cmd("ocen main.oc > /dev/null")
        cmd("./out in.txt > out.txt")
        with open("out.txt") as fp:
            nums = [int(line.split()[-1]) for line in fp]
        cmd("rm out.txt")
    if nums != expected:
        raise Exception(f"Day {day}: Expected {expected}, got {nums}")


fail = False
for d in glob("??"):
    if not os.path.isdir(d): continue
    try:
        run_day(d)
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        fail = True

if fail:
    exit(1)
    