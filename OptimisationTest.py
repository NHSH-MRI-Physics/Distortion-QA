#Quickstart script

import Analysis
import Compute_Distortion
import sys
from scipy.optimize import minimize_scalar
import os
from scipy.optimize import show_options

Paths = []
Paths.append(os.path.join(os.getcwd(),"TestData","NormTestData"))
Paths.append(os.path.join(os.getcwd(),"TestData","TestDataNoCor"))
Paths.append(os.path.join(os.getcwd(),"TestData","TestDistoredData")) 
Paths.append(os.path.join(os.getcwd(),"TestData","TestRealData"))

seq = ["3D Sag T1 BRAVO Geom Core","3D Sag T1 BRAVO","3D Sag T1 BRAVO BW=15 Shim off","3D Sag T1 BRAVO DL"]



for i in range(4):
    ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(Paths[i] ,seq[i]) 
    maxpixel = ComputeDistortionGeoCorrection.GetMaxPixel()

    def test(thresh):
        ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation(Paths[i] ,seq[i]) 
        ComputeDistortionGeoCorrection.Threshold = thresh
        ComputeDistortionGeoCorrection.BinariseMethod = "Constant"
        NoDistortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)
        ComputeDistortionGeoCorrection.GetFudicalSpheres()
        ComputeDistortionGeoCorrection.GetDistances()
        NoDistortionAnalysis.DistortionAnalysis()
        #NoDistortionAnalysis.PrintToScreen()
        return ComputeDistortionGeoCorrection.ErrorMetric


    res = minimize_scalar(test,bounds=(maxpixel*0.1,maxpixel*0.5),options = {"disp": 3,"xatol": 10,"maxiter":50})
    print(res)