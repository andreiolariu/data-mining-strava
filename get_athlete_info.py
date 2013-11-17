import cookielib
import time
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup

from credentials import *

TIME_BT_REQUESTS = 0.5

# authentication code by: https://github.com/loisaidasam/stravalib

def log_in():
	print "Logging in..."
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	f = opener.open('https://www.strava.com/login')
	soup = BeautifulSoup(f.read())

	time.sleep(TIME_BT_REQUESTS)

	utf8 = soup.findAll('input', {'name': 'utf8'})[0].get('value').encode('utf-8')
	token = soup.findAll('input', {'name': 'authenticity_token'})[0].get('value')

	values = {
		'utf8': utf8,
		'authenticity_token': token,
		'email': EMAIL,
		'password': PASSWORD,
	}

	data = urllib.urlencode(values)
	url = 'https://www.strava.com/session'
	response = opener.open(url, data)
	soup = BeautifulSoup(response.read())

	time.sleep(TIME_BT_REQUESTS)
	return opener

def get_athlete_info(opener, athlete_id):
	# without these headers, the request doesn't return anything
	opener.addheaders = [
		('X-Requested-With', 'XMLHttpRequest'),
		('Accept', 
			('text/javascript, application/javascript, application/ecmascript,'
			' application/x-ecmascript')
		),
	]

	url = 'http://www.strava.com/athletes/%s/profile_sidebar_comparison' \
			% athlete_id
	try:
		response = opener.open(url)
	except Exception, e:
		print '%s - %s' % (e, athlete_id)
		return {'error': 'fail5'}

	if response.getcode() != 200:
		raise Exception('Athlete info: %s - %s' % \
				(response.getcode(), response.msg))

	soup = BeautifulSoup(response.read())
	time.sleep(TIME_BT_REQUESTS)

	# find the data we're interested in
	run_info = list(soup.childGenerator())[4]

	# first get the 10k record
	try:
		records = list(run_info.childGenerator())[7]
		records = list(records.childGenerator())[3]
	except:
		return {'error': 'fail1'}

	ten_k = None
	for item in records.childGenerator():
		if '10k' in str(item):
			record = list(item.childGenerator())[3]
			record = record.text 

			# time is in the format 1:02:23 or 45:54
			# convert it to seconds
			splitted = record.split(':')
			try:
				seconds = int(splitted[-1]) + int(splitted[-2]) * 60
			except:
				return {'error': 'fail4'}
			if len(splitted) == 3:
				seconds += int(splitted[0]) * 3600
			ten_k = seconds
			break

	if not ten_k:
		return {'error': 'fail2'}

	# then see if the user was active all year (don't want
	# to include people that just started using strava, since they may
	# have training outsite of strava that would mess the results)
	this_year = list(run_info.childGenerator())[9]
	this_year = list(this_year.childGenerator())[3]
	this_year = list(this_year.childGenerator())[1]
	this_year = list(this_year.childGenerator())[3].text

	all_time = list(run_info.childGenerator())[11]
	all_time = list(all_time.childGenerator())[3]
	all_time = list(all_time.childGenerator())[1]
	all_time = list(all_time.childGenerator())[3].text

	if this_year == all_time:
		return {'error': 'fail3'}

	if 'km' not in this_year:
		raise Exception('weird')
	this_year = float(this_year[:-2].replace(',',''))	

	return {
		'10k': ten_k,
		'year': this_year
	}
