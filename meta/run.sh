#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--fast) FAST=1; shift;;
    *) POSITIONAL_ARGS+=("$1"); shift;;
  esac
done
set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

#################################

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

if [[ $FAST -eq 1 ]]; then
    ocen -d -cf "-O3 -march=native -funroll-loops" -o $OUT $SRC
else
    ocen -d $SRC -o $OUT
fi

zsh -c "time $OUT $ARGS"