#############################
# Dev environment
.PHONY: dev-init dep-lock build-abstract-analyzer distribute-abstract-analyzer prep-services

dev-init:
	pipenv --rm
	pipenv sync --categories="packages dev-packages analyzer_textblob analyzer_vader bill_retriever sentiment_aggregator" -v

dep-lock:
	pipenv requirements --hash --categories="packages" > ./requirements.txt
	pipenv requirements --hash --categories="analyzer_textblob" > ./analyzer_textblob/requirements.txt
	pipenv requirements --hash --categories="analyzer_vader" > ./analyzer_vader/requirements.txt
	pipenv requirements --hash --categories="bill_retriever" > ./bill_retriever/requirements.txt
	pipenv requirements --hash --categories="sentiment_aggregator" > ./sentiment_aggregator/requirements.txt

build-abstract-analyzer:
	cd ./abstract_analyzer/; python3 ./setup.py sdist
	mkdir -p ./deps/
	cp ./abstract_analyzer/dist/abstract_analyzer*.tar.gz ./deps/

distribute-abstract-analyzer:
	cp ./abstract_analyzer/dist/abstract_analyzer*.tar.gz ./analyzer_vader/deps/
	cp ./abstract_analyzer/dist/abstract_analyzer*.tar.gz ./analyzer_textblob/deps/

prep-services:
	make build-abstract-analyzer
	make distribute-abstract-analyzer

#############################
# Docker
.PHONY: build, up, down, logs

build:
	make dep-lock
	make prep-services
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

#############################
# Code Quality
.PHONY: format, isort, flake8, black, bandit, test
format: isort flake8 black bandit

isort:
	$(info ---------- ISORT ----------)
	pipenv run isort .

flake8:
	$(info ---------- FLAKE8 ----------)
	pipenv run flake8 . \
	    --count --select=B,C,E,F,W,T4,B9 --max-complexity=18 \
	    --ignore=E501,B950 \
	    --show-source --statistics

black:
	$(info ---------- BLACK ----------)
	pipenv run black .

bandit:
	$(info ---------- BANDIT ----------)
	pipenv run bandit -c "pyproject.toml" --recursive .
