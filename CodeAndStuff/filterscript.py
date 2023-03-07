from qgis.core import QgsApplication
from osgeo import gdal
import numpy as np
import matplotlib.pylab as plt
from misc import saveraster


# Starting a QGIS application
qgishome = r'C:\OSGeo4W64\apps\qgis\\'
app = QgsApplication([], True)
QgsApplication.setPrefixPath(qgishome, True)
QgsApplication.initQgis()

# Loading biG raster layer
fileName = 'c:/temp/DSM_LondonCity_1m.tif'
bigraster = gdal.Open(fileName)

# Location and radius
x = 284060 # x coordinate in geographical coordinate 
y = 5711750 # y coordinate in geographical coordinate
r = 250

# clip raster
filepath_tempdsm = 'c:/temp/clipdsm.tif'
bbox = (x - r, y + r, x + r, y - r)
gdal.Translate(filepath_tempdsm, bigraster, projWin=bbox)
data = gdal.Open(filepath_tempdsm)
mat = np.array(data.ReadAsArray())
#plt.imshow(mat)
#plt.colorbar()
#plt.show()

# Creating empty raster
col = mat.shape[1]
row = mat.shape[0]
result = np.zeros((row, col))

# mean filter kernel
meankernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
for i in np.arange(1, col - 1):
    for j in np.arange(1, row - 1):
        dom = mat[j-1:j+2, i-1:i+2]
        result[j, i] = 1/9 * np.sum(dom * meankernel)

#plt.imshow(result)
#plt.show()

# edge filter
walllimit = 2
edgetemp = np.zeros((row, col))
edgekernel = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
for i in np.arange(1, col - 1):
    for j in np.arange(1, row - 1):
        dom = mat[j-1:j+2, i-1:i+2]
        edgetemp[j, i] = np.max(dom[np.where(edgekernel == 1)])

edge = edgetemp - mat
edge[edge < walllimit] = 0

# Plotting the result
fig = plt.figure(figsize=(12, 6))
ax1 = plt.subplot(1, 3, 1)
im1 = ax1.imshow(mat, clim=[mat.min(), mat.max()])
plt.colorbar(im1)
plt.title('Original DSM')
ax2 = plt.subplot(1, 3, 2)
im2 = ax2.imshow(result, clim=[mat.min(), mat.max()])
plt.colorbar(im2)
plt.title('Mean filter')
ax3 = plt.subplot(1, 3, 3)
im3 = ax3.imshow(edge, clim=[edge.min(), edge.max()])
plt.colorbar(im3)
plt.title('Edge filter')
plt.tight_layout()
plt.show()

#save results to geotiff
saveraster(data, 'c:/temp/edgeraster.tif', edge)
saveraster(data, 'c:/temp/smoothraster.tif', result)