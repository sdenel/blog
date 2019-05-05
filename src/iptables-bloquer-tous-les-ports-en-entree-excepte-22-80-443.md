Exemple de commande pour bloquer tous les ports en TCP exceptés quelques-un :
```bash
#!/bin/bash
set -e
export INTERFACE=enp1s0 # Interface de la Gateway, obtenue avec ifconfig ou ip addr

# Suppression des règles existantes
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

iptables -A INPUT -i $INTERFACE -p tcp --dport 22 -j ACCEPT # SSH
iptables -A INPUT -i $INTERFACE -p tcp --dport 80 -j ACCEPT # HTTP
iptables -A INPUT -i $INTERFACE -p tcp --dport 443 -j ACCEPT # HTTPS
iptables -A INPUT -i $INTERFACE -p tcp --dport 32768:65535 -j ACCEPT # Les ports au dela de 32768 sont utilisés pour créer des sockets de réponse
iptables -A INPUT -i $INTERFACE -p tcp -j REJECT # On bloque le reste du traffic sur cette interface
```

# Rendre ces commandes iptables persistantes
## Avec iptables-persistent
Par défaut, ces règles ne sont pas persistentes. Pour les rendre persistentes (c'est à dire recrées à chaque démarrage du serveur) :
```bash
apt install iptables-persistent
# Valider préalablement la sélection
iptables-save | grep $INTERFACE > /etc/iptables/rules.v4

## Tester
```bash
sudo nmap -v -sS -p 0-32768 -Pn -T4 IP_OU_NOM_DE_DOMAINE_DE_VOTRE_SERVEUR
```
