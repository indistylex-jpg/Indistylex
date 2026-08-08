#!/usr/bin/env bash
# Restart local Jenkins (WAR mode, no Docker).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/jenkins.pid"
JENKINS_PORT="${JENKINS_PORT:-8080}"

stop_jenkins() {
  if [[ -f "${PID_FILE}" ]]; then
    PID="$(cat "${PID_FILE}")"
    if kill -0 "${PID}" 2>/dev/null; then
      echo "Stopping Jenkins (pid ${PID})…"
      kill "${PID}" || true
      sleep 3
      kill -9 "${PID}" 2>/dev/null || true
    fi
    rm -f "${PID_FILE}"
  fi
  # Also stop any stray jenkins.war on our port
  pkill -f "jenkins.war --httpPort=${JENKINS_PORT}" 2>/dev/null || true
}

start_jenkins() {
  export JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
  cd "${SCRIPT_DIR}"
  nohup ./start-local.sh > jenkins.log 2>&1 &
  echo $! > "${PID_FILE}"
  echo "Waiting for Jenkins…"
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${JENKINS_PORT}/login" >/dev/null 2>&1; then
      echo "Jenkins is up: http://localhost:${JENKINS_PORT}"
      return 0
    fi
    sleep 2
  done
  echo "Jenkins did not start — check jenkins.log"
  tail -30 jenkins.log
  exit 1
}

stop_jenkins
start_jenkins
