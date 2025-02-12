#Quickstart script

import Analysis
import Compute_Distortion
import sys

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDist = Compute_Distortion.DistortionCalculation("./TestData/NormTestData" , "3D Sag T1 BRAVO Geom Core") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
AnalysisValTesting = Analysis.AnalysisResults("ValTesting",ComputeDist)

#Call this function to get all the centre of the distances
ComputeDist.GetFudicalSpheres()

for point in ComputeDist.SphereLocations[0]:
    print (point)

#Call this function to calculate the distances
ComputeDist.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
AnalysisValTesting.DistortionAnalysis()

#Call this function to print the computed metrics to screen
AnalysisValTesting.PrintToScreen()


for i in AnalysisValTesting.DistorCalcObj.IntraPlateResults[0].DistanceResults:
    print(i)