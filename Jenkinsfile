pipeline {
    // Agent definition: run on any worker node with the 'docker-worker' label.
    agent { label 'docker-worker' }

    // Environment variables available throughout the pipeline.
    environment {
        IMAGE_REPO = "domain-monitor-system"
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
                    // Use the first 8 characters of the Git commit hash for a unique, temporary tag.
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
                        
                        // Run the container in detached mode (-d) so the pipeline can continue.
                        sh "docker run -d --name test-container -p 8080:8080 ${dockerUserLower}/${IMAGE_REPO}:${commitId}"

                        // The 'try/finally' block is crucial. The 'finally' section will run
                        // regardless of whether the tests in the 'try' block succeed or fail.
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
                            // *** IMPROVEMENT: CAPTURE CONTAINER LOGS ***
                            // This is the best place for debugging. It prints the application's
                            // logs before the container is removed.
                            echo "--- Capturing Application Logs from test-container ---"
                            sh "docker logs test-container"
                            
                            echo "--- Cleaning up test container ---"
                            // Use '|| true' to prevent the pipeline from failing if the container
                            // has already stopped or been removed for any reason.
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

                        // Tag the temporary commit-tagged image with the new version and 'latest'.
                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${commitId} ${dockerUserLower}/${IMAGE_REPO}:${version}"
                        sh "docker tag ${dockerUserLower}/${IMAGE_REPO}:${commitId} ${dockerUserLower}/${IMAGE_REPO}:latest"

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
                def commitId = env.GIT_COMMIT.take(8)
                withCredentials([string(credentialsId: 'dockerhub-username', variable: 'DOCKER_USER')]) {
                    def dockerUserLower = DOCKER_USER.toLowerCase()
                    echo "--- Final Workspace Cleanup ---"
                    // Remove the temporary image that was built at the start.
                    sh "docker rmi ${dockerUserLower}/${IMAGE_REPO}:${commitId} || true"
                    // Clean the Jenkins workspace to save disk space.
                    cleanWs()
                }
            }
        }
    }
}