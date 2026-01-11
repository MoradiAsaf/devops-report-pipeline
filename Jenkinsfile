pipeline {

    agent none

    parameters {
        choice(
            name: 'RUN_ON',
            choices: ['linux', 'windows'],
            description: 'Choose where to run the pipeline'
        )
    }

    stages {

        stage('Run on selected agent') {
            agent {
                label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in'
            }

            stages {

                stage('Checkout') {
                    steps {
                        checkout scm
                    }
                }

                stage('Environment') {
                    steps {
                        script {
                            if (params.RUN_ON == 'windows') {
                                bat 'python --version'
                            } else {
                                sh 'python3 --version'
                            }
                        }
                    }
                }

                stage('Run Script') {
                    steps {
                        script {
                            if (params.RUN_ON == 'windows') {
                                bat 'python main.py'
                            } else {
                                sh 'python3 main.py'
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/*.pdf, **/*.html, **/*.log', fingerprint: true
        }
    }
}
