FROM nginx:1.29.3-alpine@sha256:b3c656d55d7ad751196f21b7fd2e8d4da9cb430e32f646adcf92441b72f82b14

#remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stahg 1
COPY --chown=nginx:root dist /usr/share/nginx/html

EXPOSE 80

