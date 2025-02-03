@echo off

echo build domain-checker

python -m nuitka .\src\main.py --standalone --onefile --output-filename=domain-checker --output-dir=bin\domain-checker

xcopy plugins bin\domain-checker\plugins /E /I /Y
Remove-Item bin\domain-checker\plugins\__pycache__ -Recurse -Force
Remove-Item bin\domain-checker\plugins\whois21_query -Recurse -Force
