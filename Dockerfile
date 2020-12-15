FROM python:3.7

WORKDIR /srv/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY credentials/ ./credentials/
COPY .env ./
COPY src/ ./src/
COPY uwsgi.ini ./

EXPOSE 8000
ENTRYPOINT uwsgi uwsgi.ini
