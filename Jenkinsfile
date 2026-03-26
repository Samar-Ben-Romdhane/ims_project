pipeline {
    agent any

    stages {

        stage('Build') {
            steps {
                sh 'docker build -t ims_project .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop ims_container || true'
                sh 'docker rm ims_container || true'
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker run -d -p 8000:8000 --name ims_container ims_project'
            }
        }

    }
}

