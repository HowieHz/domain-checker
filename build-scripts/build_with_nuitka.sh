#!/bin/bash

echo "build domain-checker"
nuitka ./src/main.py --standalone --onefile --output-filename=domain-checker --output-dir=bin/domain-checker

echo "build travellings-cn-api"
nuitka ./extra-scripts/travellings-cn-api/main.py --standalone --onefile --output-filename=travellings-cn-api --output-dir=bin/travellings-cn-api

cho "build get-whois-server-list"
nuitka ./extra-scripts/get-whois-server-list/main.py --standalone --onefile --output-filename=get-whois-server-list--output-dir=bin/get-whois-server-list
