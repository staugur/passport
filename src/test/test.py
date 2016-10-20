# coding:utf8

import unittest
from api import app


class PassportTest(unittest.TestCase):

    def setUp(self):
        self.app    = app.test_client()
        self.logger = pub.logger

    def tearDown(self):
        self.logger.debug("test case")

if __name__ == '__main__':
    unittest.main()
