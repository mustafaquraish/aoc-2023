#!/usr/bin/env python3

import contextlib
import os
import os
import re
import requests
import shutil
import argparse
from time import perf_counter

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
    exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("--time", "-t", action="store_true")
args = parser.parse_args()

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

commands = []

def run_ocen(file):
    day = re.search(r"(\d+)", file).group(1)
    inp = get_input(day).strip()
    expected = get_expected(day)

    inf = f"./build/{day}.in"
    outf = f"./build/{day}.out"
    exef = f"./build/{day}"

    print(f"[+] Checking {file} ... ", end="", flush=True)
    with open(inf, "w") as fp:
        fp.write(inp)
    cmd(f"ocen {file} -o {exef} -cf '-O3 -march=native -funroll-loops'  > /dev/null")

    cmd(f"{exef} {inf} > {outf}")
    commands.append(f"{exef} {inf} > /dev/null")

    with open(outf) as fp:
        nums = [int(x) for x in re.findall(r"Part .* (\d+)", fp.read())]
    if nums != expected:
        raise Exception(f"Day {day}: Expected {expected}, got {nums}")


os.makedirs("build", exist_ok=True)

fail = False
for d in sorted(glob("src/??.oc")):
    if not os.path.isfile(d): continue
    try:
        run_ocen(d)
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        fail = True

if args.time:
    run_cmd = "\n".join(commands)
    time_cmd = f'time bash -c "{run_cmd}"'

    path = "build/run.sh"
    with open(path, "w") as fp:
        fp.write("#!/usr/bin/env bash\n")
        fp.write(time_cmd)

    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

    print()
    print("Timing execution for all days...")
    cmd(f"./build/run.sh")

if fail:
    exit(1)
    