@echo off

call "venv\Scripts\activate.bat"

echo SafetyEye API starting...
echo API docs available at http://localhost:8000/docs
echo WebSocket stream: ws://localhost:8000/ws/stream
echo WebSocket events: ws://localhost:8000/ws/events

python -m uvicorn Scripts.server:app --host 0.0.0.0 --port 8000 --reload

pause
