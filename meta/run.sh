#!/bin/bash

DAY=$(printf "%02d" $1)
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

if [ $SRC -nt $OUT ]; then
    ocen -d $SRC -o $OUT
fi

set -x

$OUT $ARGS