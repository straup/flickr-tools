#!/usr/bin/env python

# THIS ONE MAY NOT WORK AS ADVERTISED YET

import Flickr.API
import elementtree.ElementTree as ET
import os.path

import iso8601
import time
import datetime

class clustr :

    def __init__ (self, cfg) :

        key = cfg.get('flickr', 'api_key')
        secret = None

        self.api = Flickr.API.API(key, secret)
        self.cfg = cfg
        
    #
    
    def points_for_nearby (self, lat, lon, who='everyone', when='recent', sort='mostrecent', contacts=None) :

        args = {'lat':lat, 'lon':lon, 'radius':1,
                'has_geo':1, 'extras':'geo',
                'per_page':250}
        
        # whose nearby photos fetch
        
        if who != 'everyone':
            args['user_id'] = who

            if contacts :
                args['contacts'] = contacts

        # sort nearby photos like this...
        
        if sort == 'distance' :
            pass
        elif sort == 'interestingness' :
            args['sort'] = 'interestingness-desc'
        else :
            args['sort'] = 'date-posted-desc'
        
        # fetch nearby photos from when

        if type(when) == "<type 'datetime.datetime'>" :

            offset = datetime.timedelta(days=7)
            before = when - offset
            after = when + offset
            
            args['min_upload_date'] = int(time.mktime(before.timetuple()))
            args['min_upload_date'] = int(time.mktime(after.timetuple()))

        elif when == 'alltime' :

            then = iso8601.parse_date("1970-01-01T00:00:00Z")
            today = datetime.datetime.now()
            
            args['min_upload_date'] = int(time.mktime(then.timetuple()))
            args['max_upload_date'] = int(time.mktime(today.timetuple()))
            
        else :
            
            # recently

            today = datetime.datetime.now()
            then = today - datetime.timedelta(days=30)
            
            args['min_upload_date'] = int(time.mktime(then.timetuple()))
            args['max_upload_date'] = int(time.mktime(today.timetuple()))

        #
        
        dumpfile = "nearby-%s-%s-%s.txt" % (who, when, sort)
        
        current_page = 1
        num_pages = None

        try :
            fh = open(dumpfile, "w")
        except Exception, e :
            print "failed to open %s for writing, %s" % (dumpfile, e)
            return False
        
        while not num_pages or current_page < num_pages :

            # print "crunching page %s of %s" % (current_page, num_pages)

            args['page'] = current_page
            res = self.api.execute_method(method='flickr.photos.search', args=args, sign=False)

            tree = ET.parse(res)
            rsp = tree.getroot()

            # print ET.tostring(rsp)
            
            err = rsp.find("err")
    
            if err != None :
                print err.attrib['msg']
                return False
    
            if not num_pages :
                num_pages = int(rsp.find('photos').attrib['pages'])

            if num_pages == 0 :
                break
    
            for ph in rsp.findall('.//photo') :

                lat = float(ph.attrib['latitude'])
                lon = float(ph.attrib['longitude'])

                if lon == 0.0 and lat == 0.0 :
                    continue
        
                ln = "%s\t%s\t%s" % ('nearby', lon, lat)
                fh.write(ln + "\n")

            current_page += 1

        fh.close()
        return True
    
if __name__ == '__main__' :

    import optparse
    import ConfigParser

    # http://www.flickr.com/photos/kellan/3353411827/nearby?show=thumb&fromfilter=1&by=everyone&taken=alltime&sort=distance
    # 30.2648, -97.7438
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
    parser.add_option("--latitude", dest="lat", help="", default=30.2648)
    parser.add_option("--longitude", dest="lon", help="", default=-97.7438)    
    parser.add_option("-o", "--outdir", dest="outdir", help="the directory to write clustr input file ", default=None)            
    parser.add_option("--who", dest="who", help="", default='everyone')
    parser.add_option("--when", dest="when", help="", default='recent')
    parser.add_option("--sort", dest="sort", help="", default='mostrecent')
    
    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)
    
    cl = clustr(cfg)
    cl.points_for_nearby(opts.lat, opts.lon, opts.who, opts.when, opts.sort)
