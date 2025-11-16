pipeline {
    agent { label 'docker-worker' }

    environment {
        IMAGE_REPO = "domain-monitor-system"
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out the code...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    // Use the secret safely via withCredentials
                    withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                        // FIX: Convert Docker username to lowercase
                        def dockerUserLower = DOCKER_USER.toLowerCase()
                        echo "Building temporary image: ${dockerUserLower}/${IMAGE_REPO}:${commitId}"
                        sh "docker build -t ${dockerUserLower}/${IMAGE_REPO}:${commitId} ."
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                        // FIX: Convert Docker username to lowercase
                        def dockerUserLower = DOCKER_USER.toLowerCase()
                        sh "docker run -d --name test-container -p 8080:8080 ${dockerUserLower}/${IMAGE_REPO}:${commitId}"

                        try {
                            sleep 10
                            echo "--- Running API Tests ---"
                            sh "python3 -m venv test_venv"
                            sh "source test_venv/bin/activate && pip install -r tests/requirements.txt && python3 tests/test_api.py"

                            echo "--- Running UI Tests ---"
                            sh "source test_venv/bin/activate && python3 tests/test_ui.py"
                        } finally {
                            echo "--- Cleaning up test container ---"
                            sh "docker stop test-container || true"
                            sh "docker rm test-container || true"
                        }
                    }
                }
            }
        }

        stage('Publish') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    def version = "1.0.${env.BUILD_NUMBER}"

                    withCredentials([
                        usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS'),
                        string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')
                    ]) {
                        // FIX: Convert Docker username to lowercase
                        def dockerUserLower = DOCKER_USER.toLowerCase()

                        sh "docker login -u ${USER} -p ${PASS}"
                        echo "Publishing image ${dockerUserLower}/${IMAGE_REPO}:${version}"

                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${commitId} ${dockerUserLower}/${IMAGE_REPO}:${version}"
                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${commitId} ${dockerUserLower}/${IMAGE_REPO}:latest"

                        sh "docker push ${dockerUserLower}/${IMAGE_REPO}:${version}"
                        sh "docker push ${dockerUserLower}/${IMAGE_REPO}:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def commitId = env.GIT_COMMIT.take(8)
                withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                    // FIX: Convert Docker username to lowercase
                    def dockerUserLower = DOCKER_USER.toLowerCase()
                    echo "--- Final Workspace Cleanup ---"
                    sh "docker rmi ${dockerUserLower}/${IMAGE_REPO}:${commitId} || true"
                    cleanWs()
                }
            }
        }
    }
}