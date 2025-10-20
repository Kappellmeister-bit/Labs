pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Setup venv') {
      steps {
        sh '''
          set -e
          python3 -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Test') {
      environment { PYTHONPATH = '.' }
      steps {
        sh '''
          set -e
          . .venv/bin/activate
          python -m pytest -q --junitxml=test-results/junit.xml
        '''
      }
      post { always { junit 'test-results/junit.xml' } }
    }
  }
}
