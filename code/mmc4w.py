#!/usr/bin/env python3
# 
# mmc4w.py - 2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
# mmc4w.py uses the python-mpd2 library.
##

from tkinter import *
import tkinter as tk
# from tkinter import ttk
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


version = "v0.0.6"
# v0.0.7 - Added search and play a single title
# v0.0.5 - improve reliability
# v0.0.4 - a boatload of changes, including albumart display option, config editing, error catching.

client = mpd.MPDClient()                    # create client object

# confparse is for general use for normal text strings.
confparse = ConfigParser()
# cp is for use where lists are involved.
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})

path_to_dat = path.abspath(path.dirname(__file__))
mmc4wIni = path_to_dat + "/mmc4w.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)
lastpl = confparse.get("serverstats","lastsetpl")
if confparse.get('basic','installation') == "":
    confparse.set('basic','installation',path_to_dat)
    # logger.info("Writing installation path to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
#
logLevel = confparse.get('program','loglevel').upper()
logtoggle = confparse.get('program','logging').upper()
if logtoggle == 'OFF':
    logLevel = 'WARNING'

if logLevel.upper() == "INFO":
    if os.path.isfile(path_to_dat + "./mmc4w.log"):
        os.remove(path_to_dat + './mmc4w.log')

if logLevel == 'DEBUG':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w_DEBUG.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.DEBUG,
    )

if logLevel == 'INFO':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.INFO,
    )

if logLevel == 'WARNING':
    logging.basicConfig(
        filename=path_to_dat + "./mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.WARNING,
    )

logger = logging.getLogger(__name__)
mpd_logger = logging.getLogger('mpd')
mpd_logger.setLevel(logging.CRITICAL)

global serverip,serverport
endtime = time.time()
cxstat = 0
buttonvar = 'stop'
pstart = 0
dur='0'
pause_duration = 0.0
sent = 0

serverlist = confparse.get('basic','serverlist')
serverip = confparse.get('serverstats', 'lastsrvr')
serverport = confparse.get('basic','serverport')
if serverlist == "":
    proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
    if proceed == True:
        os.startfile(mmc4wIni)
        sys.exit()
if confparse.get('serverstats','lastport') != "":
    serverport = confparse.get('serverstats','lastport')
else:
    confparse.set('serverstats','lastport',serverport)
    # logger.info("Writing port to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
if version != confparse.get('program','version'):
    confparse.set('program','version',version)
    # logger.info("Writing version to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)


def connext():
    global serverip,serverport
    try:
        client.ping()  # Use ping() to see if we're connected.
        cxstat = 1
    except  (mpd.base.ConnectionError,ConnectionRefusedError) as errvar:
        logger.debug("errvar: {}".format(errvar))
        cxstat = 0
        try:
            logger.debug("Try to connect to {} on port {}".format(serverip,serverport))
            client.connect(serverip, int(serverport))
            cxstat = 1
        except  (ValueError, mpd.base.ConnectionError,ConnectionRefusedError) as errvar:
            logger.debug("Second level errvar: {}".format(errvar))
            cxstat = 0
            pass
    # print("cxstat is: {}".format(cxstat))
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
    global endtime,buttonvar
    buttonvar = 'stop'
    endtime = time.time()
    cxstat = connext()
    if cxstat == 1:
        client.stop()
    endtime = time.time()
    return buttonvar

def play():
    global buttonvar,prevbtnstate
    prevbtnstate = buttonvar
    buttonvar = 'play'
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
    global buttonvar,endtime,pstart,pause_duration,eptime,pstate
    logger.debug('Play state at button press: {}.'.format(buttonvar))
    if buttonvar == 'pause':        ## SYSTEM WAS PAUSED
        logger.debug("pause() pstart: {}".format(pstart))
        pause_duration = time.time() - pstart
        logger.debug("time.time(): {}, pstart: {}.".format(time.time(),pstart))
        logger.info(f"0) Playback resumed at {time.time()}. Pause duration: {pause_duration:.2f}")
        oldendtime = endtime
        endtime = endtime + pause_duration
        logger.info('2) New endtime generated in pause(). Old: {}, New {}'.format(oldendtime,endtime))
        button_pause.configure(bg='SystemButtonFace') ## 'systemButtonFace' is the magic word.
        pstate = 'play'
        pstart = 0 
        # Now client.pause() sets it to PLAY
    if buttonvar == 'play':         ## SYSTEM WAS PLAYING
        pstart = time.time()
        buttonvar = 'pause'
        button_pause.configure(bg="orange")
        logger.info("0) Playback paused at {}.".format(pstart))
        pstate = 'pause'
        ## Now client.pause() sets it to PAUSE
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
    global globsongtitle,endtime,aatgl,sent,pstate,elap,firstrun,prevbtnstate
    if threading.active_count() < 2:
        exit()
    #
    logger.debug("Sent: {}".format(sent))
    #
    ## Sub-function definitions
    #
    def getaartpic(**cs):
        global aatgl
        # cs = {'file': '', 'last-modified': '2023-12-18T23:22:24Z', 'format': '44100:16:2', 'title': "Title Not Available", 'disc': '1', 'artist': 'Oops', 'album': 'Unknown', 'genre': 'Error', 'date': '2024', 'track': '1', 'time': '200', 'duration': '200.000', 'pos': '0000', 'id': '00000'}
        aadict = {}
        try:
            gaperr = 0
            # cs = client.currentsong()
            # sleep(0.25)
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
                logger.info(" - - - - - - - - - - - ")
                logger.info("1) Top of getcurrsong(). artw updated with AlbumArt.")
        except mpd.base.ConnectionError:
            gaperr = 1
            cs = []
            logger.warning("1) Got a ConnectionError in getaartpic().")
        except ValueError:
            gaperr = 1
            cs = []
            logger.warning("1) Got a ValueError in getaartpic().")
            pass
        return gaperr
    #
    def getendtime(**stat):
        global dur,elap,gpstate
        stat = {'volume': '', 'repeat': '', 'random': '', 'single': '', 'consume': '', 'partition': '', 'playlist': '', 'playlistlength': '', 'mixrampdb': '', 'state': '', 'song': '', 'songid': '', 'nextsong': '', 'nextsongid': ''}
        try:
            geterr = 0
            msg = ""
            dur = cs['duration']
            if 'elapsed' in stat:
                elap = stat['elapsed']
            else:
                elap = 0
            remaining = float(dur) - float(elap)
            gendtime = time.time() + remaining
            logger.info("2) endtime generated: {}. Time Now: {}, Song dur: {}".format(gendtime,time.time(),dur))
            msg = str(cs["title"] + " - " + cs["artist"])
        except mpd.base.ConnectionError:
            geterr = 1
            logger.info("2) Got a ConnectionError in getendtime().")
            gendtime = time.time()
        except KeyError as getendtmkeyer:
            geterr = 1
            logger.info("2) Got a KeyError in getendtime().{}".format(getendtmkeyer))
            gendtime = time.time()
            pass
        return geterr,msg,gendtime
    #
    ## End sub-function definitions
    #
    cxstat = connext()  ## First connection attempt is here.
    gsent = sent
    if cxstat == 1:
        try:
            stat = client.status()
            gpstate = stat['state']
            cs = client.currentsong()
            if cs:
                gaperr = getaartpic(**cs)
            else:
                gaperr = 0
            if gaperr == 1:
                gaperr,cs = getaartpic(**cs)
            geterr,msg,gendtime = getendtime(**stat)  ### Generate 'endtime'.
            if geterr == 1:
                geterr,msg,gendtime = getendtime(**stat)
            logger.info("3) {}.".format(msg))
            globsongtitle = msg
            if firstrun != 1 and prevbtnstate != 'stop':
                if msg != confparse.get('serverstats','lastsongtitle'):
                    gsent = 0
                    logger.info("4) This is a new title.")
                    confparse.set("serverstats","lastsongtitle",str(msg))
                    with open(mmc4wIni, 'w') as SLcnf:
                        confparse.write(SLcnf)
                else:
                    logger.info("4) This is NOT a new title. - - - Rolling back gendtime and gsent.")
                    gendtime = endtime
                    gsent = 0
                    logger.info("5) gendtime returned to {}. Duration is {}.".format(gendtime,cs['duration']))
                    if float(cs['duration']) == 0.00:
                        next()
            else:
                logger.debug("Firstrun was set. {}".format(firstrun))
                logger.info("4) This is the last song you listened to.")
        except KeyError:
            msg = "No Current Song. Play one."
            displaytext1(msg)
        if geterr == 0 and gaperr == 0:
            endtime = gendtime
            pstate = gpstate
            sent = gsent
            firstrun = 0
            prevbtnstate = 'play'
    if pstate == 'stop' or pstate == 'pause':
        logger.info("6) pstate: {}.".format(pstate))
    if cxstat == 0:
        msg = "Not Connected."
        displaytext1(msg)

def songtitlefollower():
    logger.info(" ")
    logger.info("---=== Start songtitlefollower. The precursor to all else. ===---")
    logger.info(" ")
    global endtime,sent,pstate,pstart,pause_duration,eptime,elap
    sent = 0
    eptime = 0
    pstate = 'stop'
    thisendtime = endtime
    while True:
        if threading.active_count() > 2:
            logger.info("There are {} threads now.".format(threading.active_count()))
        sleep(.2)
        if pstate != 'stop' and pstate != 'pause':
            if endtime != thisendtime:
                logger.info("5) Threaded timer got new endtime.")
                thisendtime = endtime
                logger.info("6) New endtime: {}, Time now: {} sent: {}.".format(thisendtime,time.time(),sent))
            if thisendtime <= time.time() and sent == 0:
                logger.info("0) Threaded timer ran down. Getting new current song data.")
                sent = 1
                logger.debug("Bottom of songtitlefollower(). Calling getcurrsong().")
                getcurrsong()

def configurator():
        halt()
        proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
        if proceed == True:
            os.startfile(mmc4wIni)
            sleep(1)
            exit()

def logtoggler():
    print("logtoggler")
    confparse.read(mmc4wIni)
    logtog = confparse.get("program","logging")
    print('logtog: {}, logtog.upper(): {}'.format(logtog,logtog.upper()))
    if logtog.upper() == "ON":
        confparse.set('program','logging','off')
    elif logtog.upper() == 'OFF':
        confparse.set('program','logging','on')
    logger.debug("Writing log toggle to .ini file.")
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def getcurrstat():
    global buttonvar,lastpl
    cxstat = connext()
    if cxstat == 1:
        cstat = client.status()
        buttonvar = cstat["state"]
        logger.debug("getcurrstat() buttonvar: {}".format(buttonvar))
        msg = str("Server: " + serverip[-3:] +" | " + buttonvar + " | PlayList: " + lastpl)
    if cxstat == 0:
        msg = "Not Connected"
    return msg,buttonvar,lastpl

def plupdate():
    global lastpl
    cxstat = connext()
    if cxstat == 1:
        # cstat = client.status()
        cpl = client.listplaylists()
        pl = ""
        for plv in cpl:
            pl = plv['playlist'] + "," + pl
        confparse.read(mmc4wIni)
        lastpl = confparse.get("serverstats","lastsetpl")
        confparse.set("serverstats","playlists",str(pl))
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)

def displaytext1(msg):
    text1.delete("1.0", 'end')
    text1.insert("1.0", msg)

def displaytext2(msg2):
    text1.insert(END, msg2)

def albarttoggle():
    global aatgl,artw
    confparse.read(mmc4wIni)
    aatgl = confparse.get("albumart","albarttoggle")
    if aatgl == '1':
        try:
            # logger.info("Destroy AArt window.")
            artw.title()
            artw.destroy()
            aatgl = '0'
        except (AttributeError,NameError):
            pass
    else:
        # logger.info("Set aatgl to '1'.")
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

def returntoPL():
    cp.read(mmc4wIni)
    # pllist = cp.getlist('serverstats','playlists')
    lastpl = confparse.get("serverstats","lastsetpl")
    client.clear()
    client.load(lastpl)

def nonstdport():
    # logger.info("Setting non-standard port.")
    messagebox.showinfo("Setting a non-standard port","Set your non-standard port by editing the mmc4w.ini file. Use the Configure option in the File menu.\n\nPut your port number in the 'serverport' attribute under the [basic] section. 6600 is the default MPD port.")

def endWithError(msg):
    messagebox.showinfo("UhOh",msg)
    pause()
    sys.exit()

def exit():
    quitvar = halt()
    if quitvar == 'stop':
        logger.info("Connections closed.  Quitting.")
        sys.exit()


client.timeout = None                     # network timeout in seconds (floats allowed), default: None
client.idletimeout = None               # timeout for fetching the result of the idle command is handled seperately, default: None
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
# window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
window = Tk()  # Create the root window with errors in console. Invisible to Windows.
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
nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font
#
## DEFINE THE PLAY SINGLE WINDOW AND FUNCTIONS
#
def playsingle():
    cxstat = connext()
    if cxstat == 1:
        ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
        def select(event):
            i = listbx.curselection()[0]
            editing_item.set(items[i])
            client.clear()
            client.add(itemsraw[i]['file'])
            client.play()
            getcurrsong()
            plsngwin.destroy()
        ## The tk.Entry box runs this upon <Return>
        def update(event):
            srchterm = editing_item.get().replace('Search:','')
            findit = client.search('Title',srchterm)
            for f in findit:
                thisf = '"'+f['title'] + ' - ' + f['artist']+'"'
                thisfrec = dict([('song',thisf), ('file',f['file'])])
                itemsraw.append(thisfrec)
            for sng in itemsraw:
                items.append(sng['song'])
            var.set(items)
        ## FUNCTION DEFINITIONS DONE - NOW DO THE GUI STUFF
        plsngwin = Toplevel(window)
        plsngwin.title("Search & Play Single")
        plsngwin.configure(bg='black')
        plsngwin_x=200
        plsngwin_y=200
        plsngwin_xpos = str(int(plsngwin.winfo_screenwidth()- (plsngwin_x + 400)))
        plsngwin_ypos = str(int(plsngwin.winfo_screenheight()-(plsngwin_y + 640)))
        plsngwin.geometry('300x300+' + plsngwin_xpos + '+' +  plsngwin_ypos)
        plsngwin.columnconfigure([0,1,2,3,4],weight=1)
        plsngwin.rowconfigure([0,1,2,3,4,5,6],weight=1)
        plsngwin.iconbitmap('./_internal/ico/mmc4w-ico.ico')
        itemsraw = []
        items = []
        var = tk.StringVar(value=items)
        ## Feeds into update()
        listbx = tk.Listbox(plsngwin, listvariable=var)
        listbx.configure(bg='black',fg='white')
        listbx.grid(column=0,row=0,rowspan=6, padx=5,pady=5,sticky='NSEW')
        listbx.bind('<<ListboxSelect>>', select)
        ## Feeds into select()
        editing_item = tk.StringVar()
        entry = tk.Entry(plsngwin, textvariable=editing_item, width=200)
        entry.grid(row=6,column=0)
        entry.insert(0,'Search:')
        entry.bind('<Return>', update)
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
        logger.debug("serverip: {}".format(serverip))
        plupdate()
        PLSelWindow()
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverlist')
    ipvar = StringVar(srvrw)
    ipvar.set('Currently - ' + serverip + ' - Click for dropdown list.')
    plselwin = OptionMenu(srvrw,ipvar,*iplist,command=rtnplsel)
    plselwin.config(width=44)
    plselwin.grid(column=1,row=1)
#
## DEFINE THE PLAYLIST SELECTION WINDOW
#
def PLSelWindow():
    global serverip,lastpl
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
        global serverip,lastpl
        if plvar == "" or plvar == None:
            plvar = "Unchanged"
            confparse.read(mmc4wIni)
            msg = confparse.get("serverstats","lastsetpl")
        else:
            msg = plvar
        displaytext1(plvar)
        if plvar != "Unchanged":
            cxstat = connext()
            if cxstat == 1:
                client.clear()
                client.load(plvar)
                confparse.read(mmc4wIni)
                confparse.set("serverstats","lastsetpl",plvar)
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
                lastpl = plvar
        sw.destroy()
        sleep(1)
        text1['bg']='white'
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
    # aw.iconbitmap(path_to_dat + './_internal/ico/mmc4w-ico.ico')
    aw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
    awlabel = Label(aw, font=18, text ="About MMC4W " + version)
    awlabel.grid(column=0, columnspan=3, row=0, sticky="n")  # Place label in grid
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=1)
    aboutText = Text(aw, height=20, width=170, bd=3, padx=10, pady=10, wrap=WORD, font=nnFont)
    aboutText.grid(column=0, row=1)
    aboutText.insert(INSERT, "MMC4W is installed at\n" + path_to_dat + "\n\nMusic without the bloat.\n\nMMC4W is a Windows client for MPD.  It does nothing by itself, but if you have one or more MPD servers on your network, you might like this.\n\n"
                     "This little app holds forth the smallest set of functions I could think of to just play the music without being frustrating.\n\nCopyright 2023-2024 Gregory A. Sanders\nhttps://www.drgerg.com")
#
## DEFINE THE HELP WINDOW
#
def helpWindow():
    global aatgl
    if aatgl == '1':
        albarttoggle()
    pause()
    hw = Toplevel(window)
    hw.tk.call('tk', 'scaling', 1.0)    # This prevents the text being huge on hiDPI displays.
    hw.title("MMC4W Help")
    hwinWd = 800  # Set window size and placement
    hwinHt = 600
    x_Left = int(window.winfo_screenwidth() / 2 - hwinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - hwinHt / 2)
    hw.config(background="white")  # Set window background color
    hw.geometry(str(hwinWd) + "x" + str(hwinHt) + "+{}+{}".format(x_Left, y_Top))
    # hw.iconbitmap(path_to_dat + './_internal/ico/mmc4w-ico.ico')
    hw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
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
fileMenu.add_command(label="Select Playlist", command=PLSelWindow)
fileMenu.add_command(label='Toggle Logging', command=logtoggler)
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

lookMenu = Menu(menu, tearoff=False)
lookMenu.add_command(label="Turn Random On", command=plrandom)
lookMenu.add_command(label="Turn Random Off", command=plnotrandom)
lookMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
lookMenu.add_command(label="Reload Current Title", command=getcurrsong)
lookMenu.add_command(label='Play A Single',command=playsingle)
lookMenu.add_command(label='ReLoad Last Playlist',command=returntoPL)
lookMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
menu.add_cascade(label="Look", menu=lookMenu)

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

text1.grid(column=0, columnspan=5, row=0, padx=5)
# text2.grid(column=0, columnspan=7, row=2)

button_volup = tk.Button(window, width=9, text="Vol +", command=volup)                  # 
button_volup.grid(column=0, sticky='E', row=1, padx=1)                     # Place button in grid

button_voldn = tk.Button(window, width=9, text="Vol -", command=voldn)                  # 
button_voldn.grid(column=1, sticky='W', row=1, padx=1)                     # Place button in grid

button_play = tk.Button(window, width=9, text="Play", command=play)                  # 
button_play.grid(column=0, sticky='E', row=2, padx=1)                     # Place button in grid

button_stop = tk.Button(window, width=9, text="Stop", command=halt)                  # 
button_stop.grid(column=1, sticky='W', row=2, padx=1)                     # Place button in grid

button_prev = tk.Button(window, width=9, text="Prev", command=previous)                  # 
button_prev.grid(column=2, sticky='W', row=2, padx=1)                     # Place button in grid

button_pause = tk.Button(window, width=9, text="Pause", command=pause)                  # 
button_pause.grid(column=3, sticky='W', row=2, padx=1)                     # Place button in grid

button_next = tk.Button(window, width=9, text="Next", command=next)                  # 
button_next.grid(column=4, sticky='W', row=2, padx=1)                     # Place button in grid

button_tbtog = tk.Button(window, width=9, text="Mode", command=tbtoggle)                  # 
button_tbtog.grid(column=2, sticky='W', row=1, padx=1)                     # Place button in grid

button_load = tk.Button(window, width=9, text="Art", command=albarttoggle)                  #
button_load.grid(column=3, sticky='W', row=1, padx=1)                     # Place button in grid

button_exit = tk.Button(window, width=9, text="Quit", command=exit)                  #
button_exit.grid(column=4, sticky='W', row=1, padx=1)                     # Place button in grid

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
songused = 0
###
# lastpl is "Last Playlist". dur is "Song Duration". eptime is "Elasped Pause Time".
###
def threesecdisplaytext():
    global evenodd, globsongtitle,buttonvar,lastpl,endtime,dur,eptime
    # print("endtime at threesecdisplay(): {}".format(endtime))
    def eo1():
        global evenodd, globsongtitle
        # logger.info("evenodd: " + str(evenodd))
        if evenodd == 1:
            # logger.info("evenodd: " + str(evenodd))
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd,buttonvar,dur,endtime,songused
        if buttonvar != 'stop' and buttonvar != 'pause':
            songused = float(dur) - (endtime - time.time())
            # songused = str("{:.2f}".format(songused))
            songused = str(int(songused))
            # print("songused: {}".format(songused))
        if buttonvar == 'pause':
            songused = songused
        # logger.info("evenodd: " + str(evenodd))
        if evenodd == 2:
            # logger.info("evenodd: " + str(evenodd))
            # msg,buttonvar,lastpl = getcurrstat()
            msg = str("Srvr: " + serverip[-3:] +" | " + buttonvar + " | PL: " + lastpl)
            msg2=str(' | {}/{} secs.'.format(songused,dur[:3]))
            evenodd = 1
            displaytext1(msg)
            displaytext2(msg2)
    window.after(1000,eo1)
    window.after(2500,eo2)
    window.after(3000,threesecdisplaytext)
#
## Start 
logger.debug("\n-----======<<<<  STARTING UP  >>>>======-----\n")
firstrun = 1
prevbtnstate = 'stop'
threesecdisplaytext()
getcurrsong()
logger.info("Down at the bottom. Firstrun: {}".format(firstrun))
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