// ===== פונקציית ולידציית מייל =====
def isValidEmail(String email) {
    if (!email) return false
    return email ==~ /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/
}

pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline')
        string(name: 'REPORT_EMAIL', defaultValue: '', description: 'Mail to send report to')
    }

    environment {
        LOG_DIR  = "logs"
        LOG_FILE = "logs/run_${BUILD_NUMBER}.log"
        PUBLIC_BASE_URL = "https://jerrica-gargantuan-nonclinically.ngrok-free.dev"
    }

    stages {

        stage('Checkout') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage('Validate Parameters') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'if not exist %LOG_DIR% mkdir %LOG_DIR%'
                        bat 'echo ===== PIPELINE START ===== > %LOG_FILE%'
                        bat 'echo Build: %BUILD_NUMBER% >> %LOG_FILE%'
                        bat 'echo Date: %DATE% %TIME% >> %LOG_FILE%'
                    } else {
                        sh '''
                        mkdir -p logs
                        echo "===== PIPELINE START =====" > logs/run_${BUILD_NUMBER}.log
                        echo "Build: ${BUILD_NUMBER}" >> logs/run_${BUILD_NUMBER}.log
                        date >> logs/run_${BUILD_NUMBER}.log
                        '''
                    }

                    env.MAIL_OK = "false"
                    env.MAIL_VALUE = params.REPORT_EMAIL?.trim()

                    def email = env.MAIL_VALUE
                    def valid = isValidEmail(email)

                    if (!email) {
                        echo "[MAIL] No email provided"
                    } else if (!valid) {
                        echo "[MAIL] Invalid email: ${email}"
                    } else {
                        env.MAIL_OK = "true"
                        echo "[MAIL] Valid email: ${email}"
                    }
                }
            }
        }

        stage('Run Script') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'py -3 --version >> %LOG_FILE% 2>&1'
                        bat 'py -3 main.py --date %RUN_DATE% --log-file %LOG_FILE%'
                    } else {
                        sh 'python3 --version | tee -a ${LOG_FILE}'
                        sh 'python3 main.py --date ${RUN_DATE} --log-file ${LOG_FILE}'
                    }
                }
            }
        }

        stage('Generate HTML') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'py -3 main.py --refresh-html --log-file %LOG_FILE%'
                    } else {
                        sh 'python3 main.py --refresh-html --log-file ${LOG_FILE}'
                    }
                }
            }
        }
    }

    post {
        always {
            node(params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in') {

                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'echo ===== PIPELINE END ===== >> %LOG_FILE%'
                    } else {
                        sh 'echo "===== PIPELINE END =====" | tee -a ${LOG_FILE}'
                    }
                }

                archiveArtifacts artifacts: 'pdf_reports/**, report.html, logs/*.log', fingerprint: true

                publishHTML(target: [
                    reportName : "Reports",
                    reportDir  : ".",
                    reportFiles: "report.html",
                    keepAll    : true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])

                script {
                    if (env.MAIL_OK == "true") {

                        def reportUrl = "${env.PUBLIC_BASE_URL}/job/${env.JOB_NAME}/${env.BUILD_NUMBER}/Reports/"

                        mail (
                            to: env.MAIL_VALUE,
                            from: "moradiasaf@gmail.com",
                            subject: "Jenkins Report: Build #${BUILD_NUMBER} is ${currentBuild.currentResult}",
                            body: """The pipeline run #${BUILD_NUMBER} has finished with status: ${currentBuild.currentResult}.
Report link: ${reportUrl}"""
                        )
                    }
                }
            }
        }
    }
}
