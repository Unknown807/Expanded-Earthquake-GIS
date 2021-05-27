# Expanded-Earthquake-GIS
*tests have not been updated some will not work*

Python 3.7.3

## Modules Used
* tkinter
* basemap - v1.2.2
* matplotlib - v3.0.3
* numpy - v1.16.3
* beautifulsoup4 - v4.9.3
* pillow - v6.0.0
* pyproj - v1.9.6
* requests - v2.21.0

## Other Requirements
* OSGeo4W (Specifically GEOS library)

## Description
This was an exam project and improvement upon my first version, Simple-Earthquake-GIS (private archived).

This program gets earthquake data from the USGS using the Earthquake Catalog API and plots it onto a map. From there you can select a specific earthquake event to view further information about it (using wikipedia's API).

## How to Use

![alt text](/imgs/img1.PNG)

When running the program you will get the above screen. All of the options are explained when you hover over them, so to not repeat myself I'll only mention key ones.

Using the options you can specify the exact time frame and earthquake properties for getting the exact earthquake events you want. There is also a small dropdown in the bottom right hand corner, 'URL Time' which lets you specify a general time frame for getting earthquakes (past hour, day, week, month).

To send a request for earthquake data from your specific conditions you have to use the 'refresh' menu on the toolbar and then click 'use parameters'.

For the 'URL Time' dropdown also click 'refresh' and then you can choose to filter the earthquake events to get by magnitude:
* Significant Earthquakes (usually 6+)
* 4.5+ Magnitude
* 2.5+ Magnitude
* 1.0+ Magnitude

The data will be retrived after that and by switching to the map page via the 'pages' menu in the top right corner, the program will plot all the earthquake data.

![alt text](/imgs/img2.PNG)

Here you are offered the standard matplotlib graph features, a legend indicating the colour and size of earthquakes and the plotted map. By clicking on any earthquake point on the map, the program will fetch further information on it (from both the earthquake file and wikipedia).

![alt text](/imgs/img3.PNG)

On the left is information about the specific earthquake (tooltips for more detail) and on the right is information about the location the earthquake impacted. When getting this information it either looks for and finds '<place name>, <country/state/etc>' or '<country/state/etc>' or it doesn't find any information on the location.
