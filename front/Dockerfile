FROM nginx:1.29.1-alpine@sha256:42a516af16b852e33b7682d5ef8acbd5d13fe08fecadc7ed98605ba5e3b26ab8

#remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stahg 1
COPY --chown=nginx:root dist /usr/share/nginx/html

EXPOSE 80

