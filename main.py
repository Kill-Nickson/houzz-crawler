from loguru import logger

from src.crawler import HouzzCrawler
from src.utils.loguru_config import config


logger.configure(**config)


def main():
    logger.info("Started collecting contractors data.")
    HouzzCrawler().run()
    logger.info("Finished collecting contractors data.")


if __name__ == '__main__':
    main()
