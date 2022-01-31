#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys

#Just for the example script make sure the csv file is gone so we dont just add to it..
import os
if os.path.exists("DistortionData.csv"):
	os.remove("DistortionData.csv")

#Compute distortion on one sequence
#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 

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

#Call this function to save the metric data to a csv that is updated for each run
NoDistortionAnalysis.OutputPeriodicData("DistortionData.csv")





#Compute distortion on another sequence (this could be in another file)
#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeNoCorrection = Compute_Distortion.DistortionCalculation("TestDataNoCor" , "3D Sag T1 BRAVO") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
NoCorrectionAnalysis = Analysis.AnalysisResults("No_Correction",ComputeNoCorrection)

#Call this function to get all the centre of the distances
ComputeNoCorrection.GetFudicalSpheres()

#Call this function to calculate the distances
ComputeNoCorrection.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
NoCorrectionAnalysis.DistortionAnalysis()

#Call this function to print the computed metrics to screen
NoCorrectionAnalysis.PrintToScreen()

#Call this function to save the metric data to a csv that is updated for each run
NoCorrectionAnalysis.OutputPeriodicData("DistortionData.csv")



#Compute distortion on another sequence (this could be in another file)
#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortion = Compute_Distortion.DistortionCalculation("TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
DistortionAnalysis = Analysis.AnalysisResults("Distorted",ComputeDistortion)

#Call this function to get all the centre of the distances
ComputeDistortion.GetFudicalSpheres()

#Call this function to calculate the distances
ComputeDistortion.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
DistortionAnalysis.DistortionAnalysis()

#Call this function to print the computed metrics to screen
DistortionAnalysis.PrintToScreen()

#Call this function to save the metric data to a csv that is updated for each run
DistortionAnalysis.OutputPeriodicData("DistortionData.csv")




#Plot the csv so we can see data over time, check the Plot folder
NoDistortionAnalysis.PlotCSV("DistortionData.csv")