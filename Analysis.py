#Analysis Script
import Compute_Distortion
import numpy as np
from dataclasses import dataclass
import scipy
import sys 
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
import os 
import csv
import pandas as pd

#this is a helper class i found to draw 3d arrows, found it here : https://stackoverflow.com/questions/58903383/fancyarrowpatch-in-3d
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

#This class is designed to analyse the distances computed
class AnalysisResults:
	
	#This is called when we construct the AnalysisResults class and sets up all the variables.
	def __init__(self,CalcName,DistorCalcObj):
		self.Results = {}	
		self.ResultConnectingPoint={}
		self.CalcName = CalcName
		self.DistorCalcObj=DistorCalcObj
		self.ax=None
		self.fig=None
		self.curr_pos=0
	
	def GetMetrics(self):
		return list(self.Results.keys())
		
	#This is an event function that is called when a keyboard button is pressed after you call the CheckPoints function.
	def __key_event(self,e):
		
		#If the right or left arrow is pressed increase the display slice counter by 1 
		if e.key == "right":
			self.curr_pos = self.curr_pos + 1
		elif e.key == "left":
			self.curr_pos = self.curr_pos - 1
		else:
			return
		
		self.ax.cla() #Clear the plot
		
		#go through all the points we have and if any belong on this slide (rounded) then draw a cross on the plot
		for plate in self.DistorCalcObj.SphereLocations:
			for point in plate:
				if (int(round(point[2]))==self.curr_pos):
					self.ax.plot(point[0], point[1], 'b+') 
		
		#Draw the Coronal slice at the current position the user selected, update the title as well.
		self.ax.imshow(self.DistorCalcObj.GetCorSlice(self.curr_pos))
		self.fig.suptitle("Slice Number " + str(self.curr_pos))
		self.fig.canvas.draw()

	#This function opens a plot dialog that the user can scroll through to view the position of each sphere and each slice.
	def CheckPoints(self):
		self.fig = plt.figure()
		self.fig.canvas.mpl_connect('key_press_event', self.__key_event) #This sets the key event to go off whenever any keyboard button is pressed
		self.ax = self.fig.add_subplot(111)
		self.ax.imshow(self.DistorCalcObj.GetCorSlice(0)) #Display the first slice
		self.fig.suptitle("Slice Number " + str(self.curr_pos))
		plt.show()
		
	#Useful to sometimes show a 3d plot of all the spheres we computed and show direction of the maximum of some given metric
	def Show3dModel(self,metric=None):
		
		#Set up the plot 
		fig = plt.figure()
		ax = fig.gca(projection='3d')
		ax.set_aspect("auto")
		
		#ax.set_zlabel('Coronal', fontsize=20)
		#ax.set_ylabel('Axial', fontsize=20)
		#ax.set_xlabel('Sagittal', fontsize=20)
		ax.set_zlabel('z', fontsize=20)
		ax.set_ylabel('y', fontsize=20)
		ax.set_xlabel('x', fontsize=20)
		
		
	
		colours = ["r","g","b","m","y"] # List of colours so each plate gets coloured differently
		count =0
		MidPoint = [self.DistorCalcObj.img_shape[0]/2.0,self.DistorCalcObj.img_shape[1]/2.0,self.DistorCalcObj.img_shape[2]/2.0] #Not used but i kept it in case we want to adjust distances to the mid point
		
		#iterate over each sphere and point it using the correct colour
		for plate in self.DistorCalcObj.SphereLocations:
			for point in plate:
				ax.scatter( (point[0])*self.DistorCalcObj.VoxelSize[2], (point[1])*self.DistorCalcObj.VoxelSize[0], (point[2])*self.DistorCalcObj.VoxelSize[1], color=colours[count], s=100)
			count+=1
		plt.title("3d Plot")
		
		#So if there is a metric defiend by the user go into this part
		if (metric != None):
			
			if metric not in self.Results: #Check if the metric the user entered a metric we have 
				raise ValueError('Metric Not Found!')
			plt.title(metric)
			
			result = self.Results[metric]
			if "Inter" in metric:#Just a work around since the intra stuff is in a list already, makes it easy to have it one think if we can just put the inter results in a list as well.
				result=[result]
				

			count =0
			for dist in result: #Go through each point and convert from xyz coords to real distances
				print (dist[0],dist[1].Point1,dist[1].Point2)
				
				#dist[1] is a distance result object which contains several properties about the distance being used here (like connecting points)
				Point1 = dist[1].Point1InSpace
				Point2 = dist[1].Point2InSpace
				
				#Converting to real distances
				Point1[0]*=self.DistorCalcObj.VoxelSize[2]
				Point1[1]*=self.DistorCalcObj.VoxelSize[0]
				Point1[2]*=self.DistorCalcObj.VoxelSize[1]
				
				Point2[0]*=self.DistorCalcObj.VoxelSize[2]
				Point2[1]*=self.DistorCalcObj.VoxelSize[0]
				Point2[2]*=self.DistorCalcObj.VoxelSize[1]
				
				#Plot an arrow between the two points
				arw = Arrow3D([Point1[0],Point2[0]],[Point1[1],Point2[1]],[Point1[2],Point2[2]], arrowstyle="->", color=colours[count], lw = 3, mutation_scale=25)
				ax.add_artist(arw)
				count+=1
		
		plt.show()
		
		
	#This function just produces a string for all metrics for each displaying
	def __GetStatString(self):
		output=""
		output+= ("Study Date: " + str(self.DistorCalcObj.Studydate) + "\n")
		output+= ("Interplate Stats\n") 
		output+=("Interplate Max Distortion: " + str(self.Results["Interplate Max Distortion"][0]) +" mm\n")
		output+=("Interplate Max Percentage Distortion: " + str(self.Results["Interplate Max Percentage Distortion"][0]) +" %\n")
		output+=("Interplate Coefficient Of Variation: " + str(self.Results["Interplate Coefficient Of Variation"])+"\n")
		
		output+=("Interplate Max Distortion X: " + str(self.Results["Interplate Max Distortion X"][0]) +" mm\n")
		output+=("Interplate Max Distortion Y: " + str(self.Results["Interplate Max Distortion Y"][0]) +" mm\n")
		output+=("Interplate Max Distortion Z: " + str(self.Results["Interplate Max Distortion Z"][0]) +" mm\n")
		
		output+=("Interplate Coefficient Of Variation X: " + str(self.Results["Interplate Coefficient Of Variation X"])+"\n")
		output+=("Interplate Coefficient Of Variation Y: " + str(self.Results["Interplate Coefficient Of Variation Y"])+"\n")
		output+=("Interplate Coefficient Of Variation Z: " + str(self.Results["Interplate Coefficient Of Variation Z"])+"\n")
		
		output+= ("\n")
		output+= ("Intraplate Stats\n")
		output+=("Intraplate Max Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion"])) +" mm\n") #This one is a bit different since its a list of list this is a way to get the max value in a list of lists 
		output+=("Intraplate Max Percentage Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Percentage Distortion"])) +"\n" )
		output+=("Intraplate Coefficient Of Variation: " + str(max(self.Results["Intraplate Coefficient Of Variation"]))+"\n")
		
		output+=("Intraplate Max Distortion X: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion X"])) +" mm\n")
		output+=("Intraplate Max Distortion Y: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion Y"])) +" mm\n")
		output+=("Intraplate Max Distortion Z: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion Z"])) +" mm\n")
		
		output+=("Intraplate Coefficient Of Variation X: " + str(max(self.Results["Intraplate Coefficient Of Variation X"]))+"\n")
		output+=("Intraplate Coefficient Of Variation Y: " + str(max(self.Results["Intraplate Coefficient Of Variation Y"]))+"\n")
		#output+=("Intraplate Coefficient Of Variation Z: " + str(max(self.Results["Intraplate Coefficient Of Variation Z"]))+"\n")
		
		output+= ("\n")
		
		return output
	
	
	#This function updates or makes the csv file which contains all the analysis conducted
	def OutputPeriodicData(self, file):
		
		#put all metrics into a list, also add a new one called study date so we can plot
		Metrics = ["StudyDate"]
		for key in self.Results.keys():
			Metrics.append(key)
			
			
		#if the csv file does not exist, make it and fill in the csv headers.
		if os.path.isfile(file) == False:
			f=open(file,'w')
			string=""
			for value in Metrics:
				string+=value+","
			string=string[:-1]
			f.write(string+"\n")
			f.close()
			
		
		#for each metric place it in a string so we can add it to the file
		string =""
		for value in Metrics:
			if value == "StudyDate":
				string+=str(self.DistorCalcObj.Studydate)+","
			else:
				#Since inter and itnra have slightly different formats its easiest to just treat them separately when extracting the metrics
				if "Inter" in value: 
					if  ("Coefficient Of Variation" not in value):#Coefficient Of Variation has a slighly different format to so again easier to just deal with it separately
						string+=str(self.Results[value][0])+","
					else:
						string+=str(self.Results[value])+","
				if "Intra" in value:
					if  ("Coefficient Of Variation" not in value):
						string+=str(max(x[0] for x in self.Results[value]))+","
					else:
						string+=str(max(self.Results[value]))+","


		string=string[:-1] #Remove the last comma, easy way to do this
		string+="\n" 
		
		#open the file in append mode and add the string to it.
		with open(file, "a") as fileAppend:
			fileAppend.write(string)


	#This function plots the CSV file we just created
	def PlotCSV(self,file):
		#Make a folder called plots if need be
		if not os.path.exists('Plots'):
			os.makedirs('Plots')
		
		data= pd.read_csv(file)

		#Add all the metrics to a list
		Metrics =  ["Interplate Max Distortion","Interplate Max Percentage Distortion","Interplate Coefficient Of Variation"]
		Metrics += ["Intraplate Max Distortion","Intraplate Max Percentage Distortion","Intraplate Coefficient Of Variation"]

		#Go through each metric and plot it 
		for metric in Metrics:
			plt.title(metric,fontsize=100)
			fig = plt.gcf()
			fig.set_size_inches(60, 30)
			x, y = zip(*sorted(zip(data["StudyDate"],data[metric]))) #This ensures the order of the data is in accending date
			plt.plot(x,y,linewidth=10,marker="o",markersize=60)
			plt.xlabel("Date",fontsize=60)
			plt.ylabel(metric,fontsize=60)
			plt.xticks(rotation = 45,fontsize=50)
			plt.yticks(fontsize=50)
			plt.grid(linewidth = 5)
			plt.gca().spines['bottom'].set_linewidth(10) #These make the line bounds of the plot thicker or thinner
			plt.gca().spines['left'].set_linewidth(10)
			plt.gca().spines['top'].set_linewidth(0)
			plt.gca().spines['right'].set_linewidth(0)
			plt.tight_layout()
			plt.savefig("Plots/"+self.CalcName+"_"+metric+".png")
			plt.close()
			
			
		#Do the same thing again except in this case we want X,Y and Z on the same plot
		Metrics = [
			["Interplate Max Distortion X","Interplate Max Distortion Y","Interplate Max Distortion Z"],
			["Intraplate Max Distortion X","Intraplate Max Distortion Y","Intraplate Max Distortion Z"],
			["Interplate Coefficient Of Variation X","Interplate Coefficient Of Variation Y","Interplate Coefficient Of Variation Z"],
			]
		
		for metric in Metrics:
			plt.title(metric[0] + metric[1][-1] + metric[2][-1],fontsize=100)
			fig = plt.gcf()
			fig.set_size_inches(60, 30)
			x1, y1 = zip(*sorted(zip(data["StudyDate"],data[metric[0]])))
			x2, y2 = zip(*sorted(zip(data["StudyDate"],data[metric[1]])))
			x3, y3 = zip(*sorted(zip(data["StudyDate"],data[metric[2]])))
			plt.plot(x1,y1, linewidth=10,marker="o",markersize=60,label=metric[0][-1])
			plt.plot(x2,y2, linewidth=10,marker="o",markersize=60,label=metric[1][-1])
			plt.plot(x3,y3, linewidth=10,marker="o",markersize=60,label=metric[2][-1])
			
			plt.xlabel("Date",fontsize=60)
			plt.ylabel(metric[0][:-2],fontsize=60)
			plt.xticks(rotation = 45,fontsize=50)
			plt.yticks(fontsize=50)
			plt.grid(linewidth = 5)
			plt.gca().spines['bottom'].set_linewidth(10)
			plt.gca().spines['left'].set_linewidth(10)
			plt.gca().spines['top'].set_linewidth(0)
			plt.gca().spines['right'].set_linewidth(0)
			plt.legend(prop={'size': 60})
			plt.tight_layout()
			plt.savefig("Plots/"+self.CalcName+"_"+ metric[0] + metric[1][-1] + metric[2][-1] +".png")
			plt.close()
			
		
		Metrics = [
			["Intraplate Coefficient Of Variation X","Intraplate Coefficient Of Variation Y"],
			]
		for metric in Metrics:
			plt.title(metric[0] + metric[1][-1],fontsize=100)
			fig = plt.gcf()
			fig.set_size_inches(60, 30)
			x1, y1 = zip(*sorted(zip(data["StudyDate"],data[metric[0]])))
			x2, y2 = zip(*sorted(zip(data["StudyDate"],data[metric[1]])))
			plt.plot(x1,y1, linewidth=10,marker="o",markersize=60,label=metric[0][-1])
			plt.plot(x2,y2, linewidth=10,marker="o",markersize=60,label=metric[1][-1])
			
			plt.xlabel("Date",fontsize=60)
			plt.ylabel(metric[0][:-2],fontsize=60)
			plt.xticks(rotation = 45,fontsize=50)
			plt.yticks(fontsize=50)
			plt.grid(linewidth = 5)
			plt.gca().spines['bottom'].set_linewidth(10)
			plt.gca().spines['left'].set_linewidth(10)
			plt.gca().spines['top'].set_linewidth(0)
			plt.gca().spines['right'].set_linewidth(0)
			plt.legend(prop={'size': 60})
			plt.tight_layout()
			plt.savefig("Plots/"+self.CalcName+"_"+ metric[0] + metric[1][-1]+".png")
			plt.close()
		
	#Simply print the string to screen for all the metrics
	def PrintToScreen(self):
		print (self.__GetStatString())

	#Write the metric string to a file
	def OutputToFile(self,filename):
		with open(filename, 'w') as f:
			f.write(self.__GetStatString())
	
	#Private function that computes the maximum distortion
	def __GetMaxDistortion(self, ResultsObj):
		Distortion=[]
		for result in ResultsObj.DistanceResults: #Go through each distance and find the difference between measured and expected distance 
			Distortion.append(np.abs(result.Distance - result.ExpectedDistance))
		MaxDistortion = max(Distortion) #get the largest distortion
		
		idx = Distortion.index(max(Distortion)) # and the index of the largest distortion
		return [MaxDistortion,ResultsObj.DistanceResults[idx]] #return a list where [0] is the max disotrtion value and [1] is the distanceresult object (contains the info about the given distance)
	
	#Essentially same as maxdistortiikon but works out the percentage difference
	def __GetMaxPercentageDistortion(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		MaxPercDistortion= PercentageDistortion[np.argmax(np.abs(PercentageDistortion))]*100.0
		
		idx = np.argmax(np.abs(PercentageDistortion)) #Slightly different this time since percentage can go negative find the index of the largest deviaton (ie the absoloute value)
		return [MaxPercDistortion,ResultsObj.DistanceResults[idx]]
	
	#Computes the coefficant of variation
	def __CoefficientOfVariation(self, ResultsObj):
		#The next 3 lines are the same idea as with MaxDistortion
		Distortion = [] 
		for result in ResultsObj.DistanceResults:
			if (result.ExpectedDistance == 40):
				Distortion.append(result.Distance)
		#use the scipy function to get the coefficant of variation
		return scipy.stats.variation(Distortion)
	
	
	
	#Finds the max distortion in x y and z.
	def __MaxDistortionInXYZ(self,ResultsObj):
		dx=[] #Sag
		dy=[] #Axial
		dz=[] #Cor
		
		for result in ResultsObj.DistanceResults:
			
			#Based on the location of the two points (in terms of row col and depth) find the difference, ie how far away they are
			DeltaX=np.abs(result.Point1[0]-result.Point2[0])
			DeltaY=np.abs(result.Point1[1]-result.Point2[1])
			DeltaZ=np.abs(result.Point1[2]-result.Point2[2])
			
			#Find the distance difference between the two points in x, y and z
			DX=np.abs( (result.Point1InSpace[0] - result.Point2InSpace[0])*self.DistorCalcObj.VoxelSize[2])
			DY=np.abs( (result.Point1InSpace[1] - result.Point2InSpace[1])*self.DistorCalcObj.VoxelSize[0])
			DZ=np.abs( (result.Point1InSpace[2] - result.Point2InSpace[2])*self.DistorCalcObj.VoxelSize[1])

			#Find the difference between the points and the expected distance, we know that each point is 40mm apart already
			dx.append(np.abs(DX-DeltaX*40))
			dy.append(np.abs(DY-DeltaY*40))
			dz.append(np.abs(DZ-DeltaZ*40))
			
		#get the max
		idxX = dx.index(max(dx))
		idxY = dy.index(max(dy))
		idxZ = dz.index(max(dz))
		
		#return a list where each element coresponds to x, y and z.
		result = [ [max(dx),ResultsObj.DistanceResults[idxX]] , [max(dy),ResultsObj.DistanceResults[idxY]] , [max(dz),ResultsObj.DistanceResults[idxZ] ] ]
		


		return result
	
	#Unused, it didnt make much sense since many of the distances are 0
	def __MaxPercDistortionInXYZ(self,ResultsObj):
		dx=[] #Sag
		dy=[] #Axial
		dz=[] #Cor
		
		for result in ResultsObj.DistanceResults:
			DeltaX=np.abs(result.Point1[0]-result.Point2[0])
			DeltaY=np.abs(result.Point1[1]-result.Point2[1])
			DeltaZ=np.abs(result.Point1[2]-result.Point2[2])
			
			DX=np.abs( (result.Point1InSpace[0] - result.Point2InSpace[0])*self.DistorCalcObj.VoxelSize[2])
			DY=np.abs( (result.Point1InSpace[1] - result.Point2InSpace[1])*self.DistorCalcObj.VoxelSize[0])
			DZ=np.abs( (result.Point1InSpace[2] - result.Point2InSpace[2])*self.DistorCalcObj.VoxelSize[1])

			dx.append( ((DX-DeltaX*40)/ (DeltaX*40))*100.0)
			dy.append( ((DY-DeltaY*40)/ (DeltaY*40))*100.0)
			dz.append( ((DZ-DeltaZ*40)/ (DeltaZ*40))*100.0)
			
		idxX = dx.index(max(dx))
		idxY = dy.index(max(dy))
		idxZ = dz.index(max(dz))
		
		result = [ [max(dx),ResultsObj.DistanceResults[idxX]] , [max(dy),ResultsObj.DistanceResults[idxY]] , [max(dz),ResultsObj.DistanceResults[idxZ] ] ]
		
		return result
	
	#Find the coefficant of variation in x, y and z.
	def __CoefficientOfVariationXYZ(self,ResultsObj,intra=False):
		dx=[] #Sag
		dy=[] #Axial
		dz=[] #Cor
		#This part is the asme as with the maxdistortionXYZ 
		for result in ResultsObj.DistanceResults:
			DeltaX=np.abs(result.Point1[0]-result.Point2[0])
			DeltaY=np.abs(result.Point1[1]-result.Point2[1])
			DeltaZ=np.abs(result.Point1[2]-result.Point2[2])
			
			DX=np.abs( (result.Point1InSpace[0] - result.Point2InSpace[0])*self.DistorCalcObj.VoxelSize[2])
			DY=np.abs( (result.Point1InSpace[1] - result.Point2InSpace[1])*self.DistorCalcObj.VoxelSize[0])
			DZ=np.abs( (result.Point1InSpace[2] - result.Point2InSpace[2])*self.DistorCalcObj.VoxelSize[1])

			if (DeltaX==1):
				dx.append((DX))
			if (DeltaY==1):
				dy.append((DY))
			if (DeltaZ==1):
				dz.append((DZ))
			
		#The only difference is this part where we reutnr the coefficant of variation 
		if (intra==False):
			return [scipy.stats.variation(dx),scipy.stats.variation(dy),scipy.stats.variation(dz)]
		else:		
			return [scipy.stats.variation(dx),scipy.stats.variation(dy)]
		
	#This function is called by the user to analyse the distances
	def DistortionAnalysis (self):
		print ("Computing: " + self.CalcName)
		self.DistorCalcObj.InterPlateResults.Image.savefig(self.CalcName+"_InterplateDistances.png") #save the interplate image
		platenum=1
		#save each intraplate image
		for result in self.DistorCalcObj.IntraPlateResults:
			result.Image.savefig(self.CalcName+"_Plate_"+str(platenum)+"_IntraPlateDist.png")
			platenum+=1
			
		
		#Inter results, compute the metric and put it in the dictonary
		self.Results["Interplate Max Distortion"] = self.__GetMaxDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Max Percentage Distortion"] = self.__GetMaxPercentageDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Coefficient Of Variation"] = self.__CoefficientOfVariation(self.DistorCalcObj.InterPlateResults)
		
		XYZResult = self.__MaxDistortionInXYZ(self.DistorCalcObj.InterPlateResults) #Remember this returns a list of for x y and z 
		self.Results["Interplate Max Distortion X"] = XYZResult[0]
		self.Results["Interplate Max Distortion Y"] = XYZResult[1]
		self.Results["Interplate Max Distortion Z"] = XYZResult[2]
		
		XYZResult = self.__CoefficientOfVariationXYZ(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Coefficient Of Variation X"] = XYZResult[0]
		self.Results["Interplate Coefficient Of Variation Y"] = XYZResult[1]
		self.Results["Interplate Coefficient Of Variation Z"] = XYZResult[2]
		
		
		
		#Inter results, compute the metric and put it in the dictonary
		self.Results["Intraplate Max Distortion"] = []
		self.Results["Intraplate Max Percentage Distortion"] = []
		self.Results["Intraplate Coefficient Of Variation"] = []
		
		self.Results["Intraplate Max Distortion X"] = []
		self.Results["Intraplate Max Distortion Y"] = []
		self.Results["Intraplate Max Distortion Z"] = []
		
		self.Results["Intraplate Coefficient Of Variation X"] = []
		self.Results["Intraplate Coefficient Of Variation Y"] = []
		#self.Results["Intraplate Coefficient Of Variation Z"] = []
		
		count =0 
		for plate in self.DistorCalcObj.IntraPlateResults: # we need to go through each plate
			self.Results["Intraplate Max Distortion"].append(self.__GetMaxDistortion(plate))
			self.Results["Intraplate Max Percentage Distortion"].append(self.__GetMaxPercentageDistortion(plate))
			if count>0:#Ignore the first plate since it has no 40mm distances...
				self.Results["Intraplate Coefficient Of Variation"].append(self.__CoefficientOfVariation(plate))
			
			XYZResult = self.__MaxDistortionInXYZ(plate)
			self.Results["Intraplate Max Distortion X"].append(XYZResult[0])
			self.Results["Intraplate Max Distortion Y"].append(XYZResult[1])
			self.Results["Intraplate Max Distortion Z"].append(XYZResult[2])
			
			XYZResult = self.__CoefficientOfVariationXYZ(plate,True)
			self.Results["Intraplate Coefficient Of Variation X"].append(XYZResult[0])
			self.Results["Intraplate Coefficient Of Variation Y"].append(XYZResult[1])
			#self.Results["Intraplate Coefficient Of Variation Z"].append(XYZResult[2])
			count+=1
		
