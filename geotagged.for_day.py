#!/usr/bin/env python

# Usage: geotagged.for_day.py -c ~/.api/flickr.cfg -d '2009-03-24'

import Flickr.API
import elementtree.ElementTree as ET
import os.path
import sys

import time
import iso8601

# http://pypi.python.org/pypi/iso8601

if __name__ == '__main__' :

    import optparse
    import ConfigParser
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
    parser.add_option("-d", "--date", dest="date", help="")
    parser.add_option("-o", "--outdir", dest="outdir", help="the directory to write clustr input file ", default=None)            

    (opts, args) = parser.parse_args()

    #
    
    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    #
    
    key = cfg.get('flickr', 'api_key')
    secret = None
    
    api = Flickr.API.API(key, secret)

    #

    dumpfile = "%s-geotagged.txt" % opts.date

    if opts.outdir :
        dumpfile = os.path.join(opts.outdir, dumpfile)

    try :
        fh = open(dumpfile, "w")
    except Exception, e :
        print "failed to open %s for writing, %s" % (dumpfile, e)
        sys.exit()
    
    #
    
    today = iso8601.parse_date("%sT00:00:00Z" % opts.date)
    today = int(time.mktime(today.timetuple()))

    tomorrow = today + (60 * 60 * 24)
    min_date = today

    #

    total = 0
    
    while min_date < tomorrow :

        max_date = min_date + (60 * 30)
        
        args = {'has_geo':1, 'extras':'geo,'
                'min_upload_date':min_date, 'max_upload_date':max_date,
                'per_page':250}

        current_page = 1
        num_pages = None

        while not num_pages or current_page < num_pages :

            print "%s-%s page %s of %s (%s so far)" % (min_date, max_date, current_page, num_pages, total)
            
            args['page'] = current_page 
            res = api.execute_method(method='flickr.photos.search', args=args, sign=False)

            tree = ET.parse(res)
            rsp = tree.getroot()

            err = rsp.find("err")
    
            if err != None :
                print err.attrib['msg']
                break
    
            if not num_pages :
                num_pages = int(rsp.find('photos').attrib['pages'])

            if num_pages == 0 :
                break
    
            for ph in rsp.findall('.//photo') :

                lat = float(ph.attrib['latitude'])
                lon = float(ph.attrib['longitude'])

                if lon == 0.0 and lat == 0.0 :
                    continue
        
                ln = "%s,%s" % (lon, lat)
                fh.write("%s\n" % ln)
                
                total += 1

            current_page += 1
            
        min_date = max_date

    print "done, wrote %s points" % total
    fh.close()
