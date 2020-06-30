
import os, re
from .loghandler import Logger, LoggerType

URI_REGEXP = r"^spotify:(album|playlist):[a-zA-Z0-9]+$"
URL_REGEXP = r"^https://open.spotify.com/(album|playlist)/[a-zA-Z0-9]+$"

class Recorder: 
    uri = "" # Spotify URI of album/playlist to play.
    path = "" # "Path to file containing Spotify URI to play.
    content = ""
    logger = None

    def __init__(self, uri = "", path = ""):
        super().__init__()
        self.uri = uri
        self.path = path
        self.logger = Logger("recorder.log")

    def file_exists(self):
        return os.path.exists(self.path) and os.path.isfile(self.path) and os.stat(self.path).st_size != 0

    def read(self):
        if os.path.exists(self.path):
            if os.path.isfile(self.path):
                if os.stat(self.path).st_size != 0:
                    with open(self.path) as f:
                        self.content = f.read()
                    f.close()
                    return self.check_content()
                else:
                    return self.logger.write_log(f"nothing to read in file {self.path}.")
            else:
                return self.logger.write_log(f"{self.path} is not a file.")
        else:
            return self.logger.write_log(f"file {self.path} doesn't exists.")

    def check_content(self):
        if self.content == "" and self.uri == "":
            return  self.logger.write_log(f"no content nor uri to play.")
        elif self.content != "":
            if re.match(URI_REGEXP, self.content) != None:
                return self.logger.write_log(f"play {self.path} with content {self.content}", LoggerType.INFO)
            else:
                return self.logger.write_log(f"the content {self.content} is not a proper URI.")
        elif self.uri != "":
            self.transform_url()
            if re.match(URI_REGEXP, self.uri) != None:
                return self.logger.write_log(f"play uri {self.uri}", LoggerType.INFO)
            else:
                return self.logger.write_log(f"the uri {self.uri} is not a proper URI.")

    def record(self):
        if os.path.exists(self.path) and os.path.isfile(self.path):
            return self.logger.write_log(f"the file {self.path} exists.")
        elif self.uri == "":
            return self.logger.write_log("no URI to record.")
        else:
            self.transform_url()
            if re.match(URI_REGEXP, self.uri) == None:
                return self.logger.write_log("wrong format of text to record.")
            if self.write():
                return self.logger.write_log(f"Content {self.uri} saved to {self.path}", LoggerType.INFO)
            else:
                return self.logger.write_log(f"Something went wrong while saving {self.uri} in {self.path}")

    def transform_url(self):
        if re.match(URL_REGEXP, self.uri) != None:
            tempuri = self.uri.replace("https://", "").split("/")
            self.uri = ":".join(["spotify"] + tempuri[1:])

    def write(self):
        with open(self.path, "w+") as f:
            f.write(self.uri)
        f.close()
        return True