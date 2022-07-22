import json
from app.test_mks_client_bsn_hr import get_bsn_xml_response_fixture
from unittest.mock import patch

from app.server import app
from app.auth import PROFILE_TYPE_COMMERCIAL, FlaskServerTestCase

from .test_mks_client_kvk_mac_hr import (
    KVK_HR_MAC_RESPONSE,
    get_kvk_mac_xml_response_fixture,
)
from .test_mks_client_kvk_prs_hr import (
    KVK_HR_EENMANSZAAK_RESPONSE,
    get_kvk_prs_xml_response_fixture,
    get_xml_response_empty_fixture,
)
from .test_mks_client_nnp_hr import NNP_HR_RESPONSE, get_nnp_xml_response_fixture


def wrap_response(response_data, status: str = "OK"):
    return {
        "content": json.loads(json.dumps(response_data, default=str)),
        "status": status,
    }


class HRTest(FlaskServerTestCase):
    app = app

    def _get_expected_private(self):
        return wrap_response(KVK_HR_EENMANSZAAK_RESPONSE)

    def _get_expected_commercial(self):
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
        self.assertEqual(response.json, self._get_expected_private())

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
        self.assertEqual(response.json, self._get_expected_commercial())

    @patch(
        "app.service.mks_client_hr._get_response_by_kvk_number",
        lambda kvk_number: get_xml_response_empty_fixture(),
    )
    def test_empty(self):
        response = self.get_secure("/brp/hr", profile_type=PROFILE_TYPE_COMMERCIAL)
        self.assertEqual(response.status_code, 200)
