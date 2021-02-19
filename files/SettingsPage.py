from tkinter import messagebox
import tkinter as tk
import time
import json
import re

import Pmw
import requests

#dictionary of many common timezones, some have been urlencoded to avoid errors with the GeoJson API
TIMEZONES = {"UTC":"%2B00:00", "ECT":"%2B01:00", "EET":"%2B02:00", "ART": "%2B02:00",
    "EAT": "%2B03:00", "MET": "%2B03:30", "NET":"%2B04:00", "PLT":"%2B05:00",
    "IST":"%2B05:30", "BST": "%2B06:00", "VST":"%2B07:00", "CTT": "%2B08:00",
    "JST": "%2B09:00", "ACT": "%2B09:30", "AET": "%2B10:00", "SST": "%2B11:00",
    "NST": "%2B12:00", "MIT": "-11:00", "HST": "-10:00", "AST": "-09:00",
    "PST": "-08:00", "PNT":"-07:00", "MST": "-07:00", "CST": "-06:00", "EST":"-05:00",
    "IET": "-05:00", "PRT": "-04:00", "CNT": "-03:30", "AGT": "-03:00", "BET": "-03:00",
    "CAT": "-01:00"}

def create_counter(parent, label_text, current_value, min_, max_, increment):
    '''
    function for creating Pmw.Counter objects short hand
    '''
    return Pmw.Counter(parent, labelpos="w", label_text=label_text,
        label_justify="left", entryfield_value=current_value, datatype={"counter":"real", "separator":"."},
        entryfield_validate = {"validator":"real", "min":min_, "max":max_, "separator":"."}, increment=increment)

class SettingsPage(tk.Frame):
    '''
    A page that will allow you to change properties of the method of mapping
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.field_font = ("Helvitica", 16)
        self.setpage_balloon = Pmw.Balloon(self)

        self.menubar = Pmw.MenuBar(self, hull_relief="raised", hull_borderwidth=1, balloon=self.setpage_balloon)
        self.menubar.pack(fill="x")

        self.menubar.addmenu("file", "File and Data Options")
        self.menubar.addmenuitem("file", "command", "Quit The Program",
            command=self.controller.on_close_window, label="Quit")

        self.menubar.addmenu("refresh", "Update Earthquake Data")
        self.menubar.addmenu("pages", "Switch Pages", "", "right")
        self.menubar.addmenuitem("pages", "command", "Switch To Map Page",
            command=lambda: self.controller.show_frame("MapPage"), label="Map Page")

        self.menubar.addmenuitem("refresh", "command", "Use The Data You Specified",
            command=self.validate_data, label="use parameters")
        self.menubar.addmenuitem("refresh", "command", "A Standard URL",
            command=lambda: self.format_default_url("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_{}.geojson"), label="Significant Earthquakes")
        self.menubar.addmenuitem("refresh", "command", "A Standard URL",
            command=lambda: self.format_default_url("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_{}.geojson"), label="4.5+ Earthquakes")
        self.menubar.addmenuitem("refresh", "command", "A Standard URL",
            command=lambda: self.format_default_url("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_{}.geojson"), label="2.5+ Earthquakes")
        self.menubar.addmenuitem("refresh", "command", "A Standard URL",
            command=lambda: self.format_default_url("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_{}.geojson"), label="1.0+ Earthquakes")

        self.options_frame = tk.Frame(self)

        self.query_labelframe = tk.LabelFrame(self.options_frame, text="Query Options", padx=3, pady=3)
        self.coord_labelframe = tk.LabelFrame(self.options_frame, text="Search Options", padx=3, pady=3)
        self.coordframe_right_container = tk.Frame(self.coord_labelframe)
        self.searchtype_labelframe = tk.LabelFrame(self.coordframe_right_container, text="Search Type")
        
        self.coordframe_left = tk.LabelFrame(self.coord_labelframe, text="Rectangle Search")
        self.coordframe_right = tk.LabelFrame(self.coordframe_right_container, text="Circle Search")
        self.coordframe_left.pack(side="left", fill="both", expand=True, padx=3, pady=3)
        self.coordframe_right.pack(side="top", fill="both", expand=True, padx=3, pady=3)
        
        self.extra_labelframe = tk.LabelFrame(self.options_frame, text="Additional Options", padx=3, pady=3)

        self.options_frame.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.coordframe_right_container.pack(side="left", fill="both", expand=True, padx=3, pady=3)
        self.searchtype_labelframe.pack(side="bottom", fill="both", expand=True, padx=3, pady=3)
        self.query_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.coord_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.extra_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        #used to get and format the current date and time for the Pmw.Counter class
        now = (float(time.time())/300)*300
        default_date = time.strftime("%Y-%m-%d", time.localtime(now))
        default_time = time.strftime("%H:%M:%S", time.localtime(now))

        self.startdate_counter = Pmw.Counter(self.query_labelframe, labelpos="w", label_text="Start Date:",
            entryfield_value=default_date, entryfield_command=None,
            entryfield_validate={"validator": "date", "separator": "-"},
            datatype={"counter": "date", "format": "ymd", "yyyy": 1, "separator": "-"})

        self.enddate_counter = Pmw.Counter(self.query_labelframe, labelpos="w", label_text="End Date:",
            entryfield_value=default_date, entryfield_command=None,
            entryfield_validate={"validator": "date", "separator": "-"},
            datatype={"counter": "date", "format": "ymd", "yyyy": 1, "separator": "-"})
        
        self.starttime_counter = Pmw.Counter(self.query_labelframe, labelpos="w", label_text="Start Time:",
            entryfield_value=default_time, entryfield_validate={"validator": "time", "min": "00:00:00",
                "max": "23:59:59", "minstrict": 0, "maxstrict": 0},
            datatype={"counter": "time", "time24": 1}, increment=5*60)

        self.endtime_counter = Pmw.Counter(self.query_labelframe, labelpos="w", label_text="End Time:",
            entryfield_value=default_time, entryfield_validate={"validator": "time", "min": "00:00:00",
                "max": "23:59:59", "minstrict": 0, "maxstrict": 0},
            datatype={"counter": "time", "time24": 1}, increment=5*60)

        self.timezone_menu = Pmw.OptionMenu(self.query_labelframe, labelpos="w", label_text="Time Zone:",
            items=tuple(TIMEZONES.keys()), menubutton_width=10, command=None)

        self.url_time_menu = Pmw.OptionMenu(self.extra_labelframe, labelpos="w", label_text="URL Time:",
            items=("Hour", "Day", "Week", "Month"), menubutton_width=10, command=None)
        
        self.circ_rect_search_menu = Pmw.OptionMenu(self.searchtype_labelframe, labelpos="w", label_text="Search Option:",
            items=("Rectangle", "Circle"), menubutton_width=10, command=None)

        self.minlat_counter = create_counter(self.coordframe_left, "Min Latitude:", "-90", "-90", "90", 0.5)
        self.maxlat_counter = create_counter(self.coordframe_left, "Max Latitude:", "90", "-90", "90", 0.5)
        self.minlong_counter = create_counter(self.coordframe_left, "Min Longitude:", "-180", "-180", "180", 0.5)
        self.maxlong_counter = create_counter(self.coordframe_left, "Max Longitude", "180", "-180", "180", 0.5)
        self.latitude_counter = create_counter(self.coordframe_right, "Latitude:", "90", "-90", "90", 0.5)
        self.longitude_counter = create_counter(self.coordframe_right, "Longitude:", "180", "-180", "180", 0.5)
        self.maxradius_counter = create_counter(self.coordframe_right, "Max Radius:", "180", "0", "180", 1)
        self.mindepth_counter = create_counter(self.extra_labelframe, "Min Depth:", "-100", "-100", "1000", 1)
        self.maxdepth_counter = create_counter(self.extra_labelframe, "Max Depth:", "1000", "-100", "1000", 1)
        self.minmag_counter = create_counter(self.extra_labelframe, "Min Magnitude:", "1", "0", None, 1)
        self.maxmag_counter = create_counter(self.extra_labelframe, "Max Magnitude:", "2", "1", None, 1)
        self.limit_counter = create_counter(self.extra_labelframe, "Search Limit:", "1", "1", "20000", 1)

        balloon_helps = (
            (self.startdate_counter, "Limit to events on or after the specified start date"),
            (self.enddate_counter, "Limit to events on or before the specified end date"),
            (self.starttime_counter, "Limit to events on or after the specified start time"),
            (self.endtime_counter, "Limit to events on or before the specified end time"),
            (self.timezone_menu, "Allow for timezone, default is Universal Coordinated Time"),
            (self.minlat_counter, "Limit to events with a latitude larger than the specified minimum\nBetween -90 and 90 degrees"),
            (self.maxlat_counter, "Limit to events with a latitude smaller than the specified maximum\nBetween -90 and 90 degrees"),
            (self.minlong_counter, "Limit to events with a longitude larger than the specified minimum\nBetween -180 and 180 degrees"),
            (self.maxlong_counter, "Limit to events with a longitude smaller than the specified maximum\nBetween -180 and 180 degrees"),
            (self.latitude_counter, "Specify the latitude to be used for a radius search\nBetween -90 and 90 degrees"),
            (self.longitude_counter, "Specify the longitude to be used for a radius search\nBetween -90 and 90 degrees"),
            (self.maxradius_counter, "Limit to events within the specified maximum number of degrees\nfrom the geographic point defined by the latitude and longitude parameters\nBetween 0 and 180 degrees"),
            (self.circ_rect_search_menu, "Specify for a Circle search or Rectangle search\n(left for rectangle search, right for circle search)"),
            (self.mindepth_counter, "Limit to events with depth more than the specified minimum\nBetween -100 and 1000 km"),
            (self.maxdepth_counter, "Limit to events with depth less than the specified maximum\nBetween -100 and 1000 km"),
            (self.minmag_counter, "Limit to events with a magnitude larger than the specified minimum"),
            (self.maxmag_counter, "Limit to events with a magnitude smaller than the specified maximum"),
            (self.limit_counter, "Specify the amount of results returned from your query\nBetween 1 and 20000. Depending on the limit specified,\nreading data from the server may take quite long"),
            (self.url_time_menu, "If you choose other url options in 'refresh', then this filters by what time interval to get earthquake data"),
        )
        #this helps to reduce redundancy by looping through the tuple and both binding a tooltip and packing it to the screen at the same time
        for widget, helpmsg in balloon_helps:
            self.setpage_balloon.bind(widget, helpmsg)
            widget.component("label").configure(font=self.field_font)
            widget.pack(padx=5, fill="y", expand=True)

    def validate_data(self):
        '''
        Method for validating all the data from the fields in the SettingsPage
        
        e.g (starttime and endtime) checks that both fields are not blank, then the program uses
        f strings to pass the values into a url format (the GeoJson request url)
        '''
        base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson"

        startdate = self.startdate_counter.component("entry").get()
        enddate = self.enddate_counter.component("entry").get()
        starttime = self.starttime_counter.component("entry").get()
        endtime = self.endtime_counter.component("entry").get()
        timezone = TIMEZONES.get(self.timezone_menu.getcurselection())

        if (starttime and endtime):
            if (startdate and enddate):
                base_url += f"&starttime={startdate}T{starttime}{timezone}&endtime={enddate}T{endtime}{timezone}"
            else: 
                messagebox.showerror(title="Date Error", message="Sorry, the dates entered are incorrect")
                return "Bad Date"
        else: 
            messagebox.showerror(title="Time Error", message="Sorry, the times entered are inccorect")
            return "Bad Time"

        search_type=self.circ_rect_search_menu.getcurselection()
        if search_type == "Rectangle":
            minlat = self.minlat_counter.component("entry").get()
            maxlat = self.maxlat_counter.component("entry").get()
            minlong = self.minlong_counter.component("entry").get()
            maxlong = self.maxlong_counter.component("entry").get()
            if (minlat and maxlat and minlong and maxlong) and (float(minlat) < float(maxlat) and float(minlong) < float(maxlong)):
                base_url += f"&minlatitude={minlat}&maxlatitude={maxlat}&minlongitude={minlong}&maxlongitude={maxlong}"
            else: 
                messagebox.showerror(title="Rectangle Search Error", message="Please check that you've entered the min/max latitudes\nand longitudes correctly for the rectangle search")
                return "Bad Rectangle Options"

        elif search_type == "Circle":
            lat = self.latitude_counter.component("entry").get()
            long_ = self.longitude_counter.component("entry").get()
            maxradius = self.maxradius_counter.component("entry").get()
            if (lat and long_ and maxradius):
                base_url += f"&latitude={lat}&longitude={long_}&maxradius={maxradius}"
            else: 
                messagebox.showerror(title="Circle Search Error", message="Please check that you've entered the lat/long/maxradius correctly for the circle search")
                return "Bad Circle Options"

        mindepth = self.mindepth_counter.component("entry").get()
        maxdepth = self.maxdepth_counter.component("entry").get()
        minmag = self.minmag_counter.component("entry").get()
        maxmag = self.maxmag_counter.component("entry").get()
        limit = self.limit_counter.component("entry").get()

        if limit:
            if (mindepth and maxdepth) and (float(mindepth) < float(maxdepth)):
                if (minmag and maxmag) and (float(minmag) < float(maxmag)):
                    base_url += f"&mindepth={mindepth}&maxdepth={maxdepth}&minmagnitude={minmag}&maxmagnitude={maxmag}&limit={limit}"
                else: 
                    messagebox.showerror(title="Magnitude Error", message="Please check that you've entered the min/max magnitude\nfields correctly")
                    return "Bad Min/Max Magnitudes"
            else: 
                messagebox.showerror(title="Depth Error", message="Please check that you've entered the min/max depth fields correctly")
                return "Bad Min/Max Depths"
        else: 
            messagebox.showerror(title="Search Limit Error", message="Please check that the search limit you've entered is valid")
            return "Bad Limit"

        print(base_url)
        self.request_new_data(base_url)
    
    def format_default_url(self, url):
        '''
        If any toolbar button other than 'use current parameters' is pressed, then the program will simply use
        one of the default requests to get all earthquakes of a certain magnitude (2.5+, 4.5+, etc)
        '''
        time_value = self.url_time_menu.getcurselection()
        self.request_new_data(url.format(time_value.lower()))

    def request_new_data(self, chosen_url):
        '''
        This method uses the requests module to request the earthquake data using the chosen_url arguement.
        If the url is the same as the previos request's url, then the previous data is still on the disk and the
        program uses that instead of starting a new request (simple memoization).
        '''
        if self.controller.current_url == chosen_url:
            return
        else:
            messagebox.showinfo(title="Loading", message="Fetching data please wait for another notification...")
            try:
                response = requests.get(chosen_url)
            except requests.exceptions.ConnectionError:
                messagebox.showerror(title="Connection Error", message="Please check you're internet connection\nas a request could not be made")
                return "Bad Connection"
            if not response.ok:
                messagebox.showerror(title="Server Error", message="There was an error in retrieving the data\nThe data collection service could be down right now")
                return response
            else:
                self.controller.modify_url(chosen_url)
                with open("current_data.json", "w") as json_file:
                    data = response.json()
                    json.dump(data, json_file)
                    messagebox.showinfo(title="Data Retrieved", message="{} earthquakes were found".format(data["metadata"]["count"]))
                return response