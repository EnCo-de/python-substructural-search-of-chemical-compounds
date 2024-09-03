import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

datefmt="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}"
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s - %(message)s')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler('exceptions.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
