#############################
# Dev environment
.PHONY: dev-init dep-lock

dev-init:
	pipenv sync --categories="packages analyzer_nltk analyzer_vader bill_retriever sentiment_aggregator" -v

dep-lock:
	pipenv requirements --hash --categories="packages" > ./requirements.txt
	pipenv requirements --hash --categories="analyzer_nltk" > ./analyzer_nltk/requirements.txt
	pipenv requirements --hash --categories="analyzer_vader" > ./analyzer_vader/requirements.txt
	pipenv requirements --hash --categories="bill_retriever" > ./bill_retriever/requirements.txt
	pipenv requirements --hash --categories="sentiment_aggregator" > ./sentiment_aggregator/requirements.txt

#############################
# Docker
.PHONY: build, up, down, logs

build:
	make dep-lock
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f
