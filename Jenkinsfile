pipeline {
    agent { label 'docker-worker' }

    environment {
        // Correctly load the credential into an environment variable.
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        // Define the image repo name SEPARATELY.
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
                    // **THE FIX**: Use shell variable syntax ($VAR) inside the sh step.
                    echo "Building temporary image: ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId}"
                    sh "docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId} ."
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    // **THE FIX**: Also applied here.
                    sh "docker run -d --name test-container -p 8080:8080 ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId}"
                    
                    try {
                        sleep 10
                        echo "--- Running API Tests ---"
                        sh "python3 -m venv test_venv"
                        sh "source test_venv/bin/activate && pip install -r tests/requirements.txt && python3 tests/test_api.py"
                        
                        echo "--- Running UI Tests ---"
                        sh "source test_venv/bin/activate && python3 tests/test_ui.py"
                    } finally {
                        echo "--- Cleaning up test container ---"
                        sh "docker stop test-container"
                        sh "docker rm test-container"
                    }
                }
            }
        }

        stage('Publish') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    def version = "1.0.${env.BUILD_NUMBER}"
                    echo "Tests passed! Promoting image to version: ${version}"
                    
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh "docker login -u ${USER} -p ${PASS}"
                    }
                    
                    // **THE FIX**: Also applied to tag and push commands.
                    sh "docker tag ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId} ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${version}"
                    sh "docker tag ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId} ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:latest"
                    
                    sh "docker push ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${version}"
                    sh "docker push ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:latest"
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "--- Final Workspace Cleanup ---"
                def commitId = env.GIT_COMMIT.take(8)
                // **THE FIX**: Also applied here.
                sh "docker rmi ${DOCKERHUB_USERNAME}/${IMAGE_REPO}:${commitId} || true"
                cleanWs()
            }
        }
    }
}