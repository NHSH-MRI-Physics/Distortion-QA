#Analysis Script
import Compute_Distortion
import numpy as np
from dataclasses import dataclass


class AnalysisResults:
	def __init__(self,CalcName,DistorCalcObj):
		self.Results = {}	
		self.CalcName = CalcName
		self.DistorCalcObj=DistorCalcObj

	def PrintToScreen(self):
		print("Interplate Max Distortion: " + str(self.Results["Interplate Max Distortion"]) +" mm")
		print("Interplate Max Percentage Distortion: " + str(self.Results["Interplate Max Percentage Distortion"]) +" %")
		
		print("Intraplate Max Distortion: " + str(max(self.Results["Intraplate Max Distortion"])) +" mm")
		print("Intraplate Max Percentage Distortion: " + str(max(self.Results["Intraplate Max Percentage Distortion"])) +" %")
	
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
		
		self.Results["Intraplate Max Distortion"] = []
		self.Results["Intraplate Max Percentage Distortion"] = []
		for plate in self.DistorCalcObj.IntraPlateResults:
			self.Results["Intraplate Max Distortion"].append(self.GetMaxDistortion(plate))
			self.Results["Intraplate Max Percentage Distortion"].append(self.GetMaxPercentageDistortion(plate))
			
		
		
		
		#AnalysisResultobjIntra=AnalyseDistances(DistorCalcObj.IntraPlateResults)
		
	
		


