FROM kafka-client-base:latest

COPY requirements.txt ./
COPY deps/ ./deps/
RUN pipenv install -r requirements.txt

COPY analyzer_vader/ ./analyzer_vader/

# Manual Testing
ENTRYPOINT ["tail", "-f", "/dev/null"]
