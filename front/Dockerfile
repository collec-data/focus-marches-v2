FROM ghcr.io/pnpm/pnpm:12.14.0@sha256:71202ae73719148f6b6e129ca1e9fa3ceabbc9a037dc34800715606f2b5290a1 AS build

RUN pnpm runtime set node 24.21.0 -g

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm ci

COPY . .
RUN pnpm run build

FROM nginx:1.31.7-alpine@sha256:892bb2152464f0c5d8972593a5f5afaf8054552580b699d95f8ff4af08c2d33d

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

# Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy built assets from the build stage
COPY --from=build --chown=nginx:root /app/dist /usr/share/nginx/html/
COPY --chown=nginx:root docker/settings.js.template /etc/nginx/templates/

ENV NGINX_ENVSUBST_OUTPUT_DIR=/usr/share/nginx/html/

# Substitute env vars
CMD ["nginx", "-g", "daemon off;"]

EXPOSE 80

