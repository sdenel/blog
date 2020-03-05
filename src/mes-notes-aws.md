# Concepts inhérents au cloud
* High Availability vs fault tolerance, deux cibles différentes : TODO
* RTO et RPO : Recovery *Time* Objective vs Recovery *Point* Objective. TODO

# Infrastructure matérielle de AWS

## Region
TODO

## Availability Zone

* Chaque région AWS est usuellement constituée de au moins 3 datacenters distincts (AZ)
* Ces AZs sont suffisament éloignées géographiquement pour limiter le risque d'une catastrophe naturelle impactant plus d'une AZ (tremblement de terre, innodation...)
* Mais elles sont suffisament proches pour assurer une communication réseau parfaite d'un point de vue latence/débit.
* Ces datacenters sont eux memes organisés en cellules (cell)
* Bruit...
    * Le nom des AZs dans le compte (eu-central-1*b*...) est aléatoire d'un compte à un autre. Le mapping vers l'AZ physique (euc1-az2...) se retrouve dans le <s>Resource Account Manager</s>. 
* Backlog
    * Creuser la notion de Cell. Déploiement par cell ?

## Backbone
* Les différents datacenters de AWS sont reliés entre eux par des fibres optiques dediées, ce qui limite le nombre de hops réseau.

## Edge locations
TODO cache + un peu de compute (Lambda@Edge). Pour rentrer sur un edge : utiliser en frontal API Gateway ou CloudFront ou adresse IP anycast (AWS Global Accelerator)


## Nitro
Nom de l'intégration verticale en cours chez AWS :
* Hardwarisation des concepts éprouvés (VPC, security group) et de l'hyperviseur
* 
### Firecracker
* Ecrit en Rust !
* Permet d'executer des "conteneurs en bare metal"
* Très prometteur pour l'avenir (offre serverless avec Lambda ou EKS Fargate)

# Point de vue utilisateur

## Stockage
### Stockage object
* TODO S3 (principe versionnage API normée minio...)
* Glacier = legacy sauf pour de la compliance ? Finira par devenir une simple classe de stockage de S3
### Stockage block
### Autre
#### Credentials
* AWS KMS vs AWS CloudHSM :
    * KMS est mieux intégré dans l'environnement, et moins cher à l'usage
    * Mais CloudHSM peut répondre à des besoins précis : API standard, certification FIPS plus elevée

## Réseau : organisation en VPC
* subnet
    * TODO public vs private
* security group
    * stateful
* Network ACL
    * stateless
    * S'applique aux frontières d'un subnet
    * Et donc : ne s'applique pas aux communications entre instances à l'intérieur d'un meme subnet
* Notion d'Elastic Network Interface (ENI)


## Compute
### EC2
* [AWS Instance Scheduler](https://docs.aws.amazon.com/solutions/latest/instance-scheduler/architecture.html)
    * Permet d'éteindre des instances EC2 / RDS sur certaines plages horaires / jours
    * L'information est transmise sous forme de Tag sur l'instance
    * Particulièrement adapté pour les environnements hors production
    * L'absence de "DynDNS" builtin pour les instance EC2 complexifie l'intégration (solution simple : utiliser des Elastic IPs) 

### Kubernetes managés (EKS)

### Offre serverless
* TODO principe + lambda + Fargate
#### Lambda
* TODO principe
* TODO Interet
* TODO limites : attention à la logique dans les fils et à la maintenabilité (pousse à des languages faiblement typés, le plus souvent livrés sans tests... ce qui n'est pas une fatalité)
* TODO lambda en VPC vs pas en VPC

## Infrastructure as Code (IaC)
* Mes convictions IaC :
    * Le ou les comptes liés à la production ne doivent pouvoir etre mise à jour qu'à travers de l'IaC
    * Cette IaC doit etre stockée sous Git, avec un déploiement pour tout push sur une branche donnée (master...)
    * Forcer un environnement aussi identique que possible entre les environnements : le meilleur moyen étant en ayant le *meme* code entre les environnements, avec des paramètres d'entrée différents (taille et nombre des VMs, ...)

### CloudFormation
* S'écrit en JSON/YAML. Préférer à tout prix le YAML.
* Limites inhérentes au YAML/JSON (impossibilité de faire des boucles, ...). Ma proposition : utiliser Jinja pour la templatisation.
* Quelques exemples de stacks :
    * Aussi complet que complexe, [la stack de déploiement de ce blog (S3 + Cloudfront + ACM)](https://github.com/sdenel/blog/tree/master/static/mes-notes-aws/static-website-s3-cloudfront-acm)

### les alternatives
* AWS CDK ?
* Terraform et Terraform entreprise
    * L'état peut etre stocké dans S3

## Sécurité réseau
* AWS Guarduty
* AWS WAF
    * Plusieurs niveaux dont un par défaut (DDOS, ...)


# AWS en entreprise
## Utilisateurs et attribution des droits
User, Role, Groupe, Policies, inline policies et variables dans les policies


## Organisation en comptes
* AWS organization
* Service Control Policies
    * Ne peut pas s'appliquer au compte master
    * S'appliquent en cascade
    * Si existe : par défaut rien le droit de faire si l'action n'est pas Allow.
    * Vient valider que l'action a le droit d'etre réalisée en sus des controles liés aux droits de l'utilisateur sur le compte
* Mes convictions :
    * Garder le compte master pour le billing et la gestion des utilisateurs (car entre autres, pas possibilité d'y appliquer de SCP)
    * Mais rester simple dans le découpage (un unique compte pour une petite startup, pas plus de quelques comptes pour une PME)
    * Limiter via les SCP à une région, grand maximum deux pour garder une bonne visibilité sur les ressources instanciées 
* TODO AWS Tower

## Compliance
* AWS Config : pour valider que les ressources respectent des règles définies via du code dans des Lambda
    * Exemple : valider que les instances EC2 (ou autres ressources) sont bien taggées (owner, scheduling, environnement...)
    * De nombreuses règles disponibles on the shelf : port 22 avec filtrage IP, ...
    * A vocation à etre configuré dans un compte dedié à la compliance (distinct du ou des comptes applicatifs).
* AWS Inspector
    * 
* AWS CloudTrail : pour vérifier qui a fait quoi. Par défaut reglé pour conserver toutes les actions des utilisateurs sur le compte pendant 90 jours.

## Controle et réduction des couts
* Utiliser les services dediées : EC2 de non prod en spot instances, dimensionnement des EC2 au plus juste (RAM, CPU) et utilisant la scalabilité horizontale, tagging pour éviter les service oubliés allumés, extinction la nuit...
* Responsabilisation par facturation au plus près de l'usage

# Backlog
* https://web-identity-federation-playground.s3.amazonaws.com/index.html
* Limitations en date :
    * Pas d'ajout de header dans CloudFront autrement qu'avec Lambda@edge
