# Gitlab runner, Kezako ?
## Les pipelines de CI/CD selon Gitlab
Gitlab est une plateforme d'hébergement de code source qui propose de nombreuses fonctionnalités satellites, dont un orchestrateur de _pipelines_ d'intégration continue / de déploiement continue : 

* Chaque push (au sens Git) sur un dépôt déclenche le pipeline. Il est également possible d'effectuer des déclenchements périodiques ou via une API.
* Chaque _pipeline_ est composé de stages (exécutés les uns à la suite des autres).
* Chaque _stage_ contient 1 à plusieurs jobs (qui peuvent être exécutés en parallèle).
* Chaque _job_ a pour vocation d'exécuter une liste de scripts, dans un conteneur Docker particulier.

Chaque pipeline est décrit dans un fichier **.gitlab-ci.yml** à la racine d'un dépôt Git. Voir la [documentation officielle](https://docs.gitlab.com/ee/ci/yaml/).

## Les runners : en managé ou dans son infrastructure ?
Les _jobs_ Gitlab sont exécutés sur des serveurs "esclaves", dits _runners_. Dans le cas de gitlab.com, le choix par défaut est d'utiliser les **runners gérés par Gitlab**. Cette solution offre un **coût d'installation et de maintenance nuls** mais vient avec des limitations:

* La **disponibilité** des runners n'est pas assurée, à fortiori avec l'offre gratuite.
* La **vélocité** de ces workers laisse parfois à désirer. Or quel que soit le projet, **chaque minute d'exécution d'un pipeline de CI/CD est toxique pour la productivité**.
* Le plus souvent en entreprise, les **barrières réseaux** empêchent à un serveur externe d'interagir avec l'infrastructure interne (que ce soit pour lire ou écrire des artefacts ou pour déployer une application).
    
L'**alternative** est de déployer un runner Gitlab **au sein de son infrastructure**. Au prix d'une légère charge opérationnelle, les avantages sont multiples :

* Il est possible d'utiliser des **serveurs** aussi **puissants** que nécessaire, avec une bonne proximité réseau avec les différents dépôts de binaires utilisés. C'est parfois la solution la plus facile pour diminuer le temps d'exécution du pipeline.
* C'est le moyen le plus simple de permettre aux pipelines de CI/CD d'**utiliser des éléments d'infrastructure internes à l'entreprise**.

L'établissement de la connection TCP/IP s'effectue depuis le runner vers l'instance : **la connection n'est donc pas perturbée par la présence d'un ou plusieurs reverse proxys**. 
Évidemment, l'impact du déploiement d'un tel runner dans votre réseau ne peut pas être négligé.
    
    
# Pourquoi Gitlab Runner dans Kubernetes ?
La manière la plus usuelle et la plus simple de déployer un runner Gitlab est de lui dédier un serveur, potentiellement utilisé pour d'autres tâches non critiques. 
Cependant, il est également possible de confier à ce runner des droits d'accès à une instance Kubernetes pour qu'il y exécute les **_jobs_ (au sens Gitlab) en tant que _pods_ (au sens Kubernetes)**. Le runner peut également être lui-même déployé dans Kubernetes. 

Le **nombre maximum de _pods_ lancés simultanément** par le runner est réglable. Mais il peut être configuré à, virtuellement, l'**infini, si le cluster Kubernetes est lui même auto-scalable** (ex dans le cloud). Cela permet donc d'éviter tout goulet d'étranglement en cas de lancement de nombreux _jobs_ (d'une même instance de pipeline ou non).

Des complexités supplémentaires sont à considérer :

* Il est évidemment nécessaire de disposer d'un cluster Kubernetes cible.
* L'utilisation du mécanisme de cache, qui permet de rendre plus véloce le lancement des jobs en réutilisant des fichiers d'un lancement précédent (par exemple, les dépendances), nécessite d'utiliser un système de stockage distribué compatible.

# Exemple de stack de déploiement
J'ai réalisé une **première ébauche de stack de déploiement sous Kubernetes** d'un runner Gitlab : [http://simon.denel.fr/installation-de-gitlab-runner-dans-kubernetes/stack.yaml](http://simon.denel.fr/installation-de-gitlab-runner-dans-kubernetes/stack.yaml)

Cette stack présente les spécificités suivantes :

* Le runner dispose de droits larges sur son propre namespace afin d'y instancier des pods.
* Le mécanisme de cache de fichiers distribué est assuré par [MinIO](https://min.io/), qui offre une API compatible AWS S3. La stack contient une unique instance de MinIO, sans stockage persistent (ce n'est qu'un cache !).
* La segmentation réseau (via une SecurityPolicy) assure que les pods du namespace n'ont pas le droit d'accéder aux autres pods du cluster, à l'exception de MinIO et de l'API Server.

Exemple d'utilisation de la stack :

  ```bash
  kubectl -n gitlab-runner create secret generic gitlab-runner --from-literal="TOKEN=VOTRE_TOKEN_GITLAB"
  kubectl apply -f http://simon.denel.fr/installation-de-gitlab-runner-dans-kubernetes/stack.yaml
  ``` 

# Autres
## Quelques options intéressantes de Gitlab Runner
* **[concurent](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-global-section)** permet de régler le nombre de lancement de jobs en parallèle.
* **[allowed_images](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#restrict-allowed_images-to-private-registry)** permet de limiter les images Docker utilisées par les _jobs_
* **[listen_address](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-session_server-section)** permet de définir l'adresse et le port sur lequel des métriques au format OpenMetrics sont exposées (pour ingestion par un outil de monitoring tel que Prometheus)


## Tester / valider l'état de minio
```bash
# Bind MinIO sur votre port 9000 local
kubectl -n gitlab-runner port-forward svc/minio 9000:9000
```
Puis utilisez votre navigateur : [http://localhost:9000/](http://localhost:9000/) (admin:password)

## Chart Helm
Pour les adeptes de Helm, une alternative à cette stack est d'utiliser le Chart officiel : [https://gitlab.com/charts/gitlab-runner/tree/master](https://gitlab.com/charts/gitlab-runner/tree/master)

## Backlog...
Les points suivants restent à traiter :

* Créer une ou plusieurs stacks complémentaires avec :
    * Un proxy HTTPS, tel que Squid, pour faciliter la mise en cache implicite (utile, par exemple, si l'accès aux dépôts d'artefacts est lent). Cette piste semble nécessite que l'HTTPS, avec Squid en man-in-the-middle, soit reconnu par les pods :
        * Trouver comment ajouter la CA générée par Squid dans les pods instanciés par Gitlab.
        * Fournir des images qui contiennent la CA.
    * Un exemple d'ingestion des métriques par Prometheus via l'utilisation d'une Ressource ServiceMonitor.
* Comment limiter les tâches effectués par des runners sensibles, par exemple aux seules branches protégées ?
* Comment se situe cette solution par rapport à l'offre "Auto DevOps sous Kubernetes" de Gitlab ?
* Comment assurer le nettoyage périodique du cache / assurer une "lifetime expectancy" aux fichiers ? MinIO ou Gitlab proposent-ils une fonctionnalité en ce sens ?