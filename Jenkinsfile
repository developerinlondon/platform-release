pipeline {
  agent any
  options {
      ansiColor('xterm')
      timestamps()
  }

  stages {
    stage("Preparing Tests") {
      steps {
          println "Cloning cp-release"
          sh "git clone git@github.com:developerinlondon/platform-release.git"
      }
    }

    stage("Running Tests") {
      steps{
        script {
          println "Running test scenarios"
          dir('tests') {
            sh 'for i in test_*.py; do python $i; done'
          }
        }
      }
    }
  }
}
