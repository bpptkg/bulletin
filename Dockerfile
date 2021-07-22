FROM python:3.8

RUN mkdir /config
COPY requirements.txt /config/requirements.txt
RUN pip install -r /config/requirements.txt

RUN mkdir /app
COPY bulletin/ /app/bulletin/
COPY wo/ /app/wo/
COPY manage.py /app/manage.py

WORKDIR /app
