#Using alpine for base image
FROM nginx:1.17.1-alpine

#Prepared by
MAINTAINER Mayank Koli <mayank.c.koli@gmail.com>
#Removing Unecessary files
RUN rm /etc/nginx/conf.d/default.conf
#Copying configuration file
COPY flask.conf /etc/nginx/conf.d/
#Exposing image on 80 port
EXPOSE 80
#Running supervisiond which will run all program at once
#CMD ["nginx", "-c", "/etc/nginx/nginx.conf"]
