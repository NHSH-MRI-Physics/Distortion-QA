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
st.title('Distortion Calculation')



path = st.text_input('File Path')
seqname = st.text_input('Sequence Name', "3D Sag T1 BRAVO DL")
Thresh = st.text_input('Threshold', '3000')
col1, col2 = st.columns(2)
with col1:
     button = st.button('Run Distortion Calculation')
with col2:
     BinaryImages = st.checkbox('OutputBinaryImages')

if button:
    if path == "":
        st.error('Error: full path needs to be set', icon="🚨")
    else:
            dataset = path
            ComputeDistortion = Compute_Distortion.DistortionCalculation(dataset , seqname) 
            ComputeDistortion.BinariseMethod = "Constant"
            Analyse = Analysis.AnalysisResults("GUI_RUN",ComputeDistortion)
            ComputeDistortion.Threshold=int(Thresh)
            if BinaryImages:
               files = glob.glob(os.path.join('BinaryImages','*'))
               
               if not os.path.exists("BinaryImages"):
                    os.makedirs("BinaryImages")

               for f in files:
                    os.remove(f)
               ComputeDistortion.checkBinaryImages=True

            ComputeDistortion.GetFudicalSpheres()
            ComputeDistortion.GetDistances()
            Analyse.DistortionAnalysis()

            SNR = SNRCalc.SNR(ComputeDistortion)
            SNRResult = SNR.ComputerSNR()

            if ComputeDistortion.BinaryWarningThreshToLow and ComputeDistortion.BinaryWarningThreshToLow:
                 st.error('Warning: Large Radius and short distances detected try a different threshold!', icon="🚨")
            elif ComputeDistortion.BinaryWarningThreshToLow:
                 st.error('Warning: Large Radius detected try increasing threshold!', icon="🚨")
            elif ComputeDistortion.BinaryWarningThreshToHigh:
                 st.error('Warning: Short distances found, try decreasing the threshold!', icon="🚨")
                 

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
            
            img1=st.image("GUI_RUN_InterplateDistances.png")
            img2=st.image("GUI_RUN_Plate_1_IntraPlateDist.png")
            img3=st.image("GUI_RUN_Plate_2_IntraPlateDist.png")
            img4=st.image("GUI_RUN_Plate_3_IntraPlateDist.png")
            img5=st.image("GUI_RUN_Plate_4_IntraPlateDist.png")
            img6=st.image("GUI_RUN_Plate_5_IntraPlateDist.png")
