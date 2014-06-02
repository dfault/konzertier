import requests
import logging
import json

API_KEY = "cc3c95355c82c7af6ef7d51e7f24c7d8" 

format_string = '%(levelname)s %(module)s.%(funcName)s [%(lineno)s]: %(message)s'
logging.basicConfig(format=format_string)
log = logging.getLogger(__name__)

available_methods = ['getevents', 'getsimilar']

class LastFmApi(object):

    def __init__(self, method):
        if method not in available_methods:
            raise Exception('Method %s not available' % method)

        self.method = method
        # build query URL
        base_url = 'http://ws.audioscrobbler.com/2.0/'
        api_url = '?method=artist.%s' % method
        query_url = '&artist=%s&api_key=%s&format=json'
        self.full_url = base_url + api_url + query_url

        log.debug('initialized LastFmApi for method %s' % method)

    def request(self, artist_name):
        '''perform request to last.fm API for given artist'''

        log.debug('request %s for artist %s' % (self.method, artist_name))

        # send request to last.fm
        r = requests.get(self.full_url % (artist_name, API_KEY))
        if r.status_code != 200:
            log.error('artist: %s, status %s' % (artist_name, r.status_code))
            return {'events': []}
 
        # check if artist is valid
        json_dict = r.json()
        if 'error' in json_dict:
            log.error('problem with artist %s: %s' % (artist_name, json_dict))
            return {'events': []}

        return json_dict



