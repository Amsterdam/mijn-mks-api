from unittest import TestCase
import os

os.environ['TMA_CERTIFICATE'] = 'cert content'
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'

# ignoring E402: module level import not at top of file
from mks.model.gba import lookup_landen, lookup_gemeenten, lookup_prsidb_soort_code, \
    lookup_nationaliteiten  # noqa: E402


class TestGba(TestCase):
    def test_landen_lookup(self):
        self.assertEqual(lookup_landen['6030'], 'Nederland')

    def test_gemeenten_lookup(self):
        self.assertEqual(lookup_gemeenten['0363'], 'Amsterdam')

    def test_prsidb_soort_code_lookup(self):
        self.assertEqual(lookup_prsidb_soort_code[1], 'paspoort')

    def test_nationaliteiten_lookup(self):
        self.assertEqual(lookup_nationaliteiten['0336'], 'Syrische')
