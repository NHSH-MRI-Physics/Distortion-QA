#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys
import SNRCalc

ComputeDistortion = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 
ComputeDistortion.BinariseMethod = "Constant"
Analyse = Analysis.AnalysisResults("FlippedData",ComputeDistortion)
ComputeDistortion.Threshold=3000
ComputeDistortion.GetFudicalSpheres()
SNR = SNRCalc.SNR(ComputeDistortion)
SNR.boxsize=[50,50]
SNR.ComputerSNR(showRegions=True)