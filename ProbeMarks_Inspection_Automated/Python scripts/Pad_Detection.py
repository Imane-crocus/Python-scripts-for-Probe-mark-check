import cv2
import numpy as np
from matplotlib.pyplot import *
import math
import imutils
from PIL import Image
from operator import itemgetter
import pandas as pd
import tkinter as tk
import Graphic_Interface_PMI as interface
import os
import copy 
import tkinter as tk
import Tkinter_Message as TM

class Pad_detection(object):
    
    def __init__(self,img,filename):
        self.img=img
        self.filename=filename
     
    def img_resize(self,save_path,filename):
        self.img = cv2.imread(save_path+'\\'+ filename)
        size_img=self.img.shape
        #Image resizeing (twice smaller) to avoid artefact during image treatment due to too much details
        self.img=imutils.resize(self.img, width=1000)
        return(self.img)
    
    def treatment(self):
         #Image treatment algorithms
        gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        
        blur = cv2.medianBlur(gray, 3)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(blur, -1, sharpen_kernel)
        
        ret,thresh = cv2.threshold(gray,107,255,0)
        ret2,thresh2 = cv2.threshold(gray,87,205,0)

        
        edged = cv2.Canny(blur, 40, 60)
        thresh = cv2.threshold(thresh,127,255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        close = cv2.erode(thresh,None, iterations=2)
        
        thresh2 = cv2.threshold(thresh2,127,255, cv2.THRESH_BINARY_INV)[1]  
        edged2 = cv2.threshold(sharpen,127,255, cv2.THRESH_BINARY_INV)[1]
        edged3 = cv2.threshold(sharpen,97,255, cv2.THRESH_BINARY_INV)[1]
        edged4 = cv2.threshold(sharpen,77,255, cv2.THRESH_BINARY_INV)[1]


        #cv2.imshow("edged", edged)

        #Contours detection with the different algorithm
        contours1,hier1 = cv2.findContours(edged,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours2,hier2 = cv2.findContours(close,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours3,hier3 = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours4,hier4 = cv2.findContours(edged2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours5,hier5 = cv2.findContours(thresh2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours6,hier6 = cv2.findContours(edged3,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours7,hier7 = cv2.findContours(edged4,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        contours = contours1 + contours2 + contours3 + contours4 + contours5 + contours6 + contours7
        return(contours)

    def detect_pad(self,contours):
        #List creation of all the detected pad with their coordinates, position, area
        idx=0
        list_pad=[]
        for cnt in contours:
            if cv2.contourArea(cnt)>4000 and cv2.contourArea(cnt)<30000:  # remove small areas like noise and too big area like die edge
                area = cv2.contourArea(cnt)
                (x,y,w,h) = cv2.boundingRect(cnt)
                center_x=x+w//2
                center_y=y+h//2
                hull = cv2.convexHull(cnt)    # find the convex hull of contour
                hull = cv2.approxPolyDP(hull,0.02*cv2.arcLength(hull,True),True)
                #print(x-w)
                #print(y - h)
                if len(hull)==4 and 0.80<w/h<1.20: #We check the aspect ratio of the pad to avoid wrong detection or pads partially visible on the neighbouring die
                    #cv2.drawContours(img,[hull],0,(0,255,0),1)
                    #center=cv2.circle(img,(center_x,center_y),5, (0, 128, 0), 3)
                    #cv2.rectangle(img,(x, y), (x + w, y + h), (0, 128, 0), 3)
                    #list_pad.append([center_x,center_y,x,y,w,h,w*h,[hull],area])
                    list_pad.append([center_x, center_y, x, y, w, h, w * h, area,'automatic'])
                    idx=idx+1
        return(list_pad)


    def single_pad_list(self,list_pad):
        #Creation of a list to eliminate pads that have been detected multiples times
        list_pad.sort(key=itemgetter(7),reverse=True)
        list_single_pad=[]
        for pad in range(1,len(list_pad)-1):
            index=0
            for pad2 in range(pad+1,len(list_pad)):
                delta_center_x=range(list_pad[pad2][0]-list_pad[pad2][4],list_pad[pad2][0]+list_pad[pad2][4]+1)
                delta_center_y=range(list_pad[pad2][1]-list_pad[pad2][5],list_pad[pad2][1]+list_pad[pad2][5]+1)
                if (list_pad[pad][0]  in delta_center_x) and (list_pad[pad][1]  in delta_center_y):
                    double=list_pad #Useless
                else  :  
                    index=index+1
                    #print(index,len(list_pad)-(pad+1))
                    if index==(len(list_pad)-(pad+1)):
                        list_single_pad.append(list_pad[pad])
        list_single_pad.append(list_pad[-1])
        return(list_single_pad)
 

    def order_pad_list(self,list_single_pad,Pad_disposition):
        copy_list_pad=copy.deepcopy(list_single_pad)
        #Gross sort of the list
        for m in range(len(list_single_pad)):
              copy_list_pad[m][0]=(round(list_single_pad[m][0]/20))
              copy_list_pad[m][1]=(round(list_single_pad[m][1]/20))   
        copy_list_pad.sort(key=itemgetter(0))
        copy_list_pad.sort(key=itemgetter(1))
        
        #Fine sort of the list
        idx_h=-1
        idx_j=0
        check_ok=-1
        while check_ok!=(idx_j):
            idx_h=-1
            idx_j=0
            check_ok=0
            for h in range(len(Pad_disposition)):
                idx_h+=1
                for j in range(sum(Pad_disposition[h])-1):
                    idx_j+=1
                    if (copy_list_pad[idx_j-1][0]>(copy_list_pad[idx_j][0]+1)) or (copy_list_pad[idx_j-1][1]>(copy_list_pad[idx_j][1]+1)):
                        if copy_list_pad[idx_j-1][0]>(copy_list_pad[idx_j][0]+1):
                            copy_list_pad[idx_j-1],copy_list_pad[idx_j] = copy_list_pad[idx_j],copy_list_pad[idx_j-1]
                        elif copy_list_pad[idx_j][1]>(copy_list_pad[idx_j-1][1]+1):
                            copy_list_pad[idx_j],copy_list_pad[idx_j-1] = copy_list_pad[idx_j],copy_list_pad[idx_j-1]
                    else:
                        check_ok+=1
                idx_j+=1 
                check_ok+=1
                #print(idx_j,check_ok)

        for m in range(len(list_single_pad)):
            copy_list_pad[m][0]=copy_list_pad[m][0]*20
            copy_list_pad[m][1]=copy_list_pad[m][1]*20
        list_single_pad=copy_list_pad
        return(list_single_pad)
    
    # def order_pad_list(self,list_single_pad):
    #     copy_list_pad=copy.deepcopy(list_single_pad)
    #     for m in range(len(list_single_pad)):
    #         copy_list_pad[m][0]=(round(list_single_pad[m][0]/20))
    #         copy_list_pad[m][1]=(round(list_single_pad[m][1]/20))
    #     copy_list_pad.sort(key=itemgetter(0))
    #     copy_list_pad.sort(key=itemgetter(1))
    #     for m in range(len(list_single_pad)):
    #         copy_list_pad[m][0]=copy_list_pad[m][0]*20
    #         copy_list_pad[m][1]=copy_list_pad[m][1]*20
    #     list_single_pad=copy_list_pad
    #     return(list_single_pad)
    
    def draw_pad(self,list_single_pad,List_pad_name):
        #Draw rectangle of each detected pad on the original image                
        for pad3 in range(len(list_single_pad)):
            cv2.rectangle(self.img,(list_single_pad[pad3][2], list_single_pad[pad3][3]), (list_single_pad[pad3][2] + list_single_pad[pad3][4], list_single_pad[pad3][3] + list_single_pad[pad3][5]), (0, 128, 0), 3)
            #if List_pad_name[pad3]!=0:
                #cv2.putText(self.img, text= List_pad_name[pad3], org=(list_single_pad[pad3][2],list_single_pad[pad3][3]), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,0),thickness=2, lineType=cv2.LINE_AA)
    
    def name_pad(self,list_single_pad,List_pad_name,image):
         for pad_name in range(len(list_single_pad)):
             if List_pad_name[pad_name]!=0:
                 cv2.putText(image, text= List_pad_name[pad_name], org=(list_single_pad[pad_name][2],list_single_pad[pad_name][3]), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,0),thickness=2, lineType=cv2.LINE_AA)
    
        
    def comput_pad_area(self,list_single_pad):
        #Computation of pad area average considered as "true" pad size
        Pad_area=0
        for pad4 in range(len(list_single_pad)):
            Pad_area+=list_single_pad[pad4][6]
        Pad_area_average=Pad_area/len(list_single_pad)
        #print the number of detected pads and the image with the detected pad
        print('Number of detected pads on image ' +self.filename + ' is '+ str(len(list_single_pad)))
        return(Pad_area_average)
    
    
    def check_pad_position(self,list_single_pad,Pad_disposition,Product_ID):
    #Periodicity along X-axis is checked for each lign
        pad_count=-1
        X_period_pad=[]
        Y_alignement_pad=[]
        for ligne in range(len(Pad_disposition)):
            X_period=[]
            Y_alignement=[]
            #We create a list with center_X and center_Y of each pad in the given pad lign
            for pad_ligne in range(len(Pad_disposition[ligne])):
                if Pad_disposition[ligne][pad_ligne]!=0:
                    pad_count+=1
                    X_period.append(list_single_pad[pad_count][0])
                    Y_alignement.append(list_single_pad[pad_count][1])
                else : 
                    X_period.append('No')
                    Y_alignement.append('No')
            X_period_pad.append(X_period)
            Y_alignement_pad.append(Y_alignement)
            
            #We check if delta-X is quite constant between pad and if center_Y are quite similar
            for per in range(len(X_period_pad)):
                no_pad=0
                delta_x=[]
                delta_y=[]
                for per2 in range(len(X_period_pad[per])-1):
                    if X_period_pad[per][per2]!='No':
                        if no_pad==0:
                             pad_is = per2
                    if X_period_pad[per][per2+1]!='No':
                        delta_x.append((X_period_pad[per][per2+1]-X_period_pad[per][pad_is])/(no_pad+1))
                        delta_y.append(Y_alignement_pad[per][per2+1]-Y_alignement_pad[per][pad_is])
                        no_pad=0
                    else:
                        no_pad+=1
                #print(delta_x,delta_y)
                #if the difference is more than 25% the pad dimansion, it is considered as wrongly detected
                w_pad=[]
                h_pad=[]
                for j in range(len(list_single_pad)):
                    w_pad.append(list_single_pad[j][4])
                    h_pad.append(list_single_pad[j][5])
                if Product_ID in ['Iris', 'iris', 'Retina', 'retina']:
                    if len(delta_x)!=3:
                        TM.show_error('Pad position','The number of detected pads in X-axis is not correct')
                    else:
                         if (abs(delta_x[0]-delta_x[2]))>round((sum(w_pad)/len(w_pad))/4) or (max(delta_y)-min(delta_y))>round((sum(h_pad)/len(h_pad))/4) or delta_x[1]>1.45*(min(delta_x[0],delta_x[2])) or delta_x[1]<1.15*(min(delta_x[0],delta_x[2])):
                             TM.show_error('Pad periodicity issue','The perdiodicity of the pads in X-axis is not correct')
                             break
                else :
                     if (max(delta_x)-min(delta_x))>round((sum(w_pad)/len(w_pad))/4) or (max(delta_y)-min(delta_y))>round((sum(h_pad)/len(h_pad))/4):
                        #print('Error')
                        TM.show_error('Pad periodicity issue','The perdiodicity of the pads in X-axis is not correct')
                        break
                    
    #Periodicity along Y-axis is checked for each column
        copy_list_pad=copy.deepcopy(list_single_pad)
        copy_list_pad.sort(key=itemgetter(1))
        copy_list_pad.sort(key=itemgetter(0))
        pad_count=-1
        Y_period_pad=[]
        X_alignement_pad=[]
        for col in range(len(Pad_disposition[0])):
            Y_period=[]
            X_alignement=[]
            #We create a list with center_X and center_Y of each pad in the given pad column
            for pad_col in range(len(Pad_disposition)):
                if Pad_disposition[pad_col][col]!=0:
                    pad_count+=1
                    Y_period.append(copy_list_pad[pad_count][1])
                    X_alignement.append(copy_list_pad[pad_count][0])
                else : 
                    Y_period.append('No')
                    X_alignement.append('No')
            Y_period_pad.append(Y_period)
            X_alignement_pad.append(X_alignement)
            
            
            #We check if delta-Y is quite constant between pad and if center_X are quite similar
            for per in range(len(Y_period_pad)):
                if len(Y_period_pad[per])>1:
                    no_pad=0
                    delta_x=[]
                    delta_y=[]
                    for per2 in range(len(Y_period_pad[per])-1):
                        if Y_period_pad[per][per2]!='No':
                            if no_pad==0:
                                 pad_is = per2
                        if Y_period_pad[per][per2+1]!='No':
                            delta_x.append((Y_period_pad[per][per2+1]-Y_period_pad[per][pad_is])/(no_pad+1))
                            delta_y.append(X_alignement_pad[per][per2+1]-X_alignement_pad[per][pad_is])
                            no_pad=0
                        else:
                            no_pad+=1
                    #print(delta_x,delta_y)
                    #if the difference is more than 25% the pad dimansion, it is considered as wrongly detected
                    w_pad=[]
                    h_pad=[]
                    for j in range(len(list_single_pad)):
                        w_pad.append(list_single_pad[j][4])
                        h_pad.append(list_single_pad[j][5])
                    if (max(delta_x)-min(delta_x))>round((sum(w_pad)/len(w_pad))/4) or (max(delta_y)-min(delta_y))>round((sum(h_pad)/len(h_pad))/4):
                        #print('Error')
                        TM.show_error('Pad periodicity issue','The perdiodicity of the pads in Y-axis is not correct')
