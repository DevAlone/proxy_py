FROM python:3.7-slim

RUN apt update && apt install -y wget > /dev/null && rm -rf /var/lib/apt/lists/* \
	&& rm /bin/sh && ln -s /bin/bash /bin/sh \
	&& groupadd -r user && useradd --create-home --no-log-init -r -g user user \
	&& mkdir /proxy_py && chown user:user /proxy_py

WORKDIR /proxy_py
USER user
# TODO: change to master
ARG VERSION=dockerizing

RUN wget https://github.com/DevAlone/proxy_py/archive/$VERSION.tar.gz -O sources.tar.gz 2> /dev/null \
	&& tar -xf sources.tar.gz && rm sources.tar.gz \
	&& mv proxy_py-*/.[!.]* ./ && mv proxy_py-*/* ./ \
	&& rmdir proxy_py-* \
	&& python3 -m venv env

RUN cp config_examples/settings.py proxy_py/settings.py
RUN source ./env/bin/activate && pip3 install -r requirements.txt --no-cache-dir

EXPOSE 55555
CMD ./run.sh
