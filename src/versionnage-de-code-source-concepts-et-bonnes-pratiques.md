# Le versionnage de code source, kezako ?
## Qu'est-ce que le versionnage de code source ?
Le versionnage de code source consiste à **sauvegarder les modifications** apportées aux fichiers appartenants à un projet (correspondant à un répertoire). Cela permet :

* **La réversibilité des changements** : il est possible de restaurer un état du passé en cas de problème.
* **L'auditabilité** : les modifications sont accompagnés d'un message permettant de comprendre l'origine et l'objectif des changements apportés à chaque ligne, même plusieurs années plus tard.
* **Le partage** : un VCS facilite le partage du projet entre tous les protagonistes **dans une état de référence**.
* **D'effectuer des actions automatiques lors d'un changement** : par exemple, de valider que le projet est dans un état consistant via des tests automatiques.

Ce traçage s'effectue à travers un outil dit **VCS (Version Control System)**. De nombreuses solutions (telle que Google docs : Fichier->Historique des versions) intègrent un tel moteur. Nous ne nous intéresserons ici qu'au versionnage de code source.

Et dans l'univers du **code source**, les moteurs les plus connus sont **Git, SVN et Mercurial**. On utilise un unique moteur par projet. Mais :

* Il est possible d'effectuer une migration (typiquement de SVN vers Git)
* L'interface graphique (SourceTree, TortoiseSVN...) peut librement différer d'un utilisateur à un autre. 

## Que versionner ?
On peut considérer comme code source **tout fichier qui peut s'ouvrir dans un bloc note**. C'est le type de fichiers pour lequel les solutions de VCS sont conçues.
Un VCS a comme spécificité de stocker l'intégralité des changements depuis l'origine du projet. Il est donc **inadapté de versionner** :

* **Des binaires**. Un binaire est un fichier qui nécessite un logiciel spécialisé pour être lu ou modifié (image, vidéo, .zip...). Stocker un binaire léger (jusqu'à quelques méga octets, changeants peu) peut être acceptable. Mais il faut garder en mémoire que ce binaire va alourdir le projet même après sa suppression. Il est donc particulièrement inadapté de versionner des binaires lourds ou changeants régulièrement.
* **Des mots de passes**. Une fois versionné, un mot de passe est virtuellement impossible à effacer. Stocker des mots de passe dans un projet peut donc amener des réflexions toxiques à la productivité, car ils rendent le code source infiniment plus confidentiel qu'il ne devrait l'être. Il existe cependant des solutions (telles que Ansible Vault) pour permettre le stockage de ces mots de passe de manière cryptée, tout en les versionnant.

# Focus sur Git
## Git : le standard du marché
Ces dernières années, Git s'est imposé comme un standard. Des plateformes de gestion de code source aussi puissantes que ergonomiques n'existent qu'avec le moteur Git (Github, Gitlab, ...).

Git est aussi complet que complexe. Les actions de base sont simples à effectuer, mais il est également possible de réaliser des manipulations sur le code source qui nécessitent une certaine persévérance pour être maîtrisées.

Du fait que Git est le standard pour le versionnage de code source dans l'univers Open Source, et **tend à devenir le standard** (en remplacement de SVN) **en entreprise**, **le reste de cet article fait l'hypothèse que Git est le VCS utilisé**.

## Philosophie et vocabulaire
Le modèle de Git est, in fine, assez simple :

* Chaque projet est appelé un **repository**.
* Usuellement, un unique serveur central contient l'état du projet. Mais contrairement à SVN, chaque utilisateur **clone** le projet en local afin de pouvoir effectuer des modifications.
* Chaque modification du code source correspond à un **commit**. Chaque commit contient :
    * Des métadonnées sur le changement : nom et email de l'auteur des changements, heure du commit, ...
    * Un commentaire décrivant l'objectif du commit. La première ligne de ce commentaire est le titre.
    * Une référence à un commit (changement) ou deux commits (fusion).
    * Une liste de changements par rapport au commit précédent.
* Une **branche** est une variation de la base de code.
* Un **tag** peut également etre apposé sur un commit particulier.
* Chaque transfert d'un ou plusieurs commits depuis son poste local vers le serveur central s'appelle un **push**.
* Récupérer l'état du dépôt distant en local est appelé un **fetch**. On parlera de **pull** lorsque le fetch est suivi d'une fusion des modifications distantes avec l'état local.
* Usuellement, **on ne réécrit pas l'histoire sous Git** :
    * Sauf sur "sa branche" et/ou en local.
    * Sauf pour enlever un mot de passe, un fichier, ... Mais cette tâche, fastidieuse, nécessite de se synchroniser avec l'ensemble des protagonistes du projet.

## Quelques bonnes pratiques liées à Git
### Lancement d'actions lors du push
La livraison d'un code source avec son **harnais de tests automatiques** est une pratique essentielle pour assurer sa maintenabilité dans le temps. 

Par suite, c'est une bonne pratique de lancer ces tests de manière automatique **à chaque réception d'un commit** sur le serveur principal (Gitlab, Github, BitBucket...).
Idéalement, ces tests doivent être exhaustifs, rapides, et précis lorsqu'ils relèvent une erreur. Mais c'est un autre sujet ! Les pratiques modernes vont jusqu'à effectuer une mise en production de manière automatiques lorsque le code est validé, avec ou sans validation manuelle.

### Découpage : un projet Git correspond à un cycle de vie
En particulier du fait du lancement de tests automatiques (voir d'un déploiement en test/production) lors de l'arrivée du code source sur le serveur principal, une bonne pratique est de créer **un projet Git par cycle de vie distinct**. 
L'inverse amène des problèmes tels que, par exemple, des tests lents provocants une perte de productivité.

**Pour exemple, le backend d'une application web n'a pas le même cycle de vie que le frontend** : c'est donc une bonne pratique de créer deux projets Git.

### Le feature branching : modifier le code source dans une branche spécifique
#### Git et Git Flow
**Git permet de créer et fusionner facilement les branches**. Cette facilité est évidemment très pratique, mais amène son lot de questionnements méthodologiques. La méthodologie la plus connue est le workflow [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) et une extension de Git est même disponible pour faciliter les commandes du quotidien. Quelques nuances sont cependant à apporter à cette méthodologie :

#### Mise en production
**Le modèle de branche concernant la mise en production doit etre adapté à votre méthode de livraison**, actuelle et idéale. Il est absurde de considérer la même méthodologie pour une application livrée à des clients via une installation (client lourd), une application web nécessitant une interruption de service pour être mise à jour, et une application "nouvelle génération" permettant des mises à jour sans interruption de service.

Difficile d'aller plus loin dans cet article à ce sujet : la bonne méthodologie est la plus simple, mais des contraintes (livraison douloureuse, passage devant une commission pour valider les changements...) peuvent obliger à considérer une méthodologie telle que que Git Flow.

#### Branches de développement
Une bonne pratique est de **développer les fonctionnalités dans des branches spécifiques (on parle de feature branching)**. 
Cette méthode de travail permet de ne proposer les modifications au projet que lorsqu'elles représentent un ensemble fonctionnel cohérent (autrement dit une fonctionnalité), quel que soit le nombre de commits intermédiaires. Quelques points d'attention :

* Cette rigueur est **nécessaire lorsque plusieurs développeurs travaillent sur la même base de code en même temps**.
    * La merge request (ou pull request) peut être un excellent moment pour valider entre pairs que le code est à la hauteur des standards du projet (écrit au mieux, documenté et testé dans une juste mesure...).
    * Ce moment de **revue de code** est préférablement un **moment de partage (et non une validation)** effectuée entre pairs (pour éviter les points de contention : la **validation d'une merge request doit s'effectuer extrêmement rapidement**), dans un objectif de progrès de l'application et des développeurs. **Le progrès est plus important que l'égo !**
* Mais lorsqu'un unique développeur travaille sur le projet, c'est la plupart du temps s'infliger une perte de productivité. Des exceptions existent : fusion automatique lorsque le code est validé par des tests, validation par un tiers avant la fusion...
* Dans tous les cas, une feature branch doit avoir une **durée de vie extrêmement courte (de quelques heures à deux jours de travail)** sous peine de s'infliger une complexité de gestion qui n'est nullement créatrice de valeur. Lorsque, exceptionnellement, une fonctionnalité nécessite de vivre dans une branche pendant plusieurs jours / semaines, il est primordial d'effectuer fréquemment un **rebase** depuis la branche principale. Traiter les divergences au plus tôt et par petits lots évite de ne plus rien comprendre aux changements.

### Autres bonnes pratiques
* **Déterminisme de la compilation** : une base de code donnée doit donner un même binaire. Cela implique en particulier de versionner la liste des dépendances et leur version exacte (par exemple pour un frontend, versionner le fichier package-lock.json)
* **Ne pas versionner les fichiers générés** : Typiquement, le dossier target/ d'un projet Java doit être ajouté dans un fichier .gitignore afin d'éviter de versionner des binaires lourds et changeants par inadvertance.
* **Ne pas versionner les fichiers de préférence utilisateurs** : Les fichiers générés par votre IDE (par exemple le dossier .idea sous IntelliJ) définissent l'état de votre interface graphique, et n'ont donc pas de valeur ni vocation à être partagés. 

# Autres
## Backlog...
* Comment éviter les problèmes de fin de ligne entre Windows et Linux ?
* Comment régler son IDE pour éviter les changements perpétuels d'indentation
* Comment régler Gitlab et consors pour refuser le push de charactères remssemblant à un mot de passe ?
* Quels logiciels pour avoir une interface graphique ? SourceTree, Tortoise, ...
* Détailler (ou pas) la possibilité de ne pas faire des features branch, mais de faire des clone de repo en entier. Utilisé en permanence en Open Source, mais aussi en entreprise dans certains contextes.
* Poids maximum d'un projet Git : ~1Go. Au delà de ~100Mo, c'est déjà douloureux.
* Améliorer ou faire un article distinct sur le modèle Git. Inspiration : [Git Data Model](https://astahblog.com/2015/09/08/git-data-model/)
* Nuancer le non versionnage du dossier .idea : quels fichiers peuvent, discutablement, être considérés comme faisant parti du projet ?

## Liens et références
* Le livre [Pro Git](https://git-scm.com/book/en/v2) est régulièrement mis à jour et disponible gratuitement pour la version en ligne. La version en papier est ancienne (2014).