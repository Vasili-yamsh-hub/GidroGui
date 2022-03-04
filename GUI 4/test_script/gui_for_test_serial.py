from serial.tools.list_ports import comports
from   threading    import Thread
import tkinter.ttk  as ttk
from   tkinter      import*
import tkinter as  tk
import threading 
import serial
import time
import struct
import test_serial


class MainWin(tk.Tk):

    
    
    def __init__(self):
        super().__init__()
        self.title("READ DATA")
        self.list_devices = ["NDM","KVM","MGK"]
        self.list_commands = ["READ","CLEAR","MODE","VIEW"]
        self.list_baud = ["9600","38400","115200","500000"]
        self.start = True
       

        #create Frames
        self.flash_frame = ttk.LabelFrame(self,text = "Read data")#,width = 100 ,height = 100)
        self.flash_frame.pack(side = LEFT,anchor = N,fill = BOTH)

        self.device_frame = Frame(self.flash_frame,width = 100 ,height = 100)
        self.device_frame.pack(anchor = W,padx = 1,pady = 1)

        self.text_frame = Frame(self.flash_frame,width = 100 ,height = 100)
        self.text_frame.pack(anchor = W,padx = 1,pady = 1)

        self.text_but_frame = Frame(self.flash_frame,width = 100 ,height = 100)
        self.text_but_frame.pack(anchor = W,padx = 1,pady = 1)

        #create dev_components
        self.dev_label = ttk.Label(self.device_frame,text = "DEV")
        self.dev_label.grid(row = 0,column = 0,padx = 2,pady = 2)

        self.dev_comb = ttk.Combobox(self.device_frame,width=10,values = self.list_devices)
        self.dev_comb.grid(row = 0,column = 1,padx = 2,pady = 2)

        self.vers_label = ttk.Label(self.device_frame,text = "VERS")
        self.vers_label.grid(row = 0,column = 2,padx = 2,pady = 2)

        self.vers_comb = ttk.Combobox(self.device_frame,width=10)
        self.vers_comb.grid(row = 0,column = 3,padx = 2,pady = 2)

        #create com_components
        self.com_label = ttk.Label(self.device_frame,text = "COM")
        self.com_label.grid(row = 1,column = 0,padx = 2,pady = 2)

        self.com_comb = ttk.Combobox(self.device_frame,width=10,values = [p.device for p in comports()])
        self.com_comb.grid(row = 1,column = 1,padx = 2,pady = 2)

        self.com_label = ttk.Label(self.device_frame,text = "BAUD")
        self.com_label.grid(row = 1,column = 2,padx = 2,pady = 2)

        self.com_baud = ttk.Combobox(self.device_frame,width=10,values = self.list_baud)
        self.com_baud.grid(row = 1,column = 3,padx = 2,pady = 2)

        #create cmd_components
        self.cmd_label = ttk.Label(self.device_frame,text = "CMD")
        self.cmd_label.grid(row = 2,column = 0,padx = 2,pady = 2)

        self.cmd_comb = ttk.Combobox(self.device_frame,width=10,values = self.list_commands)
        self.cmd_comb.grid(row = 2,column = 1,padx = 2,pady = 2)


        #create text_components
        self.scrollbar = ttk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=RIGHT,fill=Y, pady=5)
        
        self.inp_data = Text(self.text_frame,width=140,height=20,takefocus = 0,state=NORMAL)
        self.inp_data.pack(side=LEFT,fill=BOTH,pady=5)

        self.inp_data.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.inp_data.yview)
        
        #create buttons_components
        self.clear_button = ttk.Button(self.text_but_frame,text = "Clear",command = lambda:(self.inp_data.delete(1.0,END)))
        self.clear_button.pack(side=LEFT,padx=5, pady=5)

        self.save_button = ttk.Button(self.text_but_frame,text = "Save")
        self.save_button.pack(side=LEFT,padx=5, pady=5)

        self.fgh_button = ttk.Button(self.text_but_frame,text = "Start", command = self.start_serial)#,command = self.test_com)
        self.fgh_button.pack(side=LEFT,padx=5, pady=5)


    def start_serial(self):
        if (self.start == True):

            try:
                self.serial_connect = serial.Serial(self.com_comb.get(),self.com_baud.get(),timeout = 10)
                print('Connect to: ' + str(self.com_comb.get()) + ' at ' + str(self.com_baud.get()) + ' BAUD.')
                thread = threading.Thread (target = self.read_data)
                thread.start()
                self.fgh_button.configure(text = "Stop")
                self.com_comb.config (state = DISABLED)
                self.com_baud.config (state = DISABLED)
            except:
                print('Failed to Connect with: ' + str(self.com_comb.get()) + ' at ' + str(self.com_baud.get()) + ' BAUD.')

            self.start = False
            

        else:

            try:
                self.serial_connect.close()
                print('Disconnect to: ' + str(self.com_comb.get()) + ' at ' + str(self.com_baud.get()) + ' BAUD.')

            except:
                print('UUUPS, PROBLEMM!')

            self.com_comb.config (state = NORMAL)
            self.com_baud.config (state = NORMAL)  
            self.fgh_button.configure(text = "Start")
            self.start = True


    def read_data(self):
        while True:
            self.serial_connect.reset_input_buffer()
            data = bytearray(self.serial_connect.readline(36))
            if data[0:4] in (b'1234'):
                #self.serial_connect.close()
                print(data)
            else:
                self.serial_connect.reset_input_buffer()
                data.clear()
                print("no sync") 

        
        

    
    def check_thread(self,thread):
        if thread.is_alive():
            self.after(100,lambda:self.check_thread(thread))
            #print(thread.getName())
        else:
            print(thread.name,"off")
    
    def test_com(self):
        if (MainWin.start == True):
            print("Start main programm")
            self.fgh_button.configure(text = "Stop")
            self.a = test_serial.Serial_tread(self.com_comb.get(),self.com_baud.get(),100,36,b'1234',True)
            thread = threading.Thread(target = self.a.start, name = "Serial thread")
            thread.start()
            print("start",thread.name)
            #self.check_thread(thread)
            MainWin.start = False
     
        else:
            self.a = test_serial.Serial_tread(self.com_comb.get(),self.com_baud.get(),100,36,b'1234',False)
            self.fgh_button.configure(text = "Start")
            MainWin.start = True
            print("Stop main programm")
    

                
def main():
    main_win = MainWin()
    main_win.mainloop()
  

def close_serial_thread():
    test_serial.Serial_tread.run = False
    

    
if __name__ == '__main__':
    main()
    close_serial_thread()
    
