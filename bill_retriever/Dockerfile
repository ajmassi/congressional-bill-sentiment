FROM kafka-client-base:latest

RUN apk update && apk add curl
COPY requirements.txt ./
RUN pipenv install -r requirements.txt

COPY bill_retriever/ ./bill_retriever/
COPY secrets/ ./secrets/

# Manual Testing
ENTRYPOINT ["tail", "-f", "/dev/null"]
