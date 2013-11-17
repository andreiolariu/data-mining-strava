import time

import requests
import simplejson as json

TIME_BT_REQUESTS = 0.5

def get_athletes():
	# taking athletes from http://www.strava.com/challenges/turn-up-the-heat-run
	# there are 17311 athletes registered for that challenge
	total_pages = 17311 / 50

	athletes = []
	for page in range(1, total_pages + 2):
		url = ('http://www.strava.com/challenges/192/details?paging_type='
				'overall&per_page=50&overall_page=%s&overall_male_page=1'
				'&overall_female_page=1&_=1384604957879') % page

		r = requests.get(url)
		data = json.loads(r.text)
		athletes.extend(data['athletes'].values())

		print len(athletes)
		time.sleep(TIME_BT_REQUESTS)
