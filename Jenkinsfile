pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline [cite: 48, 58]')
        string(name: 'REPORT_DATE', defaultValue: '11-01-2026', description: 'Enter date (DD-MM-YYYY) [cite: 37]')
    }

    stages {
        stage('Initialize & CSP Fix') {
            agent { label 'built-in' } [cite: 21]
            steps {
                script {
                    // שחרור חסימת האבטחה להצגת HTML [cite: 40]
                    System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
                }
            }
        }

        stage('Checkout') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' } [cite: 48, 59]
            steps {
                checkout scm [cite: 51]
            }
        }

        stage('Cleanup & Validate') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    // וולידציה (דרישה של 10% מהציון) 
                    if (params.REPORT_DATE == "") {
                        error "Validation Failed: REPORT_DATE is missing [cite: 61]"
                    }
                    
                    echo "Cleaning Workspace..."
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
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' } [cite: 48]
            steps {
                script {
                    // הרצת התסריט (סעיף 4.1) [cite: 53]
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
                // ארכוב תוצרים ולוגים (דרישת חובה) [cite: 41, 42]
                archiveArtifacts artifacts: 'pdf_reports/**, report.html, *.log', fingerprint: true
                
                // יצירת הדו"ח בממשק (סעיף 4.1) [cite: 54]
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
