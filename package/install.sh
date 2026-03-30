#!/usr/bin/env bash
# Install the QGenda Claude Code skill to ~/.claude/skills/qgenda/
#
# Usage:
#   ./install.sh                    # install from extracted package
#   curl ... | tar xz && cd qgenda-skill && ./install.sh   # one-liner
#
# What it does:
#   1. Copies skill files to ~/.claude/skills/qgenda/
#   2. Rewrites script paths in SKILL.md to use absolute paths
#   3. Installs Python dependencies (qgendapy) via uv or pip
#
# Prerequisites:
#   - Python >= 3.11
#   - uv (preferred) or pip
#   - QGENDA_CONF_FILE env var set to your qgenda.conf path
set -euo pipefail

SKILL_NAME="qgenda"
DEST="${HOME}/.claude/skills/${SKILL_NAME}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing QGenda skill to ${DEST} ..."

# Create directory structure
mkdir -p "${DEST}/references" "${DEST}/scripts"

# Copy files
cp "${SCRIPT_DIR}/SKILL.md"                       "${DEST}/SKILL.md"
cp "${SCRIPT_DIR}/references/api-reference.md"     "${DEST}/references/api-reference.md"
cp "${SCRIPT_DIR}/scripts/qgenda_query.py"         "${DEST}/scripts/qgenda_query.py"
cp "${SCRIPT_DIR}/scripts/qgenda_core.py"          "${DEST}/scripts/qgenda_core.py"

# Rewrite script paths in SKILL.md to use absolute installed paths
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|scripts/qgenda_query.py|${DEST}/scripts/qgenda_query.py|g" "${DEST}/SKILL.md"
else
    sed -i "s|scripts/qgenda_query.py|${DEST}/scripts/qgenda_query.py|g" "${DEST}/SKILL.md"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if command -v uv &>/dev/null; then
    uv pip install --system qgendapy 2>/dev/null \
        || uv pip install qgendapy 2>/dev/null \
        || echo "Warning: Could not install via uv. Install manually: uv pip install qgendapy"
elif command -v pip3 &>/dev/null; then
    pip3 install qgendapy
elif command -v pip &>/dev/null; then
    pip install qgendapy
else
    echo "Warning: No pip or uv found. Install manually: pip install qgendapy"
fi

echo ""
echo "Installed:"
echo "  ${DEST}/SKILL.md"
echo "  ${DEST}/references/api-reference.md"
echo "  ${DEST}/scripts/qgenda_query.py"
echo "  ${DEST}/scripts/qgenda_core.py"
echo ""

# Check for QGENDA_CONF_FILE
if [ -z "${QGENDA_CONF_FILE:-}" ]; then
    echo "Note: QGENDA_CONF_FILE is not set."
    echo "  Set it to your qgenda.conf path before using the skill:"
    echo "  export QGENDA_CONF_FILE=~/.qgenda.conf"
    echo ""
fi

echo "The /qgenda skill is now available in all Claude Code projects."
echo "Start a new Claude Code session and try: /qgenda Who is working today?"
