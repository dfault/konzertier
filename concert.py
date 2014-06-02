import datetime
import requests
import math
import json
import logging
import string
import os

format_string = '%(levelname)s %(module)s.%(funcName)s [%(lineno)s]: %(message)s'
logging.basicConfig(format=format_string)
log = logging.getLogger(__name__)

class Concert(object):
    '''Representation of a concert'''

    def __init__(self, artist_name, event):
        venue = event['venue']
        self.venue_name = venue['name']
        if len(venue['image'])>2:
            self.venue_image_url = venue['image'][2]['#text']
        self.loc_lat = venue['location']['geo:point']['geo:lat']
        self.loc_lat = None if self.loc_lat == u'' else float(self.loc_lat)
        self.loc_long = venue['location']['geo:point']['geo:long']
        self.loc_long = None if self.loc_long == u'' else float(self.loc_long)
        self.city = venue['location']['city']
        self.postalcode = venue['location']['postalcode']
        self.street = venue['location']['street']
        self.country = venue['location']['country']
        self.title = event['title']
        self.description = event['description']
        self.artist_name = artist_name
        self.similar_artists = []
        self.artist = event['artists']
        self.date = datetime.datetime.strptime(event['startDate'], '%a, %d %b %Y %H:%M:%S')

    def in_reach(self, geo_loc, city, country):
        '''check if a venue is with in reach of coordinates or city/country'''
        def distance(origin, destination):
            '''helper function to calculate distance between coordinates in kilometers'''
            lat1, lon1 = origin
            lat2, lon2 = destination
            radius = 6371 # km
        
            dlat = math.radians(lat2-lat1)
            dlon = math.radians(lon2-lon1)
            a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
                * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = radius * c
            return d

        # check coordinates distance
        if self.loc_lat and self.loc_long and geo_loc[0] and geo_loc[1]:
            dist = distance((self.loc_lat, self.loc_long), (geo_loc[0], geo_loc[1]))
            if dist > 100:
                return False    
        else: # else check city/country
            if self.city.encode('utf8') != city or self.country.encode('utf8') != country:
                return False
        return True

    def to_json(self):
        '''store relevenant information in dictionary (JSON)'''
        out = {
            'Artist': { 
                'headliner': self.artist['headliner'].encode('utf8'), 
                'all': [a.encode('utf8') for a in self.artist['artist']]
            },
            'Venue': self.venue_name.encode('utf8'),
            'Title': self.title.encode('utf8'),
            'Date': self.date.strftime("%d.%m.%Y")
        }
        return out

    def __str__(self):
        out = [
            'Artist: %s (%s)' % (self.artist['headliner'].encode('utf8'), 
                [a.encode('utf8') for a in self.artist['artist']]), 
            'Venue: %s' %(self.venue_name.encode('utf8')), 'Title: %s' % self.title.encode('utf8'),
            'Description: %s' % self.description.encode('utf8'),
            'Date: %s' % self.date.strftime("%d.%m.%Y")]
        return '\n'.join(out)

def get_concerts(api, artist_name, geo_location, city, country):
    '''retrieve concerts from last.fm'''
    concerts = []

    json_dict = None
    if os.path.isfile('./events/%s.json' % artist_name):
        with open('./events/%s.json' % artist_name) as f:
            json_dict = json.load(f)
    else:
        json_dict = api.request(artist_name)
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        out_artistname = ''.join(c for c in artist_name if c in valid_chars)
        with open('./events/%s.json' % out_artistname, 'wb') as f:
            json.dump(json_dict, f)

    # check if any event was found
    if 'event' not in json_dict['events']:
        return concerts

    # store found concerts if in reach
    event_list = json_dict['events']['event']
    if type(event_list) is not list:
        event_list = [event_list]
    for event in event_list:
        concert = Concert(artist_name, event)
        if concert.in_reach(geo_location, city, country):
            concerts.append(concert)

    return concerts


