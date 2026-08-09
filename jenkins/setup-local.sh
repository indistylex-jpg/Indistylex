#!/usr/bin/env bash
# One-command local Jenkins setup on your laptop.
# Usage: cd Indistylex/jenkins && ./setup-local.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="${SUDO_USER:-$USER}"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=============================================="
echo " Indistylex — Local Jenkins Setup"
echo "=============================================="

echo "==> Fixing Windows line endings on shell scripts…"
find "${SCRIPT_DIR}" -maxdepth 1 -name '*.sh' -exec sed -i 's/\r$//' {} +

echo "==> Fixing ownership…"
if [[ -d "${SCRIPT_DIR}/.jenkins_home" ]]; then
  sudo chown -R "${USER_NAME}:${USER_NAME}" "${SCRIPT_DIR}" 2>/dev/null || \
    chown -R "${USER_NAME}:${USER_NAME}" "${SCRIPT_DIR}" 2>/dev/null || true
fi

echo "==> Making scripts executable…"
chmod +x "${SCRIPT_DIR}"/*.sh

echo "==> Checking Java…"
if ! command -v java >/dev/null 2>&1; then
  echo "ERROR: Java 17+ required. Install: sudo apt install openjdk-21-jre-headless"
  exit 1
fi
java -version

echo "==> Installing Jenkins plugins…"
"${SCRIPT_DIR}/install-plugins.sh"

echo "==> Seeding pipeline jobs…"
"${SCRIPT_DIR}/seed-jobs.sh"

echo "==> Adding GitHub SSH credential from ~/.ssh…"
"${SCRIPT_DIR}/setup-github-credential.sh"

echo "==> Adding server SSH credential from ~/.ssh…"
"${SCRIPT_DIR}/setup-server-ssh-credential.sh" || true

echo "==> Starting Jenkins…"
"${SCRIPT_DIR}/restart-local.sh"

JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
INITIAL_PW="${JENKINS_HOME}/secrets/initialAdminPassword"

cat <<EOF

==============================================
 Local Jenkins is ready
==============================================

URL      : http://localhost:8080
Job      : indistylex-deploy (pre-seeded)

First-time login password (if new install):
EOF
if [[ -f "${INITIAL_PW}" ]]; then
  cat "${INITIAL_PW}"
else
  echo "  (already configured — use your admin password)"
fi

cat <<'EOF'

NEXT STEPS (one-time):
----------------------
1. Complete Jenkins setup wizard if prompted
   → Install suggested plugins OR skip (we installed via script)

2. Add SSH credential for server deploy:
   ./add-ssh-credential.sh

2b. GitHub repo access (if job shows "Repository not found"):
   ./setup-github-credential.sh
   # Uses ~/.ssh/id_ed25519 → credential ID indistylex-github-ssh
   # Job SCM URL must be: git@github.com:shivam74826/Indistylex.git

3. Open job → Build with Parameters:

   STAGING deploy (develop → server):
     ENVIRONMENT=staging  ROLLOUT_ACTION=deploy  DEPLOY_TARGET=remote

   PRODUCTION deploy (main → server):
     ENVIRONMENT=production  ROLLOUT_ACTION=deploy  DEPLOY_TARGET=remote

   Run tests only (no deploy):
     ENVIRONMENT=development  ROLLOUT_ACTION=deploy

   Rollback last deploy:
     ENVIRONMENT=staging  ROLLOUT_ACTION=rollback  DEPLOY_TARGET=remote

   Dry-run (plan only):
     ENVIRONMENT=staging  ROLLOUT_ACTION=dry-run  DEPLOY_TARGET=remote

SERVER SETUP (run once on 138.201.50.228):
  cd /var/www/html/indistylex
  git pull shivam74826 develop
  bash jenkins/setup-server-deploy.sh

Manual deploy on server (no Jenkins):
  cd /var/www/html/indistylex
  git pull shivam74826 develop
  systemctl restart indistylex

EOF
