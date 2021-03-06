import tkinter as tk
import datetime
import math
from matplotlib.lines import Line2D
class MapPoint(Line2D):
    def __init__(self, x, y, magnitude, place, time, felt, cdi, mmi, alert, tsunami, sig, title, status, dmin, gap, magtype, type_):
        '''
        The object used when plotting points on the map, by storing the earthquakes properties and passing them to the PointInfoPage when
        clicked, thereby improving performance by not having to search through a list
        '''

        #calculates the radius of the point on the map in proportion to the magnitude
        markersize = math.pow(2, magnitude)/math.pow(2, magnitude//2)
        if magnitude<=3: color="green"
        elif 3<magnitude<=6: color="yellow"
        else: color="red"
        super().__init__(xdata=[x,], ydata=[y,],marker="o",markersize=markersize,color=color,alpha=.3,picker=markersize)

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

