# -*- coding: utf-8 -*-

'''
IviGui

GUI to display measurements done over USBTMC

Jaanus Kalde, 2018
'''

import usbtmc
from Tkinter import Tk, Label, Entry


class IviGui:
    def __init__(self, master):
        self.master = master
        master.title("U2001A power measurement")

        # Label and Entry for inputting relative/attenuator value
        self.atten = Label(master, text="Relative (dB):")
        self.atten.grid(row=1,column=1)
        self.entry = Entry(master)
        self.entry.insert(0,'0')
        self.entry.grid(row=1,column=2)

        # Main display label. Shows relative measurement with dot during updates
        self.label = Label(master, text=" \n-NaN dBm", font=("Arial",32), height=3, width=20)
        self.label.grid(row=2,column=1,columnspan=2)
        # Smaller secondary display to show real measurement by device
        self.label2 = Label(master, text=" \n-NaN dBm", font=("Arial",16))
        self.label2.grid(row=3,column=1,columnspan=2)

        print usbtmc.list_resources()     # List USBTMC resources to connect to.
        self.instr = usbtmc.Instrument('USB::10893::11032::INSTR')      # Your device to connect to. Pick from the list.
        self.instr.timeout = 60*1000      # Some devices are slow, some configurations are slow, timeout in ms.
        print self.instr.ask("*IDN?")     # Print out what device itself thinks its name is for validation.

        # Keysight U2001A trigger setup - free running trigger
        self.instr.write("INIT[1]:CONT 1")
        self.instr.write("TRIG[1]:SOUR IMM")

        # Init the variables
        self.measurement = -100
        self.original_background = self.entry.cget("background")

        # Start first measurement
        self.update()

    # This method polls the device and updates display. Polling can take long time.
    def update(self):
        self.measurement = self.instr.ask("MEAS?")
        #print "%.2f" % float(self.measurement)      # Debug printout to check the connection.

        self.update_number(True)
        self.label.after(100, self.remove_dot)

    # 100 ms after getting a measurement from the device, remove the dot above the measurement.
    # This provided clear indication to user about when the data was updated.
    def remove_dot(self):
        self.update_number(False)
        self.label.after(100, self.update)

    # Deal with getting the relative number from the Entry and updating all the displays.
    def update_number(self, dot = False):
        try:
            relative_value = float(self.entry.get())
            self.entry.config(background=self.original_background)

            if dot:
                self.label.config(text=".\n%.2f dBm" % (float(self.measurement)-relative_value))
            else:
                self.label.config(text=" \n%.2f dBm" % (float(self.measurement)-relative_value))

        # If the relative box shows gibberish, just display the measurement.
        except ValueError:
            self.entry.config(background="#A44")

            if dot:
                self.label.config(text=".\n%.2f dBm" % float(self.measurement))
            else:
                self.label.config(text=" \n%.2f dBm" % float(self.measurement))

        self.label2.config(text="%.2f dBm" % float(self.measurement))


root = Tk()
my_gui = IviGui(root)
root.mainloop()