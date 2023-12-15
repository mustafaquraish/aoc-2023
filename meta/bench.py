#!/usr/bin/env python3

import os
import re
import subprocess
import shutil
import textwrap
from glob import glob
from time import perf_counter

YEAR = 2023

def cmd(c):
    return subprocess.check_output(c, shell=True, text=True)

os.makedirs("build", exist_ok=True)

def create_benchmark(days):
    # Download input
    print("[+] Downloading inputs: ", end="", flush=True)
    for day in days:
        file = f"build/{day:02d}.in"
        if not os.path.exists(file):
            cmd(f"./meta/fetch.py {YEAR} {day:02d} -o {file}")
        print(".", end="", flush=True)
    print()

    with open("build/src/run_all.oc", "w") as fp:
        for day in days:
            fp.write(f"import .day{day:02}\n")
        fp.write("\n")

        prelude = textwrap.dedent("""
        def call_fn(f: fn(i32,&str), inp: str) {
            let argv: [str; 2]
            argv[0] = "dummy"
            argv[1] = inp
            f(2, argv)
        }

        def main(argc: i32, argv: &str) {
            assert argc > 1, "no input directory provided"
            let dir = argv[1]
        """)
        fp.write(prelude)

        for day in days:
            fp.write(f"    call_fn(day{day:02}::main, `{{dir}}/{day:02}.in`)\n")

        fp.write("}\n")

    print("[+] Compiling build/src/run_all.oc")
    cmd("ocen build/src/run_all.oc -o build/run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result'")


def run_benchmark():
    times = []
    RUNS = 20
    for i in range(RUNS):
        start = perf_counter()
        cmd("./build/run_all ./build")
        end = perf_counter()
        if i > 2:
            times.append(end - start)
        print(f"[+] Running benchmark: {i+1:>3d} /{RUNS:>3d}\r", end="", flush=True)
    avg = sum(times) / len(times)
    print()

    print(f"[+] Estimated time: {avg:.3f}s")

files = sorted(glob("src/??.oc"))
days = [int(re.search(r"(\d+)", f).group(1)) for f in files]

shutil.rmtree("build/src", ignore_errors=True)
shutil.copytree("src", "build/src")
for day in days:
    shutil.move(f"build/src/{day:02}.oc", f"build/src/day{day:02}.oc")

create_benchmark(days)
run_benchmark()

shutil.rmtree("build/src")
    