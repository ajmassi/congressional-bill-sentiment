FROM kafka-client-base:latest

COPY requirements.txt ./
RUN pip install --require-hashes -r requirements.txt

COPY analyzer_vader/ ./analyzer_vader/

# Manual Testing
ENTRYPOINT ["tail", "-f", "/dev/null"]
