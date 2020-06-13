import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, 'PATH_TO_PROJECT/diskplayer/')
from app import app as application
application.secret_key = 'YOUR_SECRET_KEY'
