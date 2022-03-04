import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from serial.tools.list_ports import comports
#from PIL import ImageTk, Image
#import offset_win as ofsw
from tkinter import *
import tkinter.ttk  as ttk
import tkinter as tk
#from ttkthemes import ThemedStyle
import threading 
import multiprocessing as msg
import struct
import serial
import time
import sys
import os
import math
import collections
#import numpy as np
      

class CofeWin(tk.Tk):
    def __init__(self,mainBgColor,w_sig):   
        super().__init__()
        self.signal_width = w_sig 
        self.bg_color = mainBgColor
        #self.baud_rate = 500000
        self.baud_rate = 115200
        self.phi = math.pi/2
        self.start = True
        self.scrSize = False
        self.data = collections.deque([0] * self.signal_width, maxlen = self.signal_width)
        self.rawData = bytearray(36)
        self.UserInterface()
        self.plotTimer = 0
        self.previousTimer = 0
        


    def UserInterface(self):
        #создаем фаил для записи всех данных 
        self.main_data_file_name = ("dat/" + str(time.ctime()).replace(":","_"))
        self.main_data_file_name += "_all_info.txt"
        self.main_file = open(self.main_data_file_name,"w")
        self.main_file.write(">> ------DATA AND TIME------|--SYNCH 4b--|------------------------DATA 16b--------------------------|-----------------MNEM 12b-------------------|-------DATA 4b-------\n")
        self.main_file.close()

        #создаем изображения для кнопок 
        self.start_img = PhotoImage(file = "pic/play_32.png")
        self.stop_img  = PhotoImage(file = "pic/stop_32.png")
        self.save_img  = PhotoImage(file = "pic/save_32.png")
        self.clear_img = PhotoImage(file = "pic/clear_32.png")
        self.f_scr_img = PhotoImage(file = "pic/full_screen_32.png")
        self.com_img   = PhotoImage(file = "pic/com_32.png")
        
        #определяем размеры экрана на котором будем запускать приложение, установка иконки
        self.screenwidth = self.winfo_screenwidth()
        self.screenheight = self.winfo_screenheight()
        startSize = (str(self.screenwidth - 200) + "x" + str(self.screenheight - 200) + "+0+0")
        self.geometry(startSize)
        self.iconbitmap('pic/lightning.ico')
        self.title("Cofe Beta 0.0 " + "size " + str(self.screenwidth)+"x"+ str(self.screenheight) )

        #устанавливаем тему 
        #self.style = ThemedStyle(self)
        #self.style.set_theme("arc")
        #создаем и распологаем виджеты в главном окне 
        self.mainFrame = Frame(self,bg = self.bg_color)                        
        self.mainFrame.pack(side = TOP,fill=BOTH,expand = True)

        
        self.dataArea = Frame(self.mainFrame,bg = self.bg_color)
        self.dataArea.pack(side = TOP,fill = X)

        #фрейм для расположения текстовой информации
        #self.tWidth = self.screenwidth/3
        #self.tHight = self.screenwidth/3
        self.tex1Area = Frame(self.dataArea, bg = "blue")
        self.tex1Area.pack(side = RIGHT,padx = 0,pady = 0,anchor = NE,fill = Y)
        #self.tex1Area.pack_propagate(False)

        #фрейм для расположения анимации (отклонителя)
        self.animArea = Frame(self.dataArea, bg = self.bg_color)
        self.animArea.pack(side = LEFT,padx = 0,pady = 0,fill = BOTH, expand = True)


        #фрейм для расположения кнопок
        self.widgArea = Frame(self.mainFrame,bg = self.bg_color)    #фрейм для расположения кнопок и командных строк   
        self.widgArea.pack(side = BOTTOM,fill = X,anchor = NW)
        
        #фрейм для расположения сигнала  
        self.signalArea = Frame(self.mainFrame,bg = self.bg_color)  
        self.signalArea.pack(side = TOP, fill = X)


        self.commandBar(self.widgArea)
        self.textBar(self.dataArea,0)
        self.create_matplot_graf_area(1000)
        self.create_otkl_area(self.animArea,250,240,380)
        
    def commandBar(self,area):
        #список рабочих скоростей
        self.list_baud = ["9600","19200","38400","115200","128000","256000","500000","1000000"]

        #элементы в левой части фрейма
        self.com_lbl = Label(area,text = "COM",font="Consolas 18",bg = self.bg_color,fg = "#444444")
        self.com_lbl.pack(side = LEFT,padx = 2,pady = 2)


        self.com_comb = ttk.Combobox(area,width=10, postcommand = self.update_coms)
        self.com_comb.pack(side = LEFT,padx = 2,pady = 2)
        self.update_coms()
        
        self.baud_lbl = Label(area,text = "BAUD",font="Consolas 18",bg = self.bg_color,fg = "#444444")
        self.baud_lbl.pack(side = LEFT,padx = 2,pady = 2)

        self.baud_comb = ttk.Combobox(area,width=10,values = self.list_baud)
        self.baud_comb.pack(side = LEFT,padx = 2,pady = 2)

        #элементы в правой части фрейма
        self.startBtt = Button(area, text = "Start",bg = self.bg_color, image = self.start_img, relief=FLAT,activebackground = self.bg_color, borderwidth = 0, cursor ="hand2", command = self.start_serial) 
        self.startBtt.pack(side = RIGHT,padx = 4,pady = 2)

        self.clearBtt = Button(area, text = "Clear",bg = self.bg_color, image = self.clear_img, relief=FLAT,activebackground = self.bg_color, borderwidth = 0, cursor ="hand2", command = self.clear) 
        self.clearBtt.pack(side = RIGHT,padx = 4,pady = 2)

        self.saveBtt = Button(area, text = "Save",bg = self.bg_color, image = self.save_img, relief=FLAT,activebackground = self.bg_color, cursor ="hand2", borderwidth = 0, command = self.get_data_to_csv) 
        self.saveBtt.pack(side = RIGHT,padx = 4,pady = 2)
        
        self.fScrBtt = Button(area, text = "full",bg = self.bg_color, image = self.f_scr_img, relief=FLAT,activebackground = self.bg_color, cursor ="hand2", borderwidth = 0, command = self.full_size) 
        self.fScrBtt.pack(side = RIGHT,padx = 4,pady = 2)

    def textBar(self,area,BarAnchor):

        self.mainData = Text(self.tex1Area,height = 10,width = 70,takefocus = 0,fg = "#00d52a",bg = "#21252b" ,font="Consolas 18",relief=FLAT)
        self.mainData.pack(side = TOP, padx= BarAnchor, pady = BarAnchor, fil = BOTH, anchor = NE, expand = True)

        self.devData = Text(self.tex1Area,height = 1, takefocus = 0,fg = "#00d52a",bg = "#21252b" ,font="Consolas 8 ",relief=FLAT)
        self.devData.pack(side = TOP, padx = BarAnchor, pady = BarAnchor, fil = BOTH, anchor = NE, expand = True)


    def create_otkl_area(self,area,mid_x,mid_y,length):
        self.text_color = "white"
        color  = "white"
        dot_size = length/20

        self.mid_x = mid_x
        self.mid_y = mid_y
        self.length = length

        self.canvas = Canvas(area,width = 500,height = 500, bg = self.bg_color,highlightthickness=0)
        self.canvas.pack(side=TOP,fill=BOTH,padx = 2,pady = 2,expand = True)
        #градусная мера, текстовые выджеты 
        self.lbl_0   = self.canvas.create_text(mid_x , (mid_y - length/2 - 20),text = "0", fill = self.text_color, font="Verdana 20")
        self.lbl_90  = self.canvas.create_text((mid_x + length/2 + 25) ,mid_y, text = "90", fill = self.text_color, font="Verdana 20")
        self.lbl_180 = self.canvas.create_text(mid_x , (mid_y + length/2 + 20),text = "180", fill = self.text_color, font="Verdana 20")
        self.lbl_270 = self.canvas.create_text((mid_x - length/2 - 32) ,mid_y, text = "270", fill = self.text_color, font="Verdana 20")
        #создание осей по которым двигается отклонитель
        self.canvas.create_oval(mid_x - length/3, mid_y + length/3, mid_x + length/3, mid_y - length/3,width=1,outline='white')#,dash=(4,4))

        self.canvas.create_oval(mid_x - length/2, mid_y + length/2, mid_x + length/2, mid_y - length/2,width=1,outline='white')#,dash=(4,4))
        #текущее положение отклонителя, текстовый виджет
        self.otkl_txt = self.canvas.create_text(mid_x,mid_y,fill="white",font="Verdana 50")
        #точка отклонителя, изначально расположена по центру
        self.otkl_dot = self.canvas.create_oval( mid_x - dot_size, mid_y + dot_size, mid_x + length/30,mid_y - length/30, fill = "white", outline = self.bg_color)
     
    def create_matplot_graf_area(self,plt_interval):

        self.mainData.update()
        width = self.mainData.winfo_width()
        height = self.mainData.winfo_height()
        print(width)
        print(height)
        
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        #self.figure = plt.Figure(figsize=(15 , 2))
        self.figure = plt.Figure(figsize=(width*px , (height*2/3)*px))
        self.figure.patch.set_facecolor ("#21252b")#self.bg_color)
        
        
        
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#21252b")
        self.ax.tick_params(color = "#21252b", labelcolor = "grey", labelsize = 6)
        self.ax.spines['bottom'].set_color(self.bg_color)
        self.ax.spines['top'].set_color(self.bg_color)
        self.ax.spines['left'].set_color(self.bg_color)
        self.ax.spines['right'].set_color(self.bg_color)
        self.ax.grid(color = "#21252b")

   
        self.ax.set_xlabel("time")
        timeText = self.ax.text(0.5,0.95,'',transform = self.ax.transAxes)
       
        
        self.ax.set_xlim(0,self.signal_width)
        self.ax.set_ylim(-20000,20000)
        lineLabel = 'signal'

        
        self.canvas_graf = FigureCanvasTkAgg(self.figure, self.signalArea)
        self.canvas_graf.get_tk_widget().pack(side = TOP, padx = 0, pady = 0 ,expand = True, anchor = E)

        toolbar = NavigationToolbar2Tk(self.canvas_graf,self.signalArea,pack_toolbar = False)
        toolbar.pack(side = BOTTOM,anchor = E)
        toolbar.config(bg = self.bg_color)

        for button in toolbar.winfo_children():
            button.config(background=self.bg_color, relief = FLAT, borderwidth = 0)

        #self.canvas_graf._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lines = self.ax.plot([], [],color = 'yellow')[0]

        self.anim = animation.FuncAnimation(self.figure, self.animate, fargs = (lines,timeText),interval = 1000)
        plt.show()

    def motion(self,data):

        #координаты местопложения метки 
        o_x1 = (self.mid_x - self.length/30) + self.length/2.15* ( math.cos(math.radians(360 - data + 90)))    
        o_y1 = (self.mid_y + self.length/30) - self.length/2.15* ( math.sin(math.radians(360 - data + 90)))

        o_x2 = (self.mid_x + self.length/30) + self.length/2.15* ( math.cos(math.radians(360 - data + 90)))
        o_y2 = (self.mid_y - self.length/30) - self.length/2.15* ( math.sin(math.radians(360 - data + 90)))

        self.canvas.coords(self.otkl_dot,o_x1,o_y1,o_x2,o_y2) 

        #изменение надписи (значение отклонителя)
        self.canvas.itemconfig(self.otkl_txt, text = "%.1f" % self.num )    


    def start_serial(self):
        if (self.start == True):
            
            try:
                self.curentSerial = str(self.com_comb.get())
                self.curentBaud   = str(self.baud_comb.get())
                self.serial_connect = serial.Serial(self.curentSerial,self.curentBaud,timeout = 1000)
                print('Connect to: ' + self.curentSerial + ' at ' + self.curentBaud + ' BAUD.')
                self.devData.insert(INSERT,('>> Connect to: ' + self.curentSerial + ' at ' + self.curentBaud  + ' BAUD.\n'))
                self.devData.yview(END)

                thread = threading.Thread (target = self.read_data_tread)
                thread.start()
                self.com_comb.config (state = DISABLED)
                self.baud_comb.config (state = DISABLED)
                time.sleep(0.1)
            except:
                print('Failed to Connect with: ' + self.curentSerial + ' at ' + self.curentBaud + ' BAUD.')
                self.devData.insert(INSERT,('>> Failed to Connect with: ' + self.curentSerial + ' at ' + self.curentBaud + ' BAUD.\n'))
                self.devData.yview(END)

            self.start = False
            self.startBtt.configure(text = "Stop")
            self.startBtt.configure(image = self.stop_img)
            
        else:

            try:
                self.serial_connect.close()
                print('Disconnect to: ' + self.curentSerial + ' at ' + self.curentBaud + ' BAUD.')
                self.devData.insert(INSERT,('>> Disconnect to: ' + self.curentSerial + ' at ' + self.curentBaud + ' BAUD.\n'))
                self.devData.yview(END)

            except:
                print('UUUPS, PROBLEMM!')

            self.com_comb.config (state = NORMAL) 
            self.baud_comb.config (state = NORMAL)
            self.startBtt.configure(text = "Start")
            self.startBtt.configure(image = self.start_img)
            self.start = True


    def read_data_tread(self):
        while True:
        
            self.serial_connect.reset_input_buffer()
            self.rawData = bytearray(self.serial_connect.readline(200))

            #curentTimer = time.perf_counter()
            #self.plotTimer = int((curentTimer - self.previousTimer)*1000)
            #self.previousTimer = curentTimer
            
            self.devData.insert(INSERT,(str(self.rawData)[10:] +"len "+ str(len(self.rawData)) + "\n"))
            self.devData.yview(END)

            print(self.rawData)
            for i in range(4,(len(self.rawData)-16),2):
                value, = struct.unpack('>h', self.rawData[i:i+2])
                self.data.append(value)
            
            #if  ( self.rawData[0:4] in (b'1234')) and (self.rawData[20:32] not in b"NODATA\x00\x00\x00\x00\x00\x00") and (len(self.rawData) == 36 ):
            if (len(self.rawData) == 200):
                self.write_info_in_main_file(self.rawData)
                self.mainData.config(state = NORMAL)
                self.mainData.insert(INSERT,self.get_data_from(self.rawData)) 
                self.mainData.yview(END)
                self.mainData.config(state = DISABLED)
                if (self.mnem_txt in "GFCX"):
                    self.motion(float(self.num[0]))
                    
            else:
                if (len(self.rawData) == 200):
                    self.write_info_in_main_file(self.rawData)
                self.serial_connect.reset_input_buffer()
                self.rawData.clear()

    def get_data_from(self,array):
        sinc_data = struct.unpack("4s",array[0:4])
        sign_data = struct.unpack(">8H",array[4:20])
        mnem_data = struct.unpack("12s",array[20:32])
        self.num  = struct.unpack("f",array[32:36])
        self.numFormat = "%." + str(array[31]) + "f"
        self.mnem_txt = (str(mnem_data))[3:(str(mnem_data).find("x00"))-1]
        self.text_data = ">> " + (time.ctime()[11:19]).ljust(8," ") + " | " + self.mnem_txt.ljust(6," ") + " | " +  str(self.numFormat  % self.num).ljust(5," ") + "\n"
        return(self.text_data)          

    def get_data_to_csv(self):
        data_txt = self.mainData.get(1.0,END)
        new_name = self.create_new_file()
        file = open(new_name,"w")
        file.write(data_txt)
        file.close()

        
    def create_new_file(self):
        self.file_name = time.ctime()
        self.file_name = ("dat/"+ self.file_name.replace(":","_"))
        self.file_name += ".txt"
        return self.file_name

         
    def write_info_in_main_file(self,data):
        sinc_data = struct.unpack("4s",data[0:4])
        sign_data = struct.unpack(">8H",data[4:20])
        mnem_data = struct.unpack("12s",data[20:32])
        try:
            num_data  = struct.unpack("f",data[32:])
        except:
            num_data = 0
        self.main_file = open(self.main_data_file_name,"a")
        self.main_file.write(">> " + time.ctime() + " | " + str(sinc_data) + " | " + str(sign_data) + " | " + str(mnem_data).ljust(42," ") + " | " + str(num_data) + "\n")
        self.main_file.close()

    def clear(self):
        self.mainData.config(state = NORMAL)
        self.mainData.delete(1.0,END)
        self.mainData.config(state = DISABLED)
        
    def animate(self,frame,lines,timeText):
        lines.set_data(range(self.signal_width),self.data)
        timeText.set_text('')

        
    def full_size(self):
        
        if self.scrSize == False:
            self.attributes("-fullscreen",True)
            self.scrSize = True

        else:
            self.attributes("-fullscreen",False)
            self.scrSize = False

    #обновляем количество подключенных COM - портов
    def update_coms(self):
        list = [p.device for p in comports()]
        self.com_comb['values'] = list
    

            
def main():
    app = CofeWin("#282c35",10000)
    app.mainloop()
        
if __name__ == '__main__':
    main()
   

























