FROM sdenel/blog-builder AS build
COPY . /src
RUN cd /src/ && ./builder.py

FROM sdenel/docker-nginx-file-listing
COPY --from=build /src/target/ /mnt/data