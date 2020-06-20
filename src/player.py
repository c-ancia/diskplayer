
from src.loghandler import Logger
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
        self.loadConfig(config)
        
    def loadConfig(self, filepath):
        try:
            with open(filepath) as json_file:
                self.config = json.load(json_file)
        except Exception as e:
            self.logger.writeLog(e)
            raise e
            
    def getAuth(self):
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
                        self.getAuth()
                    token = self.oauth.refresh_access_token(refresh_token=token["refresh_token"])
                self.sp = spotipy.Spotify(auth=token["access_token"])
            else:
                if self.oauth == None:
                        self.getAuth()
                self.sp = spotipy.Spotify(oauth_manager=self.oauth)
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
        
    def find(self):
        try:
            if self.sp == None:
                self.auth()
            else:
                devices_list = self.sp.devices()
                if devices_list:
                    for item in devices_list["devices"]:
                        if item["name"] == self.config["spotify"]["device_name"]:
                            self.device_id = item["id"]
                    if self.device_id == None:
                        return self.logger.writeLog(f"device not found.")
                else:
                    return self.logger.writeLog(f"no devices available.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
            
    def play(self, uri = None):
        try:
            if self.sp == None:
                self.auth()  
            if self.device_id == None:
                self.find()
            if self.device_id:        
                if uri != None:
                    self.sp.start_playback(context_uri=uri, device_id=self.device_id)
                else:
                    self.sp.start_playback(device_id=self.device_id)
            else:
                return self.logger.writeLog(f"device not found.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
        
            
    def pause(self):
        try:
            if self.sp == None:
                self.auth()  
            if self.device_id == None:
                self.find()
            if self.device_id:       
                self.sp.pause_playback(device_id=self.device_id)
            else:
                return self.logger.writeLog(f"device not found.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
        
    def prev(self):
        try:
            if self.sp == None:
                self.auth()
            if self.device_id == None:
                self.find()
            if self.device_id:
                self.sp.previous_track(device_id=self.device_id)
            else:
                return self.logger.writeLog(f"device not found.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
        
    def next(self):
        try:
            if self.sp == None:
                self.auth()
            if self.device_id == None:
                self.find()
            if self.device_id:
                self.sp.next_track(device_id=self.device_id)
            else:
                return self.logger.writeLog(f"device not found.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)    
        
    def getCurrentPlayback(self):
        try:
            if self.sp == None:
                self.auth()  
            if self.device_id == None:
                self.find()
            if self.device_id:    
                return self.sp.currently_playing()
            else:
                return self.logger.writeLog(f"device not found.")
        except spotipy.oauth2.SpotifyOauthError as e:
            return self.logger.writeLog(e)
