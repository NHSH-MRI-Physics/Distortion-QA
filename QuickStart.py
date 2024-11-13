#Quickstart script

import Analysis
import Compute_Distortion
import sys

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("./TestData" , "3D Sag T1 BRAVO Geom Core") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
NoDistortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)

#Call this function to get all the centre of the distances
ComputeDistortionGeoCorrection.GetFudicalSpheres()

#Call this function to calculate the distances
ComputeDistortionGeoCorrection.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
NoDistortionAnalysis.DistortionAnalysis()

#Call this function to print the computed metrics to screen
NoDistortionAnalysis.PrintToScreen()

print(ComputeDistortionGeoCorrection.BinaryWarningThreshToHigh)
print(ComputeDistortionGeoCorrection.BinaryWarningThreshToLow)