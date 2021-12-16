import pydicom
import matplotlib.pyplot as plt
import glob
import numpy as np
from skimage.feature import blob_dog, blob_log, blob_doh
import math
from skimage.filters import threshold_minimum
import sys
from sklearn.cluster import KMeans
from dataclasses import dataclass
import matplotlib
import copy
import datetime

#The coordiantes are very confusing...
#I think
#X = Sag direction
#Y = Axial Direction
#Z = Coronal Direction


#This class holds results so we can refer to them later
@dataclass
class DistanceResult:
	Point1: list #row,col and depth of the point in a grid system
	Point2: list#row,col and depth of the point  in a grid system
	Distance: float #measured distance
	ExpectedDistance: float #Distance we would expect
	
	Point1InSpace: list #The acthul coordiantes 
	Point2InSpace: list #The acthul coordiantes 
	

#a holder class that keeps a list of DistanceResults and the image to plot later
@dataclass
class Result:
	DistanceResults: list
	Image: matplotlib.figure.Figure
	
	
class DistortionCalculation:
	
	#initalises the class with a bunch of variables.
	def __init__(self, folder, SequenceName):
		self.img3d = None
		self.VoxelSize=None
		self.img_shape=None
		self.SphereLocations=None
		self.InterPlateResults=None
		self.IntraPlateResults=None
		self.folder= './'+folder+'/*'
		self.SequenceName= SequenceName
		self.Studydate=None
		self.searchWidth = 4.688
		
	#a function that is designed to adjust points  (should they be detected wrong)
	def AdjustPoint(self,PointGuess,NewPoint):
		#go through each point
		for plateIdx in range(len(self.SphereLocations)):
			for pointIdx in range(len(self.SphereLocations[plateIdx])): #find a point that is with10 of what the user guessed and reset that points position to whatever the user said
				distance = math.sqrt((PointGuess[0]-self.SphereLocations[plateIdx][pointIdx][0])**2 + (PointGuess[1]-self.SphereLocations[plateIdx][pointIdx][1])**2 +(PointGuess[2]-self.SphereLocations[plateIdx][pointIdx][2])**2 )
				if distance < 10:
					self.SphereLocations[plateIdx][pointIdx]=NewPoint
					return #if we find the point we are done 
		raise ValueError("Error No Point Found") #if we donn't find a point throw up an error
	
	#These 3 functions extract the slices from the volume
	#some of the matricies are flipped so they match DICOM viewing software
	def GetSagSlice(self,SliceNumber):
		return self.img3d[:,:,SliceNumber]
	def GetAxialSlice(self,SliceNumber):
		return np.flip(self.img3d[SliceNumber,:,:], axis=1)
	def GetCorSlice(self,SliceNumber):
		return np.flip(self.img3d[:,SliceNumber,:], axis=1)
	
	##A function used to find the spheres, takes in position of slice and how many spheres we expect as well as the search width which the userr can change
	def __GetSphereCentres(self, SliceLocCentre,NumberOfSpheresExpected):
		SearchWidth=self.searchWidth
		SearchSize = int(round(SearchWidth/self.VoxelSize[1])) #get how many slices we are going to search in
		
		#go through each slice and binarise it, keep track of the threshold required for each slice and retain the smallest threshold from each slice. 
		ChosenThresh = sys.maxsize
		for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
			Image = self.GetCorSlice(i)
			thresh = threshold_minimum(Image)
			if (thresh < ChosenThresh):
				ChosenThresh=thresh
				
				
		#Get list of 3d points for kmeans clustering for each sphere, essentially a list of xyz coordaites within each sphere
		points = []
		for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
			z=i
			Image = self.GetCorSlice(i)
			Binary_Image = Image > ChosenThresh 
			Coords = np.argwhere(Binary_Image != 0)
			z_coords = np.ones( (Coords.shape[0],1),dtype=int )*z
			Coords = np.append(Coords,z_coords,axis=1)
			for xyz in Coords:
				points.append(xyz)
		points=np.array(points)
		
		
		
		Spheres = []
		kmeans = KMeans(n_clusters=NumberOfSpheresExpected, random_state=0).fit(points)# use this to cluster the points into each sphere
		
		
		#Know we know what sphere belongs to what we work out the centre of mass for each cluster and hence the centre of the sphere
		for i in range(NumberOfSpheresExpected):
			idx = np.argwhere(kmeans.labels_==i)[:,0]
			x_coords = points[idx][:,1] #[1] is x and [0] is y
			y_coords = points[idx][:,0]
			z_coords = points[idx][:,2]
			CentreOfSphere = [sum(x_coords) / len(points[idx]),sum(y_coords) / len(points[idx]),sum(z_coords) / len(points[idx])]
			Spheres.append(CentreOfSphere)
			#print (CentreOfSphere)
		
		'''
		#DebugPlot
		for I in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
			Image = GetCorSlice(I) #> HighestThresh*0.5
			plt.title(I)
			fig = plt.gcf()
			fig.set_size_inches(30, 30)
			plt.imshow(Image)
			for xyz in Spheres:
				plt.plot(xyz[0], xyz[1], 'b+')
			plt.show()
		'''
		
		
		#Return all the coords
		return Spheres
		
	#This function finds the distances within a plate.
	def __ComputerIntraPlateDistances(self, SphereLocations):
		
		ResultsForAllPlates=[]
		
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
		
		
		pos=0
		for plate in SphereLocations: # for each plate..
			x=[]
			y=[]
			z=[]
			#extract xy
			for xyz in plate: # get all the xyz in a big list
				x.append([xyz[0]])
				y.append([xyz[1]])
				z.append([xyz[2]])
			
			#we know the shape of the grid at this point
			RowsCols=[]
			if len(plate)==4 or len(plate)==5:
				RowsCols=[3,3]
			elif len(plate)==13 or len(plate)==21:
				RowsCols=[5,5]
			
			#cluster each sphere onto a grid using kmeans clustering
			kmeansCols = KMeans(n_clusters=RowsCols[1], random_state=0).fit(x)
			kmeansRows = KMeans(n_clusters=RowsCols[0], random_state=0).fit(y)
			
			#now we have the grid this part works out where the lines of the grid lay so we can figure out where in the grid a sphere lies
			colLines = []
			for i in range(RowsCols[1]):
				temp = []
				for j in range(len(kmeansCols.labels_)):
					if kmeansCols.labels_[j] == i:
						temp.append(x[j][0])
				colLines.append(sum(temp)/len(temp))
			colLines=sorted(colLines)
				
			rowLines = []
			for i in range(RowsCols[0]):
				temp = []
				for j in range(len(kmeansRows.labels_)):
					if kmeansRows.labels_[j] == i:
						temp.append(y[j][0])
				rowLines.append(sum(temp)/len(temp))
			rowLines=sorted(rowLines)
			
			
			#Iterate over each col 
			#then find spheres in the next col and work out distances
			DistResObjs=[]
			for col in range(0,RowsCols[1]): # iterate from left to the right of the image
	
				for i in range(len(x)):
					xyz = [x[i][0],y[i][0],z[i][0]]
					RowCol = self.__DetermineRowColOfPoint(xyz[1],xyz[0],rowLines,colLines) # get where on the grid this sphere is 
					targetRowCol = [RowCol[0],RowCol[1]+1]
	
					if (RowCol[1]==col): #make sure we are on the right column 
						for j in range(len(x)): # go through the other points now
							xyz_ref = [x[j][0],y[j][0],z[j][0]]
							RowCol_ref = self.__DetermineRowColOfPoint(xyz_ref[1],xyz_ref[0],rowLines,colLines) # find the grid of the new point
							if ((RowCol_ref[1] - RowCol[1]) >=0): # find any points in the same col or to the right of the current point
								if (RowCol_ref != RowCol): #Dont calc distances to the same point
									#work out the distance and expected distance to compare to
									distance = self.__distanceCalc(xyz,xyz_ref)
									expecteddistance = math.sqrt( ((RowCol_ref[0]-RowCol[0])*40)**2 + ((RowCol_ref[1]-RowCol[1])*40)**2)
									
									#fill up the distance result object and add to our list
									DistanceResultObj = DistanceResult(copy.deepcopy(RowCol_ref),copy.deepcopy(RowCol),distance,expecteddistance,xyz,xyz_ref)
									DistResObjs.append(DistanceResultObj)
		
									#hardCoded arrow drawning...
									#very very ugly maybe i can improve this if can think of a way....
									#I might put the connections in an external xml file at some point...
									fontsize = 18
									widthArrow = 3
									if (pos == 0):
										if (RowCol_ref[0]-RowCol[0])==1 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[0]-RowCol[0])==-1 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[1]-RowCol[1])==2:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
		
									if (pos == 1 or pos == 3): #this might be duplicated arrows i should fix it
										if (RowCol_ref[0]-RowCol[0])==0 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[0]-RowCol[0])==-1 and (RowCol_ref[1]-RowCol[1])==0:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
										if RowCol_ref==[1,1] and RowCol==[2,0]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[0,2] and RowCol==[1,1]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
	
										if RowCol_ref==[3,1] and RowCol==[2,0]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[4,2] and RowCol==[3,1]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
										if RowCol_ref==[1,3] and RowCol==[0,2]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[2,4] and RowCol==[1,3]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
										if RowCol_ref==[3,3] and RowCol==[4,2]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[2,4] and RowCol==[3,3]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
									if (pos == 2):
										if (RowCol_ref[0]-RowCol[0])==0 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										
										if (RowCol_ref[0]-RowCol[0])==-1 and RowCol_ref[1] == 4 and RowCol[1]==4:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										
										if (RowCol_ref[0]-RowCol[0])==-1 and (RowCol_ref[1]-RowCol[1])==0:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
										if RowCol_ref==[0,1] and RowCol==[1,0]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[1,4] and RowCol==[0,3]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
	
										if RowCol_ref==[4,1] and RowCol==[3,0]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if RowCol_ref==[3,4] and RowCol==[4,3]:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
									if (pos == 4):
										if (RowCol_ref[0]-RowCol[0])==1 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[0]-RowCol[0])==-1 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[0]-RowCol[0])==0 and (RowCol_ref[1]-RowCol[1])==1:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
										if (RowCol_ref[0]-RowCol[0])==-1 and (RowCol_ref[1]-RowCol[1])==0:
											plt.arrow(x=xyz[0], y=xyz[1], dx=xyz_ref[0]-xyz[0], dy=xyz_ref[1]-xyz[1], width=widthArrow,length_includes_head=True) 
											plt.annotate( str(round(distance,2))+"mm", xy = ( (xyz[0]+xyz_ref[0])/2, (xyz[1]+xyz_ref[1])/2) ,fontsize=fontsize,ha='center',color="orange") 
											
			plt.ioff()#I think this stopped the plot dialog constnatly showing up...
			#Draw the girdlines
			for i in colLines:
				plt.axvline(x=i)
			for i in rowLines:
				plt.axhline(y=i)
			Image = self.GetCorSlice(int(round(SlicePositions[pos]))) #Get the slice to plot
			fig = plt.gcf()
			fig.set_size_inches(30, 30)
			plt.xticks(fontsize=50)
			plt.yticks(fontsize=50)
			plt.imshow(Image)
			plt.close()
			#plt.show()
			
			#return our stuff
			ResultObj = Result(DistResObjs,fig)
			ResultsForAllPlates.append(ResultObj)
			
			pos+=1 # used by thye plotting to determine what slice we are on...
			
			
		#Some cases of duplicate distance ie 1->2 and 2->1 so this part removes that 
		
		for i in range(0,len(ResultsForAllPlates)):
			distances = ResultsForAllPlates[i].DistanceResults
			links=[]
			for j in range(len(distances)):
				link = [distances[j].Point1, distances[j].Point2] 
				link_reverse = link[::-1]
				
				if (link in links or link_reverse in links): # if a repeat is found nulify it 
					distances[j]=None
				else:
					links.append(link) #fill up this list of links
			
			ResultsForAllPlates[i].DistanceResults = [x for x in distances if x is not None] # remove all nulifed entries
		
		return ResultsForAllPlates
	
	
	
	#Original attempt, this method takes the average of the spheres in the z direction and compute distance between these lines
	def __ComputerInterPlateDistancesV1(self, SphereLocations):
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
			
		distances=[]
		for i in range(1,len(SlicePositions)):
			distances.append( (SlicePositions[i] - SlicePositions[i-1])*self.VoxelSize[0])
	
		fig= plt.figure()
		Image = self.GetSagSlice(self.img_shape[2]//2) #> HighestThresh*0.5
		for i in SlicePositions:
			plt.axvline(x=i)
		
		y=self.img_shape[0]*0.6
		for i in range(0,len(SlicePositions)-1):
			plt.arrow(x=SlicePositions[i], y=y, dx=SlicePositions[i+1]-SlicePositions[i], dy=0, width=5,length_includes_head=True) 
			plt.annotate( str(round(distances[i],2))+"mm", xy = ( (SlicePositions[i]+SlicePositions[i+1])/2, y-10),fontsize=50,ha='center',color="orange") 
			y-=30
		
		
		fig.set_size_inches(30, 30)
		plt.imshow(Image)
		
		for i in range(len(distances)):
			distances[i]/=40
		
		return distances,fig
		
	
	#Helper function that returns sthe grid point, essentially tells you what gridlines the point is closest to. 
	def __DetermineRowColOfPoint(self, y,x,rowLines,colLines):
		delta=[]
		for I in range(0,len(rowLines)):
			delta.append( np.abs(rowLines[I] - y) )
		row= delta.index(min(delta))
		delta=[]
		for I in range(0,len(colLines)):
			delta.append( np.abs(colLines[I] - x))
		col = delta.index(min(delta))
		return [row,col]
	

	#Helpeer function that returns a distance for two points
	def __distanceCalc(self, xyz1,xyz2):
		dx = (xyz1[0] - xyz2[0]) * self.VoxelSize[2] #Sag
		dy = (xyz1[1] - xyz2[1]) * self.VoxelSize[0] #Axial
		dz = (xyz1[2] - xyz2[2]) * self.VoxelSize[1] #Cor This may be wrong so might be wroth checking if things go weird....
		dist = (((dx)**2) + ((dy)**2) +((dz)**2) )**0.5
		return dist
	
	#Maybe better attempt computes the average distance between spheres in 3d
	def __ComputerInterPlateDistancesV2(self,SphereLocations):
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
		
		
		MidWaySlice = int(round(self.img_shape[2]/2))
		#Find the spheres closest to the midpoint slice for each plate 
		SpheresPerPlateToLookFor = [2,5,5,5,3]
		
		x=[]
		y=[]
		z=[]
		
		platecount = 0
		for plate in SphereLocations:
			delta=[]
			#Find x values close to the current midway slice
			for xyz in plate:
				delta.append( np.abs(xyz[0] - MidWaySlice))
			idx_closest = sorted(range(len(delta)), key=lambda k: delta[k])[:SpheresPerPlateToLookFor[platecount]]
			
			for idx in idx_closest:
				x.append([plate[idx][0]])
				y.append([plate[idx][1]])
				z.append([plate[idx][2]])
			platecount+=1
		
		
			
		#we know the number and rows and cols in this case 
		kmeansCols = KMeans(n_clusters=5, random_state=0).fit(z)
		kmeansRows = KMeans(n_clusters=5, random_state=0).fit(y)
		
		colLines = []
		for i in range(5):
			temp = []
			for j in range(len(kmeansCols.labels_)):
				if kmeansCols.labels_[j] == i:
					temp.append(z[j][0])
			colLines.append(sum(temp)/len(temp))
		colLines=sorted(colLines)
			
		rowLines = []
		for i in range(5):
			temp = []
			for j in range(len(kmeansRows.labels_)):
				if kmeansRows.labels_[j] == i:
					temp.append(y[j][0])
			rowLines.append(sum(temp)/len(temp))
		rowLines=sorted(rowLines)
		
	
		#Iterate over each col 
		#then find each sphere that is in the same row but the next col
		distances=[]
		InterPlateLongDistance = []
		for col in range(0,4):
			averagedistance=[]
			for i in range(len(x)):
				xyz = [x[i][0],y[i][0],z[i][0]]
				RowCol = self.DetermineRowColOfPoint(xyz[1],xyz[2],rowLines,colLines)
				targetRowCol = [RowCol[0],RowCol[1]+1]
				if (RowCol[1]==col): #Get the right col
					for j in range(len(x)):
						xyz_ref = [x[j][0],y[j][0],z[j][0]]
						RowCol_ref = self.DetermineRowColOfPoint(xyz_ref[1],xyz_ref[2],rowLines,colLines)
						if (RowCol_ref == targetRowCol): # find the target point
							#compute distance
							distance = self.distanceCalc(xyz,xyz_ref)
							averagedistance.append(distance)
							
						#work out thed distance right across the image
						#Oppisite columns but same row
						
						if (RowCol[1]==0 and RowCol_ref[1]==4):
							if (RowCol[0]==RowCol_ref[0]):
								distance = self.distanceCalc(xyz,xyz_ref)
								InterPlateLongDistance.append(DistanceResult(RowCol,RowCol_ref,distance,160,xyz,xyz_ref))
			
			
			DistanceResultObj= DistanceResult([col],[col+1],sum(averagedistance)/len(averagedistance),40,xyz,xyz_ref)
			#distances.append(sum(averagedistance)/len(averagedistance))
			distances.append(DistanceResultObj)
				
	
		Image = self.GetSagSlice(MidWaySlice)
		plt.imshow(Image)
		fig = plt.gcf()
		fig.set_size_inches(30, 30)
		#plt.imshow(Image)
		
		for i in SlicePositions:
			plt.axvline(x=i)
		
		y=self.img_shape[0]*0.6
		for i in range(0,len(distances)):
			plt.arrow(x=SlicePositions[i], y=y, dx=SlicePositions[i+1]-SlicePositions[i], dy=0, width=5,length_includes_head=True) 
			plt.annotate( str(round(distances[i].Distance,2))+"mm", xy = ( (SlicePositions[i]+SlicePositions[i+1])/2, y-10),fontsize=50,ha='center',color="orange") 
			y-=30
			
		distances +=InterPlateLongDistance
		ResultObj = Result(distances,fig)
			
		return ResultObj
			
	
	#helper function that returns the row,col and depth of a point by finding what grind line is closest
	def __DetermineRowColDepthOfPoint(self, x,y,z,depthLines,rowLines,colLines):
		
		delta=[]
		for I in range(0,len(rowLines)):
			delta.append( np.abs(rowLines[I] - y) )
		row= delta.index(min(delta))
		delta=[]
		for I in range(0,len(colLines)):
			delta.append( np.abs(colLines[I] - z))
		col = delta.index(min(delta))
		delta=[]
		for I in range(0,len(depthLines)):
			delta.append( np.abs(depthLines[I] - x))
		depth = delta.index(min(delta))
		
		return [row,col,depth]
	

	# Hopefully the last version...
	#In this instance we compute distance of all spheres interplate instead of just within one plane like in V2.
	def __ComputerInterPlateDistancesV3(self,SphereLocations):
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
		
		
		MidWaySlice = int(round(self.img_shape[2]/2))# used for plotting
		x=[]
		y=[]
		z=[]
		
		for plate in SphereLocations:
			for xyz in plate:
				x.append([xyz[0]])
				y.append([xyz[1]])
				z.append([xyz[2]])
			
		#we clustrer each point into a 3d grid 
		kmeansCols  = KMeans(n_clusters=5, random_state=0).fit(z)
		kmeansRows  = KMeans(n_clusters=5, random_state=0).fit(y)
		kmeansDepth = KMeans(n_clusters=5, random_state=0).fit(x)
		
		#Like in the intra case we find the grid lines in all dimeonons, in the intra we only care about one plane but here we care about all axis
		colLines = []
		for i in range(5):
			temp = []
			for j in range(len(kmeansCols.labels_)):
				if kmeansCols.labels_[j] == i:
					temp.append(z[j][0])
			colLines.append(sum(temp)/len(temp))
		colLines=sorted(colLines)
			
		rowLines = []
		for i in range(5):
			temp = []
			for j in range(len(kmeansRows.labels_)):
				if kmeansRows.labels_[j] == i:
					temp.append(y[j][0])
			rowLines.append(sum(temp)/len(temp))
		rowLines=sorted(rowLines)
		
		depthLines = []
		for i in range(5):
			temp = []
			for j in range(len(kmeansDepth.labels_)):
				if kmeansDepth.labels_[j] == i:
					temp.append(x[j][0])
			depthLines.append(sum(temp)/len(temp))
		depthLines=sorted(depthLines)
		
		
		
		distances = []
		for col in range(0,4): #go through each col
			for i in range(len(x)):
				xyz = [x[i][0],y[i][0],z[i][0]]
				RowColDepth = self.__DetermineRowColDepthOfPoint(xyz[0],xyz[1],xyz[2],depthLines,rowLines,colLines) #get the grid point
				if (RowColDepth[1]==col): #Get the right col
					for j in range(len(x)):
						xyz_ref = [x[j][0],y[j][0],z[j][0]]
						RowColDepth_ref = self.__DetermineRowColDepthOfPoint(xyz_ref[0],xyz_ref[1],xyz_ref[2],depthLines,rowLines,colLines) #ge the ref point
						if ( RowColDepth_ref[1] > RowColDepth[1]): #only accept points taht are to the right (ignore points in the same plate)
								#get the distances and store them
								distance = self.__distanceCalc(xyz,xyz_ref)
								expecteddistance = math.sqrt( ((RowColDepth_ref[0]-RowColDepth[0])*40)**2 + ((RowColDepth_ref[1]-RowColDepth[1])*40)**2 + ((RowColDepth_ref[2]-RowColDepth[2])*40)**2 )
								
								DistanceResultObj = DistanceResult(copy.deepcopy(RowColDepth_ref),copy.deepcopy(RowColDepth),distance,expecteddistance,xyz,xyz_ref)
								distances.append(DistanceResultObj)
								
		#plot in the mid slice for visualisation
		plt.ioff()
		Image = self.GetSagSlice(MidWaySlice)
		fig = plt.figure()
		plt.xticks(fontsize=50)
		plt.yticks(fontsize=50)
		plt.imshow(Image)
		fig.set_size_inches(30, 30)
		
		for i in SlicePositions:
			plt.axvline(x=i)
		
	
		#get the average interplate distance for the plot
		ArrowAverages = []
		for col in range(0,4):
			average = []
			for i in range(0,len(distances)):
				if (distances[i].Point2[1] == col):
					#print (distances[i])
					if (distances[i].Point1[2]==2 and distances[i].Point2[2]==2):
						if (distances[i].Point1[0]==distances[i].Point2[0]):
							if ( (distances[i].Point1[1]-distances[i].Point2[1]) == 1): 
								average.append(distances[i].Distance)
			ArrowAverages.append( (sum(average)/len(average)) )
		
		#draw the arrows on the plot
		y=self.img_shape[0]*0.6
		for i in range(0,len(SlicePositions)-1):
			plt.arrow(x=SlicePositions[i], y=y, dx=SlicePositions[i+1]-SlicePositions[i], dy=0, width=5,length_includes_head=True) 
			plt.annotate( str(round(ArrowAverages[i],2))+"mm", xy = ( (SlicePositions[i]+SlicePositions[i+1])/2, y-10),fontsize=50,ha='center',color="orange") 
			y-=30
		
		plt.close(fig)
		ResultObj = Result(distances,fig)
		return ResultObj
		
	#the user calls this to get the sphere locations
	def GetFudicalSpheres(self):
		#get all the DICOM files
		DICOMFiles = glob.glob(self.folder)
		ExtractedSequence = self.SequenceName
		
		#Load in all DICOM files and make sure its the right sequence 
		DICOMS=[]
		for file in DICOMFiles:
			LoadedDICOM = pydicom.read_file( file )
			if (LoadedDICOM.SeriesDescription == ExtractedSequence):
				DICOMS.append(LoadedDICOM)
		DICOMS.sort(key=lambda x: x.SliceLocation, reverse=False) # sort them by slice 
	
		#Put it into a 3d array for slicing and get some settings
		img_shape = list(DICOMS[0].pixel_array.shape) #Axial, Cor, Sag (i think)
		VoxelSize = [DICOMS[0].PixelSpacing[0],DICOMS[0].PixelSpacing[1],DICOMS[0].SpacingBetweenSlices] #Axial, Cor, Sag (i think)
		img_shape.append(len(DICOMS))
		img3d = np.zeros(img_shape)
		for i, s in enumerate(DICOMS):
			img2d = s.pixel_array
			img3d[:, :, i] = img2d
			
		#Get the datetime of the study
		LoadedDICOM = pydicom.dcmread( DICOMFiles[0] )
		date= (LoadedDICOM["AcquisitionDate"])
		time= (LoadedDICOM["AcquisitionTime"])
		year = int(date[0:4])
		month =  int(date[4:6])
		day = int(date[6:8])
		hour = int(time[0:2])
		Min = int(time[2:4])
		Sec = int(time[4:6])
		self.Studydate = datetime.datetime(year, month, day,hour,Min,Sec)		
	
		#get the centre with a guess of where each plate is
		Centre = [img_shape[0]//2,img_shape[1]//2,img_shape[2]//2] 
		Plates =  [ int(round(Centre[1]-(40/VoxelSize[1])*2)),
					int(round(Centre[1]-(40/VoxelSize[1]))),
					int(round(Centre[1])),
					int(round(Centre[1]+(40/VoxelSize[1]))),
					int(round(Centre[1]+(40/VoxelSize[1])*2))]
		
		#set some class varaibles so we can access them elsewhere
		self.img3d = img3d
		self.img_shape = img_shape
		self.VoxelSize = VoxelSize
		
		#We know the spheres in each plate 
		SpheresPerPlate = [4,13,21,13,5]
		SphereLocations = [] #plate 1 to 5 in order
		for plate in range(5): # go through each plae and get the sphere locations
			Spheres= self.__GetSphereCentres(Plates[plate],SpheresPerPlate[plate])
			SphereLocations.append(Spheres)#the xyz of each sphere is in terms of slice and coordiants (not real distances, although all distances are covered to mm)
	
		self.SphereLocations = SphereLocations

	#User calls this to get the distances computes
	def GetDistances(self):
		InterPlateResults = self.__ComputerInterPlateDistancesV3(self.SphereLocations) #Get inter distances
		plt.close()
		
		IntraPlateResults = self.__ComputerIntraPlateDistances(self.SphereLocations)  #Get intra distances


		#Adjust point1 and point 2 so its [Sag,Ax,Cor], means the xyz coords and the point index match up..
		for i in range(len(InterPlateResults.DistanceResults)):
			temp = InterPlateResults.DistanceResults[i].Point1
			InterPlateResults.DistanceResults[i].Point1=[temp[2],temp[0],temp[1]]
			
			temp = InterPlateResults.DistanceResults[i].Point2
			InterPlateResults.DistanceResults[i].Point2=[temp[2],temp[0],temp[1]]
		
		#do the same for intra
		for j in range(len(IntraPlateResults)):
			for i in range(len(IntraPlateResults[j].DistanceResults)):
				IntraPlateResults[j].DistanceResults[i].Point1.append(j)
				IntraPlateResults[j].DistanceResults[i].Point2.append(j)
				
				temp = IntraPlateResults[j].DistanceResults[i].Point1
				IntraPlateResults[j].DistanceResults[i].Point1=[temp[1],temp[0],temp[2]]
			
				temp = IntraPlateResults[j].DistanceResults[i].Point2
				IntraPlateResults[j].DistanceResults[i].Point2=[temp[1],temp[0],temp[2]]
		
		
		self.InterPlateResults = InterPlateResults
		self.IntraPlateResults = IntraPlateResults

