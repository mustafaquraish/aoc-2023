#!/bin/zsh

YEAR=2023
DAY=$(printf "%02d" $1)

cp src/template.oc src/$DAY.oc
code-insiders src/$DAY.oc

until ./meta/fetch.py 2023 $DAY --sample > input/$DAYs.txt; do sleep 1; done
until ./meta/fetch.py 2023 $DAY > input/$DAY.txt; do sleep 1; done

