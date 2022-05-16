# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 15:58:57 2021

@author: ilemammer
"""

import tkinter as tk
import tkinter.ttk

def show_error(title,core):
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showerror(title,core)
    root.destroy()

def ask_question(title,core,data):
    root = tk.Tk()
    root.withdraw()
    MsgBox = tk.messagebox.askquestion(title,core,icon=data)
    root.destroy()
    return MsgBox

def show_info(title,core,data):
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showinfo(title,core,icon=data)
    tk.Tk().destroy()

def show_warning(title,core,data):
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showwarning(title,core,icon=data)
    tk.Tk().destroy()