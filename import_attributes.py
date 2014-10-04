import arcpy

import os

# Local variables:
rootdir = os.path.dirname(__file__)
ws = rootdir + '\\' + 'landfire_habitat_analysis.gdb'

# retrive all landfire habitat types in masked layer
outLFattr = open(rootdir + "\\" + 'landfire_attributes.csv','w')
attr = ['OBJECTID','VALUE','COUNT','CLASSNAME']
raster = 'us_120evt' #landfire layer (unmasked)  
rasloc = ws + os.sep + raster

try:  
	header = ''  
	lstFlds = arcpy.ListFields(rasloc)
	fields = "*" 

	for fld in lstFlds:  
		header += ",{0}".format(fld.name)  
	print header
		
	if len(lstFlds) != 0:  
		outCSV = rootdir + "\\" + 'landfire_attributes.csv' 
		f = open(outCSV,'w')  
		print f
		header = header[1:] + ',RasterName\n'  
		f.write(header)  

		with arcpy.da.SearchCursor(rasloc, fields) as cursor:  
			for row in cursor:
				rowvals = row.replace("(","").replace(")").split(",")
				for n,i in enumerate(attr):
					f.write(str(row) + "," + raster + '\n')  
		f.close()  

except:  
	print raster + " - is not integer or has no attribute table"  
