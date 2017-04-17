import chanutils.torrent
import cherrypy
from chanutils import select_all, select_one, get_attr, post_doc
from chanutils import get_doc, get_json, series_season_episode
from chanutils import get_text, get_text_content, replace_entity, byte_size
from playitem import TorrentPlayItem, ShowMoreItem, PlayItemList

_BASE_URL = "http://www.shanaproject.com"
_SEARCH_URL = _BASE_URL + "/search/?title="

_FEEDLIST = [
  {'title':'Latest', 'url':'https://www.shanaproject.com/'},
  {'title': 'Season Shows', 'url':'http://www.shanaproject.com/season/list/?sort=date'},
  {'title':'My Shows', 'url':'http://www.shanaproject.com/user/pseudoanime/'},
]

def name():
  return 'Shana Project'

def image():
  return 'icon.png'

def description():
  return "Shana Project Channel (<a target='_blank' href='https://www.shanaproject.com/'>https://www.shanaproject.com/</a>)."

def feedlist():
  return _FEEDLIST

def feed(idx):
  doc = get_doc(_FEEDLIST[idx]['url'], proxy=True)
  if idx > 0:
    return _extract_showlist(doc)
  else:
    return _extract_html(doc)

def search(q):
  q = q.replace(' ', '-')
  doc = get_doc(_SEARCH_URL + q, proxy=True)
  return _extract_html(doc)

def showmore(show_url):
  doc = get_doc(_BASE_URL + show_url, proxy=True)
  return _extract_html(doc)

def _extract_showlist(doc):
	rtree = select_all(doc, 'tr[class="follow_list_row"]')
	img = None
	results = PlayItemList()
	if (rtree is None or len(rtree)==0):
		rtree = select_all(doc, 'div[class="header_display_box_info"]')
		for l in rtree:
			el = select_one(l, 'span[class="header_info_block"]')
			title = get_text_content(el)
			url = get_attr(select_one(el, 'a'), 'href')
			item = ShowMoreItem(title, None, url, None)
			results.add(item)
	else:
	  for l in rtree:
		el = select_one(l, 'td:nth-child(1)')
		title = get_text_content(el)
		url = get_attr(select_one(el, 'a'), 'href')
		item = ShowMoreItem(title, None, url, None)
		results.add(item)
	return results

def _extract_html(doc):
  rtree = select_all(doc, 'div[class="release_block"]')
  results = PlayItemList()
  count = 0
  for l in rtree:
	if count<2:
		count = count+1
		continue
	else:	
		par = select_one(l, 'div:nth-child(1)')
		el = select_one(par, 'span[class="release_profile"]')
		release_profile = get_text(el)
		if (release_profile is None or len(release_profile)==0):
			release_profile = "SD"
		el = select_one(par, 'a')	
		episode_name = get_text(el)
		
		el = select_one(par, 'div[class="release_subber"]')
		subber= get_text_content(select_one(el, 'div:nth-child(1)'))
		if len(subber)>0:
			subber = "[" + subber + "] "
		el = select_one(par, 'div[class="release_episode"]')
		episode = get_text_content(el)
		title = subber + episode_name + " - " + episode + " [" +release_profile + "]"
		img = '/img/icons/film.svg'
		el = select_one(l, 'a[type="application/x-bittorrent"]')
		url = "http://www.shanaproject.com/" + get_attr(el, 'href')
		#if url is None:
		  #continue
		#subs = series_season_episode(title)
		size = get_text(select_one(par, 'div[class="release_size release_last"]'))	
		subs=None
		subtitle = chanutils.torrent.subtitle(size, None, None)
		results.add(TorrentPlayItem(title, None,url,subtitle, subs=subs))
  return results

def _extract_show(data):
  results = PlayItemList()
  img = data['images']['poster']
  series = data['title']
  rtree = data['episodes'] 
  for r in rtree:
    title = r['title']
    url = r['torrents']['0']['url']
    subtitle = "Season: " + str(r['season']) + ", Episode: " + str(r['episode'])
    synopsis = r['overview']
    subs = {'series':series, 'season':r['season'], 
            'episode':r['episode']}
    results.add(TorrentPlayItem(title, img, url, subtitle, synopsis, subs=subs))
  return results
