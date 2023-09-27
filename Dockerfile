FROM python:3.11.4-alpine as kafka-client-base

ARG user_name
ARG user_id

ENV USER_NAME $user_name
ENV USER_HOME /home/$user_name

WORKDIR $USER_HOME
USER $user_name

ENV PATH=$PATH:/home/$user_name/.local/bin
ENV PYTHON=/usr/local/bin/python

COPY requirements.txt ./
COPY .env ./
RUN pip install --require-hashes -r requirements.txt

# Manual Testing
# ENTRYPOINT ["tail", "-f", "/dev/null"]
