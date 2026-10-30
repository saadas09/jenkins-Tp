pipeline {
    agent { label "${params.AGENT_LABEL}" } 
    options {
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        skipDefaultCheckout(true)
    }
  
    stages {
        stage('Checkout') {
            steps {
                bat 'if exist prix.xml del /q prix.xml\r\nif exist api.xml del /q api.xml\r\nif exist coverage.xml del /q coverage.xml'
                checkout scm
                bat '''@echo off
hostname
echo NODE_NAME=%NODE_NAME%
echo WORKSPACE=%WORKSPACE%
git rev-parse HEAD
'''
            }
        }
        stage('Installation') {
            steps {
                bat 'py -3.12 -m venv .venv'
                bat '".venv\\Scripts\\python.exe" -m pip install -r requirements-dev.txt'
            }
        }
        stage('Tests paralleles') {
            when {
  expression {
    def files = []
    for (cs in currentBuild.changeSets) {
      for (item in cs.items) {
        files.addAll(item.affectedPaths)
      }
    }
    return files.isEmpty() ||
      files.any { it != 'README.md' }
  }
}
            parallel {
                stage('Regles de prix') {
                    steps {
                        bat '".venv\\Scripts\\python.exe" -m pytest tests/test_prix.py --junitxml=prix.xml -v'
                    }
                }
                stage('API et couverture') {
                    steps {
                        bat '".venv\\Scripts\\python.exe" -m pytest tests/test_api.py --junitxml=api.xml --cov=app --cov-report=xml:coverage.xml --cov-report=term -v'
                    }
                }
            }
        }
        stage('Livraison') {
            steps {
                bat 'docker compose -p campus-cafe up -d --build'
                bat '".venv\\Scripts\\python.exe" smoke.py'
            }
        }
    }
    post {
        always {
            junit testResults: 'prix.xml,api.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'prix.xml,api.xml,coverage.xml', allowEmptyArchive: true
        }
    }
}
