#!/usr/bin/env python3

import os
import re
import subprocess
from glob import glob

YEAR = 2023

def cmd(c):
    return subprocess.check_output(c, shell=True, text=True)


def run_ocen(file):
    day = re.search(r"(\d+)", file).group(1)

    inf = f"./build/{day}.in"
    outf = f"./build/{day}.out"
    exef = f"./build/{day}"

    print(f"[+] Checking {file} ... ", end="", flush=True)
    if not os.path.isfile(inf):
        cmd(f"./meta/fetch.py {YEAR} {day} -o {inf}")
    cmd(f"ocen {file} -o {exef} -cf '-O3 -march=native -funroll-loops -Wno-unused-result'")

    out_str = cmd(f"{exef} {inf}")
    nums = [int(x) for x in re.findall(r"Part .* (\d+)", out_str)]

    expected_str = cmd(f"./meta/fetch.py {YEAR} {day} --expected")
    expected = [int(x) for x in expected_str.split()]

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

if fail:
    exit(1)
    