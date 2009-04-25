#!/usr/bin/env python

import optparse
import ConfigParser
import Flickr.API
import elementtree.ElementTree as ET
    
parser = optparse.OptionParser()
parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
parser.add_option("-w", "--woeid", dest="woeid", help="the WOE ID to fetch")

(opts, args) = parser.parse_args()

cfg = ConfigParser.ConfigParser()
cfg.read(opts.config)

apikey=cfg.get('flickr', 'api_key')

api = Flickr.API.API(apikey)
req = Flickr.API.Request(method='flickr.places.getInfo', woe_id=opts.woeid, sign=None)
res = api.execute_request(req)

et = ET.parse(res)

print ET.tostring(et.getroot())
