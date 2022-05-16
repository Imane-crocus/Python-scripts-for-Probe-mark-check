import pandas as pd
import tkinter as tk
import cv2
import datetime
import Tkinter_Message as TM

class Output_file(object):
    #---------------File summary start-----------------------------------#
    def __init__(self,list_single_pad,list_single_pad_mark,Product_ID,Lot_ID,Wafer_ID,Pad_area_average,Overlap,picture_nb,filename,save_path):
         self.list_single_pad = list_single_pad
         self.list_single_pad_mark = list_single_pad_mark  
         self.Pad_area_average = Pad_area_average
         self.Product_ID = Product_ID
         self.Lot_ID = Lot_ID
         self.Wafer_ID = Wafer_ID
         self.Overlap = Overlap
         self.picture_nb = picture_nb
         self.filename = filename
         self.save_path = save_path
         self.pad_nb=1


    def acceptance_criteria(self,Product,Lot,Wafer,Pad_nb,Ratio,Threshold_marks,db,Pass_acceptance_criteria):
        Product.append(self.Product_ID)
        Lot.append(self.Lot_ID)
        Wafer.append(self.Wafer_ID)
        Pad_nb.append(db+1)
        Ratio = Ratio+[100*self.list_single_pad_mark[db][2]/self.Pad_area_average]
        #Overlap.append('No') #To be changed
        if self.Overlap[db]=='No' and Ratio[-1]<Threshold_marks:
            acceptance_criteria = 'Yes'
        else :
            acceptance_criteria = 'No'
        Pass_acceptance_criteria.append(acceptance_criteria)
        return(Pass_acceptance_criteria,Ratio,Product,Lot,Wafer,Pad_nb)
         
    
    def write_db_file(self,filename,save_path,overlap,Product,Lot,Wafer,Pad_detection,Pad_nb, Mark_detection,Ratio,Pass_acceptance_criteria,MsgBox):
        if self.picture_nb==1 and self.pad_nb==1:
            check_header=True
        else:
            check_header=False
        #Output txt file which summarize the inspection
        if MsgBox == 'yes':
            df = pd.DataFrame({'Product' : Product, 'Lot' : Lot, 'Wafer n°' : Wafer, 'Picture name' : filename, 'Pad n°' : Pad_nb, 'Probemark to pad ratio (%)': Ratio, 
                                'Probemark on pad edge': overlap, 'Pass Acceptance Criteria (with ratio = 20%-3% GB)' : Pass_acceptance_criteria, 'Pad detection type' : Pad_detection, 
                                'Probemark detection type' : Mark_detection, 'Date' : datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")})
            df.to_csv(save_path+'\Probemark_Inspection'+ '_'+ Product +'_' + Lot+ '_'+ str(Wafer)+'.txt', index=None, sep='\t', mode='a',header=check_header)
            df.to_csv('\\\\crocusfr\\Shares\\Data\\Wafer Test\\Wafer Inspection\\Report\\Probemark_Inspection_Report_Summary.txt', index=None, sep='\t', mode='a',header=False)
            #df.to_csv('\\\\192.168.25.25\\Shares\\Data\\Wafer Test\\Wafer Inspection\\Report\\Probemark_Inspection_Report_Summary.txt', index=None, sep='\t', mode='a',header=False)
        else :
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        self.pad_nb+=1
        return(df)
    
    
    def exitApplication(self):
        MsgBox = TM.ask_question('Validation','Do you accept the image analysis?','info')
        return(MsgBox)
