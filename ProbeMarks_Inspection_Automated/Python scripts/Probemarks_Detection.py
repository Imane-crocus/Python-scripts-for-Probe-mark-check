import cv2
import numpy as np
from operator import itemgetter
import tkinter as tk
import copy
import Tkinter_Message as TM

class Probemarks_detection(object):
     #---------------Probemark detection start-----------------------------------#
      def __init__(self,img,filename,True_nb_probemarks,list_single_pad):
          self.img = img
          self.filename = filename
          self.True_nb_probemarks = True_nb_probemarks
          self.list_single_pad = list_single_pad
          self.list_pad_mark = []
          self.index_pad = -1
        
    
      def treatment(self,img,nb_pad):
            #We take the coordinates of each pad on the original picture
            x = self.list_single_pad[nb_pad][2]
            y = self.list_single_pad[nb_pad][3]
            w = self.list_single_pad[nb_pad][4]
            h = self.list_single_pad[nb_pad][5]
            #We crop the original picture only on the wanted pad (to be sure not to detect again pad edge)
            pixel_crop=round(0.1*w)
            crop_img = self.img[y+pixel_crop:y+h-pixel_crop,x+pixel_crop:x+w-pixel_crop]
            
            #We apply picture algorithm treatment
            gray_pad = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
            blur_pad = cv2.medianBlur(gray_pad, 3)
            
            crop_img = crop_img[:,:,1]
            th, crop_img = cv2.threshold(crop_img, 0, 255, cv2.THRESH_OTSU)
            thresh = cv2.adaptiveThreshold(crop_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,7,2)
            thresh=cv2.dilate(thresh,None, iterations=2) #1
            # thresh=cv2.erode(thresh,None, iterations=2) #1
            # thresh=cv2.dilate(thresh,None, iterations=1) #1
            #cv2.imshow(str(nb_pad), thresh)
            
            close_pad = cv2.Canny(blur_pad, 40, 60)
            close_pad=cv2.dilate(close_pad,None, iterations=2) #1
            close_pad=cv2.erode(close_pad,None, iterations=4) #1
            close_pad=cv2.dilate(close_pad,None, iterations=4) #1
            close_pad=cv2.erode(close_pad,None, iterations=1) 
            close_pad=cv2.dilate(close_pad,None, iterations=2)
            #cv2.imshow(str(nb_pad), close_pad)
            
            close_pad2 = cv2.Canny(blur_pad, 40, 60)
            close_pad2=cv2.dilate(close_pad2,None, iterations=2) #1
            close_pad2=cv2.erode(close_pad2,None, iterations=4) #1
            close_pad2=cv2.dilate(close_pad2,None, iterations=3) #1
            close_pad2=cv2.erode(close_pad2,None, iterations=1) 
            close_pad2=cv2.dilate(close_pad2,None, iterations=2)
            #cv2.imshow(str(nb_pad), thresh)
            
            #We find the contours of the probemarks on the cropped image
            contours_pad, hierarchy1_pad = cv2.findContours(close_pad, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours_pad2, hierarchy1_pad2 = cv2.findContours(close_pad2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours_pad3, hierarchy1_pad3 = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours_pad=contours_pad+contours_pad2+contours_pad3
 
            #cv2.waitKey(0)
            return(contours_pad,x,y,pixel_crop,w,h)
            
    
      def coordinate_correction(self,contours_pad,x,y,pixel_crop):
            #We convert the coordinates contours on the cropped image to the coordinates on the original image
            liste2=[]
            cvt_idx=-1
            cvt2_idx=-1
            for cvt in contours_pad:
                cvt_idx+=1
                cvt2_idx=-1
                liste_correct=[]
                for cvt2 in cvt:
                    cvt2_idx+=1
                    liste=contours_pad[cvt_idx][cvt2_idx].tolist()
                    liste[0][0]=liste[0][0]+x+pixel_crop
                    liste[0][1]=liste[0][1]+y+pixel_crop
                    liste_correct=liste_correct+liste
                liste_correct=[liste_correct]
                A=np.array(liste_correct, dtype='int32')
                liste2.append(A)
            contours_pad=liste2
            return(contours_pad)
            
        
      def detect_probemark(self,contours_pad,w,h,pad_area_average):
            self.index_pad=self.index_pad+1
            #We draw the contours of the detected probemarks      
            for cnt_pad in contours_pad:
                hull_pad = cv2.convexHull(cnt_pad)    # find the convex hull of contour
                hull_pad = cv2.approxPolyDP(hull_pad,0.02*cv2.arcLength(hull_pad,True),True)
                area_pad = cv2.contourArea(cnt_pad)
                (x_pad,y_pad,w_pad,h_pad) = cv2.boundingRect(cnt_pad)                
                M = cv2.moments(cnt_pad)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                center_pad_to_mark_X=abs(cX-self.list_single_pad[self.index_pad][0]) #avoid false detection near pad edge
                center_pad_to_mark_Y=abs(cY-self.list_single_pad[self.index_pad][1]) #avoid false detection near pad edge
                if len(hull_pad)>4 and 50*pad_area_average>area_pad>0.05*pad_area_average and center_pad_to_mark_X<30 and center_pad_to_mark_Y<30:
                    #print(area_pad)
                    #cv2.drawContours(img, [hull_pad], 0, (0, 255, 0), 2)
                    #print([hull_pad])
                    #index_pad=index_pad+1
                    self.list_pad_mark.append([cX,cY,area_pad,[hull_pad],'automatic'])
                    # cv2.imshow("cropped", close_pad)
                    # cv2.waitKey(0) 
            return(self.list_pad_mark)
        
        
      def single_probemark_list(self,list_pad_mark):
            #Eliminate double probemark detection on a single pad
            self.list_pad_mark.sort(reverse=True,key=itemgetter(2)) #Sorted from the biggest to the smallest probemark
            list_single_pad_mark=[]
            for i in range(len(self.list_pad_mark)-1):   
                idx_c=0
                for j in range(i+1,len(self.list_pad_mark)):
                    center_mark_x=self.list_pad_mark[j][0]
                    center_mark_y=self.list_pad_mark[j][1]
                    if (abs(center_mark_x-self.list_pad_mark[i][0])<30 and abs(center_mark_y-self.list_pad_mark[i][1])<30):
                        idx_f=1 #useless
                    else:
                        idx_c+=1
                        if idx_c==(len(self.list_pad_mark)-(i+1)):
                            list_single_pad_mark.append(self.list_pad_mark[i])
            list_single_pad_mark.append (self.list_pad_mark[-1]) 
            return(list_single_pad_mark)
        
        
      def order_pad_list(self,list_single_pad_mark):
          copy_list_pad=copy.deepcopy(list_single_pad_mark)
          for m in range(len(list_single_pad_mark)):
              copy_list_pad[m][0]=round(list_single_pad_mark[m][0]/20)
              copy_list_pad[m][1]=round(list_single_pad_mark[m][1]/20)
          copy_list_pad.sort(key=itemgetter(0))
          copy_list_pad.sort(key=itemgetter(1))
          for m in range(len(list_single_pad_mark)):
                copy_list_pad[m][0]=list_single_pad_mark[m][0]*20
                copy_list_pad[m][1]=list_single_pad_mark[m][1]*20
          list_single_pad_mark=copy_list_pad
          return(list_single_pad_mark)
    
    
      def match_mark_to_pad(self,list_single_pad,list_single_pad_mark,List_pad_name):
           for nb in range(len(list_single_pad_mark)):
               cX_mark=list_single_pad_mark[nb][0]
               cY_mark=list_single_pad_mark[nb][1]
               for nb2 in range(len(list_single_pad)):
                   xRange_pad=range(list_single_pad[nb2][2], list_single_pad[nb2][2]+list_single_pad[nb2][4]+1)
                   yRange_pad=range(list_single_pad[nb2][3], list_single_pad[nb2][3]+list_single_pad[nb2][5]+1)
                   if (cX_mark in xRange_pad) and (cY_mark in yRange_pad):
                       list_single_pad_mark[nb].append(List_pad_name[nb2])
                       if List_pad_name[nb2]==0 :
                            TM.show_warning('Warning', 'Probemarks is detected on a wrong pad','warning')
           return(list_single_pad_mark) 
                     
      def text_probemark(self,list_single_pad_mark,ratio,image):
                 cv2.putText(image, text= (str(round(ratio,2)) + "%"), org=(list_single_pad_mark[0]-20,list_single_pad_mark[1]), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,0),thickness=1, lineType=cv2.LINE_AA)
       
      def text_overlap_probemark(self,list_single_pad_mark,overlap,image):
             cv2.putText(image, text= ("Mark on edge : " + overlap), org=(list_single_pad_mark[0]-20,list_single_pad_mark[1]+40), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.3, color=(255,255,255),thickness=1, lineType=cv2.LINE_AA)

      def draw_probemark(self,list_single_pad_mark,True_nb_probemarks,image):
            #Draw the single probemark detected on each pad
            for k in range(len(list_single_pad_mark)):
                 cv2.drawContours(image, list_single_pad_mark[k][3], 0, (0, 255, 0), 2)
            print('Number of detected probemarks on image '+ self.filename + ' is ' + str(len(list_single_pad_mark)))
            
            #Comparison detected vs expected numbe rof probemarks
            if True_nb_probemarks!=len(list_single_pad_mark):
                TM.show_warning('Probemarks detection issue','The number of detected probemarks is ' + str(len(list_single_pad_mark)) + ' while it should be ' + str(True_nb_probemarks),'warning')
            return(list_single_pad_mark)
        
        
      def pass_or_fail(self,list_single_pad_mark,pass_acceptance_criteria,simplified_analyzed):
            if pass_acceptance_criteria=='Yes':
                cv2.putText(simplified_analyzed, text= ("PASS"), org=(list_single_pad_mark[0]-40,list_single_pad_mark[1]-40), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,255,0),thickness=2, lineType=cv2.LINE_AA)
            else :
                cv2.putText(simplified_analyzed, text= ("FAIL"), org=(list_single_pad_mark[0]-40,list_single_pad_mark[1]-40), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,255),thickness=2, lineType=cv2.LINE_AA)
                