import pydicom
import matplotlib.pyplot as plt
import glob
import numpy as np
from skimage.feature import blob_dog, blob_log, blob_doh
import math
from shutil import copyfile

DICOMFiles = glob.glob('./PhantomData/*')
ExtractedSequence = "3D Sag T1 BRAVO"
MaxValue = 0
DICOMS=[]
for file in DICOMFiles:
    LoadedDICOM = pydicom.read_file( file )
    if (LoadedDICOM.SeriesDescription == ExtractedSequence):
        #print (file)
        copyfile(file,"TestImages/"+file.split("/")[-1])