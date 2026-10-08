FROM ghcr.io/pnpm/pnpm:12.10.1@sha256:1aa6cd5e8ec50c046a2690efde0c25ced4c6ed896ada5509f7d33b0b94dc04a3 AS build

RUN pnpm runtime set node 24.21.0 -g

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm ci

COPY . .
RUN pnpm run build

FROM nginx:1.31.6-alpine@sha256:df221db836e1754089190208cee7eeda94f233197056426eda74a43ab1abeac2

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

