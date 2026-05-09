@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"

echo [Panel] Cerrando instancias anteriores...

taskkill /FI "WINDOWTITLE eq Panel Backend" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Panel Frontend" /T /F >nul 2>&1

call :kill_port 8000
call :kill_port 5173

if not exist "%PYTHON_EXE%" (
  echo [ERROR] No existe "%PYTHON_EXE%"
  echo Crea primero el venv en backend\.venv
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] npm no esta en PATH
  pause
  exit /b 1
)

echo [Panel] Arrancando backend...
start "Panel Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%PYTHON_EXE%"" -m uvicorn app.main:app --reload --port 8000"

echo [Panel] Esperando 2 segundos...
timeout /t 2 /nobreak >nul

echo [Panel] Arrancando frontend...
start "Panel Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

echo [Panel] Esperando frontend en :5173...
call :wait_port 5173 30

echo [Panel] Abriendo navegador...
start "" "http://localhost:5173"

echo [Panel] Backend:  http://localhost:8000
echo [Panel] Frontend: http://localhost:5173
exit /b 0

:kill_port
set "PORT=%~1"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo [Panel] Matando PID %%P en puerto %PORT%
  taskkill /PID %%P /T /F >nul 2>&1
)
exit /b 0

:wait_port
set "PORT=%~1"
set "MAX_WAIT=%~2"
if "%MAX_WAIT%"=="" set "MAX_WAIT=30"
set /a ELAPSED=0

:wait_port_loop
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  exit /b 0
)

if %ELAPSED% GEQ %MAX_WAIT% (
  echo [WARN] El puerto %PORT% no quedo escuchando tras %MAX_WAIT%s. Abriendo navegador igualmente.
  exit /b 0
)

timeout /t 1 /nobreak >nul
set /a ELAPSED+=1
goto :wait_port_loop