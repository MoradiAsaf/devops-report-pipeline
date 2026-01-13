pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline')
        string(name: 'REPORT_EMAIL', defaultValue: 'moradiasaf@gmail.com', description: 'Mail to send report to')
    }

    environment {
        LOG_DIR  = "logs"
        LOG_FILE = "logs/run_${BUILD_NUMBER}.log"
        PUBLIC_BASE_URL = "https://jerrica-gargantuan-nonclinically.ngrok-free.dev"
    }

    stages {

        stage('Run on selected agent') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }

            steps {

                //  ניקוי מלא של סביבת העבודה לפני הריצה
                deleteDir()

                // משיכת הקוד מחדש
                checkout scm

                // ===== יצירת לוג אחרי הניקוי =====
                script {
                    if (params.RUN_ON == 'windows') {
                        bat """
                        if not exist %LOG_DIR% mkdir %LOG_DIR%
                        echo ===== PIPELINE START ===== > %LOG_FILE%
                        echo Build: %BUILD_NUMBER% >> %LOG_FILE%
                        echo Date: %DATE% %TIME% >> %LOG_FILE%
                        """
                    } else {
                        sh """
                        mkdir -p ${LOG_DIR}
                        echo "===== PIPELINE START =====" > ${LOG_FILE}
                        echo "Build: ${BUILD_NUMBER}" >> ${LOG_FILE}
                        date >> ${LOG_FILE}
                        """
                    }
                }

                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'echo Workspace cleaned repo checked out >> %LOG_FILE%'
                    } else {
                        sh 'echo "Workspace cleaned & repo checked out" >> ${LOG_FILE}'
                    }
                }

                // ===== בדיקת פייתון =====
                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'py -3 --version >> %LOG_FILE% 2>&1'
                    } else {
                        sh 'python3 --version | tee -a ${LOG_FILE}'
                    }
                }

                // ===== הרצת הסקריפט =====
                script {
                    if (params.RUN_ON == 'windows') {
                        bat """
                        py -3 main.py --date %RUN_DATE% --log-file %LOG_FILE%
                        """
                    } else {
                        sh """
                       python3 main.py --date ${RUN_DATE} --log-file ${LOG_FILE}
                        """
                    }
                }
            }

            post {
    always {

        // ===== סיום לוג =====
        script {
            if (params.RUN_ON == 'windows') {
                bat 'echo ===== PIPELINE END ===== >> %LOG_FILE%'
            } else {
                sh 'echo "===== PIPELINE END =====" | tee -a ${LOG_FILE}'
            }
        }

        // 📦 ארכוב דוחות + לוגים
        archiveArtifacts artifacts: 'pdf_reports/**, report.html, logs/*.log', fingerprint: true

        // 🌐 פרסום דוח HTML
        publishHTML(target: [
            reportName : "Reports",
            reportDir  : ".",
            reportFiles: "report.html",
            keepAll    : true,
            alwaysLinkToLastBuild: true,
            allowMissing: false
        ])

        // 📧 שליחת מייל עם הדוח
        emailext(
            to: "${params.REPORT_EMAIL}",
            subject: "📊 Jenkins Report - ${JOB_NAME} #${BUILD_NUMBER} - ${currentBuild.currentResult}",
            mimeType: 'text/html',
            body: '${FILE,path="report.html"}'
        )
    }
}


        }
    }
}
