import cv2


class Overlap_marks_to_pad(object):
         #---------------Check overlap between probemark and pad egde-----------------------------------#
    def __init__(self,img,list_single_pad,list_single_pad_mark):
         self.img = img
         self.list_single_pad = list_single_pad
         self.list_single_pad_mark = list_single_pad_mark
        
    def overlap_check(self,list_single_pad_mark,image):
           Overlap=[]
           pas_test=0
           for p in range(len(self.list_single_pad_mark)):
               pas_test+=1
               for q in range(len(self.list_single_pad)):
                   #Range of pad size in X and Y by pixel_crop pixels
                   pixel_crop=round(0.1*self.list_single_pad[q][4])
                   x_range_pad=range(pixel_crop+self.list_single_pad[q][2],self.list_single_pad[q][2]+self.list_single_pad[q][4]+1-pixel_crop)
                   y_range_pad=range(pixel_crop+self.list_single_pad[q][3],self.list_single_pad[q][3]+self.list_single_pad[q][5]+1-pixel_crop)
                   #We check in the center of the probemarks is within the pad. If no, we try the next pad. If yes we check for each coordinate for the mark if it is out of the pad
                   if self.list_single_pad_mark[p][0] in (x_range_pad) and self.list_single_pad_mark[p][1] in (y_range_pad):                    
                       list_point=self.list_single_pad_mark[p][3]
                       out_pad=0
                       for l in range(len(list_point[0])):
                           A=list_point[0].tolist()
                           #We checked if the detected probemarks is not on the edge on the cropped pad
                           if (A[l][0][0]+1 not in x_range_pad) or (A[l][0][0]-1 not in x_range_pad) or (A[l][0][1]+1 not in y_range_pad)or (A[l][0][1]-1 not in y_range_pad):
                               if out_pad==0:
                                   Overlap.append('Yes') 
                                   cv2.drawContours(image, self.list_single_pad_mark[p][3], 0, (255, 0, 0), 2)
                                   out_pad+=1
               if len(Overlap)<(p+1):
                   Overlap.append('No') 
           return(Overlap)