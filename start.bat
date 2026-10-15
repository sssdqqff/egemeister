@echo off
chcp 65001 > nul
cd /d %~dp0

echo Запуск проекта Egemeister...

echo [1/3] Запуск бэкенда (FastAPI)...
start "Backend" cmd /k "cd backend && C:\Users\newbi\AppData\Local\pypoetry\Cache\virtualenvs\egemeister-BrpV7xG1-py3.13\Scripts\python.exe -m uvicorn app.main:app --reload"

echo [2/3] Запуск фронтенда (Vite)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo [3/3] Запуск бота...
start "Bot" cmd /k "cd bot && C:\Users\newbi\AppData\Local\pypoetry\Cache\virtualenvs\egemeister-BrpV7xG1-py3.13\Scripts\python.exe main.py"

echo Всё запущено!
pause