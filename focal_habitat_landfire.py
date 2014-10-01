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

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Local variables:
nl = "\n"
rootdir = os.path.dirname(__file__)
ws = rootdir + '\\' + 'landfire_habitat_analysis.gdb'
arcpy.env.workspace = ws
arcpy.env.overwriteOutput = True

habitat_raster = "us_120evt"
bacs_mask = "bacs_mask"
bacs_obs = "bacs_obs" #point layer of bacs detections
bacs_nondet = "bacs_nondet" #point layer of bacs non-detections

#dimensions for focal sample
focal_x = 7
focal_y = 7

# get the masked version of the habitat layer
# bacs_hab_mask = arcpy.gp.ExtractByMask_sa(habitat_raster, bacs_mask, "bacs_habitat_mask")
# print arcpy.Exists("bacs_habitat_mask")
# bacs_hab_mask.save(ws + "\\bacs_habitat_mask")
# bacs_hab_mask = "bacs_habitat_mask"

# retrive all habitat types in masked layer - will be used to iterate through and extract focal sums
outLFattr = open(rootdir + "\\" + 'landfire_attributes.csv','w')
habitats = {}

attr = ['OBJECTID','VALUE','COUNT','CLASSNAME']
header = ",".join(attr)
outLFattr.write(header)  

currObj = arcpy.da.SearchCursor(habitat_raster, attr)
for row in currObj:  
	if row:
		rowvals = [str(i).encode('ascii').replace("(","").replace(")","") for i in row]
		outLFattr.write(",".join(rowvals) + nl)  
		habitats[int(rowvals[1])] = rowvals[3]
outLFattr.close()  
# print str(habitats)


############
#habitat types list retrieved - iterate through process  to extract focal sums for each habitat type

# for key, hab in habitats.iteritems():
key = 3195
# lfhab = "lf" + str(key)
# lfhabbin = "lf" + str(key) + "bin"
lfhabfocal = "lf" + str(key) + "focal"
print nl + "-------------------------------------------" + nl + "begun processing " + habitats[key] + nl

# Process: Extract by Attributes
# lfhab = arcpy.gp.ExtractByAttributes_sa(habitat_raster, "VALUE =" + str(key))
whereClause = "VALUE <> " + str(key)
lfhab = arcpy.sa.SetNull(habitat_raster, 1,whereClause) #create raster with 1 for selected habitat, NoData for else
print "--completed extract by attributes"

# Process: Focal Statistics
neighborhood = arcpy.sa.NbrRectangle(focal_x, focal_y, "CELL")
lfhabfocal = arcpy.sa.FocalStatistics(lfhab, neighborhood, "SUM", "DATA")
lfhabfocal.save("focalstatout")
print "--completed focal sample"

#extract values for cells under points where bacs detected
arcpy.sa.Sample(lfhabfocal, bacs_obs, rootdir + "\\testbacsobsfocal.txt", "NEAREST")
print "--completed all"

#get focal stats and save to file

