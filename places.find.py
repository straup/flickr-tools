#!/usr/bin/env python

import optparse
import ConfigParser
import Flickr.API
import elementtree.ElementTree as ET
    
parser = optparse.OptionParser()
parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
parser.add_option("-p", "--place", dest="place", help="the location to geocode")

(opts, args) = parser.parse_args()

cfg = ConfigParser.ConfigParser()
cfg.read(opts.config)

apikey=cfg.get('flickr', 'api_key')

api = Flickr.API.API(apikey)
req = Flickr.API.Request(method='flickr.places.find', query=opts.place, sign=None)
res = api.execute_request(req)

et = ET.parse(res)

for pl in et.findall(".//place") :
    print "[%s] %s is a %s" % (pl.attrib['woeid'], pl.text, pl.attrib['place_type'])
