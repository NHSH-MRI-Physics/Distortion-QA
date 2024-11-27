#Quickstart script

import Analysis
import Compute_Distortion
import sys
from scipy.optimize import minimize_scalar
import os
from scipy.optimize import show_options

#path = os.path.join(os.getcwd(),"TestData","NormTestData")
#path = os.path.join(os.getcwd(),"TestData","TestDataNoCor")
path = os.path.join(os.getcwd(),"TestData","TestDistoredData") 
#path = os.path.join(os.getcwd(),"TestData","TestRealData") 
offset = 0
def test(thresh):
    #Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
    #ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO Geom Core") 
    #ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO") 
    ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO BW=15 Shim off") 
    #ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO DL") 

    ComputeDistortionGeoCorrection.Threshold = thresh
    ComputeDistortionGeoCorrection.BinariseMethod = "Constant"
    #Set up the analysis script, this takes the computed distacnes and output metrics. Pass a tag for the calculaton (used for naming saved images etc) and the previously constructed distirtion calc class
    NoDistortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)

    #Call this function to get all the centre of the distances
    ComputeDistortionGeoCorrection.GetFudicalSpheres()
    #print(ComputeDistortionGeoCorrection.BinaryWarningThreshToHigh,ComputeDistortionGeoCorrection.BinaryWarningThreshToLow)

    ComputeDistortionGeoCorrection.GetDistances()
    NoDistortionAnalysis.DistortionAnalysis()
    NoDistortionAnalysis.PrintToScreen()

    return ComputeDistortionGeoCorrection.ErrorMetric

#ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO Geom Core") 
#ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO") 
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO BW=15 Shim off") 
#ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO DL") 
maxpixel = ComputeDistortionGeoCorrection.GetMaxPixel()
res = minimize_scalar(test,bounds=(maxpixel*0.1,maxpixel*0.5),options = {"disp": 3,"xatol": 10,"maxiter":50})
print(res)

#Call this function to calculate the distances
#ComputeDistortionGeoCorrection.GetDistances()

#Call this functuion to analyse the distances and compute the metrics
#NoDistortionAnalysis.DistortionAnalysis()

#Call this function to print the computed metrics to screen
#NoDistortionAnalysis.PrintToScreen()
