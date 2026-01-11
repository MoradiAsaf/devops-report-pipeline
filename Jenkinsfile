pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Run Script') {
            steps {
                sh 'python3 main.py'
            }
        }
    }
}
