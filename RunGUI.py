#Basic example input file, for more complete description refer to the manual

import Analysis
import Compute_Distortion
import sys
import SNRCalc
import streamlit as st
import os
import pandas as pd
import numpy as np
import time 
import glob

dir = "DataSets"
seqname = "3D Sag T1 BRAVO Geom Core"
seqname = "3D Sag T1 BRAVO BW=15 Shim off"
st.title('Distortion Calculation')

folders = os.listdir(dir)
dates=[]
filecount = []
FoldersToDisplay=[]
for folder in folders:
    if folder[0]!='.':
        FoldersToDisplay.append(folder)
        dates.append( time.ctime( os.stat(os.path.join(dir,folder)).st_mtime ))
        filecount.append(len(os.listdir(os.path.join(dir,folder))))

options = st.multiselect(
'Select a dataset',
FoldersToDisplay)
df = pd.DataFrame()
df['Data Sets'] = FoldersToDisplay
df['Dates'] = dates
df['Number of Files'] = filecount
st.table(df)



Thresh = st.text_input('Threshold', '3000')
col1, col2 = st.columns(2)
with col1:
     button = st.button('Run Distortion Calculation')
with col2:
     BinaryImages = st.checkbox('OutputBinaryImages')

if button:
    if len(options)>1 or len(options)==0:
        st.error('Error choose exactly one dataset', icon="🚨")
    else:
            dataset = os.path.join(dir,options[0])
            ComputeDistortion = Compute_Distortion.DistortionCalculation(dataset , seqname) 
            ComputeDistortion.BinariseMethod = "Constant"
            Analyse = Analysis.AnalysisResults("GUI_RUN",ComputeDistortion)
            ComputeDistortion.Threshold=int(Thresh)
            if BinaryImages:
                files = glob.glob(os.path.join('BinaryImages','*'))
                for f in files:
                    os.remove(f)
                ComputeDistortion.checkBinaryImages=True
            ComputeDistortion.GetFudicalSpheres()
            ComputeDistortion.GetDistances()
            Analyse.DistortionAnalysis()

            SNR = SNRCalc.SNR(ComputeDistortion)
            SNRResult = SNR.ComputerSNR()
            
            st.write( "Study Date: " + str(Analyse.DistorCalcObj.Studydate) )
            st.write( "Interplate Stats") 
            st.write("Interplate Max Distortion: " + str(round(Analyse.Results["Interplate Max Distortion"][0],3)) +" mm")
            st.write("Interplate Max Percentage Distortion: " + str(round(Analyse.Results["Interplate Max Percentage Distortion"][0],3)) +"%")
            st.write("Interplate Coefficient Of Variation: " + str(round(Analyse.Results["Interplate Coefficient Of Variation"],3)))
            
            st.write ("Intraplate Stats\n")
            st.write("Intraplate Max Distortion: " + str(round(max(x[0] for x in Analyse.Results["Intraplate Max Distortion"]),3)) +" mm") #This one is a bit different since its a list of list this is a way to get the max value in a list of lists 
            st.write("Intraplate Max Percentage Distortion: " + str(round(max(x[0] for x in Analyse.Results["Intraplate Max Percentage Distortion"]),3))+"%"  )
            st.write("Intraplate Coefficient Of Variation: " + str(round(max(Analyse.Results["Intraplate Coefficient Of Variation"]),3)))

            st.write("SNR: " + str(round(SNRResult,3)))
            st.session_state.disabled=False

            if ComputeDistortion.BinaryWarning:
                 st.error('Warning: Large Radius or Overlapping Sphere Detected, Check the Binary Images!', icon="🚨")

            
            img1=st.image("GUI_RUN_InterplateDistances.png")
            img2=st.image("GUI_RUN_Plate_1_IntraPlateDist.png")
            img3=st.image("GUI_RUN_Plate_2_IntraPlateDist.png")
            img4=st.image("GUI_RUN_Plate_3_IntraPlateDist.png")
            img5=st.image("GUI_RUN_Plate_4_IntraPlateDist.png")
            img6=st.image("GUI_RUN_Plate_5_IntraPlateDist.png")
