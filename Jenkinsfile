pipeline {
    agent none 

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose execution environment')
        string(name: 'REPORT_DATE', defaultValue: '11-01-2026', description: 'Enter date (DD-MM-YYYY)')
    }

    stages {
        stage('Initialize & CSP Fix') {
            agent { label 'built-in' }
            steps {
                script {
                    System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
                }
            }
        }

        stage('Checkout') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                checkout scm
            }
        }

        stage('Cleanup & Validate') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }
            steps {
                script {
                    if (params.REPORT_DATE == "") {
                        error "Validation Failed: REPORT_DATE is missing"
                    }
                    
                    echo "Cleaning previous reports..." [cite: 41]
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
                    if (params.RUN_ON == 'windows') {
                        bat "py -3 main.py --date ${params.REPORT_DATE}"
                    } else {
                        sh "python3 main.py --date ${params.REPORT_DATE}"
                    }
                }
            }
        }
    }

    // התיקון כאן: הוספת agent לבלוק ה-post כדי שיוכל לגשת לקבצים
    post {
        always {
            node(params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in') {
                script {
                    // ארכוב תוצרים ולוגים כפי שנדרש בסעיף 4.1
                    archiveArtifacts artifacts: 'pdf_reports/**, report.html, *.log', fingerprint: true [cite: 42]
                    
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
}
