pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  securityContext:
                    runAsNonRoot: true
                    runAsUser: 1000
                    fsGroup: 1000
                    runAsGroup: 1000
                  containers:
                  - name: podman
                    image: quay.io/podman/stable:latest
                    command:
                    - sleep
                    args:
                    - 99d
                    securityContext:
                      runAsNonRoot: true
                      runAsUser: 1000
                      allowPrivilegeEscalation: false
                      capabilities:
                        drop:
                        - ALL
                    volumeMounts:
                    - name: podman-storage
                      mountPath: /var/lib/containers
                  - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - sleep
                    args:
                    - 99d
                    securityContext:
                      runAsNonRoot: true
                      runAsUser: 1000
                      allowPrivilegeEscalation: false
                      capabilities:
                        drop:
                        - ALL
                  - name: helm
                    image: alpine/helm:latest
                    command:
                    - sleep
                    args:
                    - 99d
                    securityContext:
                      runAsNonRoot: true
                      runAsUser: 1000
                      allowPrivilegeEscalation: false
                      capabilities:
                        drop:
                        - ALL
                  volumes:
                  - name: podman-storage
                    emptyDir:
                      sizeLimit: 5Gi
            '''
        }
    }
    
    environment {
        REGISTRY = 'c8n.io'
        REGISTRY_CRED = 'c8n-registry'
        NAMESPACE_DEV = 'dev'
        NAMESPACE_QA = 'qa'
        NAMESPACE_STAGING = 'staging'
        NAMESPACE_PROD = 'prod'
    }
    
    stages {
        stage('Info') {
            steps {
                script {
                    echo "Branch: ${env.BRANCH_NAME ?: env.GIT_BRANCH}"
                    echo "Build: ${env.BUILD_NUMBER}"
                    echo "Workspace: ${env.WORKSPACE}"
                    
                    // Déterminer la branche
                    def branchName = env.BRANCH_NAME ?: env.GIT_BRANCH
                    if (branchName?.startsWith('origin/')) {
                        branchName = branchName.replace('origin/', '')
                    }
                    env.CLEAN_BRANCH = branchName
                    echo "Clean Branch: ${env.CLEAN_BRANCH}"
                }
            }
        }
        
        stage('Build Cast Service') {
            steps {
                container('podman') {
                    script {
                        dir('cast-service') {
                            withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                                sh '''
                                    echo "Podman Version "
                                    podman --version
                                    
                                    echo "Configure Podman Storage"
                                    mkdir -p ~/.config/containers
                                    echo '[storage]' > ~/.config/containers/storage.conf
                                    echo 'driver = "vfs"' >> ~/.config/containers/storage.conf
                                    
                                    echo "Login to Registry"
                                    echo $PASS | podman login --username $USER --password-stdin $REGISTRY
                                    
                                    echo "Prepare Clean Username"
                                    CLEAN_USER=$(echo $USER | cut -d'@' -f1)
                                    echo "Clean user for image: $CLEAN_USER"
                                    
                                    echo "Build Cast Service "
                                    podman build -t $REGISTRY/$CLEAN_USER/cast-service:$BUILD_NUMBER .
                                    
                                    echo "Push Image"
                                    podman push $REGISTRY/$CLEAN_USER/cast-service:$BUILD_NUMBER
                                    
                                    echo "Cast Service built and pushed"
                                '''
                            }
                        }
                    }
                }
            }
        }
        
        stage('Build Movie Service') {
            steps {
                container('podman') {
                    script {
                        dir('movie-service') {
                            withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                                sh '''
                                    echo "Prepare Clean Username"
                                    CLEAN_USER=$(echo $USER | cut -d'@' -f1)
                                    
                                    echo "Build Movie Service"
                                    podman build -t $REGISTRY/$CLEAN_USER/movie-service:$BUILD_NUMBER .
                                    
                                    echo "Push Image"
                                    podman push $REGISTRY/$CLEAN_USER/movie-service:$BUILD_NUMBER
                                    
                                    echo " Movie Service built and pushed"
                                '''
                            }
                        }
                    }
                }
            }
        }
        
        stage('Deploy to DEV') {
            when {
                anyOf {
                    expression { env.CLEAN_BRANCH == 'develop' }
                    expression { env.CLEAN_BRANCH == 'main' }
                    expression { env.CLEAN_BRANCH == 'master' }
                }
            }
            steps {
                container('kubectl') {
                    script {
                        withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh '''
                                echo " Deploying to DEV namespace"
                                CLEAN_USER=$(echo $USER | cut -d'@' -f1)
                                
                                echo "Creating/updating deployments..."
                                
                                # Cast Service Deployment
                                kubectl create deployment cast-service \
                                  --image=$REGISTRY/$CLEAN_USER/cast-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_DEV \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                # Movie Service Deployment  
                                kubectl create deployment movie-service \
                                  --image=$REGISTRY/$CLEAN_USER/movie-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_DEV \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                # Expose services
                                kubectl expose deployment cast-service \
                                  --port=8000 --target-port=8000 --type=ClusterIP \
                                  --namespace=$NAMESPACE_DEV \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                  
                                kubectl expose deployment movie-service \
                                  --port=8001 --target-port=8001 --type=ClusterIP \
                                  --namespace=$NAMESPACE_DEV \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                echo "Successfully deploy to DEV!"
                                kubectl get pods -n $NAMESPACE_DEV
                                kubectl get services -n $NAMESPACE_DEV
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Deploy to QA') {
            when { 
                expression { env.CLEAN_BRANCH == 'develop' }
            }
            steps {
                container('kubectl') {
                    script {
                        withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh '''
                                echo "Deploying to QA namespace"
                                CLEAN_USER=$(echo $USER | cut -d'@' -f1)
                                
                                kubectl create deployment cast-service \
                                  --image=$REGISTRY/$CLEAN_USER/cast-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_QA \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                kubectl create deployment movie-service \
                                  --image=$REGISTRY/$CLEAN_USER/movie-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_QA \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                echo "Deployed to QA"
                                kubectl get pods -n $NAMESPACE_QA
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Deploy to PROD') {
            when { 
                anyOf {
                    expression { env.CLEAN_BRANCH == 'main' }
                    expression { env.CLEAN_BRANCH == 'master' }
                }
            }
            steps {
                input message: ' Deploy to PRODUCTION?', ok: 'DEPLOY'
                container('kubectl') {
                    script {
                        withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                            sh '''
                                echo "Deploying to PROD namespace"
                                CLEAN_USER=$(echo $USER | cut -d'@' -f1)
                                
                                kubectl create deployment cast-service \
                                  --image=$REGISTRY/$CLEAN_USER/cast-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_PROD \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                kubectl create deployment movie-service \
                                  --image=$REGISTRY/$CLEAN_USER/movie-service:$BUILD_NUMBER \
                                  --namespace=$NAMESPACE_PROD \
                                  --dry-run=client -o yaml | kubectl apply -f -
                                
                                echo "Successfully deployed to PRODUCTION"
                                kubectl get pods -n $NAMESPACE_PROD
                            '''
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            script {
                withCredentials([usernamePassword(credentialsId: REGISTRY_CRED, passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    def cleanUser = env.USER.split('@')[0]
                    echo "🐳 Images created:"
                    echo "- c8n.io/${cleanUser}/cast-service:${BUILD_NUMBER}"
                    echo "- c8n.io/${cleanUser}/movie-service:${BUILD_NUMBER}"
                    
                    if (env.CLEAN_BRANCH == 'main' || env.CLEAN_BRANCH == 'master') {
                        echo "🚀 Deployed to DEV and ready for PROD approval"
                    } else if (env.CLEAN_BRANCH == 'develop') {
                        echo "🚀 Deployed to DEV and QA"
                    } else {
                        echo "🚀 Deployed to DEV environment"
                    }
                }
            }
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            container('podman') {
                sh '''
                    mkdir -p ~/.config/containers
                    echo '[storage]' > ~/.config/containers/storage.conf
                    echo 'driver = "vfs"' >> ~/.config/containers/storage.conf
                    
                    podman system prune -f || true
                '''
            }
        }
    }
}
