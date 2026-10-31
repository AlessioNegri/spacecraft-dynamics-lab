import coloredlogs
import logging

logger: logging.Logger = logging.getLogger(name="spacelab")

if not logger.handlers:
    
    handler = logging.StreamHandler()
    
    logger.addHandler(hdlr=handler)
    
    fmt: str = "<%(name)s> %(asctime)s.%(msecs)3d | %(levelname)-8s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"
    
    datefmt: str = "%Y-%m-%d %H:%M:%S"
    
    coloredlogs.install(level="DEBUG", logger=logger, fmt=fmt, datefmt=datefmt, milliseconds=True)
