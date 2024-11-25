import Analysis
import Compute_Distortion
import sys

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
NoDistortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)

#Call this function to get all the centre of the distances
ComputeDistortionGeoCorrection.GetFudicalSpheres()

#Call this function to calculate the distances
ComputeDistortionGeoCorrection.GetDistances()

#Call this function to analyse the distances and compute the metrics
NoDistortionAnalysis.DistortionAnalysis()

print (NoDistortionAnalysis.GetMetrics())

#Show just the 3d model
NoDistortionAnalysis.Show3dModel()

#Show just the 3d model with the max interplate distortion shown
NoDistortionAnalysis.Show3dModel("Interplate Max Distortion")

#Show just the 3d model with the max intraplate distortion shown
NoDistortionAnalysis.Show3dModel("Intraplate Max Distortion")