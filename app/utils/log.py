import logging
import sys

from app.settings import LOG_LEVEL

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger('PSEUDOCONE')
logger.setLevel(LOG_LEVEL)
logger.propagate = False
logger.parent.propagate = False

# need to add a new handler or nothing is outputted
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
