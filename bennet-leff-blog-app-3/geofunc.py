import urllib2
from google.appengine.ext import db
from xml.dom import minidom

def get_coords(ip):
    # uses urlib2 library to "open" any url so I can check any ip with a http get request
    url = urllib2.urlopen("http://freegeoip.net/xml/{0}".format(ip))
    xml = minidom.parseString(url.read())

    lat = xml.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
    long = xml.getElementsByTagName("Longitude")[0].childNodes[0].nodeValue
    coords = tuple([float(lat), float(long)])

    return db.GeoPt(coords[0], coords[1])

# examples
# print get_coords("0.0.0.0")
# print get_coords("12.215.42.19")