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
        try:
            response = requests.get("https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=pageimages&format=json&pithumbsize=300".format(self.wiki_image_data))
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False

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
        
        try:
            response = requests.get(image_url, stream=True)
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False
        with open("current_image.png", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        return True

    def wiki_text_url_request(self, data):
        try:
            response = requests.get("https://en.wikipedia.org/w/api.php?action=parse&format=json&section=0&prop=text&page={}".format(data))
        except requests.exceptions.ConnectionError:
            return False
        if not response.ok:
            return False

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
                    self.wiki_image_data = False
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
        elif "commonly refers to:" in data or "may also refer to:" in data:
            data = soup.find_all("a")[1]
            self.wiki_image_data = data
            response = self.wiki_text_url_request(data)
        elif "may refer to:" in data:
            search_data = search_data if isinstance(search_data, list) else search_data.split()
            self.wiki_image_data = search_data[1]
            response = self.wiki_text_url_request(search_data[1])
        
        soup = BS4(response, features="lxml")
        all_text=""
        for string in soup.find_all("p"):
            if "\n" not in string:
                all_text+=string.get_text()
        all_text = "".join(re.split("\[\d+\]", all_text))

        return all_text
