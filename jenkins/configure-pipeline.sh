#!/usr/bin/env bash
# One command: wire local Jenkins for GitHub clone + server deploy via SSH.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

find . -maxdepth 1 -name '*.sh' -exec sed -i 's/\r$//' {} +

export PRODUCTION_USER="${PRODUCTION_USER:-indistylex-deploy}"
export PRODUCTION_HOST="${PRODUCTION_HOST:-138.201.50.228}"
KEY_PATH="${1:-${HOME}/.ssh/id_ed25519}"

echo "==> GitHub SSH credential (clone Jenkinsfile)…"
./setup-github-credential.sh "${KEY_PATH}"

echo "==> Server SSH credential (${PRODUCTION_USER}@${PRODUCTION_HOST})…"
./setup-server-ssh-credential.sh "${KEY_PATH}"

echo "==> Reseed job from template…"
./seed-jobs.sh

echo "==> Restart Jenkins…"
./restart-local.sh

cat <<EOF

==============================================
 Local Jenkins ready for Indistylex pipeline
==============================================

URL  : http://localhost:8080
Job  : indistylex-deploy

HOW TO TRIGGER
--------------
1. Open http://localhost:8080/job/indistylex-deploy/
2. Click "Build with Parameters"
3. Choose:

   Run tests only (laptop, no server change):
     ENVIRONMENT     = development
     ROLLOUT_ACTION  = deploy

   Deploy develop branch to server:
     ENVIRONMENT     = staging
     ROLLOUT_ACTION  = deploy
     DEPLOY_TARGET   = remote

   Deploy main branch to production:
     ENVIRONMENT     = production
     ROLLOUT_ACTION  = deploy
     DEPLOY_TARGET   = remote

   Preview plan without changes:
     ENVIRONMENT     = staging
     ROLLOUT_ACTION  = dry-run
     DEPLOY_TARGET   = remote

Server deploy user : ${PRODUCTION_USER}@${PRODUCTION_HOST}
App on server      : /var/www/html/indistylex

EOF
