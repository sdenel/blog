* L'agent de Gitlab (gitlab-runner) peut etre instancié dans votre propre infrastructure
* C'est d'ailleurs un bon moyen de permettre, depuis gitlab.com, d'effectuer des déploiements sur votre infrastructure :
    * Les proxys ne posent pas de problème de configuration: gitlab-runner établit une connection TCP permanente avec le serveur, d'ou l'absnece de pb
    * Vous pouvez ne permettre l'utilisation d'un runner que sur les branches protected
    
# Pourquoi Gitlab Runner dans Kubernetes ?
* gitlab-runner peut :
    * Etre instancié dans Kubernetes (facilite le monitoring, facilite le transfert de droits sur le cluster via un service account)
    * Instancier les jobs dans Kubernetes (facilite la scalabilité)
* Dans mon cas : c'est le seul moyen (simple) de permettre aux jobs de joindre l'API Server de Kubernetes

# Ma stack de déploiement
* Cache distribué :
    * L'utilisation du cache (qui permet la mise en cache, par exemple, du téléchargement des dépendances dans les pipelines) nécessite d'utiliser AWS S3 ou un équivalent compatible.
    * D'ou l'instanciation de MinIO en local au cluster, sans recherche de High Availability ou de persistence (ce n'est qu'un cache !).
* Sécurité réseau : la SecurityPolicy assure que les pods du namespace n'ont pas le droit d'accès aux autres pods du cluster, à l'exception de MinIO et de l'API Server.
* Instanciation :
  ```bash
  kubectl -n gitlab-runner create secret generic gitlab-runner --from-literal="TOKEN=tototo"
  kubectl apply -f http://simon.denel.fr/installation-de-gitlab-runner-dans-kubernetes/stack.yaml
  ``` 

# Autres
* Pour tester / voir l'état de minio :
```bash
# Bind minio sur votre port 9000 local
kubectl -n gitlab-runner port-forward svc/minio 9000:9000
```
Puis utilisez votre naviguateur : localhost:9000/
* Pour les adeptes de Helm, voir également : https://gitlab.com/charts/gitlab-runner/tree/master