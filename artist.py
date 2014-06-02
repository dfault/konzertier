import os
import mutagen.mp3
import logging
import json
import codecs

format_string = '%(levelname)s %(module)s.%(funcName)s [%(lineno)s]: %(message)s'
logging.basicConfig(format=format_string)
log = logging.getLogger(__name__)

def read_similar_artist_list(n_commons):
    similar_artists = {}
    with open('./similar_artists.json') as f:
        similar_artists = json.load(f)
    return {k:v for k,v in similar_artists.items() if len(v) > n_commons}

def read_artist_list():
    out = []
    with codecs.open('./artists_list.csv', 'rb', 'utf8') as f:
        out = [line.rstrip() for line in f]
    return out

def get_artist_list(opts):
    '''return list of artists found in MP3 files at given path (recursively)'''
    artists = set()
    for w in os.walk(opts.path):
        for f in w[2]:
            # for now only mp3 is supported
            if 'mp3' != os.path.basename(f).split('.')[-1]:
                continue

            # try to extract ID3 tag
            tag = None
            try:
                tag = mutagen.mp3.MP3(os.path.join(w[0],f))
            except:
                log.warning('problems with %s' % os.path.join(w[0],f))
                continue
            if tag.tags is None:
                continue
            if 'TPE1' not in tag.tags:
                continue
            
            # add artist to set (message if new)
            artist = tag.tags['TPE1']
            before = len(artists)
            artists.add(artist.text[0])
            if len(artists) > before:
                log.debug('added %s' % artist)

    with open('./artists_list.csv', 'wb') as f:
        for a in artists:
            f.write('%s\n' % a.encode('utf8'))

def get_similar_artist_list(api, artist_name):
    json_dict = api.request(artist_name)

    if 'similarartists' not in json_dict:
        log.warning('no similar artist found for %s' % artist_name)
        return []

    similar_artists = []
    try:
        similar_artists_list = json_dict['similarartists']['artist']
        if type(similar_artists_list) is dict:
            similar_artists = [similar_artists_list['name']]
        else:
            similar_artists = [sim['name'] for sim in similar_artists_list]
    except:
        log.info('use: %s' % json_dict['similarartists']['artist'])
        similar_artists = [json_dict['similarartists']['artist']]
    return similar_artists
    
