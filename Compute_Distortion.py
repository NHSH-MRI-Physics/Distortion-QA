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

#The coordiantes are very confusing...
#I think
#X = Sag direction
#Y = Axial Direction
#Z = Coronal Direction

@dataclass
class DistanceResult:
	refPoint: list
	StartingPoint: list
	Distance: float
	ExpectedDistance: float
	


@dataclass
class Result:
	DistanceResults: list
	Image: matplotlib.figure.Figure
	
	
class DistortionCalculation:
	
	def __init__(self, folder, SequenceName):
		self.img3d = None
		self.VoxelSize=None
		self.img_shape=None
		self.SphereLocations=None
		self.InterPlateResults=None
		self.IntraPlateResults=None
		self.folder= './'+folder+'/*'
		self.SequenceName= SequenceName
		
		
		
	
	
	def GetSagSlice(self,SliceNumber):
		return self.img3d[:,:,SliceNumber]
	def GetAxialSlice(self,SliceNumber):
		return np.flip(self.img3d[SliceNumber,:,:], axis=1)
	def GetCorSlice(self,SliceNumber):
		return np.flip(self.img3d[:,SliceNumber,:], axis=1)
	
	
	def GetSphereCentres(self, SliceLocCentre,NumberOfSpheresExpected,SearchWidth=4.688):
		SearchSize = int(round(SearchWidth/self.VoxelSize[1]))
		#BuildHistogram
		ChosenThresh = sys.maxsize
		for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
			Image = self.GetCorSlice(i)
			thresh = threshold_minimum(Image)
			if (thresh < ChosenThresh):
				ChosenThresh=thresh
				
		#Get list of 3d points for kmeans clustering
		points = []
		for i in range(SliceLocCentre-SearchSize,SliceLocCentre+SearchSize):
			z=i
			Image = self.GetCorSlice(i)
			Binary_Image = Image > ChosenThresh #To high and you miss spheres, to low and you may pick up background noise, maybe this should be the lowest thresh or maybe a list of thresholds for each image?
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
		
	def ComputerIntraPlateDistances(self, SphereLocations):
		
		ResultsForAllPlates=[]
		
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
		
		pos=0
		for plate in SphereLocations:
			x=[]
			y=[]
			z=[]
			#extract xy
			for xyz in plate:
				x.append([xyz[0]])
				y.append([xyz[1]])
				z.append([xyz[2]])
			
			RowsCols=[]
			if len(plate)==4 or len(plate)==5:
				RowsCols=[3,3]
			elif len(plate)==13 or len(plate)==21:
				RowsCols=[5,5]
			
			kmeansCols = KMeans(n_clusters=RowsCols[1], random_state=0).fit(x)
			kmeansRows = KMeans(n_clusters=RowsCols[0], random_state=0).fit(y)
			
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
			for col in range(0,RowsCols[1]):
	
				for i in range(len(x)):
					xyz = [x[i][0],y[i][0],z[i][0]]
					RowCol = self.DetermineRowColOfPoint(xyz[1],xyz[0],rowLines,colLines)
					targetRowCol = [RowCol[0],RowCol[1]+1]
	
					if (RowCol[1]==col): #Get the right col
						for j in range(len(x)):
							xyz_ref = [x[j][0],y[j][0],z[j][0]]
							RowCol_ref = self.DetermineRowColOfPoint(xyz_ref[1],xyz_ref[0],rowLines,colLines)
							if ((RowCol_ref[1] - RowCol[1]) >=0): # find any points in the same col or to the right
								if (RowCol_ref != RowCol): #Dont calc distances to the same point
									distance = self.distanceCalc(xyz,xyz_ref)
									expecteddistance = math.sqrt( ((RowCol_ref[0]-RowCol[0])*40)**2 + ((RowCol_ref[1]-RowCol[1])*40)**2)
									
									DistanceResultObj = DistanceResult(RowCol_ref,RowCol,distance,expecteddistance)
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
											
			plt.ioff()			
			for i in colLines:
				plt.axvline(x=i)
			for i in rowLines:
				plt.axhline(y=i)
			Image = self.GetCorSlice(int(round(SlicePositions[pos]))) #> HighestThresh*0.5
			fig = plt.gcf()
			fig.set_size_inches(30, 30)
			plt.imshow(Image)
			plt.close()
			#plt.show()
			
			ResultObj = Result(DistResObjs,fig)
			ResultsForAllPlates.append(ResultObj)
			
			pos+=1
			
			
		#Remove duplicates so check for inverse distances 
		
		for i in range(0,len(ResultsForAllPlates)):
			distances = ResultsForAllPlates[i].DistanceResults
			links=[]
			
			for j in range(len(distances)):
				link = [distances[j].refPoint, distances[j].StartingPoint] 
				link_reverse = link[::-1]
				
				if (link in links or link_reverse in links):
					distances[j]=None
				else:
					links.append(link)
			
			ResultsForAllPlates[i].DistanceResults = [x for x in distances if x is not None]
	
		
		
		return ResultsForAllPlates
	
	
	
	#Original attempt, this method takes the average of the spheres in the z direction and compute distance between these lines
	def ComputerInterPlateDistancesV1(self, SphereLocations):
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
		
	
	def DetermineRowColOfPoint(self, y,x,rowLines,colLines):
		delta=[]
		for I in range(0,len(rowLines)):
			delta.append( np.abs(rowLines[I] - y) )
		row= delta.index(min(delta))
		delta=[]
		for I in range(0,len(colLines)):
			delta.append( np.abs(colLines[I] - x))
		col = delta.index(min(delta))
		return [row,col]
	

	
	def distanceCalc(self, xyz1,xyz2):
		dx = (xyz1[0] - xyz2[0]) * self.VoxelSize[2] #Sag
		dy = (xyz1[1] - xyz2[1]) * self.VoxelSize[0] #Axial
		dz = (xyz1[2] - xyz2[2]) * self.VoxelSize[1] #Cor This may be wrong so might be wroth checking if things go weird....
		dist = (((dx)**2) + ((dy)**2) +((dz)**2) )**0.5
		return dist
	
	#Maybe better attempt computes the average distance between spheres in 3d
	def ComputerInterPlateDistancesV2(self,SphereLocations):
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
								InterPlateLongDistance.append(DistanceResult(RowCol,RowCol_ref,distance,160))
			
			
			DistanceResultObj= DistanceResult([col],[col+1],sum(averagedistance)/len(averagedistance),40)
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
			
	
	def DetermineRowColDepthOfPoint(self, x,y,z,depthLines,rowLines,colLines):
		
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
	def ComputerInterPlateDistancesV3(self,SphereLocations):
		SlicePositions=[]
		for plateXYZ in SphereLocations:
			average=0
			for XYZ in plateXYZ:
				average += XYZ[2]
			SlicePositions.append(average/len(plateXYZ))
		
		
		MidWaySlice = int(round(self.img_shape[2]/2))
		x=[]
		y=[]
		z=[]
		
		for plate in SphereLocations:
			for xyz in plate:
				x.append([xyz[0]])
				y.append([xyz[1]])
				z.append([xyz[2]])
			
		#we know the number and rows and cols in this case 
		kmeansCols  = KMeans(n_clusters=5, random_state=0).fit(z)
		kmeansRows  = KMeans(n_clusters=5, random_state=0).fit(y)
		kmeansDepth = KMeans(n_clusters=5, random_state=0).fit(x)
		
		
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
		for col in range(0,4):
			for i in range(len(x)):
				xyz = [x[i][0],y[i][0],z[i][0]]
				RowColDepth = self.DetermineRowColDepthOfPoint(xyz[0],xyz[1],xyz[2],depthLines,rowLines,colLines)
				if (RowColDepth[1]==col): #Get the right col
					for j in range(len(x)):
						xyz_ref = [x[j][0],y[j][0],z[j][0]]
						RowColDepth_ref = self.DetermineRowColDepthOfPoint(xyz_ref[0],xyz_ref[1],xyz_ref[2],depthLines,rowLines,colLines)
						if ( RowColDepth_ref[1] > RowColDepth[1]): 
								distance = self.distanceCalc(xyz,xyz_ref)
								expecteddistance = math.sqrt( ((RowColDepth_ref[0]-RowColDepth[0])*40)**2 + ((RowColDepth_ref[1]-RowColDepth[1])*40)**2 + ((RowColDepth_ref[2]-RowColDepth[2])*40)**2 )
								
								DistanceResultObj = DistanceResult(RowColDepth_ref,RowColDepth,distance,expecteddistance)
								distances.append(DistanceResultObj)

		plt.ioff()
		Image = self.GetSagSlice(MidWaySlice)
		fig = plt.figure()
		plt.imshow(Image)
		fig.set_size_inches(30, 30)
		
		for i in SlicePositions:
			plt.axvline(x=i)
		

		y=self.img_shape[0]*0.6
		ArrowAverages = []
		for col in range(0,4):
			average = []
			for i in range(0,len(distances)):
				if (distances[i].StartingPoint[1] == col):
					#print (distances[i])
					if (distances[i].refPoint[2]==2 and distances[i].StartingPoint[2]==2):
						if (distances[i].refPoint[0]==distances[i].StartingPoint[0]):
							if ( (distances[i].refPoint[1]-distances[i].StartingPoint[1]) == 1): 
								average.append(distances[i].Distance)
			ArrowAverages.append( (sum(average)/len(average)) )
						
		
		for i in range(0,len(SlicePositions)-1):
			plt.arrow(x=SlicePositions[i], y=y, dx=SlicePositions[i+1]-SlicePositions[i], dy=0, width=5,length_includes_head=True) 
			plt.annotate( str(round(ArrowAverages[i],2))+"mm", xy = ( (SlicePositions[i]+SlicePositions[i+1])/2, y-10),fontsize=50,ha='center',color="orange") 
			y-=30
		
		plt.close(fig)

		ResultObj = Result(distances,fig)
		
		return ResultObj
		
		
	def GetFudicalSpheres(self):
		#CleanData
		DICOMFiles = glob.glob(self.folder)
		ExtractedSequence = self.SequenceName
		
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
		VoxelSize = [DICOMS[0].PixelSpacing[0],DICOMS[0].PixelSpacing[1],DICOMS[0].SpacingBetweenSlices] #Axial, Cor, Sag (i think)
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
		
		self.img3d = img3d
		self.img_shape = img_shape
		self.VoxelSize = VoxelSize
		
		SpheresPerPlate = [4,13,21,13,5]
		SphereLocations = [] #plate 1 to 5 in order
		for plate in range(5):
			Spheres= self.GetSphereCentres(Plates[plate],SpheresPerPlate[plate])
			SphereLocations.append(Spheres)
	
		self.SphereLocations = SphereLocations


	def GetDistances(self):
		InterPlateResults = self.ComputerInterPlateDistancesV3(self.SphereLocations) 
		plt.close()
		
		IntraPlateResults = self.ComputerIntraPlateDistances(self.SphereLocations) 
			
		self.InterPlateResults = InterPlateResults
		self.IntraPlateResults = IntraPlateResults
		

