FROM ghcr.io/pnpm/pnpm:12.10.0@sha256:333da074a29dcc495459433955e15e03a2715f6ae3f4904139a544e110d2d411 AS build

RUN pnpm runtime set node 24.21.0 -g

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm ci

COPY . .
RUN pnpm run build

FROM nginx:1.31.1-alpine@sha256:8b1e78743a03dbb2c95171cc58639fef29abc8816598e27fb910ed2e621e589a

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

