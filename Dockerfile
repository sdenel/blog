# Test local : ./serve-dev.sh
FROM sdenel/blog-builder AS build
ARG COMPILATION_MODE
ENV COMPILATION_MODE=$COMPILATION_MODE
COPY . /src
RUN cd /src/ && python3 -m doctest builder.py && ./builder.py

FROM sdenel/docker-nginx-file-listing
COPY --from=build /src/target/ /mnt/data