pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline [cite: 48]')
        string(name: 'REPORT_DATE', defaultValue: '11-01-2026', description: 'Enter date (DD-MM-YYYY) [cite: 37]')
    }

    stages {
        stage('Initialize & CSP Fix') {
            agent { label 'built-in' } 
            steps {
                script {
                    // שחרור חסימת האבטחה של ג'נקינס כדי לאפשר תצוגת HTML וקישורים תקינה
                    System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
                    echo "Jenkins CSP protection has been relaxed."
                }
            }
        }

        stage('Cleanup & Checkout') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    echo "Cleaning Workspace to avoid old reports..."
                    if (params.RUN_ON == 'windows') {
                        // ניקוי תיקיות וקבצים ישנים בווינדוס
                        bat 'if exist pdf_reports rmdir /s /q pdf_reports'
                        bat 'if exist report.html del report.html'
                    } else {
                        // ניקוי בלינוקס
                        sh 'rm -rf pdf_reports report.html'
                    }
                }
                checkout scm [cite: 51]
            }
        }

        stage('Run Script') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    // הרצת הסקריפט עם הפרמטרים שהוזנו [cite: 53]
                    if (params.RUN_ON == 'windows') {
                        bat "py -3 main.py --date ${params.REPORT_DATE}"
                    } else {
                        sh "python3 main.py --date ${params.REPORT_DATE}"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                // ארכוב התוצרים (PDF, HTML ולוגים) כפי שנדרש בסעיף 4.1 
                archiveArtifacts artifacts: 'pdf_reports/**, report.html, *.log', fingerprint: true
                
                // פרסום דוח ה-HTML [cite: 54]
                publishHTML(target: [
                    reportName : "Reports Output",
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
