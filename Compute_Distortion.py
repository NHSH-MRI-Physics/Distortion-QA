import pydicom
import matplotlib.pyplot as plt
import glob
import numpy as np
from skimage.feature import blob_dog, blob_log, blob_doh
import math
from skimage.filters import threshold_minimum
import sys
from sklearn.cluster import KMeans

img3d = None
def GetSagSlice(SliceNumber):
	return img3d[:,:,SliceNumber]
def GetAxialSlice(SliceNumber):
	return np.flip(img3d[SliceNumber,:,:], axis=1)
def GetCorSlice(SliceNumber):
	return np.flip(img3d[:,SliceNumber,:], axis=1)


def GetSphereCentres(SliceLocCentre,NumberOfSpheresExpected,SearchSize=10):
	#BuildHistogram
	HighestThresh = 0
	for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
		Image = GetCorSlice(i)
		thresh = threshold_minimum(Image)
		if (thresh > HighestThresh):
			HighestThresh=thresh
			
	#Get list of 3d points for kmeans clustering
	points = []
	for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
		z=i
		Image = GetCorSlice(i)
		Binary_Image = Image > HighestThresh*0.5
		Coords = np.argwhere(Binary_Image != 0)
		z_coords = np.ones( (Coords.shape[0],1),dtype=int )*z
		Coords = np.append(Coords,z_coords,axis=1)
		for xyz in Coords:
			points.append(xyz)
	points=np.array(points)
	
	Spheres = []
	kmeans = KMeans(n_clusters=NumberOfSpheresExpected, random_state=0).fit(points)
	
	for i in range(NumberOfSpheresExpected):

		idx = np.argwhere(kmeans.labels_==i)[:,0]
		x_coords = points[idx][:,0]
		y_coords = points[idx][:,1]
		z_coords = points[idx][:,2]
		CentreOfSphere = [sum(x_coords) / len(points[idx]),sum(y_coords) / len(points[idx]),sum(z_coords) / len(points[idx])]
		Spheres.append(CentreOfSphere)
		print (CentreOfSphere)
	
	
	#DebugPlot
	for I in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
		Image = GetCorSlice(I) > HighestThresh*0.5
		plt.title(I)
		fig = plt.gcf()
		fig.set_size_inches(30, 30)
		plt.imshow(Image)
		for xyz in Spheres:
			plt.plot(xyz[1], xyz[0], 'b+')
		plt.show()
		
	#Test this method on the other slabs to make sure it all works...
	#Return all the coords
	
	sys.exit()
	
def ComputeIntraPlaneDistances():
	pass
def ComputerInterPlanDistances():
	pass

def GetFudicalSpheres():
	global img3d
	#DICOMFiles = glob.glob('./PhantomData/*')
	DICOMFiles = glob.glob('./TestData/*')
	ExtractedSequence = "3D Sag T1 BRAVO"
	
	#Load in all DICOM slices
	MaxValue = 0
	DICOMS=[]
	for file in DICOMFiles:
		LoadedDICOM = pydicom.read_file( file )
		if (LoadedDICOM.SeriesDescription == ExtractedSequence):
			DICOMS.append(LoadedDICOM)
			if ( np.max(DICOMS[-1].pixel_array) > MaxValue):
				MaxValue = np.max(DICOMS[-1].pixel_array)
	DICOMS.sort(key=lambda x: x.SliceLocation, reverse=False)

	#Put it into a 3d array for slicing
	img_shape = list(DICOMS[0].pixel_array.shape) #Axial, Cor, Sag (i think)
	VoxelSize = [DICOMS[0].PixelSpacing[0],DICOMS[0].PixelSpacing[1],DICOMS[0].SpacingBetweenSlices]
	img_shape.append(len(DICOMS))
	img3d = np.zeros(img_shape)
	for i, s in enumerate(DICOMS):
		img2d = s.pixel_array
		img3d[:, :, i] = img2d
	
	

	
	Centre = [img_shape[0]//2,img_shape[1]//2,img_shape[2]//2] 
	Plates =  [ int(round(Centre[1]-(40/VoxelSize[1])*2)),
				int(round(Centre[1]-(40/VoxelSize[1]))),
				int(round(Centre[1])),
				int(round(Centre[1]+(40/VoxelSize[1]))),
				int(round(Centre[1]+(40/VoxelSize[1])*2))]
	
	SpheresPerPlate = [4,13,21,13,5]
	
	
	plate=0
	GetSphereCentres(Plates[plate],SpheresPerPlate[plate])
	

GetFudicalSpheres()