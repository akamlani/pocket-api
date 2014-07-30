import json
import requests
import pprint
import webbrowser

import optparse
from optparse import OptionParser


# Pocket Specific APIs
BASE_URL = "https://getpocket.com/v3/"
REQ_TOKEN_URL = BASE_URL + "oauth/request"
ACCESS_TOKEN_URL = BASE_URL + "oauth/authorize"
GET_URL = BASE_URL + "get"

TAG_PREFIX = "server::"
TAG_TOKEN_LEN = 2
CATEGORY_TOKEN_LEN = 3


headers = {'Content-Type' : 'application/json; charset=UTF-8','X-Accept': 'application/json'}
redirect_uri = 'pocketapp1234:authorizationFinished'

def get_request_token():
	req_token_data = {'consumer_key': consumer_key, 'redirect_uri': redirect_uri}
	response = requests.post(REQ_TOKEN_URL, data=json.dumps(req_token_data), headers=headers)
	data = json.loads(response.content)
	code = str(data['code'])
	return code	

def authorize(code):
	auth_url = 'https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s' % (code, redirect_uri)
	webbrowser.open(auth_url, new=0)
	raw_input('Authorize the app url %s and press enter:\n' % auth_url)

def get_access_token(consumer_key, code):
	access_token_data = {'consumer_key': consumer_key, 'code': code}
	response = requests.post(ACCESS_TOKEN_URL, data=json.dumps(access_token_data), headers=headers)
	data = json.loads(response.content)
	access_token = str(data['access_token'])
	return access_token	

def get_articles(consumer_key, access_token):
	get_data = {'consumer_key': consumer_key, 'access_token': access_token,
				'contentType': 'article', 'state': 'all',
				'detailType': 'complete', 'sort': 'newest',
				'tag': TAG_PREFIX}
	response = requests.post(GET_URL, data=json.dumps(get_data), headers=headers)
	data = json.loads(response.content)
	#pprint.pprint(data)
	return data

def process_articles(data):
	articles = []
	for key in data['list']: 
		tags = []; tag_name = "";
		categories = []; cat_name = "";
		pocket_record = data['list'][key]
		# get all tags and strip 'webserver::' prepended header
		for idx in pocket_record['tags']: 
			tag_vector = pocket_record['tags'][idx]['tag']
			tag_vector = tag_vector.split("::")
			if(len(tag_vector) == CATEGORY_TOKEN_LEN): 
				cat_name = str(tag_vector[2]);
				categories.append(cat_name)
			elif((len(tag_vector) == TAG_TOKEN_LEN) and (tag_vector[1] != "")):
				tag_name = str(tag_vector[1]);
				tags.append(tag_name)	
		# create record
		record = {'title': pocket_record['resolved_title'], 
				  'url': pocket_record['resolved_url'],
				  'tags': tags,
				  'categories': categories}
		# add to dictionary
		articles.append(record)
	pprint.pprint(articles)	
	return articles



if __name__ == "__main__":

	parser = OptionParser()
	desc="Pocket-Api Python Articles to News AutoReel"
	parser = optparse.OptionParser(description=desc, usage="usage: %prog [options] filename", version="%prog version 1.0")
	parser.add_option('-k', '--key', help='consumer key,default=""', action='store', dest="consumer_key", default="", metavar='<CONSUMER_KEY>')
	(args, opts) = parser.parse_args()
	consumer_key = args.consumer_key
	
	# request token
	code = get_request_token()
	# authorization url
	authorize(code)
	# convert to access token
	access_token = get_access_token(consumer_key, code)
	# retrieve articles
	data = get_articles(consumer_key, access_token)
	# process articles
	articles = process_articles(data)
	# write articles to json format file
	articles_vector = ({"articles": articles, "headline": "News AutoReel"})
	with open('data_sources.json', 'w') as f: 
		json.dump(articles_vector, f, indent = 4)

