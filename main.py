import matplotlib.pyplot as plt
from sklearn import svm

from get_athletes import get_athletes
from get_athlete_info import log_in, get_athlete_info

def get_data():
	athletes = get_athletes()
	opener = log_in()

	athlete_data = {}

	count_valid = 0
	count_invalid = 0
	total = 0

	for athlete in athletes:
		info = get_athlete_info(opener, athlete['id'])
		athlete_data[athlete['id']] = info

		if 'error' in info:
			count_invalid += 1
		else:
			count_valid += 1

		total += 1
		if total % 50 == 0:
			print '%s %s %s' % (total, count_valid, count_invalid)

	athlete_data = [
			(key, item['10k'], item['year']) 
			for key, item in athlete_data.iteritems()
			if '10k' in item
	]

	return athlete_data

def main():
	data = get_data()

	# remove unnatural values
	ten_k_max = 2 * 60 * 60 # you'd be walking at this pace
	valid_data = [v for v in data if v[1] < ten_k_max]

	max_dist = 7000 
	valid_data = [v for v in valid_data if v[2] < max_dist]

	# split into X-axis and Y-axis values - for easy plotting and model training
	ten_k_times = [i[1] for i in valid_data]
	year_distances = [i[2] for i in valid_data]

	# train SVR model
	clf = svm.SVR(kernel='rbf', C=10000, gamma=0.000003)
	clf.fit([[k] for k in ten_k_times], year_distances) 
	# then get some predictions
	clf_line_x = range(800, 7000)
	clf_line_y = clf.predict([[x] for x in clf_line_x])

	# plot resuls
	plt.scatter(ten_k_times, year_distances, alpha=0.2, marker='.', c='blue')

	me = athlete_data[434554] # my strava user id
	plt.plot([me['10k']], [me['year']], alpha=1, marker='o', c='red')
	
	plt.plot(clf_line_x, clf_line_y, alpha=0.2, marker='.', c='green')

	plt.axis([0, 7200, 0, 7000])
	plt.ylabel('Kilometers ran this year')
	plt.xlabel('10K record in seconds')
	plt.show()