FROM ubuntu:latest
RUN apt install -y wget && \
  wget https://github.com/jgm/pandoc/releases/download/2.7.2/pandoc-2.7.2-1-amd64.deb && \
  dpkg -i pandoc-2.7.2-1-amd64.deb

