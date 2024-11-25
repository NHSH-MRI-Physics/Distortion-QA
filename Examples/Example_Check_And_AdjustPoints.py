import Analysis
import Compute_Distortion
import sys

#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(".\TestData\NormTestData" , "3D Sag T1 BRAVO Geom Core") 

#Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
NoDitsortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)

#Call this function to get all the centre of the distances
ComputeDistortionGeoCorrection.GetFudicalSpheres()

#Call this function to check the points which have been found, shows a plotting dialog you can navigate with right/left keyboard arrows
#Look at the points on slice 85 and 86
NoDistortionAnalysis.CheckPoints()

# move the point x=118,y=262,slice=85 to x=120.1,y=262.4,slice=86
ComputeDistortionGeoCorrection.AdjustPoint([118,262,85],[120.1,262.4,86])
# move the point x=182,y=174,slice=85 to x=182.5,y=173.3,slice=86
ComputeDistortionGeoCorrection.AdjustPoint([182,174,85],[183.5,173.3,86])

#Now lets check how the point has moved to slice 86
NoDistortionAnalysis.CheckPoints()