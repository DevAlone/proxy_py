#!/usr/bin/env bash
if [ $# -eq 0 ]
then
	tag='latest'
	git checkout master || exit 1
else
	tag=$1
	git checkout $tag || exit 1
fi

docker build -t DevAlone/proxy_py:$tag .
docker push DevAlone/proxy_py:$tag
