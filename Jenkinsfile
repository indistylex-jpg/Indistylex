pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'development = run tests only | staging = deploy develop | production = deploy main'
        )
        choice(
            name: 'ROLLOUT_ACTION',
            choices: ['deploy', 'rollback', 'dry-run', 'restart-only', 'health-check'],
            description: 'deploy = git pull + restart | rollback = previous deploy | dry-run = plan only'
        )
        choice(
            name: 'DEPLOY_TARGET',
            choices: ['remote', 'local'],
            description: 'remote = SSH from laptop to server | local = run on server Jenkins (no SSH)'
        )
        booleanParam(
            name: 'RUN_MIGRATIONS',
            defaultValue: false,
            description: 'Run optional SQL migrations (MySQL only, staging/production)'
        )
        booleanParam(
            name: 'AUTO_ROLLBACK_ON_FAILURE',
            defaultValue: false,
            description: 'If health check fails after deploy, automatically rollback'
        )
        string(
            name: 'GIT_REMOTE',
            defaultValue: 'shivam74826',
            description: 'Git remote on server (passwordless pull must already be configured)'
        )
    }

    environment {
        APP_DIR = '/var/www/html/indistylex'
        PRODUCTION_HOST = '138.201.50.228'
        PRODUCTION_USER = 'root'
        SSH_CREDENTIAL = 'indistylex-server-ssh'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Plan') {
            steps {
                script {
                    def branchMap = [
                        development: 'develop (tests only)',
                        staging      : 'develop',
                        production   : 'main'
                    ]
                    echo """
=== Indistylex Deploy Plan ===
Environment     : ${params.ENVIRONMENT}
Branch target   : ${branchMap[params.ENVIRONMENT]}
Rollout action  : ${params.ROLLOUT_ACTION}
Deploy target   : ${params.DEPLOY_TARGET}
Git remote      : ${params.GIT_REMOTE}
Run migrations  : ${params.RUN_MIGRATIONS}
Auto rollback   : ${params.AUTO_ROLLBACK_ON_FAILURE}
Server          : ${PRODUCTION_HOST}
App directory   : ${APP_DIR}
"""
                }
            }
        }

        stage('Development — Tests') {
            when {
                expression { params.ENVIRONMENT == 'development' && params.ROLLOUT_ACTION == 'deploy' }
            }
            steps {
                sh '''
                    set -e
                    echo "[test] Running Indistylex test suite…"
                    if [[ ! -d .testvenv ]]; then
                      python3 -m venv .testvenv
                    fi
                    . .testvenv/bin/activate
                    pip install -q -r requirements.txt
                    pip install -q pytest pytest-cov 2>/dev/null || pip install -q pytest
                    pytest tests/ -q --tb=short
                    echo "[test] All tests passed."
                '''
            }
        }

        stage('Deploy') {
            when {
                expression { params.ENVIRONMENT != 'development' }
            }
            steps {
                script {
                    if (params.DEPLOY_TARGET == 'local' && !fileExists(env.APP_DIR)) {
                        error("""
DEPLOY_TARGET=local only works when Jenkins runs ON the server (${env.APP_DIR} must exist).
On your laptop, use DEPLOY_TARGET=remote and add credential ${env.SSH_CREDENTIAL}.
Run: cd jenkins && ./setup-server-ssh-credential.sh
""")
                    }

                    def deployEnv = [
                        "ENVIRONMENT=${params.ENVIRONMENT}",
                        "ROLLOUT_ACTION=${params.ROLLOUT_ACTION}",
                        "GIT_REMOTE=${params.GIT_REMOTE}",
                        "RUN_MIGRATIONS=${params.RUN_MIGRATIONS}",
                        "APP_DIR=${APP_DIR}"
                    ].join(' ')

                    if (params.DEPLOY_TARGET == 'remote') {
                        sshagent(credentials: [env.SSH_CREDENTIAL]) {
                            sh """
                                ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20 \\
                                    ${PRODUCTION_USER}@${PRODUCTION_HOST} \\
                                    '${deployEnv} bash -s' < jenkins/deploy.sh
                            """
                        }
                    } else {
                        sh """
                            ${deployEnv} bash ${APP_DIR}/jenkins/deploy.sh
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                if (params.ENVIRONMENT == 'development' && params.ROLLOUT_ACTION == 'deploy') {
                    echo 'Development pipeline passed — tests green.'
                } else {
                    echo "${params.ROLLOUT_ACTION} on ${params.ENVIRONMENT} succeeded."
                }
            }
        }
        failure {
            script {
                def canRollback = params.ROLLOUT_ACTION == 'deploy' &&
                    params.AUTO_ROLLBACK_ON_FAILURE &&
                    params.ENVIRONMENT != 'development'

                if (canRollback) {
                    echo 'Deploy failed — attempting automatic rollback…'
                    try {
                        def deployEnv = [
                            "ENVIRONMENT=${params.ENVIRONMENT}",
                            "ROLLOUT_ACTION=rollback",
                            "GIT_REMOTE=${params.GIT_REMOTE}",
                            "APP_DIR=${APP_DIR}"
                        ].join(' ')

                        if (params.DEPLOY_TARGET == 'remote') {
                            sshagent(credentials: [env.SSH_CREDENTIAL]) {
                                sh """
                                    ssh -o StrictHostKeyChecking=accept-new \\
                                        ${PRODUCTION_USER}@${PRODUCTION_HOST} \\
                                        '${deployEnv} bash -s' < jenkins/deploy.sh
                                """
                            }
                        } else {
                            sh "${deployEnv} bash ${APP_DIR}/jenkins/deploy.sh"
                        }
                        echo 'Automatic rollback completed.'
                    } catch (err) {
                        echo "Automatic rollback also failed: ${err}"
                    }
                } else {
                    echo 'Pipeline failed — check console output.'
                    echo 'Manual rollback: Build with Parameters → ROLLOUT_ACTION=rollback'
                }
            }
        }
    }
}
