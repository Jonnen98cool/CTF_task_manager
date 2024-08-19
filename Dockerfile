#Set container OS. These are slimmed-down versions of the OS.
FROM ubuntu:22.04

#Set working dirrectory, / means root of the container
WORKDIR /flaskApp

#Copy all files from host system current dir to container dir
COPY ./ /flaskApp

#The app database needs to persist when we stop the container and
#then launch it back up. This line ensures that.
VOLUME /flaskApp/instance/

#Download necessary stuff for our container. 
RUN    apt-get update -y \
	&& apt-get install -y nginx \
	&& apt-get install -y python3 \
	&& apt-get install -y python3-pip \
	&& pip install -r requirements.txt \
	&& pip install gunicorn
#	&& pip install ngxtop==0.0.3

#Replace default nginx configuration
COPY ./nginx.conf /etc/nginx/
