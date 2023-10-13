#!/usr/bin/env python3
# 
# mmc4wp.py - 2023 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
##

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.font import Font
from time import strftime, localtime,sleep
import sys
from configparser import ConfigParser
from os import path
import os
from pathlib import Path
import mpd
import threading

client = mpd.MPDClient()                    # create client object
version = "v0.0.2"
# v0.0.2 - renamed from mlmp.py to mmc4w.py
confparse = ConfigParser()
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
path_to_dat = path.abspath(path.dirname(__file__))
mmc4wIni = path_to_dat + "/mmc4w.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)
global serverip,serverport
serverip = confparse.get('serverstats', 'lastsrvr')
serverport = confparse.get('serverstats','lastport')
client.timeout = 10                     # network timeout in seconds (floats allowed), default: None
client.idletimeout = None               # timeout for fetching the result of the idle command is handled seperately, default: None
# client.connect(serverip, int(serverport))    # connect to localhost:6600

def initialize():
    global serverip,serverport
    try:
        client.connect(serverip, int(serverport))
    except:
        window.mainloop()
        SrvrWindow()


def connext():
    global serverip,serverport
    try:
        client.close()
        client.disconnect()
    except mpd.base.ConnectionError:
        pass
    client.connect(serverip, int(serverport))

def loadpl1():
    connext()
    client.load("Everything_Edited")
    client.play(100)
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def random():
    randobtn = "Random"
    connext()
    client.random(1)
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def halt():
    connext()
    client.stop()
    # getcurrstat()
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def play():
    connext()
    client.play()
    getcurrsong()
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def next():
    try:
        connext()
        client.next()
    except mpd.base.CommandError:
        connext()
        play()
    getcurrsong()
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def previous():
    connext()
    client.previous()
    getcurrsong()
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def pause():
    connext()
    client.pause()
    getcurrsong()
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def volup():
    connext()
    client.volume(+5)
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server
    
def voldn():
    connext()
    client.volume(-5)
    # client.close()                          # send the close command
    # client.disconnect()                     # disconnect from the server

def getcurrsong():
    global globsongtitle
    connext()
    cs = client.currentsong()
    try:
        msg = str(cs["title"] + " - " + cs["artist"])
        globsongtitle = msg
    except KeyError:
        msg = "No Current Song. Play one."
    confparse.set("serverstats","lastsongtitle",str(msg))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    displaytext1(msg)
    window.update()
    sleep(1)
    # getcurrstat()

def getcurrstat():
    connext()
    cstat = client.status()
    cpl = client.listplaylists()
    pl = ""
    for plv in cpl:
        pl = plv['playlist'] + "," + pl
    confparse.read(mmc4wIni)
    lastpl = confparse.get("serverstats","lastsetpl")
    confparse.set("serverstats","playlists",str(pl))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    # client.close()
    # client.disconnect()
    msg = str("Server: " + serverip[-3:] +" | " + cstat["state"] + " | PlayList: " + lastpl)
    # displaytext1(msg)
    return msg

def displaytext1(msg):
    text1.delete("1.0", 'end')
    text1.insert("1.0", msg)
#
## DINK MORE WITH THREADED SONG TITLE CAPTURE =================================================================
#

globsongtitle = ""
def songtitlelooptest():
    global globsongtitle
    globsongtitle = 0
    while True:
        sleep(10)
        globsongtitle += 1


def songtitleloop():
    global globsongtitle
    while True:
        confparse.read(mmc4wIni)
        lastst = confparse.get("serverstats","lastsongtitle")
        try:
            client.connect(serverip, int(serverport))
        except mpd.base.ConnectionError as cerr:
            if cerr == "Already connected":
                print("Already connected error.")
                pass
        try:
            cs = client.currentsong()
            stat = client.status()
        except ValueError:
            pass
        try:
            dur = stat['duration']
            elap = stat['elapsed']
            remaining = float(dur) - float(elap)
        except KeyError:
            remaining = 0
        try:
            thissongtitle = str(cs["title"] + " - " + cs["artist"])
        except KeyError:
            thissongtitle = "No Current Song. Play one."
        if thissongtitle != lastst:
            confparse.set("serverstats","lastsongtitle",str(thissongtitle))
            with open(mmc4wIni, 'w') as SLcnf:
                confparse.write(SLcnf)
            print("{}. Time remaining: {} secs.".format(thissongtitle,remaining))
        globsongtitle = thissongtitle
        client.close()
        client.disconnect()
        try:
            sleep(remaining + 1)
        except ValueError:
            pass

#
## WRAP UP AND DISPLAY ==========================================================================================
#

def endWithError(msg):
    messagebox.showinfo("UhOh",msg)
    pause()
    sys.exit()

def exit():
    halt()
    sys.exit()
#
## A CLASS TO CREATE ERROR MESSAGEBOXES (USED VERBATIM FROM STACKOVERFLOW)
## https://stackoverflow.com/questions/6666882/tkinter-python-catching-exceptions
#
class FaultTolerantTk(tk.Tk):
    def report_callback_exception(self, exc, val, tb):
        self.destroy_unmapped_children(self)
        messagebox.showerror('Error', val)

    # NOTE: It's an optional method. Add one if you have multiple windows to open
    def destroy_unmapped_children(self, parent):
        """
        Destroys unmapped windows (empty gray ones which got an error during initialization)
        recursively from bottom (root window) to top (last opened window).
        """
        children = parent.children.copy()
        for index, child in children.items():
            if not child.winfo_ismapped():
                parent.children.pop(index).destroy()
            else:
                self.destroy_unmapped_children(child)
#
##  END ERROR MESSAGEBOX SECTION
#
def tbtoggle():
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:
        window.overrideredirect(1)
    else:
        window.overrideredirect(0)



##
##  EVERYTHING SOUTH OF HERE IS THE 'window.mainloop' UNDEFINED BUT YET DEFINED QUASI-FUNCTION
############################################################################
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
############################################################################
# window = FaultTolerantTk()  # Create the root window.  Shows abbreviated error messages in popup.
window = Tk()  # Create the root window.  Shows errors in console.  THIS IS THE 'ROOT' WINDOW.
window.title("Mini MPD Player " + version)  # Set window title
winWd = 380  # Set window size and placement
winHt = 80
x_Left = int(window.winfo_screenwidth() - (winWd + 40))
# y_Top = int(window.winfo_screenheight() / 2 - (winHt / 2))
y_Top = int(window.winfo_screenheight() - (winHt + 400))
window.geometry(str(winWd) + "x" + str(winHt) + "+{}+{}".format(x_Left, y_Top))
window.config(background="white")  # Set window background color
window.columnconfigure([0,1,2,3,4], weight=0)
window.rowconfigure([0,1,2], weight=0)

def featureNotReady():
    messagebox.showinfo(title='Not Yet', message='That feature is not ready.')

nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font

#
## DEFINE THE SELECTIONS WINDOW
#
def SelWindow():
    global serverip
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    sw = Toplevel(window)
    sw.title("PlayLists")
    swinWd = 200
    swinHt = 30
    x_Left = int(window.winfo_screenwidth() / 2 - swinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - swinHt / 2)
    sw.config(background="white")  
    sw.geometry(str(swinWd) + "x" + str(swinHt) + "+{}+{}".format(x_Left, y_Top))
    def rtnplsel(plvar):
        global serverip
        if plvar == "" or plvar == None:
            plvar = "Unchanged"
            confparse.read(mmc4wIni)
            msg = confparse.get("serverstats","lastsetpl")
        else:
            msg = plvar
        print("plvar: {} msg: {}".format(plvar,msg))
        displaytext1(plvar)
        if plvar != "Unchanged":
            print("not unchanged: {}".format(plvar))
            connext()
            client.clear()
            client.load(plvar)
            confparse.read(mmc4wIni)
            confparse.set("serverstats","lastsetpl",plvar)
            with open(mmc4wIni, 'w') as SLcnf:
                confparse.write(SLcnf)
        sw.destroy()
        sleep(1)
        # getcurrstat()
    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    plvar =StringVar(sw)
    plvar.set('---== Select a Playlist ==---')
    plselwin = OptionMenu(sw,plvar,*pllist,command=rtnplsel)
    plselwin.grid(column=1,row=1)


def SrvrWindow():
    global serverip
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    srvrw = Toplevel(window)
    srvrw.title("Servers")
    srvrwinWd = 200
    srvrwinHt = 30
    x_Left = int(window.winfo_screenwidth() / 2 - srvrwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - srvrwinHt / 2)
    srvrw.config(background="gray")  
    srvrw.geometry(str(srvrwinWd) + "x" + str(srvrwinHt) + "+{}+{}".format(x_Left, y_Top))
    def rtnplsel(plvar):
        global serverip
        halt()
        msg = ipvar
        displaytext1(msg)
        serverip = str(ipvar.get())
        confparse.read(mmc4wIni)
        confparse.set("serverstats","lastsrvr",str(ipvar.get()))
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        srvrw.destroy()
        print("serverip: {}".format(serverip))
        SelWindow()
        # getcurrstat()
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverip')
    # print(pllist)
    ipvar = StringVar(srvrw)
    ipvar.set('---== Select a Server ==---')
    plselwin = OptionMenu(srvrw,ipvar,*iplist,command=rtnplsel)
    plselwin.grid(column=1,row=1)


#
## DEFINE THE ABOUT WINDOW
#
def aboutWindow():
    aw = Toplevel(window)
    aw.title("About NextNum")
    awinWd = 400  # Set window size and placement
    awinHt = 400
    x_Left = int(window.winfo_screenwidth() / 2 - awinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - awinHt / 2)
    aw.config(background="white")  # Set window background color
    aw.geometry(str(awinWd) + "x" + str(awinHt) + "+{}+{}".format(x_Left, y_Top))
    aw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    awlabel = Label(aw, font=18, text ="About NextNum " + version)
    awlabel.grid(column=0, columnspan=3, row=0, sticky="n")  # Place label in grid
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=1)
    aboutText = Text(aw, height=20, width=170, bd=3, padx=10, pady=10, wrap=WORD, font=nnFont)
    aboutText.grid(column=0, row=1)
    aboutText.insert(INSERT, "There is nothing to say.")
#
## DEFINE THE HELP WINDOW
#
def helpWindow():
    hw = Toplevel(window)
    hw.title("NextNum Help")
    hwinWd = 600  # Set window size and placement
    hwinHt = 600
    x_Left = int(window.winfo_screenwidth() / 2 - hwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - hwinHt / 2)
    hw.config(background="white")  # Set window background color
    hw.geometry(str(hwinWd) + "x" + str(hwinHt) + "+{}+{}".format(x_Left, y_Top))
    hw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    # hw.iconbitmap('./ico/mmc4w-ico.ico')

    hwlabel = Label(hw, height=8, font=18, text ="NextNum Help")
    hw.columnconfigure(0, weight=1)
    hw.rowconfigure(0, weight=1)
    hw.rowconfigure(1, weight=1)

    helpText = Text(hw, height=40, width=80, bd=3, padx=6, pady=6, wrap=WORD, font=nnFont)
    helpsb = ttk.Scrollbar(hw, orient='vertical', command=helpText.yview)

    helpText['yscrollcommand'] = helpsb.set
    hwlabel.grid(column=0, columnspan=3, row=0, padx=10, pady=10)  # Place label in grid
    helpText.grid(column=0, row=1)
    helpsb.grid(column=1, row=1, sticky='ns')

    with open("mmc4w_help.txt", "r") as f:
        hlptxt = f.read()
    helpText.insert(INSERT, hlptxt)
#
## MENU AND MENU ITEMS
#
Frame(window)
menu = Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
fileMenu = Menu(menu, tearoff=False)
# fileMenu.add_command(label="Configure", command=lambda:configWindow())
fileMenu.add_command(label="Select Server", command=SrvrWindow)
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

lessMenu = Menu(menu, tearoff=False)
lessMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
lessMenu.add_command(label="Current Title", command=getcurrsong)
lessMenu.add_command(label="Status", command=getcurrstat)
menu.add_cascade(label="Look", menu=lessMenu)

helpMenu = Menu(menu, tearoff=False)
helpMenu.add_command(label="Help", command=helpWindow)
helpMenu.add_command(label="About", command=aboutWindow)
menu.add_cascade(label="Help", menu=helpMenu)


# window.iconbitmap('./ico/mmc4w-ico.ico')
window.iconbitmap('./_internal/ico/mmc4w-ico.ico')

## Set up text windows
# text_area = scrolledtext.ScrolledText()      ## scrolledtext is a text window with a scrollbar already there.
#
text1 = Text(window, height=1, width=52, wrap=WORD, font=nnFont)
# text2 = Text(window, height=4, width=56, wrap=WORD, font=nnFont)

text1.grid(column=0, columnspan=5, row=0)
# text2.grid(column=0, columnspan=7, row=2)

button_volup = ttk.Button(window, text="Vol +", command=volup)                  # 
button_volup.grid(column=0, row=1)                     # Place Exit button in grid

button_voldn = ttk.Button(window, text="Vol -", command=voldn)                  # 
button_voldn.grid(column=1, row=1)                     # Place Exit button in grid

button_play = ttk.Button(window, text="Play", command=play)                  # 
button_play.grid(column=0, row=2)                     # Place Exit button in grid

button_stop = ttk.Button(window, text="Stop", command=halt)                  # 
button_stop.grid(column=1, row=2)                     # Place Exit button in grid

button_prev = ttk.Button(window, text="Prev", command=previous)                  # 
button_prev.grid(column=2, row=2)                     # Place Exit button in grid

button_pause = ttk.Button(window, text="Pause", command=pause)                  # 
button_pause.grid(column=3, row=2)                     # Place Exit button in grid

button_next = ttk.Button(window, text="Next", command=next)                  # 
button_next.grid(column=4, row=2)                     # Place Exit button in grid

button_tbtog = ttk.Button(window, text="Mode", command=tbtoggle)                  # 
button_tbtog.grid(column=2, row=1)                     # Place Exit button in grid

button_load = ttk.Button(window, text="CurrTitle", command=getcurrsong)                  #
button_load.grid(column=3, row=1)                     # Place Exit button in grid

button_exit = ttk.Button(window, text="Quit", command=exit)                  #
button_exit.grid(column=4, row=1)                     # Place Exit button in grid

# Instead of directly specifying a main() function, we let the window.mainloop() wait for a button press
# from one of the buttons we defined.  The function associated with the button defines what happens next.
#
# main()
# getcurrsong()
initialize()
# getcurrstat()
connext()
# client.connect(serverip, int(serverport))
cs = client.currentsong()
# client.close()
# client.disconnect()
# msg = str(cs["title"] + " - " + cs["artist"])
# displaytext1(msg)
## THREADING NOTES BELOW HERE ==============================
# while threading.active_count() > 0:
# Make all threads daemon threads, and whenever the main thread dies all threads will die with it.
t1 = threading.Thread(target=songtitleloop)
t1.daemon = True
t1.start()
## END THREADING NOTES =====================================
evenodd = 1
def tensecdisplaytext():
    global evenodd, globsongtitle
    def eo1():
        global evenodd, globsongtitle
        if evenodd == 1:
            # print("evenodd: " + str(evenodd))
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd
        if evenodd == 2:
            # print("evenodd: " + str(evenodd))
            msg = getcurrstat()
            evenodd = 1
            displaytext1(msg)
    window.after(1000,eo1)
    window.after(2500,eo2)
    window.after(3000,tensecdisplaytext)
tensecdisplaytext()
window.mainloop()  # Run the (not defined with 'def') main window loop.

