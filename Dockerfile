FROM ruby:2.7-alpine

RUN apk -Uuv add python3

ARG version='1.0.1'
RUN gem install cfndsl -v $version

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

RUN addgroup -S mygroup && adduser -S myuser -G mygroup -u 1000
USER myuser

COPY main.py entrypoint.sh /app/
ENTRYPOINT ["/app/entrypoint.sh"]
