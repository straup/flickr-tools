#!/usr/bin/env python

import optparse
import ConfigParser
import Flickr.API
import elementtree.ElementTree as ET
    
parser = optparse.OptionParser()
parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
parser.add_option("-v", "--verbose", dest="verbose", help="display more than just a WOE ID", action="store_true", default=False)
parser.add_option("--lat", dest="latitude", help="the latitude to reverse geocode")
parser.add_option("--lon", dest="longitude", help="the longitude to reverse geocode")

(opts, args) = parser.parse_args()

cfg = ConfigParser.ConfigParser()
cfg.read(opts.config)

apikey=cfg.get('flickr', 'api_key')

api = Flickr.API.API(apikey)
req = Flickr.API.Request(method='flickr.places.findByLatLon', lat=opts.latitude, lon=opts.longitude, sign=None)
res = api.execute_request(req)

et = ET.parse(res)

for pl in et.findall(".//place") :

    if opts.verbose :
        print pl.attrib['woeid']
        print pl.attrib['place_url']
    else :
        print pl.attrib['woeid']
