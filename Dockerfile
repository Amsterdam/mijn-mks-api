FROM amsterdam/python:3.8.7-buster
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

EXPOSE 8000

RUN apt-get update \
	&& apt-get install -y \
		libxml2-dev \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt \
	&& pip install uwsgi

WORKDIR /app
COPY requirements.txt /app/
COPY uwsgi.ini /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY .flake8 /app/
COPY ./tests /app/tests

COPY *.crt /usr/local/share/ca-certificates/extras/
RUN chmod -R 644 /usr/local/share/ca-certificates/extras/ \
 && update-ca-certificates

COPY mks /app/mks
COPY docker-entrypoint.sh /app/
USER datapunt
CMD ["/app/docker-entrypoint.sh"]
