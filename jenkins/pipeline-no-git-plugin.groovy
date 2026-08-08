// Works WITHOUT Git SCM plugin — copy entire file into Jenkins UI.
// Job → Pipeline → Definition: "Pipeline script" (NOT "from SCM")
pipeline {
    agent any

    parameters {
        choice(name: 'BRANCH', choices: ['develop', 'main'], description: 'Branch to deploy')
        choice(name: 'GIT_REMOTE', choices: ['shivam74826', 'origin'], description: 'Git remote on server')
    }

    stages {
        stage('Deploy to production') {
            steps {
                sshagent(credentials: ['indistylex-server-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=accept-new root@138.201.50.228 bash -s <<'EOF'
set -e
APP_DIR=/var/www/html/indistylex
GIT_REMOTE=shivam74826
BRANCH=develop
cd "$APP_DIR"
git fetch "$GIT_REMOTE" "$BRANCH"
git checkout "$BRANCH"
git pull "$GIT_REMOTE" "$BRANCH"
source venv/bin/activate
pip install -r requirements.txt -q
chown -R www-data:www-data "$APP_DIR"
systemctl restart indistylex
systemctl is-active indistylex && echo "Deploy OK"
EOF
                    '''
                }
            }
        }
    }
}
