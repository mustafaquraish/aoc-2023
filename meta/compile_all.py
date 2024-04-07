#!/usr/bin/env python3

import os
import re
import subprocess
from glob import glob

os.makedirs("build", exist_ok=True)
for d in sorted(glob("src/??.oc")):
    if not os.path.isfile(d): continue
    day = int(re.search(r"(\d+)", d).group(1))
    os.system(f"ocen {d} -o ./build/day{day}")
