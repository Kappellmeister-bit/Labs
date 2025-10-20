pipeline {
  agent any
  stages {
    stage('Checkout'){ steps { checkout scm } }
    stage('Setup'){ steps {
      sh 'python3 -m pip install --upgrade pip'
      sh 'python3 -m pip install -r requirements.txt'
    }}
    stage('Test'){
      environment { PYTHONPATH = '.' }
      steps { sh 'pytest -q --junitxml=test-results/junit.xml' }
      post { always { junit 'test-results/junit.xml' } }
    }
  }
}
