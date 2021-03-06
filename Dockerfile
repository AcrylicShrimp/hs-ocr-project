FROM python:3.7

WORKDIR /srv/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY credentials/ ./credentials/
COPY .env ./
COPY src/ ./src/
COPY uwsgi.ini ./

EXPOSE 8000
ENTRYPOINT uwsgi uwsgi.ini
