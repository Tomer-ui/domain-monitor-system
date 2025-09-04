import logging
import sys


log_level = 'DEBUG'
log_file = 'domain_checker.log'

logging.basicConfig(
    level= log_level,
    format= '[Time: %(asctime)s, File: %(filename)s:%(lineno)d, Function: %(funcName)s] %(levelname)-s - %(message)s',
    handlers= [logging.FileHandler(log_file),
               logging.StreamHandler(sys.stdout)
               ]
    )
#with this i will import the logger onto other files.

logger = logging.getLogger(__name__)
