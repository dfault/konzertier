import pickle
import optparse
import logging

import htmlmaker
import concert
import artist
import lastfmapi

format_string = '%(levelname)s %(module)s.%(funcName)s [%(lineno)s]: %(message)s'
logging.basicConfig(format=format_string)
log = logging.getLogger(__name__)

def get_events(opts):
    artists = artist.read_artist_list()
    # include similar artists
    similar_artists = artist.read_similar_artist_list(3)
    artists.extend([s for s in similar_artists.keys() if s not in artists])
    api = lastfmapi.LastFmApi('getevents')
    concerts_dict = {}
    counter = 0
    for a in artists:
        concerts = concert.get_concerts(api, a, (opts.geo_lat, opts.geo_long), opts.city, opts.country)
        similar = similar_artists.get(a,[])
        for c in concerts:
            c.similar_artists = similar
            d = int(c.date.strftime("%Y%m%d"))
            concerts_dict.setdefault((d,a), []).append(c)
            counter += 1
        # break if limit is exceeded
        if counter > opts.limit:
            break

    with open('concerts_dict.dat', 'wb') as f:
        pickle.dump(concerts_dict, f)
        
def create_page(opts):
    concerts_dict = None
    with open('concerts_dict.dat') as f:
        concerts_dict = pickle.load(f)
    htmlmaker.make_html(concerts_dict, './page.html')

def get_similar_artists_list(opts):
    artists = artist.read_artist_list()
    api = lastfmapi.LastFmApi('getsimilar')
   
    all_similars = {}
    counter = 0
    for a in artists:
        similar_artist = artist.get_similar_artist_list(api, a)
        dict_entry = {s:a for s in similar_artist}
        for sim, orig in dict_entry.items():
            all_similars.setdefault(sim, []).append(a)
        counter += 1
        if counter > opts.limit:
            break

    with open('similar_artists.json', 'wb') as f:
        import json
        json.dump(all_similars, f)
    

if __name__ == '__main__':

    BCN = (41.368858, 2.156721)
    
    parser = optparse.OptionParser()
    parser.add_option('-m', '--mode', dest='mode',
        help='0: scan artist list in path, 1: retrieve events, 2: create webpage, 3: get similar artists')
    parser.add_option('-p','--path', dest='path',
        help='path to mp3 library')
    parser.add_option('-f','--file', dest='filename',
        help='filename to load artist/concert list')
    parser.add_option('-l', dest='limit', type='int', default=10000,
        help='limits the number of events, artists, etc.')
    parser.add_option('-c', dest='city', default='Barcelona',
        help='city you are located at')
    parser.add_option('-C', dest='country', default='Spain',
        help='country you are located at')
    parser.add_option('--long', dest='geo_long', default=None, type='float',
        help='longitude of your location')
    parser.add_option('--lat', dest='geo_lat', default=None, type='float',
        help='lattidue of your location')

    (opts, args) = parser.parse_args()

    process = {
        '0': artist.get_artist_list,
        '1': get_events,
        '2': create_page,
        '3': get_similar_artists_list
    }

    process[opts.mode](opts)
       
