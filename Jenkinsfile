// =============================================================================
// Pipeline CI/CD — movie-service et cast-service
//
//   toutes branches : lint du chart, build des images, scan Trivy bloquant
//   develop         : + push des images, déploiement dev puis qa
//   main            : + push des images, déploiement staging,
//                       validation manuelle, déploiement prod
//
// Déploiement : helm upgrade --install --atomic (rollback automatique si les
// pods ne deviennent pas prêts).
// =============================================================================

SERVICES = ['movie-service', 'cast-service']   // variable globale du script, visible dans tous les blocs

// Déploie le chart dans un namespace avec les values de l'environnement
def helmDeploy(String namespace, String environment) {
    container('helm') {
        sh """
            helm upgrade --install movie-app ${env.CHART} \\
              --namespace ${namespace} \\
              --values ${env.CHART}/values-${environment}.yaml \\
              --set image.registry=${env.REGISTRY}/${env.IMAGE_NAMESPACE} \\
              --set image.tag=${env.IMAGE_TAG} \\
              --atomic --wait --timeout 5m
            helm status movie-app --namespace ${namespace}
        """
    }
}

pipeline {
    agent {
        kubernetes {
            yamlFile 'jenkins/agent-pod.yaml'
        }
    }

    options {
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        REGISTRY        = 'c8n.io'
        IMAGE_NAMESPACE = 'roxane451'       // compte sur la registry
        REGISTRY_CRED   = 'c8n-registry'    // credential Jenkins (username/password)
        CHART           = 'charts/movie-app'
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    env.BRANCH = (env.BRANCH_NAME ?: env.GIT_BRANCH ?: '').replaceFirst(/^origin\//, '')
                    def sha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    // Tag immuable : commit + numéro de build
                    env.IMAGE_TAG = "${sha}-${env.BUILD_NUMBER}"
                    env.PUBLISH = (env.BRANCH in ['develop', 'main']).toString()
                    echo "Branche : ${env.BRANCH} — images : ${env.IMAGE_TAG} — publication : ${env.PUBLISH}"
                }
            }
        }

        stage('Lint') {
            parallel {
                stage('Helm') {
                    steps {
                        container('helm') {
                            sh '''
                                for environment in dev qa staging prod; do
                                  helm lint "$CHART" --strict \
                                    --values "$CHART/values-$environment.yaml" \
                                    --set image.registry=lint.local/ci --set image.tag=lint
                                done
                            '''
                        }
                    }
                }
                stage('Config Nginx') {
                    steps {
                        // La passerelle Docker et le chart doivent servir la même configuration
                        sh 'diff -u nginx/nginx.conf "$CHART/files/nginx.conf"'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                container('podman') {
                    script {
                        SERVICES.each { svc ->
                            sh """
                                podman build --pull=always \\
                                  -t ${env.REGISTRY}/${env.IMAGE_NAMESPACE}/${svc}:${env.IMAGE_TAG} ${svc}
                                podman save -o ${svc}.tar ${env.REGISTRY}/${env.IMAGE_NAMESPACE}/${svc}:${env.IMAGE_TAG}
                            """
                        }
                    }
                }
            }
        }

        stage('Scan Trivy') {
            steps {
                container('trivy') {
                    script {
                        // Bloquant : aucune vulnérabilité HIGH/CRITICAL corrigeable
                        SERVICES.each { svc ->
                            sh "trivy image --input ${svc}.tar --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 --no-progress"
                        }
                    }
                }
            }
        }

        stage('Push') {
            when { expression { env.PUBLISH == 'true' } }
            steps {
                container('podman') {
                    withCredentials([usernamePassword(credentialsId: env.REGISTRY_CRED,
                                                      usernameVariable: 'REGISTRY_USER',
                                                      passwordVariable: 'REGISTRY_PASSWORD')]) {
                        sh 'printf "%s" "$REGISTRY_PASSWORD" | podman login --username "$REGISTRY_USER" --password-stdin "$REGISTRY"'
                    }
                    script {
                        SERVICES.each { svc ->
                            sh "podman push ${env.REGISTRY}/${env.IMAGE_NAMESPACE}/${svc}:${env.IMAGE_TAG}"
                        }
                    }
                }
            }
        }

        stage('Deploy dev') {
            when { expression { env.BRANCH == 'develop' } }
            steps { script { helmDeploy('dev', 'dev') } }
        }

        stage('Deploy qa') {
            when { expression { env.BRANCH == 'develop' } }
            steps { script { helmDeploy('qa', 'qa') } }
        }

        stage('Deploy staging') {
            when { expression { env.BRANCH == 'main' } }
            steps { script { helmDeploy('staging', 'staging') } }
        }

        stage('Validation production') {
            when { expression { env.BRANCH == 'main' } }
            options { timeout(time: 1, unit: 'HOURS') }
            steps {
                input message: "Déployer ${env.IMAGE_TAG} en production ?", ok: 'Déployer'
            }
        }

        stage('Deploy prod') {
            when { expression { env.BRANCH == 'main' } }
            steps { script { helmDeploy('prod', 'prod') } }
        }
    }

    post {
        success {
            echo "Pipeline réussi : images ${env.IMAGE_TAG}"
        }
        failure {
            echo 'Pipeline en échec : voir les logs de l\'étape concernée'
        }
    }
}
