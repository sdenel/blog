# Bloquer les 
```bash
#!/bin/bash
set -e
export INTERFACE=enp1s0 # Interface de la Gateway, obtenue avec ifconfig ou ip addr
iptables -F; iptables -X; iptables -t nat -F; iptables -t nat -X; iptables -t mangle -F; iptables -t mangle -X; iptables -P INPUT ACCEPT; iptables -P FORWARD ACCEPT; iptables -P OUTPUT ACCEPT
iptables -A INPUT -i $INTERFACE -p tcp --dport 22 -j ACCEPT # SSH
iptables -A INPUT -i $INTERFACE -p tcp --dport 80 -j ACCEPT # HTTP
iptables -A INPUT -i $INTERFACE -p tcp --dport 443 -j ACCEPT # HTTPS
iptables -A INPUT -i $INTERFACE -p tcp --dport 1194 -j ACCEPT # OpenVPN
iptables -A INPUT -i $INTERFACE -p tcp --dport 32768:65535 -j ACCEPT # Les ports au dela de 32768 sont utilisés pour créer des sockets de réponse
iptables -A INPUT -i $INTERFACE -p tcp -j REJECT # On bloque le reste du traffic sur cette interface
```

# Rendre iptables persistant
## Avec iptables-persistent
Par défaut, ces règles ne sont pas persistentes. Pour les rendre persistentes (c'est à dire recrées à chaque démarrage du serveur) :
```bash
apt install iptables-persistent
iptables-save > /etc/iptables/rules.v4
```
## Avec un fichier executé au demarrage
* Permet de garder la structure précédente
* C'est la solution que j'utilise sur mon serveur : "iptables-save" sort également d'autres règles que celles nouvellement ajoutées (ex routage de Kubernetes pour ma part)
* Mettre les règles dans un fichier /etc/network/if-pre-up.d/iptables puis chmod +x
Typiquement, tester OpenVPN (port 943)
