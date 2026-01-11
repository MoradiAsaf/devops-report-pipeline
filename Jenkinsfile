pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline')
    }

    stages {

        stage('Run on selected agent') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }

            steps {
                // 🔥 ניקוי מלא של סביבת העבודה לפני הריצה
                deleteDir()

                // משיכת הקוד מחדש
                checkout scm

                // הרצת הסקריפט לפי מערכת הפעלה
                script {
                    if (params.RUN_ON == 'windows') {
                        bat 'py -3 --version'
                        bat 'py -3 main.py'
                    } else {
                        sh 'python3 --version'
                        sh 'python3 main.py'
                    }
                }
            }

            post {
                always {
                    // 📦 ארכוב כל הדוחות וה-HTML
                    archiveArtifacts artifacts: 'pdf_reports/**, report.html', fingerprint: true

                    // 🌐 פרסום דוח HTML בתוך Jenkins
                    publishHTML(target: [
                        reportName : "Reports",
                        reportDir  : ".",
                        reportFiles: "report.html",
                        keepAll    : true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: false
                    ])
                }
            }
        }
    }
}
