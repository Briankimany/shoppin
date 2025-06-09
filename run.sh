#!/bin/bash

# ========== PART 0: Setup ==========
# ANSI colors
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
RED='\033[0;91m'
RESET='\033[0m'

# Logging setup
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_ROOT/script_log.txt"
PYTHON_LOG="$PROJECT_ROOT/python_log.txt"

log() {
    local LOG_MSG="$1"
    local LOG_LEVEL="${2:-INFO}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$LOG_LEVEL] $LOG_MSG" >> "$LOG_FILE"
}

# Clear old logs
rm -f "$LOG_FILE" "$PYTHON_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Script started" > "$LOG_FILE"
log "Initialized logging system"
log "Project root: $PROJECT_ROOT"

# ========== PART 1: Path Setup ==========
echo -e "${GREEN}PART 1: Path Setup${RESET}"
PYTHON_EXE="python3"
VENV_DIR="$PROJECT_ROOT/venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"

# Test write permission
if ! touch "$PROJECT_ROOT/write_test.tmp" 2>/dev/null; then
    log "Cannot write to project directory" "ERROR"
    echo -e "${RED}Error: No write permissions in project directory${RESET}"
    exit 1
fi
rm "$PROJECT_ROOT/write_test.tmp"
log "Can write to project directory"

# Verify requirements.txt
if [[ ! -f "$REQ_FILE" ]]; then
    log "requirements.txt not found at $REQ_FILE" "ERROR"
    echo -e "${RED}Error: requirements.txt not found${RESET}"
    exit 1
fi

# ========== PART 2: Virtual Environment Setup ==========
echo -e "${GREEN}PART 2: Virtual Environment Setup${RESET}"
if [[ ! -d "$VENV_DIR" ]]; then
    log "Creating virtual environment at $VENV_DIR"
    echo -e "${GREEN}Creating virtual environment...${RESET}"
    $PYTHON_EXE -m venv "$VENV_DIR" || {
        log "Failed to create virtual environment" "ERROR"
        echo -e "${RED}Failed to create venv${RESET}"
        exit 1
    }
    log "Virtual environment created successfully"
fi

# Activate venv
source "$VENV_DIR/bin/activate" || {
    log "Failed to activate virtual environment" "ERROR"
    echo -e "${RED}Failed to activate venv${RESET}"
    exit 1
}
log "Virtual environment activated"
echo -e "${GREEN}Virtual environment activated${RESET}"

# ========== PART 3: Package Comparison ==========
log "Starting package comparison"
echo -e "${GREEN}PART 3: Package Comparison${RESET}"

FREEZE_FILE="$PROJECT_ROOT/current_reqs.txt"

log "Generating pip freeze output"
pip freeze > "$FREEZE_FILE"
if [[ ! -f "$FREEZE_FILE" ]]; then
    log "Failed to generate current_reqs.txt" "ERROR"
    echo -e "${RED}Error: Failed to generate package list${RESET}"
    exit 1
fi

log "Starting requirements comparison"
echo -e "${GREEN}Running requirements comparison...${RESET}"
$PYTHON_EXE "$PROJECT_ROOT/compare_req.py" "$REQ_FILE" "$FREEZE_FILE"
RAW_ERROR=$?
log "Comparison completed with exit code $RAW_ERROR"

echo -e "${YELLOW}[DEBUG] RAW ERRORLEVEL: $RAW_ERROR${RESET}"

if [[ "$RAW_ERROR" == "0" ]]; then
    log "All requirements satisfied"
    echo -e "${GREEN}Validation passed${RESET}"
elif [[ "$RAW_ERROR" == "1" ]]; then
    log "Missing packages detected"
    echo -e "${YELLOW}Installing requirements...${RESET}"
    pip install -r "$PROJECT_ROOT/reqs_diff.txt" --upgrade || {
        log "Install failed" "ERROR"
        echo -e "${RED}Installation failed${RESET}"
        exit 1
    }
else
    log "Unknown error: $RAW_ERROR" "ERROR"
    echo -e "${RED}UNKNOWN ERROR: $RAW_ERROR${RESET}"
    exit 1
fi

# ========== PART 4: Launch Flask ==========
log "Starting Flask server"
echo -e "${GREEN}Starting Flask server...${RESET}"
export PYTHONPATH="$PROJECT_ROOT"

# Defaults
HOST="127.0.0.1"
PORT="5000"
DEBUG="1"

# Parse CLI args
for ARG in "$@"; do
    if [[ "$ARG" == host=* ]]; then
        HOST="${ARG#host=}"
    elif [[ "$ARG" == port=* ]]; then
        PORT="${ARG#port=}"
    fi
done

# Open browser (optional, depends on xdg-open availability)
BROWSER_HOST="$HOST"
[[ "$HOST" == "0.0.0.0" ]] && BROWSER_HOST="localhost"
xdg-open "http://$BROWSER_HOST:$PORT/shop" 2>/dev/null &

# Launch main app
"$VENV_DIR/bin/python" "$PROJECT_ROOT/main.py" "$HOST" "$PORT" "$DEBUG"
STATUS=$?

if [[ "$STATUS" -ne 0 ]]; then
    log "Flask server crashed" "ERROR"
    echo -e "${RED}Flask crash details:${RESET}"
    "$VENV_DIR/bin/python" -c "import sys; from app.main import app; sys.exit(0)" || {
        echo -e "${RED}Import failed! Verify:${RESET}"
        echo "1. Virtual environment activation"
        echo "2. 'flask' installed in venv"
        echo "3. PYTHONPATH includes $PROJECT_ROOT"
    }
    exit 1
fi

exit 0
