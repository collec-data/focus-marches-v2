FROM nginx:1.29.8-alpine@sha256:582c496ccf79d8aa6f8203a79d32aaf7ffd8b13362c60a701a2f9ac64886c93d

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

