#!/bin/bash

nuitka ./src/main.py --standalone --onefile --include-data-files=.venv/Lib/site-packages/whois21/vcard-map.json=whois21/vcard-map.json --output-filename=domain-checker --output-dir=bin
