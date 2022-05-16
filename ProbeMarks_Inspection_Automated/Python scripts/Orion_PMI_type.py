# -*- coding: utf-8 -*-
"""
Created on Mon May  9 10:26:01 2022

@author: dlamaison
"""
import tkinter as tk
import tkinter.ttk

def orion_pmi_choice():
    root2=tk.Tk()
    #root.geometry('300x200')
    canvas3 = tk.Canvas(root2, width = 300, height = 100)
    canvas3.pack()
    
    def action(event):
        global select
        select=listeCombo.get()
        print("Votre selection est: '",select,"'")
  
    labelChoix = tk.Label(root2, text = 'Choose the Orion PMI type')
    #labelChoix.place(relx = 0.5,rely = 0.1,anchor = 'ne')
    labelChoix.pack()
    
   # listeProduits = ["Retina", "Hammer/Empire", "Nimbus", "Halo2","Personnalized"]
    listeProduits = ["MSI", "ASIC"]
    
    listeCombo = tkinter.ttk.Combobox(root2, values=listeProduits)
    listeCombo.current(0)
    
    listeCombo.pack()
    listeCombo.bind("<<ComboboxSelected>>",action)
    
    button3 = tk.Button(root2,text='Validation', command=root2.destroy)
    canvas3.create_window(150, 50, window=button3)
    
    root2.mainloop()
    return(select)