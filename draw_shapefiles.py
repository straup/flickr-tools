#!/usr/bin/env python
# -*-python-*-

import sys
import optparse
import ConfigParser
import types

print "Hey! This won't work yet because a new version of modestMMarkers hasn't been released yet."
sys.exit()

try :
    import Flickr.API
    import elementtree.ElementTree as ET
    import ModestMaps
    import modestMMarkers
    import cairo
except Exception, e :
    print "Hrm. It looks like you're missing one or more dependencies: %s" % e
    sys.exit()
    
class Shapefiles :

    def __init__ (self, cfg) :

        key = cfg.get('flickr', 'api_key')
        secret = None

        self.api = Flickr.API.API(key, secret)
        self.mm_img = None

    def calculate_bbox_for_points (self, points) :

        sw_lat = None
        sw_lon = None
        ne_lat = None
        ne_lon = None

        for pt in points :

                # ugh...
                
                if type(pt) == types.DictType :
                        if pt.has_key('lat') :
                                lat = pt['lat']
                                lon = pt['lon']                                
                        else :
                                lat = pt['latitude']
                                lon = pt['longitude']

                elif type(pt) == types.ListType :
                        lat = pt[0]
                        lon = pt[1]
                elif type(pt) == types.TupleType :
                        lat = pt[0]
                        lon = pt[1]                        
                else :
                        continue

                #
                
                if not sw_lat or lat < sw_lat :
                        sw_lat = lat
                
                if not sw_lon or lon < sw_lon :
                        sw_lon = lon
                        
                if not ne_lat or lat > ne_lat :
                        ne_lat = lat

                if not ne_lon or lon > ne_lon :
                        ne_lon = lon

        return (sw_lat,sw_lon,ne_lat,ne_lon)
        
    def munge_place (self, et) :

        polys = []
        allpoints = []

        for poly in et.findall(".//polyline") :
            points = []        

            if not poly.text :
                continue
        
            for coord in poly.text.split(" ") :
                pair = coord.split(",")
                lat = float(pair[0])
                lon = float(pair[1])
                
                points.append({'latitude':lat, 'longitude':lon})
                allpoints.append({'lat':lat, 'lon':lon})
            
            polys.append(points)

        return (polys, allpoints)

    def draw (self, **kwargs) :

        polys = []
        donuts = []
        children = []
        
        # Fetch the current shapefile
    
        req = Flickr.API.Request(method='flickr.places.getInfo', woe_id=kwargs['woeid'], sign=False)
        res = self.api.execute_request(req)

        (polys, allpoints) = self.munge_place(ET.parse(res))

        # Fetch donut hole shapes
        
        if opts.donuts :
            req = Flickr.API.Request(method='flickr.places.getShapeHistory', woe_id=kwargs['woeid'], sign=False)
            res = self.api.execute_request(req)

            et = ET.parse(res)
    
            for shp in et.findall(".//shape") :

                if shp.attrib['is_donuthole'] == '1' :
                    (donuts, ignore) = self.munge_place(shp)
                    break

        # Fetch children
        
        if opts.children :
            req = Flickr.API.Request(method='flickr.places.getChildrenWithPhotosPublic', woe_id=kwargs['woeid'], sign=False)
            res = self.api.execute_request(req)

            et = ET.parse(res)
        
            for pl in et.findall(".//place") :
                woeid = pl.attrib['woeid']
            
                subreq = Flickr.API.Request(method='flickr.places.getInfo', woe_id=woeid)
                subres = self.api.execute_request(subreq)

                (child_polys, child_points) = self.munge_place(ET.parse(subres))
                
                if len(child_polys) > 0 :
                    children.append(child_polys)

        # Draw the map

        bbox = self.calculate_bbox_for_points(allpoints)
        dims = ModestMaps.Core.Point(int(kwargs['width']), int(kwargs['height']))
        sw = ModestMaps.Geo.Location(bbox[0], bbox[1])
        ne = ModestMaps.Geo.Location(bbox[2], bbox[3])
    
        provider = ModestMaps.builtinProviders[kwargs['provider']]()
        
        mm_obj = ModestMaps.mapByExtent(provider, sw, ne, dims)
        mm_img = mm_obj.draw()
    
        # Draw the shapes

        markers = modestMMarkers.modestMMarkers(mm_obj)
        mm_img = markers.draw_polylines(mm_img, polys)
        
        if len(donuts) :
            mm_img = markers.draw_polylines(mm_img, donuts, colour=(.005, 0, 1))
        
        if len(children) :
            for ch in children :
                mm_img = markers.draw_polylines(mm_img, ch, colour=(255,255,255), no_fill=True)

        self.mm_img = mm_img

        
    def save (self, out) :
        self.mm_img.save(out)
    
    #

if __name__ == '__main__' :

    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="The path to an ini config file with your Flickr API key")
    parser.add_option("-w", "--woeid", dest="woeid", help="The WOE ID whose shapes you want to draw")    
    parser.add_option("-o", "--out", dest="out", help="The path where the final PNG image should be created")
    parser.add_option("-P", "--provider", dest="provider", help="The name of the ModestMaps tile provider to use", default='OPEN_STREET_MAP')
    parser.add_option("-H", "--height", dest="height", help="Image height (in pixels)", default=1024)
    parser.add_option("-W", "--width", dest="width", help="Image width (in pixels)", default=1024)
    parser.add_option("-C", "--children", dest="children", help="Draw the child shapefiles for WOE ID too", default=None, action='store_true')
    parser.add_option("-D", "--donuts", dest="donuts", help="Draw the donut hole shapefiles for WOE ID too", default=None, action='store_true')    

    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    shp = Shapefiles(cfg)
    shp.draw(woeid=opts.woeid, provider=opts.provider, height=opts.height, width=opts.width, children=opts.children, donuts=opts.donuts)
    shp.save(opts.out)

    sys.exit()
