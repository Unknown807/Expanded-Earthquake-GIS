import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))

from GisMain import GISMain
from TKPages import SettingsPage

import unittest
import unittest.mock as mock

class TestClassMethodCalls(unittest.TestCase):
    '''
    This tests methods of classes and just checks the arguments used.
    But it also tests that other functions were run as well
    '''

    def test_page_switch(self):
        _to = "SettingsPage"
        with mock.patch.object(GISMain, "show_frame") as mocked:
            mocked(_to)
            mocked.assert_called_with("SettingsPage")

    def test_refresh_earthquake_data(self):
        with mock.patch("TKPages.SettingsPage") as MockClass:
            instance = MockClass()
            instance.request_new_data()
            instance.request_new_data.assert_called()

if __name__ == "__main__":
    unittest.main(exit=False)
