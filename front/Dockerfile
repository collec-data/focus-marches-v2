FROM nginx:1.29.2-alpine@sha256:7c1b9a91514d1eb5288d7cd6e91d9f451707911bfaea9307a3acbc811d4aa82e

#remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stahg 1
COPY --chown=nginx:root dist /usr/share/nginx/html

EXPOSE 80

