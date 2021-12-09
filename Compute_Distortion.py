import pydicom
import matplotlib.pyplot as plt
import glob
import numpy as np
from skimage.feature import blob_dog, blob_log, blob_doh
import math

def GetFudicalSpheres():

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
	img_shape = list(DICOMS[0].pixel_array.shape)
	img_shape.append(len(DICOMS))
	img3d = np.zeros(img_shape)
	for i, s in enumerate(DICOMS):
		img2d = s.pixel_array
		img3d[:, :, i] = img2d
	
	
	def GetSagSlice(SliceNumber):
		return img3d[:,:,SliceNumber]
	def GetAxialSLice(SliceNumber):
		return img3d[SliceNumber,:,:]
	def GetCorSlice(SliceNumber):
		return img3d[:,SliceNumber,:]
	
	
	
	Centre = [img_shape[0]//2,img_shape[1]//2,img_shape[2]//2]
	
	
	
	
	plt.imshow(GetCorSlice(Centre[1]))
	plt.show()		   
		   
		   
	'''
	count=19 
	for dicom in DICOMS[19:44]:
	    blobs = blob_log(dicom.pixel_array, max_sigma=50, num_sigma=20, threshold=.03)
	    blobs[:, 2] = blobs[:, 2] * math.sqrt(2)
	    print (len(blobs))
	    for blob in blobs:
	        y, x, r = blob
	        c = plt.Circle((x, y), r, linewidth=2, fill=False)
	        plt.axes().add_patch(c)
	
	    plt.imshow(dicom.pixel_array,vmin=0, vmax=MaxValue)
	    plt.colorbar()
	    count +=1
	    plt.savefig("TestImages/"+str(count)+".png")
	    plt.close()
	'''
	
GetFudicalSpheres()