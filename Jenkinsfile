pipeline {
    agent none

    parameters {
        choice(name: 'RUN_ON', choices: ['linux', 'windows'], description: 'Choose where to run the pipeline')
    }

    stages {
        stage('Initialize & Clean CSP') {
            agent { label 'built-in' } // רץ על המאסטר כדי לשנות הגדרות מערכת
            steps {
                script {
                    // פקודה זו משחררת את חסימת ה-CSP של ג'נקינס ומאפשרת לקישורים ב-HTML לעבוד
                    System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
                    echo "Jenkins CSP protection has been relaxed for HTML reports."
                }
            }
        }

        stage('Run on selected agent') {
            agent { label params.RUN_ON == 'windows' ? 'windows-agent' : 'built-in' }

            steps {
                checkout scm

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
                    // ארכוב התוצרים
                    archiveArtifacts artifacts: 'pdf_reports/**, report.html', fingerprint: true

                    // פרסום דף ה-HTML
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
