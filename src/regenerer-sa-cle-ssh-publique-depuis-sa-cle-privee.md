En SSH, la clé privée (ex ~/.ssh/id_rsa) contient également les informations stockées dans la clé publique (ex ~/.ssh/id_rsa.pub), à l'exception du nom, qui est une variable libre, généralement sous la forme "NOM_UTILISATEUR@NOM_MACHINE".

Ainsi, pour regénérer votre fichier id_rsa.pub, vous pouvez utiliser la commande suivante :
```bash
echo "`ssh-keygen -y -f ~/.ssh/id_rsa` $USER@`hostname`"
```