import tkinter as tk
import tkinter.ttk  as ttk
from tkinter import *


class Offset_Window(tk.Toplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.iconbitmap('compas.ico')
        self.title("Offset config V 0.01")
        self.resizable(width = False, height = False)

        self.new_offset = tk.StringVar()
        
        #1_фрейм для основной надписи 
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side = TOP, fill=BOTH)

        self.main_label = ttk.Label(self.main_frame,text = "Configuration table",font="Verdana 15")
        self.main_label.pack(side = TOP)

        #2_фрейм для таблицы виджетов 
        self.second_frame = ttk.Frame(self)
        self.second_frame.pack(side = TOP, fill=BOTH)

        self.offset_lbl = ttk.Label(self.second_frame,text = "Offset",font="Verdana 13")
        self.offset_lbl.pack(side = LEFT,padx = 2,pady = 2)
        
        self.main_entr = ttk.Entry(self.second_frame,width = 10,font="Verdana 13",textvariable = self.new_offset)
        self.main_entr.pack(side = LEFT,padx = 2,pady = 2)

        self.main_button = ttk.Button(self.second_frame,width = 10,text = "Apply",command=self.destroy)
        self.main_button.pack(side = LEFT,padx = 2,pady = 2)
        
        #3_фрейм для текстового виджета вывода ошибок
        self.eror_frame = ttk.Frame(self)
        self.eror_frame.pack(side = TOP, fill=BOTH)
        
        self.warning_lbl_frame = ttk.LabelFrame(self.eror_frame,text = "Warning")
        self.warning_lbl_frame.pack(side = TOP)
        
        self.err_data = Text(self.warning_lbl_frame,width= 30,height=6,takefocus = 0)
        self.err_data.pack(side=LEFT,fill=BOTH,pady = 2,padx = 2)

        self.scrollbar = ttk.Scrollbar(self.warning_lbl_frame)
        self.scrollbar.pack(side = LEFT,fill=Y)
        
        self.err_data.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.err_data.yview)

       
        
        
    def open(self):
         self.grab_set()
         self.wait_window()
         new_value = self.new_offset.get()
         return(new_value)

        
if __name__ == '__main__':
    root = tk.Tk() 
    Offset_Window(root)
   
