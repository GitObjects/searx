"""
Genius

 @website     https://www.genius.com/
 @provide-api yes (https://docs.genius.com/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content, thumbnail, publishedDate
"""

from json import loads
from urllib.parse import urlencode
from datetime import datetime

# engine dependent config
categories = ['music']
paging = True
language_support = False
page_size = 5

url = 'https://genius.com/api/'
search_url = url + 'search/{index}?{query}&page={pageno}&per_page={page_size}'


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      index='multi',
                                      page_size=page_size,
                                      pageno=params['pageno'])
    return params


def parse_lyric(hit):
    try:
        content = hit['highlights'][0]['value']
    except:
        content = None
    timestamp = hit['result']['lyrics_updated_at']
    result = {'url': hit['result']['url'],
              'title': hit['result']['full_title'],
              'content': content,
              'thumbnail': hit['result']['song_art_image_thumbnail_url'],
              'template': 'videos.html'}
    if timestamp:
        result.update({'publishedDate': datetime.fromtimestamp(timestamp)})
    return result


def parse_artist(hit):
    result = {'url': hit['result']['url'],
              'title': hit['result']['name'],
              'content': None,
              'thumbnail': hit['result']['image_url'],
              'template': 'videos.html'}
    return result


def parse_album(hit):
    result = {'url': hit['result']['url'],
              'title': hit['result']['full_title'],
              'thumbnail': hit['result']['cover_art_url'],
              # 'thumbnail': hit['result']['cover_art_thumbnail_url'],
              'template': 'videos.html'}
    try:
        year = hit['result']['release_date_components']['year']
    except:
        pass
    else:
        if year:
            result.update({'content': 'Released: {}'.format(year)})
    return result


parse = {'lyric': parse_lyric, 'song': parse_lyric, 'artist': parse_artist, 'album': parse_album}


def response(resp):
    results = []
    json = loads(resp.text)
    hits = [hit for section in json['response']['sections'] for hit in section['hits']]
    for hit in hits:
        try:
            func = parse[hit['type']]
        except KeyError:
            continue
        results.append(func(hit))
    return results
