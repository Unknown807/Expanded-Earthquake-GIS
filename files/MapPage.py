from tkinter import messagebox
import tkinter as tk
import json

import Pmw
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.basemap import Basemap
from matplotlib.lines import Line2D
mp.use("TkAgg")

from TKCustomClasses import MapPoint

class MapPage(tk.Frame):
    '''
    A page that will show the map of currently plotted earthquakes from the 'current_data.json' file
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.local_url = None
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

        #Line2D objects are used here to be placed in the legend of the graph for more detail on the map
        legend_elements = [Line2D([0], [0], marker="o", color="green", label="Small (below 3)"),
                    Line2D([0], [0], marker="o", color="yellow", label="Medium (below 6)"),
                    Line2D([0], [0], marker="o", color="red", label="Large (above 6)")]

        self.map_figure = plt.figure(num=None, figsize=(12, 4))
        self.map_axes = self.map_figure.add_subplot(111)
        self.map_axes_legend = self.map_axes.legend(handles=legend_elements, loc="upper right") #placing the legend
        self.map_axes.set_title("Earthquake Events - Mercator Projection")
        self.map_figure.tight_layout() #makes sure that when placing the map onto the GUI, it is responsive

        self.figure_basemap = Basemap(projection="merc", llcrnrlat=-80, urcrnrlat=80,
            llcrnrlon=-180, urcrnrlon=180, resolution="c") #defines that the map is using mercator projection
        
        self.figure_basemap.drawcoastlines()
        self.figure_basemap.fillcontinents(color="tan", lake_color="lightblue")
        self.figure_basemap.drawstates(color="darkred")
        self.figure_basemap.drawparallels(np.arange(-90.,91.,30.), labels=(True, True, False, False), dashes=(2,2))
        self.figure_basemap.drawmeridians(np.arange(-180.,181.,60.), labels=(False, False, False, True), dashes=(2,2))
        self.figure_basemap.drawmapboundary(fill_color="lightblue")
        self.figure_basemap.drawcountries()

        self.figure_canvas = FigureCanvasTkAgg(self.map_figure, self.map_frame) #creates the figure and draws the map onto it
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
        self.canvas_pick_event = self.figure_canvas.mpl_connect("pick_event", self.display_point_info)
        
        self.figure_toolbar = NavigationToolbar2Tk(self.figure_canvas, self.map_frame) #Toolbar with additional options is added to the figure
        self.figure_toolbar.update()
        self.figure_canvas._tkcanvas.pack(side="top", fill="both", expand=True)
    
    def refresh_plot(self, event):
        '''
        Method for checking whether there is any different data to plot and if so
        reads it from the json file, done by checking the local_url against controller's current_url
        '''
        if self.local_url == self.controller.current_url:
            return "Same Request"

        self.local_url = self.controller.current_url
        with open("current_data.json", "r") as json_file:
            data = json.load(json_file)
        
        self.plot_points(data)
        messagebox.showinfo(title="Data Plotted", message="{} points plotted".format(data["metadata"]["count"]))

    def plot_points(self, filedata):
        '''
        Method for creating MapPoint objects and plotting them on the figure, by first clearing the figure of any
        previous plots and then reading 'current_data.json'
        '''
        self.map_axes.lines.clear()
        
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
            
            self.map_axes.add_line(new_point)
        self.figure_canvas.draw()
    
    def display_point_info(self, event):
        '''
        Method when an individual point is picked, prompts the user to view information about it
        '''
        line_obj = event.artist
        
        messagebox.showinfo(title="Point Selected", message="Here is more info about the point - {}".format(line_obj.place))
        self.figure_canvas.mpl_disconnect(self.canvas_pick_event)
        self.controller.call_display_info(line_obj)
        self.controller.show_frame("PointInfoPage")

    def reconnect_pick_event(self):
        '''
        Method to reconnect pick event with the figure after a previous disconnect
        '''
        self.canvas_pick_event = self.figure_canvas.mpl_connect("pick_event", self.display_point_info)