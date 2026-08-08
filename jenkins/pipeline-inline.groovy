// Paste this in Jenkins job → Pipeline → Definition: "Pipeline script" (no Git plugin needed)
pipeline {
    agent any

    parameters {
        choice(name: 'BRANCH', choices: ['develop', 'main'], description: 'Branch to deploy')
        choice(name: 'GIT_REMOTE', choices: ['shivam74826', 'origin'], description: 'Git remote on server')
    }

    environment {
        APP_DIR = '/var/www/html/indistylex'
        PRODUCTION_HOST = '138.201.50.228'
        PRODUCTION_USER = 'root'
    }

    stages {
        stage('Deploy to production') {
            steps {
                sshagent(credentials: ['indistylex-server-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=accept-new \\
                            ${PRODUCTION_USER}@${PRODUCTION_HOST} \\
                            'APP_DIR=${APP_DIR} GIT_REMOTE=${params.GIT_REMOTE} BRANCH=${params.BRANCH} RUN_MIGRATIONS=false bash -s' \\
                            < ${WORKSPACE}/jenkins/deploy.sh
                    """
                }
            }
        }
    }
}
