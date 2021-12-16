import Analysis
import Compute_Distortion
import sys

#Set up and run the Distortion Distance Calculation
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 
NoDitsortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)
ComputeDistortionGeoCorrection.GetFudicalSpheres()
ComputeDistortionGeoCorrection.GetDistances()
NoDitsortionAnalysis.DistortionAnalysis()
NoDitsortionAnalysis.PrintToScreen()
#NoDitsortionAnalysis.OutputPeriodicData("DistortionData.csv")


print ("")
ComputeDistortionShimOffCorrection = Compute_Distortion.DistortionCalculation("TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off")
ShimOffDitsortionAnalysis = Analysis.AnalysisResults("Distortion",ComputeDistortionShimOffCorrection)
ComputeDistortionShimOffCorrection.GetFudicalSpheres()
ComputeDistortionShimOffCorrection.GetDistances()
ShimOffDitsortionAnalysis.DistortionAnalysis()
ShimOffDitsortionAnalysis.PrintToScreen()
#ShimOffDitsortionAnalysis.OutputPeriodicData("DistortionData.csv")

print ("")
ComputeDistortionNoGeoCorrection = Compute_Distortion.DistortionCalculation("TestDataNoCor" , "3D Sag T1 BRAVO")
NoCorrDitsortionAnalysis = Analysis.AnalysisResults("No_Correction",ComputeDistortionNoGeoCorrection)
ComputeDistortionNoGeoCorrection.GetFudicalSpheres()
ComputeDistortionNoGeoCorrection.GetDistances()
NoCorrDitsortionAnalysis.DistortionAnalysis()
NoCorrDitsortionAnalysis.PrintToScreen()
#NoCorrDitsortionAnalysis.OutputPeriodicData("DistortionData.csv")


NoDitsortionAnalysis.PlotCSV("DistortionData.csv")