#!/usr/bin/env python3
# 
# mmc4w.py - 2023-2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
# mmc4w.py uses the python-mpd2 library.
##

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.font import Font
from time import sleep
import sys
from configparser import ConfigParser
from os import path
import os
from tkhtmlview import HTMLScrolledText, RenderHTML, HTMLLabel
import mpd
# import threading
import threading
from PIL import ImageTk, Image
from io import BytesIO
import time
import logging

client = mpd.MPDClient()                    # create client object
version = "v0.0.4"
# v0.0.4 - a boatload of changes, including albumart display option, config editing, error catching.
# v0.0.2 - renamed from mlmp.py to mmc4w.py
# confparse is for general use for normal text strings.
confparse = ConfigParser()
# cp is for use where lists are involved.
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
path_to_dat = path.abspath(path.dirname(__file__))
mmc4wIni = path_to_dat + "/mmc4w.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)
if confparse.get('basic','installation') == "":
    confparse.set('basic','installation',path_to_dat)
    # logger.warning("Writing installation path to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
#
logLevel = confparse.get('program','logging')

if logLevel == 'warning':
    if os.path.isfile(path_to_dat + "./mmc4w.log"):
        os.remove(path_to_dat + './mmc4w.log')
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.WARNING,
    )

if logLevel != 'warning':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.CRITICAL,
    )

logger = logging.getLogger(__name__)
global serverip,serverport,noloop
endtime = time.time()

def connext():
    global serverip,serverport
    cxstat = 0
    if serverip != "" and serverport != "":
        try:
            client.close()
            client.disconnect()
        except (ValueError, mpd.base.ConnectionError):
            pass
        client.connect(serverip, int(serverport))
        cxstat = 1
    else:
        cxstat = 0
    return cxstat

def plrandom():
    cxstat = connext()
    if cxstat == 1:
        client.random(1)

def plnotrandom():
    cxstat = connext()
    if cxstat == 1:
        client.random(0)

def halt():
    global endtime
    endtime = time.time()
    cxstat = connext()
    if cxstat == 1:
        client.stop()
    endtime = time.time()

def play():
    cxstat = connext()
    if cxstat == 1:
        client.play()
    getcurrsong()

def next():
    try:
        cxstat = connext()
        if cxstat == 1:
            client.next()
            getcurrsong()
    except mpd.base.CommandError:
        cxstat = connext()
        if cxstat == 1:
            play()

def previous():
    cxstat = connext()
    if cxstat == 1:
        client.previous()
    getcurrsong()

def pause():
    cxstat = connext()
    if cxstat == 1:
        client.pause()
    getcurrstat()

def volup():
    cxstat = connext()
    if cxstat == 1:
        client.volume(+5)
    
def voldn():
    cxstat = connext()
    if cxstat == 1:
        client.volume(-5)


def getcurrsong():
    global globsongtitle,endtime,aatgl,sent,pstate
    if threading.active_count() < 2:
        exit()
    def getaartpic():
        global aatgl
        cs = {'file': '', 'last-modified': '2023-12-18T23:22:24Z', 'format': '44100:16:2', 'title': "Title Not Available", 'disc': '1', 'artist': 'Oops', 'album': 'Unknown', 'genre': 'Error', 'date': '2024', 'track': '1', 'time': '200', 'duration': '200.000', 'pos': '0000', 'id': '00000'}
        aadict = {}
        try:
            gaperr = 0
            cs = client.currentsong()
            sleep(0.25)
            aadict = client.readpicture(cs['file'])
            if 'binary' in aadict:
                aartvar = 1
                try:
                    artw.title()
                    artw.destroy()
                except (AttributeError,NameError,TclError):
                    pass
            else:
                aartvar = 0
            if aatgl == '1':
                artWindow(aartvar,**aadict)
                logger.warning(" - - - - - - - - - - - ")
                logger.warning("1) Top of getcurrsong(). artw updated with AlbumArt.")
        except mpd.base.ConnectionError:
            gaperr = 1
            cs = []
            logger.warning("1) Got a ConnectionError in getaartpic().")
        except ValueError:
            gaperr = 1
            cs = []
            logger.warning("1) Got a ValueError in getaartpic().")
            pass
        return gaperr,cs
    def getendtime():
        stat = {'volume': '', 'repeat': '', 'random': '', 'single': '', 'consume': '', 'partition': '', 'playlist': '', 'playlistlength': '', 'mixrampdb': '', 'state': '', 'song': '', 'songid': '', 'nextsong': '', 'nextsongid': ''}
        try:
            geterr = 0
            msg = ""
            stat = client.status()
            gpstate = stat['state']
            dur = cs['duration']
            elap = stat['elapsed']
            remaining = float(dur) - float(elap)
            gendtime = time.time() + remaining
            logger.warning("2) endtime generated: {}.".format(gendtime))
            msg = str(cs["title"] + " - " + cs["artist"])
        except mpd.base.ConnectionError:
            geterr = 1
            logger.warning("2) Got a ConnectionError in getendtime().")
            gendtime = time.time()
        except KeyError:
            geterr = 1
            logger.warning("2) Got a KeyError in getendtime().")
            gendtime = time.time()
            pass
        return geterr,msg,gendtime,gpstate
    cxstat = connext()
    gsent = sent
    if cxstat == 1:
        try:
            gaperr,cs = getaartpic()
            if gaperr == 1:
                gaperr,cs = getaartpic()
            geterr,msg,gendtime,gpstate = getendtime()
            if geterr == 1:
                geterr,msg,gendtime,gpstate = getendtime()
            logger.warning("3) {}.".format(msg))
            globsongtitle = msg
            if msg != confparse.get('serverstats','lastsongtitle'):
                gsent = 0
                logger.warning("4) This is a new title.")
                confparse.set("serverstats","lastsongtitle",str(msg))
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
            else:
                logger.warning("4) This is NOT a new title. - - - Rolling back gendtime and gsent.")
                gendtime = endtime
                gsent = 0
                logger.warning("5) gendtime returned to {}. Duration is {}.".format(gendtime,cs['duration']))
                if float(cs['duration']) == 0.00:
                    next()
        except KeyError:
            msg = "No Current Song. Play one."
            displaytext1(msg)
        if geterr == 0 and gaperr == 0:
            endtime = gendtime
            pstate = gpstate
            sent = gsent
    if pstate == 'stop' or pstate == 'pause':
        logger.warning("6) pstate: {}.".format(pstate))

    if cxstat == 0:
        msg = "Not Connected."
        displaytext1(msg)

def songtitlefollower():
    logger.warning("Start songtitlefollower.")
    global endtime,sent,pstate
    sent = 0
    pstate = 'stop'
    thisendtime = endtime
    while True:
        if threading.active_count() > 2:
            logger.warning("There are {} threads now.".format(threading.active_count()))
        sleep(.2)
        if pstate != 'stop' and pstate != 'pause':
            if endtime != thisendtime:
                logger.warning("5) Threaded timer got new endtime.")
                thisendtime = endtime
                logger.warning("6) endtime: {}, now: {} sent: {}.".format(thisendtime,time.time(),sent))
            if thisendtime <= time.time() and sent == 0:
                logger.warning("0) Threaded timer ran down. Getting new current song data.")
                sent = 1
                getcurrsong()

def configurator():
        halt()
        proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
        if proceed == True:
            os.startfile(mmc4wIni)
            sleep(1)
            exit()

def getcurrstat():
    cxstat = connext()
    if cxstat == 1:
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
        msg = str("Server: " + serverip[-3:] +" | " + cstat["state"] + " | PlayList: " + lastpl)
    if cxstat == 0:
        msg = "Not Connected"
    return msg

def displaytext1(msg):
    text1.delete("1.0", 'end')
    text1.insert("1.0", msg)

def albarttoggle():
    global aatgl,artw
    confparse.read(mmc4wIni)
    aatgl = confparse.get("albumart","albarttoggle")
    if aatgl == '1':
        try:
            # logger.warning("Destroy AArt window.")
            artw.title()
            artw.destroy()
            aatgl = '0'
        except (AttributeError,NameError):
            pass
    else:
        # logger.warning("Set aatgl to '1'.")
        aatgl = '1'
        try:
            cs = client.currentsong()
            aadict = client.readpicture(cs['file'])
            if 'binary' in aadict:
                aartvar = 1
            else:
                aartvar = 0
            artWindow(aartvar,**aadict)
        except (ValueError,KeyError):
            pass
    confparse.set("albumart","albarttoggle",aatgl)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def tbtoggle():
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:
        window.overrideredirect(1)
        confparse.set("mainwindow","titlebarstatus",'0')  # Titlebar off (overridden)
    else:
        window.overrideredirect(0)
        confparse.set("mainwindow","titlebarstatus",'1')  # Titlebar on (not overridden)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    getcurrsong()

def nonstdport():
    # logger.warning("Setting non-standard port.")
    messagebox.showinfo("Setting a non-standard port","Set your non-standard port by editing the mmc4w.ini file. Use the Configure option in the File menu.\n\nPut your port number in the 'serverport' attribute under the [basic] section. 6600 is the default MPD port.")

def endWithError(msg):
    messagebox.showinfo("UhOh",msg)
    pause()
    sys.exit()

def exit():
    halt()
    sys.exit()

serverlist = confparse.get('basic','serverlist')
serverip = confparse.get('serverstats', 'lastsrvr')
if serverlist == "":
    configurator()
    serverport = confparse.get('basic','serverport')
if confparse.get('serverstats','lastport') != "":
    serverport = confparse.get('serverstats','lastport')
else:
    confparse.set('serverstats','lastport',serverport)
    # logger.warning("Writing port to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
if version != confparse.get('program','version'):
    confparse.set('program','version',version)
    # logger.warning("Writing version to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
client.timeout = None                     # network timeout in seconds (floats allowed), default: None
client.idletimeout = None               # timeout for fetching the result of the idle command is handled seperately, default: None
# client.connect(serverip, int(serverport))    # connect to localhost:6600
artw = None


globsongtitle = ""
aatgl = '0'


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
#
## WRAP UP AND DISPLAY ==========================================================================================
#
##
##  EVERYTHING SOUTH OF HERE IS THE 'window.mainloop' UNDEFINED BUT YET DEFINED QUASI-FUNCTION
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
# window = Tk()  # Create the root window with errors in console.  THIS IS THE 'ROOT' WINDOW.
window.title("Minimal MPD Client " + version)  # Set window title
winWd = 380  # Set window size
winHt = 80
confparse.read(mmc4wIni)  # get parameters from config .ini file.
win_x = int(confparse.get("mainwindow","win_x"))
win_y = int(confparse.get("mainwindow","win_y"))
tbarini = confparse.get("mainwindow","titlebarstatus")
x_Left = int(window.winfo_screenwidth() - (winWd + win_x))
y_Top = int(window.winfo_screenheight() - (winHt + win_y))
window.geometry(str(winWd) + "x" + str(winHt) + "+{}+{}".format(x_Left, y_Top))
window.config(background="white")  # Set window background color
window.columnconfigure([0,1,2,3,4], weight=0)
window.rowconfigure([0,1,2], weight=0)
if tbarini == '0':
    window.overrideredirect(1)

def featureNotReady():
    messagebox.showinfo(title='Not Yet', message='That feature is not ready.')



nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font

#
## DEFINE THE SERVER SELECTION WINDOW
#
def SrvrWindow():
    global serverip
    text1['bg']='orange'
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    srvrw = Toplevel(window)
    srvrw.title("Servers")
    srvrwinWd = 300
    srvrwinHt = 30
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    win_x = int(confparse.get("mainwindow","win_x"))
    win_y = int(confparse.get("mainwindow","win_y"))
    x_Left = int(window.winfo_screenwidth() - srvrwinWd - (win_x+60))
    y_Top = int(window.winfo_screenheight() - srvrwinHt - (win_y+120))
    srvrw.config(background="gray")  
    srvrw.geometry(str(srvrwinWd) + "x" + str(srvrwinHt) + "+{}+{}".format(x_Left, y_Top))
    srvrw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    def rtnplsel(ipvar):
        global serverip
        # halt()
        msg = ipvar
        displaytext1(msg)
        # serverip = str(ipvar.get())
        serverip = ipvar
        confparse.read(mmc4wIni)
        confparse.set("serverstats","lastsrvr",ipvar)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        srvrw.destroy()
        # logger.warning("serverip: {}".format(serverip))
        getcurrstat()
        PLSelWindow()
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverlist')
    # logger.warning(pllist)
    ipvar = StringVar(srvrw)
    ipvar.set('Currently - ' + serverip + ' - Click for dropdown list.')
    plselwin = OptionMenu(srvrw,ipvar,*iplist,command=rtnplsel)
    plselwin.config(width=44)
    plselwin.grid(column=1,row=1)
#
## DEFINE THE PLAYLIST SELECTION WINDOW
#
def PLSelWindow():
    global serverip
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    sw = Toplevel(window)
    sw.title("PlayLists")
    swinWd = 300
    swinHt = 30
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    win_x = int(confparse.get("mainwindow","win_x"))
    win_y = int(confparse.get("mainwindow","win_y"))
    x_Left = int(window.winfo_screenwidth() - swinWd - (win_x+60))
    y_Top = int(window.winfo_screenheight() - swinHt - (win_y+120))
    sw.config(background="white")  
    sw.geometry(str(swinWd) + "x" + str(swinHt) + "+{}+{}".format(x_Left, y_Top))
    sw.iconbitmap('./_internal/ico/mmc4w-ico.ico')
    def rtnplsel(plvar):
        global serverip
        if plvar == "" or plvar == None:
            plvar = "Unchanged"
            confparse.read(mmc4wIni)
            msg = confparse.get("serverstats","lastsetpl")
        else:
            msg = plvar
        # logger.warning("plvar: {} msg: {}".format(plvar,msg))
        displaytext1(plvar)
        if plvar != "Unchanged":
            # logger.warning("not unchanged: {}".format(plvar))
            cxstat = connext()
            if cxstat == 1:
                client.clear()
                client.load(plvar)
                confparse.read(mmc4wIni)
                confparse.set("serverstats","lastsetpl",plvar)
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
        sw.destroy()
        sleep(1)
        text1['bg']='white'
        # getcurrstat()
    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    lastpl = confparse.get("serverstats","lastsetpl")
    plvar =StringVar(sw)
    plvar.set('Current Playlist - ' + lastpl + ' - Click for list.')
    plselwin = OptionMenu(sw,plvar,*pllist,command=rtnplsel)
    plselwin.config(width=44)
    plselwin.grid(column=1,row=1)
    window.update()
    window.update_idletasks()

#
## DEFINE THE ABOUT WINDOW
#
def aboutWindow():
    aw = Toplevel(window)
    aw.title("About MMC4W")
    awinWd = 400  # Set window size and albumart
    awinHt = 400
    x_Left = int(window.winfo_screenwidth() / 2 - awinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - awinHt / 2)
    aw.config(background="white")  # Set window background color
    aw.geometry(str(awinWd) + "x" + str(awinHt) + "+{}+{}".format(x_Left, y_Top))
    aw.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
    awlabel = Label(aw, font=18, text ="About MMC4W " + version)
    awlabel.grid(column=0, columnspan=3, row=0, sticky="n")  # Place label in grid
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=1)
    aboutText = Text(aw, height=20, width=170, bd=3, padx=10, pady=10, wrap=WORD, font=nnFont)
    aboutText.grid(column=0, row=1)
    aboutText.insert(INSERT, "MMC4W is installed at\n" + path_to_dat + "\n\nMusic without the bloat.\n\nMMC4W is a Windows client for MPD.  It does nothing by itself, but if you have one or more MPD servers on your network, you might like this.\n\n"
                     "This little app holds forth the smallest set of functions I could think of to just play the music without being frustrating.\n\nCopyright 2023-2023 Gregory A. Sanders\nhttps://www.drgerg.com")
#
## DEFINE THE HELP WINDOW
#
def helpWindow():
    hw = Toplevel(window)
    hw.tk.call('tk', 'scaling', 1.0)    # This prevents the text being huge on hiDPI displays.
    hw.title("MMC4W Help")
    hwinWd = 800  # Set window size and placement
    hwinHt = 600
    x_Left = int(window.winfo_screenwidth() / 2 - hwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - hwinHt / 2)
    hw.config(background="white")  # Set window background color
    hw.geometry(str(hwinWd) + "x" + str(hwinHt) + "+{}+{}".format(x_Left, y_Top))
    hw.iconbitmap(path_to_dat + '/ico/mmc4w-ico.ico')
    hwlabel = HTMLLabel(hw, height=3, html='<h2 style="text-align: center">MMC4W Help</h2>')
    hw.columnconfigure(0, weight=1)
    helpText = HTMLScrolledText(hw, height=44, padx=10, pady=10, html=RenderHTML(path_to_dat + "\\mmc4w_help.html"))
    hwlabel.grid(column=0, row=0, sticky="NSEW")  # Place label in grid
    helpText.grid(column=0, row=1, ipadx=10, ipady=10, sticky="NSEW")

#
## DEFINE THE ART WINDOW
#
def artWindow(aartvar,**aadict):
    global artw
    if aartvar == 1:
        thisimage = BytesIO(aadict['binary'])
    if aartvar == 0:
        thisimage = path_to_dat + '/ico/mmc4w.png'
    artw = Toplevel(window)
    artw.title("AlbumArt")
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    aartwin_x = int(confparse.get("albumart","aartwin_x"))
    aartwin_y = int(confparse.get("albumart","aartwin_y"))
    artwinWd = 110  # Set window size
    artwinHt = 110
    x_Left = int(window.winfo_screenwidth() - aartwin_x)
    y_Top = int(window.winfo_screenheight() - aartwin_y)
    artw.config(background="white")  # Set window background color
    artw.geometry(str(artwinWd) + "x" + str(artwinHt) + "+{}+{}".format(x_Left, y_Top))
    artw.columnconfigure([0,1,2], weight=1)
    artw.rowconfigure(0, weight=1)
    artw.rowconfigure(1, weight=1)
    aart = Image.open(thisimage)
    aart = aart.resize((100,100))
    aart = ImageTk.PhotoImage(aart)
    aart.image = aart  # required for some reason
    aartLabel = Label(artw,image=aart)
    aartLabel.grid(column=0, row=0, padx=5, pady=5)
    artw.overrideredirect(1) ## turn off the titlebar

#
## MENU AND MENU ITEMS
#
Frame(window)
menu = Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
fileMenu = Menu(menu, tearoff=False)
fileMenu.add_command(label="Configure", command=configurator)
fileMenu.add_command(label="Select Server", command=SrvrWindow)
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

lessMenu = Menu(menu, tearoff=False)
lessMenu.add_command(label="Turn Random On", command=plrandom)
lessMenu.add_command(label="Turn Random Off", command=plnotrandom)
lessMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
lessMenu.add_command(label="Reload Current Title", command=getcurrsong)
lessMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
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
button_volup.grid(column=0, row=1)                     # Place button in grid

button_voldn = ttk.Button(window, text="Vol -", command=voldn)                  # 
button_voldn.grid(column=1, row=1)                     # Place button in grid

button_play = ttk.Button(window, text="Play", command=play)                  # 
button_play.grid(column=0, row=2)                     # Place button in grid

button_stop = ttk.Button(window, text="Stop", command=halt)                  # 
button_stop.grid(column=1, row=2)                     # Place button in grid

button_prev = ttk.Button(window, text="Prev", command=previous)                  # 
button_prev.grid(column=2, row=2)                     # Place button in grid

button_pause = ttk.Button(window, text="Pause", command=pause)                  # 
button_pause.grid(column=3, row=2)                     # Place button in grid

button_next = ttk.Button(window, text="Next", command=next)                  # 
button_next.grid(column=4, row=2)                     # Place button in grid

button_tbtog = ttk.Button(window, text="Mode", command=tbtoggle)                  # 
button_tbtog.grid(column=2, row=1)                     # Place button in grid

button_load = ttk.Button(window, text="Art", command=albarttoggle)                  #
button_load.grid(column=3, row=1)                     # Place button in grid

button_exit = ttk.Button(window, text="Quit", command=exit)                  #
button_exit.grid(column=4, row=1)                     # Place button in grid

## THREADING NOTES =========================================
# while threading.active_count() > 0:
# Make all threads daemon threads, and whenever the main thread dies all threads will die with it.
## END THREADING NOTES =====================================
#

t1 = threading.Thread(target=songtitlefollower)
t1.daemon = True
t1.start()
#
confparse.read(mmc4wIni)
aatgl = confparse.get("albumart","albarttoggle")
evenodd = 1

def threesecdisplaytext():
    global evenodd, globsongtitle
    def eo1():
        global evenodd, globsongtitle
        # logger.warning("evenodd: " + str(evenodd))
        if evenodd == 1:
            # logger.warning("evenodd: " + str(evenodd))
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd
        # logger.warning("evenodd: " + str(evenodd))
        if evenodd == 2:
            # logger.warning("evenodd: " + str(evenodd))
            msg = getcurrstat()
            evenodd = 1
            displaytext1(msg)
    window.after(1000,eo1)
    window.after(2500,eo2)
    window.after(3000,threesecdisplaytext)
#
## Start 
threesecdisplaytext()
getcurrsong()
logger.warning("Down at the bottom.")
window.mainloop()  # Run the (not defined with 'def') main window loop.

## Some random things I want to keep around:
#
    # aart = Image.open(BytesIO(aadict['binary']))
    # aart = aart.resize((100,100))
    # aart = ImageTk.PhotoImage(aart)
    # aart = Image.open('./ico/mmc4w.png')
    # aart_byte_array = BytesIO()
    # aart.save('./ico/mmc4w.png', format='PNG')
    # aart_byte_array = BytesIO()
    # aart.save(aart_byte_array, format='PNG')
    # aart_byte_array = aart_byte_array.getvalue()