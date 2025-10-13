FROM nginx:1.29.2-alpine@sha256:61e01287e546aac28a3f56839c136b31f590273f3b41187a36f46f6a03bbfe22

#remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=nginx:root /nginx/ /etc/nginx/

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html

# Copy from the stahg 1
COPY --chown=nginx:root dist /usr/share/nginx/html

EXPOSE 80

