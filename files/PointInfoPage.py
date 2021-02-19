from tkinter import messagebox
import tkinter as tk
import shutil
import json
import re

import Pmw
import requests
from bs4 import BeautifulSoup as BS4
from PIL import ImageTk, Image

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
        #this helps to reduce redundancy by looping through the tuple and both binding a tooltip and packing it to the screen at the same time
        for widget, helpmsg in balloon_helps:
            self.infopage_balloon.bind(widget, helpmsg)
            widget.pack(padx=10, pady=10, anchor="w")

    def on_show_frame(self, page_name):
        '''
        If the user switches back to the settings or map page, then the program first reconnects the pick event to 
        all MapPoint objects on the map.
        '''
        self.controller.call_reconnect()
        self.controller.show_frame(page_name)

    def configure_labels(self, point_obj):
        '''
        Method for changing the text of several onscreen labels in order to display more in-depth
        information about a selected earthquake
        '''
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
        '''
        Method for retrieving text information about the place affected by communicating
        with the wikipedia API, and configuring the textbox with it
        '''
        text_content = self.get_wiki_text()
        if not text_content:
            text_content = "No Information Found"
        self.wiki_scrolledtext.settext(text_content)

    def configure_event_photo(self):
        '''
        Method for retrieving a picture of the place affected by communicating with the
        wikipedia API, and configuring the wiki_photo_label with it
        '''
        use_default = "current_image.png" if self.get_wiki_image() else "default_image.png"
        image = Image.open(use_default)
        self.wiki_photo = ImageTk.PhotoImage(image)
        self.wiki_photo_label.config(image=self.wiki_photo)
        self.wiki_photo_label.image = self.wiki_photo

    def wiki_image_url_request(self):
        '''
        Method used for the direct request to the wikipedia API for an image url for later download
        '''
        try:
            response = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=pageimages&format=json&pithumbsize=300".format(self.wiki_image_data))
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False

        data = response.json()
        data = data["query"]["pages"]
        key = "".join(data.keys())

        if key == "-1": #if no image is found for the selected place
            return False
        
        if data[key].get("thumbnail", None) is None: #if the selected place exists, but no image was found
            return False
        
        data = data[key]["thumbnail"]["source"] #image url is here

        return data

    def get_wiki_image(self):
        '''
        Method used to download the image of the affected place onto the disk, with
        the image's download url
        '''
        image_url = self.wiki_image_url_request()
        if not image_url:
            return False #if no image was found then there is no point in continuing
        
        try:
            response = requests.get(image_url, stream=True)
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False
        with open("current_image.png", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file) #statement for writing the image's raw data to disk as a png image file
        del response

        return True

    def wiki_text_url_request(self, data):
        '''
        Method used for the direct request to the wikipedia API for text information regarding the affected place
        '''
        try:
            response = requests.get("https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page={}".format(data))
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False

        data = response.json()
        if "error" in data.keys():
            return False #if the article does not exist, or there is no information regarding the place
        else:
            data = data["parse"]["text"]["*"] #the retrieved here
            return data

    def get_wiki_text(self):
        '''
        By using the place name, this method creates and formats the url most likely to get
        an accurate match with the wikipedia place.
        ---------------------------------------------
        A total of 3-4 requests may be made, with varying request arguments.
        
        example_text = "Salamanca, Chile"
        
        first one request is made with the argument of "Salamanca, Chile"
        if that fails then a second request is made with the argument of "Salamanca"
        if the result is still not acceptable then a final third request is made with
        the argument of "Chile", just to be able to get the general information about
        the country instead
        '''
        search_data = self.place_label.cget("text").split()
        if not search_data[1][0].isdigit():
            self.wiki_image_data = False
            return False
        
        search_data = " ".join(search_data[4:])
        response = self.wiki_text_url_request(search_data)
        if not response:
            search_data = search_data.split(",")
            response = self.wiki_text_url_request(search_data[1])
            if not response:
                self.wiki_image_data = False
                return False
            else:
                self.wiki_image_data = search_data[1]
        else:
            self.wiki_image_data = search_data

        soup = BS4(response, features="lxml")
        data = soup.find("p").getText() #retrieves text and parses out all of the unecessary html tags
        if "Redirect to:" in data: #instead of the text, if theres a redirect link, then it is followed to find the right text
            data = soup.find("a").getText() #finds all <a> tags in the text
            self.wiki_image_data = data
            response = self.wiki_text_url_request(data) # uses the link found in the first <a> tag for redirect, its almost always the first link
        elif "commonly refers to:" in data or "may also refer to:" in data: #different format of redirect, gets the first item from the list of links
            data = soup.find_all("a")[1] #in this case its the second <a> tag link
            self.wiki_image_data = data
            response = self.wiki_text_url_request(data)
        elif "may refer to:" in data: #different format of redirect
            search_data = search_data if isinstance(search_data, list) else search_data.split() #sometimes if the first request was successful, then the place name wouldn't have been split into a list, so its easier to just expect a list instead
            self.wiki_image_data = search_data[1]
            response = self.wiki_text_url_request(search_data[1])
        
        soup = BS4(response, features="lxml")
        all_text=""
        for string in soup.find_all("p"): #finds all <p> tags and appends them onto all_text with no newline characters (to avoid text formatting issues)
            if "\n" not in string:
                all_text+=string.get_text() 
        all_text = "".join(re.split("\[\d+\]", all_text)) #sometimes wikipedia articles could have appendix links, e.g [3], which need to be removed

        return all_text #the text is returned for use in configuring the textbox
