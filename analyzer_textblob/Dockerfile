FROM kafka-client-base:latest

COPY requirements.txt ./
COPY deps/ ./deps/
RUN pipenv install -r requirements.txt

COPY analyzer_textblob/ ./analyzer_textblob/

CMD [ "pipenv", "run", "python", "analyzer_textblob" ]
