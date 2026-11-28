
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    docker run --rm \
                    -v "$WORKSPACE:/app" \
                    -w /app \
                    python:3.12-slim \
                    sh -c "pip install --no-cache-dir -r requirements.txt && python -m unittest discover -s . -p 'test_*.py' -v"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                    -t student-management:${BUILD_NUMBER} \
                    -t student-management:latest .
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker volume create student-data

                    docker rm -f student-app || true

                    docker run -d \
                    --restart unless-stopped \
                    -p 5000:5000 \
                    -v student-data:/app/instance \
                    --name student-app \
                    student-management:latest
                '''
            }
        }
    }
}
