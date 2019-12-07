FROM nginx

COPY password /password
COPY certs /certs
COPY nginx.conf /etc/nginx/nginx.conf
COPY fedor.conf /etc/nginx/conf.d/
#RUN ln -s /etc/nginx/sites-available/fedor.conf /etc/nginx/sites-enabled/fedor.conf

RUN mkdir /var/logs
