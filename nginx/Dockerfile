# Variante non root de l'image officielle : écoute sur 8080, pas de privilèges
FROM nginxinc/nginx-unprivileged:stable-alpine

USER root
RUN apk upgrade --no-cache
USER 101

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
