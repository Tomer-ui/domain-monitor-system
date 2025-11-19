pipeline {
    // Agent definition: run on any worker node with the 'docker-worker' label.
    agent { label 'docker-worker' }

    // Environment variables available throughout the pipeline.
    environment {
        IMAGE_REPO = "domain-monitor-system"
        // *** IMPROVEMENT: Define commitId once for the whole pipeline ***
        // This variable is now available in all stages as env.commitId
        commitId = env.GIT_COMMIT.take(8)
    }

    // Trigger definition: automatically start the pipeline on a push to any branch.
    triggers {
        githubPush()
    }

    stages {
        // NOTE: The initial 'checkout' is handled automatically by Jenkins
        // when using 'Pipeline script from SCM'. An explicit checkout stage is not needed.

        stage('Build') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                        def dockerUserLower = DOCKER_USER.toLowerCase()
                        // Use the globally defined commitId from the environment block
                        echo "Building temporary image: ${dockerUserLower}/${IMAGE_REPO}:${env.commitId}"
                        sh "docker build -t ${dockerUserLower}/${IMAGE_REPO}:${env.commitId} ."
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                        def dockerUserLower = DOCKER_USER.toLowerCase()
                        
                        // Run the container in detached mode using the global commitId
                        sh "docker run -d --name test-container -p 8080:8080 ${dockerUserLower}/${IMAGE_REPO}:${env.commitId}"

                        // The 'try/finally' block is crucial for cleanup.
                        try {
                            // Give the application a moment to start up inside the container.
                            sleep 10
                            
                            echo "--- Preparing Test Environment ---"
                            sh """
                                python3 -m venv test_venv
                                test_venv/bin/pip install -r tests/requirements.txt
                            """

                            echo "--- Running API Tests ---"
                            sh "test_venv/bin/python3 tests/test_api.py"

                            echo "--- Running UI Tests ---"
                            sh "test_venv/bin/python3 tests/test_ui.py"
                        } finally {
                            // This runs whether tests succeed or fail, great for debugging.
                            echo "--- Capturing Application Logs from test-container ---"
                            sh "docker logs test-container"
                            
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
                    // Create a semantic version using the build number for uniqueness.
                    def version = "1.0.${env.BUILD_NUMBER}"

                    withCredentials([
                        usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS'),
                        string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')
                    ]) {
                        def dockerUserLower = DOCKER_USER.toLowerCase()

                        // Log in to Docker Hub.
                        sh "docker login -u ${USER} -p ${PASS}"
                        echo "Publishing image ${dockerUserLower}/${IMAGE_REPO}:${version}"

                        // Tag the temporary image (using global commitId) with the new version and 'latest'.
                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${env.commitId} ${dockerUserLower}/${IMAGE_REPO}:${version}"
                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${env.commitId} ${dockerUserLower}/${IMAGE_REPO}:latest"

                        // Push both tags to Docker Hub.
                        sh "docker push ${dockerUserLower}/${IMAGE_REPO}:${version}"
                        sh "docker push ${dockerUserLower}/${IMAGE_REPO}:latest"
                    }
                }
            }
        }
    }

    // The 'post' block runs after all stages are complete.
    post {
        // 'always' means this will run for SUCCESS, FAILURE, or ABORTED builds.
        always {
            script {
                withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                    def dockerUserLower = DOCKER_USER.toLowerCase()
                    echo "--- Final Workspace Cleanup ---"
                    // Remove the temporary image using the global commitId
                    sh "docker rmi ${dockerUserLower}/${IMAGE_REPO}:${env.commitId} || true"
                    // Clean the Jenkins workspace to save disk space.
                    cleanWs()
                }
            }
        }
    }
}