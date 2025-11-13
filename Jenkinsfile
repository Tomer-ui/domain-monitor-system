pipeline {
    // 1. Tell Jenkins to run this pipeline on any agent with the 'docker-worker' label.
    agent { label 'docker-worker' }

    // 2. Define environment variables.
    environment {
        // Use Jenkins Credentials plugin for security. Create a 'Secret Text' credential with your Docker Hub username.
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        // We will generate the version number dynamically.
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/domain-monitor-system"
    }

    stages {
        // Stage 1: Checkout code from GitHub
        stage('Checkout') {
            steps {
                echo 'Checking out the code...'
                checkout scm
            }
        }

        // Stage 2: Build a temporary Docker image
        stage('Build') {
            steps {
                script {
                    // Use the short Git commit hash as a unique, temporary tag.
                    def commitId = env.GIT_COMMIT.take(8)
                    echo "Building temporary image: ${IMAGE_NAME}:${commitId}"
                    sh "docker build -t ${IMAGE_NAME}:${commitId} ."
                }
            }
        }

        // Stage 3: Run Tests
        stage('Test') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    // Run the application container in the background
                    sh "docker run -d --name test-container -p 8080:8080 ${IMAGE_NAME}:${commitId}"
                    
                    try {
                        // Wait a moment for the Flask app to start inside the container
                        sleep 10

                        echo "--- Running API Tests ---"
                        // Create a virtual environment, install dependencies, and run the API test script.
                        sh "python3 -m venv test_venv"
                        // Assumes you have a tests/requirements.txt file with dependencies like 'requests' and 'selenium'.
                        sh "source test_venv/bin/activate && pip install -r tests/requirements.txt && python3 tests/test_api.py"
                        
                        echo "--- Running UI Tests ---"
                        // Run the UI test script in the same virtual environment.
                        // The worker node must have Google Chrome and a compatible ChromeDriver installed for this to succeed.
                        sh "source test_venv/bin/activate && python3 tests/test_ui.py"

                    } catch (e) {
                        // If any test fails, print the error and fail the pipeline
                        echo "A test failed!"
                        echo e.getMessage()
                        error "Build failed due to test failures."
                    } finally {
                        // This block ALWAYS runs, ensuring cleanup happens.
                        echo "--- Cleaning up test container ---"
                        sh "docker stop test-container"
                        sh "docker rm test-container"
                    }
                }
            }
        }

        // Stage 4: Promote and Push to Docker Hub
        stage('Publish') {
            steps {
                script {
                    def commitId = env.GIT_COMMIT.take(8)
                    // Use the Jenkins build number for simple semantic versioning.
                    def version = "1.0.${env.BUILD_NUMBER}"
                    echo "Tests passed! Promoting image to version: ${version}"
                    
                    // Log in to Docker Hub using the 'Username with password' credential type.
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh "docker login -u ${USER} -p ${PASS}"
                    }
                    
                    // Re-tag the temporary image with the new version and 'latest'.
                    sh "docker tag ${IMAGE_NAME}:${commitId} ${IMAGE_NAME}:${version}"
                    sh "docker tag ${IMAGE_NAME}:${commitId} ${IMAGE_NAME}:latest"
                    
                    // Push both tags to Docker Hub.
                    sh "docker push ${IMAGE_NAME}:${version}"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }
    }
    
    // Post-build actions that run regardless of the pipeline's success or failure.
    post {
        always {
            script {
                echo "--- Final Workspace Cleanup ---"
                def commitId = env.GIT_COMMIT.take(8)
                // Remove the temporary Docker image from the worker node.
                sh "docker rmi ${IMAGE_NAME}:${commitId} || true" // '|| true' prevents failure if image doesn't exist
                // Jenkins' own cleanup
                cleanWs()
            }
        }
    }
}