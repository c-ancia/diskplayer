import os, logging
from enum import Enum

class LoggerType(Enum):
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    DEBUG = "debug"
    CRITICAL = "critical"
    EXCEPTION = "exception"

class Logger:
    logfile = ""

    def __init__(self, logfile):
        super().__init__()
        self.logfile = logfile
        filepath = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-2])
        filename = f"{filepath}{os.path.sep}logs{os.path.sep}{self.logfile}"
        logging.basicConfig(filename=filename,level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def write_log(self, message, logtype = LoggerType.ERROR):
        getattr(logging, logtype.value)(message)
        return {"error": logtype != LoggerType.INFO, "message": message}