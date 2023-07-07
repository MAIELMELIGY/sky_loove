FROM python:3.11-slim-bullseye as builder


ENV APP_HOME=/opt/application/webapp
WORKDIR $APP_HOME

COPY ./requirements.txt $APP_HOME

RUN apt-get update
RUN apt-get install --yes --no-install-recommends gcc netcat libmariadb-dev-compat curl libstdc++6 apt-transport-https ca-certificates
RUN update-ca-certificates
RUN pip install -r requirements.txt
COPY . $APP_HOME
RUN chmod +x $APP_HOME/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/opt/application/webapp/docker-entrypoint.sh"]
