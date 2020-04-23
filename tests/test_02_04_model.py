import os
from unittest.case import TestCase

from bs4 import BeautifulSoup

from mks.model.stuf_02_04 import extract_data


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204.xml")


class Model0204Tests(TestCase):
    def test_response(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        print("result", result)
