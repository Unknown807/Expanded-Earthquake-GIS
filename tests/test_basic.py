import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))

from GisMain import GISMain

import unittest
import unittest.mock as mock

class TestMainMethodCalls(unittest.TestCase):
    '''
    This tests the methods of the root class to a small extent, such as whether the method
    was called and with which arguements
    '''

    def test_page_switch(self):
        _to = "SettingsPage"
        with mock.patch.object(GISMain, "show_frame") as mocked:
            mocked(_to)
            mocked.assert_called_with("SettingsPage")

    def test_modify_url(self):
        with mock.patch.object(GISMain, "modify_url") as mocked:
            mocked()
            mocked.assert_called()

    def test_call_reconnect(self):
        with mock.patch.object(GISMain, "call_reconnect") as mocked:
            mocked()
            mocked.assert_called()

    def test_call_display_info(self):
        with mock.patch.object(GISMain, "call_display_info") as mocked:
            mocked()
            mocked.assert_called()
    
    def test_on_close_window(self):
        open("current_data.json", "wb").close()
        open("current_image.png", "wb").close()
            
        GISMain.on_close_window(mock.Mock())
        self.assertFalse(os.path.isfile("current_data.json"))
        self.assertFalse(os.path.isfile("current_image.png"))

class TestSettingsPageMethodCalls(unittest.TestCase):
    '''
    This tests the methods of the settings page to a small extent, such as whether
    the method was called and with which arguments
    '''

    def test_refresh_earthquake_data(self):
        with mock.patch("SettingsPage.SettingsPage") as MockClass:
            instance = MockClass()
            instance.request_new_data()
            instance.request_new_data.assert_called()

class TestMapPageMethodCalls(unittest.TestCase):
    '''
    This tests the methods of the map page to a small extent, such as whether
    the method was called and with which arguments
    '''
    
    def test_reconnect_pick_event(self):
        with mock.patch("MapPage.MapPage") as MockClass:
            instance = MockClass()
            instance.reconnect_pick_event()
            instance.reconnect_pick_event.assert_called()

    def test_display_point_info(self):
        with mock.patch("MapPage.MapPage") as MockClass:
            instance = MockClass()
            instance.display_point_info()
            instance.display_point_info.assert_called()

if __name__ == "__main__":
    unittest.main(exit=False)
