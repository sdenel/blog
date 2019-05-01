# Test local : docker build . -t blog && docker run -p0.0.0.0:8080:80 blog
FROM sdenel/blog-builder AS build
COPY . /src
RUN cd /src/ && ./builder.py

FROM sdenel/docker-nginx-file-listing
COPY --from=build /src/target/ /mnt/data