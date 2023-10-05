FROM kafka-client-base:latest

COPY requirements.txt ./
RUN pipenv install -r requirements.txt

COPY sentiment_aggregator/ ./sentiment_aggregator/

CMD [ "pipenv", "run", "python", "sentiment_aggregator" ]
