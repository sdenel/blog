Le standard DynDNS permet de mettre à jour une entrée DNS de manière automatique. Pratique lorsqu'on ne dispose pas d'une IP fixe !

# Installation du client sous Debian / Ubuntu
```bash
apt install ddclient
```

Modifier le fichier vim /etc/ddclient.conf. Exemple pour du DynDNS via noip :
```
protocol=dyndns2
use=web
ssl=yes
server=www.noip.com
login=sdenel
password='blabla'
violette.hopto.org
```

* Server :
  * www.noip.com pour hopto.org, ...
  * www.ovh.com pour le DynDNS de OVH (il est possible sur OVH de créer des identifiants spécifiques pour une entrée DnyDNS)

# Pour tester
```bash
sudo ddclient -daemon=0 -debug -verbose -noquiet
```


