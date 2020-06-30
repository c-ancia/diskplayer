import unittest, os
from .recorder import Recorder

class TestRecorder(unittest.TestCase):
    def test_read(self):
        rec = Recorder(path="mydir")
        result = rec.read()
        self.assertEqual(result["message"], "file mydir doesn't exists.")
        rec.path = "resources"
        result = rec.read()
        self.assertEqual(result["message"], "resources is not a file.")
        rec.path = "src/test/recorder/01_empty.txt"
        result = rec.read()
        self.assertEqual(result["message"], "nothing to read in file src/test/recorder/01_empty.txt.")
        rec.path = "src/test/recorder/02_somecontent.txt"
        result = rec.read()
        self.assertEqual(result["message"], "the content test some content 123 is not a proper URI.")

    def test_check_content(self):
        rec = Recorder()
        result = rec.check_content()
        self.assertEqual(result["message"], "no content nor uri to play.")
        rec.uri="https://open.spotify.com/album/4Fl6pgHomJyIduHVoO4yJE"
        result = rec.check_content()
        self.assertEqual(result["message"], "play uri spotify:album:4Fl6pgHomJyIduHVoO4yJE")
        rec.uri="spotify:album:4Fl6pgHomJyIduHVoO4yJE"
        result = rec.check_content()
        self.assertEqual(result["message"], "play uri spotify:album:4Fl6pgHomJyIduHVoO4yJE")
        rec.uri="https://open.spotify.com/playlist/37i9dQZF1DXdLEN7aqioXM"
        result = rec.check_content()
        self.assertEqual(result["message"], "play uri spotify:playlist:37i9dQZF1DXdLEN7aqioXM")
        rec.uri="spotify:playlist:37i9dQZF1DXdLEN7aqioXM"
        result = rec.check_content()
        self.assertEqual(result["message"], "play uri spotify:playlist:37i9dQZF1DXdLEN7aqioXM")
        rec.uri=""
        rec.path="src/test/recorder/02_somecontent.txt"
        result = rec.check_content()
        self.assertEqual(result["message"], "no content nor uri to play.")
        rec.read()
        result = rec.check_content()
        self.assertEqual(result["message"], "the content test some content 123 is not a proper URI.")
        rec.path = "src/test/recorder/03_album.txt"
        rec.read()
        result = rec.check_content()
        self.assertEqual(result["message"], "play src/test/recorder/03_album.txt with content spotify:album:4Fl6pgHomJyIduHVoO4yJE")
        rec.path = "src/test/recorder/04_playlist.txt"
        rec.read()
        result = rec.check_content()
        self.assertEqual(result["message"], "play src/test/recorder/04_playlist.txt with content spotify:playlist:37i9dQZF1DXdLEN7aqioXM")

    def test_record(self):
        rec = Recorder(path="src/test/recorder/01_empty.txt")
        result = rec.record()
        self.assertEqual(result["message"], "the file src/test/recorder/01_empty.txt exists.")
        rec.path = "src/test/recorder/05a_missingURI.txt"
        result = rec.record()
        self.assertEqual(result["message"], "no URI to record.")
        rec.path = "src/test/recorder/05b_randomtext.txt"
        rec.uri = "I am a random text"
        result = rec.record()
        self.assertEqual(result["message"], "wrong format of text to record.")
        rec.path = "src/test/recorder/05c_wrongURL.txt"
        rec.uri = "https://www.google.com"
        result = rec.record()
        self.assertEqual(result["message"], "wrong format of text to record.")
        rec.path = "src/test/recorder/05d_wrongURI.txt"
        rec.uri = "spotify:artist:6n1fB5NgTsFNdT4JHpVMe1"
        result = rec.record()
        self.assertEqual(result["message"], "wrong format of text to record.")
        rec.path = "src/test/recorder/06a_recordURLalbum.txt"
        rec.uri = "https://open.spotify.com/album/4Fl6pgHomJyIduHVoO4yJE"
        result = rec.record()
        self.assertEqual(result["message"], "Content spotify:album:4Fl6pgHomJyIduHVoO4yJE saved to src/test/recorder/06a_recordURLalbum.txt")
        rec.path = "src/test/recorder/06b_recordURIalbum.txt"
        rec.uri = "spotify:album:4Fl6pgHomJyIduHVoO4yJE"
        result = rec.record()
        self.assertEqual(result["message"], "Content spotify:album:4Fl6pgHomJyIduHVoO4yJE saved to src/test/recorder/06b_recordURIalbum.txt")
        rec.path = "src/test/recorder/07a_recordURLplaylist.txt"
        rec.uri = "https://open.spotify.com/playlist/37i9dQZF1DXdLEN7aqioXM"
        result = rec.record()
        self.assertEqual(result["message"], "Content spotify:playlist:37i9dQZF1DXdLEN7aqioXM saved to src/test/recorder/07a_recordURLplaylist.txt")
        rec.path = "src/test/recorder/07b_recordURIplaylist.txt"
        rec.uri = "spotify:playlist:37i9dQZF1DXdLEN7aqioXM"
        result = rec.record()
        self.assertEqual(result["message"], "Content spotify:playlist:37i9dQZF1DXdLEN7aqioXM saved to src/test/recorder/07b_recordURIplaylist.txt")

    @classmethod  
    def teardown_class(cls):
        os.remove("src/test/recorder/06a_recordURLalbum.txt") 
        os.remove("src/test/recorder/06b_recordURIalbum.txt") 
        os.remove("src/test/recorder/07a_recordURLplaylist.txt") 
        os.remove("src/test/recorder/07b_recordURIplaylist.txt") 

if __name__ == '__main__':
    unittest.main()