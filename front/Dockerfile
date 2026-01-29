FROM nginx:1.29.4-alpine@sha256:7d7a15b8a280c661051955f14c2b91fed3e23724ddba18d2f53e8b44e74ab37a

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

# Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stage 1
COPY --chown=nginx:root dist /usr/share/nginx/html/
COPY --chown=nginx:root docker/settings.js.template /etc/nginx/templates/

ENV NGINX_ENVSUBST_OUTPUT_DIR=/usr/share/nginx/html/

# Substitute env vars
CMD ["nginx", "-g", "daemon off;"]

EXPOSE 80

