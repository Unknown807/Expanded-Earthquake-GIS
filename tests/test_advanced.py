
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))

import PointInfoPage
import SettingsPage
import MapPage
import GisMain

import unittest
import unittest.mock as mock

class MockPointObj:
    '''
    This class is used to imitate a MapPoint object, it has default values for lack of any, but any
    property of the earthquake event can be changed. This class is used for the configure_labels method
    of the PointInfoPage class
    '''
    def __init__(self, *args, **kwargs):
        self.place = "12km NNE of Thousand Palms, CA" if not kwargs.get("place", False) else kwargs["place"]
        self.time = "2019-08-12T15:18:03.430000" if not kwargs.get("time", False) else kwargs["time"]
        self.gap = "82" if not kwargs.get("gap", False) else kwargs["gap"]
        self.dmin = "0.04146" if not kwargs.get("dmin", False) else kwargs["dmin"]
        self.status = "automatic" if not kwargs.get("status", False) else kwargs["status"]
        self.alert = "null" if not kwargs.get("alert", False) else kwargs["alert"]
        self.felt = "14" if not kwargs.get("felt", False) else kwargs["felt"]
        self.magnitude = "1.22" if not kwargs.get("magnitude", False) else kwargs["magnitude"]
        self.type_ = "earthquake" if not kwargs.get("type_", False) else kwargs["type_"]
        self.magtype = "ml" if not kwargs.get("magtype", False) else kwargs["magtype"]
        self.sig = "23" if not kwargs.get("sig", False) else kwargs["sig"]
        self.tsunami = "0" if not kwargs.get("tsunami", False) else kwargs["tsunami"]
        self.mmi = "null" if not kwargs.get("mmi", False) else kwargs["mmi"]
        self.cdi = "null" if not kwargs.get("cdi", False) else kwargs["cdi"]
        self.title = "M 1.2 - 12km NNE of Thousand Palms, CA" if not kwargs.get("title", False) else kwargs["title"]

class MockResponse:
    '''
    Imitates a response from the Earthquake Catalog API + Wiki API for valid and invalid requests/responses
    '''
    def __init__(self, json_data, status_code, ok):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = ok
    
    def json(self):
        return self.json_data

class MockTextNode:
    '''
    Imitates BS4 text nodes from parsed data, works for <a> and <p> html tags only
    '''
    def __init__(self, data, index):
        self.data = data
        self.index = index

    def getText(self):
        '''
        the actual getText function returns a list of html tags
        '''
        return self.data[self.index]

    def get_text(self):
        '''
        the actual get_text function returns all the non-html substrings in a string
        '''
        return self.data

    def __contains__(self, item):
        return False
        

class MockBS4:
    '''
    Imitates the BeautifulSoup class for the various functions used. it mocks the html
    parsing process
    '''
    def __init__(self, data, **kwargs):
        self.data = data
    
    def find(self, item):
        '''
        method for creating a text node for the right html tag
        '''
        if item == "p":
            return MockTextNode(self.data, 0)
        elif item == "a":
            return MockTextNode(self.data, 1)
    
    def find_all(self, item):
        return self.data
        
WIKI_GET_COUNT = 0
def mocked_wiki_text_url_request(*args, **kwargs):
    global WIKI_GET_COUNT
    '''
    the side_effect function for patching the PointInfoPage.wiki_text_url_request method
    used by the PointInfoPage class

    This function is quite self-explanatory as it imitates the process for a successful api response
    after 1 request, 2 requests, 3 requests or no valid response (input for requests varying)
    '''

    if args[0] == "Hongtu, China": #2 good responses, after one redirect
        return ["Redirect to:", "Redirect to Hongtu, China"]
    elif args[0] == "Redirect to Hongtu, China":
        return (MockTextNode("P1 about Hongtu, China", None), 
            MockTextNode("P2 about Hongtu, China", None))
    
    elif args[0] == "Salamanca, Chile": #1 bad response, 2 good responses, with a different type of redirect 
        return False
    elif args[0] == "Salamanca":
        return ["commonly refers to:", "Redirect to Salamanca"]
    elif args[0] == "Redirect to Salamanca":
        return (MockTextNode("P1 about Salamanca", None), 
            MockTextNode("P2 about salamanca", None))

    elif args[0] == "Ridgecrest, CA": #2 bad responses, 2 good responses, with a different type of redirect
        return False
    elif args[0] == "Ridgecrest":
        return False
    elif args[0] == " CA" and WIKI_GET_COUNT == 0:
        WIKI_GET_COUNT += 1
        return ["may refer to:", "Redirect to California"]
    elif args[0] == " CA" and WIKI_GET_COUNT == 1:
        return (MockTextNode("P1 about California", None),
            MockTextNode("P2 about California", None))

    elif args[0] == "Esso, Russia": #1 good response no redirects
        return (MockTextNode("P1 about Esso, Russia", None),
            MockTextNode("P2 about Esso, Russia", None))
    
    elif args[0] == "London, England": #3 bad responses, no successful response
        return False
    elif args[0] == "London":
        return False
    elif args[0] == " England":
        return False

WIKI_TEXT_COUNT = True
def mocked_get_wiki_text(*args, **kwargs):
    global WIKI_TEXT_COUNT
    '''
    the side_effect function for patching the PointInfoPage.get_wiki_text method used in the
    PointInfoPage module, used by the PointInfoPage class. The function normally returns
    either false or a string.
    '''
    
    if WIKI_TEXT_COUNT:
        WIKI_TEXT_COUNT = not WIKI_TEXT_COUNT
        return "wiki info about topic"
    elif not WIKI_TEXT_COUNT:
        return False

WIKI_IMG_COUNT = 0
def mocked_get_image_url(*args, **kwargs):
    global WIKI_IMG_COUNT
    '''
    the side_effect function for patching the PointInfoPage.wiki_image_url_request method used
    in the PointInfoPage module, used by the PointInfoPage class. The function normally returns
    either false or an image url string

    Note - where this function is used as a side_effect, multiple other functions have also been patched and almost work
    together to test different scenarios, the WIKI_IMG_COUNT variable is just used for incrementing onto the next test
    '''
    
    if WIKI_IMG_COUNT == 0: #no image url found
        WIKI_IMG_COUNT += 1 
        return False
    elif WIKI_IMG_COUNT == 1:
        WIKI_IMG_COUNT += 1
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Tonga.svg/300px-Flag_of_Tonga.svg.png"
    elif WIKI_IMG_COUNT == 2:
        WIKI_IMG_COUNT += 1
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/300px-Flag_of_Fiji.svg.png"
    elif WIKI_IMG_COUNT == 3:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/300px-Flag_of_Thailand.svg.png"

def mocked_wiki_request_get_2(*args, **kwargs):
    '''
    the side_effect function for patching the requests.get method used in the PointInfoPage module
    used by the PointInfoPoint class.
    '''
    
    if args[0] == "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Tonga.svg/300px-Flag_of_Tonga.svg.png":
        return mock.MagicMock(raw=bytes("filler", encoding="utf-8")) #valid image data is returned
    elif args[0] == "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/300px-Flag_of_Fiji.svg.png":
        return MockResponse(None, 400, False) #no image data returned with successful request
    elif args[0] == "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/300px-Flag_of_Thailand.svg.png":
        raise PointInfoPage.requests.exceptions.ConnectionError #connectivity issue with successful request

def mocked_request_get(*args, **kwargs):
    '''
    the side_effect function for patching the requests.get method used in the SettingsPage module
    used by the SettingsPage class
    '''
    
    #successful request and response with GeoJson formatted data
    if args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1":
        return MockResponse({"type":"FeatureCollection","metadata":{"generated":1557156255000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":1,"offset":1,"count":1},"features":[{"type":"Feature","properties":{"mag":1.7,"place":"75km S of Kobuk, Alaska","time":1557153499064,"updated":1557153801598,"tz":-540,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ak0195sm9zcz","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ak0195sm9zcz&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":44,"net":"ak","code":"0195sm9zcz","ids":",ak0195sm9zcz,","sources":",ak,","types":",geoserve,origin,","nst":None,"dmin":None,"rms":0.95,"gap":None,"magType":"ml","type":"earthquake","title":"M 1.7 - 75km S of Kobuk, Alaska"},"geometry":{"type":"Point","coordinates":[-157.2,66.2404,0.1]},"id":"ak0195sm9zcz"}]}, 200, True)
    elif args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson":
        return MockResponse(None, 400, False) #invalid response, possibly server-side error
    elif args[0] == "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson&limit=100":
        raise SettingsPage.requests.exceptions.ConnectionError #connectivity issue, only client-side

    return MockResponse(None, 400, False) #unsuccessful request, unsuccessful response

def mocked_wiki_request_get(*args, **kwargs):
    '''
    the side_effect function for patching the requests.get method used in the PointInfoPage module
    used by the PointInfoPage class. the image url will be returned inside a json structure.
    '''
    
    #in order:
    #successful response with image url
    #successful response with missing article
    #successful response with missing image url
    #unsuccessful response
    #connectivity issue

    if args[0] == "https://en.wikipedia.org/w/api.php?action=query&titles=Thailand&prop=pageimages&format=json&pithumbsize=300":
        return MockResponse({"batchcomplete":"","query":{"pages":{"30128":{"pageid":30128,"ns":0,"title":"Thailand","thumbnail":{"source":"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/300px-Flag_of_Thailand.svg.png","width":300,"height":200},"pageimage":"Flag_of_Thailand.svg"}}}}, 200, True)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=query&titles=asdfasgas&prop=pageimages&format=json&pithumbsize=300":
        return MockResponse({"batchcomplete":"","query":{"normalized":[{"from":"asdfasgas","to":"Asdfasgas"}],"pages":{"-1":{"ns":0,"title":"Asdfasgas","missing":""}}}}, 200, True)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=query&titles=Nothing&prop=pageimages&format=json&pithumbsize=300":
        return MockResponse({"batchcomplete":"","query":{"pages":{"72197":{"pageid":72197,"ns":0,"title":"Nothing"}}}}, 200, True)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=query&titles=China&prop=pageimages&format=json&pithumbsize=300":
        return MockResponse(None, 400, False)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=query&titles=Serbia&prop=pageimages&format=json&pithumbsize=300":
        raise PointInfoPage.requests.exceptions.ConnectionError

def mocked_wiki_request_get_3(*args, **kwargs):
    '''
    the side_effect function for patching the requests.get method used in the PointInfoPage module
    used by the PointInfoPage class. sends a request for text information to the wikipedia API, the returned
    text will need to be parsed to get rid of the unecessary html tags and appendices figure (e.g '[23]')
    '''
    
    #in order:
    #successful response with text
    #unsuccessful response default text
    #successful response but invalid article
    #connectivity issue
    
    if args[0] == "https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page=Nothing":
        return MockResponse({"parse":{"title":"Nothing","pageid":72197,"text":{"*":"<div class=\"mw-parser-output\"><p class=\"mw-empty-elt\">\n</p>\n<div role=\"note\" class=\"hatnote navigation-not-searchable\">For other uses, see <a href=\"/wiki/Nothing_(disambiguation)\" class=\"mw-disambig\" title=\"Nothing (disambiguation)\">Nothing (disambiguation)</a>.</div><p>\n\"<b>Nothing</b>\", used as a pronoun subject, denotes the absence of a <a href=\"/wiki/Something_(concept)\" title=\"Something (concept)\">something</a> or particular thing that one might expect or desire to be present (\"We found nothing,\" \"Nothing was there\") or the inactivity of a thing or things that are usually or could be active (\"Nothing moved,\" \"Nothing happened\").  As a predicate or complement \"nothing\" denotes the absence of meaning, value, worth, relevance, standing, or <a href=\"/wiki/Importance\" title=\"Importance\">significance</a> (\"It is a tale/ Told by an idiot, full of sound and fury,/ Signifying nothing\"; \"The affair meant nothing\"; \"I'm nothing in their eyes\").<sup id=\"cite_ref-MWD_1-0\" class=\"reference\"><a href=\"#cite_note-MWD-1\">&#91;1&#93;</a></sup>  \"<b>Nothingness</b>\" is a philosophical term that denotes the general state of <a href=\"/wiki/Nonexistence\" class=\"mw-redirect\" title=\"Nonexistence\">nonexistence</a>, sometimes reified as a domain or dimension into which things pass when they cease to exist or out of which they may come to exist, e.g., God is understood to have created the universe <i>ex nihilo</i>, \"out of nothing.\"<sup id=\"cite_ref-MWD_1-1\" class=\"reference\"><a href=\"#cite_note-MWD-1\">&#91;1&#93;</a></sup><sup id=\"cite_ref-2\" class=\"reference\"><a href=\"#cite_note-2\">&#91;2&#93;</a></sup></p><div class=\"mw-references-wrap\"><ol class=\"references\">\n<li id=\"cite_note-MWD-1\"><span class=\"mw-cite-backlink\">^ <a href=\"#cite_ref-MWD_1-0\"><sup><i><b>a</b></i></sup></a> <a href=\"#cite_ref-MWD_1-1\"><sup><i><b>b</b></i></sup></a></span> <span class=\"reference-text\"><a rel=\"nofollow\" class=\"external text\" href=\"http://www.merriam-webster.com/dictionary/nothing\">\"Nothing\"</a>, <i>Merriam-Webster Dictionary</i></span>\n</li>\n<li id=\"cite_note-2\"><span class=\"mw-cite-backlink\"><b><a href=\"#cite_ref-2\">^</a></b></span> <span class=\"reference-text\">definition of suffix \"-ness\" - <i>\"the state of being\"</i>, Yourdictionary.com, [www.yourdictionary.com/ness-suffix]</span>\n</li>\n</ol></div>\n<!-- \nNewPP limit report\nParsed by mw1345\nCached time: 20190812194235\nCache expiry: 2592000\nDynamic content: false\nComplications: []\nCPU time usage: 0.076 seconds\nReal time usage: 0.101 seconds\nPreprocessor visited node count: 39/1000000\nPreprocessor generated node count: 0/1500000\nPost\u2010expand include size: 510/2097152 bytes\nTemplate argument size: 0/2097152 bytes\nHighest expansion depth: 3/40\nExpensive parser function count: 2/500\nUnstrip recursion depth: 0/20\nUnstrip post\u2010expand size: 269/5000000 bytes\nNumber of Wikibase entities loaded: 0/400\nLua time usage: 0.041/10.000 seconds\nLua memory usage: 806 KB/50 MB\n-->\n<!--\nTransclusion expansion time report (%,ms,calls,template)\n100.00%   87.980      1 -total\n 84.90%   74.694      1 Template:Pp-vandalism\n 14.79%   13.013      1 Template:Other_uses\n-->\n</div>"}}}, 200, True)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page=Thailand":
        return MockResponse(None, 400, False)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page=badrequest":
        return MockResponse({"error":{"code":"missingtitle","info":"The page you specified doesn't exist.","*":"See https://en.wikipedia.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/mailman/listinfo/mediawiki-api-announce&gt; for notice of API deprecations and breaking changes."},"servedby":"mw1340"}, 200, True)
    elif args[0] == "https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page=China":
        raise PointInfoPage.requests.exceptions.ConnectionError

class TestPointInfoPage(unittest.TestCase):
    '''
    This tests the various methods and functionalities of the PointInfoPage
    class and sees whether labels are being configured correctly, along with
    the varying calls and responses from the wikipedia API for individual
    earthquake events
    '''

    def setUp(self):
        self.PI_page = PointInfoPage.PointInfoPage(None, mock.Mock())
        self.imgpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))+r"\current_image.png"

    def tearDown(self):
        pass

    def test_configure_labels(self):
        #checks if the labels will have the correct strings configured
        PI_obj = MockPointObj()
        real_call = self.PI_page.configure_labels(PI_obj)
        
        config_strings = [f"Place: {PI_obj.place}", f"Time: {PI_obj.time}", 
            f"Gap: {PI_obj.gap}", f"Dmin: {PI_obj.dmin}",
            f"Status: {PI_obj.status}", f"Alert: {PI_obj.alert}", 
            f"Felt: {PI_obj.felt}", f"Magnitude: {PI_obj.magnitude}",
            f"Type: {PI_obj.type_}", f"Magnitude Type: {PI_obj.magtype}", 
            f"Significance: {PI_obj.sig}", f"Tsunami: {PI_obj.tsunami}", 
            f"MMI: {PI_obj.mmi}", f"CDI: {PI_obj.cdi}"]
        
        label_strings = [self.PI_page.place_label.cget("text"),
            self.PI_page.time_label.cget("text"),
            self.PI_page.gap_label.cget("text"),
            self.PI_page.dmin_label.cget("text"),
            self.PI_page.status_label.cget("text"),
            self.PI_page.alert_label.cget("text"),
            self.PI_page.felt_label.cget("text"),
            self.PI_page.mag_label.cget("text"),
            self.PI_page.type_label.cget("text"),
            self.PI_page.magtype_label.cget("text"),
            self.PI_page.sig_label.cget("text"),
            self.PI_page.tsunami_label.cget("text"),
            self.PI_page.mmi_label.cget("text"),
            self.PI_page.cdi_label.cget("text")]

        for string, label in zip(config_strings, label_strings):
            self.assertEqual(string, label)

    def test_configure_scrolledtext(self):
        with mock.patch("PointInfoPage.PointInfoPage.get_wiki_text", side_effect=mocked_get_wiki_text) as mocked_get:
            #check whether text was found and the scrolled text widget configured properly
            real_call = self.PI_page.configure_scrolledtext()
            text_value = self.PI_page.wiki_scrolledtext.component("text").get("1.0", "end")
            self.assertEqual(text_value, "wiki info about topic\n", "Should be equal to 'wiki info about topic' string")

            #check whether text was not found and the scrolled text widget configured properly
            real_call = self.PI_page.configure_scrolledtext()
            text_value = self.PI_page.wiki_scrolledtext.component("text").get("1.0", "end")
            self.assertEqual(text_value, "No Information Found\n", "Should be equal to 'No Information Found' string")

    def test_configure_event_photo(self):
        with mock.patch("PointInfoPage.PointInfoPage.get_wiki_image", side_effect=lambda: False) as mocked_get:
            #check whether image holder widget was configured properly
            real_call = self.PI_page.configure_event_photo()
            self.assertEqual(self.PI_page.wiki_photo_label.image, self.PI_page.wiki_photo)

    def test_wiki_image_url_request(self):
        with mock.patch("PointInfoPage.requests.get", side_effect=mocked_wiki_request_get) as mocked_get:
            #check a valid request and valid response - with image
            self.PI_page.wiki_image_data = "Thailand"
            real_call = self.PI_page.wiki_image_url_request()
            mocked_get.assert_called_once()
            self.assertEqual(real_call, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/300px-Flag_of_Thailand.svg.png")
            
            #check a invalid request and valid response
            self.PI_page.wiki_image_data = "asdfasgas"
            real_call = self.PI_page.wiki_image_url_request()
            mocked_get.assert_called()
            self.assertFalse(real_call)

            #check a valid request and valid response - but no image
            self.PI_page.wiki_image_data = "Nothing"
            real_call = self.PI_page.wiki_image_url_request()
            mocked_get.assert_called()
            self.assertFalse(real_call)

            #check a valid request and invalid response
            self.PI_page.wiki_image_data = "China"
            real_call = self.PI_page.wiki_image_url_request()
            mocked_get.assert_called()
            self.assertFalse(real_call)
            
            #check a valid request with connectivity issues
            self.PI_page.wiki_image_data = "Serbia"
            real_call = self.PI_page.wiki_image_url_request()
            self.assertFalse(real_call)
    
    @mock.patch("PointInfoPage.PointInfoPage.wiki_image_url_request", side_effect=mocked_get_image_url)
    @mock.patch("PointInfoPage.requests.get", side_effect=mocked_wiki_request_get_2)
    @mock.patch("PointInfoPage.shutil.copyfileobj", side_effect=mock.MagicMock())
    def test_get_wiki_image(self, mocked_img_url, mocked_get, mocked_shutil):
        #check that no image was received from the wiki_image_url_request() method
        real_call = self.PI_page.get_wiki_image()
        self.assertFalse(real_call)
        
        #check a valid request and a valid response
        real_call = self.PI_page.get_wiki_image()
        self.assertTrue(real_call)

        #check a valid request and a invalid response
        real_call = self.PI_page.get_wiki_image()
        self.assertFalse(real_call)

        #check a valid request with connectivity issues
        real_call = self.PI_page.get_wiki_image()
        self.assertFalse(real_call)
    
    def test_wiki_text_url_request(self):
        with mock.patch("PointInfoPage.requests.get", side_effect=mocked_wiki_request_get_3) as mocked_get:
            #check a valid request and a valid response
            real_call = self.PI_page.wiki_text_url_request("Nothing")
            self.assertTrue(bool(real_call))
            self.assertIsInstance(real_call, str) #done as string is too long
            
            #check a valid request and an invalid response
            real_call = self.PI_page.wiki_text_url_request("Thailand")
            self.assertFalse(real_call)

            #check an invalid request and a valid response
            real_call = self.PI_page.wiki_text_url_request("badrequest")
            self.assertFalse(real_call)
        
            #check a valid request with connectivity issues
            real_call = self.PI_page.wiki_text_url_request("China")
            self.assertFalse(real_call)

    @mock.patch("PointInfoPage.PointInfoPage.wiki_text_url_request", side_effect=mocked_wiki_text_url_request)
    @mock.patch("PointInfoPage.BS4", side_effect=MockBS4) 
    def test_get_wiki_text(self, mocked_BS4_class, mocked_request):
        #Check if place does not contain any digits
        self.PI_page.place_label.configure(text="No Digits")
        real_call = self.PI_page.get_wiki_text()
        self.assertFalse(self.PI_page.wiki_image_data)
        self.assertFalse(real_call)

        #Check first response returns true with - "Redirect to:" included
        self.PI_page.place_label.configure(text="Place: 95km NNW of Hongtu, China")
        real_call = self.PI_page.get_wiki_text()
        self.assertTrue(real_call)
        self.assertIsInstance(real_call, str)

        #Check second response returns true with - "commonly refers to:" and or "may also refer to:" included
        self.PI_page.place_label.configure(text="Place: 53km EES of Salamanca, Chile")
        real_call = self.PI_page.get_wiki_text()
        self.assertTrue(real_call)
        self.assertIsInstance(real_call, str)

        #Check third response returns true with - "may refer to" included
        self.PI_page.place_label.configure(text="Place: 54km NNW of Ridgecrest, CA")
        real_call = self.PI_page.get_wiki_text()
        self.assertTrue(real_call)
        self.assertIsInstance(real_call, str)

        #Check any response returns true with no additional search
        self.PI_page.place_label.configure(text="Place: 65km NNW of Esso, Russia")
        real_call = self.PI_page.get_wiki_text()
        self.assertTrue(real_call)
        self.assertIsInstance(real_call, str)        

        #Check all responses return False
        self.PI_page.place_label.configure(text="Place: 34km EES of London, England")
        real_call = self.PI_page.get_wiki_text()
        self.assertFalse(self.PI_page.wiki_image_data)
        self.assertFalse(real_call)

class TestMapPage(unittest.TestCase):
    '''
    This tests the various methods and functionalities of the MapPage class
    and sees that interactions between the map and mappoint objects are 
    working correctly
    '''

    def setUp(self):
        self.map_page = MapPage.MapPage(None, mock.Mock())
        self.jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))+r"\current_data.json"

    def tearDown(self):
        pass

    def test_refresh_plot(self):
        #Checks whether the same data has already been plotted, if yes, then it should not plot it again
        self.map_page.local_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=3"
        self.map_page.controller.current_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=3"
        real_call = self.map_page.refresh_plot(None)
        self.assertEqual(real_call, "Same Request", "Should be a return of 'Same Request'")

        #Checks whether there is different data to be plotted, if yes, then it plots it
        self.map_page.local_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=5"
        with open(self.jsonpath, "w") as out_file:
            json.dump({"type":"FeatureCollection","metadata":{"generated":1565616904000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=5","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":5,"offset":1,"count":5},"features":[{"type":"Feature","properties":{"mag":0.56000000000000005,"place":"7km WNW of The Geysers, CA","time":1565616767480,"updated":1565616862340,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/nc73248286","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=nc73248286&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":5,"net":"nc","code":"73248286","ids":",nc73248286,","sources":",nc,","types":",geoserve,nearby-cities,origin,phase-data,","nst":8,"dmin":0.0016639999999999999,"rms":0.040000000000000001,"gap":93,"magType":"md","type":"earthquake","title":"M 0.6 - 7km WNW of The Geysers, CA"},"geometry":{"type":"Point","coordinates":[-122.8281631,38.810333300000003,2.0299999999999998]},"id":"nc73248286"},
            {"type":"Feature","properties":{"mag":0.90000000000000002,"place":"7km NW of San Jacinto, CA","time":1565616601960,"updated":1565616828359,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959312","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959312&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":12,"net":"ci","code":"38959312","ids":",ci38959312,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":13,"dmin":0.090730000000000005,"rms":0.23000000000000001,"gap":102,"magType":"ml","type":"earthquake","title":"M 0.9 - 7km NW of San Jacinto, CA"},"geometry":{"type":"Point","coordinates":[-117.00633329999999,33.832999999999998,23.300000000000001]},"id":"ci38959312"},
            {"type":"Feature","properties":{"mag":1.24,"place":"22km ESE of Little Lake, CA","time":1565616447250,"updated":1565616672288,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959304","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959304&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":24,"net":"ci","code":"38959304","ids":",ci38959304,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":25,"dmin":0.085470000000000004,"rms":0.12,"gap":81,"magType":"ml","type":"earthquake","title":"M 1.2 - 22km ESE of Little Lake, CA"},"geometry":{"type":"Point","coordinates":[-117.684,35.8645,8.2400000000000002]},"id":"ci38959304"},
            {"type":"Feature","properties":{"mag":1.5800000000000001,"place":"16km SSW of Searles Valley, CA","time":1565615959780,"updated":1565616624630,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959280","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959280&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":38,"net":"ci","code":"38959280","ids":",ci38959280,","sources":",ci,","types":",focal-mechanism,geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":24,"dmin":0.039570000000000001,"rms":0.20999999999999999,"gap":55,"magType":"ml","type":"earthquake","title":"M 1.6 - 16km SSW of Searles Valley, CA"},"geometry":{"type":"Point","coordinates":[-117.47033329999999,35.634833299999997,2.4700000000000002]},"id":"ci38959280"},
            {"type":"Feature","properties":{"mag":0.56999999999999995,"place":"22km ESE of Little Lake, CA","time":1565615877760,"updated":1565616104491,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959272","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959272&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":5,"net":"ci","code":"38959272","ids":",ci38959272,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":13,"dmin":0.080879999999999994,"rms":0.089999999999999997,"gap":86,"magType":"ml","type":"earthquake","title":"M 0.6 - 22km ESE of Little Lake, CA"},"geometry":{"type":"Point","coordinates":[-117.6773333,35.864166699999998,7.29]},"id":"ci38959272"}],"bbox":[-122.8281631,33.833,2.03,-117.0063333,38.8103333,23.3]}, out_file)
        real_call = self.map_page.refresh_plot(None)
        self.assertIsNone(real_call, "Should be a return of None")

        #Check whether the local_url is now equal to the controller url
        self.assertEqual(self.map_page.controller.current_url, self.map_page.local_url, "Both urls should be equal after successful function call")

    def test_plot_points(self):
        #Here the file data will contains 5 new points to plot
        json_data = {"type":"FeatureCollection","metadata":{"generated":1565616904000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=5","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":5,"offset":1,"count":5},"features":[{"type":"Feature","properties":{"mag":0.56000000000000005,"place":"7km WNW of The Geysers, CA","time":1565616767480,"updated":1565616862340,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/nc73248286","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=nc73248286&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":5,"net":"nc","code":"73248286","ids":",nc73248286,","sources":",nc,","types":",geoserve,nearby-cities,origin,phase-data,","nst":8,"dmin":0.0016639999999999999,"rms":0.040000000000000001,"gap":93,"magType":"md","type":"earthquake","title":"M 0.6 - 7km WNW of The Geysers, CA"},"geometry":{"type":"Point","coordinates":[-122.8281631,38.810333300000003,2.0299999999999998]},"id":"nc73248286"},
            {"type":"Feature","properties":{"mag":0.90000000000000002,"place":"7km NW of San Jacinto, CA","time":1565616601960,"updated":1565616828359,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959312","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959312&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":12,"net":"ci","code":"38959312","ids":",ci38959312,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":13,"dmin":0.090730000000000005,"rms":0.23000000000000001,"gap":102,"magType":"ml","type":"earthquake","title":"M 0.9 - 7km NW of San Jacinto, CA"},"geometry":{"type":"Point","coordinates":[-117.00633329999999,33.832999999999998,23.300000000000001]},"id":"ci38959312"},
            {"type":"Feature","properties":{"mag":1.24,"place":"22km ESE of Little Lake, CA","time":1565616447250,"updated":1565616672288,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959304","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959304&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":24,"net":"ci","code":"38959304","ids":",ci38959304,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":25,"dmin":0.085470000000000004,"rms":0.12,"gap":81,"magType":"ml","type":"earthquake","title":"M 1.2 - 22km ESE of Little Lake, CA"},"geometry":{"type":"Point","coordinates":[-117.684,35.8645,8.2400000000000002]},"id":"ci38959304"},
            {"type":"Feature","properties":{"mag":1.5800000000000001,"place":"16km SSW of Searles Valley, CA","time":1565615959780,"updated":1565616624630,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959280","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959280&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":38,"net":"ci","code":"38959280","ids":",ci38959280,","sources":",ci,","types":",focal-mechanism,geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":24,"dmin":0.039570000000000001,"rms":0.20999999999999999,"gap":55,"magType":"ml","type":"earthquake","title":"M 1.6 - 16km SSW of Searles Valley, CA"},"geometry":{"type":"Point","coordinates":[-117.47033329999999,35.634833299999997,2.4700000000000002]},"id":"ci38959280"},
            {"type":"Feature","properties":{"mag":0.56999999999999995,"place":"22km ESE of Little Lake, CA","time":1565615877760,"updated":1565616104491,"tz":-480,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ci38959272","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ci38959272&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":5,"net":"ci","code":"38959272","ids":",ci38959272,","sources":",ci,","types":",geoserve,nearby-cities,origin,phase-data,scitech-link,","nst":13,"dmin":0.080879999999999994,"rms":0.089999999999999997,"gap":86,"magType":"ml","type":"earthquake","title":"M 0.6 - 22km ESE of Little Lake, CA"},"geometry":{"type":"Point","coordinates":[-117.6773333,35.864166699999998,7.29]},"id":"ci38959272"}],"bbox":[-122.8281631,33.833,2.03,-117.0063333,38.8103333,23.3]}
        #checks whether all new points have been successfully plotted
        real_call = self.map_page.plot_points(json_data)
        self.assertTrue(self.map_page.map_figure.get_axes())
        self.assertTrue(self.map_page.map_axes.lines)
        self.assertEqual(len(self.map_page.map_axes.lines), 5)

class TestSettingsPage(unittest.TestCase):
    '''
    This tests the various methods and functionalities of the SettingsPage class 
    and sees whether the data validation is correct as well as test calls to the external Earthquake Catalog API
    and the possible responses
    '''
    
    def setUp(self):
        self.settings_page = SettingsPage.SettingsPage(None, mock.Mock())
        self.jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))+r"\current_data.json"

    def tearDown(self):
        pass

    def test_request_get(self):
        with mock.patch("SettingsPage.requests.get", side_effect=mocked_request_get) as mocked_get:
            long_url  = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1"
            short_url = "https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson"

            real_call = self.settings_page.request_new_data(long_url)

            #check a valid request and good response
            mocked_get.assert_called_once_with(long_url)
            self.assertTrue(real_call.ok)
            self.assertEqual(real_call.status_code, 200, "Should be 200")
            self.assertEqual(real_call.json_data, {"type":"FeatureCollection","metadata":{"generated":1557156255000,"url":"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2019-05-05T15:55:03%2B00:00&endtime=2019-05-06T15:55:03%2B00:00&minlatitude=-90&maxlatitude=90&minlongitude=-180&maxlongitude=180&mindepth=-100&maxdepth=1000&minmagnitude=1&maxmagnitude=2&limit=1","title":"USGS Earthquakes","status":200,"api":"1.8.1","limit":1,"offset":1,"count":1},"features":[{"type":"Feature","properties":{"mag":1.7,"place":"75km S of Kobuk, Alaska","time":1557153499064,"updated":1557153801598,"tz":-540,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/ak0195sm9zcz","detail":"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ak0195sm9zcz&format=geojson","felt":None,"cdi":None,"mmi":None,"alert":None,"status":"automatic","tsunami":0,"sig":44,"net":"ak","code":"0195sm9zcz","ids":",ak0195sm9zcz,","sources":",ak,","types":",geoserve,origin,","nst":None,"dmin":None,"rms":0.95,"gap":None,"magType":"ml","type":"earthquake","title":"M 1.7 - 75km S of Kobuk, Alaska"},"geometry":{"type":"Point","coordinates":[-157.2,66.2404,0.1]},"id":"ak0195sm9zcz"}]})
            self.assertTrue(os.path.isfile(self.jsonpath), True)
            
            #check a valid request and bad response
            real_call = self.settings_page.request_new_data(short_url)
            mocked_get.assert_called_with(short_url)
            self.assertFalse(real_call.ok)
            self.assertEqual(real_call.status_code, 400, "Should be 400")
            self.assertIsNone(real_call.json_data, "Should be None")
            os.remove(self.jsonpath)

            #check a valid request with connectivity issues
            real_call = self.settings_page.request_new_data(short_url+"&limit=100")
            mocked_get.assert_called_with(short_url+"&limit=100")
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