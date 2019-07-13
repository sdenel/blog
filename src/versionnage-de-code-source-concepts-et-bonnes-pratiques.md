# Le versionnage de code source, kezako ?
## Qu'est-ce que le versionnage de code source ?
Le versionnage de code source consiste à **sauvegarder fréquemment l'état des fichiers** d'un répertoire correspondant à un projet. Cela permet :

* **La réversibilité des changements** : il est possible de restaurer un état du passé en cas de problème.
* **L'auditabilité** : les modifications sont accompagnées d'un message permettant de comprendre l'origine et l'objectif des changements apportés à chaque ligne, même plusieurs années plus tard.
* **Le partage** : un VCS facilite le partage du projet entre tous les protagonistes **dans une état de référence**.
* **D'effectuer des actions automatiques lors d'un changement** : par exemple, de valider que le projet est dans un état consistant via des tests automatiques.

Ce traçage s'effectue à travers un outil dit **VCS (Version Control System)**. Les moteurs les plus connus sont **Git, SVN et Mercurial**. On utilise un unique moteur par projet. Mais :

* Il est possible d'effectuer une migration (typiquement de SVN vers Git)
* L'interface graphique (SourceTree, TortoiseSVN...) peut librement différer d'un utilisateur à un autre. 

## Que versionner ?
On peut considérer comme code source **tout fichier qui peut s'ouvrir dans un bloc note**. C'est le type de fichiers pour lequel les solutions de VCS sont conçues.
Du fait des avantages qu'offre le versionnage, la tendance est de versionner non seulement le code applicatif, mais également les fichiers plus opérationnels (configuration, codes liés à de l'Infrastructure as Code), ainsi que les documentations (au format Markdown, par exemple).

Un VCS a comme spécificité de stocker l'intégralité des changements depuis l'origine du projet. Il est donc **inadapté de versionner** :

* **Des binaires**. Un binaire est un fichier qui nécessite un logiciel spécialisé pour être lu ou modifié (image, vidéo, .zip...). Stocker un binaire léger (jusqu'à quelques méga octets, changeants peu) peut être acceptable. Mais il faut garder en mémoire que ce binaire va alourdir le projet même après sa suppression. Il est donc particulièrement inadapté de versionner des binaires lourds ou changeants régulièrement.
* **Des mots de passes**. Une fois versionné, un mot de passe est virtuellement impossible à effacer de l'historique. **Stocker des mots de passe dans un projet** peut donc amener des réflexions toxiques à la productivité, car ils rendent **le code source infiniment plus confidentiel qu'il ne devrait l'être**. Il existe cependant des solutions (telles que Ansible Vault) pour permettre le stockage de ces mots de passe de manière cryptée, tout en les versionnant.

# Focus sur Git
## Git : le standard du marché
Ces dernières années, Git s'est imposé comme un standard. Des plateformes de gestion de code source aussi puissantes que ergonomiques n'existent qu'avec le moteur Git (Github, Gitlab, ...).

Git est aussi complet que complexe. Les actions de base sont simples à effectuer, mais il est également possible de réaliser des manipulations sur le code source qui nécessitent une certaine persévérance pour être maîtrisées.

Du fait que Git est le standard pour le versionnage de code source dans l'univers Open Source, et **tend à devenir le standard** (en remplacement de SVN) **en entreprise**, **le reste de cet article fait l'hypothèse que Git est le VCS utilisé**.

## Philosophie et vocabulaire
Le modèle de Git est, in fine, assez simple :

* Chaque projet est appelé un *repository*.
* Usuellement, un unique serveur central contient l'état du projet. Mais contrairement à SVN, **chaque utilisateur *clone* le projet en local** afin de pouvoir effectuer des modifications.
* Chaque modification du code source correspond à un *commit*. Chaque commit contient :
    * Des métadonnées sur le changement : nom et email de l'auteur des changements, heure du commit, ...
    * Un commentaire décrivant l'objectif du commit. La première ligne de ce commentaire est le titre.
    * Une référence à un commit (changement) ou deux commits (fusion).
    * Une liste de changements par rapport au commit précédent.
* Une *branche* est une variation de la base de code. Chaque repository dispose à **minima de une branche**, dite branche principale (souvent nommée *master*).
* Un *tag* peut également être apposé sur un commit particulier. **Les tags sont usuellement utilisés pour colorer les commits qui correspondent à une mise en production.**
* Chaque transfert d'un ou plusieurs commits depuis son poste local vers le serveur central s'appelle un *push*. **Contrairement à SVN, les commits ne sont transmis au serveur central que lors du push !**
* Récupérer l'état du dépôt distant en local est appelé un *fetch*. On parlera de *pull* lorsque le fetch est suivi d'une fusion en local des modifications distantes avec l'état local.
* Usuellement, **on ne réécrit pas l'histoire sous Git** :
    * Sauf sur "sa branche" et/ou en local.
    * Sauf pour enlever un mot de passe, un fichier, ... Mais cette tâche, fastidieuse, nécessite de se synchroniser avec l'ensemble des protagonistes du projet.

## Utilisation des branches, du développement à la mise en production
**Git permet de facilement créer et fusionner des branches**. 
Cette facilité est évidemment très pratique, mais amène son lot de questionnements méthodologiques. 
Plusieurs méthodologies existent :

* La plus connue (aussi complète que complexe) est [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/). [Une extension de Git est disponible pour faciliter les commandes du quotidien][https://github.com/nvie/gitflow]. 
* [Github flow](https://guides.github.com/introduction/flow/) et [Gitlab flow](https://docs.gitlab.com/ee/workflow/gitlab_flow.html) sont des alternatives notables.

**Ces méthodologies représentent d'avantages d'excellentes sources d'inspiration que des modèles parfaits quel que soit le contexte (mode de livraison, nombre de protagonistes, phase du projet...).** 
Dans tous les cas, **obliger au respect de ces pratiques via la configuration du serveur principal est une nécessité** si vous ne souhaitez pas vous emmêler les pinceaux dans les branches.

### Branches de développement
Une bonne pratique est de **développer les fonctionnalités dans des branches spécifiques (on parle de feature branching)**. 
Cette méthode de travail permet de ne proposer les modifications au projet que lorsqu'elles représentent un ensemble fonctionnel cohérent (autrement dit une fonctionnalité), quel que soit le nombre de commits intermédiaires. Quelques points d'attention :

* Cette rigueur est **nécessaire lorsque plusieurs développeurs travaillent sur la même base de code en même temps**.
    * La merge request (ou pull request) peut être un excellent moment pour valider entre pairs que le code est à la hauteur des standards du projet (écrit au mieux, documenté et testé dans une juste mesure...).
    * Ce moment de **revue de code** est préférablement un **moment de partage (et non une validation)** effectuée entre pairs (pour éviter les points de contention : la **validation d'une merge request doit s'effectuer extrêmement rapidement**), dans un objectif de progrès de l'application et des développeurs. **Le progrès est plus important que l'égo !**
* Mais lorsqu'un unique développeur travaille sur le projet, faire des features branches revient la plupart du temps à s'infliger inutilement une perte de productivité. Des exceptions existent : fusion automatique lorsque le code est validé par des tests, validation par un tiers avant la fusion...
* Dans tous les cas, une feature branch doit avoir une **durée de vie extrêmement courte (de quelques heures à deux jours de travail)** sous peine de s'infliger une complexité de gestion qui n'est nullement créatrice de valeur. Lorsque, exceptionnellement, une fonctionnalité nécessite de vivre dans une branche pendant plusieurs jours / semaines, il est primordial d'effectuer fréquemment un **rebase** depuis la branche principale. Traiter les divergences au plus tôt et par petits lots évite de ne plus rien comprendre aux changements. Et d'un point de vue qualité, [des revues de code fréquentes sur des petits lots sont plus constructives][Ask a programmer to review ten lines of code, and he'll find ten issues. Ask him to do five hundred lines, and he'll say it looks good. (The DevOps Handbook, p255)].
* Technique de fusion : [désactiver le fast-forward][https://nvie.com/posts/a-successful-git-branching-model/#incorporating-a-finished-feature-on-develop] sur le serveur central. Cela empêche les commits de la feature branch d'être simplement reportés sur la branche principale, et force la création d'un commit de merge spécifique.
    * La lisibilité de l'arbre de modifications est meilleure
    * Il est plus facile pour revenir en arrière
    * Cela permet d'utiliser les commits sur les features branchs sans réfléchir à l'impact : pour créer des points de retour, lancer un pipeline de tests automatiques...

### Mise en production

**Le modèle de branche concernant la mise en production doit être adapté à votre réalité. Le plus simple possible est le mieux !**

#### Plusieurs versions de l'application vivent en parallèle
* Cette configuration correspond à un client lourd (".exe" téléchargé par les utilisateurs) ou à un environnement avec de multiples environnements de préproduction (gare au noeuds au cerveau !)
* C'est **la situation la plus complexe à gérer !**
* Tagger les releases, en utilisant la convention de versionnage [Semantic Versioning](semver.org) (vMAJEUR.MINEUR.CORRECTIF). :
    * Incrémenter MAJEUR pour des changements non rétrocompatibles.
    * Incrémenter MINEUR pour des ajouts de fonctionnalités rétrocompatibles.
    * Incrémenter CORRECTIF pour des corrections d’anomalies rétrocompatibles.
* Exemple : [kubernetes](https://github.com/kubernetes/kubernetes/branches)) utilise ces conventions.
* Créer **une branche spécifique par MAJEUR.MINEUR nommée release-MAJEUR.MINEUR** (on parle de *release branch*). En règle générale, seule la dernière release branch en date fait l'objet d'ajout de fonctionnalités.

#### Une seule version existe en production
* Cette configuration correspond à **une part grandissante des applications** : la tendance est de ne plus livrer de clients lourds, qui sont complexes à maintenir, et de privilégier les applications web et la fourniture de service dits "managés" (hébergés par l'entreprise qui développe le produit).
* Cette configuration rend possible des processus de livraison plus légers :
    * Si vos utilisateurs ont besoin d'être tenus au courant des mises à jour, Versionnez vos mises en production (MAJOR.MINOR est suffisant).
    * Sinon, préférer un **unique compteur de version vVERSION**.
    * Dans certains cas, il est même possible de ne pas réfléchir au versionnage : la simple arrivée d'un commit sur la branche principale peut signifier une mise en production (idéalement automatique)
    
La gestion des environnement de préproduction dépend là aussi des cas :
* Si vous êtes en capacité de créer des environnements de préproduction éphémères, vous pouvez en créer un par feature branch, qui sera détruit lors de la fusion.


## Quelques bonnes pratiques liées à Git
### Lancement d'actions lors du push
La livraison d'un code source avec son **harnais de tests automatiques** est une pratique essentielle pour assurer sa maintenabilité dans le temps.  

Par suite, c'est une bonne pratique de lancer ces tests de manière automatique **à chaque réception d'un commit** sur le serveur principal (Gitlab, Github, BitBucket...).
Idéalement, ces tests doivent être exhaustifs, rapides, et précis lorsqu'ils relèvent une erreur. Mais c'est un autre sujet ! 
Les pratiques modernes vont jusqu'à effectuer une mise en production de manière automatique lorsque le code est validé, avec ou sans validation manuelle.

### Découpage : un projet Git correspond à un cycle de vie
En particulier du fait du lancement de tests automatiques (voire d'un déploiement en test/production) lors de l'arrivée du code source sur le serveur principal, une bonne pratique est de créer **un projet Git par cycle de vie distinct**. 
L'inverse amène des problèmes tels que, par exemple, des tests lents provocants une perte de productivité.

**Pour exemple, le backend d'une application web n'a pas le même cycle de vie que le frontend** : c'est donc une bonne pratique de créer deux projets Git distincts.

Réciproquement, des projets Git trop couplés rendent les tests et la mise en production fastidieux et risqués.

### Autres bonnes pratiques
* **Déterminisme de la compilation** : Un commit donné doit donner un même binaire après compilation. Cela implique en particulier de versionner la liste des dépendances et leur version exacte (par exemple pour un frontend, versionner le fichier package-lock.json)
* **Ne pas versionner les fichiers générés** : Typiquement, le dossier target/ d'un projet Java doit être ajouté dans un fichier .gitignore afin d'éviter de versionner des binaires lourds et changeants par inadvertance. Cette règle n'est pas un absolu : le code généré automatiquement (ex les services d'accès à une interface REST disposant d'une documentation OpenAPI et générés via (Swagger CodeGen)[https://github.com/swagger-api/swagger-codegen]) a sa place sous Git.
* **Ne pas versionner les fichiers de préférence utilisateurs** : Les fichiers générés par votre IDE (par exemple le dossier .idea sous IntelliJ) définissent l'état de votre interface graphique, et n'ont donc pas de valeur ni vocation à être partagés. 
* **Insérer la référence du ticket résolu dans le nom de la feature branch / dans le titre du commit**. Cette pratique facilite la traçabilité. Par la suite, Git blame et les outils graphiques (par exemple VCS->Git->Annotate sous IntelliJ) permettent d'utiliser cette information.
* Ecrire un **README.md** (en Markdown) à la racine du projet, qui décrit succinctement l'objectif du projet. Les plateformes Git l'affichent automatiquement sur la page d'accueil du projet.
* Accès en console via **https ou ssh ? Impossible d'établir une réponse tranchée** :
    * HTTPS a le mérite d'être moins bloqué en entreprise,
    * SSH permet de donner un accès plus restreint (pas d'accès web)

# Autres
## Quelques pratiques de Git avancées

Git est un outil extrêmement puissant. Sans rentrer dans le détail, voici quelques manipulations que Git permet d'effectuer sur la base de code :

* **squash** : Fusion de commits consécutifs pour nettoyer l'historique. Cette manipulation réécrit l'histoire (sur les branches principales, cela rend invalide le clone local de vos collègue !).
* Appliquer un commit depuis une autre branche, dit **Cherry picking** (picorage)
* **git bissect** : trouver quel commit a introduit un bug par dichotomie.
* **Signer ses commits** à l'aide d'une clé GPG. C'est une pratique davantage destinée au monde de l'Open Source. 
* **clone partiel** : cela permet de disposer du dernier état d'un projet sans récupérer tout l'historique. C'est particulièrement pratique pour de l'automatisation, mais c'est une mauvaise odeur si vous en avez besoin pour travailler (pourquoi votre projet est-il si lourd ?) : `git clone --depth 1 https://path/to/repo/foo.git -b bar`
* **Git LFS (Large File Storage)** Nuancer le stockage de binaires lourds grace à QQQ. Evite de récupérer les fichiers lourds lors d'un clone. Mais mise en place manuelle.


## Backlog...
* Commencer une FAQ :
    * Comment éviter les problèmes de fin de ligne entre Windows et Linux ?
    * Comment régler son IDE pour éviter les changements perpétuels d'indentation ?
    * Comment gérer les environnement de préproduction qui ne font pas partie du cycle de Release Management ? Avec une branche spécifique ?
* Comment régler Gitlab et consors pour refuser le push de caractères ressemblant à un mot de passe ?
* Quels logiciels pour avoir une interface graphique ? SourceTree, Tortoise, ...
* Détailler (ou pas) la possibilité de ne pas faire des features branch, mais de faire des clones de repository en entier. Utilisé en permanence en Open Source, mais aussi en entreprise dans certains contextes.
* Poids maximum d'un projet Git : ~1Go. Au delà de ~100Mo, c'est déjà douloureux.
* Faire un article distinct sur le modèle Git. Inspiration : [Git Data Model](https://astahblog.com/2015/09/08/git-data-model/)
* Nuancer le non versionnage du dossier .idea : quels fichiers peuvent, discutablement, être considérés comme faisant parti du projet ?
* Réaliser des schémas pour les branches de développement / de mise en production.
* Sujet avant tout méthodologique mais qui se retrouve dans Git : limiter la complexité. Pas plus de branches que nécessaire, limiter le nécessaire, limiter le Work In Progress
* Les fonctionnalités sympas des solutions en ligne, au dela de l'interface de merge request : branches protégées, tokens et clés SSH techniques avec droits restreints et durée de vie, ...
* Est-ce important de garder les branches principales "vertes" ? Pour quelles raisons ?

## Références et autres liens
Références : [[references]]

Autres liens :

* Le livre [Pro Git](https://git-scm.com/book/en/v2) est régulièrement mis à jour et disponible gratuitement pour la version en ligne. La version en papier est ancienne (2014).