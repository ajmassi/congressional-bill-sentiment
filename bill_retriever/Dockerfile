FROM kafka-client-base:latest

RUN apk update && apk add curl
COPY requirements.txt ./
RUN pip install --require-hashes -r requirements.txt

COPY __main__.py ./

# Manual Testing
# ENTRYPOINT ["tail", "-f", "/dev/null"]
