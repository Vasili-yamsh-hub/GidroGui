from threading import Thread
import threading
import serial
import time
import gui_for_test_serial as gfs


class Serial_tread :

    def __init__(self,com,baud,t_out,buff_size,synch_templ,state):
        #Динамические атребуты класса
        self.com   = com
        self.baud  = baud
        self.t_out = t_out
        self.size  = buff_size
        self.synch = synch_templ
        self.data = bytearray(buff_size)
        self.state = state        
    def start(self):
        try:
            self.serial_connect = serial.Serial(self.com,self.baud,timeout = self.t_out)
            print('Connect to: ' + str(self.com) + ' at ' + str(self.baud) + ' BAUD.')
        except:
            print('Failed to Connect with: ' + str(self.com) + ' at ' + str(self.baud) + ' BAUD.')    
            
        while (self.state == True):
            self.serial_connect.reset_input_buffer()
            data = bytearray(self.serial_connect.readline(self.size))
            if data[0:4] in self.synch:
                #self.serial_connect.close()
                print(data)
                print(self.state)
            else:
                self.serial_connect.reset_input_buffer()
                data.clear()
                print("no sync")
            
        
        
    
        
        
            

    




