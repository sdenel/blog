Exemple de cas d'usage :

* Un service ne sert que sur localhost (pour des raisons de sécurité).
* Un autre service (userB sur serverB) souhaite accéder à ce service
* Une commande du type `ssh -L8080:localhost:8080 userA@serveurA` permet à l'utilisateur B d'obtenir, sur son port 8080, le service exposé par serverA
* Comment restreindre les droits de l'utilisateur B sur le serveur A ?

Exemples pratiques : Api Server de Kubernetes protégé des accès via internet


# Restreindre les droits pour un utilisateur

Dans le fichier /etc/ssh/sshd_config:
```
Match User limited-user
   #AllowTcpForwarding yes
   X11Forwarding no
   #PermitTunnel no
   #GatewayPorts no
   AllowAgentForwarding no
   # Exemple de liste
   PermitOpen localhost:8080 localhost:8081
   ForceCommand echo 'This account can only be used for [reason]'
```

# Pour une clé : directement dans le fichier .ssh/authorized_keys
```
command="echo 'port forward is authorized with this key'",no-agent-forwarding,no-X11-forwarding,permitopen="host-1:3389",permitopen="host-2:3389" ssh-rsa...
``` 