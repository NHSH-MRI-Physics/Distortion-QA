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

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)


class AnalysisResults:
	def __init__(self,CalcName,DistorCalcObj):
		self.Results = {}	
		self.ResultConnectingPoint={}
		self.CalcName = CalcName
		self.DistorCalcObj=DistorCalcObj
		self.ax=None
		self.fig=None
		self.curr_pos=0
		
	def __key_event(self,e):
		if e.key == "right":
			self.curr_pos = self.curr_pos + 1
		elif e.key == "left":
			self.curr_pos = self.curr_pos - 1
		else:
			return
		
		self.ax.cla()
		for plate in self.DistorCalcObj.SphereLocations:
			for point in plate:
				if (int(round(point[2]))==self.curr_pos):
					self.ax.plot(point[0], point[1], 'b+')
		
		
		self.ax.imshow(self.DistorCalcObj.GetCorSlice(self.curr_pos))
		self.fig.suptitle("Slice Number " + str(self.curr_pos))
		self.fig.canvas.draw()

		
	def CheckPoints(self):
		self.fig = plt.figure()
		self.fig.canvas.mpl_connect('key_press_event', self.__key_event)
		self.ax = self.fig.add_subplot(111)
		self.ax.imshow(self.DistorCalcObj.GetCorSlice(0))
		self.fig.suptitle("Slice Number " + str(self.curr_pos))
		plt.show()
		
	def Show3dModel(self,metric=None):
		fig = plt.figure()
		ax = fig.gca(projection='3d')
		ax.set_aspect("auto")
		
		ax.set_zlabel('Coronal', fontsize=20)
		ax.set_ylabel('Axial', fontsize=20)
		ax.set_xlabel('Sagittal', fontsize=20)
		
		colours = ["r","g","b","m","y"]
		count =0
		MidPoint = [self.DistorCalcObj.img_shape[0]/2.0,self.DistorCalcObj.img_shape[1]/2.0,self.DistorCalcObj.img_shape[2]/2.0]
		for plate in self.DistorCalcObj.SphereLocations:
			for point in plate:
				ax.scatter( (point[0])*self.DistorCalcObj.VoxelSize[2], (point[1])*self.DistorCalcObj.VoxelSize[0], (point[2])*self.DistorCalcObj.VoxelSize[1], color=colours[count], s=100)
			count+=1
		
		plt.title("3d Plot")
		if (metric != None):
			
			if metric not in self.Results:
				raise ValueError('Metric Not Found!')
			
			plt.title(metric)
			
			result = self.Results[metric]
			if "Inter" in metric:
				result=[result]
			count =0
			for dist in result: 
				Point1 = dist[1].Point1InSpace
				Point2 = dist[1].Point2InSpace
				
				Point1[0]*=self.DistorCalcObj.VoxelSize[2]
				Point1[1]*=self.DistorCalcObj.VoxelSize[0]
				Point1[2]*=self.DistorCalcObj.VoxelSize[1]
				
				Point2[0]*=self.DistorCalcObj.VoxelSize[2]
				Point2[1]*=self.DistorCalcObj.VoxelSize[0]
				Point2[2]*=self.DistorCalcObj.VoxelSize[1]
				
				arw = Arrow3D([Point1[0],Point2[0]],[Point1[1],Point2[1]],[Point1[2],Point2[2]], arrowstyle="->", color=colours[count], lw = 3, mutation_scale=25)
				ax.add_artist(arw)
				count+=1
		
		plt.show()
		
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
		output+= ("Intraplate Stats")
		output+=("Intraplate Max Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion"])) +" mm\n")
		output+=("Intraplate Max Percentage Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Percentage Distortion"])) +"\n" )
		output+=("Intraplate Coefficient Of Variation: " + str(max(self.Results["Intraplate Coefficient Of Variation"]))+"\n")
		
		output+=("Intraplate Max Distortion X: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion X"])) +" mm\n")
		output+=("Intraplate Max Distortion Y: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion Y"])) +" mm\n")
		output+=("Intraplate Max Distortion Z: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion Z"])) +" mm\n")
		
		output+=("Intraplate Coefficient Of Variation X: " + str(max(self.Results["Intraplate Coefficient Of Variation X"]))+"\n")
		output+=("Intraplate Coefficient Of Variation Y: " + str(max(self.Results["Intraplate Coefficient Of Variation Y"]))+"\n")
		output+=("Intraplate Coefficient Of Variation Z: " + str(max(self.Results["Intraplate Coefficient Of Variation Z"]))+"\n")
		
		output+= ("\n")
		
		return output
	
	def OutputPeriodicData(self, file):
		Metrics = ["StudyDate"]
		for key in self.Results.keys():
			Metrics.append(key)
			
		if os.path.isfile(file) == False:
			f=open(file,'w')
			string=""
			for value in Metrics:
				string+=value+","
			string=string[:-1]
			f.write(string+"\n")
			f.close()
		string =""
		for value in Metrics:
			if value == "StudyDate":
				string+=str(self.DistorCalcObj.Studydate)+","
			else:
				if "Inter" in value:
					if  ("Coefficient Of Variation" not in value):
						string+=str(self.Results[value][0])+","
					else:
						string+=str(self.Results[value])+","
				if "Intra" in value:
					if  ("Coefficient Of Variation" not in value):
						string+=str(max(x[0] for x in self.Results[value]))+","
					else:
						string+=str(max(self.Results[value]))+","


		string=string[:-1]
		string+="\n"
		with open(file, "a") as fileAppend:
			fileAppend.write(string)

	def PlotCSV(self,file):
		if not os.path.exists('Plots'):
			os.makedirs('Plots')
		
		data= pd.read_csv(file)

		Metrics =  ["Interplate Max Distortion","Interplate Max Percentage Distortion","Interplate Coefficient Of Variation"]
		Metrics += ["Intraplate Max Distortion","Intraplate Max Percentage Distortion","Intraplate Coefficient Of Variation"]

		for metric in Metrics:
			plt.title(metric,fontsize=100)
			fig = plt.gcf()
			fig.set_size_inches(60, 30)
			x, y = zip(*sorted(zip(data["StudyDate"],data[metric])))
			plt.plot(x,y,linewidth=10,marker="o",markersize=60)
			plt.xlabel("Date",fontsize=60)
			plt.ylabel(metric,fontsize=60)
			plt.xticks(rotation = 45,fontsize=50)
			plt.yticks(fontsize=50)
			plt.grid(linewidth = 5)
			plt.gca().spines['bottom'].set_linewidth(10)
			plt.gca().spines['left'].set_linewidth(10)
			plt.gca().spines['top'].set_linewidth(0)
			plt.gca().spines['right'].set_linewidth(0)
			plt.tight_layout()
			plt.savefig("Plots/"+self.CalcName+"_"+metric+".png")
			plt.close()
			
		Metrics = [
			["Interplate Max Distortion X","Interplate Max Distortion Y","Interplate Max Distortion Z"],
			["Intraplate Max Distortion X","Intraplate Max Distortion Y","Intraplate Max Distortion Z"],
			["Interplate Coefficient Of Variation X","Interplate Coefficient Of Variation Y","Interplate Coefficient Of Variation Z"],
			["Intraplate Coefficient Of Variation X","Intraplate Coefficient Of Variation Y","Intraplate Coefficient Of Variation Z"],
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
		
		
	def PrintToScreen(self):
		print (self.__GetStatString())

	def OutputToFile(self,filename):
		with open(filename, 'w') as f:
			f.write(self.__GetStatString())
	
	def __GetMaxDistortion(self, ResultsObj):
		Distortion=[]
		for result in ResultsObj.DistanceResults:
			Distortion.append(np.abs(result.Distance - result.ExpectedDistance))
		MaxDistortion = max(Distortion)
		
		idx = Distortion.index(max(Distortion))
		return [MaxDistortion,ResultsObj.DistanceResults[idx]]
	
	
	def __GetMaxPercentageDistortion(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		MaxPercDistortion= PercentageDistortion[np.argmax(np.abs(PercentageDistortion))]*100.0
		
		idx = np.argmax(np.abs(PercentageDistortion))
		return [MaxPercDistortion,ResultsObj.DistanceResults[idx]]
	
	def __CoefficantOfVariation(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance))
		return scipy.stats.variation(PercentageDistortion)
	
	
	
	
	def __MaxDistortionInXYZ(self,ResultsObj):
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

			dx.append(np.abs(DX-DeltaX*40))
			dy.append(np.abs(DY-DeltaY*40))
			dz.append(np.abs(DZ-DeltaZ*40))
			
		idxX = dx.index(max(dx))
		idxY = dy.index(max(dy))
		idxZ = dz.index(max(dz))
		
		result = [ [max(dx),ResultsObj.DistanceResults[idxX]] , [max(dy),ResultsObj.DistanceResults[idxY]] , [max(dz),ResultsObj.DistanceResults[idxZ] ] ]
		
		return result
	
	
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
	
	def __CoefficantOfVariationXYZ(self,ResultsObj):
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

			dx.append((DX-DeltaX*40))
			dy.append((DY-DeltaY*40))
			dz.append((DZ-DeltaZ*40))
			
		return [scipy.stats.variation(dx),scipy.stats.variation(dy),scipy.stats.variation(dz)]
		
		
	
	def DistortionAnalysis (self):
		print ("Computing: " + self.CalcName)
		self.DistorCalcObj.InterPlateResults.Image.savefig(self.CalcName+"_InterplateDistances.png")
		platenum=1
		for result in self.DistorCalcObj.IntraPlateResults:
			result.Image.savefig(self.CalcName+"_Plate_"+str(platenum)+"_IntraPlateDist.png")
			platenum+=1
			
		
		#Inter results
		self.Results["Interplate Max Distortion"] = self.__GetMaxDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Max Percentage Distortion"] = self.__GetMaxPercentageDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Coefficient Of Variation"] = self.__CoefficantOfVariation(self.DistorCalcObj.InterPlateResults)
		
		XYZResult = self.__MaxDistortionInXYZ(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Max Distortion X"] = XYZResult[0]
		self.Results["Interplate Max Distortion Y"] = XYZResult[1]
		self.Results["Interplate Max Distortion Z"] = XYZResult[2]
		
		XYZResult = self.__CoefficantOfVariationXYZ(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Coefficient Of Variation X"] = XYZResult[0]
		self.Results["Interplate Coefficient Of Variation Y"] = XYZResult[1]
		self.Results["Interplate Coefficient Of Variation Z"] = XYZResult[2]
		
		
		
		#Intra results
		self.Results["Intraplate Max Distortion"] = []
		self.Results["Intraplate Max Percentage Distortion"] = []
		self.Results["Intraplate Coefficient Of Variation"] = []
		
		self.Results["Intraplate Max Distortion X"] = []
		self.Results["Intraplate Max Distortion Y"] = []
		self.Results["Intraplate Max Distortion Z"] = []
		
		self.Results["Intraplate Coefficient Of Variation X"] = []
		self.Results["Intraplate Coefficient Of Variation Y"] = []
		self.Results["Intraplate Coefficient Of Variation Z"] = []
		
		for plate in self.DistorCalcObj.IntraPlateResults:
			self.Results["Intraplate Max Distortion"].append(self.__GetMaxDistortion(plate))
			self.Results["Intraplate Max Percentage Distortion"].append(self.__GetMaxPercentageDistortion(plate))
			self.Results["Intraplate Coefficient Of Variation"].append(self.__CoefficantOfVariation(plate))
			
			XYZResult = self.__MaxDistortionInXYZ(plate)
			self.Results["Intraplate Max Distortion X"].append(XYZResult[0])
			self.Results["Intraplate Max Distortion Y"].append(XYZResult[1])
			self.Results["Intraplate Max Distortion Z"].append(XYZResult[2])
			
			XYZResult = self.__CoefficantOfVariationXYZ(plate)
			self.Results["Intraplate Coefficient Of Variation X"].append(XYZResult[0])
			self.Results["Intraplate Coefficient Of Variation Y"].append(XYZResult[1])
			self.Results["Intraplate Coefficient Of Variation Z"].append(XYZResult[2])
		

		

		
		
	
		


