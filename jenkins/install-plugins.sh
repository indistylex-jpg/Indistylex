#!/usr/bin/env bash
# Install Jenkins plugins offline/CLI (no UI needed).
# Usage: ./install-plugins.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
JENKINS_WAR="${SCRIPT_DIR}/jenkins.war"
PLUGIN_FILE="${SCRIPT_DIR}/plugins.txt"
PLUGIN_MGR="${SCRIPT_DIR}/jenkins-plugin-manager.jar"
PLUGIN_MGR_VERSION="2.13.2"

mkdir -p "${JENKINS_HOME}/plugins"

if [[ ! -f "${PLUGIN_MGR}" ]]; then
  echo "Downloading Jenkins Plugin Installation Manager…"
  curl -fsSL -o "${PLUGIN_MGR}" \
    "https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/${PLUGIN_MGR_VERSION}/jenkins-plugin-manager-${PLUGIN_MGR_VERSION}.jar"
fi

if [[ ! -f "${JENKINS_WAR}" ]]; then
  echo "Downloading Jenkins WAR…"
  curl -fsSL -o "${JENKINS_WAR}" \
    https://get.jenkins.io/war-stable/latest/jenkins.war
fi

echo "Installing plugins from ${PLUGIN_FILE}…"
java -jar "${PLUGIN_MGR}" \
  --war "${JENKINS_WAR}" \
  --plugin-file "${PLUGIN_FILE}" \
  --plugin-download-directory "${JENKINS_HOME}/plugins"

echo ""
echo "Plugins installed. Restart Jenkins:"
echo "  ./restart-local.sh"
