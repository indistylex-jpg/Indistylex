#!/usr/bin/env bash
# Start Jenkins locally without Docker (requires Java 17+).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
JENKINS_WAR="${SCRIPT_DIR}/jenkins.war"
JENKINS_PORT="${JENKINS_PORT:-8080}"

mkdir -p "${JENKINS_HOME}"

if [[ ! -f "${JENKINS_WAR}" ]]; then
  echo "Downloading Jenkins LTS…"
  curl -fsSL -o "${JENKINS_WAR}" \
    https://get.jenkins.io/war-stable/latest/jenkins.war
fi

echo "Starting Jenkins on http://localhost:${JENKINS_PORT}"
echo "JENKINS_HOME=${JENKINS_HOME}"
echo ""
echo "Initial password (after first start):"
echo "  cat ${JENKINS_HOME}/secrets/initialAdminPassword"
echo ""

exec java -jar "${JENKINS_WAR}" \
  --httpPort="${JENKINS_PORT}" \
  --httpListenAddress=127.0.0.1
