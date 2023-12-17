#!/bin/zsh

YEAR=2023
DAY=$(printf "%02d" $1)

cp src/template.oc src/$DAY.oc
code-insiders src/$DAY.oc

until ./meta/fetch.py 2023 $DAY --sample -o input/${DAY}s.txt; do sleep 1; done
until ./meta/fetch.py 2023 $DAY -o input/$DAY.txt; do sleep 1; done

DAY_NO_PREFIX=$(printf "%d" $DAY)
open https://adventofcode.com/2023/day/$DAY_NO_PREFIX