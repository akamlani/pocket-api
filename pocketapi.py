import json
import requests
import pprint
import webbrowser


# Pocket Specific APIs
BASE_URL = "https://getpocket.com/v3/"
REQ_TOKEN_URL = BASE_URL + "oauth/request"
ACCESS_TOKEN_URL = BASE_URL + "oauth/authorize"
GET_URL = BASE_URL + "get"


if __name__ == "__main__":
	headers = {'Content-Type' : 'application/json; charset=UTF-8','X-Accept': 'application/json'}
	consumer_key = '30040-a9f9772158c16fa6bc8f936e'
	
	# request token
	redirect_uri = 'pocketapp1234:authorizationFinished'
	req_token_data = {'consumer_key': consumer_key, 'redirect_uri': redirect_uri}
	response = requests.post(REQ_TOKEN_URL, data=json.dumps(req_token_data), headers=headers)
	data = json.loads(response.content)
	code = str(data['code'])
	#print data, len(data)

	# authorization url
	auth_url = 'https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s' % (code, redirect_uri)
	webbrowser.open(auth_url, new=0)
	raw_input('Please open %s in your browser to authorize the app and press enter:' % auth_url)

	# access token
	access_token_data = {'consumer_key': consumer_key, 'code': code}
	response = requests.post(ACCESS_TOKEN_URL, data=json.dumps(access_token_data), headers=headers)
	data = json.loads(response.content)
	access_token = str(data['access_token'])
	#print data, len(data)
	
	# read articles
	get_data = {'consumer_key': consumer_key, 'access_token': access_token,
				'contentType': 'article', 'state': 'all',
				'detailType': 'complete', 'sort': 'newest',
				'tag': "server::"}
	response = requests.post(GET_URL, data=json.dumps(get_data), headers=headers)
	data = json.loads(response.content)
	#pprint.pprint(data)

	# process articles
	articles = []
	for key in data['list']: 
		tags = []; tag_name = "";
		categories = []; cat_name = "";
		pocket_record = data['list'][key]
		# get all tags and strip 'webserver::' prepended header
		for idx in pocket_record['tags']: 
			tag_vector = pocket_record['tags'][idx]['tag']
			tag_vector = tag_vector.split("::")
			if(len(tag_vector) == 3): 
				cat_name = str(tag_vector[2]);
				categories.append(cat_name)
			elif((len(tag_vector) == 2) and (tag_vector[1] != "")):
				tag_name = str(tag_vector[1]);
				tags.append(tag_name)	
		# create record
		record = {'title': pocket_record['resolved_title'], 
				  'url': pocket_record['resolved_url'],
				  'tags': tags,
				  'categories': categories}
		# add to dictionary
		articles.append(record)
	
	articles_vector = ({"articles": articles, "headline": "News AutoReel"})
	with open('data_sources.json', 'w') as f: 
		json.dump(articles_vector, f, indent = 4)

