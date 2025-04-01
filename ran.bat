@echo off
:: ==== PART 0: Setup Colors (Pretty Output) ====
:: Green text
for /F "tokens=2 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%a"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "RESET=%ESC%[0m"

:: ==== PART 1: Path Setup ====

set PROJECT_ROOT=%~dp0
set PYTHON_EXE="%PROJECT_ROOT%winpython\Winpython64-3.11.1.0dot.exe"
set VENV_DIR="%PROJECT_ROOT%venv"
set REQ_FILE="%PROJECT_ROOT%requirements.txt"

:: ==== PART 2: Virtual Environment Setup ====
if not exist %VENV_DIR% (
    echo %GREEN%Creating virtual environment...%RESET%
    %PYTHON_EXE% -m venv %VENV_DIR%
    call %VENV_DIR%\Scripts\activate
    echo %GREEN%Installing base packages...%RESET%
    pip install -r %REQ_FILE%
) else (
    call %VENV_DIR%\Scripts\activate
    :: Check if requirements changed
    for /F %%i in ('powershell -command "(Get-FileHash %REQ_FILE%).Hash"') do set "REQ_HASH=%%i"
    if not defined LAST_REQ_HASH (
        set "LAST_REQ_HASH=%REQ_HASH%"
    )
    if not "%REQ_HASH%"=="%LAST_REQ_HASH%" (
        echo %YELLOW%Requirements changed - updating packages...%RESET%
        pip install -r %REQ_FILE%
        set "LAST_REQ_HASH=%REQ_HASH%"
    )
)

:: ==== PART 3: Launch Flask ====
echo %GREEN%Starting Flask server...%RESET%
set PYTHONPATH=%PROJECT_ROOT%
start "" http://localhost:5000/shop
python -c "from app.main import app; app.run(debug=True)"

:: ==== PART 4: Error Handling ====
if errorlevel 1 (
    echo %RED%Error: Flask server crashed!%RESET%
    echo %YELLOW%Check the messages above for details.%RESET%
)
pause