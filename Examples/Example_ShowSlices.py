import Analysis
import Compute_Distortion
import sys
import matplotlib.pyplot as plt


#Compute distortion on one sequence
#Set up the distortion calc by passing the folder with all the DICOMS and the sequence of interest.
ComputeDistortionGeoCorrection = Compute_Distortion.DistortionCalculation("TestData" , "3D Sag T1 BRAVO Geom Core") 
#need this bit to run the loading part
ComputeDistortionGeoCorrection.GetFudicalSpheres()


SagSlice = ComputeDistortionGeoCorrection.GetSagSlice(184)#Get sag slice 184
AxialSlice = ComputeDistortionGeoCorrection.GetAxialSlice(260)#Get Axial slice 260
CorSlice = ComputeDistortionGeoCorrection.GetCorSlice(260)# Get Cor slice 260


#Display them
plt.imshow(SagSlice)
plt.show()

plt.imshow(AxialSlice)
plt.show()

plt.imshow(CorSlice)
plt.show()