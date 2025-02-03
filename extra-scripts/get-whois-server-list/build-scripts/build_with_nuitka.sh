#!/bin/bash

echo "build get-whois-server-list"
python -m nuitka ./extra-scripts/get-whois-server-list/main.py --standalone --onefile --output-filename=get-whois-server-list--output-dir=bin/get-whois-server-list
