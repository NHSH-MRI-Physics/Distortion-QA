#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys

#Default
ComputeDistortion = Compute_Distortion.DistortionCalculation(".\TestData\NormTestData" , "3D Sag T1 BRAVO Geom Core") 
Analyse = Analysis.AnalysisResults("Default",ComputeDistortion)
ComputeDistortion.GetFudicalSpheres()
ComputeDistortion.GetDistances()
Analyse.DistortionAnalysis()
Analyse.PrintToScreen()

#Constant
ComputeDistortion = Compute_Distortion.DistortionCalculation(".\TestData\NormTestData" , "3D Sag T1 BRAVO Geom Core") 
ComputeDistortion.Threshold = 3000
ComputeDistortion.BinariseMethod = "Constant"
Analyse = Analysis.AnalysisResults("Constant",ComputeDistortion)
ComputeDistortion.GetFudicalSpheres()
ComputeDistortion.GetDistances()
Analyse.DistortionAnalysis()
Analyse.PrintToScreen()

#Ratio
ComputeDistortion = Compute_Distortion.DistortionCalculation(".\TestData\NormTestData" , "3D Sag T1 BRAVO Geom Core") 
ComputeDistortion.BinariseMethod = "RatioOfMax"
ComputeDistortion.ratio=0.3
Analyse = Analysis.AnalysisResults("RatioOfMax",ComputeDistortion)
ComputeDistortion.GetFudicalSpheres()
ComputeDistortion.GetDistances()
Analyse.DistortionAnalysis()
Analyse.PrintToScreen()

#IslandChecker
ComputeDistortion = Compute_Distortion.DistortionCalculation(".\TestData\NormTestData" , "3D Sag T1 BRAVO Geom Core") 
#The isaldnChecker method is a bit more sensitive to background noise so its usually good to shortern the search width
ComputeDistortion.searchWidth = 3.9
ComputeDistortion.BinariseMethod = "IslandChecker"
Analyse = Analysis.AnalysisResults("IslandChecker",ComputeDistortion)
ComputeDistortion.GetFudicalSpheres()
ComputeDistortion.GetDistances()
Analyse.DistortionAnalysis()
Analyse.PrintToScreen()
