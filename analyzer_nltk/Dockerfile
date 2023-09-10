FROM kafka-client-base:latest

COPY requirements.txt ./
RUN pip install --require-hashes -r requirements.txt

# Manual Testing
# ENTRYPOINT ["tail", "-f", "/dev/null"]