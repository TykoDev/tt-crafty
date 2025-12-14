#!/bin/bash
pip install pyinstaller
pyinstaller --clean versus_ai.spec
echo "Build complete. Executable is in dist/VersusAI"
