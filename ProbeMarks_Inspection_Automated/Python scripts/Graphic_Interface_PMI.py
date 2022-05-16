# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 15:58:57 2021

@author: dlamaison
"""

import tkinter as tk
import tkinter.ttk

root= tk.Tk()
#win1 = tk.Toplevel(root)

global Input_data
global entry1
canvas1 = tk.Canvas(root, width = 600, height = 180)
canvas1.pack()

entry0 = tk.Entry (root)
entry1 = tk.Entry (root) 


    
def get_data():

    global Input_data
    #print([entry2.get(),entry3.get(),entry4.get(),entry5.get(),entry6.get()])
    #Input_data=[entry1.get(),entry2.get(),entry3.get(),entry4.get(),entry5.get(),[float(entry6.get())],entry0.get()]
    Input_data=[entry0.get(),entry1.get()]
    #print(Input_data)
    return(Input_data)

    
    
def gui():

    
    canvas1.create_window(350, 50,  width=300, window=entry0)
    canvas1.create_window(350, 90,  width=300, window=entry1)
    
    path = tk.Label(root, text= 'Saving path')
    canvas1.create_window(150, 50, window=path)
    
    
    
    text0 = tk.Label(root, text= 'Input data for PMI')
    canvas1.create_window(350, 10, window=text0)
    text1 = tk.Label(root, text= 'Product')
    canvas1.create_window(150, 90, window=text1)  
     
    button1 = tk.Button(root,text='Validate Data', command=get_data)
    button2 = tk.Button(root,text='Start the inspection', command=root.destroy)
    
    canvas1.create_window(350, 130, window=button1)
    canvas1.create_window(350, 170, window=button2)
    
    root.mainloop()


    save_path=Input_data[0]
    Product=Input_data[1]
    #print(save_path)
    save_path.encode('unicode-escape')
    #print(xSide,ySide,xStep,yStep,Max_field,rotDegree,save_path)
    return(save_path,Product)





