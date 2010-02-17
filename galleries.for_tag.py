#!/usr/bin/env python

import optparse
import ConfigParser
import Flickr.API
import elementtree.ElementTree as ET

parser = optparse.OptionParser()
parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
parser.add_option("-t", "--tag", dest="tag", help="")

(opts, args) = parser.parse_args()

cfg = ConfigParser.ConfigParser()
cfg.read(opts.config)

apikey=cfg.get('flickr', 'api_key')

api = Flickr.API.API(apikey)
req = Flickr.API.Request(method='flickr.photos.search', tags=opts.tag, in_gallery=1, sign=None)
res = api.execute_request(req)

et = ET.parse(res)

galleries = {}

for ph in et.findall('//photo'):
    id = ph.attrib['id']

    req = Flickr.API.Request(method='flickr.galleries.getListForPhoto', photo_id=id)
    res = api.execute_request(req)
    et = ET.parse(res)

    for g in et.findall('//gallery'):
        title = g.find('title').text

        galleries[ title ] = g.attrib['url']

for name, url in galleries.items():
    print "%s (%s)" % (url, name)
