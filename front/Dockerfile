FROM nginx:1.25.3-alpine@sha256:f2802c2a9d09c7aa3ace27445dfc5656ff24355da28e7b958074a0111e3fc076

#remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stahg 1
COPY --chown=nginx:root dist /usr/share/nginx/html

EXPOSE 80

