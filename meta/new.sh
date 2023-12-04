#!/bin/zsh

YEAR=2023
DAY=$(printf "%02d" $1)

cp src/template.oc src/$DAY.oc
./meta/fetch.py $YEAR $DAY
code-insiders src/$DAY.oc