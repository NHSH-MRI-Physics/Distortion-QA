#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
NoDitsortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)

#Call this function to get all the centre of the distances
ComputeDistortionGeoCorrection.GetFudicalSpheres()

#Call this function to check the points which have been found, shows a plotting dialog you can navigate with right/left keyboard arrows
#NoDitsortionAnalysis.CheckPoints()

#Call this function to calculate the distances
ComputeDistortionGeoCorrection.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
NoDitsortionAnalysis.DistortionAnalysis()

#Call this function to print the computed metrics to screen
NoDitsortionAnalysis.PrintToScreen()

#Call this function to save the metric data to a csv that is updated for each run
#NoDitsortionAnalysis.OutputPeriodicData("DistortionData.csv")

#Plot the csv so we cna see data over time
NoDitsortionAnalysis.PlotCSV("DistortionData.csv")