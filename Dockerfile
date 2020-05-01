FROM python:3.7-slim

RUN \
    apt-get update \
#	&& apt-get install -y wget \
#    && apt-get install -y libzmq3-dev \
	&& rm -rf /var/lib/apt/lists/* \
	&& rm /bin/sh \
	&& ln -s /bin/bash /bin/sh \
	&& groupadd -r user \
	&& useradd --create-home --no-log-init -r -g user user \
	&& mkdir /proxy_py \
	&& chown user:user /proxy_py

WORKDIR /proxy_py
USER user

COPY sources.tar.gz .


RUN \
#    python3 -m venv ./environment \
#	&& source ./environment/bin/activate \
	cd /proxy_py/ \
	&& tar xf sources.tar.gz \
	&& rm sources.tar.gz \
	&& echo "Installing dependencies..." \
	&& pip3 install -r requirements.txt --no-cache-dir

#EXPOSE 55555
