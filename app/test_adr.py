import os
from unittest import TestCase
from unittest.mock import patch

from app.auth import FlaskServerTestCase

from app.helpers import encrypt
from app.server import app
from app.service.adr_mks_client_02_04 import extract
from app.config import get_jwt_key

jwk_string = "RsKzMu5cIx92FSzLZz1RmsdLg7wJQPTwsCrkOvNNlqg"


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "adr_response.xml")
EMPTY_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "adr_empty_response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, "rb") as response_file:
        return response_file.read()


def get_empty_xml_response_fixture(*args):
    with open(EMPTY_RESPONSE_PATH, "rb") as response_file:
        return response_file.read()


@patch.dict(os.environ, {"MKS_JWT_KEY": jwk_string})
class AdrTest(TestCase):
    def get_result(self):
        return {"residentCount": 3, "crossRefNummer": "MijnAmsterdam"}

    def test_config(self):
        key = get_jwt_key().export()

        self.assertIn(jwk_string, key)

    def test_extraction(self):
        xml_data = get_xml_response_fixture()

        result = extract(xml_data)

        self.assertEqual(result, self.get_result())

    def test_empty_extraction(self):
        xml_data = get_empty_xml_response_fixture()

        result = extract(xml_data)
        self.assertEqual(result, None)


@patch.dict(os.environ, {"MKS_JWT_KEY": jwk_string})
class ResidentsTest(FlaskServerTestCase):
    app = app

    @patch("app.service.adr_mks_client_02_04._get_response", get_xml_response_fixture)
    def test_adr_call(self):
        post_body = {"addressKey": encrypt("1234")}

        response = self.post_secure("/brp/aantal_bewoners", json=post_body)
        self.assertEqual(
            response.json,
            {
                "content": {"crossRefNummer": "MijnAmsterdam", "residentCount": 3},
                "status": "OK",
            },
        )

    @patch("app.service.adr_mks_client_02_04._get_response", get_xml_response_fixture)
    def test_adr_call_empty(self):
        response = self.post_secure("/brp/aantal_bewoners", json="")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "bad request")
        self.assertEqual(response.json["status"], "ERROR")

    @patch("app.service.adr_mks_client_02_04._get_response", get_xml_response_fixture)
    def test_adr_call_wrong_key(self):
        response = self.post_secure("/brp/aantal_bewoners", json={"wrongKey": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "bad request")
        self.assertEqual(response.json["status"], "ERROR")

    @patch("app.service.adr_mks_client_02_04._get_response", get_xml_response_fixture)
    def test_adr_call_not_encrypted(self):
        post_body = {"addressKey": "1234"}

        response = self.post_secure("/brp/aantal_bewoners", json=post_body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "bad request")
        self.assertEqual(response.json["status"], "ERROR")

    @patch(
        "app.service.adr_mks_client_02_04._get_response", get_empty_xml_response_fixture
    )
    def test_empty_adr(self):
        response = self.post_secure(
            "/brp/aantal_bewoners", json={"addressKey": encrypt("1234")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["content"], None)
        self.assertEqual(response.json["status"], "OK")
