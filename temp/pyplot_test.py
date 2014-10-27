#testing pyplot

import numpy as np
import matplotlib.pyplot as pyplot

#import data
rootdir = 'C:/data/@projects/bacs_surveys/analysis/habitat_analysis/'

def create_array (f):
	#import file text, return array of values
	#convert to columns of data
	fr = f.splitlines()
	labels = []
	data = {} #dictionary with labels as keys
	for n,r in enumerate(fr):
		rd = r.split(',')
		if n ==0: #first row, headers
			labels = rd
			for c in labels: data[c] = [] #empty arrays for each column
				
		else:
			for nc,c in enumerate(labels): #cycle through columns, add to arrays
				data[c].append(rd[nc])
				
	return data


def main():
	#import data
	bacsobs = open(rootdir + 'bacsobsout.csv','r').read()
	# bacsnodet = open(rootdir + 'bacsnodetout.csv','r')
	# testout = open(rootdir + 'testout.txt','w')

	
	# labels = np.genfromtxt('bacsobsout.csv',delimiter=',', dtype=str)[:1][0]
	d = create_array(bacsobs)
	npa = np.array([d['3195'],d['3191']], np.dtype(float))
	print str(npa)
	labels = d.keys()
	# data = np.genfromtxt('bacsobsout.csv', delimiter=',')[1::]
	print str(d.keys())
	data = d['3195']
	print str(data)

	fs = 10 #fontsize
	
	fig, axes = pyplot.subplots(nrows=len(data),ncols=1)
	# axes[0,0].boxplot(data)
	pyplot.boxplot(npa)
	pyplot.show()
	# bo = []
	# bnd = []
	
	# pyplot.plot([1,2,3], [1,2,3], 'go-', label='line 1', linewidth=2)
	# pyplot.plot([1,2,3], [1,4,9], 'rs',  label='line 2', linewidth=1)
	# pyplot.axis([0, 4, 0, 10])
	# pyplot.legend()
	# pyplot.show()


		
if __name__ == "__main__":
	main()