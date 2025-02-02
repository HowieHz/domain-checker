@echo off

echo build domain-checker

start nuitka .\src\main.py --standalone --onefile --include-data-files=.venv\Lib\site-packages\whois21\vcard-map.json=whois21\vcard-map.json --output-filename=domain-checker --output-dir=bin\domain-checker

echo build travellings-cn-api

start nuitka .\extra-scripts\travellings-cn-api\main.py --standalone --onefile --output-filename=travellings-cn-api --output-dir=bin\travellings-cn-api

echo build get-whois-server-list

start nuitka .\extra-scripts\get-whois-server-list\main.py --standalone --onefile --output-filename=get-whois-server-list --output-dir=bin\get-whois-server-list
