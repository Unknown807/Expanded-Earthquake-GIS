
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))

import TKPages

import unittest
import unittest.mock as mock

def mocked_request_get(*args, **kwargs):
    '''
    the side_effect function for patching the requests.get method used in the TKPages module
    used by the SettingsPage class
    '''
    class MockResponse:
        '''
        Imitates a response from the GeoJson API for valid and invalid requests/responses
        '''
        def __init__(self, json_data, status_code, ok):
            self.json_data = json_data
            self.status_code = status_code
            self.ok = ok
        
        def json(self):
            return self.json_data
    
    if args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1":
        return MockResponse('{"type":"FeatureCollection","metadata":{"generated":1557156255000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":1,"offset":1,"count":1},"features":[{"type":"Feature","properties":{"mag":1.7,"place":"75km S of Kobuk, Alaska","time":1557153499064,"updated":1557153801598,"tz":-540,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ak0195sm9zcz","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ak0195sm9zcz&format=geojson","felt":null,"cdi":null,"mmi":null,"alert":null,"status":"automatic","tsunami":0,"sig":44,"net":"ak","code":"0195sm9zcz","ids":",ak0195sm9zcz,","sources":",ak,","types":",geoserve,origin,","nst":null,"dmin":null,"rms":0.95,"gap":null,"magType":"ml","type":"earthquake","title":"M 1.7 - 75km S of Kobuk, Alaska"},"geometry":{"type":"Point","coordinates":[-157.2,66.2404,0.1]},"id":"ak0195sm9zcz"}]}', 200, True)
    elif args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson":
        return MockResponse(None, 400, False)
    elif args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson&limit=100":
        raise TKPages.requests.exceptions.ConnectionError

    return MockResponse(None, 400, False)

class TestRefreshMethod(unittest.TestCase):
    '''
    This tests the refresh method of the SettingsPage class and sees whether the data validation
    is correct. It also tests calls to the external GeoJson API.
    '''
    
    def setUp(self):
        self.settings_page = TKPages.SettingsPage(None, None)
        self.jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))+r"\current_data.json"

    def test_request_get(self):
        with mock.patch("TKPages.requests.get", side_effect=mocked_request_get) as mocked_get:
            long_url  = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1"
            short_url = "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson"

            real_call = self.settings_page.request_new_data(long_url)

            #check a valid request and good response
            mocked_get.assert_called_once_with(long_url)
            self.assertEqual(real_call.ok, True, "Should be True")
            self.assertEqual(real_call.status_code, 200, "Should be 200")
            self.assertEqual(real_call.json_data, '{"type":"FeatureCollection","metadata":{"generated":1557156255000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":1,"offset":1,"count":1},"features":[{"type":"Feature","properties":{"mag":1.7,"place":"75km S of Kobuk, Alaska","time":1557153499064,"updated":1557153801598,"tz":-540,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ak0195sm9zcz","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ak0195sm9zcz&format=geojson","felt":null,"cdi":null,"mmi":null,"alert":null,"status":"automatic","tsunami":0,"sig":44,"net":"ak","code":"0195sm9zcz","ids":",ak0195sm9zcz,","sources":",ak,","types":",geoserve,origin,","nst":null,"dmin":null,"rms":0.95,"gap":null,"magType":"ml","type":"earthquake","title":"M 1.7 - 75km S of Kobuk, Alaska"},"geometry":{"type":"Point","coordinates":[-157.2,66.2404,0.1]},"id":"ak0195sm9zcz"}]}')
            self.assertTrue(os.path.isfile(self.jsonpath), True)
            
            #check a valid request and bad response
            real_call = self.settings_page.request_new_data(short_url)
            mocked_get.assert_called_with(short_url)
            self.assertEqual(real_call.ok, False, "Should be False")
            self.assertEqual(real_call.status_code, 400, "Should be 400")
            self.assertIsNone(real_call.json_data, "Should be None")
            os.remove(self.jsonpath)

            #check a valid request with connectivity issues
            real_call = self.settings_page.request_new_data(short_url+"&limit=100")
            self.assertEqual(real_call, "Bad Connection", "Should be a return of 'Bad Connection'")

    def test_data_validation(self):
        #check if validation works with default values
        real_call = self.settings_page.validate_data()
        self.assertIsNone(real_call, "Should be None")
        os.remove(self.jsonpath)

        #check if any value for date or time is missing
        self.settings_page.startdate_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Date", "Should be a return of 'Bad Date'")

        self.settings_page.starttime_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Time", "Should be a return of 'Bad Time'")

        self.settings_page.starttime_counter.setentry("12:45:00")
        self.settings_page.startdate_counter.setentry("2018-05-06")

        #check if any value is missing for rectangle search
        self.settings_page.minlat_counter.clear()
        self.settings_page.minlong_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Rectangle Options", "Should be a return of 'Bad Rectangle Options'")

        #check if min latitude is greater/equal to max latitude and for longitude as well
        self.settings_page.minlat_counter.setentry("90")
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Rectangle Options", "Should be a return of 'Bad Rectangle Options'")
        self.settings_page.minlat_counter.setentry("-90")

        self.settings_page.minlong_counter.setentry("180")
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Rectangle Options", "Should be a return of 'Bad Rectangle Options'")
        self.settings_page.minlong_counter.setentry("-180")

        #check if any value is missing for circle search    
        self.settings_page.circ_rect_search_menu.setvalue("Circle")
        self.settings_page.maxradius_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Circle Options", "Should be a return of 'Bad Circle Options'")
        self.settings_page.maxradius_counter.setentry("180")

        #check if any value is missing for magnitude
        self.settings_page.minmag_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Min/Max Magnitudes", "Should be a return of 'Bad Min/Max Magnitudes'")

        #check if min magnitude is greater/equal to max magnitude
        self.settings_page.minmag_counter.setentry("2")
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Min/Max Magnitudes", "Should be a return of 'Bad Min/Max Magnitudes'")
        self.settings_page.minmag_counter.setentry("1")

        #check if any value is missing for depth
        self.settings_page.mindepth_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Min/Max Depths", "Should be a return of 'Bad Min/Max Depths'")

        #check if min depth is greater/equal to max depth
        self.settings_page.mindepth_counter.setentry("1000")
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Min/Max Depths", "Should be a return of 'Bad Min/Max Depths'")
        self.settings_page.mindepth_counter.setentry("-100")

        #check if limit value is missing
        self.settings_page.limit_counter.clear()
        real_call = self.settings_page.validate_data()
        self.assertEqual(real_call, "Bad Limit", "Should be a return of 'Bad Limit'")
        

if __name__ == "__main__":
    unittest.main(exit=False)