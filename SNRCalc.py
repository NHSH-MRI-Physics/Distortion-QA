import pydicom
import matplotlib.pyplot as plt
import glob
import numpy as np
from skimage.feature import blob_dog, blob_log, blob_doh
import math
from skimage.filters import threshold_minimum
import skimage.filters 
import sys
from sklearn.cluster import KMeans
from dataclasses import dataclass
import matplotlib
import copy
import datetime
from scipy import ndimage
import matplotlib.patches as patches


class SNR():
		
	#initalises the class with a bunch of variables.
	def __init__(self, DistortionObj):
		self.DistortionObj = DistortionObj

	def ComputerSNR(self):
		Spheres = self.DistortionObj.SphereLocations[0] #get spheres in the top slice 
		averagex = []
		averagey = []
		averagez = []

		boxsize = [50,50]

		for xyz in Spheres:
			averagex.append(xyz[0])
			averagey.append(xyz[1])
			averagez.append(xyz[2])

		averagex= int(round( (float)(sum(averagex)/len(averagex))))
		averagey= int(round( (float)(sum(averagey)/len(averagey))))
		averagez= int(round( (float)(sum(averagez)/len(averagez))))
		
		Image = self.DistortionObj.GetCorSlice( int(round(averagez)))

		Signal = Image[int(averagey-boxsize[1]/2):int(averagey+boxsize[1]/2),int(averagex-boxsize[0]/2):int(averagex+boxsize[0]/2)]
		
		Noise1 = Image[int(0):int(boxsize[1]),int(0):int(boxsize[0])]
		Noise2 = Image[int(Image.shape[0]-1-boxsize[0]):int(Image.shape[0]-1),int(0):int(boxsize[0])]
		Noise3 = Image[int(0):int(boxsize[1]),int(Image.shape[1]-1-boxsize[1]):int(Image.shape[1]-1)]
		Noise4 = Image[int(Image.shape[0]-1-boxsize[0]):int(Image.shape[0]-1),int(Image.shape[1]-1-boxsize[1]):int(Image.shape[1]-1)]

		#Image[int(0):int(boxsize[1]),int(0):int(boxsize[0])] = 7000000
		#Image[int(Image.shape[0]-1-boxsize[0]):int(Image.shape[0]-1),int(0):int(boxsize[0])] = 7000000
		#Image[int(0):int(boxsize[1]),int(Image.shape[1]-1-boxsize[1]):int(Image.shape[1]-1)] = 7000000
		#Image[int(Image.shape[0]-1-boxsize[0]):int(Image.shape[0]-1),int(Image.shape[1]-1-boxsize[1]):int(Image.shape[1]-1)] = 7000000

		'''
		SigRect = patches.Rectangle((averagex-boxsize[0]/2, averagey-boxsize[1]/2), boxsize[0], boxsize[1], linewidth=1, edgecolor='r', facecolor='none')
		Noise1Rect = patches.Rectangle((0, 0), boxsize[0], boxsize[1], linewidth=1, edgecolor='r', facecolor='none')
		Noise2Rect = patches.Rectangle((Image.shape[1]-1-boxsize[0], 0), boxsize[0], boxsize[1], linewidth=1, edgecolor='r', facecolor='none')
		Noise3Rect = patches.Rectangle((0,Image.shape[0]-1-boxsize[1]), boxsize[0], boxsize[1], linewidth=1, edgecolor='r', facecolor='none')
		Noise4Rect = patches.Rectangle((Image.shape[1]-1-boxsize[0], Image.shape[0]-1-boxsize[1]), boxsize[0], boxsize[1], linewidth=1, edgecolor='r', facecolor='none')
						
		plt.gca().add_patch(SigRect)
		plt.gca().add_patch(Noise1Rect)
		plt.gca().add_patch(Noise2Rect)
		plt.gca().add_patch(Noise3Rect)
		plt.gca().add_patch(Noise4Rect)

		plt.imshow(Image)
		plt.show()
		sys.exit()
		'''

		N = (np.std(Noise1.flatten()) + np.std(Noise2.flatten()) + np.std(Noise3.flatten()) + np.std(Noise4.flatten()))/4.0 
		S = np.mean(Signal)
		SNR = S/N*0.66
		print ("SNR: " + str(SNR))