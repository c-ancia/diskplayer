import unittest, os, json
from player import Player

class TestPlayer(unittest.TestCase):
    def test_loadConfig(self):
        with self.assertRaises(FileNotFoundError):
            pla = Player("src/test/player/00_inexistant.txt")
        with self.assertRaises(json.decoder.JSONDecodeError):
            pla = Player( "src/test/player/01_dummy.txt")
        pla = Player("src/test/player/02_empty_conf.json")
        self.assertEqual(pla.config, {})
        filepath = "resources/config.json"
        pla = Player(filepath)
        with open(filepath) as json_file:
            config = json.load(json_file)
        self.assertEqual(pla.config, config) 
        
if __name__ == '__main__':
    unittest.main()