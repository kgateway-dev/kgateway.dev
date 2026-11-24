# syntax=docker/dockerfile:1
#
# Serves an already-built offline copy of the kgateway docs (see
# `make build-offline` and hugo-offline.yaml). This file builds nothing: the
# build context IS the built site, so the image needs no Hugo, Node, or network
# access, and anyone holding the offline tarball can build it behind a firewall:
#
#   mkdir kgateway-docs && tar -xzf kgateway-docs-offline.tar.gz -C kgateway-docs
#   docker build -t kgateway-docs kgateway-docs
#   docker run --rm -p 8080:8080 kgateway-docs     # then open http://localhost:8080
#
# From a clone of this repo, `make offline-image` does the same thing.
#
# nginx-unprivileged runs as a non-root user and listens on 8080, so the image
# also runs under a restricted Kubernetes pod security context.
FROM nginxinc/nginx-unprivileged:1.29-alpine

# The default server block already serves index.html for folder URLs, which is
# all a Hugo site needs. This replaces it only to add the site's own 404 page.
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen       8080;
    server_name  _;
    root         /usr/share/nginx/html;
    index        index.html;
    error_page   404 /404.html;
}
EOF

COPY --chown=nginx:nginx . /usr/share/nginx/html/
EXPOSE 8080
