import tkinter as tk
import datetime
from matplotlib.lines import Line2D

class MapPoint(object):
    def __init__(self, magnitude, place, time, felt, cdi, mmi, alert, tsunami, sig, title, status, dmin, gap, magtype, type_):
        self.title = title
        self.place = place
        self.time = datetime.datetime.fromtimestamp(time/1000.0).isoformat()
        self.magnitude = magnitude
        self.felt = felt
        self.cdi = cdi
        self.mmi = mmi
        self.alert = alert
        self.tsunami = bool(tsunami)
        self.sig = sig
        self.status = status
        self.dmin = dmin
        self.gap = gap
        self.magtype = magtype
        self.type_ = type_
        self.line_obj = None
    
    def create_line_obj(self, x, y):
        '''
        Function for creating a line2D object to have a reference to and be able
        to plot on the figure
        '''
        markersize = 2+(self.magnitude*1.5)
        self.line_obj = Line2D(x, y, marker="o", markersize=markersize, color="r", alpha=.45, picker=4)

