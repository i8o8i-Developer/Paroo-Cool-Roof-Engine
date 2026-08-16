@echo off
title PARoo - Satellite Rooftop Heat Vulnerability Classifier
echo ================================================================================
echo Starting PARoo Production Server On http://127.0.0.1:8000 ...
echo ================================================================================
python -m uvicorn Backend.Server:App --host 127.0.0.1 --port 8000
pause
