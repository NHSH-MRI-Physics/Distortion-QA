
import Analysis
import Compute_Distortion
import sys
from scipy.optimize import minimize_scalar
from scipy.optimize import show_options
import unittest
import numpy as np
import os 
class TestDistortion(unittest.TestCase):
    def testNormal(self):
        path = os.path.join(os.getcwd(),"TestData","NormTestData")
        ComputeDist = Compute_Distortion.DistortionCalculation(path, "3D Sag T1 BRAVO Geom Core") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("No_Distortion",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        self.assertEqual(AnalysisObj.Results["Interplate Max Distortion"][0], 0.4539283722220375)
        self.assertEqual(AnalysisObj.Results["Interplate Max Percentage Distortion"][0], -0.6146744110059288)
        self.assertEqual(AnalysisObj.Results["Interplate Coefficient Of Variation"], 0.0025495782290646044)
  
        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][0][0], 0.07473029224722438)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][0][0],-0.1321057410201621)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][0], 0.0013115364699629922)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][1][0], 0.158630523314244)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][1][0],0.29669524395544045)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][1], 0.0017423566110522845)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][2][0], 0.20782062870937068)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][2][0],0.41594541077360603)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][2], 0.00100642857749169)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][3][0], 0.14079410561267025)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][3][0],-0.24771133457146985)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][3], 0.001197094586304424)

    def testNoCor(self):
        path = os.path.join(os.getcwd(),"TestData","TestDataNoCor")
        ComputeDist = Compute_Distortion.DistortionCalculation(path , "3D Sag T1 BRAVO") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("No_Correction",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        self.assertEqual(AnalysisObj.Results["Interplate Max Distortion"][0], 2.0433243523222586)
        self.assertEqual(AnalysisObj.Results["Interplate Max Percentage Distortion"][0], -2.6544179829351364)
        self.assertEqual(AnalysisObj.Results["Interplate Coefficient Of Variation"], 0.0027249702790519813)
  
        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][0][0], 0.8471673992755058)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][0][0],1.0589592490943822)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][0], 0.007718235287971137)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][1][0], 1.8959916127822964)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][1][0],2.1810759012171665)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][1], 0.016311547994254237)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][2][0], 3.624660447990337)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][2][0],-4.927366387463614)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][2], 0.0077633440788463315)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][3][0], 2.1500477020811957)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][3][0],2.2064982245830222)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][3], 0.007298502469600538)

    def testDist(self):
        path = os.path.join(os.getcwd(),"TestData","TestDistoredData")
        ComputeDist  = Compute_Distortion.DistortionCalculation(path, "3D Sag T1 BRAVO BW=15 Shim off") 
        ComputeDist.BinariseMethod = "Constant"
        ComputeDist.Threshold=int(3000)
        AnalysisObj = Analysis.AnalysisResults("Distortion",ComputeDist)
        ComputeDist.GetFudicalSpheres()

        ComputeDist.GetDistances()
        AnalysisObj.DistortionAnalysis()

        self.assertEqual(AnalysisObj.Results["Interplate Max Distortion"][0], 29.038806321881943)
        self.assertEqual(AnalysisObj.Results["Interplate Max Percentage Distortion"][0], -32.466372460589334 )
        self.assertEqual(AnalysisObj.Results["Interplate Coefficient Of Variation"], 0.051824509587756355)
  
        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][0][0], 9.935363332545535)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][0][0],-11.108073896365331 )
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][0], 0.017338008066554614)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][1][0], 4.517836566837872)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][1][0],-3.075268812737999)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][1], 0.0189254984908528)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][2][0], 5.699496091462407)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][2][0],-4.883586331946166)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][2], 0.13641222042125206)

        self.assertEqual(AnalysisObj.Results["Intraplate Max Distortion"][3][0],44.62937309275635)
        self.assertEqual(AnalysisObj.Results["Intraplate Max Percentage Distortion"][3][0],-51.035135369740445)
        self.assertEqual(AnalysisObj.Results["Intraplate Coefficient Of Variation"][3], 0.18601857949879502)