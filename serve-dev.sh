#!/bin/bash
set -e

docker pull sdenel/blog-builder

while true; do
    { # try
        docker build --build-arg COMPILATION_MODE=DEV . -t blog &&
        (docker rm -f blog-container || true) &&
        docker run -d --name blog-container -p0.0.0.0:8080:80 blog &&
        # Moyen d'être prévenu de manière audio lorsque le conteneur est redéployé
        # Alternatives : spd-say
        # apt install sox libsox-fmt-mp3 && pip3 install google_speach
        google_speech "Compiled"
        # rend la main lors d'une modification (apt install inotify-tools)
    } || { # catch
        google_speech "Failure!"
    }
    inotifywait -r .
    google_speech "Recompiling"
done