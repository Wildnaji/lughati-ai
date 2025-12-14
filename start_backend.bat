@echo off
echo Starting Lughati AI Backend Server...
echo.
echo Make sure you have set OPENAI_API_KEY environment variable!
echo.
uvicorn back_end.app:app --reload --host 0.0.0.0 --port 8000


