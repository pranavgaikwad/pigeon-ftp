import unittest
from pftp.utils.config import PFTPCLIENT_MEM_LIM

class ConfigTest(unittest.TestCase):

    def test_config(self):
        self.assertEqual(PFTPCLIENT_MEM_LIM, 1024)

if __name__ == "__main__":
    unittest.main()