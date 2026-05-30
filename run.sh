#!/usr/bin/env bash
# Run the portfolio app using the local virtual environment
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$DIR/.venv/bin/streamlit" run "$DIR/app.py" "$@"
