

from tkinter import messagebox
import tkinter as tk
import shutil
import time
import json
import re

import Pmw
import requests
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.basemap import Basemap
from matplotlib.lines import Line2D
from bs4 import BeautifulSoup as BS4
from PIL import ImageTk, Image
mp.use("TkAgg")

from TKCustomClasses import MapPoint

#tk.messageboxes should be uncommented during a production release, otherwise they are just an annoyance when it comes to testing

TIMEZONES = {"UTC":"%2B00:00", "ECT":"%2B01:00", "EET":"%2B02:00", "ART": "%2B02:00",
            "EAT": "%2B03:00", "MET": "%2B03:30", "NET":"%2B04:00", "PLT":"%2B05:00",
            "IST":"%2B05:30", "BST": "%2B06:00", "VST":"%2B07:00", "CTT": "%2B08:00",
            "JST": "%2B09:00", "ACT": "%2B09:30", "AET": "%2B10:00", "SST": "%2B11:00",
            "NST": "%2B12:00", "MIT": "-11:00", "HST": "-10:00", "AST": "-09:00",
            "PST": "-08:00", "PNT":"-07:00", "MST": "-07:00", "CST": "-06:00", "EST":"-05:00",
            "IET": "-05:00", "PRT": "-04:00", "CNT": "-03:30", "AGT": "-03:00", "BET": "-03:00",
            "CAT": "-01:00"}

def create_counter(parent, label_text, current_value, min_, max_, increment):
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
        
        self.coordframe_left = tk.Frame(self.coord_labelframe)
        self.coordframe_right = tk.Frame(self.coord_labelframe)
        self.coordframe_left.pack(side="left", fill="both", expand=True)
        self.coordframe_right.pack(side="left", fill="both", expand=True)
        
        self.extra_labelframe = tk.LabelFrame(self.options_frame, text="Additional Options", padx=3, pady=3)

        self.options_frame.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.query_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.coord_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.extra_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)

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
        
        self.circ_rect_search_menu = Pmw.OptionMenu(self.coordframe_right, labelpos="w", label_text="Search Option:",
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

        for widget, helpmsg in balloon_helps:
            self.setpage_balloon.bind(widget, helpmsg)
            widget.pack(pady=5)

    def validate_data(self):
        '''
        Function for validating all the data from the fields in the SettingsPage
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
            minlat = int(self.minlat_counter.component("entry").get())
            maxlat = int(self.maxlat_counter.component("entry").get())
            minlong = int(self.minlong_counter.component("entry").get())
            maxlong = int(self.maxlong_counter.component("entry").get())
            if (minlat and maxlat and minlong and maxlong) and (minlat < maxlat and minlong < maxlong):
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

        mindepth = int(self.mindepth_counter.component("entry").get())
        maxdepth = int(self.maxdepth_counter.component("entry").get())
        minmag = int(self.minmag_counter.component("entry").get())
        maxmag = int(self.maxmag_counter.component("entry").get())
        limit = self.limit_counter.component("entry").get()

        if limit:
            if (mindepth and maxdepth) and (mindepth < maxdepth):
                if (str(minmag) and maxmag) and (minmag < maxmag):
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

        self.request_new_data(base_url)
    
    def format_default_url(self, url):
        time_value = self.url_time_menu.getcurselection()
        self.request_new_data(url.format(time_value.lower()))

    def request_new_data(self, chosen_url):
        '''
        This Function will take in a url that calls the GeoJson API and will retrive the JSON data from
        that url and store it in a file, or if the url is the same as the previous one, it will use the
        same file
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
                    message = "{} earthquakes were found".format(data["metadata"]["count"])
                    messagebox.showinfo(title="Data Retrieved", message=message)
                return response
            
class MapPage(tk.Frame):
    '''
    A page that will show the map of currently plotted earthquakes
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.local_url = None
        self.current_line_objs = []
        self.mappage_balloon = Pmw.Balloon(self)

        self.bind("<<RefreshPlot>>", self.refresh_plot)

        self.menubar = Pmw.MenuBar(self, hull_relief="raised", hull_borderwidth=1, balloon=self.mappage_balloon)
        self.menubar.pack(side="top", fill="x")

        self.menubar.addmenu("pages", "Switch Pages", "", "right")
        self.menubar.addmenu("file", "File And Data Options")
        self.menubar.addmenuitem("file", "command", "Quit The Program",
            command=self.controller.on_close_window, label="Quit")

        self.menubar.addmenuitem("pages", "command", "Switch To Settings Page",
            command=lambda: self.controller.show_frame("SettingsPage"), label="Settings Page")

        self.map_frame = tk.Frame(self)
        self.map_frame.pack(side="bottom", fill="both", expand=True)

        legend_elements = [Line2D([0], [0], marker="o", color="g", label="Small (below 3)"),
                    Line2D([0], [0], marker="o", color="y", label="Medium (below 6)"),
                    Line2D([0], [0], marker="o", color="r", label="Large (above 6)")]

        self.map_figure = plt.figure(num=None, figsize=(12, 4))
        self.map_axes = self.map_figure.add_subplot(111)
        self.map_axes_legend = self.map_axes.legend(handles=legend_elements, loc="upper right")
        self.map_axes.set_title("Earthquake Events - Mercator Projection")
        self.map_figure.tight_layout()

        self.figure_basemap = Basemap(projection="merc", llcrnrlat=-80, urcrnrlat=80,
            llcrnrlon=-180, urcrnrlon=180, resolution="c")
        
        self.figure_basemap.drawcoastlines()
        self.figure_basemap.fillcontinents(color="tan", lake_color="lightblue")
        self.figure_basemap.drawparallels(np.arange(-90.,91.,30.), labels=(True, True, False, False), dashes=(2,2))
        self.figure_basemap.drawmeridians(np.arange(-180.,181.,60.), labels=(False, False, False, True), dashes=(2,2))
        self.figure_basemap.drawmapboundary(fill_color="lightblue")
        self.figure_basemap.drawcountries()

        self.figure_canvas = FigureCanvasTkAgg(self.map_figure, self.map_frame)
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
        self.canvas_pick_event = self.figure_canvas.mpl_connect("pick_event", self.display_point_info)
        
        self.figure_toolbar = NavigationToolbar2Tk(self.figure_canvas, self.map_frame)
        self.figure_toolbar.update()
        self.figure_canvas._tkcanvas.pack(side="top", fill="both", expand=True)
    
    def refresh_plot(self, event):
        '''
        Function for checking whether there is any different data to plot and if so
        reads it from the json file
        '''
        if self.local_url == self.controller.current_url:
            return

        self.local_url = self.controller.current_url
        with open("current_data.json", "r") as json_file:
            data = json.load(json_file)
        
        self.plot_points(data)
        message = "{} points plotted".format(data["metadata"]["count"])
        messagebox.showinfo(title="Data Plotted", message=message)

    def plot_points(self, filedata):
        '''
        Function for creating MapPoint objects and plotting them on the figure
        '''
        self.map_axes.lines.clear()
        self.current_line_objs.clear()
        for quake in filedata["features"]:
            lat=quake["geometry"]["coordinates"][1]
            if lat > 80: lat=80
            elif lat <-80: lat=-80
            nx,ny = self.figure_basemap((quake["geometry"]["coordinates"][0],), (lat,))

            new_point = MapPoint(nx, ny, quake["properties"]["mag"], quake["properties"]["place"],
                quake["properties"]["time"], quake["properties"]["felt"], quake["properties"]["cdi"],
                quake["properties"]["mmi"], quake["properties"]["alert"], quake["properties"]["tsunami"],
                quake["properties"]["sig"], quake["properties"]["title"], quake["properties"]["status"],
                quake["properties"]["dmin"], quake["properties"]["gap"], quake["properties"]["magType"],
                quake["properties"]["type"])
            
            self.current_line_objs+=[new_point]
            self.map_axes.add_line(new_point)
        self.figure_canvas.draw()
    
    def display_point_info(self, event):
        '''
        Function when an individual point is picked, prompts the user to view information about it
        '''
        line_obj = event.artist
        message="Here is more info about the point - {}".format(line_obj.place)
        
        messagebox.showinfo(title="Point Selected", message=message)
        self.figure_canvas.mpl_disconnect(self.canvas_pick_event)
        self.controller.call_display_info(line_obj)
        self.controller.show_frame("PointInfoPage")

    def reconnect_pick_event(self):
        '''
        Function to reconnect pick event with the figure after a previous disconnect
        '''
        self.canvas_pick_event = self.figure_canvas.mpl_connect("pick_event", self.display_point_info)
        
class PointInfoPage(tk.Frame):
    '''
    A page that will show the map of currently plotted earthquakes
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.infopage_balloon = Pmw.Balloon(self)
        self.font = ("Helvitica", 12)
        self.title_font = ("Helvetica", 12, "bold")

        self.menubar = Pmw.MenuBar(self, hull_relief="raised", hull_borderwidth=1, balloon=self.infopage_balloon)
        self.menubar.pack(fill="x")

        self.menubar.addmenu("file", "File and Data Options")
        self.menubar.addmenuitem("file", "command", "Quit The Program",
            command=self.controller.on_close_window, label="Quit")

        self.menubar.addmenu("pages", "Switch Pages", "", "right")
        self.menubar.addmenuitem("pages", "command", "Switch To Map Page",
            command=lambda: self.on_show_frame("MapPage"), label="Map Page")
        self.menubar.addmenuitem("pages", "command", "Switch To Settings Page",
            command=lambda: self.on_show_frame("SettingsPage"), label="Settings Page")

        self.label_title = tk.Label(self, text="Default Title", font=self.title_font)
        self.labelframe_container = tk.Frame(self)
        
        self.bulletpoint_labelframe = tk.LabelFrame(self.labelframe_container, text="Event Properties", font=self.title_font)
        self.bulletpoint_frame_left = tk.Frame(self.bulletpoint_labelframe)
        self.bulletpoint_frame_right = tk.Frame(self.bulletpoint_labelframe)

        self.wiki_labelframe = tk.LabelFrame(self.labelframe_container, text="Additional Information", font=self.title_font)
        self.wiki_frame_top = tk.Frame(self.wiki_labelframe)
        self.wiki_frame_bottom = tk.Frame(self.wiki_labelframe)
        
        self.label_title.pack(side="top", fill="x")
        self.labelframe_container.pack(side="bottom", fill="both", expand=True)
        self.bulletpoint_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.bulletpoint_frame_left.pack(side="left", fill="both", expand=True)
        self.bulletpoint_frame_right.pack(side="right", fill="both", expand=True)

        self.wiki_labelframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.wiki_frame_top.pack(side="top", fill="both", expand=True)
        self.wiki_frame_bottom.pack(side="bottom", fill="both", expand=True)

        self.wiki_scrolledtext = Pmw.ScrolledText(self.wiki_frame_bottom, text_padx=4, text_pady=4)
        self.wiki_scrolledtext.configure(text_state="disabled")

        image = Image.open("default_image.png")
        self.wiki_photo = ImageTk.PhotoImage(image)
        self.wiki_photo_label = tk.Label(self.wiki_frame_top, image=self.wiki_photo)
        self.wiki_photo_label.image = self.wiki_photo

        self.wiki_scrolledtext.pack(fill="both", expand=True, padx=5, pady=5)
        self.wiki_photo_label.pack(fill="both", expand=True, padx=5, pady=5)

        self.place_label = tk.Label(self.bulletpoint_frame_left, text="Place:", font=self.font)
        self.time_label = tk.Label(self.bulletpoint_frame_left, text="Time:", font=self.font)
        self.gap_label = tk.Label(self.bulletpoint_frame_left, text="Gap:", font=self.font)
        self.dmin_label = tk.Label(self.bulletpoint_frame_left, text="Dmin:", font=self.font)
        self.status_label = tk.Label(self.bulletpoint_frame_left, text="Status:", font=self.font)
        self.alert_label = tk.Label(self.bulletpoint_frame_left, text="Alert:", font=self.font)
        self.felt_label = tk.Label(self.bulletpoint_frame_left, text="Felt:", font=self.font)

        self.mag_label = tk.Label(self.bulletpoint_frame_right, text="Magnitude:", font=self.font)
        self.type_label = tk.Label(self.bulletpoint_frame_right, text="Type:", font=self.font)
        self.magtype_label = tk.Label(self.bulletpoint_frame_right, text="Magnitude Type:", font=self.font)
        self.sig_label = tk.Label(self.bulletpoint_frame_right, text="Significance:", font=self.font)
        self.tsunami_label = tk.Label(self.bulletpoint_frame_right, text="Tsunami:", font=self.font)
        self.mmi_label = tk.Label(self.bulletpoint_frame_right, text="MMI:", font=self.font)
        self.cdi_label = tk.Label(self.bulletpoint_frame_right, text="CDI:", font=self.font)

        balloon_helps = (
            (self.place_label, "Description of named geograpic region near to the event"),
            (self.time_label, "Time when event occurred"),
            (self.gap_label, "The largest azimuthal gap between azimuthally adjacent stations (in degrees)"),
            (self.dmin_label, "Horizontal distance from the epicenter to the nearest station (in degrees)"),
            (self.status_label, "Indicates whether the event has been reviewed by a human"),
            (self.alert_label, "The alert level from the PAGER earthquake impact scale"),
            (self.felt_label, "The total number of felt reports submitted to the DYFI system"),
            (self.mag_label, "The magnitude of the event"),
            (self.type_label, "Whether the event was an 'earthquake' or 'quarry'"),
            (self.magtype_label, "The method used to calculate the preferred magnitude for the event"),
            (self.sig_label, "A number describing how significant the event is (between 0 and 1000)"),
            (self.tsunami_label, "A flag indicating whether a large event ocurred in oceanic regions\nBut the existence of this flag does not indicate if a tsunami\nactually did or will exist"),
            (self.mmi_label, "The maximum estimated instrumental intensity for the event"),
            (self.cdi_label, "The maximum reported intensity for the event"),
        )
        
        for widget, helpmsg in balloon_helps:
            self.infopage_balloon.bind(widget, helpmsg)
            widget.pack(pady=10, anchor="w")

    def on_show_frame(self, page_name):
        self.controller.call_reconnect()
        self.controller.show_frame(page_name)

    def configure_labels(self, point_obj):
        self.label_title.config(text=point_obj.title)

        self.place_label.config(text="Place: {}".format(point_obj.place))
        self.time_label.config(text="Time: {}".format(point_obj.time))
        self.gap_label.config(text="Gap: {}".format(point_obj.gap))
        self.dmin_label.config(text="Dmin: {}".format(point_obj.dmin))
        self.status_label.config(text="Status: {}".format(point_obj.status))
        self.alert_label.config(text="Alert: {}".format(point_obj.alert))
        self.felt_label.config(text="Felt: {}".format(point_obj.felt))
        self.mag_label.config(text="Magnitude: {}".format(point_obj.magnitude))
        self.type_label.config(text="Type: {}".format(point_obj.type_))
        self.magtype_label.config(text="Magnitude Type: {}".format(point_obj.magtype))
        self.sig_label.config(text="Significance: {}".format(point_obj.sig))
        self.tsunami_label.config(text="Tsunami: {}".format(point_obj.tsunami))
        self.mmi_label.config(text="MMI: {}".format(point_obj.mmi))
        self.cdi_label.config(text="CDI: {}".format(point_obj.cdi))

    def configure_scrolledtext(self):
        text_content = self.get_wiki_text()
        if not text_content:
            text_content = "No Information Found"
        self.wiki_scrolledtext.settext(text_content)

    def configure_event_photo(self):
        use_default = "current_image.png" if self.get_wiki_image() else "default_image.png"
        
        image = Image.open(use_default)
        self.wiki_photo = ImageTk.PhotoImage(image)
        self.wiki_photo_label.config(image=self.wiki_photo)
        self.wiki_photo_label.image = self.wiki_photo

    def wiki_image_url_request(self):
        response = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=pageimages&format=json&pithumbsize=300".format(self.wiki_image_data))
        data = response.json()
        data = data["query"]["pages"]
        key = "".join(data.keys())

        if key == "-1":
            return False
        
        if data[key].get("thumbnail", None) is None:
            return False
        
        data = data[key]["thumbnail"]["source"]

        return data

    def get_wiki_image(self):
        image_url = self.wiki_image_url_request()
        if not image_url:
            return False
        
        response = requests.get(image_url, stream=True)
        with open("current_image.png", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        return True

    def wiki_text_url_request(self, data):
        response = requests.get("https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page={}".format(data))
        if response.ok:
            data = response.json()
            if "error" in data.keys():
                return False
            else:
                data = data["parse"]["text"]["*"]
                return data

    def get_wiki_text(self):
        search_data = self.place_label.cget("text").split()
        if not search_data[1][0].isdigit():
            self.wiki_image_data = False
            return False
        
        search_data = " ".join(search_data[4:])
        response = self.wiki_text_url_request(search_data)
        if not response:
            search_data = search_data.split(",")
            response = self.wiki_text_url_request(search_data[0])
            if not response:
                response = self.wiki_text_url_request(search_data[1])
                if not response:
                    return False
                else:
                    self.wiki_image_data = search_data[1]
            else:
                self.wiki_image_data = search_data[0]
        else:
            self.wiki_image_data = search_data

        soup = BS4(response, features="lxml")
        data = soup.find("p").getText()
        if "Redirect to:" in data:
            data = soup.find("a").getText()
            self.wiki_image_data = data
            response = self.wiki_text_url_request(data)
        elif "commonly refers to:" in search_data or "may also refer to:" in search_data:
            data = soup.find_all("a")[1]
            self.wiki_image_data = data
            response = self.wiki_text_url_request(data)
        elif "may refer to:" in data:
            self.wiki_image_data = search_data[1]
            response = self.wiki_text_url_request(search_data[1])
        
        soup = BS4(response, features="lxml")
        all_text=""
        for string in soup.find_all("p"):
            if "\n" not in string:
                all_text+=string.get_text()
        all_text = "".join(re.split("\[\d+\]", all_text))

        return all_text
