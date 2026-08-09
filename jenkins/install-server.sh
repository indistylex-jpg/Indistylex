#!/usr/bin/env bash
# Install Jenkins on Ubuntu 24.04 (production server).
# Run as root: bash jenkins/install-server.sh
set -euo pipefail

JENKINS_PORT="${JENKINS_PORT:-8081}"
APP_DIR="${APP_DIR:-/var/www/html/indistylex}"

echo "==> Installing Java 21…"
apt-get update -qq
apt-get install -y openjdk-21-jre-headless curl git

echo "==> Adding Jenkins apt repository…"
install -d -m 0755 /usr/share/keyrings
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | gpg --dearmor -o /usr/share/keyrings/jenkins-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.gpg] https://pkg.jenkins.io/debian-stable binary/" \
  > /etc/apt/sources.list.d/jenkins.list
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y jenkins

echo "==> Configuring Jenkins on port ${JENKINS_PORT}…"
sed -i "s/^HTTP_PORT=.*/HTTP_PORT=${JENKINS_PORT}/" /etc/default/jenkins || true
grep -q "^HTTP_PORT=" /etc/default/jenkins || echo "HTTP_PORT=${JENKINS_PORT}" >> /etc/default/jenkins

echo "==> Allowing jenkins user to run deploy script…"
cat > /etc/sudoers.d/jenkins-indistylex <<SUDOERS
jenkins ALL=(root) NOPASSWD: ${APP_DIR}/jenkins/deploy.sh
jenkins ALL=(root) NOPASSWD: /bin/systemctl restart indistylex, /bin/systemctl status indistylex, /bin/systemctl is-active indistylex
SUDOERS
chmod 440 /etc/sudoers.d/jenkins-indistylex

echo "==> Adding jenkins to www-data group for deploy script…"
usermod -aG www-data jenkins || true

systemctl enable jenkins
systemctl restart jenkins

echo ""
echo "=============================================="
echo " Jenkins installed."
echo " URL:  http://$(hostname -I | awk '{print $1}'):${JENKINS_PORT}"
echo " Initial admin password:"
cat /var/lib/jenkins/secrets/initialAdminPassword
echo ""
echo " Next steps:"
echo "  1. Open Jenkins UI and complete setup wizard"
echo "  2. Install suggested plugins + Pipeline"
echo "  3. New Item → Pipeline → name: indistylex-deploy"
echo "  4. Pipeline script from SCM → Git"
echo "     Repo: https://github.com/shivam74826/Indistylex.git"
echo "     Branch: develop"
echo "     Script path: Jenkinsfile"
echo "  5. Build with Parameters → DEPLOY_TARGET=local"
echo "=============================================="
