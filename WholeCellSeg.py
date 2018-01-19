# Copyright (c) General Electric Company, 2017.  All rights reserved.

'''
Created on Mar 23, 2017
Updated on April 17, 2017

@author: Yousef Al-Kofahi

This script performs Nuclei segmentation followed cell segmentation using a second cell stain/channel.
If no cell stain/channel is available, a synthetic cell boundary will be generated
'''


import sys
import numpy as np
import cv2
import subprocess
import time


def SubtractBackground(im,filterSize):

    filterSize = filterSize

    
    kernel = np.ones((filterSize,filterSize),np.uint8)
    
    im = cv2.resize(im,dsize=(0,0),fx=2,fy=2)
    im = cv2.medianBlur(im,5)
    im = cv2.resize(im,dsize=(0,0),fx=0.5,fy=0.5)
    im = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, kernel)
    

    return im



if __name__ == '__main__':
    #
    # Perform Nuclei and Cell Segmentation
    #    
    
    t = time.time()
    if len(sys.argv) < 8:
        print("Incorrect arguments...Script should be called as follows:")
        print("python WholeCellSeg.py InNucName OutNucSegName OutCellSegName minLevel maxLevel smoothingSigma MaxCytoplasmThickness [Optional: CellMarkerImageName CellSegSensitivity")
        sys.exit()
        
    
    inNucName = sys.argv[1]
    outNucName = sys.argv[2]
    outCellname = sys.argv[3]
    minLevel = int(sys.argv[4])
    maxLevel = int(sys.argv[5])
    smoothingSigma = float(sys.argv[6])
    cytThickness = int(sys.argv[7])
    inCellName = ''
    twoChannels = 0
    cellseg_sensitivity = 0.75
    if len(sys.argv) >= 9:
        inCellName = sys.argv[8]
        twoChannels = 1
        if len(sys.argv) == 10:
            cellseg_sensitivity = float(sys.argv[9])
    
    if minLevel > maxLevel:
        print 'maxlevel cannot be less than minLevel'
        sys.exit()
        
    numLevels = maxLevel - minLevel + 1
    
    
    im = cv2.imread(inNucName,-1)
    tmpNuc = im.copy()
    im = SubtractBackground(im,cytThickness*5)
    nm = inNucName[:-4] + '_bgsub.tif'
    cv2.imwrite(nm, im)
    
    
    # Run Nuclei segmentation
    exeName = './itkWaveletNucleiSegmentationTest'
    exeArgs = ' ' + inNucName + ' ' + outNucName  + ' ' + str(minLevel)+ ' ' + str(maxLevel)+ ' ' + str(numLevels)+ ' '+ str(smoothingSigma)
    cmmd = exeName + exeArgs
    #subprocess.call(cmmd)
    subprocess.check_call(cmmd,shell=True)
    
    # Read the nuclei image and compute the distance transform
    im = cv2.imread(outNucName, -1)
    
    im2 = (im.copy()).astype('uint8')
    im2[im==0] = 255
    im2[im>0] = 0
    #dist_transform = cv2.distanceTransform(im2,cv2.cv.CV_DIST_L2,5)
    dist_transform = cv2.distanceTransform(im2,cv2.DIST_L2,5)
    
    I = []
    im = im + 1
    if twoChannels == 1:
        # Read the cell marker image
        im3 = cv2.imread(inCellName,-1)
        
        # binarize it
        im3 = (im3.astype('float32') / im3.max())*255
        tmpNuc = (tmpNuc.astype('float32') / tmpNuc.max())*255
        im3 = im3 + tmpNuc
        kernel = np.ones((7,7),np.uint8)
        im3 = cv2.morphologyEx(im3, cv2.MORPH_CLOSE, kernel)
        
        ret2,im3Bin = cv2.threshold(im3.astype('uint8'),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        TH = (1-cellseg_sensitivity)* ret2 + cellseg_sensitivity*(ret2/2.0)
        im3Bin[im3>TH] = 255
        
        im3Bin = cv2.morphologyEx(im3Bin, cv2.MORPH_CLOSE, kernel)
        im3Bin[dist_transform > cytThickness] = 0
        I = np.where((dist_transform>0) & (im3Bin>0))
        I2 = np.where((dist_transform>0) & (im3Bin==0))
        im[I] = 0
        dist_transform[I2] = dist_transform.max()
    else:         
        I = np.where((dist_transform>0) & (dist_transform<cytThickness))
        im[I] = 0
        
        
    
    
    
    markers = np.int32(im)    

    dist_transform = cv2.cvtColor(np.uint8(dist_transform),cv2.COLOR_GRAY2RGB)
    cv2.watershed(dist_transform,markers)
    
    wtd_seg = markers.copy()
    wtd_seg[wtd_seg<=1] = 0
    
        
    cv2.imwrite(outCellname, wtd_seg)
    
    t2 = time.time()
    
    print 'processing time = ', t2-t
    
    
    
    
   
    
    
    