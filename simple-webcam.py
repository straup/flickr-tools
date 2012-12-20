#!/usr/bin/env python

# http://opencv.willowgarage.com/wiki/Mac_OS_X_OpenCV_Port
# http://astrobeano.blogspot.com/2012/02/webcam-capture-with-python-on-mac-os-x.html

import sys
import time
import logging
import os.path
import tempfile
import re

import Flickr.API
from xml.dom import minidom

import cv2

class webcam:
    
    def __init__(self, cfg):
        self.cfg = cfg

    def capture(self):

        vidcap = cv2.VideoCapture()
        vidcap.open(0)

        retval, image = vidcap.retrieve()
        vidcap.release()

        now = int(time.time())

        tmp = tempfile.gettempdir()
        fname = "%s.jpg" % now
        path = os.path.join(tmp, fname)

        cv2.imwrite(path, image)
        return path

    def upload(self, path):

        photo = open(path, 'rb')

        key = self.cfg.get('flickr', 'api_key')
        secret = self.cfg.get('flickr', 'api_secret')
        token = self.cfg.get('flickr', 'auth_token')

        api = Flickr.API.API(key, secret)

        req = Flickr.API.Request("http://api.flickr.com/services/upload", auth_token=token, title='test upload', photo=photo)
        rsp = api.execute_request(req, sign=True, encode=Flickr.API.encode_multipart_formdata)

        # seriously why did we never update the photo upload
        # endpoint to return json... (20121220/straup)

        doc = minidom.parseString(rsp.read())
        tag_list = doc.getElementsByTagName('photoid')
        tag = tag_list[0]
        txt = tag.firstChild

        photoid = txt.nodeValue

        os.unlink(path)
        return photoid

if __name__ == '__main__':

    import optparse
    import ConfigParser

    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="The path to an ini config file with your Flickr API key")

    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    wc = webcam(cfg)

    path = wc.capture()
    photoid = wc.upload(path)

    print photoid
