import json
import logging.config
import pathlib

from textblob import TextBlob

from abstract_analyzer.abstract_analyzer import SentimentAnalyzer

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger("analyzer_textblob")


class TextBlobAnalyzer(SentimentAnalyzer):
    def __init__(self):
        super().__init__(consumer_group_id="analyzer_textblob")

    async def calculate_sentiment(self, raw_bill: dict) -> dict:
        sentiment = TextBlob(raw_bill.get("title")).sentiment._asdict()
        log.debug(f"Sentiment {sentiment}: {raw_bill.get('title')}")
        return sentiment


def main():
    log.info("Starting TextBlobAnalyzer")
    analyzer = TextBlobAnalyzer()
    analyzer.start()


if __name__ == "__main__":
    main()
