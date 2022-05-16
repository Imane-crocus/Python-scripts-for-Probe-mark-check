import argparse
import imutils
import cv2
import numpy as np
import msvcrt
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path

class Manual_Pad_Detection(object):
    def __init__(self,img,filename,list_pad):
        self.img=img
        self.filename=filename
        self.list_pad=list_pad

    def img_resize(self,save_path,filename):
        self.img = cv2.imread(save_path+'\\'+ filename)
        size_img=self.img.shape
        #Image resizeing (twice smaller) to avoid artefact during image treatment due to too much details
        self.img=imutils.resize(self.img, width=1000)
        return(self.img)

    def click_and_crop_pad(self, event, x, y, flags, list_pad):
        # grab references to the global variables
        global refPt, cropping
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv2.EVENT_LBUTTONDOWN:
            refPt = [(x, y)]
            cropping = True
        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            refPt.append((x, y))
            cropping = False
            # draw a rectangle around the region of interest
            cv2.rectangle(self.img, refPt[0], refPt[1], (0, 0, 255), 2)
            w = abs(refPt[0][0] - refPt[1][0])
            h = abs(refPt[0][1] - refPt[1][1])
            area = abs(refPt[0][0] - refPt[1][0]) * abs(refPt[0][1] - refPt[1][1])
            center_x = abs((math.floor((refPt[0][0] + refPt[1][0]) / 2)))
            center_y = abs((math.floor((refPt[0][1] + refPt[1][1]) / 2)))
            detection_mode = 'manual'
            out_x=min(refPt[0][0],refPt[1][0])
            out_y=min(refPt[0][1],refPt[1][1])
            if abs(refPt[0][1] - refPt[1][1]) == 0:
                ratio = 0
            else:
                ratio = abs(refPt[0][0] - refPt[1][0]) / abs(refPt[0][1] - refPt[1][1])
            if 0.80 < ratio < 1.20:  # We check the aspect ratio of the pad to avoid wrong detection or pads partially visible on the neighbouring die
                #self.list_pad.append([center_x, center_y, x, y, w, h, w * h, 4, area, detection_mode])
                self.list_pad.append([center_x, center_y, out_x, out_y, w, h, w * h, area,detection_mode])
                #print(self.list_pad)
            cv2.imshow("image", self.img)
        return (self.list_pad)



    def updateArray(array, indices):
        lin = np.arange(array.size)
        newArray = array.flatten()
        newArray[lin[indices]] = 1
        return newArray.reshape(array.shape)

    def onselect(verts):
        global array, pix
        p = path.Path(verts)
        ind = p.contains_points(pix, radius=1)
        array = updateArray(array, ind)
        msk.set_data(array)
        fig.canvas.draw_idle()
