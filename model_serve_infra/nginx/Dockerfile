FROM nginx

#install logrotate for log compress
RUN apt-get update && apt-get install -y logrotate cron 

# delete nginx default .conf files
RUN rm /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/nginx.conf

# add conf files for blue and green
COPY nginx_green.conf /etc/nginx/nginx_green.conf
COPY nginx_blue.conf /etc/nginx/nginx_blue.conf

#COPY log compress config
COPY logrotate.conf /etc/logrotate.d/nginx

# link to custom config, by default green deployment
# for convenience of swap deploy
RUN ln -s /etc/nginx/nginx_green.conf /etc/nginx/nginx.conf
