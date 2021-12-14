#Analysis Script
import Compute_Distortion
import numpy as np
from dataclasses import dataclass
import scipy
import sys 
import matplotlib.pyplot as plt

class AnalysisResults:
	def __init__(self,CalcName,DistorCalcObj):
		self.Results = {}	
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
		

	def PrintToScreen(self):
		print("Interplate Max Distortion: " + str(self.Results["Interplate Max Distortion"]) +" mm")
		print("Interplate Max Percentage Distortion: " + str(self.Results["Interplate Max Percentage Distortion"]) +" %")
		print("Interplate Coefficient Of Variation: " + str(self.Results["Interplate Coefficient Of Variation"]) +" %")
		
		print("Intraplate Max Distortion: " + str(max(self.Results["Intraplate Max Distortion"])) +" mm")
		print("Intraplate Max Percentage Distortion: " + str(max(self.Results["Intraplate Max Percentage Distortion"])) +" %")
		print("Intraplate Coefficient Of Variation: " + str(max(self.Results["Intraplate Coefficient Of Variation"])))
	
	def GetMaxDistortion(self, ResultsObj):
		Distortion=[]
		for result in ResultsObj.DistanceResults:
			Distortion.append(np.abs(result.Distance - result.ExpectedDistance))
		MaxDistortion = max(Distortion)
		return MaxDistortion
	
	
	def GetMaxPercentageDistortion(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		MaxPercDistortion= PercentageDistortion[np.argmax(np.abs(PercentageDistortion))]*100.0
		return MaxPercDistortion
	
	def CoefficantOfVariation(self, ResultsObj):
		PercentageDistortion = []
		for result in ResultsObj.DistanceResults:
			PercentageDistortion.append( (result.Distance - result.ExpectedDistance)/result.ExpectedDistance)
		return scipy.stats.variation(PercentageDistortion)
	
	
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
			
		
		
		
		#AnalysisResultobjIntra=AnalyseDistances(DistorCalcObj.IntraPlateResults)
		
	
		


