pipeline {
    agent none 

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose execution environment [cite: 48]')
        string(name: 'REPORT_DATE', defaultValue: '11-01-2026', description: 'Enter date (DD-MM-YYYY) [cite: 37]')
    }

    stages {
        stage('Initialize & CSP Fix') {
            agent { label 'built-in' } // ריצה על המאסטר [cite: 21]
            steps {
                script {
                    // שחרור חסימת האבטחה להצגת HTML [cite: 40]
                    System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
                }
            }
        }

        stage('Checkout') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                checkout scm // משיכת קוד מ-GitHub [cite: 15, 51]
            }
        }

        stage('Cleanup & Validate') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    // וולידציה של הפרמטרים - דרישה של 10% מהציון [cite: 39, 52]
                    if (params.REPORT_DATE == "") {
                        error "Validation Failed: REPORT_DATE is missing [cite: 61]"
                    }
                    
                    echo "Cleaning previous reports... [cite: 41]"
                    if (params.RUN_ON == 'windows') {
                        bat 'if exist pdf_reports rmdir /s /q pdf_reports'
                        bat 'if exist report.html del report.html'
                    } else {
                        sh 'rm -rf pdf_reports report.html'
                    }
                }
            }
        }

        stage('Run Script') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    // הרצת התסריט ויצירת הפלט - דרישה של 30% [cite: 53, 54]
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
                // ארכוב קבצים ולוגים - חובה לפי סעיף 4.1 [cite: 42]
                archiveArtifacts artifacts: 'pdf_reports/**, report.html, *.log', fingerprint: true
                
                // פרסום הדוח ב-Jenkins UI [cite: 13, 99]
                publishHTML(target: [
                    reportName : "Final Reports Output",
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
