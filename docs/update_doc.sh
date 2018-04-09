#!/usr/bin/env bash

sphinx-apidoc --force --separate -o source/modules ../ && sed -i "1s/.*/proxy_py Modules/" source/modules/modules.rst && make html
