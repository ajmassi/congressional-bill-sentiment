FROM kafka-client-base:latest

COPY requirements.txt ./
COPY deps/ ./deps/
RUN pipenv install -r requirements.txt

# Manual Testing
# ENTRYPOINT ["tail", "-f", "/dev/null"]