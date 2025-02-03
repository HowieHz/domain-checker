#!/bin/bash

echo "build domain-checker"
python -m nuitka ./src/main.py --standalone --onefile --output-filename=domain-checker --output-dir=bin/domain-checker

cp -r plugins bin/domain-checker/plugins
rm -rf bin/domain-checker/plugins/__pycache__
rm -rf bin/domain-checker/plugins/whois21_query
