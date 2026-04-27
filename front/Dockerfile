FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build
FROM nginx:1.30.0-alpine@sha256:0272e4604ed93c1792f03695a033a6e8546840f86e0de20a884bb17d2c924883

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

