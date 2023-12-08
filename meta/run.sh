#!/bin/bash

DAY=$(printf "%02d" "${1#0}")
shift

mkdir -p build

SRC=./src/$DAY.oc
OUT=./build/$DAY.out

if [ -z "$1" ]; then
    ARGS="./input/$DAY.txt"
elif [ "$1" = "s" ]; then
    ARGS="./input/${DAY}s.txt"
else
    ARGS="$@"
fi

set -e

ocen -d $SRC -o $OUT

set -x

$OUT $ARGS