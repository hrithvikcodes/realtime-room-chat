import logging
from pythonjsonlogger.jsonlogger import JsonFormatter # type: ignore

def get_logger(name:str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler.setFormatter(formatter) 
        logger.addHandler(handler)

    return logger

