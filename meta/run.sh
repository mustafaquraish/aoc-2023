#!/bin/bash

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--fast) FAST=1; shift;;
    -p|--pgo) PGO=1; shift;;
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

if [ $# -eq 0 ]; then
    ARGS="./input/$DAY.txt"
elif [ "$1" = "s" ]; then
    ARGS="./input/${DAY}s.txt"
else
    ARGS="$@"
fi

set -e

if [[ $FAST -eq 1 ]]; then
    ocen -d -cf "-O3 -march=native -funroll-loops" -o $OUT $SRC
elif [[ $PGO -eq 1 ]]; then
    # if macos, use `llvm-profdata merge -output=profdata.profdata *.profraw`
    if [[ "$OSTYPE" == "darwin"*  ]] && [[ -z "${CC}" ]]; then
        ocen -cf "-O3 -march=native -funroll-loops -fprofile-generate" -o $OUT $SRC
        $OUT $ARGS > /dev/null
        xcrun llvm-profdata merge -output=build/default.profdata *.profraw
        ocen -d -cf "-O3 -march=native -funroll-loops -fprofile-use=build/default.profdata" -o $OUT $SRC
        rm -f ./*.profraw ./build/*.profdata

    # Assume linux with gcc
    else
        ocen -d -cf "-O3 -march=native -funroll-loops -fprofile-generate" -o $OUT $SRC
        $OUT $ARGS > /dev/null
        ocen -d -cf "-O3 -march=native -funroll-loops -fprofile-use" -o $OUT $SRC
        rm -f ./*.gcda ./*.gcno

    fi
else
    ocen -d $SRC -o $OUT
fi

zsh -c "time $OUT $ARGS"