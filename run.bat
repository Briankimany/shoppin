@echo off
:: ==== PART 0: Setup ====
setlocal enabledelayedexpansion

:: ANSI colors
for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "RESET=%ESC%[0m"

:: Jump to main execution
goto :main

:: ======================
:: LOGGING FUNCTIONALITY
:: ======================
:log
set "LOG_MSG=%~1"
set "LOG_LEVEL=%~2"
if not defined LOG_LEVEL set "LOG_LEVEL=INFO"
echo [%date% %time%] [%LOG_LEVEL%] %LOG_MSG% >> "%LOG_FILE%"
exit /b 0

:main
:: ==== Initialize logging ====
set "PROJECT_ROOT=%~dp0"
set "LOG_FILE=%PROJECT_ROOT%script_log.txt"
set "PYTHON_LOG=%PROJECT_ROOT%python_log.txt"

:: Clear previous logs
if exist "%LOG_FILE%" del "%LOG_FILE%"
if exist "%PYTHON_LOG%" del "%PYTHON_LOG%"

echo [%date% %time%] Script started > "%LOG_FILE%"
call :log "Initialized logging system"
call :log "Project root: %PROJECT_ROOT%"


:: ==== PART 1: Path Setup ====
echo %GREEN%PART 1: Path Setup%RESET%
set "PYTHON_EXE=%PROJECT_ROOT%winpython\WPy64-31110\python-3.11.1.amd64\python.exe"
set "VENV_DIR=%PROJECT_ROOT%venv"
set "REQ_FILE=%PROJECT_ROOT%requirements.txt"
set "WINPYTHON_ARCHIVE=%PROJECT_ROOT%winpython\Winpython64-3.11.1.0dot.exe"

if not exist "%PYTHON_EXE%" (
    if exist "%WINPYTHON_ARCHIVE%" (
        echo %YELLOW%Extracting WinPython...%RESET%
        "%WINPYTHON_ARCHIVE%" -o"%PROJECT_ROOT%winpython" 
    ) else (
        echo %RED%WinPython archive missing!%RESET%
        echo Download from: https://winpython.github.io/
        echo Save as: %WINPYTHON_ARCHIVE%
		goto :cleanup
    )
)

:: Verify extraction worked
if not exist "%PYTHON_EXE%" (
    echo %RED%Extraction failed!%RESET%
    echo Manually extract %WINPYTHON_ARCHIVE% to %PROJECT_ROOT%
	goto :cleanup
)


echo. > "%PROJECT_ROOT%\write_test.tmp" 2>nul
if not exist "%PROJECT_ROOT%\write_test.tmp" (
    call :log "Cannot write to project directory" "ERROR"
    echo %RED%Error: No write permissions in project directory%RESET%
    goto :cleanup
)
call :log "Can write to project directory" "INFO"
del "%PROJECT_ROOT%\write_test.tmp" 2>nul



:: Verify critical files
if not exist "%PYTHON_EXE%" (
    call :log "Python executable not found at %PYTHON_EXE%" "ERROR"
    echo %RED%Error: Python not found at %PYTHON_EXE%%RESET%
    goto :cleanup_with_pause
)

if not exist "%REQ_FILE%" (
    call :log "requirements.txt not found at %REQ_FILE%" "ERROR"
    echo %RED%Error: requirements.txt not found%RESET%
    goto :cleanup_with_pause
)

:: ==== PART 2: Virtual Environment Setup ====
echo %GREEN%PART 2: Virtual Environment Setup%RESET%
if not exist "%VENV_DIR%" (
    call :log "Creating virtual environment at %VENV_DIR%"
    echo %GREEN%Creating virtual environment...%RESET%
    "%PYTHON_EXE%" -m venv "%VENV_DIR%" || (
        call :log "Failed to create virtual environment" "ERROR"
        echo %RED%Failed to create venv%RESET%
        goto :cleanup_with_pause
    )
    call :log "Virtual environment created successfully"
)

call "%VENV_DIR%\Scripts\activate" || (
    call :log "Failed to activate virtual environment" "ERROR"
    echo %RED%Failed to activate venv%RESET%
    goto :cleanup_with_pause
)
call :log "Virtual environment activated"
echo %GREEN%Virtual environment activated%RESET%



:: ==== PART 3: Package Comparison - FIXED VERSION ====
call :log "Starting package comparison"
echo %GREEN%PART 3: Package Comparison%RESET%

set "FREEZE_FILE=%PROJECT_ROOT%current_reqs.txt"

:: Generate requirements snapshot
call :log "Generating pip freeze output"
pip freeze > "%FREEZE_FILE%"
if not exist "%FREEZE_FILE%" (
    call :log "Failed to generate current_reqs.txt" "ERROR"
    echo %RED%Error: Failed to generate package list%RESET%
    goto :cleanup_with_pause
)

:: Compare using Python script
call :log "Starting requirements comparison"
echo %GREEN%Running requirements comparison...%RESET%

:: Run comparison - capture raw errorlevel as string
"%PYTHON_EXE%" compare_req.py requirements.txt current_reqs.txt
set "RAW_ERROR=%errorlevel%"
call :log "Comparison completed with exit code %RAW_ERROR%"


:: Debug output
echo %YELLOW%[DEBUG] RAW ERRORLEVEL: "%RAW_ERROR%" %RESET%

:: String comparison block (SAFE)
if "%RAW_ERROR%" == "0" (
    call :log "All requirements satisfied"
    echo %GREEN%Validation passed%RESET%
) else if "%RAW_ERROR%" == "1" (
    call :log "Missing packages detected"
    echo %YELLOW%Installing requirements...%RESET%
    pip install -r reqs_diff.txt --upgrade || (
        call :log "Install failed" "ERROR"
        echo %RED%Installation failed%RESET%
        goto :cleanup_with_pause
    )
) else (
    call :log "Unknown error: %RAW_ERROR%" "ERROR"
    echo %RED%UNKNOWN ERROR: "%RAW_ERROR%" %RESET%
    goto :cleanup_with_pause
)

:: ==== PART 4: Launch Flask ====
call :log "Starting Flask server"
echo %GREEN%Starting Flask server...%RESET%
set "PYTHONPATH=%PROJECT_ROOT%"

:: Default values
set HOST=127.0.0.1
set PORT=5000
set DEBUG=1

:: Loop over all arguments
:parse_args
if "%~1"=="" goto after_args

:: Check if argument starts with "host=" or "port="
if /i "%~1"=="host" (
    set HOST=%~2
    shift
) else if /i "%~1"=="port" (
    set PORT=%~2
    shift
) else (
    :: Fallback: Try parsing as key=value
    for /f "tokens=1,2 delims==" %%A in ("%~1") do (
        if /i "%%A"=="host" set HOST=%%B
        if /i "%%A"=="port" set PORT=%%B
    )
)
shift
goto parse_args



:after_args
:: Run Python script with parsed args
:: Determine browser host
set "BROWSER_HOST=%HOST%"
if "%HOST%"=="0.0.0.0" (
    set "BROWSER_HOST=localhost"
)
:: Open browser
start "" http://%BROWSER_HOST%:%PORT%/shop
"%VENV_DIR%\Scripts\python.exe" "%~dp0main.py" %HOST% %PORT% %DEBUG%

:: Check if main.py exited with error
if %errorlevel% neq 0 (
    call :log "Flask server crashed" "ERROR"
    echo %RED%Flask crash details:%RESET%
    "%VENV_DIR%\Scripts\python.exe" -c "import sys; from app.main import app; sys.exit(0)" || (
        echo %RED%Import failed! Verify:%RESET%
        echo 1. Virtual environment activation
        echo 2. 'flask' installed in venv
        echo 3. PYTHONPATH includes %PROJECT_ROOT%
    )
    goto :cleanup_with_pause
)


:cleanup_with_pause
call :log "Script paused due to error"
echo.
echo %RED%Script encountered an error%RESET%
echo %YELLOW%Press any key to close this window...%RESET%
pause >nul
exit /b 1