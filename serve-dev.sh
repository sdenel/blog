#!/bin/bash
set -e
while true; do
    docker build . -t blog
    docker rm -f blog-container || true
    docker run -d --name blog-container -p0.0.0.0:8080:80 blog
    # Moyen d'etre prévenu à
    # Alternatives : spd-say
    # apt install sox libsox-fmt-mp3 && pip3 install google_speach
    google_speech "Compiled"
    # rend la main lors d'une modification (apt install inotify-tools)
    inotifywait -r .
    google_speech "Recompiling"
done