"""
By Damien LAMAISON

V1 : 21/10/2021

Pad detection for Crocus Technology Product
"""

import cv2
import numpy as np
from matplotlib.pyplot import *
import math
import imutils
from PIL import Image
from operator import itemgetter
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import Graphic_Interface_PMI as interface
import os
import sys
import Pad_Detection
import Probemarks_Detection
import Overlap_probemark_to_pad
import Output_file_PMI
import Manual_Pad_Detection
import Manual_Mark_Detection
from tkinter import Tk
import Tkinter_Message as TM
import Orion_PMI_type

#User has to fill picture path and Product name
save_path,Product=interface.gui()
save_path.encode('unicode-escape')
split_path=save_path.split("\\")
split_path=split_path[-1].split(" ")
Wafer_ID=split_path[-1][1:3]
Lot_ID=split_path[0]
Product_ID=Product


if Product_ID in ['Orion', 'orion']:
    PMI_type = Orion_PMI_type.orion_pmi_choice() #MSI or ASIC
else:
    PMI_type=''

#True number of probemarks to be detected
if Product_ID in ['Malibu', 'malibu']:
    True_nb_probemarks=8
    List_pad_name = ['SinN', 'VDD', 'VSin', 'CosN', 'SinP', 'VCos', 'GND', 'CosP']
    Pad_disposition = [[1,1],[1,1],[1,1],[1,1]]# En ligne de haut en bas
elif Product_ID in ['Nimbus','nimbus']:
    True_nb_probemarks = 4
    List_pad_name = ['X1(Bond)', 'X1(Test)', 'X2(Test)', 'X2(Bond)', 'VCC(Bond)', 'VCC(Test)', 'GND(TEST)', 'GND(Bond)']
    Pad_disposition = [[1,1,1,1],[1,1,1,1]]# En ligne de haut en bas
elif Product_ID in ['Empire','Hammer','Sirius','empire','hammer','sirius']:
    True_nb_probemarks=4
    List_pad_name = [0, 'VDD', 0, 0, 'X2', 0, 0, 0, 0, 0, 0, 0, 0, 'VSS', 0, 0, 'X1', 0]
    Pad_disposition = [[1,1,1,1,1,1],[1,0,0,0,0,1],[1,0,0,0,0,1],[1,0,0,0,0,1],[1,1,1,1,1,1]]
elif Product_ID in ['Halo','halo']:
    True_nb_probemarks=6 
    List_pad_name = ['VPL', 'VML', 'AVCCBR', 'AVSS', 'VMR', 'VPR']
    Pad_disposition = [[1,1,1,1,1,1]]
elif Product_ID in ['Orion','orion']:
    if PMI_type =='MSI':
        True_nb_probemarks=6 
        List_pad_name = ['VPL', 'VML', 'AVCCBR', 'AVSS', 'VMR', 'VPR']
        Pad_disposition = [[1,1,1,1,1,1]]
    elif PMI_type =='ASIC':
        True_nb_probemarks=5 
        List_pad_name = ['1', '2', '3', '4', '5']
        Pad_disposition = [[1,1,1,1,1]]
elif Product_ID in ['Iris','Retina','iris','retina']:
    True_nb_probemarks=8 # Supposing 2 dies are taken on a single picture
    List_pad_name = ['OUT1', 'VDD', 'OUT1', 'VDD', 'GND', 'OUT2', 'GND', 'OUT2']
    Pad_disposition = [[1,1,1,1],[1,1,1,1]]
else :
    TM.show_error('Product choice error','The chosen product does not exists')

#Iteration on all the pictures with .jpg  extension and "PMI" name in the folder
files=os.listdir(save_path)
picture_nb=0

for filename in files:
    if filename.endswith(r".jpg") and "PMI" in filename and PMI_type in filename:
        picture_nb=picture_nb+1
        img = cv2.imread(save_path+'\\'+ filename)
        if Product_ID in ['Nimbus','nimbus']: # Rotate image by 90° clockwise
            img = cv2.rotate(img , cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)

        size_img=img.shape
        #Image resizeing (twice smaller) to avoid artefact during image treatment due to too much details
        if Product_ID in ['Nimbus','nimbus']: # Rotate image by 90° clockwise
            img = imutils.resize(img, height=1000)
        else:
            img=imutils.resize(img, width=1000)

        clone_full_reset = img.copy()
        #---------------Pad detection-----------------------------------#
        pad = Pad_Detection.Pad_detection(img,filename)
        
        #Image treatment to emphasize contours of pads
        contours_pad = pad.treatment()
        
        #List of coordinates of all the detected pad
        list_pad = pad.detect_pad(contours_pad)
        
        #Eliminate all the pads detected several to keep only one (inner pad edge)
        list_single_pad = pad.single_pad_list(list_pad)
      
        #Draw rectangle of the detected pad on the original image
        pad.draw_pad(list_single_pad,List_pad_name)

        #Ask for Pad selection confirmation
        cv2.imshow(filename,img)        
        MsgBox = TM.ask_question('Validation','Do you accept the pad selection?','info')
        if MsgBox == 'no':
            MsgBox_Pads = TM.ask_question('Manual Selection of Pads','Do you want to do a manual selection of missing Pads?','info')

            #Manual selection of Pads
            if MsgBox_Pads == 'yes':
                clone = img.copy()
                list_single_pad_clone = list_single_pad
                TM.show_info('Selection','You can select all pads on same picture. Type "v" to validate selection. Press "r" to reset manual seletion. Press "a" to reset all selection.','info')
                cv2.namedWindow("image")
                while True:
                    pad_man = Manual_Pad_Detection.Manual_Pad_Detection(img, filename,list_single_pad)
                    cv2.setMouseCallback("image", pad_man.click_and_crop_pad, list_single_pad)
                    # display the image and wait for a keypress
                    cv2.imshow("image", img)
                    key = cv2.waitKey(1) & 0xFF
                    # if the 'r' key is pressed, reset the manually selected pads
                    if key == ord("r"):
                        img = clone.copy()
                        list_single_pad = list_single_pad_clone
                    # if the 'a' key is pressed, reset all selected pads (manual + automatic)
                    elif key == ord("a"):
                        cv2.namedWindow("image")
                        img = clone_full_reset.copy()
                        list_single_pad = []
                        TM.show_info('Selection','All selections have been reset. Please reselect all pads','info')
                    # if the 'v' key is pressed, validate manual selection
                    elif key == ord("v"):
                        nb_pad = len(list_single_pad)
                        TM.show_info('Validation', 'Manual selection validated', 'info')
                        cv2.destroyAllWindows()
                        break


        #Compute pad area average
        pad_area_average=pad.comput_pad_area(list_single_pad)
        
        #Pad are sorted from top left to bottom right
        list_single_pad = pad.order_pad_list(list_single_pad,Pad_disposition)        
 
        #Copy if the image for the pass/fail output image
        simplified_analyzed  = img.copy()
        
        if len(list_single_pad)==len(List_pad_name):
            #We add the name pad to the list
            for nbp in range(len(list_single_pad)):
                list_single_pad[nbp].append(List_pad_name[nbp])
            pad.check_pad_position(list_single_pad,Pad_disposition,Product_ID)
        else :
            TM.show_warning('Wrong number of detected pads', 'The number of detected pads is ' + str(len(list_single_pad)) + ' while it should be ' + str(len(List_pad_name)),'warning')
            break
        #---------------Probemark detection-----------------------------------#
        probemark = Probemarks_Detection.Probemarks_detection(img,filename,True_nb_probemarks,list_single_pad)
        
        for nb_pad in range(len(list_single_pad)):
            #Image treatment to emphasize contours of probemarks
            contours_marks,x,y,pixel_crop,w,h = probemark.treatment(img,nb_pad)
            
            #Coordinate correction of cropped pad image to match original image
            contours_marks = probemark.coordinate_correction(contours_marks,x,y,pixel_crop)
            
            #Draw contours of the detected probemarks
            list_pad_mark = probemark.detect_probemark(contours_marks,w,h,pad_area_average)
            
            # if len(list_pad_mark)!=0 :
            #     if len(list_pad_mark[-1])<6:
            #            #We add the pad name on which is the probemark
            #            list_pad_mark[-1].append(List_pad_name[nb_pad])

        #Eliminate double probemark detection on a single pad
        list_single_pad_mark = probemark.single_probemark_list(list_pad_mark)
        
        clone = img.copy()
        #Draw detected probemark
        list_single_pad_mark = probemark.draw_probemark(list_single_pad_mark,True_nb_probemarks,img)
        clone2 = img.copy() 
        
        #---------------Check overlap between probemark and pad egde-----------------------------------#
        overlap_check = Overlap_probemark_to_pad.Overlap_marks_to_pad(img,list_single_pad,list_single_pad_mark)
        
        #Check if there is overlap between probemark and pad edge
        overlap = overlap_check.overlap_check(list_single_pad_mark,img)
            
        
        #---------------File summary creation-----------------------------------#
        Threshold_marks = 17 #Max area on pad covered with probemarks (20% - 3% guardband)
        Product=[]
        Lot=[]
        Wafer=[]
        Pad_nb=[]
        Ratio=[] #Probemark_Area/Pad_area
        Pass_acceptance_criteria =[]
        output_file = Output_file_PMI.Output_file(list_single_pad,list_single_pad_mark,Product_ID,Lot_ID,Wafer_ID,pad_area_average,overlap,picture_nb,filename,save_path)


        # Ask for Mark selection confirmation
        cv2.imshow(filename, img)
        MsgBox2 = TM.ask_question('Validation', 'Do you accept the mark selection?', 'info')
        if MsgBox2 == 'no':
            MsgBox_Mark = TM.ask_question('Manual Selection of Marks', 'Do you want to do a manual selection of Probe Marks?','info')

            # Manual selection of Pads#Manual selection of Pads
            if MsgBox_Mark == 'yes':   
                list_single_pad_mark_clone = list_single_pad_mark
                cv2.destroyAllWindows()
                TM.show_info('Selection','You can select all pads on same picture. Type "v" to validate selection. Press "r" to reset manual seletion. Press "a" to reset all selection.','info')
                cv2.namedWindow("image")
                while True:
                    mark = Manual_Mark_Detection.Manual_Mark_Detection(img, filename, list_single_pad_mark)
                    cv2.setMouseCallback("image", mark.click_and_crop_mark, list_single_pad_mark)
                    # display the image and wait for a keypress
                    cv2.imshow("image", img)
                    key = cv2.waitKey(1) & 0xFF
                    # if the 'r' key is pressed, reset the cropping region
                    if key == ord("r"):
                        #img = clone.copy()
                        img=clone2.copy()
                        list_single_pad_mark = list_single_pad_mark_clone
                    # if the 'a' key is pressed, reset all selected probemarks (manual + automatic)
                    elif key == ord("a"):
                        cv2.namedWindow("image")
                        #img = clone_full_reset.copy()
                        img=clone.copy()
                        list_single_pad_mark = []
                        TM.show_info('Selection','All selections have been reset. Please reselect all marks', 'info')
                    # if the 'v' key is pressed, validate manual selection
                    elif key == ord("v"):
                        TM.show_info('Validation', 'Manual selection validated', 'info')
                        break


            cv2.destroyAllWindows() 
            
            #Match probemark to the associated pad
            list_single_pad_mark = probemark.match_mark_to_pad(list_single_pad,list_single_pad_mark,List_pad_name)
            
            #Draw the pad name on the original image
            pad.name_pad(list_single_pad,List_pad_name,img)
            
            
            # ---------------Check overlap between probemark and pad egde-----------------------------------#
            overlap_check = Overlap_probemark_to_pad.Overlap_marks_to_pad(img, list_single_pad, list_single_pad_mark)
            # Check if there is overlap between probemark and pad edge
            overlap = overlap_check.overlap_check(list_single_pad_mark,img)
            output_file = Output_file_PMI.Output_file(list_single_pad,list_single_pad_mark, Product_ID, Lot_ID, Wafer_ID,pad_area_average, overlap, picture_nb, filename, save_path)

            # for db in range(len(list_single_pad_mark)):
            for db in range(len(list_single_pad_mark)): 
                name=list_single_pad_mark[db][5]
                for db2 in range(len(list_single_pad)):
                    if list_single_pad[db2][9]==name:
                        Pad_match=list_single_pad[db2][8]
                                        
                # Check the acceptance critieria according to the 2 rules :
                # 1) No probemark on pas edge
                # 2) Ratio probemark size by pad size below the threshold (25%))
                pass_acceptance_criteria, ratio, product, lot, wafer, pad_nb = output_file.acceptance_criteria(Product,Lot,Wafer,Pad_nb,Ratio,Threshold_marks,db,Pass_acceptance_criteria)
                output_file.write_db_file(filename, save_path, overlap[db], product[-1], lot[-1], wafer[-1], Pad_match, list_single_pad_mark[db][5],list_single_pad_mark[db][4],ratio, pass_acceptance_criteria[-1], 'yes')
                
                #Write the ratio value near the probemark on the image
                probemark.text_probemark(list_single_pad_mark[db],ratio[-1],img)
                
                #Write if the probemark is on the pad edge
                probemark.text_overlap_probemark(list_single_pad_mark[db],overlap[db],img)
                
                cv2.imshow("image", img)
                img_analyzed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_analyzed = Image.fromarray(img_analyzed) 
                img_analyzed.save(save_path + "\\" + filename + "_Analyzed.jpeg") 
                
                
                #Write if the pad is pass or fail according to acceptance critiria
                probemark.pass_or_fail(list_single_pad_mark[db],pass_acceptance_criteria[-1],simplified_analyzed)
                pass_or_fail_img = cv2.cvtColor(simplified_analyzed, cv2.COLOR_BGR2RGB)
                pass_or_fail_img = Image.fromarray(pass_or_fail_img)
                pass_or_fail_img.save(save_path + "\\" + filename +"_Pass_or_Fail.jpeg")
        else:
            #  # ---------------Check overlap between probemark and pad egde-----------------------------------#
            # overlap_check = Overlap_probemark_to_pad.Overlap_marks_to_pad(img, list_single_pad, list_single_pad_mark)
            # # Check if there is overlap between probemark and pad edge
            # overlap = overlap_check.overlap_check(list_single_pad_mark)
            # output_file = Output_file_PMI.Output_file(list_single_pad_mark, Product_ID, Lot_ID, Wafer_ID,pad_area_average, overlap, picture_nb, filename, save_path)

            cv2.waitKey(500)
            cv2.destroyAllWindows()
            
             #Match probemark to the associated pad
            list_single_pad_mark = probemark.match_mark_to_pad(list_single_pad,list_single_pad_mark,List_pad_name)
          
            #Draw the pad name on the original image
            pad.name_pad(list_single_pad,List_pad_name,img)

            for db in range(len(list_single_pad_mark)):
                name=list_single_pad_mark[db][5]
                for db2 in range(len(list_single_pad)):
                    if list_single_pad[db2][9]==name:
                        Pad_match=list_single_pad[db2][8]
  
                #Check the acceptance critieria according to the 2 rules :
                        #1) No probemark on pas edge
                        #2) Ratio probemark size by pad size below the threshold (25%))
                pass_acceptance_criteria,ratio,product,lot,wafer,pad_nb = output_file.acceptance_criteria(Product,Lot,Wafer,Pad_nb,Ratio,Threshold_marks,db,Pass_acceptance_criteria)
                output_file.write_db_file(filename,save_path,overlap[db],product[-1],lot[-1],wafer[-1],Pad_match,list_single_pad_mark[db][5],list_single_pad_mark[db][4],ratio,pass_acceptance_criteria[-1],'yes')
                
                #Write the ratio value near the probemark on the image
                probemark.text_probemark(list_single_pad_mark[db],ratio[-1],img)
                
                #Write if the probemark is on the pad edge
                probemark.text_overlap_probemark(list_single_pad_mark[db],overlap[db],img)
                
                cv2.imshow("image", img)
                img_analyzed = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_analyzed = Image.fromarray(img_analyzed) 
                img_analyzed.save(save_path + "\\" + filename + "_Analyzed.jpeg")
                
                
                #Write if the pad is pass or fail according to acceptance critiria
                probemark.pass_or_fail(list_single_pad_mark[db],pass_acceptance_criteria[-1],simplified_analyzed)
                pass_or_fail_img = cv2.cvtColor(simplified_analyzed, cv2.COLOR_BGR2RGB)
                pass_or_fail_img = Image.fromarray(pass_or_fail_img)
                pass_or_fail_img.save(save_path + "\\" + filename +"_Pass_or_Fail.jpeg")
                
cv2.waitKey(0)
MsgBox_Restart = TM.ask_question('Restart?', 'Do you want to analyse another PMI picture?','info')
if   MsgBox_Restart == 'yes':
     print("argv was", sys.argv)
     print("sys.executable was", sys.executable)
     print("restart now")
     os.execv(sys.executable, [sys.executable, '"' + sys.argv[0] + '"'] + sys.argv[1:] + ['--uid'])
else:
    print("\nThe program will be closed...")
    sys.exit(0)
cv2.destroyAllWindows()
