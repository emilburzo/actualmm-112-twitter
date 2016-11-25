#!/usr/bin/env python

import requests
from requests_oauthlib import OAuth1
from lxml import html
from tinydb import TinyDB, Query

############## DEBUG
# import requests
# import logging
#
# # Enabling debugging at http.client level (requests->urllib3->http.client)
# # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # the only thing missing will be the response.body which is not logged.
# try: # for Python 3
#     from http.client import HTTPConnection
# except ImportError:
#     from httplib import HTTPConnection
# HTTPConnection.debuglevel = 1
#
# logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
#
############## DEBUG

db = TinyDB('/tmp/actualmm112.json')

# actualmm
ACTUALMM_PARAMS = {
    'action': 'td_ajax_block',
    'td_atts': '{"custom_title":"Eveniment","header_color":"#e29c04","category_id":"10","td_ajax_filter_type":"td_category_ids_filter","ajax_pagination":"next_prev","limit":5,"class":"td_block_id_2336598469 td_uid_4_57fa53095af9c_rand"}',
    'td_block_id': 'td_uid_4_57fa53095af9c',
    'td_column_number': 2,
    'td_current_page': 1,
    'block_type': 'td_block_1',
    'td_filter_value': '32707'
}

# twitter
TWITTER_UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
AUTH = OAuth1('client_key', 'client_secret',
              'owner_key', 'owner_secret')


def post(title, url):
    if url_exists(url):
        return

    content = title + " " + url

    r = requests.post(TWITTER_UPDATE_URL, data={'status': content}, auth=AUTH)
    r.close()


def fetch():
    # fetch data
    r = requests.post('http://actualmm.ro/wp-admin/admin-ajax.php', data=ACTUALMM_PARAMS)

    # parse HTML
    tree = html.fromstring(r.content.decode('unicode_escape'))

    entries = tree.xpath("//h3[contains(@class, 'entry-title')]")

    return entries

def url_exists(url):
    Link = Query()

    return db.search(Link.link == url)

def persist(url):
    if not url_exists(url):
        db.insert({'link': url})

############

entries = fetch()

for entry in entries:
    a = entry[0]
    link = a.get('href').replace('\\', '')
    title = a.get('title')

    post(title, link)
    persist(link)