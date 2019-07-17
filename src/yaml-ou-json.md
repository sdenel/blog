De nombreux outils CLI, par exemple ceux liés à l'Infrastructure As Code (IaC) tels que kubectl autorisent d'utiliser en entrée un fichier au format JSON ou au format YAML.

Ma conviction : 

* **Lorsque vous avez le choix et que votre fichier a valeur de code source, préférez le format YAML. C'est le consensus, à juste titre.**
* Mais le JSON reste prépondérant sur le YAML pour les interfaces entre services (API REST, ...)

# De quoi parle t'on ?
JSON comme YAML sont des formats standards qui permettent d'exprimer un contenu sous la forme de dictionnaires, de listes, de chaînes de caractères, de nombres et de booléens.

Un exemple de JSON :
```json
{
  "env": [
    {
      "name": "DEMO_GREETING",
      "value": "Hello from the environment"
    },
    {
      "name": "DEMO_FAREWELL",
      "value": "Such a sweet sorrow"
    }
  ]
}
```

La meme contenu, en YAML :
```yaml
env:
  - name: DEMO_GREETING
    value: "Hello from the environment"
  - name: DEMO_FAREWELL
    value: "Such a sweet sorrow"
```

# Les (petits) inconvénients du YAML
* **La distinction visuelle entre les listes et les dictionnaires n'est pas suffisamment claire.** Les non initiés pesteront à juste titre.
* Tout comme le JSON, l'extension des fichiers ne permet pas aux IDEs de détecter facilement la grammaire utilisée (Ansible, CloudFormation...). 
* Contrairement au XML (avec le XSD), il n'existe pas de possibilité de définir la grammaire utilisée ce qui permettrait à votre IDE :
    * De faciliter la complétion automatique
    * De souligner les erreurs de sémantique.
    * Le JSON profite ici d'un léger avantage, puisqu'il est possible de définir une grammaire au format [JSON Schema](https://json-schema.org/). Même s'il n'est pas possible de définir la grammaire utilisée en en-tête, comme en XML.
* La tabulation peut se faire avec 2 espaces, ou avec 4 espaces, ce qui est perturbant. Heureusement, les tabulations sont interdites.

# Les petits mais nombreux avantages du YAML

* **Il est possible d'ajouter des commentaires** en commençant une ligne par un dièse (#). Dans un code source, des commentaires en juste quantité, c'est vital.
* **Le YAML fait consensus contre le JSON au moment d'écrire du code source** :
    * [exemple d'article en ce sens sur le blog officiel d'AWS](https://aws.amazon.com/blogs/mt/the-virtues-of-yaml-cloudformation-and-using-cloudformation-designer-to-convert-json-to-yaml/)
    * [Documentation Kubernetes : "Write your configuration files using YAML rather than JSON"](https://kubernetes.io/docs/concepts/configuration/overview/)
* La structuration basée sur des espaces **limite l'encombrement visuel**. Les fichiers sont plus concis, l'oeil s'attache à l'important.
* **La gestion des longues chaînes de caractère est bien meilleure** :
    * Il est possible de faire du **multi-ligne** :
```yaml
nginxConf: |-
    server {
        listen 80;
        ...
    }
# En JSON, nous aurions du écrire sur une seule ligne : server {\n    listen 80;\n    ...\n}\n
``` 
    * Il est possible de couper une valeur en **plusieurs lignes alors que le résultat est attendu sur une seule ligne** :
```yaml
MAVEN_OPTS: >-
    -Dhttps.protocols=TLSv1.2
    ...
    -Djava.awt.headless=true
```
  * La règle est la suivante :
    * Premier caractère :
        * **\|** pour garder les retours à la ligne
        * **\>** pour les supprimer.
    * Second caractère :
        * **rien** pour finir la valeur par un unique retour à la ligne
        * **\-** pour supprimer le dernier retour à la ligne
        * **\+** pour garder tous les derniers retours à la ligne.
    * Voir également [yaml-multiline.info](https://yaml-multiline.info/).

# Autres

* **Extension : .yml ou .yaml ?** Il n'y a pas de consensus clair. Il est donc préférable de se plier à la norme établie dans votre projet. Si vous devez vraiment choisir, préférer **.yaml** : ["Please use ".yaml" when possible."](https://yaml.org/faq.html) 

# Backlog...

* Détailler les autres fonctionnalités avancées de Yaml :
  * YAML anchors pour éviter la duplication : [https://docs.gitlab.com/ee/ci/yaml/#anchors]( https://docs.gitlab.com/ee/ci/yaml/#anchors)
  * Mais incompatible avec, au moins, CloudFormation :
    * "YAML aliases are not allowed in CloudFormation templates"
    * (However, you can use YAML anchors in imported template snippets.)[https://github.com/awslabs/serverless-application-model/issues/228#issuecomment-350425716]
    * "aws cloudformation package followed by aws cloudformation deploy to support Anchors"
* Quels outils pour la conversion hors ligne (pour des raisons de confidentialité) pour la conversion JSON <-> YAML ?
* Comment marier l'utilitaire jq et du YAML ?
    * yq apparaît moins développé : [yq](https://yq.readthedocs.io/en/latest/)
    * Ma meilleure réponse jusqu'ici, transformer le YAML en JSON à la volée : `cat some.yaml | yq | jq ...`
* Intégration de YAML avec les outils de templating, en particulier Jinja, afin de respecter l'indentation.