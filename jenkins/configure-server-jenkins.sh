#!/usr/bin/env bash
# One-time: install Jenkins ON the production server and wire indistylex-deploy job.
# Run as root on 138.201.50.228:
#   cd /var/www/html/indistylex && bash jenkins/configure-server-jenkins.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html/indistylex}"
JENKINS_PORT="${JENKINS_PORT:-8081}"
GIT_REMOTE="${GIT_REMOTE:-shivam74826}"
GITHUB_REPO="${GITHUB_REPO:-git@github.com:shivam74826/Indistylex.git}"
JENKINS_HOME="${JENKINS_HOME:-/var/lib/jenkins}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_FILE="${SCRIPT_DIR}/plugins.txt"
PLUGIN_MGR="${SCRIPT_DIR}/jenkins-plugin-manager.jar"
PLUGIN_MGR_VERSION="2.13.2"

log() { echo "[configure-jenkins] $*"; }
die() { echo "[configure-jenkins] ERROR: $*" >&2; exit 1; }

[[ "${EUID}" -eq 0 ]] || die "Run as root: sudo bash jenkins/configure-server-jenkins.sh"
[[ -d "${APP_DIR}/.git" ]] || die "${APP_DIR} is not a git repo."

log "Step 1/6 — Server deploy prerequisites (git + sudoers)…"
bash "${APP_DIR}/jenkins/setup-server-deploy.sh"

log "Step 2/6 — Install Jenkins (port ${JENKINS_PORT})…"
if ! command -v jenkins >/dev/null 2>&1; then
  bash "${SCRIPT_DIR}/install-server.sh"
else
  log "Jenkins package already installed."
  grep -q "^HTTP_PORT=" /etc/default/jenkins && \
    sed -i "s/^HTTP_PORT=.*/HTTP_PORT=${JENKINS_PORT}/" /etc/default/jenkins || \
    echo "HTTP_PORT=${JENKINS_PORT}" >> /etc/default/jenkins
fi

log "Step 3/6 — Jenkins user: git access + app permissions…"
usermod -aG www-data jenkins
install -d -m 700 -o jenkins -g jenkins "${JENKINS_HOME}/.ssh"

if [[ -f /root/.ssh/id_ed25519 ]]; then
  install -m 600 -o jenkins -g jenkins /root/.ssh/id_ed25519 "${JENKINS_HOME}/.ssh/id_ed25519"
  [[ -f /root/.ssh/id_ed25519.pub ]] && \
    install -m 644 -o jenkins -g jenkins /root/.ssh/id_ed25519.pub "${JENKINS_HOME}/.ssh/id_ed25519.pub"
  [[ -f /root/.ssh/known_hosts ]] && \
    install -m 644 -o jenkins -g jenkins /root/.ssh/known_hosts "${JENKINS_HOME}/.ssh/known_hosts"
fi

sudo -u jenkins git config --global safe.directory "${APP_DIR}"
sudo -u jenkins git config --global safe.directory "${APP_DIR}/.git"

chmod -R g+rwX "${APP_DIR}/.git" 2>/dev/null || true
chgrp -R www-data "${APP_DIR}/.git" 2>/dev/null || true

if [[ -f "${APP_DIR}/.env" ]]; then
  chown www-data:www-data "${APP_DIR}/.env"
  chmod 640 "${APP_DIR}/.env"
fi

log "Step 4/6 — Sudoers for jenkins deploy…"
cat > /etc/sudoers.d/jenkins-indistylex <<SUDOERS
# Jenkins on-server deploy (local DEPLOY_TARGET)
jenkins ALL=(root) NOPASSWD: ${APP_DIR}/jenkins/deploy.sh
jenkins ALL=(ALL) NOPASSWD: /bin/systemctl restart indistylex, /bin/systemctl status indistylex, /bin/systemctl is-active indistylex
jenkins ALL=(root) NOPASSWD: /bin/chown -R www-data\:www-data ${APP_DIR}
jenkins ALL=(root) NOPASSWD: /bin/chmod 640 ${APP_DIR}/.env
SUDOERS
chmod 440 /etc/sudoers.d/jenkins-indistylex
visudo -cf /etc/sudoers.d/jenkins-indistylex

log "Step 5/6 — Skip setup wizard + install plugins…"
install -d -m 755 "${JENKINS_HOME}/init.groovy.d"
echo "2.492.1" > "${JENKINS_HOME}/jenkins.install.InstallUtil.lastExecVersion"
echo "2.492.1" > "${JENKINS_HOME}/jenkins.install.UpgradeWizard.state"

if [[ ! -f "${PLUGIN_MGR}" ]]; then
  curl -fsSL -o "${PLUGIN_MGR}" \
    "https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/${PLUGIN_MGR_VERSION}/jenkins-plugin-manager-${PLUGIN_MGR_VERSION}.jar"
fi

JENKINS_VER="$(jenkins --version 2>/dev/null | awk '{print $NF}' || echo "2.479.1)"
java -jar "${PLUGIN_MGR}" \
  --jenkins-version "${JENKINS_VER}" \
  --plugin-file "${PLUGIN_FILE}" \
  --plugin-download-directory "${JENKINS_HOME}/plugins" \
  --verbose

chown -R jenkins:jenkins "${JENKINS_HOME}"

log "Step 6/6 — GitHub credential + indistylex-deploy job…"
GITHUB_SSH_CREDENTIAL_ID="${GITHUB_SSH_CREDENTIAL_ID:-indistylex-github-ssh}"
JENKINS_HOME="${JENKINS_HOME}" GITHUB_SSH_CREDENTIAL_ID="${GITHUB_SSH_CREDENTIAL_ID}" \
  bash "${SCRIPT_DIR}/setup-github-credential.sh" "${JENKINS_HOME}/.ssh/id_ed25519"

JENKINS_HOME="${JENKINS_HOME}" bash "${SCRIPT_DIR}/seed-jobs.sh"

python3 - "${JENKINS_HOME}/jobs/indistylex-deploy/config.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
tree = ET.parse(path)
root = tree.getroot()

for param in root.iter("hudson.model.ChoiceParameterDefinition"):
    name = param.find("name")
    if name is None:
        continue
    choices = param.find("choices/a")
    if choices is None:
        continue
    if name.text == "DEPLOY_TARGET":
        choices.clear()
        for val in ("local", "remote"):
            el = ET.SubElement(choices, "string")
            el.text = val
    if name.text == "ENVIRONMENT":
        choices.clear()
        for val in ("staging", "production", "development"):
            el = ET.SubElement(choices, "string")
            el.text = val

for boolean in root.iter("hudson.model.BooleanParameterDefinition"):
    name = boolean.find("name")
    default = boolean.find("defaultValue")
    if name is not None and default is not None and name.text == "RUN_MIGRATIONS":
        default.text = "true"

ET.indent(tree, space="  ")
tree.write(path, encoding="UTF-8", xml_declaration=True)
print("Updated job defaults: DEPLOY_TARGET=local, RUN_MIGRATIONS=true")
PY

chown -R jenkins:jenkins "${JENKINS_HOME}/jobs" "${JENKINS_HOME}/credentials.xml" 2>/dev/null || true

systemctl restart jenkins
sleep 5

SERVER_IP="$(hostname -I | awk '{print $1}')"

cat <<EOF

==============================================
 Server Jenkins ready — use this for ALL deploys
==============================================

URL   : http://${SERVER_IP}:${JENKINS_PORT}
Job   : indistylex-deploy

HOW TO DEPLOY (every time after git push):
  1. Push code: git push shivam74826 develop
  2. Open Jenkins → indistylex-deploy → Build with Parameters
  3. Use:
       ENVIRONMENT     = staging
       ROLLOUT_ACTION  = deploy
       DEPLOY_TARGET   = local
       RUN_MIGRATIONS  = true (checked)

First login: get admin password with:
  sudo cat ${JENKINS_HOME}/secrets/initialAdminPassword

Do NOT deploy with manual git pull anymore — always use Jenkins on the server.

EOF
