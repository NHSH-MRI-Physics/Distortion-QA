
import Analysis
import Compute_Distortion
import sys
from scipy.optimize import minimize_scalar
from scipy.optimize import show_options
import unittest
import numpy as np
class TestStringMethods(unittest.TestCase):
    def testNormal(self):
        for i in range(100):
            ComputeDist = Compute_Distortion.DistortionCalculation("./TestData" , "3D Sag T1 BRAVO Geom Core") 
            ComputeDist.BinariseMethod = "Constant"
            ComputeDist.Threshold=int(3000)
            AnalysisObj = Analysis.AnalysisResults("No_Distortion",ComputeDist)
            ComputeDist.GetFudicalSpheres()
            print(ComputeDist.SphereLocations)

            #ComputeDist.GetDistances()
            #AnalysisObj.DistortionAnalysis()

            print (AnalysisObj.Results['Interplate Max Distortion'][0],AnalysisObj.Results['Interplate Max Percentage Distortion'][0],AnalysisObj.Results['Interplate Coefficient Of Variation'])
            #np.save("NoDist.npy",AnalysisObj.Results,allow_pickle=True)

            TestResults = np.load("NoDist.npy",allow_pickle=True).item()     

            #self.assertEqual(AnalysisObj.Results['Interplate Max Distortion'], TestResults['Interplate Max Distortion'])
            #self.assertEqual(AnalysisObj.Results['Interplate Max Percentage Distortion'], TestResults['Interplate Max Percentage Distortion'])
            #self.assertEqual(AnalysisObj.Results['Interplate Coefficient Of Variation'], TestResults['Interplate Coefficient Of Variation'])

            #self.assertEqual(AnalysisObj.Results['Intraplate Max Distortion'], TestResults['Intraplate Max Distortion'])
            #self.assertEqual(AnalysisObj.Results['Intraplate Max Percentage Distortion'], TestResults['Intraplate Max Percentage Distortion'])
            #self.assertEqual(AnalysisObj.Results['Intraplate Coefficient Of Variation'], TestResults['Intraplate Coefficient Of Variation'])

#ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("./TestDataNoCor" , "3D Sag T1 BRAVO") 
#ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("./TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off") 