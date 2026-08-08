pipeline {
    agent any

    parameters {
        choice(
            name: 'BRANCH',
            choices: ['develop', 'main'],
            description: 'Git branch to deploy'
        )
        booleanParam(
            name: 'RUN_MIGRATIONS',
            defaultValue: false,
            description: 'Run optional SQL migrations (MySQL only)'
        )
        choice(
            name: 'DEPLOY_TARGET',
            choices: ['local', 'production'],
            description: 'local = this machine app dir; production = SSH to server'
        )
        string(
            name: 'GIT_REMOTE',
            defaultValue: 'origin',
            description: 'Git remote name (use shivam74826 on server if configured)'
        )
    }

    environment {
        APP_DIR = '/var/www/html/indistylex'
        PRODUCTION_HOST = '138.201.50.228'
        PRODUCTION_USER = 'root'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Deploy') {
            steps {
                script {
                    if (params.DEPLOY_TARGET == 'production') {
                        sshagent(credentials: ['indistylex-server-ssh']) {
                            sh """
                                ssh -o StrictHostKeyChecking=accept-new \\
                                    ${PRODUCTION_USER}@${PRODUCTION_HOST} \\
                                    'APP_DIR=${APP_DIR} GIT_REMOTE=${params.GIT_REMOTE} BRANCH=${params.BRANCH} RUN_MIGRATIONS=${params.RUN_MIGRATIONS} bash -s' \\
                                    < jenkins/deploy.sh
                            """
                        }
                    } else {
                        sh """
                            sudo APP_DIR=${APP_DIR} \\
                            GIT_REMOTE=${params.GIT_REMOTE} \\
                            BRANCH=${params.BRANCH} \\
                            RUN_MIGRATIONS=${params.RUN_MIGRATIONS} \\
                            bash ${APP_DIR}/jenkins/deploy.sh
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Deployed ${params.BRANCH} to ${params.DEPLOY_TARGET} successfully."
        }
        failure {
            echo 'Deploy failed — check console output and journalctl -u indistylex on the server.'
        }
    }
}
