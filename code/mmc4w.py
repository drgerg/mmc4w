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


version = "v0.8.2"
# v0.8.2 = I think I got that decode error this time.
# v0.8.1 - Handle a new comm error.
# v0.8.0 - Album mode, artist lookup, track number, vol indication, inidicator for 'not-random' mode, select PL, and more.
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

global serverip,serverport,tbarini
endtime = time.time()
cxstat = 0
buttonvar = 'stop'
pstart = 0
dur='0'
pause_duration = 0.0
sent = 0
lastvol = confparse.get('serverstats','lastvol')

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
if confparse.get('serverstats','lookuppl') == '1':
    lastpl = confparse.get('serverstats','lookuppltext')
else:
    lastpl = confparse.get('serverstats','lastsetpl')


def connext():  ## Checks connection, then connects if necessary.
    global serverip,serverport
    try:
        client.ping()  # Use ping() to see if we're connected.
        cxstat = 1
    except  (mpd.base.ConnectionError,ConnectionRefusedError,UnicodeDecodeError) as errvar:
        print('Error received: ' + str(errvar))
        logger.debug("errvar: {}".format(errvar))
        cxstat = 0
        try:
            logger.debug("Try to connect to {} on port {}".format(serverip,serverport))
            client.connect(serverip, int(serverport))
            cxstat = 1
            print('2nd try. cxstat is : ' + str(cxstat))
        except  (ValueError, mpd.base.ConnectionError,ConnectionRefusedError) as errvar:
            logger.debug("Second level errvar: {}".format(errvar))
            cxstat = 0
            print('2nd try. errvar is : {}. \ncxstat is : {}'.format(errvar,cxstat))
            pass
    return cxstat


def plrandom():  # Set random playback mode.
    cxstat = connext()
    if cxstat == 1:
        client.random(1)
        text1['bg']='white'
        text1['fg']='black'

def plnotrandom():  # Set sequential playback mode.
    cxstat = connext()
    if cxstat == 1:
        client.random(0)
        text1['bg']='navy'
        text1['fg']='white'

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

def pause():  # Pause is complicated because of time-keeping.
    global buttonvar,endtime,pstart,pause_duration,eptime,pstate
    logger.debug('Play state at button press: {}.'.format(buttonvar))
    #
    if buttonvar == 'pause':        ## SYSTEM WAS PAUSED
        logger.debug("pause() pstart: {}".format(pstart))
        pause_duration = time.time() - pstart
        logger.debug("time.time(): {}, pstart: {}.".format(time.time(),pstart))
        logger.info(f"0) Playback resumed at {time.time()}. Pause duration: {pause_duration:.2f}")
        oldendtime = endtime
        endtime = endtime + pause_duration
        logger.info('2) New endtime generated in pause(). Old: {}, New {}'.format(oldendtime,endtime))
        button_pause.configure(text='Pause',bg='SystemButtonFace') ## 'systemButtonFace' is the magic word.
        pstate = 'play'
        pstart = 0 
        #                           ## Now client.pause() sets it to PLAY
    if buttonvar == 'play':         ## SYSTEM WAS PLAYING
        pstart = time.time()
        buttonvar = 'pause'
        button_pause.configure(text='Resume',bg="orange")
        logger.info("0) Playback paused at {}.".format(pstart))
        pstate = 'pause'
        #                           ## Now client.pause() sets it to PAUSE
    cxstat = connext()
    if cxstat == 1:
        client.pause()
    getcurrstat()

def volup():
    global lastvol
    vol_int = int(lastvol)
    cxstat = connext()
    if cxstat == 1:
        if vol_int < 100:
            client.volume(+5)
            vol_int = vol_int + 5
            volbtncolor(vol_int)
    lastvol = str(vol_int)


def voldn():
    global lastvol
    vol_int = int(lastvol)
    cxstat = connext()
    if cxstat == 1:
        if vol_int > 0:
            client.volume(-5)
            vol_int = vol_int - 5
            volbtncolor(vol_int)
    lastvol = str(vol_int)


def volbtncolor(vol_int):  # Provide visual feedback on volume buttons.
    thisvol = vol_int
    if thisvol == 100:
        button_volup.configure(text='100',bg="#8B8378",fg='white')
    if thisvol == 95:
        button_volup.configure(text='95',bg="#8B8378",fg='white')
    if thisvol == 90:
        button_volup.configure(text='90',bg="#CDC0B0",fg='black')
    if thisvol == 85:
        button_volup.configure(text='85',bg="#CDC0B0",fg='black')
    if thisvol == 80:
        button_volup.configure(text='80',bg="#FFEFDB",fg='black')
    if thisvol == 75:
        button_volup.configure(text='75',bg="#FFEFDB",fg='black')
    if thisvol <= 70 and thisvol >=30:
        button_volup.configure(text='Vol +',bg='SystemButtonFace')
        button_voldn.configure(text='Vol -',bg='SystemButtonFace')
    if thisvol == 25:
        button_voldn.configure(text='25',bg="#98F5FF",fg='black')
    if thisvol == 20:
        button_voldn.configure(text='20',bg="#98F5FF",fg='black')
    if thisvol == 15:
        button_voldn.configure(text='15',bg="#7AC5CD",fg='black')
    if thisvol == 10:
        button_voldn.configure(text='10',bg="#7AC5CD",fg='black')
    if thisvol == 5:
        button_voldn.configure(text='5',bg="#53868B",fg='white')
    if thisvol == 0:
        button_voldn.configure(text='0',bg="#53868B",fg='white')
    confparse.set('serverstats','lastvol',lastvol)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def toglrepeat():
    cxstat = connext()
    if cxstat == 1:
        cstats = client.status()
        rptstat = cstats['repeat']
        if rptstat == '0':
            client.repeat(1)
            msg = 'Repeat is set to 1.'
        else:
            client.repeat(0)
            msg = 'Repeat is set to 0.'
        displaytext1(msg)

def toglconsume():
    cxstat = connext()
    if cxstat == 1:
        cstats = client.status()
        cnsmstat = cstats['consume']
        if cnsmstat == '0':
            client.consume(1)
            msg = 'Consume is set to 1.'
        else:
            client.consume(0)
            msg = 'Consume is set to 0.'
        displaytext1(msg)

def toglsingle():
    cxstat = connext()
    if cxstat == 1:
        cstats = client.status()
        snglstat = cstats['single']
        if snglstat == '0':
            client.single(1)
            msg = 'Single is set to 1.'
        else:
            client.single(0)
            msg = 'Single is set to 0.'
        displaytext1(msg)
#
##  DEFINE getcurrsong() - THE MOST POPULAR FUNCTION HERE.
#
def getcurrsong():
    global globsongtitle,endtime,aatgl,sent,pstate,elap,firstrun,prevbtnstate,lastvol
    if threading.active_count() < 2:
        logger.debug("The threading.active_count() dropped below 2. Quitting.")
        exit()
    #
    logger.debug("Sent: {}".format(sent))
    # Sub-function definitions
    def getaartpic(**cs):
        global aatgl,aartvar
        aadict = {}
        try:
            gaperr = 0
            aadict = client.readpicture(cs['file'])
            logger.debug('len(aadict) is: {}'.format(len(aadict)))
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
        except UnicodeDecodeError:
            gaperr = 1
            cs = []
            logger.warning("1) Got a UnicodeDecodeError in getaartpic().")
            aartvar = 0
            aadict = {}
            pass
        return gaperr
    #
    def getendtime(**stat):
        global dur,elap,gpstate
        try:
            geterr = 0
            msg = ""
            dur = cs['duration']
            trk = cs['track'].zfill(2)
            if 'elapsed' in stat:
                elap = stat['elapsed']
            else:
                elap = 0
            remaining = float(dur) - float(elap)
            gendtime = time.time() + remaining
            logger.info("2) endtime generated: {}. Time Now: {}, Song dur: {}".format(gendtime,time.time(),dur))
            msg = str(trk + '-' + cs["title"] + " - " + cs["artist"])
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
    ## End getcurrsong(): sub-function definitions
    #
    cxstat = connext()  ## First connection attempt is here.
    gsent = sent
    if cxstat == 1:
        try:
            stat = client.status()
            logger.debug('status: {}'.format(stat))
            if stat['random'] == '0':
                text1['bg']='navy'
                text1['fg']='white'
                window.update()
            lastvol = stat['volume']
            vol_int = int(lastvol)
            volbtncolor(vol_int)
            gpstate = stat['state']
            logger.debug("Retrieving 'cs' in getcurrsong().")
            cs = client.currentsong()
            if cs:
                gaperr = getaartpic(**cs)
            else:
                gaperr = 0
            if gaperr == 1:
                gaperr = getaartpic(**cs)
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
    confparse.read(mmc4wIni)
    logtog = confparse.get("program","logging")
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
    global aatgl,artw,aartvar
    cxstat = connext()
    if cxstat == 1:
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
    argeo = artw.geometry()
    argeo = argeo.replace('x',' ')
    argeo = argeo.replace('+',' ')
    argeo = argeo.split()
    wingeo = window.geometry()
    wingeo = wingeo.replace('x',' ')
    wingeo = wingeo.replace('+',' ')
    wingeo = wingeo.split()
    x_Left = int(window.winfo_screenwidth())
    y_Top = int(window.winfo_screenheight())
    xarw = int(x_Left)-int(argeo[2])
    yarw = int(y_Top)-int(argeo[3])
    xwndw = int(x_Left)-int(wingeo[2])
    ywndw = int(y_Top)-int(wingeo[3])
    confparse.set("albumart","aartwin_x",str(xarw))
    confparse.set("albumart","aartwin_y",str(yarw))
    confparse.set("mainwindow","win_x",str(xwndw))
    confparse.set("mainwindow","win_y",str(ywndw))
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:
        window.overrideredirect(1)
        artw.overrideredirect(1)
        confparse.set("mainwindow","titlebarstatus",'0')  # Titlebar off (overridden)
    else:
        window.overrideredirect(0)
        artw.overrideredirect(0)
        confparse.set("mainwindow","titlebarstatus",'1')  # Titlebar on (not overridden)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    getcurrsong()

def returntoPL():
    global lastpl
    cxstat = connext()
    if cxstat == 1:
        confparse.read(mmc4wIni)
        lastpl = confparse.get("serverstats","lastsetpl")
        confparse.set("serverstats","lookuppl",'0')
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        client.clear()
        client.load(lastpl)

def nonstdport():
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
## WRAP UP AND DISPLAY ==========================================================================================
#
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
# window = Tk()  # Create the root window with errors in console, invisible to Windows.
window.title("Minimal MPD Client " + version)  # Set window title
winWd = 380  # Set window size
winHt = 80
confparse.read(mmc4wIni)  # get parameters from config .ini file.
win_x = int(confparse.get("mainwindow","win_x"))
win_y = int(confparse.get("mainwindow","win_y"))
tbarini = confparse.get("mainwindow","titlebarstatus")
x_Left = int(window.winfo_screenwidth() - (win_x))
y_Top = int(window.winfo_screenheight() - (win_y))
window.geometry(str(winWd) + "x" + str(winHt) + "+{}+{}".format(x_Left, y_Top))
window.config(background='white')  # Set window background color
window.columnconfigure([0,1,2,3,4], weight=0)
window.rowconfigure([0,1,2], weight=0)
if tbarini == '0':
    window.overrideredirect(1)
nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font
#
## DEFINE THE LOOKUP WINDOW AND ASSOCIATED FUNCTIONS
#
def lookupwin(lookupT):
    secfind = ''
    if lookupT == 'title':
        srchTxt = 'Title: '
        secfind = 'artist'
    if lookupT == 'album':
        srchTxt = 'Album: '
        secfind = 'artist'
    if lookupT == 'artist':
        srchTxt = 'Artist: '
        secfind = 'title'
    cxstat = connext()
    if cxstat == 1:
        ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
        def clickedit(event):
            global lastpl
            cxstat = connext()
            if cxstat == 1:
                i = listbx.curselection()[0]
                # editing_item.set(dispitems[i])
                if lookupT == 'album':
                    albsngs = client.search(lookupT,str(itemsraw[i]['album']))
                    ## We turn random mode off for albums. ##
                    rstat = client.status()['random']
                    if rstat == '1':
                        client.random(0)
                        text1['bg']='navy'  # True Blue album mode
                        text1['fg']='white' # Random mode
                    client.clear()
                    for s in albsngs:
                        client.add(s['file'])
                    play()
                else:
                    client.clear()
                    client.add(itemsraw[i]['file'])
                    play()
                lastpl = confparse.get('serverstats','lookuppltext')  # default: 'That Thing You Looked For'
                confparse.read(mmc4wIni)
                confparse.set("serverstats","lookuppl",'1')
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
                plsngwin.update()
                getcurrsong()
                plsngwin.destroy()
        ## The tk.Entry box runs this upon <Return>
        def pushret(event):
            cxstat = connext()
            if cxstat == 1:
                dispitems = []
                srchterm = editing_item.get().replace('Search: ','')
                editing_item.set('Search: ')
                if srchterm == 'status':
                    stats = client.status()
                    for s,v in stats.items():
                        dispitems.append(s + ' : ' + v)
                    for i in dispitems:
                        listbx.insert(END,i)
                    plsngwin.update()
                if srchterm == 'stats':
                    stats = client.stats()
                    for s,v in stats.items():
                        if s == 'uptime' or s == 'playtime' or s == 'db_playtime':
                            v = int(v)
                            v = time.strftime("%H:%M:%S", time.gmtime(v))
                        if s == 'db_update':
                            v = int(v)
                            v = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(v))
                        dispitems.append(s + ' : ' + v)
                    for i in dispitems:
                        listbx.insert(END,i)
                    plsngwin.update()
                if srchterm != 'status' and srchterm != 'stats':
                    findit = client.search(lookupT,srchterm)
                    lastf = ''
                    for f in findit:
                        thisf = '"'+f[lookupT] + ' - ' + f[secfind] + ' | ' + f['album']+'"'
                        thisfrec = dict([('song',thisf), ('file',f['file']),('album',f['album'])])
                        if lookupT == 'album':
                            if f[lookupT] != lastf:
                                itemsraw.append(thisfrec)
                                lastf = f[lookupT]
                        else:
                            itemsraw.append(thisfrec)
                    for sng in itemsraw:
                        dispitems.append(sng['song'])
                    for i in dispitems:
                        listbx.insert(END,i)
                    plsngwin.update()
                    if srchterm == 'quit;':
                        plsngwin.destroy()
        ## FUNCTION DEFINITIONS DONE - NOW DO THE GUI STUFF
        plsngwin = Toplevel(window)
        plsngwin.title("Search & Play " + srchTxt)
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
        dispitems = []
        var = tk.StringVar(value=dispitems)
        ## Feeds into update()
        listbx = tk.Listbox(plsngwin)
        listbx.configure(bg='black',fg='white')
        listbx.grid(column=0,row=0,rowspan=6, padx=5,pady=5,sticky='NSEW')
        listbx.bind('<<ListboxSelect>>', clickedit)
        ## Feeds into select()
        editing_item = tk.StringVar()
        entry = tk.Entry(plsngwin, textvariable=editing_item, width=200)
        entry.grid(row=6,column=0)
        entry.insert(0,'Search: ')
        entry.bind('<Return>', pushret)
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
        msg = ipvar
        displaytext1(msg)
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
                confparse.set("serverstats","lookuppl",'0')
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
    global artw,tbarini
    tbarini = confparse.get("mainwindow","titlebarstatus")
    if aartvar == 1:
        thisimage = BytesIO(aadict['binary'])
    if aartvar == 0:
        thisimage = path_to_dat + '/ico/mmc4w.png'
    artw = Toplevel(window)
    artw.title("AlbumArt")
    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    aartwin_x = int(confparse.get("albumart","aartwin_x"))
    aartwin_y = int(confparse.get("albumart","aartwin_y"))
    artwinWd = int(confparse.get("albumart","artwinWd"))
    artwinHt = int(confparse.get("albumart","artwinHt"))
    x_Left = int(window.winfo_screenwidth() - aartwin_x)
    y_Top = int(window.winfo_screenheight() - aartwin_y)
    artw.config(background="white")  # Set window background color
    artw.geometry(str(artwinWd) + "x" + str(artwinHt) + "+{}+{}".format(x_Left, y_Top))
    artw.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')
    artw.columnconfigure([0,1,2], weight=1)
    artw.rowconfigure(0, weight=1)
    artw.rowconfigure(1, weight=1)
    aart = Image.open(thisimage)
    aart = aart.resize((100,100))
    aart = ImageTk.PhotoImage(aart)
    aart.image = aart  # required for some reason
    aartLabel = Label(artw,image=aart)
    aartLabel.grid(column=0, row=0, padx=5, pady=5)

    if tbarini == '0':
        artw.overrideredirect(1)
    artw.update()
    # artw.overrideredirect(1) ## turn off the titlebar
#
## MENU AND MENU ITEMS
#
Frame(window)
menu = Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
fileMenu = Menu(menu, tearoff=False)
fileMenu.add_command(label="Configure", command=configurator)
fileMenu.add_command(label="Select a Server", command=SrvrWindow)
fileMenu.add_command(label='Toggle Logging', command=logtoggler)
fileMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="File", menu=fileMenu)

toolMenu = Menu(menu, tearoff=False)
toolMenu.add_command(label="Reload Current Title", command=getcurrsong)
toolMenu.add_command(label="Turn Random On", command=plrandom)
toolMenu.add_command(label="Turn Random Off", command=plnotrandom)
toolMenu.add_command(label="Toggle Repeat", command=toglrepeat)
toolMenu.add_command(label="Toggle Consume", command=toglconsume)
toolMenu.add_command(label="Toggle Single", command=toglsingle)
toolMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
toolMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
menu.add_cascade(label="Tools", menu=toolMenu)

lookMenu = Menu(menu, tearoff=False)
lookMenu.add_command(label='Play a Single',command=lambda: lookupwin('title'))
lookMenu.add_command(label='Play an Album',command=lambda: lookupwin('album'))
lookMenu.add_command(label='Find by Artist',command=lambda: lookupwin('artist'))
lookMenu.add_command(label='Reload Last Playlist',command=returntoPL)
lookMenu.add_command(label="Select a Playlist", command=PLSelWindow)
menu.add_cascade(label="Look", menu=lookMenu)

helpMenu = Menu(menu, tearoff=False)
helpMenu.add_command(label="Help", command=helpWindow)
helpMenu.add_command(label="About", command=aboutWindow)
menu.add_cascade(label="Help", menu=helpMenu)

window.iconbitmap(path_to_dat + './ico/mmc4w-ico.ico')

## Set up text window
text1 = Text(window, height=1, width=52, wrap=WORD, font=nnFont)
text1.grid(column=0, columnspan=5, row=0, padx=5)
#
# Define buttons
button_volup = tk.Button(window, width=9, text="Vol +", font=nnFont, command=volup)                  # 
button_volup.grid(column=0, sticky='E', row=1, padx=1)                     # Place button in grid

button_voldn = tk.Button(window, width=9, text="Vol -", font=nnFont, command=voldn)                  # 
button_voldn.grid(column=1, sticky='W', row=1, padx=1)                     # Place button in grid

button_play = tk.Button(window, width=9, text="Play", font=nnFont, command=play)                  # 
button_play.grid(column=0, sticky='E', row=2, padx=1)                     # Place button in grid

button_stop = tk.Button(window, width=9, text="Stop", font=nnFont, command=halt)                  # 
button_stop.grid(column=1, sticky='W', row=2, padx=1)                     # Place button in grid

button_prev = tk.Button(window, width=9, text="Prev", font=nnFont, command=previous)                  # 
button_prev.grid(column=2, sticky='W', row=2, padx=1)                     # Place button in grid

button_pause = tk.Button(window, width=9, text="Pause", font=nnFont, command=pause)                  # 
button_pause.grid(column=3, sticky='W', row=2, padx=1)                     # Place button in grid

button_next = tk.Button(window, width=9, text="Next", font=nnFont, command=next)                  # 
button_next.grid(column=4, sticky='W', row=2, padx=1)                     # Place button in grid

button_tbtog = tk.Button(window, width=9, text="Mode", font=nnFont, command=tbtoggle)                  # 
button_tbtog.grid(column=2, sticky='W', row=1, padx=1)                     # Place button in grid

button_load = tk.Button(window, width=9, text="Art", font=nnFont, command=albarttoggle)                  #
button_load.grid(column=3, sticky='W', row=1, padx=1)                     # Place button in grid

button_exit = tk.Button(window, width=9, text="Quit", font=nnFont, command=exit)                  #
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
    def eo1():
        global evenodd, globsongtitle
        if evenodd == 1:
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd,buttonvar,dur,endtime,songused
        if buttonvar != 'stop' and buttonvar != 'pause':
            songused = float(dur) - (endtime - time.time())
            if songused >= float(dur[:3]):
                songused = float(dur[:3])
                getcurrstat()
            songused = str(int(songused))
        if buttonvar == 'pause':
            songused = songused
        if evenodd == 2:
            msg = str("Svr: " + serverip[-3:] +" | " + buttonvar + " | PL: " + lastpl)
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

