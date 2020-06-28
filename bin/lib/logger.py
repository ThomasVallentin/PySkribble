import logging as log
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL


def Logger(name, level=log.INFO):
    logger = log.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        handler = log.StreamHandler()
        handler.setLevel(log.DEBUG)
        formatter = log.Formatter("%(levelname)s - %(name)s : %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
