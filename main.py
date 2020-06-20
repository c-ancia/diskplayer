
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
    parser.add_option("", "--prev", dest="prev", action="store_true", help="Skip to previous song.")
    parser.add_option("", "--next", dest="next", action="store_true", help="Skip to next song.")
    (options, args) = parser.parse_args()
    
    nb_options = 0
    stringValues = ["uri", "path"]
    for opt, value in options.__dict__.items():
        if (opt in stringValues and value != "") or (opt not in stringValues and value != None):
            nb_options += 1
    
    if (nb_options == 0):
        parser.error("Please specify at least one command.") 
        
    if (nb_options > 1):
        parser.error("Please specify only one command.") 
        
    config_file_path = f"{project_dir}{os.path.sep}resources/config.json"
        
    if options.path != "":
        rec = Recorder(path=options.path)
        rec.read()
        if rec.content != "":
            pla = Player(config_file_path)
            # Check if we play a new album/playlist or resume
            playback = pla.getCurrentPlayback()
            if playback == None or playback["context"]["uri"] != rec.content.strip():
                pla.play(uri=rec.content)
            else:
                pla.play()
    elif options.uri != "":
        pla = Player(config_file_path)
        pla.play(uri=options.uri)
    elif options.pause != None:
        pla = Player(config_file_path)
        pla.pause()
    elif options.current != None:
        pla = Player(config_file_path)
        pla.getCurrentPlayback()
    elif options.resume != None:
        pla = Player(config_file_path)
        pla.play()
    elif options.prev != None:
        pla = Player(config_file_path)
        pla.prev()
    elif options.next != None:
        pla = Player(config_file_path)
        pla.next()
    
if __name__ == "__main__":
   main(sys.argv[1:])