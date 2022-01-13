FROM amsterdam/python:3.8.7-buster

LABEL maintainer=datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN apt-get update
RUN apt-get install -y libxml2-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN adduser --system datapunt
RUN pip install uwsgi

WORKDIR /app

COPY mks ./mks
COPY scripts ./scripts
COPY tests ./tests
COPY requirements.txt .
COPY uwsgi.ini .

COPY /test.sh /app
COPY .flake8 .

COPY *.crt /usr/local/share/ca-certificates/extras/
RUN chmod -R 644 /usr/local/share/ca-certificates/extras/ \
	&& update-ca-certificates

RUN pip install --no-cache-dir -r /app/requirements.txt

USER datapunt
CMD uwsgi --ini /app/uwsgi.ini
