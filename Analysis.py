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
		
	def key_event(self,e):
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
		self.fig.canvas.mpl_connect('key_press_event', self.key_event)
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

	def PrintToScreen(self):
		print("Interplate Max Distortion: " + str(self.Results["Interplate Max Distortion"][0]) +" mm")
		print("Interplate Max Percentage Distortion: " + str(self.Results["Interplate Max Percentage Distortion"][0]) +" %")
		print("Interplate Coefficient Of Variation: " + str(self.Results["Interplate Coefficient Of Variation"]) +" %")
		
		print (  )
		
		print("Intraplate Max Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Distortion"])) +" mm")
		print("Intraplate Max Percentage Distortion: " + str(max(x[0] for x in self.Results["Intraplate Max Percentage Distortion"])) +" %")
		print("Intraplate Coefficient Of Variation: " + str(max(self.Results["Intraplate Coefficient Of Variation"])))
	
	def GetMaxDistortion(self, ResultsObj):
		Distortion=[]
		for result in ResultsObj.DistanceResults:
			Distortion.append(np.abs(result.Distance - result.ExpectedDistance))
		MaxDistortion = max(Distortion)
		
		idx = Distortion.index(max(Distortion))
		return [MaxDistortion,ResultsObj.DistanceResults[idx]]
	
	
	def GetMaxPercentageDistortion(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		MaxPercDistortion= PercentageDistortion[np.argmax(np.abs(PercentageDistortion))]*100.0
		
		idx = np.argmax(np.abs(PercentageDistortion))
		return [MaxPercDistortion,ResultsObj.DistanceResults[idx]]
	
	def CoefficantOfVariation(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		return scipy.stats.variation(PercentageDistortion)
	
	def MaxDistortionInXYZ(self,ResultsObj):
		dx=[] #Sag
		dy=[] #Axial
		dz=[] #Cor
		for result in ResultsObj.DistanceResults:
			
			DeltaX=np.abs(result.Point1[0]-result.Point2[0])
			DeltaY=np.abs(result.Point1[0]-result.Point2[0])
			DeltaZ=np.abs(result.Point1[0]-result.Point2[0])
			
			DX=np.abs(result.Point1InSpace[0] - result.Point2InSpace[0])
			DY=np.abs(result.Point1InSpace[1] - result.Point2InSpace[1])
			DZ=np.abs(result.Point1InSpace[2] - result.Point2InSpace[2])
			

			sys.exit()
			dx.append(np.abs(DX-DeltaX*40))
			dy.append(np.abs(DY-DeltaY*40))
			dz.append(np.abs(DZ-DeltaZ*40))
			
			
		
	
	def DistortionAnalysis (self):
		print ("Computing: " + self.CalcName)
		#self.DistorCalcObj.GetFudicalSpheres()
		self.DistorCalcObj.InterPlateResults.Image.savefig(self.CalcName+"_InterplateDistances.png")
		platenum=1
		for result in self.DistorCalcObj.IntraPlateResults:
			result.Image.savefig(self.CalcName+"_Plate_"+str(platenum)+"_IntraPlateDist.png")
			platenum+=1
			
		
		
		self.Results["Interplate Max Distortion"] = self.GetMaxDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Max Percentage Distortion"] = self.GetMaxPercentageDistortion(self.DistorCalcObj.InterPlateResults)
		self.Results["Interplate Coefficient Of Variation"] = self.CoefficantOfVariation(self.DistorCalcObj.InterPlateResults)
		
		self.Results["Intraplate Max Distortion"] = []
		self.Results["Intraplate Max Percentage Distortion"] = []
		self.Results["Intraplate Coefficient Of Variation"] = []
		for plate in self.DistorCalcObj.IntraPlateResults:
			self.Results["Intraplate Max Distortion"].append(self.GetMaxDistortion(plate))
			self.Results["Intraplate Max Percentage Distortion"].append(self.GetMaxPercentageDistortion(plate))
			self.Results["Intraplate Coefficient Of Variation"].append(self.CoefficantOfVariation(plate))
			
		self.MaxDistortionInXYZ(self.DistorCalcObj.InterPlateResults)
		
		
		#AnalysisResultobjIntra=AnalyseDistances(DistorCalcObj.IntraPlateResults)
		
	
		


