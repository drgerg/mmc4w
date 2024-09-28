#!/usr/bin/env python3
# 
# mmc4w.py - 2024 by Gregory A. Sanders (dr.gerg@drgerg.com)
# Minimal MPD Client for Windows - basic set of controls for an MPD server.
# Take up as little space as possible to get the job done.
# mmc4w.py uses the python-musicpd library.
##

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.font import Font
import datetime
from time import sleep
import sys
from configparser import ConfigParser
import os
import musicpd
import threading
from PIL import ImageTk, Image
import time
import logging
import webbrowser
from collections import OrderedDict
from pathlib import Path

if sys.platform != "win32":
    import subprocess
else:
    # from win32api import GetSystemMetrics
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
    ctypes.windll.user32.SetProcessDPIAware()

version = "v2.1.0"
# v2.1.0 - Gently handle attempting to run with no server. Add 'delete debug log'.
# v2.0.9 - Finally get scale factors working. Renamed menus. Browse help.html.
# v2.0.8 - Use buttons in search windows for added flexibility.
# v2.0.7 - Trade pathlib for os.path. Deal with 'already connected' error.
# v2.0.6 - Fine tuning lookups and search windows. Completely revamp win size methods.
# v2.0.5 - Way better Playlist Build Mode.
# v2.0.4 - Doing things a better way.
# v2.0.1 - Handling the queue.
# v2.0.0 - Introduced classes for some windows. Tons more stability tweaks.
# v1.0.0 - Fixed error in the fiver() function.
# v0.9.9 - tk.Scrollbars on all windows. Windows are more uniform.

# colours used for buttons
colrButton = "grey90"                   # default button colour
colrVolume = {          # volume button definitions
    # key:  Vol+ label, bg color, fg color,      Vol- label, bg color, fg color
    100: ['100','gray13','white',          'Vol -','gray90','black'],
    95:  [ '95','gray12','white',          'Vol -','gray90','black'],
    90:  [ '90','AntiqueWhite4','white', 'Vol -','gray90','black'],
    85:  [ '85','AntiqueWhite4','white', 'Vol -','gray90','black'],
    80:  [ '80','AntiqueWhite3','black', 'Vol -','gray90','black'],
    75:  [ '75','AntiqueWhite3','black', 'Vol -','gray90','black'],
    70:  [ '70','AntiqueWhite2','black', 'Vol -','gray90','black'],
    65:  [ '65','AntiqueWhite2','black', 'Vol -','gray90','black'],
    60:  [ '60','AntiqueWhite1','black', 'Vol -','gray90','black'],
    55:  [ '55','AntiqueWhite1','black', 'Vol -','gray90','black'],
    50:  ['Vol +','gray90','black',      'Vol -','gray90','black'],
    45:  ['Vol +','gray90','black',     '45','CadetBlue1','black'],
    40:  ['Vol +','gray90','black',     '40','CadetBlue1','black'],
    35:  ['Vol +','gray90','black',     '35','turquoise1','black'],
    30:  ['Vol +','gray90','black',     '30','turquoise1','black'],
    25:  ['Vol +','gray90','black',     '25','turquoise2','black'],
    20:  ['Vol +','gray90','black',     '20','turquoise2','black'],
    15:  ['Vol +','gray90','black',     '15','turquoise3','black'],
    10:  ['Vol +','gray90','black',     '10','turquoise3','black'],
    5:   ['Vol +','gray90','black',      '5','turquoise4','white'],
    0:   ['Vol +','gray90','black',      '0','turquoise4','white']
}

client = musicpd.MPDClient()                    # create client object

# confparse is for general use for normal text strings.
# confparse = ConfigParser()
confparse = ConfigParser()

# cp is for use where lists are involved.
cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})

# path_to_dat = path.abspath(path.dirname(__file__))
path_to_dat = Path(__file__).parent
mmc4wIni = path_to_dat / "mmc4w.ini"
workDir = os.path.expanduser("~")
confparse.read(mmc4wIni)

lastpl = confparse.get("serverstats","lastsetpl") ## 'lastpl' is the most currently loaded playlist.
if confparse.get('basic','installation') == "":
    confparse.set('basic','installation',str(path_to_dat))
if confparse.get('basic','sysplatform') == "":
    confparse.set('basic','sysplatform',sys.platform)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
#
logLevel = confparse.get('program','loglevel').upper()
logtoggle = confparse.get('program','logging').upper()
if logtoggle == 'OFF':
    logLevel = 'WARNING'

if logLevel == "INFO":
    if os.path.isfile(path_to_dat / "mmc4w.log"):
        os.remove(path_to_dat / "mmc4w.log")

if logLevel == 'DEBUG':
    logging.basicConfig(
        filename=path_to_dat / "mmc4w_DEBUG.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.DEBUG,
    )

if logLevel == 'INFO':
    logging.basicConfig(
        filename=path_to_dat / "mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.INFO,
    )

if logLevel == 'WARNING':
    logging.basicConfig(
        filename=path_to_dat / "mmc4w.log",
        format="%(asctime)s - %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        level=logging.WARNING,
    )

logger = logging.getLogger(__name__)
musicpd_logger = logging.getLogger('musicpd')
musicpd_logger.setLevel(logging.WARNING)
logger.info(" ")
logger.info("     -----======<<<<  STARTING UP  >>>>======-----")
logger.info("D0) sys.platform is {}".format(sys.platform))
logger.info(" ")

global tbarini,endtime,firstrun, confparse
aartvar = 0     ## aartvar tells us whether or not to display the art window.
endtime = time.time()
cxstat = 0      ## 'cxstat' indicates the connection status. '1' is connected.
buttonvar = 'stop'
pstart = 0      ## the time the pause button was pressed.
dur='0'         ## the value from client.getcurrentsong() showing the song's duration.
elap='0'
pause_duration = 0.0
sent = 0
lastvol = confparse.get('serverstats','lastvol')
serverlist = confparse.get('basic','serverlist')
serverip = confparse.get('serverstats', 'lastsrvr')
serverport = confparse.get('basic','serverport')
firstrun = confparse.get('basic','firstrun')
ran = 'r'
rpt = 'p'
sin = 's'
con = 'c'
if serverlist == "":
    proceed = messagebox.askokcancel("Edit Config File","OK closes the app and opens mmc4w.ini for editing.")
    if proceed == True:
        if sys.platform == "win32":
            os.startfile(mmc4wIni)
        else:
            subprocess.run(["xdg-open", mmc4wIni])
        sys.exit()

if serverip == '':
    cp.read(mmc4wIni)
    iplist = cp.getlist('basic','serverlist')
    serverip = iplist[0]
    confparse.set('serverstats','lastsrvr',serverip)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    messagebox.showinfo("Server Set","Current server is set to\n" + serverip)

if confparse.get('serverstats','lastport') != "":
    serverport = confparse.get('serverstats','lastport')
else:
    confparse.set('serverstats','lastport',serverport)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

if version != confparse.get('program','version'):
    confparse.set('program','version',version)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

lastpl = confparse.get('serverstats','lastsetpl')

def maketsbinilist(): # for search windows
    tsbinilist = [int(s) for s in confparse.get('searchwin','swingeo').split(',')]
    return tsbinilist

def makebplwinilist(): # for the 'Build Playlist' window
    bplwinilist = [int(s) for s in confparse.get('buildplwin','bplwingeo').split(',')]
    return bplwinilist

def makeartwinilist():
    artwinilist = [int(s) for s in confparse.get('albumart','aartgeo').split(',')]
    artwinilist[1] = artwinilist[0]
    return artwinilist

bplwinilist = makebplwinilist()
tsbinilist = maketsbinilist()
artwinilist = makeartwinilist()

cp.read(mmc4wIni)
pllist = cp.getlist('serverstats','playlists')

#
## ================= TOPLEVEL WINDOW CLASS DEFINITION ==========================
class TlSbBWin(tk.Toplevel):  ## with Listbox and Scrollbar and Button.
    def __init__(self, parent, title, inilist):
        tk.Toplevel.__init__(self)
        self.swin_x = inilist[2]
        self.swin_y = inilist[3]
        self.swinht = inilist[1]
        self.swinwd = inilist[0]
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        if sys.platform == "win32":
            self.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico")
        else:
            self.iconphoto(False, iconpng) # Linux
        self.columnconfigure([0,1,2,3],weight=1)
        self.rowconfigure([0,1,2,3,4,5],weight=1)
        self.rowconfigure([6,7],weight=0)
        self.listvar = tk.StringVar()
        self.listbx = tk.Listbox(self,listvariable=self.listvar)
        self.listbx.configure(bg='black',fg='white')
        self.listbx.grid(column=0,row=0,columnspan=4,rowspan=6,sticky='NSEW')
        scrollbar = tk.Scrollbar(self, orient='vertical')
        self.listbx.config(yscrollcommand = scrollbar.set)
        scrollbar.config(bg='black',command=self.listbx.yview)
        scrollbar.grid(column=5,row=0,rowspan=6,sticky='NS')
        self.frame = tk.Frame(self,bg='black')
        self.frame.rowconfigure(0,weight=1)
        self.frame.columnconfigure(0,weight=1)
        self.frame.grid(row=7,sticky='NSEW')
        self.closebtn = tk.Button(self.frame, bg='gray90', width=8, font=nnFont, text='Close', command=lambda:self.destroy())
        self.closebtn.grid(column=0,row=0,sticky='W')

class TlSbWin(tk.Toplevel):  ## with Listbox and Scrollbar.
    def __init__(self, parent, title, inilist):
        tk.Toplevel.__init__(self)
        self.swin_x = inilist[2]
        self.swin_y = inilist[3]
        self.swinht = inilist[1]
        self.swinwd = inilist[0]
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        if sys.platform == "win32":
            self.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico")
        else:
            self.iconphoto(False, iconpng) # Linux
        self.columnconfigure([0,1,2,3],weight=1)
        self.rowconfigure([0,1,2,3,4,5],weight=1)
        self.rowconfigure([6],weight=0)
        self.listvar = tk.StringVar()
        self.listbx = tk.Listbox(self,listvariable=self.listvar)
        self.listbx.configure(bg='black',fg='white')
        self.listbx.grid(column=0,row=0,columnspan=4,rowspan=6,sticky='NSEW')
        scrollbar = tk.Scrollbar(self, orient='vertical')
        self.listbx.config(yscrollcommand = scrollbar.set)
        scrollbar.config(bg='black',command=self.listbx.yview)
        scrollbar.grid(column=5,row=0,rowspan=6,sticky='NS')

class TbplWin(tk.Toplevel):  ##Build Playlist Window.
    def __init__(self, parent, title, inilist):
        tk.Toplevel.__init__(self)
        self.swin_x = inilist[2]
        self.swin_y = inilist[3]
        self.swinht = inilist[1]
        self.swinwd = inilist[0]
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        if sys.platform == "win32":
            self.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico")
        else:
            self.iconphoto(False, iconpng)
        self.columnconfigure([0,1], weight=1)
        self.rowconfigure(0,weight=1)
        self.listvar = tk.StringVar()
        self.listbx = tk.Listbox(self,listvariable=self.listvar,exportselection=0)
        self.listbx.configure(bg='black',fg='white')
        self.listbx.grid(column=0,row=0,sticky='NSEW')
        self.listvar2 = tk.StringVar()
        self.listbx2 = tk.Listbox(self,listvariable=self.listvar2,exportselection=0)
        self.listbx2.configure(bg='black',fg='white')
        self.listbx2.grid(column=1,row=0,sticky='NSEW')

class TartWin(tk.Toplevel):  ## for album art.
    def __init__(self, parent, title, artwinilist,aart):
        tk.Toplevel.__init__(self)
        self.swin_x = artwinilist[2]
        self.swin_y = artwinilist[3]
        self.swinht = artwinilist[0] # use width for both to keep square
        self.swinwd = artwinilist[0]
        self.title(title)
        self.configure(bg='black')
        srchwin_xpos = str(int(self.winfo_screenwidth() - self.swin_x))
        srchwin_ypos = str(int(self.winfo_screenheight() - self.swin_y))
        geometrystring = str(self.swinwd) + 'x'+ str(self.swinht) + '+' + srchwin_xpos + '+' +  srchwin_ypos
        self.geometry(geometrystring)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.config(bg="white")  # Set window background color
        self.aartLabel = tk.Label(self,image=aart)
        self.aartLabel.grid(column=0, row=0, padx=5, pady=5)
        if sys.platform == "win32":
            self.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico") # - Windows
        else:
            self.iconphoto(False, iconpng) # Linux
#
## ================  END OF CLASS DEFINITIONS ===================================
#
# wingeoxlator(geostring,None,'') brings in a tkinter geometry() string and outputs a list that
#   configparser can deal with.
#
# wingeoxlator('',ValuesListObject,'') takes in a list of values and
#   output them in the proper string format to use in a tk.geometry() call.
#
# wingeoxlator('',None,ValuesListObject) converts a list object back into a 
#   configparser comma-delimited string.
#
def wingeoxlator(geostring,geovals,geolist):
        geostr = ''
        cnflist = []
        outstring = ''
        if geostring != '': # Convert tk.geometry() string to configparser string entry.
            cnflist = geostring.replace('x',' ')
            cnflist = cnflist.replace('+',' ')
            cnflist = cnflist.split()
            cnflist[2] = str(window.winfo_screenwidth() - int(cnflist[2])) # Take out screen dims.
            cnflist[3] = str(window.winfo_screenheight() - int(cnflist[3]))# Take out screen dims.
            confstr = str("{},{},{},{}".format(cnflist[0],cnflist[1],cnflist[2],cnflist[3]))
            return confstr
        if geovals != None: # Convert values list object to tk.geometry() string.
            outstring = geovals[0] + 'x' + geovals[1] + '+' + geovals[2] + '+' + geovals[3]
            return outstring
        if geolist != None: # Convert values list object to configparser string entry.
            geostr = str("{},{},{},{}".format(geolist[0],geolist[1],geolist[2],geolist[3]))
            return geostr

def getscalefactors():
#    confparse.read(mmc4wIni)
    wglst = confparse.get("default_values","maingeo").split(',') #  Get default values from mmc4w.ini.
    mainwingeo = window.geometry() #                                Get current window values 
    mwglist = wingeoxlator(mainwingeo,None,'').split(',') #            Send current to generate list.
    geogeo = wingeoxlator('',mwglist,'')
    wd_ratio = int(mwglist[0]) / int(wglst[0])
    ht_ratio = int(mwglist[1]) / int(wglst[1])
    scalef = str(wd_ratio) + ',' + str(ht_ratio) + ','
    confparse.set('display','scalefactors',scalef)
    confparse.set('display','displaysize',str(window.winfo_screenwidth()) + 'x' + str(window.winfo_screenheight()))
    confparse.set('mainwindow','maingeo',wingeoxlator('',None,mwglist))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def deletedebuglog():
    if os.path.isfile(path_to_dat / "mmc4w_DEBUG.log"):
        ddlsure = messagebox.askyesno("Delete Debug Log","Are you sure?")
        if ddlsure == True:
            try:
                os.remove(path_to_dat / "mmc4w_DEBUG.log")
                messagebox.showinfo("Debug Log Deleted","mmc4w_DEBUG.log has been removed.")
            except:
                messagebox.showinfo("File in Use","Toggle Logging before attempting to delete the log.")
    else:
        messagebox.showinfo("No Debug Log Found","The operating system reports no such file.")

def loadplsongs(song,album):
    connext()
    pls_on_srvr = []
    pl_without_sng = []
    pl_with_sng = []
    pls_on_srvr = client.listplaylists()
    for i in pls_on_srvr:
        plsongs = client.listplaylistinfo(i['playlist'])
        init = 0
        for s in plsongs:
            if song == s['title'] and album == s['album']:
                init = 1
        if init == 0:
            pl_without_sng.append(i['playlist'])
        if init == 1:
            pl_with_sng.append(i['playlist'])
    return pl_without_sng,pl_with_sng

def getoutputs():
    connext()
    outputs = []
    outputsraw = client.outputs()
    for thisop in outputsraw:
        if thisop['outputenabled'] == '1':
            openab = 'Enabled'
        else:
            openab = 'Disabled'
        outputs.append(str('ID: {} "{}" Status: {}'.format(thisop['outputid'],thisop['outputname'],openab)))
    return outputsraw,outputs

def connext():  ## Checks connection, then connects if necessary.
                # if no connection this program ends with error message
    global serverip,serverport
    try:
        client.ping()  # Use ping() to see if we're connected.
    except (musicpd.ConnectionError, ConnectionRefusedError,ConnectionAbortedError) as errvar:
        logger.debug("D1| Initial errvar: {}".format(errvar))
        if errvar == 'Already connected':
            pass
        else:
            try:
                logger.debug("D1| Try to reconnect to {} on port {}".format(serverip,serverport))
                client.connect(serverip, int(serverport))
                logger.debug('D1| 2nd try. cxstat is : ' + str(cxstat))
            except  (ValueError, musicpd.ConnectionError, ConnectionRefusedError,ConnectionAbortedError) as err2var:
                if err2var == 'Already connected':
                    pass
                if 'WinError' in str(err2var) or 'Not connected' in str(err2var):
                    messagebox.showinfo("Server Down","The server you selected is not responding. Edit mmc4w.ini to ensure the 'lastsrvr' IP address is for a running server.")
                    configurator("Double-check all the IP addresses. OK sends you to edit mmc4w.ini.")
                else:
                    logger.debug("D1| Second level errvar: {}".format(err2var))
                    endWithError("The server you selected is not responding.\nEdit mmc4w.ini to ensure the 'lastsrvr' IP address is for a running server.")
    return


def plrandom():  # Set random playback mode.
    global ran
    client.random(1)
    ran = 'R'
    text1['bg']='white'
    text1['fg']='black'

def plnotrandom():  # Set sequential playback mode.
    global ran
    client.random(0)
    ran = 'r'
    text1['bg']='navy'
    text1['fg']='white'

def halt():
    global endtime,buttonvar
    if buttonvar == 'pause':
        pause()
    connext()
    buttonvar = 'stop'
    client.stop()
    endtime = time.time()
    return buttonvar

def play():
    global buttonvar,prevbtnstate
    if buttonvar == 'pause':
        pause()
    else:
        connext()
        prevbtnstate = buttonvar
        buttonvar = 'play'
        client.play()
        getcurrsong()

def next():
    global buttonvar
    if buttonvar == 'pause':
        pause()
    else:
        connext()
    try:
        client.next()
    except musicpd.CommandError:
        client.play()
        client.next()
    getcurrsong()

def previous():
    global buttonvar
    if buttonvar == 'pause':
        pause()
    else:
        connext()
    try:
        client.previous()
    except musicpd.CommandError:
        client.play()
        client.previous()
    getcurrsong()

def pause2play():
    global pstate,endtime,pstart,buttonvar,pstart,pause_duration,dur,elap
    oldendtime = endtime
    endtime = time.time() + int(float(dur) - float(elap))
    logger.info('2) New endtime generated in pause(). Old: {}, New {}'.format(oldendtime,endtime))
    button_pause.configure(text='Pause',bg='gray90') ## 'systemButtonFace' is the magic word.
    pstate = 'play'
    buttonvar = 'play'
    pstart = 0 
    #                           ## Now client.pause() sets it to PLAY
def play2pause():
    global buttonvar,pstate,endtime,pstart
    pstart = time.time()
    buttonvar = 'pause'
    button_pause.configure(text='Resume',bg="orange")
    logger.info("0) Playback paused at {}.".format(pstart))
    pstate = 'pause'
    #                           ## Now client.pause() sets it to PAUSE

def pause():  # Pause is complicated because of time-keeping.
    global buttonvar,pstate,dur,elap
    logger.debug('Buttonvar state at button press: {}.'.format(buttonvar))
    cstat = getcurrstat()
    if buttonvar == 'pause':        ## SYSTEM WAS PAUSED
        if cstat["state"] == 'pause':
            dur = cstat['duration']
            elap = cstat['elapsed']
            pause2play()
            client.pause()
        if cstat['state'] == 'play':
            getcurrsong()
    elif buttonvar == 'play':         ## SYSTEM WAS PLAYING
        if cstat['state'] == 'pause':
            play2pause()
        if cstat["state"] == 'play':
            elap = cstat['elapsed']
            play2pause()
            connext()
            client.pause()
            # start timer here to check pstate after a time.
            if threading.active_count() < 3:
                t3 = threading.Thread(target=lambda: pausethreadtimer(cstat))
                t3.daemon = True
                t3.start()

def volup():
    global lastvol
    connext()
    vol_int = int(lastvol)
    vpre = lastvol[:]
    if vol_int < 100:
        client.volume(+5)
        vol_int = vol_int + 5
        volbtncolor(vol_int)


def voldn():
    global lastvol
    connext()
    vol_int = int(lastvol)
    if vol_int > 0:
        client.volume(-5)
        vol_int = vol_int - 5
        volbtncolor(vol_int)

def pausethreadtimer(cstat):
    global buttonvar
    songdur = float(cstat['duration'])
    songelap = float(cstat['elapsed'])
    leftover = int(songdur - songelap)
    for i in range(leftover,0,-1):
        time.sleep(1)
    logger.debug('PTT) PauseThreadedTimer ran down after {} seconds.'.format(leftover))
    getcurrsong()

def btnupdater(newstate):
    global buttonvar, endtime
    if newstate == 'pause':
        button_pause.configure(text='Pause',bg='orange')
        cstat = getcurrstat()
        ## Threaded timer during pause state.
        t2 = threading.Thread(target=lambda: pausethreadtimer(cstat))
        t2.daemon = True
        t2.start()
    if newstate == 'stop' and buttonvar == 'pause':
        button_pause.configure(bg='gray90')
        endtime = time.time()
    if newstate == 'play' and buttonvar == 'pause':
        pause2play()

def volbtncolor(vol_int):  # Provide visual feedback on volume buttons.
    global lastvol
    if lastvol != str(vol_int):
        connext()
        client.setvol(vol_int)
    lastvol = str(vol_int)
    logger.debug('Set volume to {}.'.format(vol_int))
    thisvol = vol_int
    upconf = colrVolume[thisvol]        # the up and down button paramaters
    button_volup.configure(text=upconf[0],bg=upconf[1],fg=upconf[2])
    button_voldn.configure(text=upconf[3],bg=upconf[4],fg=upconf[5])
    currvolconf = confparse.get('serverstats','lastvol')
    if lastvol != currvolconf:
        confparse.set('serverstats','lastvol',lastvol)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        logger.info('Saved volume to mmc4w.ini. lastvol is {}.'.format(lastvol))


def toglrandom():
    connext()
    ranstat =  client.status()
    if ranstat['random'] == '1':
        plnotrandom()
    else:
        plrandom()

def toglrepeat():
    global rpt
    connext()
    cstats = client.status()
    rptstat = cstats['repeat']
    if rptstat == '0':
        client.repeat(1)
        rpt = 'P'
        msg = 'Repeat is set to ON.'
    else:
        client.repeat(0)
        rpt = 'p'
        msg = 'Repeat is set to OFF.'
    displaytext1(msg)

def toglconsume():
    global con
    connext()
    cstats = client.status()
    cnsmstat = cstats['consume']
    if cnsmstat == '0':
        client.consume(1)
        con = 'C'
        msg = 'Consume is set to ON.'
    else:
        client.consume(0)
        con = 'c'
        msg = 'Consume is set to OFF.'
    displaytext1(msg)

def toglsingle():
    global sin
    connext()
    cstats = client.status()
    snglstat = cstats['single']
    if snglstat == '0':
        client.single(1)
        sin = 'S'
        msg = 'Single is set to ON.'
    else:
        client.single(0)
        sin = 's'
        msg = 'Single is set to OFF.'
    displaytext1(msg)

def dbupdate():
    connext()
    cludrtn = client.update()
    logger.info("99) Ran client.update(). Returned {}".format(cludrtn))
#
##  DEFINE getcurrsong() - THE MOST POPULAR FUNCTION HERE.
#
def getcurrsong():
    global globsongtitle,endtime,aatgl,sent,pstate,elap,firstrun,prevbtnstate,lastvol,buttonvar,ran,rpt,sin,con,artw,lastpl
    connext()
    if threading.active_count() < 2:
        logger.debug("D9| The threading.active_count() dropped below 2. Quitting.")
        exit()
    logger.info(' = = = = = = getcurrsong = = = = = = = = ')
    logger.debug("D2| Sent: {}".format(sent))
    gsent = sent
    gpstate = ''
    cs = []
    stat = []
    stat = client.status()
    if stat['random'] == '0':
        ran = 'r'
        text1['bg']='navy'
        text1['fg']='white'
    else:
        ran = 'R'
        text1['bg']='white'
        text1['fg']='black'
    if stat['repeat'] == '1':
        rpt = 'P'
    else:
        rpt = 'p'
    if stat['single'] == '1':
        sin = 'S'
    else:
        sin = 's'
    if stat['consume'] == '1':
        con = 'C'
    else:
        con = 'c'
    logger.debug('D2| Got status. state: {}, rand: {}, rpt: {}.'.format(stat['state'],ran,rpt))
    newstate = stat['state']
    btnupdater(newstate)
    buttonvar = newstate
    logger.debug('D2| Retrieving "cs" in getcurrsong().')
    cs = client.currentsong()
    logger.debug('D2| Got cs (client.currentsong()) with a length of {}.'.format(len(cs)))
    if cs == {}:
        client.stop()
        buttonvar = 'stop'
        aart = artWindow(0)
        if aatgl == '1':
            artw.aartLabel.configure(image=aart)
        globsongtitle = "No song in the queue. Go find one."
        lastpl = confparse.get('serverstats','lastsetpl')
        plrandom()
    else:
        msg,gendtime = getendtime(cs,stat)
        if cs['album'] != lastpl:
            lastpl = confparse.get('serverstats','lastsetpl')
        logger.debug('D2| Headed to getaartpic(**cs).')
        getaartpic(**cs)
        aart = artWindow(aartvar)
        if aatgl == '1':
            artw.aartLabel.configure(image=aart)
        if 'volume' in stat:
            lastvol = stat['volume']
            vol_fives = int( (float(lastvol)+3) /5 )         # map 0-100 to range of 0-20
            vol_int = int(vol_fives * 5)                    # and back to 0-100
            volbtncolor(vol_int)
            logger.info('3) Volume is {}, Random is {}, Repeat is {}.'.format(lastvol,stat['random'],stat['repeat']))
        gpstate = stat['state']
        logger.info('3) {}.'.format(msg))
        globsongtitle = msg
        if firstrun != '1' and prevbtnstate != 'stop':
            if msg != confparse.get('serverstats','lastsongtitle'):
                gsent = 0
                logger.info("4) This is a new title. Writing title to mmc4w.ini.")
                confparse.set("serverstats","lastsongtitle",str(msg))
                with open(mmc4wIni, 'w') as SLcnf:
                    confparse.write(SLcnf)
            else:
                logger.info("4) This title is still playing or just finished. Modifying endtime based on dur-elap.")
                gendtime = time.time() + (float(dur)-float(elap))
                gsent = 0
                logger.info("5) gendtime returned to {}. Remaining is {}.".format(gendtime,(float(cs['duration'])-float(elap))))
                if float(cs['duration']) == 0.00:
                    next()
        else:
            logger.info("4) This is the last song you played during your last session.")
        logger.debug('D7| lastvol: {}, gendtime: {}, gpstate: {}, gsent {}.'.format(lastvol,gendtime,gpstate,gsent))
        endtime = gendtime
        pstate = gpstate
        sent = gsent
        prevbtnstate = 'play'
        if threading.active_count() < 2:
            logger.debug("D10| The threading.active_count() dropped below 2. Quitting.")
            exit()
        if pstate == 'stop' or pstate == 'pause':
            logger.info("6) pstate: {}.".format(pstate))
        bpltgl = confparse.get('program','buildmode')
        if bpltgl == '1':
            pls_without_song,pls_with_song = loadplsongs(cs['title'],cs['album'])
            bplwin.listbx.delete(0,tk.END)
            bplwin.listvar.set(pls_with_song)
            bplwin.listbx2.delete(0,tk.END)
            bplwin.listvar2.set(pls_without_song)
    return cs
#
#
def getendtime(cs,stat):
    global dur,elap
    msg = ""
    dur = cs['duration']
    trk = cs['track'].zfill(2)
    if 'elapsed' in stat:
        elap = stat['elapsed']
    remaining = float(dur) - float(elap)
    gendtime = time.time() + remaining
    logger.info('1) endtime generated: {}. Length: {}, Song dur: {}, Elapsed: {}.'.format(gendtime,int(gendtime - time.time()),dur,elap))
    msg = str(trk + '-' + cs["title"] + " - " + cs["artist"])
    return msg,gendtime
#
#
def getaartpic(**cs):
    global aatgl,aartvar
    eadict = {}
    fadict = {}
    eadict = client.readpicture(cs['file'],0)
    if len(eadict) > 0:
        size = int(eadict['size'])
        done = int(eadict['binary'])
        with open(path_to_dat / "cover.png", 'wb') as cover:
            cover.write(eadict['data'])
            while size > done:
                eadict = client.readpicture(cs['file'],done)
                done += int(eadict['binary'])
                cover.write(eadict['data'])
        logger.debug('D6| Wrote {} bytes to cover.png.  len(eadict) is: {}'.format(done,len(eadict)))
        aartvar = 1
    elif len(eadict) == 0:
        try:
            fadict = client.albumart(cs['file'],0)
            if len(fadict) > 0:
                received = int(fadict.get('binary'))
                size = int(fadict.get('size'))
                with open(path_to_dat / "cover.png", 'wb') as cover:
                    cover.write(fadict.get('data'))
                    while received < size:
                        fadict = client.albumart(cs['file'], received)
                        cover.write(fadict.get('data'))
                        received += int(fadict.get('binary'))
                logger.debug('D6| Wrote {} bytes to cover.png.  len(fadict) is: {}'.format(received,len(fadict)))
                aartvar = 1
            else:
                aartvar = 0
        except musicpd.CommandError:
            aartvar = 0
            pass
    else:
        aartvar = 0
    if aatgl == '1':
        logger.info('2) Bottom of getaartpic(). Headed to artWindow(). aartvar is {}, len(eadict) is {}, len(fadict) is {}.'.format(aartvar,len(eadict),len(fadict)))

        artWindow(aartvar)
    else:
        logger.debug('D6| aartvar is: {}, len(eadict) is {}, len(fadict) is {}.'.format(aartvar,len(eadict),len(fadict)))
#
## songtitlefollower() is the threaded timer.
#
def songtitlefollower():

    logger.info("---=== Start songtitlefollower() threaded timer. ===---")
    logger.info(" ")
    global endtime,sent,pstate,pstart,pause_duration,elap
    sent = 0
    pstate = 'stop'
    thisendtime = endtime
    while True:
        if threading.active_count() > 3:
            logger.info("There are {} threads now.".format(threading.active_count()))
        sleep(.2)
        if pstate != 'stop' and pstate != 'pause':
            if endtime != thisendtime:
                logger.info("5) Threaded timer got new endtime.")
                thisendtime = endtime
                logger.info("6) New endtime: {}, Length: {}. sent: {}.".format(thisendtime,int(thisendtime - time.time()),sent))
            if thisendtime <= time.time() and sent == 0:
                logger.info("0) Threaded timer ran down. Getting new current song data.")
                sent = 1
                logger.debug("D0| time.time() reached endtime. Calling getcurrsong().")
                logger.info(" - - - - -  songtitlefollower - - - - - - ")
                getcurrsong()

def configurator(confmsg):
    if confmsg == '':
        confmsg = "OK closes the app and opens mmc4w.ini for editing."
    proceed = messagebox.askokcancel("Edit Config File",confmsg)
    if proceed == True:
        if sys.platform == "win32":
            os.startfile(mmc4wIni)
        else:
            subprocess.run(["xdg-open", mmc4wIni])
        sleep(1)
        exit()
    else:
        sys.exit()

def logtoggler():
#    confparse.read(mmc4wIni)
    logtog = confparse.get("program","logging")
    loglevel = confparse.get("program","loglevel")
    if logtog.upper() == "ON":
        newlog = "off"
        confparse.set('program','logging',newlog)
    elif logtog.upper() == 'OFF':
        newlog = "on"
        confparse.set('program','logging',newlog)
    logger.debug("{}. Wrote to .ini file.".format(newlog))
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    messagebox.showinfo("Logging Toggled","Logging is now " + newlog + ".\nLogging level is " + loglevel + ".\nExiting. Restart to refresh config.")
    exit()

def getcurrstat():
    connext()
    try:
        cstat = client.status()
    except musicpd.ProtocolError as mproterr:
        logger.info('Caught a ProtocolError at getcurrstat(): {}'.format(mproterr))
        cstat = {}
        connext()
        cstat = client.status()
    return cstat

def plupdate():
    global lastpl,firstrun
    connext()
    cpl = client.listplaylists()
    if len(cpl) > 0:
        pl = ""
        for plv in cpl:
            pl = plv['playlist'] + "," + pl
        confparse.read(mmc4wIni)
        lastpl = confparse.get("serverstats","lastsetpl")
        confparse.set("serverstats","playlists",str(pl))
        if lastpl == '':
            confparse.set('serverstats','lastsetpl',cpl[0]['playlist'])
            lastpl = 'Select a saved playlist. "Look" menu.' # a backup strategy. 'Joined Server Queue' is primary.
        if firstrun == '1':
            confparse.set('basic','firstrun','0')
            firstrun = '0'
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
    else:
        plquestion = messagebox.askyesno("No PlayList Found","The MPD server shows no saved playlist."
                                         "\nEither click 'Yes' to let MMC4W create an 'Everything' list"
                                         "\nor click 'No' to create a new empty one.\n'Yes' is recommended.")
        if plquestion == True:
            makeeverything()
        else:
            createnewpl()

def displaytext1(msg):
    text1.delete("1.0", 'end')
    text1.insert("1.0", msg)

def displaytext2(msg2):
    text1.insert(tk.END, msg2)

def albarttoggle():
    global aatgl,artw,aartvar
    connext()
#    confparse.read(mmc4wIni)
    aatgl = confparse.get("albumart","albarttoggle")
    if aatgl == '1':
        try:
            artw.destroy()
            aatgl = '0'
        except (AttributeError,NameError,tk.TclError):
            pass
    else:
        aatgl = '1'
        try:
            cs = client.currentsong()
            aadict = client.readpicture(cs['file'],0)
            if len(aadict) > 0:
                aartvar = 1
            else:
                aartvar = 0
            aart = artWindow(1)  ## artWindow now returns aart ready for use.
            artw = TartWin(window, "AlbumArt",artwinilist,aart) # new window instance.
            if tbarini == '0':
                artw.overrideredirect(True)
        except (ValueError,KeyError):
            aartvar = 0
            artWindow(aartvar)
            pass
    confparse.set("albumart","albarttoggle",aatgl)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def savesrchwinstats(wintype):
    global tsbinilist
    if tk.Toplevel.winfo_exists(wintype):
        swingeo = wintype.geometry()
        srchstr = wingeoxlator(swingeo,None,None)
        confparse.set("searchwin","swingeo",srchstr)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        wintype.destroy()
        if sys.platform != 'win32':
            tbstatus = window.overrideredirect()
            if tbstatus == True:
                tbtoggle()
                sys.exit()
        if aatgl == '1':
            artw.aartLabel.configure(image=aart)
        tsbinilist = maketsbinilist()

def savebplwinstats():
    bplwingeo = bplwin.geometry()
    bplstr = wingeoxlator(bplwingeo,None,None)
    confparse.set("buildplwin","bplwingeo",bplstr)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)

def savewinstats():
    mainwingeo = window.geometry()
    mwstr = wingeoxlator(mainwingeo,None,None)
    confparse.set("mainwindow","maingeo",mwstr)
    if artw is not None:
        if tk.Toplevel.winfo_exists(artw):
            artwingeo = artw.geometry()
            aawstr = wingeoxlator(artwingeo,None,None)
            aawl = aawstr.split(',')
            aawl[0] = aawl[1]
            aawstr = wingeoxlator('',None,aawl)
            confparse.set("albumart","aartgeo",aawstr)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    if aatgl == '1':
        global artwinilist
#        confparse.read(mmc4wIni)
        artwinilist = makeartwinilist()
        aart = artWindow(aartvar)
        artw.aartLabel.configure(image=aart)
        artw.update()

def tbtoggle():
    global aatgl
    tbstatus = window.overrideredirect()
    if tbstatus == None or tbstatus == False:  # Titlebar is visible, NOT overridden.
        savewinstats()
        window.overrideredirect(1) #             Override it. Turn it OFF.
        if aatgl == '1':
            artw.overrideredirect(1)
        confparse.set("mainwindow","titlebarstatus",'0')  # Set Titlebar status off (overridden)
    else: #                               When Titlebar is NOT visible, it is overridden.
        window.overrideredirect(0) #           Disable Override. Turn titlebar ON.
        if aatgl == '1':
            artw.overrideredirect(0)
        confparse.set("mainwindow","titlebarstatus",'1')  # Set Titlebar status ON (not overridden)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    if sys.platform != 'win32':
        sys.exit()
    else:
        getcurrsong()

def returntoPL():
    global lastpl
    connext()
#    confparse.read(mmc4wIni)
    lastpl = confparse.get("serverstats","lastsetpl")
    client.clear()
    try:
        client.load(lastpl)
    except musicpd.CommandError:
        logger.info('R2PL) The last playlist loaded is not available. Select new one.')
        PLSelWindow()

def resetwins():
#    confparse.read(mmc4wIni)
    aartwin_x = confparse.get("default_values","aartgeo")
    win_x = confparse.get("default_values","maingeo")
    bwinx = confparse.get("default_values","bplwingeo")
    swinx = confparse.get("default_values","swingeo")
    confparse.set("mainwindow","maingeo",win_x)
    confparse.set("albumart","aartgeo",aartwin_x)
    confparse.set("buildplwin","bplwingeo",bwinx)
    confparse.set("searchwin","swingeo",swinx)
    logger.info('Reset window positions & sizes to defaults from mmc4w.ini file.')
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    sys.exit()

def applyscalefactors():
#    confparse.read(mmc4wIni)
    sf = confparse.get("display","scalefactors")
    sf = sf.split(',')
    sfx = float(sf[0])
    sfy = float(sf[1])
    winvarnames = ['aartgeo','bplwingeo','swingeo']
    for i in winvarnames:
        w = confparse.get("default_values",i)
        w = w.split(',')
        w[0] = str(int(float(w[0])*sfx))
        w[1] = str(int(float(w[1])*sfy))
        wx = wingeoxlator('',None,w)
        if i == 'aartgeo':
            confparse.set("albumart","aartgeo",wx)
        if i == 'bplwingeo':
            confparse.set("buildplwin","bplwingeo",wx)
        if i == 'swingeo':
            confparse.set("searchwin","swingeo",wx)
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    sys.exit()

def nonstdport():
    messagebox.showinfo("Setting a non-standard port","Set your non-standard port by editing the mmc4w.ini file. Use the Configure option in the File menu.\n\nPut your port number in the 'serverport' attribute under the [basic] section. 6600 is the default MPD port.")

def endWithError(msg):
    messagebox.showinfo("UhOh",msg)
    sys.exit()

def exit():
    if confparse.get('program','buildmode') == '1':
        buildpl()
    logger.info("EXIT) Connections closed. Playback not affected. Quitting.")
    sys.exit()


client.timeout = None                     # network timeout in seconds (floats allowed), default: None
client.idletimeout = None               # timeout for fetching the result of the idle command is handled seperately, default: None
artw = None
globsongtitle = ""
aatgl = '0'

def makeeverything():
    connext()
    client.clear()
    pllist = client.listplaylists()
    if 'Everything' in str(pllist):
        client.rm('Everything')
    client.add('/')
    client.save('Everything')
    logger.info('The playlist named "Everything" was just updated.')
    PLSelWindow()
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
##  tk.END ERROR MESSAGEBOX SECTION
#
## WRAP UP AND DISPLAY ==========================================================================================
#
##  THIS IS THE 'ROOT' WINDOW.  IT IS NAMED 'window' rather than 'root'.  ##
# window = FaultTolerantTk()  # Create the root window with abbreviated error messages in popup.
window = tk.Tk()  # Create the root window with errors in console, invisible to Windows.
window.title("Minimal MPD Client " + version)  # Set window title
#confparse.read(mmc4wIni)  # get parameters from config .ini file.
if confparse.get("basic","firstrun") == '1':
    wglst = confparse.get("default_values","maingeo").split(',')
else:
    wglst = confparse.get("mainwindow","maingeo").split(',')
tbarini = confparse.get("mainwindow","titlebarstatus")  # get titlebar status. 
wglst[2] = str(int(window.winfo_screenwidth() - (int(wglst[2])))) # compensate for screen width
wglst[3] = str(int(window.winfo_screenheight() - (int(wglst[3]))))
window.geometry(wingeoxlator('',wglst,'')) # send wglst to generate tk.geometry() string.
window.config(background='white')  # Set window background color
window.columnconfigure([0,1,2,3,4], weight=0)
window.rowconfigure([0,1,2], weight=1)
if firstrun == '0' and tbarini == '0':
    window.overrideredirect(1)
nnFont = Font(family="Segoe UI", size=10, weight='bold')          ## Set the base font
main_frame = tk.Frame(window, )
main_frame.grid(column=0,row=0,padx=2)
main_frame.columnconfigure([0,1,2,3,4], weight=1)
if sys.platform == "win32":
    window.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico") # Windows
else:
    iconpng = tk.PhotoImage(file = path_to_dat / "ico/mmc4w-ico.png") # Linux
    window.iconphoto(False, iconpng) # Linux
confparse.set('display','displaysize',str(window.winfo_screenwidth()) + ',' + str(window.winfo_screenheight()))
with open(mmc4wIni, 'w') as SLcnf:
    confparse.write(SLcnf)
window.update()
#
##
#
quewinhelptext = ["All commands end with a semicolon.","Use 'q;' to exit.","Use 'keys;' for a list of valid search keys.",
                   "Use 'savewin;' to save window location and size.","Use 'key:value' to search.",
                   "    Ex: artist:john or title:greatest.","A word or phrase with no ':' defaults to a title search."]
#
## DEFINE THE QUEUE WINDOW
#
def queuewin(qwaction):
    global findit,dispitems,tsbinilist,lastpl
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    def qwclicked(event):
        global findit,dispitems
        connext()
        t = queuewin.listbx.curselection()[0]
        clikd = dispitems[t].split(" | ")
        for m in findit:
            if clikd[0] == m['artist'] and clikd[1] == m['title'] and clikd[2] == m['album']:
                playit = m['pos']
        client.play(playit)
        getcurrsong()
        lastpl = confparse.get('serverstats','lastsetpl')
        queuewin.destroy()
    ## The tk.Entry box runs this upon <Return>
    def pushret(event):
        global findit,dispitems
        connext()
        srchterm = editing_item.get().replace('Search: ','')
        valid_list = ['file','title','artist','album','genre','date']
        editing_item.set('Search: ')
        if srchterm.upper() == "HELP;":
            queuewin.listbx.delete(0,tk.END)
            queuewin.listbx.update()
            queuewin.listvar.set(quewinhelptext)
        if srchterm.upper() == "SAVEWIN;":
            savesrchwinstats(queuewin)
        if srchterm.upper() == "KEYS;":
            findit = valid_list
            dispitems = []
            for f in findit:
                dispitems.append(f)
            queuewin.listbx.delete(0,tk.END)
            queuewin.listbx.update()
            queuewin.listvar.set(dispitems)
        ifnot = ['Q;','SAVEWIN;','KEYS;','HELP;']
        if srchterm.upper() not in ifnot:
            if ":" in srchterm:
                fullsearch = srchterm.split(":")
                category = fullsearch[0]
                srchstr = fullsearch[1]
                if category in valid_list:
                    findit = client.playlistsearch(category,srchstr)
                else:
                    category = 'artist'
            else:
                category = 'title'
                srchstr = srchterm
                findit = client.playlistsearch(category,srchstr)
            if len(findit) > 0:
                dispitems = []
                queuewin.listbx.delete(0,tk.END)
                queuewin.listbx.update()
                if len(findit) == 0:
                    findit = client.playlistinfo()
                    category = 'title'
                findit.sort(key=lambda x: x[category])
                for f in findit:
                    thisfrec = f['artist'] + ' | ' + f['title'] + ' | ' + f['album'] + ' | ' + f[category]
                    dispitems.append(thisfrec)
                queuewin.listbx.delete(0,tk.END)
                queuewin.listbx.update()
                queuewin.listvar.set(dispitems)
        if srchterm.upper() == 'Q;':
            queuewin.destroy()
            if aatgl == '1':
                aart = artWindow(aartvar)
                artw.aartLabel.configure(image=aart)
    queuewin = TlSbWin(window, "Search the Queue or 'help;'",tsbinilist)
    connext()
    dispitems = []
    findit = client.playlistinfo()
    for f in findit:
        thisfrec = f['artist'] + ' | ' + f['title'] + ' | ' + f['album']
        dispitems.append(thisfrec)
    #     dispitems.sort()
    queuewin.listvar.set(dispitems)
    ## Feeds into select()
    editing_item = tk.StringVar()
    entry = tk.Entry(queuewin, textvariable=editing_item, width=tsbinilist[2])
    entry.grid(row=6,column=1,columnspan=5,sticky='NSEW')
    entry.insert(0,'Search: ')
    entry.bind('<Return>', pushret)
    entry.focus_set()
    queuewin.listbx.bind('<<ListboxSelect>>', qwclicked)
#
##
#
lookupwinhelptext = ["All commands end with a semicolon.","Use 'q;' to exit.","Use 'keys;' for a list of valid search keys.",
                   "Use 'savewin;' to save window location and size.","Use 'key:value' to search.",
                   "    Ex: artist:john or title:greatest."]
#
## DEFINE THE LOOKUP WINDOW AND ASSOCIATED FUNCTIONS
#
def lookupwin(lookupT):
    logger.info('Opened {} search window.'.format(lookupT))
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    def clickedit(event):
        global lastpl, itemsraw
        connext()
        i = plsngwin.listbx.curselection()[0]
        if lookupT == 'album':
            albsngs = client.search(lookupT,str(itemsraw[i]['album']))
            ## We turn rePeat and Random mode off for albums. ##
            client.repeat(0)
            rstat = client.status()['random']
            if rstat == '1':
                client.random(0)
                text1['bg']='navy'  # True Blue album mode
                text1['fg']='white' 
            client.clear()
            for s in albsngs:
                client.add(s['file'])
            lastpl = str(itemsraw[i]['album'])
            play()
        else:
            client.repeat(0)
            client.clear()
            client.add(itemsraw[i]['file'])
            lastpl = confparse.get('serverstats','lastsetpl')
            logger.info('Repeat turned OFF, queue cleared, added {}.'.format(itemsraw[i]['file']))
            play()
        plsngwin.update()
        plsngwin.destroy()
    ## The tk.Entry box runs this upon <Return>
    def pushret(event,lookupT):
        global itemsraw
        connext()
        dispitems = []
        srchterm = editing_item.get().replace('Search: ','')
        valid_list = ['file','title','artist','album','genre','date']
        editing_item.set('Search: ')
        if srchterm.upper() == "HELP;":
            luwhtplus = lookupwinhelptext.copy()
            luwhtplus.append("A word or phrase with no ':' defaults to a " + lookupT + " search.")
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listbx.update()
            plsngwin.listvar.set(luwhtplus)
            luwhtplus = []
        if srchterm.upper() == "SAVEWIN;":
            savesrchwinstats(plsngwin)
        if srchterm.upper() == "KEYS;":
            findit = valid_list
            dispitems = []
            for f in findit:
                dispitems.append(f)
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listbx.update()
            plsngwin.listvar.set(dispitems)
        if srchterm.upper() == "Q;":
            plsngwin.destroy()
            window.mainloop()
        if srchterm.upper() == 'STATUS;':
            stats = client.status()
            for s,v in stats.items():
                dispitems.append(s + ' : ' + v)
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listbx.update()
            plsngwin.listvar.set(dispitems)
        if srchterm.upper() == 'STATS;':
            stats = client.stats()
            for s,v in stats.items():
                if s == 'db_playtime':
                    v = int(v)
                    v = str(datetime.timedelta(seconds=v))
                if s == 'uptime' or s == 'playtime':
                    v = int(v)
                    v = str(datetime.timedelta(seconds=v))
                if s == 'db_update':
                    v = int(v)
                    v = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(v))
                dispitems.append(s + ' : ' + v)
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listbx.update()
            plsngwin.listvar.set(dispitems)
        ifnot = ['STATUS;','SAVEWIN;','STATS;','HELP;','KEYS;','Q;']
        if srchterm.upper() not in ifnot:
            if ":" in srchterm:
                fullsearch = srchterm.split(":")
                lookupT = fullsearch[0]
                srchterm = fullsearch[1]
            dispitems = []
            itemsraw = []
            findit = client.search(lookupT,srchterm)
            lastf = ''
            for f in findit:
                thisf = '"'+f['title'] + ' - ' + f['artist'] + ' | ' + f['album']+'"'
                thisfrec = dict([('song',thisf), ('file',f['file']),('album',f['album'])])
                itemsraw.append(thisfrec)
            for sng in itemsraw:
                dispitems.append(sng['song'])
            plsngwin.listbx.delete(0,tk.END)
            plsngwin.listbx.update()
            plsngwin.listvar.set(dispitems)
            # if srchterm.upper() == 'Q;':
            #     plsngwin.destroy()
#    confparse.read(mmc4wIni)  # get parameters from config .ini file.
    plsngwin = TlSbWin(window, "Search & Play by " + lookupT + " or 'help;'", tsbinilist)
    itemsraw = []
    dispitems = []
    editing_item = tk.StringVar()
    entry = tk.Entry(plsngwin, textvariable=editing_item, width=tsbinilist[2])
    entry.grid(row=6,column=1,columnspan=5,sticky='NSEW')
    entry.insert(0,'Search: ')
    entry.bind('<Return>', lambda event: pushret(event,lookupT))
    entry.focus_set()
    plsngwin.listbx.bind('<<ListboxSelect>>', clickedit)
#
## DEFINE THE ADD-SONG-TO-PLAYLIST WINDOW
#
def addtoplclicked(event):
    connext()
    cs = client.currentsong()
    pls_without_song,pls_with_song = loadplsongs(cs['title'],cs['album'])
    selectedlst2 = bplwin.listbx2.curselection()[0]
    logger.info('A2PL) Added "{}" to "{}".'.format(cs['title'],pls_without_song[selectedlst2]))
    client.playlistadd(pls_without_song[selectedlst2],cs['file'])
    window.focus_force()
    pls_without_song,pls_with_song = loadplsongs(cs['title'],cs['album'])
    bplwin.listbx.delete(0,tk.END)
    bplwin.listvar.set(pls_with_song)
    bplwin.listbx2.delete(0,tk.END)
    bplwin.listvar2.set(pls_without_song)
    if aatgl == '1':
        aart = artWindow(aartvar)  ## artWindow prepares the image, 'configs' the Label and returns image as well.
        artw.aartLabel.configure(image=aart)
#
##
#
def delfromplclicked(event):
    connext()
    cs = client.currentsong()
    pls_without_song,pls_with_song = loadplsongs(cs['title'],cs['album'])
    selectedlst = bplwin.listbx.curselection()[0]
    pldata = client.listplaylistinfo(pls_with_song[selectedlst])
    for x in enumerate(pldata):
        if x[1]['title'] == cs['title']:
            thesong = x[0]
    logger.info('DELCUR) Deleting "{}", song number {} from "{}".'.format(cs['title'],thesong,pls_with_song[selectedlst]))
    client.playlistdelete(pls_with_song[selectedlst],thesong)
    window.focus_force()
    pls_without_song,pls_with_song = loadplsongs(cs['title'],cs['album'])
    bplwin.listbx.delete(0,tk.END)
    bplwin.listvar.set(pls_with_song)
    bplwin.listbx2.delete(0,tk.END)
    bplwin.listvar2.set(pls_without_song)
    if aatgl == '1':
        aart = artWindow(aartvar)  ## artWindow prepares the image, 'configs' the Label and returns image as well.
        artw.aartLabel.configure(image=aart)
#
##
#
def addtopl(plaction):
    ## The tk.Listbox runs this upon click (<<ListboxSelect>>)
    plupdate()
    def plclickedit(event):
        global lastpl
        selectlst = a2plwin.listbx.curselection()[0]
        pllist = cp.getlist('serverstats','playlists')
        connext()
        if plaction == 'remove':
            pllist = cp.getlist('serverstats','playlists')
            doublecheck = messagebox.askyesno(message='Are you sure you want to PERMANENTLY delete \n"{}"?'.format(pllist[selectlst]))
            if doublecheck == True:
                client.rm(pllist[selectlst])
                logger.info("RMPL) Playlist '{}' removed.".format(pllist[selectlst]))
                plupdate()
        a2plwin.update()
        a2plwin.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    def songlistclick(event):
        songsel = a2plwin.listbx.curselection()[0]
        logger.debug("ATPL) Playlist '{}' was listed in addtopl().".format(lastpl))
        logger.debug("ATPL) '{}' was selected to play.".format(songlist[songsel].split('/')[2]))
        connext()
        client.play(songsel)
        cs = getcurrsong()
        a2plwin.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    if plaction == 'list':
        a2title = "List {} - Play Selected".format(lastpl)
    if plaction == 'remove':
        a2title = "Delete the Selected Playlist"
    a2plwin = TlSbWin(window, a2title, tsbinilist)
    a2plwin.configure(bg='black')
    if plaction == 'remove':
        a2plwin.listbx.bind('<<ListboxSelect>>', plclickedit)
        cp.read(mmc4wIni)
        pllist = cp.getlist('serverstats','playlists')
        for lst in pllist:
            a2plwin.listbx.insert(tk.END,lst)
    if plaction == 'list':
        a2plwin.listbx.bind('<<ListboxSelect>>', songlistclick)
        thislist = confparse.get('serverstats','lastsetpl')
        connext()
        songlist=[]
        if thislist == 'Joined Server Queue':
            songlistq = client.playlistinfo()
            for s in songlistq:
                songlist.append(s['file'])
            logger.info('ATPL) Listed queue songs. Saved PL not known.')
        else:
            songlist = client.listplaylist(thislist)
            logger.info('ATPL) Listed songs from {}.'.format(thislist))
        for s in songlist:
            a2plwin.listbx.insert(tk.END,s)
#
## DEFINE THE SERVER SELECTION WINDOW
#
def SrvrWindow(swaction):
    global serverip,firstrun,lastpl, cp
#    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    if swaction == 'server':
        srvrwtitle = "Servers"
    if swaction == 'output':
        srvrwtitle = "MPD Server Outputs"
    srvrw = TlSbBWin(window, srvrwtitle, tsbinilist)
    def rtnplsel(ipvar):
        global serverip,firstrun,lastpl
        client.close()
        selection = srvrw.listbx.curselection()[0]
        msg = ipvar
        displaytext1(msg)
        serverip = iplist[selection]
#        confparse.read(mmc4wIni)
        connext()
        confparse.set("serverstats","lastsrvr",serverip)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        # srvrw.destroy()
        logger.debug("serverip: {}".format(serverip))
        lastpl = 'Joined Server Queue'
        confparse.set('serverstats','lastsetpl',lastpl)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        logger.info('0) Connected to server {}.'.format(serverip))
        getcurrsong()

    def outputtggl(outputvar):
        selection = srvrw.listbx.curselection()[0]
        outputs = getoutputs()[1]
        oid = outputs[selection][4:5]
        client.toggleoutput(oid)
        logger.info('0) Output [{}] toggled to opposite state.'.format(outputvar))
        outputs = getoutputs()[1]
        srvrw.listbx.delete(0,tk.END)
        srvrw.listbx.update()
        srvrw.listvar.set(outputs)
        # srvrw.destroy()
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
    if swaction == 'server':
        srvrw.listbx.bind('<<ListboxSelect>>', rtnplsel)
#        cp.read(mmc4wIni)
        iplist = cp.getlist('basic','serverlist')
        srvrw.listbx.delete(0,tk.END)
        srvrw.listbx.update()
        srvrw.listvar.set(iplist)
    if swaction == 'output':
        srvrw.listbx.bind('<<ListboxSelect>>', outputtggl)
        outputs = getoutputs()[1]
        srvrw.listbx.delete(0,tk.END)
        srvrw.listbx.update()
        srvrw.listvar.set(outputs)
#
## DEFINE THE PLAYLIST SELECTION WINDOW
#
def PLSelWindow():
    global serverip,lastpl, aartvar,aatgl,tsbinilist
    plupdate()
    cp = ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    plswtitle = "PlayLists"
    plsw = TlSbWin(window, plswtitle, tsbinilist)
    def rtnplsel(plvar):
        global serverip,lastpl
        selection = plsw.listbx.curselection()[0]
        plvar = pllist[selection]
        displaytext1(plvar)
        logger.info('PLSel) Set playlist to "{}".'.format(plvar))
        loadit = messagebox.askyesno("Load Playlist Now?","Load it now?\n'No' will remember your selection\nwithout replacing the queue.")
        if loadit == True:
            client.clear()
            client.load(plvar)
#        confparse.read(mmc4wIni)
        confparse.set("serverstats","lastsetpl",plvar)
        with open(mmc4wIni, 'w') as SLcnf:
            confparse.write(SLcnf)
        lastpl = plvar
        plsw.destroy()
        sleep(1)
        if aatgl == '1':
            aart = artWindow(aartvar)
            artw.aartLabel.configure(image=aart)
#    cp.read(mmc4wIni)
    pllist = cp.getlist('serverstats','playlists')
    lastpl = confparse.get("serverstats","lastsetpl")
    plsw.listbx.bind('<<ListboxSelect>>', rtnplsel)
    plsw.listbx.delete(0,tk.END)
    plsw.listbx.update()
    plsw.listvar.set(pllist)
    
#
## DEFINE THE ABOUT WINDOW
#
def aboutWindow():
    aw = tk.Toplevel(window)
    aw.title("About MMC4W " + version)
#    confparse.read(mmc4wIni)
    sf = confparse.get("display","scalefactors")
    sf = sf.split(',')
    sfx = float(sf[0])
    sfy = float(sf[1])
    awinWd = int(float(400) * sfx) # Set window size. x = y. Square.
    x_Left = int(window.winfo_screenwidth() / 2 - awinWd / 2)
    y_Top = int(window.winfo_screenheight() / 2 - awinWd / 2)
    aw.config(background="white")  # Set window background color
    aw.geometry(str(awinWd) + "x" + str(awinWd) + "+{}+{}".format(x_Left, y_Top))
    if sys.platform == "win32":
        aw.iconbitmap(path_to_dat / "ico/mmc4w-ico.ico")
    else:
        aw.iconphoto(False, iconpng) # Linux
    aw.columnconfigure(0, weight=1)
    aw.rowconfigure(0, weight=0)
    aw.rowconfigure(1, weight=0)
    aw.rowconfigure(2, weight=0)
    awlabel = tk.Label(aw, bg="white", font=18, text ="Putting the Music First")
    awlabel.grid(column=0, row=1, sticky="n")  # Place label in grid
    aboutText = tk.Text(aw, height=int(float(20)*(sfy/.056)), width=170, bd=3, padx=10, pady=10, wrap=tk.WORD, font=nnFont)
    # aboutText = tk.Text(aw, bd=3, padx=10, pady=10, wrap=tk.WORD, font=nnFont)
    aboutText.grid(column=0, row=2, sticky="s")
    aboutText.tag_configure("center", justify='center')
    aboutText.insert( tk.INSERT, "\n\nMMC4W is installed on a "+ sys.platform + " computer at:\n\n" + str(path_to_dat) + "\n"
                     "\nMMC4W is a minimally invasive client for MPD.  It does nothing by itself, but if you have one or more MPD servers "
                     "on your network, you might like this.\n\nThis little app holds forth the smallest possible GUI hiding a "
                     "full set of MPD control functions. It may be homely, but it is mighty.\n\nJust play the music and stay out of my face."
                     "\n\nCopyright 2023-2024 Gregory A. Sanders\nhttps://www.drgerg.com", "center")
#
## DEFINE THE HELP WINDOW
#
def helpbrowser():
    path_to_dat = Path(__file__).parent
    if "_internal" not in str(path_to_dat): # Compensate for varying installations.
        path_to_dat = Path.joinpath(path_to_dat, "_internal")
    theurl = str("file://" / path_to_dat / "mmc4w_help.html")
    webbrowser.open_new(theurl)
#
## DEFINE THE ART WINDOW
#
def artWindow(aartvar):
    global tbarini,artwinilist  ## removed artw from this list.
    tbarini = confparse.get("mainwindow","titlebarstatus")
    if aartvar == 1:
        thisimage = (path_to_dat / "cover.png")
    if aartvar == 0:
        thisimage = path_to_dat / "ico/mmc4w.png"
    aart = Image.open(thisimage)
    aart = aart.resize((artwinilist[0]-10,artwinilist[0]-10))
    aart = ImageTk.PhotoImage(aart)
    aart.image = aart  # required for some reason
    return aart
#
## DEFINE BUILD PLAYLIST MODE
#
def buildpl():
    global bplwinilist,bplwin
#    confparse.read(mmc4wIni)
    bpltgl = confparse.get('program','buildmode')
    if bpltgl == '0':  ## If zero (OFF), set to ON and set up for ON.
        confparse.set('program','buildmode','1')
        bplwin = TbplWin(window, "Playlists With and Without Current Song",bplwinilist)
        bplwin.listbx.bind('<<ListboxSelect>>', delfromplclicked)
        bplwin.listbx2.bind('<<ListboxSelect>>', addtoplclicked)
        logger.debug('BPM) PL Build Mode turned ON.') 
        getcurrsong()
    else:
        confparse.set('program','buildmode','0')
        if bplwin.winfo_exists():
            bplwin.update()
            savebplwinstats()
            bplwin.destroy()
        bplwinilist = makebplwinilist()
        logger.debug('BPM) PL Build Mode turned OFF.') 
    with open(mmc4wIni, 'w') as SLcnf:
        confparse.write(SLcnf)
    window.update()
#
## CREATE NEW SAVED PLAYLIST
#
def createnewpl():
    global aartvar,aatgl
    connext()
    newpl = simpledialog.askstring('Playlist Name','Name the New Playlist\nRequires reloading current playlist.',parent=window)
    if newpl > "":
        client.clear()
        client.save(newpl)
        PLSelWindow()
        logger.info("NPL) A new saved Playlist named '{}' was created.".format(newpl))
#
def browserplayer():
    global buttonvar
    outputsraw = getoutputs()[0]
    thisurl = ''
    for thisop in outputsraw:
        if thisop['plugin'] == 'httpd':
            if thisop['outputenabled'] == '1':
                thisport = confparse.get('serverstats','httpport')
                thisurl = str('http://' + serverip + ':' + thisport)
            else:
                messagebox.showinfo('MMC4W BrowserPlayer','The http output is not enabled.')
    if 'httpd' not in str(outputsraw):
        messagebox.showinfo('MMC4W BrowserPlayer','There is no http output configured on this server.')
    if thisurl > '':
        if buttonvar == 'play':
            webbrowser.open_new(thisurl)
            logger.info('BP) A call to the default browser was made. Music should play.')
        else:
            messagebox.showinfo('MMC4W BrowserPlayer','Press Play before starting BrowserPlayer.')

#
## MENU AND MENU ITEMS
#
tk.Frame(window)
menu = tk.Menu(window)
window.config(menu=menu)
nnFont = Font(family="Segoe UI", size=10)          ## Set the base font
confMenu = tk.Menu(menu, tearoff=False)
confMenu.add_command(label="Edit mmc4w.ini", command=lambda: configurator(''))
confMenu.add_command(label="Select a Server", command=lambda: SrvrWindow('server'))
confMenu.add_command(label="Toggle an Output", command=lambda: SrvrWindow('output'))
confMenu.add_command(label='Toggle Logging', command=logtoggler)
confMenu.add_command(label='Delete Debug Log',command=deletedebuglog)
confMenu.add_command(label='Reset Win Positions', command=resetwins)
confMenu.add_command(label="Get Scaling Factors",command=getscalefactors)
confMenu.add_command(label="Apply Scaling Factors",command=applyscalefactors)
confMenu.add_command(label="Set Non-Standard Port", command=nonstdport)
confMenu.add_command(label="Exit", command=exit)
menu.add_cascade(label="Config", menu=confMenu)

toglMenu = tk.Menu(menu, tearoff=False)
toglMenu.add_command(label="Reload Current Title", command=getcurrsong)
toglMenu.add_command(label="Toggle Random", command=toglrandom)
toglMenu.add_command(label="Toggle Repeat", command=toglrepeat)
toglMenu.add_command(label="Toggle Consume", command=toglconsume)
toglMenu.add_command(label="Toggle Single", command=toglsingle)
toglMenu.add_command(label="Toggle Titlebar", command=tbtoggle)
toglMenu.add_command(label="Update Database", command=dbupdate)
menu.add_cascade(label="Switches", menu=toglMenu)

listsMenu = tk.Menu(menu, tearoff=False)
listsMenu.add_command(label='Play a Single',command=lambda: lookupwin('title'))
listsMenu.add_command(label='Play an Album',command=lambda: lookupwin('album'))
listsMenu.add_command(label='Find by Artist',command=lambda: lookupwin('artist'))
listsMenu.add_command(label="Select a Playlist", command=PLSelWindow)
listsMenu.add_command(label='Create New Saved Playlist', command=createnewpl)
listsMenu.add_command(label='Remove Saved Playlist',command=lambda: addtopl('remove'))
listsMenu.add_command(label='Update "Everything" Playlist', command=makeeverything)
menu.add_cascade(label="Lists", menu=listsMenu)

queueMenu = tk.Menu(menu, tearoff=False)
queueMenu.add_command(label='Ingest Last Playlist',command=returntoPL)
queueMenu.add_command(label='Find and Play in Queue',command=lambda: queuewin('title'))
queueMenu.add_command(label="Toggle PL Build Mode", command=buildpl)
queueMenu.add_command(label="Launch Browser Player", command=browserplayer)
menu.add_cascade(label="Queue", menu=queueMenu)

helpMenu = tk.Menu(menu, tearoff=False)
helpMenu.add_command(label="Help", command=helpbrowser)
helpMenu.add_command(label="About", command=aboutWindow)
menu.add_cascade(label="Help", menu=helpMenu)

## Set up text window
text1 = tk.Text(main_frame, height=1, width=52, wrap= tk.WORD, font=nnFont)
text1.grid(column=0, columnspan=5, row=0, padx=5)
#
# Define buttons
button_volup = tk.Button(main_frame, bg='gray90', width=9, text="Vol +", font=nnFont, command=volup)
button_volup.grid(column=0, sticky='E', row=1, padx=1)                     # Place button in grid

button_voldn = tk.Button(main_frame, bg='gray90', width=9, text="Vol -", font=nnFont, command=voldn)
button_voldn.grid(column=1, sticky='W', row=1, padx=1)                     # Place button in grid

button_play = tk.Button(main_frame, width=9, bg='gray90', text="Play", font=nnFont, command=play)
button_play.grid(column=0, sticky='E', row=2, padx=1)                     # Place button in grid

button_stop = tk.Button(main_frame, width=9, bg='gray90', text="Stop", font=nnFont, command=halt)
button_stop.grid(column=1, sticky='W', row=2, padx=1)                     # Place button in grid

button_prev = tk.Button(main_frame, width=9, bg='gray90', text="Prev", font=nnFont, command=previous)
button_prev.grid(column=2, sticky='W', row=2, padx=1)                     # Place button in grid

button_pause = tk.Button(main_frame, width=9, bg='gray90', text="Pause", font=nnFont, command=pause)
button_pause.grid(column=3, sticky='W', row=2, padx=1)                     # Place button in grid

button_next = tk.Button(main_frame, width=9, bg='gray90', text="Next", font=nnFont, command=next)
button_next.grid(column=4, sticky='W', row=2, padx=1)                     # Place button in grid

button_tbtog = tk.Button(main_frame, width=9, bg='gray90', text="Mode", font=nnFont, command=tbtoggle)
button_tbtog.grid(column=2, sticky='W', row=1, padx=1)                     # Place button in grid

button_load = tk.Button(main_frame, width=9, bg='gray90', text="Art", font=nnFont, command=albarttoggle)
button_load.grid(column=3, sticky='W', row=1, padx=1)                     # Place button in grid

button_exit = tk.Button(main_frame, width=9, bg='gray90', text="Quit", font=nnFont, command=exit)
button_exit.grid(column=4, sticky='W', row=1, padx=1)                     # Place button in grid

## THREADING NOTES =========================================
# while threading.active_count() > 0:
# Make all threads daemon threads, and whenever the main thread dies all threads will die with it.
## tk.END THREADING NOTES =====================================
#
t1 = threading.Thread(target=songtitlefollower)
t1.daemon = True
t1.start()
#
#confparse.read(mmc4wIni)
aatgl = confparse.get("albumart","albarttoggle")
abp = confparse.get('program','autobrowserplayer')
evenodd = 1
songused = 0
###
# lastpl is "Last Playlist". dur is "Song Duration".
###
def threesecdisplaytext():
    global evenodd, globsongtitle,buttonvar,lastpl,endtime,dur,ran,rpt,sin,con,elap
    def eo1():
        global evenodd, globsongtitle
        if evenodd == 1:
            msg = globsongtitle
            evenodd = 2
            displaytext1(msg)
    def eo2():
        global evenodd,buttonvar,dur,endtime,songused,elap
        splitdur = dur.split(".")
        songlen = splitdur[0]
        if buttonvar != 'stop' and buttonvar != 'pause':
            songused = float(dur) - (endtime - time.time())
            if songused >= float(songlen):
                songused = float(songlen)
            songused = str(int(songused))
        if buttonvar == 'pause':
            songused = int(float(elap))
            # songused = songused
        if buttonvar == 'stop':
            songused = '0'
            songlen = '0'
        if evenodd == 2:
            # msg = str("Svr: " + serverip[-3:] +" | " + buttonvar + " | PL: " + lastpl)
            msg = str("S: {} | {} | {}{}{}{} | PL:{}".format(serverip[-3:],buttonvar,ran,rpt,sin,con,lastpl))
            msg2=str(' | {}/{}s.'.format(songused,songlen))
            evenodd = 1
            displaytext1(msg)
            displaytext2(msg2)
    window.after(1000,eo1)
    window.after(2500,eo2)
    window.after(3000,threesecdisplaytext)
#
## Do these things right before starting window.mainloop().
prevbtnstate = 'stop'
if firstrun == '1':
    # getscalefactors()
    plupdate()
threesecdisplaytext()
confparse.read(mmc4wIni)
bpltgl = confparse.get('program','buildmode')
if bpltgl == '1': # Just on the odd chance it crashed and left this at '1'.
    bplwin = TbplWin(window, "Playlists Without Current Song",bplwinilist)
    buildpl()
if aatgl == '1':
    aart = artWindow(1)
    artw = TartWin(window, "AlbumArt",artwinilist,aart)
    if firstrun == '1':
        artw.overrideredirect(False)
    elif firstrun == '0' and tbarini == '0':
        artw.overrideredirect(True)
    elif firstrun == '0' and tbarini == '1':
        artw.overrideredirect(False)
getcurrsong()
getoutputs()
if abp == '1':
    if buttonvar == 'play':
        browserplayer()
logger.info("Down at the bottom. Firstrun: {}".format(firstrun))
window.mainloop()  # Run the (not defined with 'def') main window loop.
