<h2 align="center">Congressional Bill Sentiment</h2>

<!-- TABLE OF CONTENTS -->
### Table of Contents

- [About](#about)
  - [Why does this repo exist?](#why-does-this-repo-exist)
  - [What does it do?](#what-does-it-do)
  - [Hypothesis?](#hypothesis)
  - [How does it work?](#how-does-it-work)
  - [Built With](#built-with)
  - [Other Features](#other-features)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Dependencies](#dependencies)
  - [Development](#development)
  - [Execution](#execution)
    - [Start Everything](#start-everything)
    - [Stop Everything](#stop-everything)
    - [View Logs](#view-logs)

## About
### Why does this repo exist?
This repo is purely experimental - a technical solution in search of a problem. Using a handful of technologies that I would like to understand better in a from-the-ground up development setting, I've constructed a distributed pipeline to retrieve, enrich, store, and analyze data.

### What does it do?
Bearing in mind that this is a fairly contrived example... when up and running, the pipeline can retrieve Congressional Bill data, apply a suite of sentiment analyzers to the Bill's title, and then collect resulting information within a Neo4j database for later analysis.

### Hypothesis?
For the sake of giving this experiment purpose: I hypothesize that there should be little-to-no variance in average Bill title sentiment. Given that Bills are legal documents I expect them to be fairly neutral in their language, however this will also provide an interesting comparison between different sentiment analysis tools in how they rank the same text.

### How does it work?
* Everything runs in a container
* Services communicate over Kafka (KRaft)
* All data is stored within Neo4j
  
Again, in my ideal project I would be using constantly-generated high-throughput data, but what's more important for this proof-of-concept is making the pieces work together.

1. Starting with the public data set of [US Congressional data](https://api.congress.gov/#/), the `bill-retriever` service will asynchronously GET all Bills for a configured Congress.
2. Raw data returned from the API will be pushed to the `bill.raw` Kafka Topic.
3. Analyzers defined using `abstract_analyzer` (local python package to facilitate integration of sentiment analysis tools) will run in parallel, each consuming every message from `bill.raw`, applying unique analysis, and producing a processed output on the `bill.processed` Topic.
4. Finally, `sentiment-aggregator` consumes all messages from the `bill.raw` and `bill.processed` Topics and stores them within a Neo4j instance.
5. TODO: Analysis, graphing
6. Profit


### Built With

Python Packages:
- [Kafka](https://github.com/dpkp/kafka-python) - Producer/Consumer messaging
- [Pydantic](https://github.com/pydantic/pydantic) - Used for configuration management
- [VaderSentiment](https://github.com/cjhutto/vaderSentiment) - Sentiment Analyzer
- [TextBlob](https://github.com/sloria/TextBlob) - Sentiment Analyzer
- [Neo4j](https://github.com/neo4j/neo4j-python-driver) - Data storage


### Other Features
* Make "phony targets" are leveraged heavily to simplify the build process and streamline common tasks
* Part of the interest in building this as a mono-repo was exploring how one might organize/manage Python dependencies for the development environment while maintaining minimal Docker Images for each service. 
  * In this repo what I settled on was to have all dependencies be tracked by a top-level `Pipfile`; using categories to distinguish service-specific deps. This makes it so the developer's environment can install ALL dependencies and leverage VSCode IntelliSense. 
  * Before Docker image generation, each service is provided its own `requirements.txt` from which to install relevant deps.
  * **Note:** Major caveat to this technique is I'm not sure what would occur should there be version collisions between packages or package dependencies. I would expect it would not be pleasant.
* The `abstract_analyzer` package provides an Abstract Base Class (`SentimentAnalyzer`) for easy integration of new sentiment analyzers into the pipeline. Contained within the class are a Kafka Consumer and Producer for each instance, and a single abstract method `calculate_sentiment()` for subclasses to implement. Examples of implementation are provided in `analyzer_vader` and `analyzer_textblob`.

## Usage
### Configuration
1. In order to get things running in full, an API key needs to be [requested](https://api.congress.gov/sign-up/). The key should be pasted as-is in a file called `api_key` within `bill_retriever/secrets/`.

### Dependencies
The following are required on the host for operation:
```text
Python >= 3.11
Pipenv
Make
Docker
Docker Compose
```

### Development
Within the root directory run the following to initialize the development venv.
```
make dev-init
```

### Execution
#### Start Everything
Some containers are sensitive to startup order which is managed using various techniques in the `docker-compose` file. If it looks like things are hanging on startup, they might just be waiting on a healthcheck to pass.   
Within the root directory run the following:
```
make build
make up
```
**Note:** Currently the healthcheck for Neo4j is incorrect, this means that the following should be run to fix `sentiment-analyzer`.
```
docker compose restart sentiment-analyzer
```

#### Stop Everything
Within the root directory run the following:
```
make down
```

#### View Logs
Logs are best accessed directly, for example:
```
docker compose logs -f sentiment-analyzer
```
