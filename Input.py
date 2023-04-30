#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys
import SNRCalc

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortion = Compute_Distortion.DistortionCalculation("TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off") 

#The isaldnChecker method is a bit more sensitive to background noise so its usually good to shortern the search width
#ComputeDistortion.searchWidth = 3.9

#This function lets you check each binary image but its alot of images...
ComputeDistortion.checkBinaryImages=False

#Set the method to binarise
ComputeDistortion.BinariseMethod = "Constant"
#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
Analyse = Analysis.AnalysisResults("FlippedData",ComputeDistortion)
ComputeDistortion.Threshold=5000
#Call this function to get all the centre of the distances
ComputeDistortion.GetFudicalSpheres()

#Call this function to check the points which have been found, shows a plotting dialog you can navigate with right/left keyboard arrows
#Analyse.CheckPoints()

#Call this function to calculate the distances
ComputeDistortion.GetDistances()

##Call this functuion to analyse the distances and compute the metrics
Analyse.DistortionAnalysis()

#Call this function to print the computed metrics to screen
Analyse.PrintToScreen()

SNR = SNRCalc.SNR(ComputeDistortion)
SNR.ComputerSNR()