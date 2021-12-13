import Analysis
import Compute_Distortion

#Set up and run the Distortion Distance Calculation
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") #
ComputeDistortionGeoCorrection.GetFudicalSpheres()

#Pass the distortion calc to the analysis class for well analysis...
NoDitsortionAnalysis = Analysis.AnalysisResults("No_Distortion",ComputeDistortionGeoCorrection)
NoDitsortionAnalysis.DistortionAnalysis()
NoDitsortionAnalysis.PrintToScreen()

#ComputeDistortionShimOff = Compute_Distortion.DistortionCalculation("TestDistoredData" , "3D Sag T1 BRAVO BW=15 Shim off")
#Analysis.DistortionAnalysis(ComputeDistortionShimOff, "Distortion")


#ComputeDistortionNoGeoCorr = Compute_Distortion.DistortionCalculation("TestDataNoCor" , "3D Sag T1 BRAVO")
#Analysis.DistortionAnalysis(ComputeDistortionNoGeoCorr, "NoGeometryCorrection")