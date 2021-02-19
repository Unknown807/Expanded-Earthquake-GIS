import os
import sys
import tkinter as tk
from SettingsPage import SettingsPage
from MapPage import MapPage
from PointInfoPage import PointInfoPage

class GISMain(tk.Tk):
    '''
    The Main Tk Window
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w, h = self.winfo_screenwidth()-100, self.winfo_screenheight()-100
        self.geometry("{}x{}+0+0".format(w, h))
        self.title("Earthquake Mapping")
        self.protocol("WM_DELETE_WINDOW", self.on_close_window)

        self.container = tk.Frame(self)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        self.current_url = None
        
        #loop for storing all page classes in a dictionary where their name corresponds to the instance
        #thereby allowing them to be shown to the user via the show_frame method
        for frame in (SettingsPage, MapPage, PointInfoPage):
            page_name = frame.__name__
            new_frame = frame(parent=self.container, controller=self)
            self.frames[page_name] = new_frame
            new_frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("SettingsPage")

    def show_frame(self, page_name):
        '''
        Method for lifting frames over one another
        '''
        frame = self.frames[page_name]
        frame.event_generate("<<RefreshPlot>>")
        frame.tkraise()
    
    def modify_url(self, new_url):
        '''
        Method for modfiying the url to check whether new data needs plotting
        '''
        self.current_url = new_url
    
    def call_reconnect(self):
        '''
        Method that calls the map page's reconnect function to enable event handling again
        '''
        page = self.frames["MapPage"]
        page.reconnect_pick_event()
    
    def call_display_info(self, point_obj):
        '''
        Method that calls the point info page's configure labels function to configure labels
        to show the appropriate information about the selected point
        '''
        page = self.frames["PointInfoPage"]
        page.configure_labels(point_obj)
        page.configure_scrolledtext()
        page.configure_event_photo()
    
    def on_close_window(self):
        '''
        Method that makes sure the current_data.json file is deleted as after the
        program is closed its no longer needed
        '''
        filename="current_data.json"
        if os.path.isfile(filename):
            os.remove(filename)
            
        filename="current_image.png"
        if os.path.isfile(filename):
            os.remove(filename)
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = GISMain()
    root.mainloop()