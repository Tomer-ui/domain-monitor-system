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
                    withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
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
                        def dockerUserLower = DOCKER_USER.toLowerCase()
                        sh "docker run -d --name test-container -p 8080:8080 ${dockerUserLower}/${IMAGE_REPO}:${commitId}"

                        try {
                            sleep 10
                            
                            // FIX: Create the virtual environment and install requirements
                            // by calling the venv's pip directly, avoiding the 'source' command.
                            echo "--- Preparing Test Environment ---"
                            sh """
                                python3 -m venv test_venv
                                test_venv/bin/pip install -r tests/requirements.txt
                            """

                            // FIX: Run tests by calling the python executable from the venv directly.
                            echo "--- Running API Tests ---"
                            sh "test_venv/bin/python3 tests/test_api.py"

                            echo "--- Running UI Tests ---"
                            sh "test_venv/bin/python3 tests/test_ui.py"
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
                    def dockerUserLower = DOCKER_USER.toLowerCase()
                    echo "--- Final Workspace Cleanup ---"
                    sh "docker rmi ${dockerUserLower}/${IMAGE_REPO}:${commitId} || true"
                    cleanWs()
                }
            }
        }
    }
}