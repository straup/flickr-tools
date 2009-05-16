#!/usr/bin/env python

import Flickr.API
import elementtree.ElementTree as ET
import os.path

class clustr :

    def __init__ (self, cfg) :

        key = cfg.get('flickr', 'api_key')
        secret = None

        self.api = Flickr.API.API(key, secret)
        self.cfg = cfg
        
    #
    
    def points_for_tag (self, tag, **kwargs) :

        dumpfile = "points_%s.txt" % tag

        print kwargs
        
        if kwargs['outdir'] :
            dumpfile = os.path.join(kwargs['outdir'], dumpfile)
        
        current_page = 1
        num_pages = None

        try :
            fh = open(dumpfile, "w")
        except Exception, e :
            print "failed to open %s for writing, %s" % (dumpfile, e)
            return False
        
        while not num_pages or current_page < num_pages :

            # print "crunching page %s of %s" % (current_page, num_pages)

            args = {'tags':tag, 'page':current_page, 'per_page':500, 'has_geo':1, 'extras':'geo'}

            if kwargs['woeid'] :
                args['woe_id'] = kwargs['woeid']
                
            res = self.api.execute_method(method='flickr.photos.search', args=args, sign=False)

            tree = ET.parse(res)
            rsp = tree.getroot()

            err = rsp.find("err")
    
            if err != None :
                print err.attrib['msg']
                return False
    
            if not num_pages :
                num_pages = int(rsp.find('photos').attrib['pages'])
                # print "%s pages to crunch" % num_pages

            if num_pages == 0 :
                break
    
            for ph in rsp.findall('.//photo') :

                lat = float(ph.attrib['latitude'])
                lon = float(ph.attrib['longitude'])

                if lon == 0.0 and lat == 0.0 :
                    continue
        
                ln = "%s\t%s\t%s" % (tag, lon, lat)
                fh.write(ln + "\n")

            current_page += 1

        fh.close()
        return True
    
if __name__ == '__main__' :

    import optparse
    import ConfigParser
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
    parser.add_option("-t", "--tag", dest="tag", help="the tag to clustr-ize")
    parser.add_option("-w", "--woeid", dest="woeid", help="scope the tag search to a specific WOE ID", default=None)    
    parser.add_option("-o", "--outdir", dest="outdir", help="the directory to write clustr input file ", default=None)            

    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    cl = clustr(cfg)
    cl.points_for_tag(opts.tag, woeid=opts.woeid, outdir=opts.outdir)
