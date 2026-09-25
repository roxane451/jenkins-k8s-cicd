# DevOps - Pipeline CI/CD avec Jenkins

## Contexte et Objectifs
En tant qu’ingénieur **DevOps junior**, l’objectif est de mettre en place un **pipeline CI/CD complet** pour une application microservices.  

Le pipeline devra permettre :
- La **construction** et le **push** des images vers une registry distante.  
- Le **déploiement automatisé** sur différents environnements Kubernetes.
- L’**orchestration CI/CD** à l’aide de **Jenkins**.  
- Le **packaging et déploiement** avec **Helm Charts**.  

---

## Architecture Technique

### Technologies utilisées
- **Conteneurisation** : [Podman](https://podman.io/)
- **Orchestration Kubernetes** : Cluster Kubernetes (Rancher) 
- **Registry d’images** : [c8n.io](https://c8n.io/)  
- **CI/CD** : [Jenkins](https://www.jenkins.io/)  
- **SCM** : [GitHub](https://github.com/)  
- **Packaging & déploiement** : [Helm](https://helm.sh/)  

---

## Flux du Pipeline CI/CD

1. **Commit & Push GitHub**  
   → Déclenchement automatique du pipeline Jenkins.  

2. **Build & Push d’images**  
   - Construction des images avec **Podman**.  
   - Publication vers la registry **c8n.io**.  

3. **Déploiement sur Kubernetes**  
   - Déploiement de l’application dans l’environnement cible.  
   - Utilisation de **Helm Charts** pour gérer les releases.  

4. **Gestion des environnements**
   - Namespaces Kubernetes séparés par environnement  
   - Configuration spécifique par environnement
---

## Sécurité et durcissement

- Jenkins : utiliser des credentials Jenkins (username/password pour registry) et éviter toute exposition du mot de passe dans les logs.
- Pipeline : ne pas exécuter en `root`, appliquer `runAsNonRoot`, `runAsUser: 1000`, `usePodSecurityContext` dans le pod Jenkins agent.
- Conteneurs : `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities.drop: [ALL]`.
- Kubernetes : ne pas déployer en mode `NodePort` non protégé en production ; utiliser `Ingress` TLS.
- Images : éviter `latest`, verrouiller version (tag explicite). Scanner avec Trivy/Anchore.
- Secrets : utiliser `imagePullSecrets` et ne pas stocker DB_PASSWORD dans `docker-compose.yml` en clair.

## Changelog de sécurité

- 2026-04-03 : hardening critique
  - `Jenkinsfile` : passage en `runAsNonRoot`, suppression de `privileged` et ajout de `allowPrivilegeEscalation: false` + `capabilities.drop: [ALL]`.
  - `Jenkinsfile` : limité les déploiements DEV à `develop`, `main`, `master` (plus de “toutes branches”).
  - `charts/values.yaml` : ajout `podSecurityContext`/`securityContext` durcis.
  - `README.md` : ajout section sécurité et durcissement.

## Arborescence du projet

```bash
.
├── cast-service
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── charts
│   ├── Chart.yaml
│   ├── namespaces.yaml
│   ├── README.md
│   ├── templates
│   └── values.yaml
├── docker-compose.yml
├── Jenkinsfile
├── movie-service
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
└── README.md

