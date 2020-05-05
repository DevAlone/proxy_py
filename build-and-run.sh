#!/usr/bin/env bash

number_of_threads=$(grep -c "^processor" /proc/cpuinfo)

function cleanup() {
    docker-compose down
}

trap cleanup EXIT

# TODO: fix
rm sources.tar.gz 2> /dev/null
#git archive -o sources.tar.gz --format=tar.gz HEAD || exit 1
#git ls-files | tar Tzcf - sources.tar.gz || exit 1

docker-compose up --build \
  --scale proxies-handler="$number_of_threads" \
  --scale results-handler="$number_of_threads" \

exit $?
