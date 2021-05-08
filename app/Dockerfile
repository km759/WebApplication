FROM python:3.8

RUN mkdir /app

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app

RUN apk add -U --no-cache --virtual=build-dependencies \
    gcc linux-headers musl musl-dev

RUN cd /app \
    && pip install -r requirements.txt --upgrade pip
    && apk del build-dependencies \
    && rm -rf /var/cache/apk/* \
    && mv /app/start.sh /start \
    && chmod +x /start

COPY . /app

CMD python app.py