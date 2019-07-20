#Using alpine for base image
FROM alpine:3.10

#Prepared by
MAINTAINER Mayank Koli <mayank.c.koli@gmail.com>

#Installing necessary packages
RUN apk update && apk add python3 python3-dev build-base linux-headers pcre-dev
#Copying requirement file which is having module names used by python
COPY ./requirements.txt /project/requirements.txt
#Installing modules using pip command
RUN pip3 install -r /project/requirements.txt
#Copying configuration file
COPY uwsgi.ini /project
COPY server.py /project
#Chosing /project as default directory
WORKDIR /project
#Exposing image on 80 port
EXPOSE 8080
#Running supervisiond which will run all program at once
CMD ["uwsgi", "--ini", "uwsgi.ini"]
