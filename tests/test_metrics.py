from tma_saml import FlaskServerTMATestCase

from mks.server import application


class HrBsnTest(FlaskServerTMATestCase):
    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)

    def test_get(self):
        response = self.client.get('/metrics')

        print(response.data.decode())
