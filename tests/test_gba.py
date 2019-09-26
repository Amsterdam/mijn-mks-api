from unittest import TestCase
import os

# ignoring E402: module level import not at top of file
os.environ['TMA_CERTIFICATE'] = 'cert content'  # noqa: E402
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'  # noqa: E402
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'  # noqa: E402
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'  # noqa: E402

from mks.model.gba import lookup_landen, lookup_gemeenten


class TestGba(TestCase):
    def test_landen_lookup(self):
        self.assertEqual(lookup_landen['6030'], 'Nederland')

    def test_gemeenten_lookup(self):
        self.assertEqual(lookup_gemeenten['0363'], 'Amsterdam')
