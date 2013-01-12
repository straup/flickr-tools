#!/usr/bin/env python

# http://opencv.willowgarage.com/wiki/Mac_OS_X_OpenCV_Port
# http://astrobeano.blogspot.com/2012/02/webcam-capture-with-python-on-mac-os-x.html

import sys
import time
import logging
import os.path
import tempfile
import re
import subprocess
import logging

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

    def upload(self, path, permissions):

        photo = open(path, 'rb')

        key = self.cfg.get('flickr', 'api_key')
        secret = self.cfg.get('flickr', 'api_secret')
        token = self.cfg.get('flickr', 'auth_token')

        args = {
            'auth_token': token,
            'photo': photo
            }

        # TO DO: titles, tags?

        if permissions == 'public':
            args['is_public'] = '1'
        elif permissions == 'private':
            args['is_public'] = '0'
        elif permissions == 'fr':
            args['is_public'] = '0'
            args['is_friend'] = '1'
            args['is_family'] = '0'
        elif permissions == 'fa':
            args['is_public'] = '0'
            args['is_friend'] = '0'
            args['is_family'] = '1'
        elif permissions == 'ff':
            args['is_public'] = '0'
            args['is_friend'] = '1'
            args['is_family'] = '1'
        else:
            pass

        api = Flickr.API.API(key, secret)

        req = Flickr.API.Request("http://api.flickr.com/services/upload", **args)
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
    parser.add_option("-p", "--permissions", dest="permissions", help="...", default=None)
    parser.add_option("-f", "--filtr", dest="filtr", help="The path to the filtr application", default=None)
    parser.add_option("-r", "--recipe", dest="recipe", help="The name of the filtr to apply", default='filtr')

    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    wc = webcam(cfg)

    path = wc.capture()

    if opts.filtr:

        tmp = tempfile.gettempdir()
        now = int(time.time())

        fname = "%s-%s.jpg" % (now, opts.recipe)
        filtr_path = os.path.join(tmp, fname)

        filtr = os.path.join(opts.filtr, 'recipes', opts.recipe)
        filtr = os.path.realpath(filtr)

        subprocess.check_call([filtr, path, filtr_path])
        os.rename(filtr_path, path)

    photoid = wc.upload(path, opts.permissions)

    print photoid
