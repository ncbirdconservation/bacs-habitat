# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# focal_habitat_landfire.py
# Description: 
# INPUT habitat raster
# OUTPUT focal sum of cells using mask
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
# from arcpy import env
# from arcpy.sa import *
import os
import sys


def main():

	#set all switches to false
	switch={"no_overwrite":False}
	#set switch values based on passed arguments
	for arg in sys.argv[1:]: 
		print arg + ' running...'
		switch[arg] = True

	if switch["no_overwrite"]: arcpy.env.overwriteOutput = False
	else: arcpy.env.overwriteOutput = True
	
	# Check out any necessary licenses
	arcpy.CheckOutExtension("spatial")

	# Local & environment variables:
	nl = "\n"
	rootdir = os.path.dirname(__file__)
	ws = rootdir + '\\' + 'landfire_habitat_analysis.gdb'
	arcpy.env.workspace = ws

	#mask all analysis to bacs_mask
	# arcpy.env.mask = 'bacs_mask_poly'
	analysis_mask = 'bacs_mask_poly'
	
	bacs_obs_out = open(rootdir + "\\bacsobsout.csv",'w')
	bacs_nodet_out = open(rootdir + "\\bacsnodetout.csv",'w')
	random_out = open(rootdir + "\\randomout.csv",'w')

	# habitat_raster = ws + "\\us_120evt"
	habitat_input_raster = ws + "\\us_120evt"
	bacs_mask = "bacs_mask"
	
	#create new raster with only mask data
	habitat_raster_mask = arcpy.sa.ExtractByMask(habitat_input_raster, analysis_mask)
	habitat_raster_mask.save("habitat_raster")
	habitat_raster = "habitat_raster"
	# habitat_raster = habitat_input_raster
	# arcpy.BuildRasterAttributeTable_management(habitat_raster,"Overwrite")
	
	bacs_obs = "bacs_obs" #point layer of bacs detections
	bacs_nodet = "bacs_nodet" #point layer of bacs non-detections
	random = "random_points" #point layer of bacs non-detections
	bacs_obs_results = {}
	bacs_nodet_results = {}
	random_results = {}
	
	#dimensions for focal sample
	focal_x = 7
	focal_y = 7

	# retrive all habitat types in masked layer - will be used to iterate through and extract focal sums
	outLFattr = open(rootdir + "\\" + 'landfire_attributes.csv','w')
	habitats = {}
	hab_headers = []

	attr = ['OBJECTID','VALUE','COUNT','CLASSNAME']
	header = ",".join(attr)
	outLFattr.write(header + nl)  

	currObj = arcpy.da.SearchCursor(habitat_raster, attr)
	for row in currObj:  
		if row:
			rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
			outLFattr.write(",".join(rowvals) + nl)  
			habitats[int(rowvals[1])] = rowvals[3]
	outLFattr.close()  
	
	#setup bacs_obs results
	bacs_obs_attr = ['OBJECTID','X','Y']
	currObj = arcpy.da.SearchCursor(bacs_obs, bacs_obs_attr)
	for row in currObj:  
		if row:
			rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
			bacs_obs_results[int(rowvals[0])] = rowvals[1:]
	
	#setup bacs_nodet results
	bacs_nodet_attr = ['OBJECTID','X','Y']
	currObj = arcpy.da.SearchCursor(bacs_nodet, bacs_nodet_attr)
	for row in currObj:  
		if row:
			rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
			bacs_nodet_results[int(rowvals[0])] = rowvals[1:]
	
	#setup random point results
	random_attr = ['OID','X','Y']
	currObj = arcpy.da.SearchCursor(random, random_attr)
	for row in currObj:  
		if row:
			rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
			random_results[int(rowvals[0])] = rowvals[1:]
	
	# print str(habitats)


	############
	#habitat types list retrieved - iterate through process  to extract focal sums for each habitat type
	counter = 1
	numhab = len(habitats.keys())
	
	print "-- " + str(numhab) + ' habitats identified' + nl

	for key, hab in habitats.iteritems():
	
		# if counter >5: break
		# key = 3195
		hab_headers.append(str(key))
		print str(hab_headers)
		lfhabfocal = "lf" + str(key) + "focal"
		print nl + "-------------------------------------------------------------------------------" + nl + "processing " + habitats[key] + nl + " (#" + str(key) + " - " + str(counter) + " of " + str(numhab) + ")"+ nl

		# Process: Extract by Attributes
		# lfhab = arcpy.gp.ExtractByAttributes_sa(habitat_raster, "VALUE =" + str(key))
		whereClause = "VALUE <> " + str(key)
		lfhab = arcpy.sa.SetNull(habitat_raster, 1,whereClause) #create raster with 1 for selected habitat, NoData for else
		print "--completed extract by attributes"

		# Process: Focal Statistics
		neighborhood = arcpy.sa.NbrRectangle(focal_x, focal_y, "CELL")
		lfhabfocal = arcpy.sa.FocalStatistics(lfhab, neighborhood, "SUM", "DATA")
		lfhabfocal.save("focalstatout")
		print "--completed focal statistics"

		
		##########################################################
		#extract values for cells under points where bacs detected
		arcpy.sa.Sample(lfhabfocal, bacs_obs, rootdir + "\\bacsobsfocal" + str(key), "NEAREST")
		#loop through resuts, add to bacs_obs_results
		# fieldList = arcpy.ListFields(rootdir + "\\bacsobsfocal" + str(key))
		# for field in fieldList:
			# print("{0} is a type of {1} with a length of {2}".format(field.name, field.type, field.length)) 
		fieldList = ['BACS_OBS','X','Y','FOCALSTATOUT']
		currObj = arcpy.da.SearchCursor(rootdir + "\\bacsobsfocal" + str(key), fieldList)
		for row in currObj:  
			if row:
				# print row
				rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
				bacs_obs_results[int(rowvals[0])].append(rowvals[-1])

		#get focal stats and save to file

		print "--completed bacs obs sample"

		##########################################################
		#extract values for cells under points where bacs NOT detected
		arcpy.sa.Sample(lfhabfocal, bacs_nodet, rootdir + "\\bacsnodetfocal" + str(key), "NEAREST")
		#loop through resuts, add to bacs_obs_results
		# fieldList = arcpy.ListFields(rootdir + "\\bacsnodetfocal" + str(key))
		# for field in fieldList:
			# print("{0} is a type of {1} with a length of {2}".format(field.name, field.type, field.length)) 
		fieldList = ['BACS_NODET','X','Y','FOCALSTATOUT']
		currObj = arcpy.da.SearchCursor(rootdir + "\\bacsnodetfocal" + str(key), fieldList)
		for row in currObj:  
			if row:
				rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
				bacs_nodet_results[int(rowvals[0])].append(rowvals[-1])
		counter +=1
		print "--completed bacs nodet sample"
		
		##########################################################
		#extract values for cells under random points
		arcpy.sa.Sample(lfhabfocal, random, rootdir + "\\randomfocal" + str(key), "NEAREST")
		#loop through resuts, add to bacs_obs_results
		# fieldList = arcpy.ListFields(rootdir + "\\bacsnodetfocal" + str(key))
		# for field in fieldList:
			# print("{0} is a type of {1} with a length of {2}".format(field.name, field.type, field.length)) 
		fieldList = ['RANDOM_POINTS','X','Y','FOCALSTATOUT']
		currObj = arcpy.da.SearchCursor(rootdir + "\\randomfocal" + str(key), fieldList)
		for row in currObj:  
			if row:
				rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
				random_results[int(rowvals[0])].append(rowvals[-1])
		counter +=1
		print "--completed random sample"
		
	##########################################################
	#save all data to csv file
	print nl + '==============================================' + nl + 'save data to text files' + nl
	print 'headers:' + nl + ",".join(['ID','X','Y'] + hab_headers) +nl
	bacs_obs_out.write(",".join(['ID','X','Y'] + hab_headers) + nl)
	for k,v in bacs_obs_results.iteritems(): bacs_obs_out.write(",".join([str(k)] + v)+nl)
	print '--output bacs obs' + nl

	##########################################################
	#save all nodet data to csv file
	bacs_nodet_out.write(",".join(['ID','X','Y'] + hab_headers)+nl)
	for k,v in bacs_nodet_results.iteritems(): bacs_nodet_out.write(",".join([str(k)] + v)+nl)
	print '--output bacs no det' + nl
	
	##########################################################
	#save all random data to csv file
	random_out.write(",".join(['ID','X','Y'] + hab_headers)+nl)
	for k,v in random_results.iteritems(): random_out.write(",".join([str(k)] + v)+nl)
	print '--output random' + nl
	
		
if __name__ == "__main__":
	main()