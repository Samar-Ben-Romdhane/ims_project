pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "samarbenromdhane/ims_project"
        KUBE_CONFIG = "/var/jenkins_home/.kube/config"
    }
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Samar-Ben-Romdhane/ims_project.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $DOCKER_IMAGE:latest .
                '''
            }
        }
        stage('Push to DockerHub') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push $DOCKER_IMAGE:latest
                        '''
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                export KUBECONFIG=$KUBE_CONFIG
                kubectl apply -f k8s/k8s-deployment.yaml
                '''
            }
        }
        stage('Verify Deployment') {
            steps {
                sh '''
                export KUBECONFIG=$KUBE_CONFIG
                kubectl get pods
                kubectl get svc
                '''
            }
        }
    }
}
