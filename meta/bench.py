#!/usr/bin/env python3

import os
import re
import sys
import contextlib
import subprocess
import shutil
import textwrap
from glob import glob
import json
from time import perf_counter

YEAR = 2023

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

def cmd(c):
    return subprocess.check_output(c, shell=True, text=True)

os.makedirs("build", exist_ok=True)

def compile_benchmark():
    # Profile guided optimization
    if sys.platform == "linux" or "gcc" in os.getenv("CC", "clang"):
        print("[+] Compiling with instrumentation")
        cmd("ocen src/run_all.oc -o ./run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result -fprofile-generate'")
        print("[+] Running benchmark")
        cmd("./run_all ./ 2")
        print("[+] Compiling with profile")
        cmd("ocen src/run_all.oc -o ./run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result -fprofile-use'")
        cmd("rm -f *.gcda")
    elif sys.platform == "darwin":
        print("[+] Compiling with instrumentation")
        cmd("ocen src/run_all.oc -o ./run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result -fprofile-generate'")
        print("[+] Running benchmark")
        cmd("./run_all ./ 2")
        # use llvm-profdata to merge the profiles
        print("[+] Merging profiles with llvm-profdata")
        cmd("xcrun llvm-profdata merge -output=default.profdata *.profraw")
        print("[+] Compiling with profile")
        cmd("ocen src/run_all.oc -o ./run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result -fprofile-use=default.profdata'")
        cmd("rm -f *.profraw *.profdata")
    else:
        print("[+] Compiling ")
        cmd("ocen src/run_all.oc -o ./run_all -cf '-O3 -march=native -funroll-loops -Wno-unused-result'")


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
        import std::vector::{ Vector }
        import std::buffer::{ Buffer }
                              
        @compiler c_include "time.h"
        def clock(): i64 extern
        const CLOCKS_PER_SEC: i64 extern

        def ftime(): f32 => clock() as f32 / CLOCKS_PER_SEC as f32
        let RUNS: u32 = 20
                                  
        def call_fn(times: &Vector<f32>, f: fn(i32,&str), inp: str) {
            let argv: [str; 2]
            argv[0] = "dummy"
            argv[1] = inp

            f(2, argv)  // warmup

            let total = 0.0
            for let i = 0; i < RUNS; i++ {                  
                let start = ftime()
                f(2, argv)
                let end = ftime()
                total += end - start
            }
            let avg = total / RUNS as f32
            times.push(avg)
        }

        def main(argc: i32, argv: &str) {
            assert argc > 1, "no input directory provided"
            
            if argc > 2 {
                RUNS = argv[2].to_u32()
            }
                                  
            let times = Vector<f32>::new()
            let dir = argv[1]
        """)
        fp.write(prelude)

        for day in days:
            fp.write(f"    call_fn(times, day{day:02}::main, `{{dir}}/{day:02}.in`)\n")

        fp.write(textwrap.dedent("""

            let buf = Buffer::make()
            buf.puts("{\\n")
            let total = 0.0
            for let i = 0; i < times.size; i++ {
                let t = times.at(i)
                total += t
                buf.putsf(`    "{i+1:02d}": {t:.3f},\\n`)                        
            }
            buf.putsf(`    "total": {total:.3f}\\n`)
            buf.puts("}\\n")

            let file = std::File::open("benchmark.json", "w")
            file.write(buf.data, buf.size)
            file.close()
        }                         
        """))

    with pushd("build"):
        compile_benchmark()


def run_benchmark():
    with pushd("build"):
        print("[+] Running benchmark")
        cmd("./run_all ./")
        assert os.path.exists("benchmark.json"), "benchmark.json not found"
        print("[+] Benchmark results:")
        res = json.load(open("benchmark.json"))
        for k, v in res.items():
            print(f" {k:>6s}: {v:.3f}s")


files = sorted(glob("src/??.oc"))
days = [int(re.search(r"(\d+)", f).group(1)) for f in files]

shutil.rmtree("build/src", ignore_errors=True)
shutil.copytree("src", "build/src")
for day in days:
    shutil.move(f"build/src/{day:02}.oc", f"build/src/day{day:02}.oc")

create_benchmark(days)
run_benchmark()

shutil.rmtree("build/src")
    