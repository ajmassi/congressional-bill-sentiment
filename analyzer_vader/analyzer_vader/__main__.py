import json
import logging.config
import pathlib

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from abstract_analyzer.abstract_analyzer import SentimentAnalyzer

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger(__name__)


class VaderAnalyzer(SentimentAnalyzer):
    def __init__(self):
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()

    async def calculate_sentiment(self, raw_bill: dict) -> dict:
        sentiment = self.analyzer.polarity_scores(raw_bill.get("title"))
        log.debug(f"Calculated Sentiment for Bill:\n{sentiment}\n{raw_bill.get('title')}")
        return sentiment


def main():
    analyzer = VaderAnalyzer()
    analyzer.start()


if __name__ == "__main__":
    main()
