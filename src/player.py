
from .loghandler import Logger
import os, spotipy, json

class Player: 
    oauth = None
    sp = None
    logger = None
    device_id = None
    config = None
    
    def __init__(self, config):
        super().__init__()
        self.logger = Logger("player.log")
        self.load_config(config)

    def load_config(self, filepath):
        try:
            with open(filepath) as json_file:
                self.config = json.load(json_file)
        except Exception as e:
            self.logger.write_log(e)
            raise e

    def check_connection(self):
        if self.sp == None:
            self.auth()

    def check_device(self):
        self.check_connection()
        if self.device_id == None:
            self.find()
        if self.device_id:
            return True
        else:
            self.logger.write_log(f"device not found.")
            return False

    def get_auth(self):
        self.oauth = spotipy.SpotifyOAuth(client_id=self.config["spotify"]["client_id"], client_secret=self.config["spotify"]["client_secret"],
            redirect_uri=self.config["spotify"]["redirect_url"], cache_path=self.config["spotify"]["token_path"],
            scope=self.config["spotify"]["scope_rights"])

    def auth(self):
        try:
            filepath = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-2])
            tokenpath = filepath + (os.path.sep) + self.config["spotify"]["token_path"]
            if os.path.exists(tokenpath) and os.path.isfile(tokenpath):
                with open(tokenpath) as json_file:
                    token = json.load(json_file)
                if spotipy.oauth2.is_token_expired(token):
                    if self.oauth == None:
                        self.get_auth()
                    token = self.oauth.refresh_access_token(refresh_token=token["refresh_token"])
                self.sp = spotipy.Spotify(auth=token["access_token"])
            else:
                if self.oauth == None:
                        self.get_auth()
                self.sp = spotipy.Spotify(oauth_manager=self.oauth)
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def find(self):
        try:
            self.check_connection()
            devices_list = self.sp.devices()
            if devices_list:
                for item in devices_list["devices"]:
                    if item["name"] == self.config["spotify"]["device_name"]:
                        self.device_id = item["id"]
                if self.device_id == None:
                    return self.logger.write_log(f"device not found.")
            else:
                return self.logger.write_log(f"no devices available.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def play(self, uri = None):
        try:
            if self.check_device():
                if uri != None:
                    self.sp.start_playback(context_uri=uri, device_id=self.device_id)
                else:
                    self.sp.start_playback(device_id=self.device_id)
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def pause(self):
        try:
            if self.check_device():
                self.sp.pause_playback(device_id=self.device_id)
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def prev(self):
        try:
            if self.check_device():
                self.sp.previous_track(device_id=self.device_id)
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def next(self):
        try:
            if self.check_device():
                self.sp.next_track(device_id=self.device_id) 
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)

    def get_current_playback(self):
        try:
            if self.check_device():
                return self.sp.currently_playing()
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.write_log(e)