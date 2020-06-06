
import sys, os, logging
from optparse import OptionParser
from src.recorder import Recorder
from src.player import Player


def main(argv):
    project_dir = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-1])
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("", "--uri", dest="uri", default="", help="Spotify URI of album/playlist to play.")
    parser.add_option("", "--path", dest="path", default="", help="Path to file containing Spotify URI to play.")
    parser.add_option("", "--current", dest="current", action="store_true", help="Get the currently played song.")
    parser.add_option("", "--pause", dest="pause", action="store_true", help="Pause the stream.")
    (options, args) = parser.parse_args()
    
    if options.uri != "" and options.path != "":
        parser.error("Please specify either [uri] or [path], but not both.") 
        
    if options.current != None and (options.uri != "" or options.path != ""):
        parser.error("Please specify [current] only or any other command.") 
        
    config_file_path = f"{project_dir}{os.path.sep}resources/config.json"
        
    if options.path != "":
        rec = Recorder(path=options.path)
        rec.read()
        if rec.content != "":
            pla = Player(config_file_path)
            pla.play(uri=rec.content)
    elif options.uri != "":
        pla = Player(config_file_path)
        pla.play(uri=options.uri)
    elif options.pause != None:
        pla = Player(config_file_path)
        pla.pause()
    elif options.current != None:
        pla = Player(config_file_path)
        pla.getCurrentPlayback()
    
if __name__ == "__main__":
   main(sys.argv[1:])