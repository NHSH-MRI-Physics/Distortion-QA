
import Analysis
import Compute_Distortion
import sys
from scipy.optimize import minimize_scalar
from scipy.optimize import show_options
import unittest
import numpy as np
class TestStringMethods(unittest.TestCase):
    def testNormal(self):
        ComputeDist = Compute_Distortion.DistortionCalculation("./TestData" , "3D Sag T1 BRAVO Geom Core") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("No_Distortion",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        #np.save("NoDist.npy",AnalysisObj.Results,allow_pickle=True)
        TestResults = np.load("NoDist.npy",allow_pickle=True).item()     

        self.assertEqual(AnalysisObj.Results, TestResults)

    def testNoCor(self):
        ComputeDist = Compute_Distortion.DistortionCalculation("./TestDataNoCor" , "3D Sag T1 BRAVO") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("No_CorrectioN",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        #np.save("NoCor.npy",AnalysisObj.Results,allow_pickle=True)
        TestResults = np.load("NoCor.npy",allow_pickle=True).item()     

        self.assertEqual(AnalysisObj.Results, TestResults)

    def testNoCor(self):
        ComputeDist  = Compute_Distortion.DistortionCalculation("./TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("Distortion",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        #np.save("Dist.npy",AnalysisObj.Results,allow_pickle=True)
        TestResults = np.load("Dist.npy",allow_pickle=True).item()     

        self.assertEqual(AnalysisObj.Results, TestResults)
