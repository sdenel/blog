# Des bonnes pratiques, pourquoi faire ?
En tant qu'humain, nous avons l'habitude d'interagir avec des systèmes informatiques à travers une interface graphique.
Pourtant, l'écrasante majorité des échanges d'informations entre systèmes ont lieu entre deux applications, à travers des frontières applicatives dites API (pour Application Programming Interface).
Et **au moment de faire des échanges de données de manière synchrone, les API en HTTP sont prépondérantes**.

Pourtant, leur qualité laisse souvent à désirer. Cet article de blog a pour but de donner quelques bonnes directions, simples, mais trop souvent ignorées. 
Le coût est peu élevé si elle sont respectées dès le début du projet, et les bénéfices sont nombreux :

* Pour l'**intuitivité d'utilisation** : une norme est toujours plus facile à appréhender qu'une documentation spécifique.
* Pour la **sécurité** : Une API est une frontière avec des utilisateurs plus ou moins connus et bien intentionnés.
Les problématiques d'authentification et d'autorisation forment un excellent terreau pour une faille de sécurité.
* Pour faciliter l'**évolutivité** : ces pratiques aident à limiter les incohérences et autres erreurs de conceptions. 
Elles augmentent également la capacité d'un nouveau développeur à comprendre rapidement la philosophie du contrat en place et à l'étendre dans le même esprit. Sur le long terme, elle peuvent faciliter un changement de technologie d'implémentation.
* Pour l'**intégration avec les outils du marché** : certaines de ces pratiques sont issues d'un retour d'expérience plus ou moins douloureux par rapport aux outils lorsqu'elles ne sont pas respectées (GET sans effet de bord, éviter PATCH, conventions de nommage...)


# Bonnes pratiques
## Méthodologie
### Réfléchir la position des frontières applicatives
Les APIs font partie des murs porteurs d'un SI : elles sont faciles à étendre, mais très coûteuses à faire évoluer.

Une API définit la frontière d'un système. C'est certainement la première question à se poser au moment de construire une application. 
Une réflexion formelle, préalable au développement, est vitale. 
**L'API doit in fine être la formalisation d'une frontière fonctionnelle saine, et non d'une frontière organisationnelle**, sous peine de transformer un cancer en métastases.


### Concevoir l'API pour répondre aux premiers cas d'usage, sans y coller
<non>/getClientWithContactData/4</non>→<oui>/clients/4/</oui>

Développer pour répondre aux usages (et ne pas hésiter à supprimer ce qui est sous utilisé) est une bonne méthodologie de conception. 
Mais pour une API, **le risque est de concevoir une API trop spécifique, et de tomber dans le travers de créer une API par cas d'usage**. 
Ce qui n'est pas couteux sur le coup, mais se révèle désastreux au moment d'évoluer.

Les pratiques ci-dessous vous aideront à garder une interface générique, qui répond aux premiers cas d'usage, sans pour autant redévelopper des interfaces spécifiques pour le cas d'usage suivant.


### Versionner l'API de manière globale
<non>/tickets/uf4a</non><non>/tickets/v1/uf4a</non>→<oui>/v1/tickets/uf4a</oui>

La norme est d'utiliser un versionnage global, et non par endpoint (un endpoint correspond à une URL générique associée à un verbe). 

Incrémenter la version lorsqu'on introduit un comportement non rétrocompatible. L'ajout de nouveaux endpoints, par exemple, ne nécessite pas d'incrémentation.

### Rester pragmatique
Aucune API n'est parfaite et chercher la perfection peut se révéler chronophage sans apporter de valeur. 
Ce pragmatisme peut par exemple amener à ne considérer, dans un premier temps, que les cas autoroutes (aussi dit **happy path**), 
et à ne développer les cas particuliers (**edges cases** type 404, ...) que dans un second temps.

## Architecture
### Penser ressource
<non>/recuperer-les-paniers-et-.../</non>→<oui>/paniers/</oui>

L'approche dite REST propose de voir l'API comme une exposition de ressources que l'on peut consulter et manipuler (dans la limite de ce que l'API permet et de ses autorisations). 
Cette approche est devenue un standard.

Une ressource est une représentation d'un objet (voiture, fiche de contact...) dotée d'un **identifiant unique** auprès du système.

### Ranger les ressources dans des collections
<non>/panier-4/</non>→<oui>/paniers/f/</oui>

l'approche REST propose de ranger les ressources par type, dans des collections (c'est à dire des sous chemins dans l'URL) avec la convention d'URL ci-dessus (nom de la collection au pluriel). 

## Standards HTTP

Pour rappel, un échange en HTTP est composé de :

* Une requête par le client, contenant :
    * Un verbe (GET, POST, ...)
    * Une URL
    * Des métadonnées sous la forme clé/valeur (headers)
    * Optionnellement, des données (payload)
* Et d'une réponse de la part du serveur, contenant :
    * Un statut (200, 204, ...)
    * Des métadonnées sous la forme clé/valeur (headers)
    * Optionnellement, des données (payload)
    
Pour un exemple de requête et de la réponse associée, exécuter : `curl -v -D - google.fr.`

### Utiliser les codes de retour à bon escient : 200, 201, 204, 404...
<non>200 "ressource created"</non>→<oui>204 [Location: ...]</oui>

En tant que consommateur, traiter différemment des erreurs exprimées avec le même code de retour est inutilement compliqué. 
Les codes de retour les plus courants sont :

* **2XX : c'est tout bon !** 
    * **200 - OK : retourner le contenu demandé (page HTML. ressource JSON...)**.
    * **201 - ressource créée** : retourner l'URL de la ressource dans le header "Location" ou la ressource directement (voir section POST).
    * **204 - OK (mais rien à dire de plus)**.
* **3XX : Il faut aller voir ailleurs...**
    * **301 - redirection permanente**. Suivre l'URL fournie dans le header Location.
    * **302 - Redirection temporaire**. Suivre l'URL fournie dans le header Location.
    * **304 - Not Modified**. Les headers fournis dans la requête permettent au serveur d'assurer que le client a déjà la dernière version du contenu, 
et donc qu'un renvoi n'est pas nécessaire (gain en bande passante).
* **4XX : Vous êtes sur ?**
    * **400 - syntaxe erronée**.
    * **401 - authentification nécessaire**.
    * **403 - accès interdit**. S'authentifier ne changera rien, la requête n'est pas autorisée pour cet utilisateur.
    * **404 - ressource introuvable**.
    * **409 - conflit** . La ressource existe déjà.
* **5XX : Oups...**
    * **500 - erreur interne** : C'est l'erreur retournée par défaut par les frameworks lors d'une situation qui n'a pas été prévue.
    * **503 - système indisponible** : La requête est probablement correcte, mais le serveur n'est pas en état de la traiter.

Voir également : [HTTP STATUS DOG][https://httpstatusdogs.com/] et, en moins imagé, [Liste des codes HTTP sur Wikipedia][https://fr.wikipedia.org/wiki/Liste_des_codes_HTTP]

### Respecter les verbes HTTP et leur sens : GET, PUT, POST...
#### GET : pour la consultation
<oui>GET /livres/uf4a</oui>

Une verbe GET est par convention réservé à la **consultation**. Autrement dit, requête ne doit **pas avoir d'effet de bord** (c'est à dire ne pas provoquer de modification dans la base de données). 
**Cette absence d'effet de bord permet de consulter librement l'état du système sans en modifier l'état. **
C'est vital dans la phase de compréhension d'un bug.

#### POST : pour la création
<non>POST /createItem payload={"telephone": "06..."}</non>→<oui>POST /items/ payload={"telephone": "06..."}</oui>

Le verbe POST est principalement réservé à la création d'une ressource dans le système. Un comportement **idempotent** est préférable. 
Cela signifie qu'un second envoi de la même requête n'a pas de conséquence (autre que le renvoi d'une erreur 409 avec le header "Location" pointant vers la ressource existante). 

En cas de succès, le serveur renvoie un code 201 (CREATED). Deux approches existent concernant la payload de retour :

* **Retourner la ressource, de manière équivalente à un appel consécutif via un GET sur la ressource**.
    * Cette approche peut éviter une double requête aux utilisateurs.
* **Ma préférence (et la norme) : retourner l'URL de la ressource dans header Location**, et garder la payload pour un éventuel message explicatif :
    * Cette approche permet de relever au plus tôt un éventuel bug de persistance.
    * Et permet de conserver la possibilité d'ajouter un message de retour qui peut faciliter l'utilisation de l'API

#### PUT : pour modifier l'intégralité des propriétés d'une ressource existante
<oui>PUT /items/4 payload={"telephone": "06..."}</oui>

Le verbe PUT est réservé à la mise jour **complète** d'une ressource.

L'action doit, là aussi, être idempotente. 
Renvoyer plus de champs que nécessaire dans la payload de la requête ne doit pas être une erreur : le serveur doit simplement ne pas traiter l'information (c'est d'ailleurs le comportement par défaut des déserialiseurs). Ce comportement permet à l'utilisateur de renvoyer dans un PUT les données récupérées via un GET, après avoir modifié les propriétés de son choix.

<oui>PUT /items/4 payload={"telephone": "06...", "version": 5}</oui>

**Versionner la ressource** a ici beaucoup de sens : en ajoutant un compteur de version dans la ressource, que l'utilisateur a la charge d'incrémenter, vous assurez que la modification ne va pas, par inadvertance, écraser des informations plus récentes par inadvertance.

Si la ressource n'existe pas, deux choix sont possibles :

* Renvoyer une erreur 404 (implémentation la plus commune)
* Créer la ressource (et renvoyer 201) : cela fournit un comportement d'**upsert** (contraction de update et insertion). 
Ce comportement est préférable sur le verbe PUT que sur le verbe POST pour éviter tout écrasement de données involontaire.

#### PATCH : ne pas utiliser !
<non>PATCH /items/4 payload={"telephone": "06..."}</non>→<oui>PUT /items/4 payload={"adresse": "...", "telephone": "06..."}</oui>

Le verbe PATCH est historiquement utilisé pour réaliser des mises à jour granulaires de certaines propriétés de la ressource seulement.

L'intention est louable, mais pose de nombreux problèmes :

* Assurer que la ressource est cohérente dans son ensemble (numéro de téléphone compatible avec le pays, ...) devient fastidieux car non déterministe : une requête peut être invalide, et devenir valide une minute plus tard car le pays a changé !
* L'implémentation (avec Spring Boot, avec Angular...) est, d'expérience, compliquée. Par exemple, il est extrêmement difficile en Java, avec Jackson (désérialiseur de JSON par défaut en Spring Boot) de différencier une propriété fournie avec la valeur null d'une propriété non fournie. 

De ce fait, **préférer une mise à jour complète de la ressource** via un GET, suivie d'une modification de la ressource coté client, suivie d'un PUT.

Pour les quelques propriétés amenées à changer souvent (disponibilité d'un livre, ...), utiliser un endpoint de notification dédié (voir plus bas).

#### DELETE : pour supprimer la ressource
<non>POST /deleteItem/118</non>→<oui>DELETE /items/118</oui>

Répondre 204 en cas de succès.

#### Le cas des notifications : rester pragmatique
<non>PUT /lettres/uf4a/ {"": ..., "status": "sent"}</non>→<oui>POST /lettres/uf4a/notify-sent?token=7fda0a6a-15a2-4d46-8e96-6b6d5af876e3</oui>

Les notifications sont une sorte d'exception à la vision ressource. Elles sont très pratiques par exemple pour réaliser des **webhooks**, qui permettent de chaîner des actions entres différents services (push sur Github qui prévient Docker Hub,  qui à son tour prévient un serveur, etc).

* Accepter GET et POST sur le endpoint (même implémentation sous jacente) peut aider à la compatibilité.
* Authentification : exceptionnellement, l'authentification peut avoir lieu via un paramètre dans l'URL, voire dans certains contextes, être anonyme. Cela facilite grandement l'intégration.

**Pour rester idempotent, il est préférable que l'appel ne provoque par une action, mais la vérification de la nécessité de faire une action**. 
Par exemple, le système appelé peut retourner voir le sytème appelant pour avoir d'avantage d'informations sur la tâche à effectuer (c'est généralement le cas des webhooks dans une CI/CD).

## Conventions
### Privilégier le format JSON
Le format de référence pour une API HTTP est dorénavant le JSON. Des anciennes APIs existent au format XML, mais ce n'est pas la norme et travailler avec est douloureux.

Le format gRPC permet de gagner en compacité des messages et en temps de sérialisation / désérialisation, mais n'est à envisager pour les APIs avec un besoin avéré de performance.

Il est possible, pour une même API, d'exposer l'information dans des format différents (JSON, XML...) en se basant sur les headers "Content-Type" et "Accept" de la requête HTTP.

### Nommage des propriétés : préférer la convention camelCase
<non>{"last_price": ...}</non>→<oui>{"lastPrice": ...}</oui>

Ce choix ne fait pas l'unanimité, mais [c'est la convention la plus recommandée][https://github.com/json-api/json-api/issues/1255#issue-296124902]. 
Elle est utilisée par d'innombrables APIs d'envergure : Kubernetes, tous les projets Google...  
C'est également ce qui est généré par défaut par les frameworks tels que Spring Boot.

### URL : uniquement en lower case
<non>/api/v1/AuteursDeLivres</non>→<oui>/api/v1/auteurs-de-livres</oui>

L'usage est de ne pas utiliser de lettres majuscules ni d'underscore dans les URLs.

## Autres bonnes pratiques

### Authentification : utiliser un header

Une fois l'utilisateur connecté, la preuve d'identité doit s'effectuer via des informations dans un Header (le contenu dépasse le cadre de cet article). C'est la norme, pour de bonnes raisons : 

* Dans l'URL : c'est inadapté car les URLs consultées peuvent être écrites dans les logs, ce qui les rendraient sensibles alors que leur visibilité doit rester large au sein de l'organisation.
* Dans la payload de la requête : la payload est usuellement réservée à la charge applicative.

### Authentification en cas d'appels en cascade : préférer utiliser l'identité de l'utilisateur

Dans le cas d'un appel d'API en cascade (API A appelant l'API B), il est préférable d'utiliser les credentials de l'appelant par transfert, et non des credentials techniques.
Cela évite entre autres une élévation de privilèges par utilisation d'une procuration (ex pas l'utilisateur n'a pas le droit de supprimer un livre de la bibliothèque, mais peut y parvenir en passant par une API intermédiaire).

### Gestion des erreur : être aidant mais pas innocent
<non>500 "Internal error"</non>→<oui>400 "Field email is invalid"</oui><br />
<non>400 "Email not known"</non>→<oui>400 "Authentication failure"</oui>

Être prévenant pour **aider à la bonne utilisation** ("field email is invalid"). Mais pour des raisons de sécurité, **ne pas faciliter les mauvaises utilisations**. 
Exemple, en cas d'email non existant au moment de l'authentification : répondre "authentication failure" plutôt que "email not known" ou "bad password".

### Ne pas utiliser de double référence dans les URLs
<non>/clients/a3fu/paniers/uf4a/</non>→<oui>/paniers/uf4a/</oui><oui>/clients/a3fu/panier/</oui>

Soit il n'y a qu'une seule sous ressource de ce type dans la ressource parent : la ressource fille n'a pas besoin de référence.
Soit la ressource fille a besoin d'une référence : mais inclure deux références n'a aucun intérêt et pose de nombreux problèmes :

* C'est une perte de flexibilité : ici, le panier pourra difficilement, dans le futur, appartenir à deux clients en même temps.
* C'est un terrain avantageux pour une faille de sécurité : l'appartenance sera t'elle effectivement systématiquement vérifiée ?

### Ne pas exposer les IDs de sa base de données relationnelle
<non>/paniers/4/</non>→<oui>/paniers/fdbdb695-8364-47d5-8c3d-fdd690b63e87/</oui>

Utiliser l'id de la ressource dans votre base de données relationnelle est pratique, mais c'est une fuite de 
la technologie utilisée en sous couche qui n'est pas sans conséquences. Impossible par exemple de :

* Faire évoluer votre modèle en base de données, en regroupant ou en séparant des tables.
* Migrer sur une base de données distribuée (par exemple pour des raisons de performance).
* Dupliquer la base de données (par exemple pour être présent sur deux zones géographiques éloignées).

**Alternative 1 : utiliser une id fonctionnelle (joli, mais complexe).** C'est la technique utilisée pour les ressources principales sous Github, Gitlab, LinkedIn...

* Cela évite d'accepter que l'utilisation d'une base de donnée unique fasse partie du contrat.
* Il faut gérer l'unicité, voire le renommage et les redirections en cas de renommage. 
* La génération d'objets décentralisée (une base de donnée par zone géographique, génération de l'objet coté client...) est impossible.

**Alternative 2 : utiliser des UUIDs (moins joli, mais techniquement très pratique)**. 
Une UUID (pour Universally Unique IDentifiers) est une format standard, composé de 128 bits générés au hasard exprimés en hexadécimal. 
Exemple : "6169a008-57d9-4cb7-a8f7-bb469cc568e6". 
[Le risque de collision est virtuellement nul : 1 chance sur deux si vous générez 1 milliard d'UUID chaque seconde pendant un siècle][https://en.wikipedia.org/wiki/Universally_unique_identifier#Collisions].
Les avantages sont multiples :

* Il n'y a pas de fuite de la technologie d'implémentation dans le contrat. Cette implémentation est d'ailleurs plus pratique à utiliser, même avec une base de données relationnelle : on peut générer l'identifiant de la ressource préalablement à tout appel à la base de données.
* Le système est prêt à la génération de ressources de manière décentralisée (exemple, un paquet de café peut prendre vie dès l'usine, bien avant d'être créé dans le SI).
* Retrouver les interactions avec une ressource dans les logs est facilité : une recherche sur une UUID ne retournera pas de faux positifs. "6589", si.
* Pour un pirate, trouver une ressource qui existe dans une collection par brute force est virtuellement impossible. Cela limite les risques en cas de faille de sécurité dans l'API.

### Documenter automatiquement au format OpenAPI
Des outils permettent de générer cette documentation depuis des commentaires/annotations au plus près de l'implémentation. Ce qui évite qu'avec le temps, la documentation soit décorrélée de la réalité.

Cette documentation est idéalement **interactive**. Par exemple en Java Spring Boot, [SpringFox][https://springfox.github.io/springfox/] (librairies springfox-swagger2 et springfox-swagger-ui) 
génère automatiquement le contrat au format OpenAPI ainsi qu'une GUI en HTML pour naviguer dans l'API.
Le générateur extrait la documentation d'un parcours des endpoints de l'applications et de leur documentation, fournie sous forme 
d'[annotations Java au format swagger-core][https://github.com/swagger-api/swagger-core/wiki/Annotations-1.5.X].


### Autres bonnes pratiques
* **Supprimer les endpoints inutilisés au plus tôt** : cela permet de réduire sa surface d'attaque potentielle.
* **Ne pas exposer les stack traces en production** : elle peuvent donner des informations précieuses pour un pirate (technologie et librairies utilisées, version...).
* **Valider les données en entrée au plus tôt** : qu'un email est bien un email, ... Cela évite de stocker des données inconsistantes, voire nocives (injection XML, ...)
* **Monitorer le flux de requêtes en les séparant par statut** pour détecter les anomalies (bug, attaque...). [Le Dashboard de monitoring de Gitlab est un excellent exemple][https://dashboards.gitlab.com/] d'un tel monitoring. Des solutions existent également pour créer des alertes intelligemment en cas de comportement anormal (ELK, Instana, ...).  
* **Concevoir chaque API comme si elle allait être exposée au public** : cela augmente la flexibilité.
* **Inclure systématiquement dans ses tests automatiques le test de la contraposée** : Exemple : "en tant qu'utilisateur **non** administrateur, je ne peux **pas** supprimer de panier".

# Autres
## Outils
* Postman permet à la fois de naviguer dans une API et d'[automatiser des tests][Automatiser des tests d'API avec Postman][https://www.youtube.com/watch?v=pi9MxX0HSHU&list=PLM-7VG-sgbtDD69PEPRQt13DcyN5JUZnS] 

## Backlog...
* Implémenter le contrat avec précision peut se faire au fur et à mesure : exemple, renvoyer 500 en cas d'absence de la ressource mais renvoyer 404 dès que le cas d'usage se présente.
* Renvoyer les mêmes informations sur GET /items/ que sur GET /items/uf4a ? Ou un sous ensemble ?
* Comment amener élégamment dans un GET les informations dont on sait que l'utilisateur aura besoin (noms des auteurs d'un livre, ...)
* Push : différentes implémentations possibles (flag watch=1, ...)
* Le 204 est-il un piège ? Il est impossible d'augmenter les informations de retour sans changer le code de retour, donc le contrat.
* Dans quelle langue écrire l'API ? Si le métier est français, tout traduire en Franglais ?!
* Monitoring :
    * exposer /healthz au minimum. A protéger par un filtrage réseau, car il peut donner des informations permettant à un pirate de valider les effets de son attaque !
    * voire /metrics au format OpenMetrics, exposant des métriques techniques **et** fonctionnelles.
* Toujours enfermer l'API publique dans un sous chemin (/api) pour permettre de bloquer l'accès à d'autres endpoints depuis l'extérieur (/healthz, /actuators, ...) 
* Insister sur une conception avec un regard d'utilisateur.
* Mettre en exergue des principes **fondamentaux** type idempotence
* Gestion des recherches / filtrage / tri :
    * Comment / quels conventions ?
    * Quelles conventions pour la pagination ?
    * Que penser du GET avec un body comme ELK ?
    * Dans tous les cas, enfermer les listes dans des objets : cela permet de facilement ajouter des champs d'information annexes autour de la liste (nombre d'entrées, ...)
* A traiter rapidement :
    * Que retourner dans une GET ? uniquement les propriétés ? Ou également les sous ressources ?
    * Que retourner lorsqu'on liste une collection ? l'intégralité des propriétés des ressources, ou une sélection de propriétés ?
    * Lors d'une création / modification d'une ressource, retourner la Location ou la ressource dans sa nouvelle forme ?
    * Illustrer :
        * par exemple avec Jeff Bezos : https://image.slidesharecdn.com/webinar-retail-omnichannel-final-140624161040-phpapp01/95/using-apis-to-create-an-omnichannel-retail-experience-8-638.jpg?cb=1403627461
        * Ou avec le screenshot d'un curl
* Que penser de GraphQL ?
    * Regarder : https://wptavern.com/lessons-from-the-graphql-documentary-never-underestimate-the-power-of-open-source-communities
* Décorréler la problématique d'identification dans un HEADER. mais :
    * /me qui compte dessus ?
    * Comment assurer avec certitude que le développeur va valider l'autorisation si c'est décorellé ? A priori pas possible de bloquer le risque de manière structurelle, mais possibilité de limiter le risque en utilisant des UUIDs (id des autres objets en base impossible à retrouver par brute force)
    * Cookie ou Authentication Bearer ? Ou accepter les deux ?
* Comment gérer la problématique des droits d'accès sur des champs ? Exemple : en tant que A je ne peux voir que les propriétés 1, 2, 4. Obligation de passer sur des ressources ou sous ressources ?
* Parler des inconvénients d'une API bien découpée : beaucoup d'appels serveurs, dépendants les uns des autres donc difficiles à paralléliser... mais permet également de ne pas ramener plus d'informations que nécessaire.
* Download de fichiers lourds : permettre le multipart
* Comment gérer l'atomicité d'une "transaction" nécessitant plusieurs requêtes pour être exécutée ?
* Comment gérer l'interface administrateur ?
    * Même API : idéal de simplicité, mais nécessite une confiance totale en l'application (un piratage est dramatique)
    * Autre endpoint : ça dépend de la technologie sous jacente. En Java Spring Boot, c'est aussi difficile que exotique à implémenter.
    * Utiliser un sous chemin spécifique : (/admin/api/ au lieu de /api/) : cela permet, sans diminuer la sécurité côté applicative, de rajouter des sécurité en amont dans les Reverse Proxy (mécanisme d'authentification supplémentaire, filtrage IP...)
* Authentification sous Swagger ui ?
* Comment traiter le cas de deux consommateurs dont les usages apparaissent orthogonaux (interface administrateur, application passe plat...)
    * Une seule API : besoin de réfléchir aux politiques d'autorisation de manière fine
    * Deux APIs ?
* Quid des propriétés :
    * En lecture seule seulement (valeur calculée, lien de parenté, propriété modifiable uniquement avec certains droits...) : à priori, il ne doivent pas faire partie du DTO du PUT / POST.
    * Des champs modifiables seulement avec certains droits ? (clientId d'un panier...) Comment se parer contre un problème de développement ?
    * Est-ce normal ou un problème de design que d'avoir des droits différent sur un sous ensemble de la ressource (exemple accès à la date de naissance d'un individu)
* Une API est une frontière, c'est à dire que la mise à jour des consommateurs est au mieux faite dans la même journée, au pire virtuellement impossible à forcer.
* Quelle stratégie adopter pour forcer la mise à jour des clients ? Gitlab accepte de très peu respecter l'historique pour mieux avancer, est-ce une bonne stratégie ?
* Comment gérer les sous ressources qui n'ont pas besoin d'ID à elle (encapsulées) :
    * à la lecture ? à la modification ?
    * Si mise à jour ou récupération de la sous ressource uniquement, comment assurer la cohérence ?
    * Par extension, **est-ce normal de pouvoir récupérer une (sous)-ressource sans ID ni version ?**
* HATEOAS, qu'en penser ? Est-ce une nécessité et dans quels contextes ?
* Traitement des cas tordus (faire des études de cas) :
    * Example : "Question" de type "freeform" ou "qcm" qui "appartiennent" à un questionnaire
* Considérations sur la performance :
    * Est-ce un problème en pratique (hors géants du web) ?
    * Est-ce un problème de saturation des serveurs (difficulté à scaler horizontalement) ou de latence (multiples requêtes au chargement) ?
    * Quelles solutions proposer ? GraphQL ?
* Une API Gateway, quel intérêt ?
    * Contrôle des utilisateurs :
        * Authentification
        * Limitation du nombre de requêtes
    * Autres (glissant ?) :
        * Gérer les accès (autorisation)
        * Transformer les données
* Regarder de près l'article Octo [Designer une API REST][https://blog.octo.com/designer-une-api-rest/]

## Références et autres liens
Références : [[references]]

Autres liens utiles :

* [REST API Design Guide](https://www.apiopscycles.com/rest-api-design-guide)