#!/usr/bin/env bash
# One-time setup for local Jenkins on your ThinkPad.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"

echo "==> Fixing ownership (jenkins/ may have been created as root)…"
sudo chown -R "${USER_NAME}:${USER_NAME}" "${SCRIPT_DIR}"

echo "==> Installing plugins (git + pipeline)…"
"${SCRIPT_DIR}/install-plugins.sh"

echo "==> Restarting Jenkins…"
"${SCRIPT_DIR}/restart-local.sh"

echo ""
echo "==> Verify git plugin:"
ls "${SCRIPT_DIR}/.jenkins_home/plugins/git.jpi" && echo "OK: git plugin installed"
echo ""
echo "Open http://localhost:8080 → New Item → Pipeline"
echo "Definition: Pipeline script from SCM → Git"
