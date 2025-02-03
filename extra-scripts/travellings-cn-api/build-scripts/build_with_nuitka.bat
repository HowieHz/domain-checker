@echo off

echo build travellings-cn-api

python -m nuitka .\extra-scripts\travellings-cn-api\main.py --standalone --onefile --output-filename=travellings-cn-api --output-dir=bin\travellings-cn-api
