import json
import os
from unittest.mock import patch

from app.auth import PROFILE_TYPE_COMMERCIAL, FlaskServerTestCase
from app.server import app
from app.test_mks_client_bsn_hr import get_bsn_xml_response_fixture
from .test_02_04_model import RESPONSE_PATH, BRP_RESPONSE
from .test_mks_client_kvk_mac_hr import (
    KVK_HR_MAC_RESPONSE,
    get_kvk_mac_xml_response_fixture,
)
from .test_mks_client_kvk_prs_hr import (
    KVK_HR_EENMANSZAAK_RESPONSE,
    get_xml_response_empty_fixture,
)
from .test_mks_client_nnp_hr import NNP_HR_RESPONSE, get_nnp_xml_response_fixture


def get_bsn_xml_brp_response_fixture():
    with open(RESPONSE_PATH, "rb") as response_file:
        return response_file.read().decode("utf-8")


def wrap_response(response_data, status: str = "OK"):
    return {
        "content": json.loads(json.dumps(response_data, default=str)),
        "status": status,
    }


@patch.dict(
    os.environ,
    {
        "MA_BUILD_ID": "999",
        "MA_GIT_SHA": "abcdefghijk",
        "MA_OTAP_ENV": "unittesting",
    },
)
class ApiTests(FlaskServerTestCase):
    app = app

    def test_status(self):
        response = self.client.get("/status/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode(),
            '{"content":{"buildId":"999","gitSha":"abcdefghijk","otapEnv":"unittesting"},"status":"OK"}\n',
        )

    def _get_expected_private_hr(self):
        return wrap_response(KVK_HR_EENMANSZAAK_RESPONSE)

    def _get_expected_private(self):
        return wrap_response(BRP_RESPONSE["persoon"])

    def _get_expected_commercial_hr(self):
        return wrap_response({**KVK_HR_MAC_RESPONSE, **NNP_HR_RESPONSE})

    @patch(
        "app.service.mks_client_hr.HR_URL",
        "http://localhost/some/api/endpoint",
    )
    @patch(
        "app.service.mks_client_hr._get_response_by_bsn",
        lambda bsn: get_bsn_xml_response_fixture(),
    )
    def test_bsn(self):
        response = self.get_secure("/brp/hr")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected_private_hr())

    @patch(
        "app.service.mks_client_02_04.get_0204_raw",
        lambda bsn: get_bsn_xml_brp_response_fixture(),
    )
    def test_brp_show_bsn(self):
        response = self.get_secure("/brp/brp")
        self.assertEqual(response.status_code, 200)
        supposed_result = self._get_expected_private()["content"]
        self.assertEqual(response.json["content"]["persoon"], supposed_result)

    @patch(
        "app.service.mks_client_hr.HR_URL",
        "http://localhost/some/api/endpoint",
    )
    @patch(
        "app.service.mks_client_hr._get_response_by_kvk_number",
        lambda kvk_number: get_kvk_mac_xml_response_fixture(),
    )
    @patch(
        "app.service.mks_client_hr._get_response_by_nnpid",
        lambda kvk_number: get_nnp_xml_response_fixture(),
    )
    def test_get_mac_hr(self):
        response = self.get_secure("/brp/hr", profile_type=PROFILE_TYPE_COMMERCIAL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected_commercial_hr())

    @patch(
        "app.service.mks_client_hr._get_response_by_kvk_number",
        lambda kvk_number: get_xml_response_empty_fixture(),
    )
    def test_empty(self):
        response = self.get_secure("/brp/hr", profile_type=PROFILE_TYPE_COMMERCIAL)
        self.assertEqual(response.status_code, 200)
