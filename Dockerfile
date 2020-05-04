FROM amsterdam/python3.8
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

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

COPY mks /app/mks
COPY docker-entrypoint.sh /app/
USER datapunt
CMD ["/app/docker-entrypoint.sh"]
