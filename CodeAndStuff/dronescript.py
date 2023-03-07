from qgis.core import QgsVectorLayer, QgsApplication
from osgeo import gdal
import numpy as np

# Starting a QGIS application
qgishome = r'C:\OSGeo4W64\apps\qgis\\'
app = QgsApplication([], True)
QgsApplication.setPrefixPath(qgishome, True)
QgsApplication.initQgis()

# Loading a vector layer
vlayer = QgsVectorLayer('c:/temp/dronephotos.shp', 'point', 'ogr')
print(vlayer.isValid())

# Loading big raster layer
fileName = 'c:/temp/DSM_LondonCity_1m.tif'
bigraster = gdal.Open(fileName)

r = 200
filepath_tempdsm = 'c:/temp/clipdsm.tif'

# creating empty matrix for testfile
rows = vlayer.featureCount()
cols = 3
matrix = np.zeros((rows, cols))
index = 0
idx = vlayer.dataProvider().fieldNameIndex('Id')

for f in vlayer.getFeatures():
    #print(f.attributes()[idx])
    # accessing x and y for vector point
    x = f.geometry().centroid().asPoint().x()
    y = f.geometry().centroid().asPoint().y()
    #print('x = ' + str(x) + ' and y = ' + str(y))

    # clipping out from big raster
    bbox = (x - r, y + r, x + r, y - r)
    gdal.Translate(filepath_tempdsm, bigraster, projWin=bbox)
    data = gdal.Open(filepath_tempdsm)
    mat = np.array(data.ReadAsArray())
    data = None
    #print(mat.mean())
    #print(mat.max())

    matrix[index, 0] = f.attributes()[idx]
    matrix[index, 1] = mat.mean()
    matrix[index, 2] = mat.max()
    index += 1
    print(matrix)

# save to file
header = 'ID   MEAN   MAX'
numformat = '%d %6.2f %6.2f'
np.savetxt('c:/temp/droneheight.txt', matrix, fmt=numformat, header = header)