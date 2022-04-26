FROM amsterdam/python:3.9.6-buster

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

RUN apt-get install -y libxml2-dev

WORKDIR /api

COPY app /api/app
COPY scripts /api/scripts
COPY requirements.txt /api
COPY uwsgi.ini /api

COPY /test.sh /api
COPY .flake8 /api

COPY /cert/*.crt /usr/local/share/ca-certificates/extras/
RUN chmod -R 644 /usr/local/share/ca-certificates/extras/ \
	&& update-ca-certificates

RUN pip install --no-cache-dir -r /api/requirements.txt

USER datapunt
CMD uwsgi --ini /api/uwsgi.ini
