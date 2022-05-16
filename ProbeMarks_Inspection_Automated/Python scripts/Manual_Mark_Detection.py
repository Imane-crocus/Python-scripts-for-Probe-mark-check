import argparse
import imutils
import cv2
import numpy as np
import msvcrt
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path

class Manual_Mark_Detection(object):
    def __init__(self,img,filename,list_mark):
        self.img=img
        self.filename=filename
        self.list_mark=list_mark

    def img_resize(self,save_path,filename):
        self.img = cv2.imread(save_path+'\\'+ filename)
        size_img=self.img.shape
        #Image resizeing (twice smaller) to avoid artefact during image treatment due to too much details
        self.img=imutils.resize(self.img, width=1000)
        return(self.img)

    def click_and_crop_mark(self,event, x, y, flags, list_mark):
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
            # Ellipse data
            cX = math.floor((refPt[0][0] + refPt[1][0]) / 2)
            cY = math.floor((refPt[0][1] + refPt[1][1]) / 2)
            center_coordinates = (cX, cY)
            axesLength = (abs(math.floor((refPt[0][0]-refPt[1][0])/2)),abs(math.floor((refPt[0][1]-refPt[1][1])/2)))
            ellipse_surface = axesLength[0] * axesLength[1] * math.pi
            hull_pad = 30
            detection_mode = 'manual'
            list_mark.append([cX, cY, ellipse_surface,[np.array([[[cX+axesLength[0],cY]],[[cX-axesLength[0],cY]],[[cX,cY-axesLength[1]]],[[cX,cY+axesLength[1]]]])],detection_mode])
            cv2.ellipse(self.img, center_coordinates, axesLength, 0, 0, 360, (0, 128, 255), 3)
            # print(list_mark)
            cv2.imshow("image", self.img)
        return (self.list_mark)



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
