from Tkinter import *
import serial
import time
from __main__ import *

###vars to send
stepLocation = 0
gStepLocation = 0

inProgress = 'yes'

PCbcode = ('/Users/bobmain/Desktop/Google Drive/Cthulhu/bcode.txt' if comp == 'm' else
       'C:/Users/Robert/Google Drive/Cthulhu/bcode.txt')
SDbcode = ('D:/PATH.TXT')

port = serial.Serial('COM4', 38400)
loopcontrol = 'open'
time.sleep(2)
        
def main(order):
    if order == 'path':
        print "\n\nPATH ORDER COPYING to SD CARD..."
        openPCfile = open(PCbcode)
        openSDfile = open(SDbcode,'w')
        entireFileContents = openPCfile.read()
        openSDfile.write(entireFileContents)
        openSDfile.close()
        openPCfile.close()   
        print "\nPATH SAVED TO SD card...\nMOVE SD to TANYA\n"
       

####we need to re-establish the connection.???
#### for some reason, it fucks with the loop if you re-establish here.
            ###test not calling port before main loop and then individually in each call.   
    
    if order[0] == 'Q':
        print"\n\nSingle Move Order Sending..."
        while (port.inWaiting()>0):
            ArdData = port.readline()
            if ArdData[0] == 'g':
                port.write(order)
                        
        print "\nMOVE SENT TO ARDUINO"
        ArdData = port.readline()
        print ArdData
        ArdData = port.readline()
        print ArdData
        
        
    return order
if __name__ == "__main__":
    x = main(order)
